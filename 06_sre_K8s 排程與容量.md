# 第6章　K8s 叢集：節點、排程與自癒

## 情境 11　ImagePullBackOff 的全局免疫(Cluster-wide Immunity)
**背景**：一個橫跨 3 個 region、共 1,200 個節點的 EKS 叢集，每天部署 400+ 次，映像檔來自自建 Harbor registry 加 AWS ECR 雙來源。
**問題**：凌晨 02:14，ECR 的某個 NAT Gateway 開始間歇性丟封包。8 分鐘內，新排程的 Pod 像骨牌一樣倒下——`ImagePullBackOff` 從 3 個飆到 1,900 個，HPA 此時剛好因為流量尖峰想擴容，結果擴出來的全是拉不到映像的殭屍 Pod。值班工程師的手機在 2 分鐘內收到 600 則告警，Slack 直接卡死。
**需要的技能**：Kubernetes event 流分析、容器 registry 拓樸理解、跨 region 網路除錯、批次 kubectl 操作。
**開源工具**：`kube-state-metrics`、`Trivy`、`k9s`、`stern`。
**用到的 Agent 特性**：龍蝦 OpenClaw 透過 **本地腳本執行** 持續 watch 全叢集的 `FailedPull` event 流，當它偵測到「同一映像 digest 在 90 秒內跨 ≥3 個節點失敗」時，立刻判定這不是單機問題而是來源側故障。它的 **子 Agent** 兵分兩路：一個去 `nslookup` + `curl -w` ECR endpoint 量測 RTT 與封包丟失率，另一個比對 Harbor 的同一份映像是否健康。確認 ECR 掛了之後，龍蝦從 **ClawHub** 載入「registry-failover」技能外掛，自動把受影響 Deployment 的 `imagePullSecrets` 與映像前綴熱切到 Harbor 鏡像，並用 `Multi-Channel Gateway` 同時在 Slack、PagerDuty、企業微信丟出一張帶 region 拓樸圖的根因卡片：「ECR ap-northeast-1 封包丟失 47%，已切換 1,900 Pod 至 Harbor 鏡像，預估 4 分鐘恢復。」
**沒有 Agent 的窘境**：值班工程師被 600 則告警淹沒，要花 15 分鐘才意識到「不是我的 app 壞了，是 registry 壞了」，再花 20 分鐘手動改 11 個 namespace 的 imagePull 設定，過程中還改錯 2 個 namespace 引發二次事故。
**效益**：MTTR 從 52 分鐘壓到 3 分 40 秒；告警風暴從 600 則收斂成 1 張卡片；avoided 一次本可波及 30% 線上流量的容量塌方。

> 💡 君之一席話
> 「`ImagePullBackOff` 從來不是 Pod 的病，而是供應鏈的咳嗽——你要治的是上游，不是退燒。」

> 🔍 進階點評──道路在哪裡
> 這個案例把龍蝦從「告警轉述員」推向「供應鏈健康度的主動裁判」。往前看一步，它的道路是建立一張**跨叢集的映像來源信任圖譜**，讓 failover 不再是腳本式的硬切，而是依據實時 SLO 加權的智慧路由。落地的工程邊界很現實：誰授權 Agent 修改生產的 imagePullSecrets？failover 後的「自動切回」如何避免 registry 抖動引發乒乓震盪？這需要在 Agent 與 GitOps(Argo CD) 之間劃出一條清楚的「誰是真相來源」的紅線。

## 情境 12　控制面腦裂(Control Plane Split-Brain)的仲裁者
**背景**：自建的 5 節點 etcd 叢集，跨兩個機房(AZ-A 3 台、AZ-B 2 台)，承載一個金融級的 kube-apiserver 高可用部署。
**問題**：14:03，連接兩機房的骨幹光纖被施工挖斷。AZ-A 這邊 3 個 etcd 還能湊到 quorum 繼續寫，AZ-B 的 2 個 etcd 失去多數派變唯讀。但糟糕的是 AZ-B 有自己的本地 load balancer 還在把寫請求導向那 2 台——controller-manager 開始出現幻覺，對同一批 Pod 反覆 create/delete，`resourceVersion` 衝突日誌每秒刷 4,000 行。再 90 秒，整個叢集的 leader election 進入抖動，scheduler 停止排程。
**需要的技能**：etcd raft 共識原理、quorum 與 fencing 機制、kube-apiserver HA 拓樸、災難隔離決策。
**開源工具**：`etcdctl`、`etcd-defrag`、`Patroni`(設計參照)、`kube-apiserver` healthz 探針。
**用到的 Agent 特性**：龍蝦 OpenClaw 透過 **本地腳本執行** 在每個 AZ 部署了輕量哨兵，持續對各 etcd member 跑 `etcdctl endpoint status --write-out=json`，當它發現「AZ-B 的 member 回報 `raftIndex` 落後 AZ-A 超過 50,000 且 `isLeader` 全為 false」時，立即判定發生網路分區。它沒有貿然動手，而是先用 **子 Agent** 驗證:這是真分區還是探針誤判——交叉確認跨 AZ ping、BGP 路由表、雲商狀態頁。確認後，龍蝦執行最關鍵的 **fencing 決策**:把 AZ-B 的本地 LB 從寫入路徑摘除(更新其 backend 權重為 0)，強制所有寫流量回到擁有 quorum 的 AZ-A，阻止腦裂雙寫。同時透過 **Multi-Channel Gateway** 在指揮頻道發出紅色卡片並 @ 值班主管:「偵測到 control plane split-brain，已 fence AZ-B 寫入路徑，叢集回到單一真相，等待人工確認光纖修復後再恢復。」
**沒有 Agent 的窘境**：腦裂是 SRE 最怕的場景之一。人類要先從 4,000 行/秒的衝突日誌裡看出「這是分區不是過載」，光這一步就 20 分鐘起跳；等意識到要 fencing，雙寫造成的資料分歧可能已經污染了數千個 Pod 的狀態，事後對帳要熬一整夜。
**效益**：從分區發生到 fencing 完成 75 秒；避免了雙寫污染(estimated 影響 8,000+ 物件)；把一場可能需要 etcd 從快照重建的 P0，降級成一次有序的單側降級。

> 💡 君之一席話
> 「分散式系統最深的恐懼，不是某一半死了，而是兩半都還活著、卻都以為自己是唯一的真相。」

> 🔍 進階點評──道路在哪裡
> 腦裂仲裁是 Agent 自動化的「深水區」——因為 fencing 是一個**會主動讓一部分系統失去能力**的破壞性決策。這指向龍蝦未來最具爭議也最有價值的道路:**成為分散式共識的元仲裁層**。但這裡的信任邊界極其鋒利:當 Agent 自己的哨兵也跨越了被切斷的網路，它如何確保自己不是基於分區的「半邊真相」做判斷？答案可能是引入一個**獨立於 K8s 控制面之外的第三方見證(witness)**，讓 Agent 的決策本身也滿足 quorum。否則,自動化的 fencing 可能變成下一場腦裂的源頭。

## 情境 13　雲端機器硬體預警時的無感移民(Live Migration)
**背景**：跑在 GCP 上的有狀態服務叢集，混用 Spot 與 on-demand 節點，其中一批 c2-standard-60 上跑著 Redis、ClickHouse 等對重啟敏感的 StatefulSet。
**問題**：03:47，GCP 推送了一則 `HostError` 維護預警:某台底層宿主機的 ECC 記憶體連續報出 17 次可糾正錯誤，預測 6 小時內會強制 live migration 或下線。這台機器上正好跑著 ClickHouse 的一個 shard leader，硬遷移會造成 40–90 秒的 stop-the-world 凍結，足以讓上游的即時報表查詢全部 timeout。
**需要的技能**：雲商維護事件解讀、StatefulSet 優雅遷移、PodDisruptionBudget 設計、有狀態服務的 leader 轉移。
**開源工具**：`Node Problem Detector`、`Descheduler`、`Velero`、`cluster-autoscaler`。
**用到的 Agent 特性**：龍蝦 OpenClaw 訂閱了 GCP 的 metadata `maintenance-event` endpoint，透過 **本地腳本執行** 在 Node Problem Detector 之上加一層語意理解:它不只看到「有維護」，而是用 **子 Agent** 反查這台節點上跑了哪些 workload、哪些是 leader、哪些有 PDB 保護。判定 ClickHouse shard leader 在風險節點後，龍蝦選擇**主動先發制人**:在維護窗口到來前的低峰期(凌晨 04:10)，先觸發 ClickHouse 的優雅 leader 轉移到健康節點，再 cordon + drain 風險節點,讓 GCP 的 live migration 遷移一台空機器。整個過程透過 **Multi-Channel Gateway** 在 Slack 留下時間軸:「04:10 預測性遷移 shard leader、04:14 drain 完成、04:30 等待 GCP 維護、用戶零感知。」並從 **ClawHub** 載入「stateful-graceful-evict」外掛確保 quorum 全程不破。
**沒有 Agent 的窘境**：多數團隊根本沒人盯 metadata endpoint,等 GCP 真的開始 live migration、ClickHouse 凍結 60 秒、報表全紅了才被動救火。即使有人看到預警,半夜手動操作有狀態服務的 leader 轉移風險極高,一個手抖就是資料不一致。
**效益**：把一次注定 40–90 秒的用戶可感知凍結,變成**零感知**遷移;預測性處理把被動救火窗口從「6 小時內隨時爆」變成「凌晨低峰主動排程」;有狀態服務遷移的人為失誤率歸零。

> 💡 君之一席話
> 「最高明的運維,是讓災難在它發生之前,就已經被搬空了現場。」

> 🔍 進階點評──道路在哪裡
> 這個案例的精髓是**從「響應事件」進化到「響應預兆」**——龍蝦讀的是硬體的「心電圖」而非「死亡證明」。往前看,這條道路通向**容量與健康的概率化調度**:Agent 依據宿主機 ECC 錯誤率、磁碟 SMART、Spot 中斷概率,給每個節點打一個動態「壽命分數」,讓 scheduler 主動避開高風險宿主。工程挑戰在於:預測性遷移有成本(多佔一台機器、多一次 leader 轉移),Agent 必須學會在「預防的成本」與「災難的期望損失」之間做量化權衡,而不是一見預警就草木皆兵。

## 情境 14　K8s 副本數動態下班制(Replica Off-hours Scheduling)
**背景**：一家面向 B2B 企業客戶的 SaaS,80% 流量集中在工作日 09:00–19:00,但開發團隊習慣把所有環境的 `replicas` 寫死成「應付尖峰」的數字,180 個 Deployment 全年 7×24 滿載。
**問題**：財務月底盤帳發現,光是 staging 與 internal-tools 兩個 namespace,夜間(19:00–次日 08:00)與週末的閒置運算就燒掉每月 USD 38,000——一堆每秒 0 QPS 的 Pod 整夜亮著燈跑空轉,CPU 使用率長期低於 3%,但沒人敢手動縮容,怕第二天上班忘了開回去出事。
**需要的技能**：流量畫像與週期性建模、HPA/VPA 調校、成本歸因(FinOps)、安全的縮放護欄設計。
**開源工具**：`KEDA`、`kube-downscaler`、`OpenCost`、`Goldilocks`。
**用到的 Agent 特性**：龍蝦 OpenClaw 透過 **本地腳本執行** 連續 14 天採集每個 Deployment 的 QPS 與資源曲線,用 **子 Agent** 為每個服務自動畫出「作息畫像」,辨識出哪些是「真 7×24」(支付、認證)、哪些是「朝九晚五」(後台、報表)、哪些是「純工作日」。它不直接砍,而是先生成一份**動態下班排程提案**,透過 **Multi-Channel Gateway** 發到 Slack 讓 owner 一鍵核准。核准後,龍蝦從 **ClawHub** 載入 KEDA 的 `Cron` ScaledObject 外掛,為每個服務裝上「下班制」:夜間縮到最小副本、清晨流量回升前 15 分鐘自動預熱擴容。關鍵是它設了**雙保險護欄**——任何「下班」的服務一旦收到非預期流量(QPS 突破基線 3σ),立刻自動全量擴回並通報。
**沒有 Agent 的窘境**：FinOps 報表每月罵一次,工程師每月道歉一次,但沒人有空為 180 個服務逐一分析作息、逐一寫縮放規則、還要承擔「縮錯導致線上事故」的責任,於是這筆錢就這樣年復一年地燒。
**效益**：staging/internal namespace 夜間與週末運算成本下降 71%,月省約 USD 27,000;180 個服務的作息分析從「沒人做」變成「14 天自動完成」;因設了 3σ 流量護欄,縮容期間零事故。

> 💡 君之一席話
> 「雲端帳單最貴的一項,叫做『沒人敢動』——而 Agent 賣的,正是『敢動』這件事的安全感。」

> 🔍 進階點評──道路在哪裡
> 這是 Agent 進入 **FinOps 自治** 的典型入口——它把「省錢」從一個需要勇氣的人類決策,變成一個有護欄、可審計、可回滾的自動化動作。往前的道路是**全叢集的彈性容量大腦**:不只按時間表,而是融合業務日曆(財報日、大促)、區域時區、甚至客戶合約 SLA 來編排容量。但這裡的信任邊界在於「縮容的爆炸半徑」:Agent 越敢縮,省得越多,但縮錯一個被低估的依賴服務,就是一次連鎖故障。未來真正的考驗,是 Agent 能否建立對「服務間隱性依賴」的因果模型,而不只是看單一服務的 QPS 曲線。

## 情境 15　節點遭勒索軟體爆發的孤立分區斷尾求生(Ransomware Quarantine)
**背景**：一個混合雲叢集,部分 worker 節點是託管在 IDC 的裸金屬,某次第三方供應鏈套件被植入了挖礦兼勒索的惡意載荷。
**問題**：02:58,安全側的 Falco 突然連續告警:3 個節點上的容器在做異常行為——大量 `chmod`、對 `/var/lib/kubelet` 的可疑寫入、向境外 IP 發起 TLS 連線、CPU 100% 跑加密運算。這是勒索軟體在橫向移動,而這 3 個節點與正常生產 workload 共處同一個 VLAN,再過幾分鐘可能透過 service account token 污染整個叢集。
**需要的技能**：runtime 安全偵測、K8s NetworkPolicy 與微隔離、RBAC/ServiceAccount 失效化、取證快照(forensics)。
**開源工具**：`Falco`、`Cilium`(NetworkPolicy)、`Tetragon`、`kube-bench`。
**用到的 Agent 特性**：龍蝦 OpenClaw 把 Falco 的告警流接進 **本地腳本執行** 的決策引擎,當它在 60 秒內看到「同類異常行為跨 ≥2 節點 + 境外連線 + 加密熵升高」的組合特徵時,判定為勒索軟體橫向爆發,進入**斷尾求生**協議。它的 **子 Agent** 同步執行三件事:① 用 Cilium 給受感染節點打上 `quarantine` NetworkPolicy,切斷一切東西向與南北向流量(只留取證通道);② 立即撤銷這些節點上 Pod 的 ServiceAccount token,並輪換可能洩漏的叢集 secret;③ 對受感染容器做記憶體與磁碟快照後再 `kubectl cordon`+冷凍,保留證據。完成隔離後透過 **Multi-Channel Gateway** 向安全、SRE、法務三個頻道同步發出 incident 卡片並啟動 war room。它沒有自作主張刪除任何東西——**取證優先,斷尾但不毀屍**。
**沒有 Agent 的窘境**:凌晨 3 點,從一堆 Falco 告警裡辨識出「這是勒索軟體在橫移」需要資深安全工程師,而他可能要 20 分鐘才上線;這 20 分鐘足夠惡意載荷污染整個叢集的 secret,事後可能要全叢集憑證輪換+重建,影響面從 3 個節點擴大到整個 region。
**效益**:從首個告警到完成微隔離 + token 撤銷 52 秒;把橫向爆炸半徑死死摁在 3 個節點(否則 estimated 波及 200+ 節點);取證快照完整保留,讓事後溯源從「靠猜」變成「有實證」。

> 💡 君之一席話
> 「面對勒索軟體,慢一秒不是多丟一台機器,而是多丟一整個信任域——斷尾要快,但別把證據也一起燒了。」

> 🔍 進階點評──道路在哪裡
> 這個場景把龍蝦推到 **安全自動響應(SOAR)與運維的交界**,而這正是最敏感的信任邊界:Agent 被授權執行「切斷網路、撤銷憑證」這類具有強破壞性的防禦動作。往前的道路是 **可逆的、分級的自動圍堵**——隔離應該像保險絲一樣分級熔斷,而非一刀切。最大的工程難題是「誤殺成本」:如果 Falco 的特徵命中了一個被誤判為惡意的正常批次任務,Agent 的自動隔離本身就成了一次自殘式 DoS。因此這條路的關鍵,是讓 Agent 的圍堵決策帶有「置信度分級」與「秒級可回滾」,讓安全與可用性不必二選一。

## 情境 16　拓樸感知排程救活跨 AZ 延遲(Topology-Aware Scheduling)
**背景**：一個跨 3 個可用區的微服務叢集,核心鏈路是 `gateway → order → inventory → payment`,四個服務各有數十個副本,被 scheduler 隨機撒在各 AZ。
**問題**：大促壓測時,P99 延遲詭異地飆到 380ms,但每個服務單看都很健康、CPU 都不高。深挖才發現:scheduler 把調用鏈上下游 Pod 散落在不同 AZ,一次完整下單請求要跨 AZ 來回 6 次,每跳 +1.5ms 的跨區延遲被鏈式放大,再疊加跨 AZ 流量還在燒每 GB USD 0.01 的傳輸費,壓測一小時燒掉 USD 900 的純網路費。
**需要的技能**:調用鏈拓樸分析、Topology Spread Constraints、Pod Affinity 設計、跨 AZ 流量成本建模。
**開源工具**：`Jaeger`、`Kiali`、`Descheduler`、`kube-scheduler`(topology plugin)。
**用到的 Agent 特性**：龍蝦 OpenClaw 透過 **本地腳本執行** 把 Jaeger 的 trace 資料聚合成服務間的「跨 AZ 跳數熱力圖」,用 **子 Agent** 算出每條鏈路的跨區放大係數,精準指認出「order↔inventory 這對黃金搭檔被拆散在 AZ-A 與 AZ-C」是元兇。它生成一份基於 `topologySpreadConstraints` + zone-aware affinity 的排程修正方案,先在 staging 跑 A/B 驗證(同區親和後 P99 從 380ms 降到 90ms),確認無副作用後透過 **Multi-Channel Gateway** 把 before/after 對比圖推給架構組核准,再用 Descheduler 漸進式地把錯位 Pod 重新調度到同 AZ,全程灰度、隨時可停。
**沒有 Agent 的窘境**:「每個服務都健康但整體很慢」是分散式系統最折磨人的灰色故障——人類工程師可能花兩三天看 dashboard 都找不到,因為沒有任何單一指標亮紅燈,真相藏在「拓樸錯位」這個沒有專屬監控項的維度裡。
**效益**:核心鏈路 P99 從 380ms 降到 90ms(−76%);大促期間跨 AZ 傳輸費下降 64%;一個原本可能要花 3 人天排查的灰色故障,被壓縮到一次自動的拓樸分析。

> 💡 君之一席話
> 「當每個零件都顯示正常、機器卻在發抖,問題往往不在零件,而在它們被擺放的方式。」

> 🔍 進階點評──道路在哪裡
> 拓樸錯位是教科書級的 Grey Failure:沒有單點告警,只有整體的緩慢。這指向龍蝦的一條深刻道路——**成為調用鏈的空間規劃師**,讓排程從「資源視角(哪裡有 CPU)」升維到「關係視角(誰該離誰近)」。落地的張力在於:親和性越強,容災性越弱——把上下游全擠進同一 AZ,延遲最低,但那個 AZ 一掛就全鏈路歸零。未來 Agent 必須在「延遲最優」與「故障域隔離」之間做動態權衡,甚至依大促/平峰切換不同的拓樸策略,這是一個沒有靜態最優解的多目標優化問題。

## 情境 17　驅逐風暴(Eviction Storm)下的優先級保衛戰
**背景**：一個資源超賣(overcommit)的多租戶叢集,為了提高利用率,memory request 普遍設得偏低,靠 limit 與 QoS 分級來兜底。
**問題**：某個資料團隊半夜跑了個沒設 limit 的 Spark 任務,記憶體像氣球一樣膨脹,把所在節點推到 MemoryPressure。kubelet 的 eviction 機制啟動,但因為很多關鍵服務當初為了「容易被排程」把 request 設得很低、QoS 掉到 `Burstable` 甚至 `BestEffort`,結果 kubelet 按 QoS 排序驅逐時,**先把支付閘道的 Pod 給趕走了**,而那個吃記憶體的 Spark 反而因為 request 設得高、QoS 是 `Burstable` 活了下來。驅逐引發 Pod 重排程到別的節點,又把別的節點推爆,形成跨節點的**驅逐連鎖風暴**,3 分鐘內 47 個 Pod 被連環驅逐。
**需要的技能**:QoS 分級與 eviction 機制、資源 request/limit 治理、PriorityClass 設計、節點壓力傳導分析。
**開源工具**：`kube-state-metrics`、`Goldilocks`(VPA 建議)、`Kyverno`(策略守門)、`node-exporter`。
**用到的 Agent 特性**：龍蝦 OpenClaw 在 **本地腳本執行** 層持續監看各節點的 `node_memory_*` 與 eviction event,當它偵測到「同一節點 60 秒內 ≥3 次 eviction 且關鍵服務(帶 `tier=critical` label)被驅逐」時,判定驅逐風暴正在錯誤地犧牲核心服務。它的 **子 Agent** 立即做兩件事:① 緊急為被誤驅的關鍵服務臨時注入高 `PriorityClass` 並標記 `system-node-critical`,讓它們在下一輪排程中優先落地、免於再被驅逐;② 反向定位到肇事的 Spark Pod,為其打上 cordon 標記並限流,切斷壓力源頭。風暴平息後,龍蝦從 **ClawHub** 載入 Kyverno 策略外掛,自動補上「禁止無 limit 的批次任務進入生產節點池」的准入規則,並透過 **Multi-Channel Gateway** 給資料團隊發一張「你的任務引發了驅逐風暴,已隔離,請加 limit」的事故回執。
**沒有 Agent 的窘境**:驅逐風暴的恐怖在於它會「自我傳染」——人類還在查第一個節點為什麼驅逐,風暴已經跳到第三、第四個節點。等搞清楚「原來是 QoS 排序把支付閘道當成了 BestEffort 先殺」,核心交易可能已經抖了十幾分鐘。
**效益**:從風暴啟動到關鍵服務止損 68 秒;把連環驅逐摁在 47 個 Pod 而非整個節點池;事後自動補上准入策略,讓「無 limit 批次任務」這個復發性病根被根治。

> 💡 君之一席話
> 「kubelet 驅逐時不問你重不重要,只問你的 request 填得高不高——資源治理的疏忽,會在最壞的時刻替你決定誰生誰死。」

> 🔍 進階點評──道路在哪裡
> 驅逐風暴揭露了一個殘酷真相:K8s 的調度公平性,完全建立在 request/limit 被誠實填寫的前提上,而這個前提幾乎從不成立。龍蝦的道路因此延伸向 **資源契約的主動治理者**——不只在事故時救火,更在准入時就用策略引擎攔下「謊報資源」的 workload。工程上的深水區在於:Agent 臨時提升 PriorityClass 是一把雙刃劍,它救了支付閘道,卻可能在下一刻把別人擠下節點。未來真正成熟的形態,是 Agent 維護一張**全叢集的優先級與資源預算總帳**,讓每一次緊急提權都是在已知的零和賽局裡做有據可查的取捨,而非臨場的英雄主義。

## 情境 18　Cluster Autoscaler 在 Spot 中斷潮中的容量續命(Spot Interruption Surge)
**背景**：為了極致省錢,一個批次運算叢集 70% 節點用 AWS Spot 實例,靠 cluster-autoscaler 自動伸縮,跑著大量可中斷的 ETL 與訓練任務,但也混了一些「假設自己一直在」的長連線服務。
**問題**：某天 AWS 對 `c5.4xlarge` 這個機型在 ap-northeast-1 全區回收 Spot,兩分鐘內發出 60 張 2 分鐘倒數的中斷通知。cluster-autoscaler 想擴新節點補位,但因為大家都搶同一機型,`InsufficientInstanceCapacity` 連環報錯,擴容失敗。可調度容量瞬間蒸發 40%,Pending Pod 堆到 900 個,任務佇列開始雪崩。
**需要的技能**:Spot 中斷處理、cluster-autoscaler 與 node group 設計、多機型/多 AZ 容量分散、批次任務的可中斷化。
**開源工具**：`Karpenter`、`AWS Node Termination Handler`、`cluster-autoscaler`、`Kueue`。
**用到的 Agent 特性**：龍蝦 OpenClaw 訂閱 EC2 的 Spot 中斷 metadata,在 **本地腳本執行** 層做容量態勢感知,當它偵測到「單一機型 2 分鐘內 ≥20 張中斷通知 + autoscaler 連續 `InsufficientCapacity`」時,判定為 Spot 中斷潮,啟動**容量續命**協議。它的 **子 Agent** 即時改寫 Karpenter 的 NodePool 約束,把搶不到的 `c5.4xlarge` 從首選裡剔除,動態擴大到 `m5/m6i/c6i` 等 6 個可替代機型 + 3 個 AZ,讓 autoscaler 不再死磕一個型號;同時它識別出那些「假裝自己不會被中斷」的長連線服務,把它們優先重排到僅剩的 on-demand 節點上保命,讓真正可中斷的 ETL 去承受抖動。透過 **Multi-Channel Gateway** 發出容量儀表板:「Spot c5.4xlarge 全區回收,已切換至多機型混合擴容,Pending 從 900 收斂中,核心服務已遷至 on-demand。」
**沒有 Agent 的窘境**:cluster-autoscaler 的 node group 機型約束通常是寫死在 IaC 裡的,中斷潮來時人類要現場改 Terraform、跑 apply、等生效,每一步都是分鐘級;而那 900 個 Pending Pod 和雪崩的佇列不會等你,等你改完,SLA 可能已經破了。
**效益**:Pending Pod 從 900 在 4 分鐘內降到 50 以下;透過多機型分散,把對單一 Spot 機型的依賴從 70% 降到 25%;核心長連線服務零中斷;這次中斷潮的恢復從「破 SLA」變成「波瀾不驚」。

> 💡 君之一席話
> 「把雞蛋放進 Spot 這個便宜的籃子沒問題,問題是你只買了一種籃子——容量的韌性,藏在你願意接受多少種替代品裡。」

> 🔍 進階點評──道路在哪裡
> Spot 中斷潮逼問的是一個 FinOps 的永恆矛盾:省到極致與穩到極致天然對立。龍蝦的道路是成為 **動態容量組合的操盤手**——像管理投資組合一樣管理機型/AZ/Spot-OnDemand 的配比,實時根據中斷概率與價格重新平衡。落地的硬骨頭在於「狀態正確性」:Agent 改寫 NodePool、遷移 workload 的速度必須快過中斷的 2 分鐘倒數,這對 Agent 的決策延遲提出了硬實時要求。更前瞻地看,這條路最終會走向 Agent 與雲商容量市場的**博弈與預測**——在中斷潮真正爆發前,就已經悄悄把雞蛋換好了籃子。

## 情境 19　殭屍 Pod 與孤兒資源的全叢集清道夫(Zombie & Orphan Reaper)
**背景**：一個運轉了 4 年、經手過十幾任工程師的「歷史悠久」叢集,累積了大量沒人記得的測試 namespace、卡在 `Terminating` 的 Pod、解除綁定後沒回收的 PV、以及一堆指向已刪除 Pod 的孤兒 endpoint。
**問題**：某次擴容時發現,叢集「明明有 30% 資源閒置」卻擴不出新 Pod——`kubectl get pods -A` 一看,2,400 個 Pod 裡有 380 個卡在 `Terminating` 超過 6 小時(因為 finalizer 死鎖),占著資源不放;另有 60 個 PV 處於 `Released` 卻不回收,綁著的 EBS 卷每月白燒 USD 1,200;更陰險的是一堆孤兒 endpoint 還在 Service 的負載均衡列表裡,把流量導向早已不存在的 Pod IP,造成間歇性 502。
**需要的技能**:finalizer 與 GC 機制、PV/PVC 生命週期、Service/Endpoint 一致性、叢集衛生治理。
**開源工具**：`kube-janitor`、`Velero`、`Polaris`、`kubectl-neat`。
**用到的 Agent 特性**：龍蝦 OpenClaw 定期透過 **本地腳本執行** 做全叢集「健康普查」,用 **子 Agent** 分類掃出四種垃圾:殭屍 Terminating Pod、孤兒 PV、失聯 endpoint、無主 namespace。對於高風險操作(刪 PV、清 namespace),它絕不擅自動手——而是生成一份帶「證據鏈」的清理提案(每一項都附上「為何判定為垃圾」的依據:多久沒人 owner、最後活動時間、是否還有引用),透過 **Multi-Channel Gateway** 推給平台組做**分級核准**:低風險的殭屍 Pod(清 finalizer)可自動處理,高風險的 PV 刪除必須人工點頭。核准後,龍蝦從 **ClawHub** 載入 kube-janitor 規則外掛安全執行,並對每一步都留下可回滾的審計日誌。
**沒有 Agent 的窘境**:叢集衛生是典型的「重要但不緊急」,永遠排在所有需求後面,於是垃圾年復一年累積。等到它終於以「擴不出容量」「神祕 502」的形式爆發時,人類要在 2,400 個 Pod 裡靠肉眼考古,分辨哪個 Terminating 是死鎖、哪個 PV 真能刪——刪錯一個還在用的 PV,就是一場資料災難,於是大家更不敢動。
**效益**:回收 380 個殭屍 Pod 占用的資源,讓 30% 的「假閒置」變成真可用;清掉 60 個孤兒 PV,月省 USD 1,200;修復孤兒 endpoint,間歇性 502 歸零;把「沒人敢做的考古工作」變成每週一次的自動普查。

> 💡 君之一席話
> 「叢集裡最危險的不是壞掉的東西,而是『死了卻沒人敢宣布它死亡』的東西——技術債的利息,是用容量和 502 來償還的。」

> 🔍 進階點評──道路在哪裡
> 殭屍與孤兒資源是熵的具象化——任何長壽系統都會自發走向混亂。龍蝦在這裡的道路是 **叢集的常駐免疫系統**:不是偶爾大掃除,而是持續地識別、隔離、回收死亡組織。最關鍵的工程命題是「如何證明一個東西真的死了」——一個看似無主的 namespace,可能是某個季度才跑一次的合規任務。因此這條路的核心不是「清理能力」,而是 **可解釋的死亡判定**:Agent 必須為每一次回收提供經得起審計的證據鏈,並讓破壞性操作永遠停在「人類核准」這道閘前,直到信任被長期觀測所積累。

## 情境 20　調度器抖動(Scheduler Thrashing)與反親和死鎖的破局
**背景**：一個對高可用要求極嚴的叢集,核心服務普遍配了 `podAntiAffinity` 強制「同一服務的副本不能落在同一節點」,以保證單節點故障不會團滅。
**問題**：一次節點縮容後,叢集進入一個詭異狀態:某個 6 副本的關鍵服務,因為反親和約束是 `requiredDuringScheduling`(硬約束),而剩餘的可用節點只剩 5 個滿足條件,第 6 個副本永遠 `Pending`;同時 HPA 看到「副本沒到目標數」一直催 scheduler,scheduler 一直嘗試又一直失敗,排程佇列每秒抖動數百次,kube-scheduler 的 CPU 被自己的徒勞嘗試燒到 90%,連帶拖慢了**整個叢集所有 Pod 的排程速度**——一個服務的死鎖,劣化了全叢集的調度吞吐。
**需要的技能**:affinity/anti-affinity 約束求解、scheduler 性能剖析、約束放鬆(soft constraint)權衡、調度佇列健康度監控。
**開源工具**：`kube-scheduler`(profiling)、`Descheduler`、`kube-state-metrics`、`Prometheus`。
**用到的 Agent 特性**：龍蝦 OpenClaw 透過 **本地腳本執行** 監看 scheduler 的 `scheduler_pending_pods` 與 `scheduling_attempt_duration` 指標,當它發現「某 Pod 排程嘗試次數暴增 + 全叢集排程延遲同步抬升」時,判定發生了**約束無解導致的調度抖動**。它的 **子 Agent** 跑了一遍約束求解模擬,精準算出「6 副本 × 硬反親和 × 僅 5 個合格節點 = 數學上無解」,並給出三個帶權衡的選項:① 把第 6 副本的反親和從 `required` 降級為 `preferred`(犧牲一點容災換取可調度);② 擴一個合格節點;③ 把目標副本數從 6 降到 5。它透過 **Multi-Channel Gateway** 把這道「不可能三角」連同每個選項的容災影響清楚呈報給 owner,而非自作主張。owner 選了擴節點後,龍蝦自動觸發 Karpenter 擴容並驗證第 6 副本成功落地、scheduler CPU 回落、全叢集排程延遲恢復。
**沒有 Agent 的窘境**:這是最隱蔽的一類故障——表面上只有「一個 Pod 一直 Pending」,沒人會想到它正在拖垮整個叢集的調度器。人類工程師通常要等到「為什麼全叢集所有部署都變慢了」才警覺,再花很久才能把因果鏈追溯到「那個無解的反親和約束」上,因為這兩件事在 dashboard 上看起來毫不相干。
**效益**:從調度抖動到定位約束死鎖根因 90 秒;全叢集排程延遲從劣化的 8 秒恢復到 200ms;把一個「看起來只影響 1 個 Pod、實則拖垮整個 scheduler」的隱形殺手,變成一道有量化權衡、可決策的選擇題。

> 💡 君之一席話
> 「最貴的死鎖,不是把自己鎖死,而是一邊鎖死自己,一邊讓全世界陪它一起變慢。」

> 🔍 進階點評──道路在哪裡
> 這個場景的深刻之處,在於它是一道**數學上無解卻偽裝成性能問題**的故障——約束求解的不可滿足性,投射成了調度器的 CPU 燃燒。龍蝦的道路因此指向 **約束系統的求解器與翻譯官**:它不僅要算出「無解」,更要把這個冰冷的數學結論翻譯成人類能權衡的業務語言(容災 vs 容量 vs 副本數的不可能三角)。工程上最前瞻的命題是:當約束衝突在大規模叢集中變得普遍,Agent 能否從「事後破局」進化到「准入時就攔截無解約束」——在工程師提交一個數學上注定 Pending 的 YAML 時,就提前告訴他「你這組約束在當前叢集無解」。那才是把調度從救火,真正推向了可被證明的事前正確。
