# 第7章　保存与数据库：一致性与爆满的战争

## 情境 21　主从拷贝延迟(Replication Lag)的读写分离紧急限流
**背景**：电商主库(Primary)承接写入，5 台只读副本(Read Replica)分流查找，双十一前一周的压测流量正灌进来。
**问题**：凌晨 02:14，某促销活动触发批量写入，主库 WAL 产出速度暴冲到 180 MB/s，副本 `pg_stat_replication` 的 `replay_lag` 从 200ms 飙到 **47 秒**。用户下单后查订单「查无此单」的客诉每分钟 300 笔涌入，更惨的是——有人重复下单了。一致性破口正在变成金钱破口。
**需要的技能**：拷贝拓扑健康判读、读写分离路由策略、流量整形(Traffic Shaping)、业务分级降级。
**开源工具**：PostgreSQL、Patroni、ProxySQL/PgBouncer、Prometheus + `postgres_exporter`。
**用到的 Agent 特性**：龙虾 OpenClaw 由 Prometheus 告警触发，先跑 ClawHub 上的 `replica-lag-triage` 技能插件，比对 5 台副本的 `replay_lag` 与主库 `pg_current_wal_lsn` 差值，判定为「写入风暴导致的全域 lag」而非单副本故障。它在本地运行脚本，动态调整 ProxySQL 路由规则：把「订单查找」这类强一致读请求**临时改打主库**，弱一致读(商品浏览)维持副本，并对批量写入做 token-bucket 限流到 80 MB/s。Multi-Channel Gateway 同步把「已启动读流量回切主库 + 写入限流」的决策推到 Slack 战情室与值班 PagerDuty，附上 lag 曲线截屏。
**没有 Agent 的窘境**：值班 SRE 被叫醒，先花 8 分钟登录跳板机、确认到底是哪台副本坏了还是全坏，再手动改 ProxySQL 规则——手抖把订单读也切去副本，雪上加霜，客诉再翻一倍。
**效益**：一致性破口收敛时间 MTTR 从 **22 分钟 → 50 秒**；重复下单事故从 1,200 笔压到 18 笔。

> 💡 君之一席话
> 「拷贝延迟从来不是数据库的病，是你假装『读到的就是真的』那一刻种下的因。」

> 🔍 高端点评──道路在哪里
> 这个案例把龙虾推向「一致性等级的动态路由器」这条路——未来的 Agent 不只是改规则，而是依每条 SQL 的业务语意自动判定它能忍受多少 staleness。落地的工程难点在信任边界：把读流量回切主库是一把双刃剑，Agent 必须懂得「主库还剩多少写入余量」，否则救了一致性却压垮了写路径。下一步是让 Agent 持有一张「业务一致性 SLA 地图」，而这张图的维护权，会是人与 Agent 角力最久的地带。

## 情境 22　PostgreSQL 死锁(Deadlock)的根因追踪与解锁
**背景**：金流对帐服务，两个 worker 各自在交易内更新 `accounts` 与 `ledger`，加锁顺序不一致。
**问题**：14:03 对帐批量启动后，`pg_stat_activity` 出现大片 `wait_event_type = Lock`，活跃连接从 40 堆积到 **池上限 200**，新请求全部 `too many connections`。日志里 `deadlock detected` 每 7 秒滚一次，PostgreSQL 虽会自动牺牲一方回滚，但两个 worker 像两只互让门的人，无限重试、互相对撞，吞吐归零。
**需要的技能**：锁等待图(Lock Wait Graph)分析、交易加锁顺序审计、连接池治理、`pg_blocking_pids` 判读。
**开源工具**：PostgreSQL、`pg_locks`/`pg_stat_activity`、pgBadger、pganalyze collector(开源版)。
**用到的 Agent 特性**：龙虾从 `deadlock detected` 日志模式触发，调用 ClawHub 的 `deadlock-grapher` 技能，查找 `pg_blocking_pids()` 重建锁等待环，定位到两条 SQL 加锁顺序相反的根因。它**不贸然 kill**，而是先用子 Agent 拉出两个 worker 的调用堆栈，确认哪一侧交易较短、回滚代价较小，再对该 PID 运行 `pg_terminate_backend` 打破死结，并把连接池 `statement_timeout` 暂时收紧到 5s 止血。Multi-Channel Gateway 把「锁等待环的 Mermaid 图 + 凶手两条 SQL」贴进工程群，@ 上对应的 code owner。
**没有 Agent 的窘境**：DBA 手动跑三层 `pg_locks` JOIN 查找，眼睛在十六进位 PID 之间来回比对，10 分钟后才看懂环在哪，期间连接池早已爆满、整个对帐服务 503。
**效益**：死锁根因定位 **15 分钟 → 40 秒**；连接池耗尽导致的服务不可用窗口从 11 分钟缩到 35 秒。

> 💡 君之一席话
> 「死锁不是运气不好，是两段代码对『先锁谁』各执一词——数据库只是替你们的傲慢做了仲裁。」

> 🔍 高端点评──道路在哪里
> 真正的价值不在解锁，而在 Agent 能把「加锁顺序相反」这个根因反向喂回 CI——这指向「运维事故自动转化为静态检查规则」的道路。难点在于：杀 backend 是一个有副作用的破坏性动作，Agent 必须证明自己选的是「回滚代价最小」那一方，否则它砍掉的可能是正在跑的关键对帐。规模化后，谁来授权 Agent 的 `terminate` 权限、授到什么粒度，会是每家公司都要重新谈一次的红线。

## 情境 23　Ceph/MinIO 对象保存空间突发性归零的就地封锁
**背景**：自建 MinIO 集群承接日志与媒体上传，后端 4 节点 × 12 颗 HDD 的 Erasure Set。
**问题**：21:40，监控显示集群可用空间在 25 分钟内从 18 TB **直线归零**。罪魁是某服务的 debug 开关被误开，把完整 request body 当对象狂写，QPS 不高但每笔 40 MB。MinIO 开始回 `XMinioStorageFull`，连带把同集群的正常上传全部拖死，更危险的是——磁盘写满后元数据更新都会失败，集群面临进入唯读甚至损坏风险。
**需要的技能**：对象保存容量水位判读、Bucket 流量归因、配额(Quota)即时下发、生命周期(Lifecycle)策略。
**开源工具**：MinIO、`mc` admin CLI、Prometheus(`minio_bucket_usage` metrics)、Grafana。
**用到的 Agent 特性**：龙虾在水位破 92% 时即触发(不等归零)，跑 ClawHub `object-store-hog-finder` 技能，用 `mc admin` 与 bucket metrics 在 40 秒内归因到暴写的 bucket 与来源 IP。它**就地封锁**：对该 bucket 下发临时 quota、用 bucket policy 挡掉凶手 service account 的 `PutObject`，同时挂上一条 7 天的 lifecycle 规则清理 debug 对象。本地脚本顺手 dump 出 top-10 暴增前缀(prefix)。Multi-Channel Gateway 把「已封锁 bucket X、来源 svc-Y、回收空间预估 9 TB」同步到 on-call 与该服务 owner 的 Teams 频道。
**没有 Agent 的窘境**：SRE 收到「磁盘满」告警，先怀疑是不是日志爆量，逐 bucket 跑 `mc du` 排查(每次几分钟)，等找到凶手时集群已写满、元数据写入失败，被迫进入紧急扩容与 fsck，停机数小时。
**效益**：从告警到封锁凶手 **30 分钟 → 45 秒**；避免集群写满后的唯读降级，挽回约 6 小时潜在停机。

> 💡 君之一席话
> 「保存空间不是被『用完』的，是被某个没人盯着的 debug 开关，在你睡着时一个字节一个字节偷走的。」

> 🔍 高端点评──道路在哪里
> 这条路通向「容量的主动免疫系统」——Agent 在 92% 而非 100% 出手，本质是把运维从『救火』改成『打疫苗』。工程上的真难题是归因的速度与准度：在 PB 级对象保存里实时算出 top prefix 并不便宜，Agent 需要常驻的增量统计而非临时全扫。而封锁 service account 这个动作会直接让某条业务线断供，Agent 必须区分「失控的 debug」与「合法的尖峰」，这道判断题答错一次，信任就赔光了。

## 情境 24　跨大洲数据库拷贝链路中断的全球读写转移
**背景**：金融级服务采三地部署(东京 Primary、法兰克福 Sync Standby、维吉尼亚 Async Replica)，跨洲走专线拷贝。
**问题**：03:27，东京↔法兰克福海缆段抖动，同步拷贝(synchronous_commit)因等不到 standby 确认而**整体写入卡死**——东京主库的 commit 全部 hang 在 `SyncRep wait`，欧洲用户交易超时率冲到 60%。这是最凶的一种：不是主库挂了，是它「健康地卡死在等一个永远不回的 ACK」。
**需要的技能**：同步/异步拷贝语义、Quorum commit 调整、跨区故障转移(Failover)决策、脑裂(Split-brain)防护。
**开源工具**：PostgreSQL、Patroni + etcd、HAProxy、Prometheus blackbox_exporter。
**用到的 Agent 特性**：龙虾由 `SyncRep wait` 时长 + 跨区 RTT 探测同时触发，跑 ClawHub `geo-failover-advisor` 技能，先用 blackbox 探针确认是「链路中断」而非「standby 进程死」，避免误判。它做出分级动作：第一步把 `synchronous_standby_names` 从强同步降级为 `ANY 1 (frankfurt, virginia)`，**让 commit 改向尚通的维吉尼亚取得 quorum**，立刻解除写入 hang；同步通知 Patroni 不要在链路抖动期间误触 failover(防脑裂)。子 Agent 并行监测海缆恢复，一旦 RTT 回稳自动升回强同步。Multi-Channel Gateway 把「已降级同步策略至 quorum、RPO 风险窗口 X 秒」广播到全球 SRE on-call。
**没有 Agent 的窘境**：值班工程师面对「主库没挂但写不进去」的诡异现象，第一反应是想 failover，差点触发脑裂酿成数据分叉；光是厘清「该不该切」就开了 20 分钟电话会议。
**效益**：写入 hang 解除 **MTTR 25 分钟 → 60 秒**；避免一次跨洲脑裂(潜在数据分叉与数小时对帐)。

> 💡 君之一席话
> 「最可怕的故障不是主库死了，是它活着、健康着、却在等一个永远不会来的回信——这正是分布式系统的灰色地带。」

> 🔍 高端点评──道路在哪里
> 此案指向 Agent 最敏感的能力边界：**自动调整一致性与 RPO 的权衡**。降级同步策略意味着「我愿意承担几秒的数据丢失风险来换可用性」，这是传统上只有人类才敢签字的决定。把它交给 Agent，需要一份明确的、可审计的「业务愿意拿一致性换可用性到什么程度」契约。而防脑裂这件事告诉我们：Agent 在跨区灾难里最大的价值,有时是『劝住人类别乱切』——克制，将成为下一代运维 Agent 最难训练的美德。

## 情境 25　Longhorn/Rook-Ceph 卡载(Stuck Volume)的无痛解除
**背景**：Kubernetes 集群用 Longhorn 提供 PV，有状态服务(StatefulSet)的数据库 Pod 挂载 RWO 卷。
**问题**：节点意外硬重启后，Pod 漂移到新节点却卡在 `ContainerCreating`，事件刷着 `Multi-Attach error: Volume is already exclusively attached to one node`。旧节点的 `VolumeAttachment` 对象因 kubelet 没能优雅卸载而成了**孤儿**，PV 死死绑在已不存在的旧节点上。数据库主 Pod 已下线 **14 分钟**，主从切换又因卷卡住无法完成,服务彻底躺平。
**需要的技能**：CSI Attach/Detach 生命周期、Longhorn 卷状态机、K8s finalizer 清理、StatefulSet 恢复编排。
**开源工具**：Longhorn、Kubernetes、`kubectl`、Longhorn Manager API。
**用到的 Agent 特性**：龙虾监测到 Pod `ContainerCreating` 超过 90 秒 + `Multi-Attach` 事件即触发，跑 ClawHub `stuck-volume-rescue` 技能。它**先验证安全前提**：通过 Longhorn API 确认旧节点确实已 NotReady 且该卷无实际写入挂载(避免双写毁数据)，才运行清理——删除孤儿 `VolumeAttachment`、移除卡住的 finalizer、触发 Longhorn detach，让卷释放给新节点 attach。本地脚本接着确认数据库 Pod `Running` 且通过 readiness 探针。Multi-Channel Gateway 全程把「孤儿 VA 已清、卷已重挂、DB 健康检查通过」推到 SRE 群并附事件时间轴。
**没有 Agent 的窘境**：工程师被 `Multi-Attach error` 吓到——这词自带「乱搞会双写爆数据」的警告，于是不敢动手，先翻 Longhorn 文档、再开会确认旧节点真的死透，半小时过去 Pod 还躺着。
**效益**：卡载卷解除 **MTTR 35 分钟 → 70 秒**；有状态数据库恢复时间从 40+ 分钟压进 2 分钟内。
> 💡 君之一席话
> 「`Multi-Attach error` 吓人的不是错误本身，是你不确定『旧节点到底死透没』——而确认这件事，正是 Agent 该替你扛的活。」

> 🔍 高端点评──道路在哪里
> 这条路通向「有状态工作负载的自愈」，是 K8s 运维里最后、也最硬的一块骨头。难点全在那句「先验证安全前提」：清理孤儿 VolumeAttachment 是一个只要前提判断错就会双写毁数据的高危动作，Agent 的价值不在『敢清』，而在『敢于确认到能清为止』。规模化后，Agent 需要一套跨 CSI 厂商(Longhorn/Rook/EBS)的统一卷状态抽象，否则每换一种保存后端，这套自愈逻辑就得重写一遍——标准化，会是这条路最大的拦路虎。

## 情境 26　MySQL 大表在线加索引导致主库锁表的滚动规避
**背景**：内核交易库一张 8 亿列的 `orders` 大表，PM 紧急要求加一个查找索引上线。
**问题**：某工程师图快，直接在主库跑 `ALTER TABLE ... ADD INDEX`，虽然 MySQL 8.0 号称 Online DDL，但这张表的 DDL 触发了 metadata lock 升级，后续所有对 `orders` 的读写**全部排队**。`SHOW PROCESSLIST` 里 `Waiting for table metadata lock` 堆到 3,000 条，主库 QPS 从 5 万腰斩到 800，下单页面开始转圈。
**需要的技能**：Online DDL 机制与限制、Metadata Lock 链分析、gh-ost cut-over 原子性与失败模式、binlog replay/DML buffer 监控、变更窗口调度。
**开源工具**：MySQL、gh-ost、pt-online-schema-change(Percona Toolkit)、Orchestrator。
**用到的 Agent 特性**：龙虾侦测到 `Waiting for table metadata lock` 计数暴增 + 一条长寿 DDL 连接持有 MDL，跑 ClawHub `ddl-guardian` 技能。它**第一时间止血**：kill 掉那条原生 ALTER 连接解除 MDL 雪崩；接着改用 gh-ost 重新编排——影子表 + binlog 回放无锁灌历史数据，期间用 row-copy 与 binlog apply 两条流并进。但龙虾不把 gh-ost 当「设一个 `--max-load` 就高枕无忧」的黑盒，它正面处理三个真实风险：
> **(1) cut-over 那一刻仍会锁**——gh-ost 的 cut-over 用 `LOCK TABLES` + 原子 RENAME 切换影子表，这一瞬间对原表是**独占 MDL，典型数十到数百毫秒**(表越热、需等 in-flight query 排空越久)。所以龙虾设 `--cut-over-lock-timeout-seconds=3`：抢不到锁就**自动放弃这次切换、原表毫发无伤、稍后重试**，而不是硬等到把在线请求堵死。
> **(2) 不靠 `--max-load` 赌运气，而是择时切换**——`--max-load Threads_running=50` 这个 50 并非魔法数字，是按该库历史「`Threads_running` 超过此值即出现明显争用(contention)」的 p95 反推的阈值，且它只控制**row-copy 的节流**、管不到 cut-over 的锁等待。所以龙虾挂上 `--postpone-cut-over-flag-file`：row-copy 跑完后**不自动切**，而是把 cut-over 卡在 flag file 后面，由它持续读主库负载曲线，等到一个真正的低谷(`Threads_running` 回落、无长事务、binlog 无突发)才删 flag 触发切换——**择时切换比靠 `--max-load` 赌一个随机时刻安全得多**。理想上整个变更直接排到离峰窗口跑，根本不在高峰赌。
> **(3) 监控 replay/DML buffer 防活锁**——灌历史数据的同时，在线 DML 不断产生新 binlog 要 apply；若此刻业务 DML 突增、apply 速度追不上产生速度，gh-ost 的待回放 buffer 会持续膨胀、永远收敛不到 cut-over 条件，形成**活锁**。龙虾盯着 gh-ost 的 `Lag`(影子表落后秒数)与 binlog apply 积压，一旦落后持续扩大就**主动再降 row-copy 速率**把带宽让给 replay，或直接暂停等 DML 洪峰过去。
>
> Multi-Channel Gateway 通报「原生 DDL 已中止、改用 gh-ost 后台跑、cut-over 设 3s 超时+人工/低谷择时切换、replay 落后监控中、预计离峰完成」，并 @ 那位手快的工程师做事后教学。
**没有 Agent 的窘境**：DBA 看到主库雪崩却不敢贸然 kill 那条 DDL(怕留半成品)，犹豫 5 分钟交易已损失数十万；就算改用 gh-ost，新手也常以为「设个 `--max-load` 就万无一失」，结果 cut-over 撞上高峰被一堆 in-flight query 卡住、或 DML 突增让 replay 永远追不上而活锁一整夜。
**效益**：MDL 雪崩止血 **18 分钟 → 35 秒**；8 亿列索引以 cut-over 数百毫秒的可控锁代价、在离峰择时完成，replay 不溢出、不活锁，主库 QPS 不再受影响。

> 💡 君之一席话
> 「『Online DDL』这个词最大的陷阱，是让你以为它对所有表、所有时刻都 online——而连 gh-ost 也没有真正『零锁』，它只是把那把不可避免的锁，压缩成你能挑时机、能放弃、能重试的几百毫秒。健壮性不在于消灭锁，而在于让锁发生在你选的时刻。」

> 🔍 高端点评──道路在哪里
> 此案把龙虾推向「变更守门员(Change Gatekeeper)」的角色——理想终局是危险的原生大表 DDL 在进主库前就被拦截、自动改写成 gh-ost 流程。但要诚实面对：cut-over 的那把 MDL 锁**无法消除，只能择时**，而「最低谷在哪、会不会刚挑中就来一波流量」本质是对未来几百毫秒的赌注——`--postpone-cut-over-flag-file` 把这个赌注交回人/Agent 择时，比 `--max-load` 赌随机时刻好，但仍不是零风险。更深的灰色地带是 replay 活锁：当业务 DML 持续高于 apply 能力，gh-ost 可能**永远跑不完**，这时唯一诚实的答案不是「再降速」，而是承认「此表此时段不适合在线变更，请排离峰维护窗」——把赌桌收起来，比优化赌技更安全。当 Agent 能可靠接管 schema 变更，DBA 的角色就从运行者升级为策略审核者；而把 kill 主库连接这种权限交给 Agent，依然需要一份写得清清楚楚的授权边界。

## 情境 27　Redis 缓存雪崩(Cache Avalanche)击穿主库的多级熔断
**背景**：高流量内容站，Redis 集群做热点数据缓存，TTL 统一设 1 小时，背后是单一 MySQL 主库。
**问题**：18:00 整点，一批同时写入的缓存 key **同一秒集体过期**，瞬间数十万请求全部穿透到 MySQL。主库连接数 1 秒内从 200 冲到上限 2,000，`Threads_running` 飙到 400，CPU 100%，缓存击穿演变成缓存雪崩——MySQL 开始拒连，连带把还没过期的缓存回填也卡死，整站进入死亡螺旋。
**需要的技能**：缓存失效模式(雪崩/击穿/穿透)辨识、热点 key 探测、互斥重建(mutex rebuild)、后端重载保护。
**开源工具**：Redis、`redis-cli --hotkeys`、Sentinel、Sentinel/Resilience4j 风格熔断(此处用 envoy 限流)。
**用到的 Agent 特性**：龙虾由「MySQL 连接数陡增 + Redis miss rate 飙升」双信号触发，跑 ClawHub `cache-avalanche-breaker` 技能，秒判这是「集体 TTL 同时到期」型雪崩。它打出组合拳：在接入层(Envoy)对穿透到 DB 的请求**启动排队限流**，只放一个请求去重建每个热 key(分布式互斥锁)、其余短暂返回 stale 缓存；本地脚本批量为回填的 key 注入**随机抖动 TTL**(3600±300s)以防下次再同步过期。子 Agent 持续监测主库 `Threads_running` 回落后逐步放开限流。Multi-Channel Gateway 同步「已对 DB 启动互斥重建限流、TTL 已加抖动」到值班群。
**没有 Agent 的窘境**：SRE 看到 MySQL 连接爆满先去扩连接池,结果扩了更多请求进来把主库彻底压死;绕了 20 分钟才反应过来根因在 Redis 整点集体过期。
**效益**：雪崩到熔断止血 **MTTR 20 分钟 → 40 秒**；主库重载窗口从 12 分钟缩到 30 秒,并从根上消除「整点集体过期」复发。

> 💡 君之一席话
> 「缓存的善意在于替主库挡子弹，但当所有缓存约好同一秒一起阵亡，它们就成了压垮主库的同一支军队。」

> 🔍 高端点评──道路在哪里
> 这条路指向「跨层(缓存↔数据库)的协同重载保护」——单看 Redis 或单看 MySQL 都救不了,Agent 的独特价值是同时握着两层的信号做联合决策。工程上的硬骨头是「放 stale 还是挡请求」的取舍,它与业务对数据新鲜度的容忍度强绑定,Agent 需要一份 per-endpoint 的「可接受 staleness」清单。更前瞻地看,给缓存 TTL 自动注入抖动这类「治本动作」一旦由 Agent 常态化运行,运维就从『扑灭雪崩』进化到『让雪崩在物理上无法发生』——这才是自动化的终点。

## 情境 28　误删数据的时间点恢复(PITR)与 binlog 精准回放
**背景**：营运后台一支脚本因 WHERE 条件写错,在生产库 `UPDATE users SET status=0` **漏掉了限定条件**,全表 200 万用户被一键停权。
**问题**：09:12 事故发生,客服电话 3 分钟内被打爆,200 万用户全部无法登录。直接从昨夜全量备份还原会丢掉一整个上午的真实业务写入,代价不可接受;必须做到「只回滚这一条误操作,保留其余所有正常交易」的外科手术式恢复。
**需要的技能**：时间点恢复(PITR)原理、binlog 事件解析与反向生成、影子库验证、最小化数据损失恢复。
**开源工具**：MySQL、Percona XtraBackup、my2sql/binlog2sql、mydumper。
**用到的 Agent 特性**：龙虾由「单条 SQL 影响行数 = 全表」的异常审计规则触发,跑 ClawHub `pitr-surgeon` 技能。它先定位那条灾难 SQL 在 binlog 中的精确 GTID 与时间戳(09:12:07),用 binlog2sql **反向生成回滚 SQL**(把 `status=0` 还原成事务前的原值),并在隔离的影子库先回放验证行数与抽样比对无误,才在主库运行补偿。整个过程**不碰其他 9:12 之后的正常写入**。本地脚本生成一份完整的「误操作影响清单 + 回滚 diff」。Multi-Channel Gateway 把「已定位误删 GTID、影子库验证通过、待人工最终批准运行回滚」推给 DBA 主管,**保留人类的最终确认权**。
**没有 Agent 的窘境**：DBA 在「全量还原丢半天数据」与「手写回滚 SQL 怕再错」之间天人交战,手动翻 binlog 找那条 SQL 的位置就花了 40 分钟,期间 200 万用户持续被锁在门外。
**效益**：误删定位到可运行回滚 **40+ 分钟 → 90 秒**;数据损失从「半天业务」降为「零」,恢复精度达单事务级。

> 💡 君之一席话
> 「一条漏写 WHERE 的 UPDATE,能在 0.3 秒内毁掉 200 万人的早晨——数据库从不问你是不是手滑,它只忠实地运行你的傲慢。」

> 🔍 高端点评──道路在哪里
> 此案最关键的设计是「Agent 备好回滚、人按下确认」——它划出了一条清晰的信任边界:**生成与验证可以自动,运行毁灭级补偿必须有人签字**。这条路指向「可逆运维」的理想:任何写操作都附带一份随时可运行的反向补偿。工程难点在 binlog 反向生成的完备性(触发器、级联、JSON 字段都是坑),以及影子库验证要快到能在事故窗口内完成。当这套能力成熟,DBA 面对误删时的心态会从『灾难』变成『撤销(Undo)』——而这正是 Agent 给人类运维最大的礼物:把不可逆,变回可逆。

## 情境 29　分布式交易帐本数据不一致的对账与最终一致性修复
**背景**：微服务架构下,订单服务与库存服务各自有库,靠本地消息表 + MQ 做最终一致性,理论上「下单成功必扣库存」。
**问题**：某次 MQ broker 滚动重启期间,部分「扣库存」消息既没成功投递、本地消息表的补偿任务也因 bug 没重试,出现 **2,317 笔「订单已成立但库存未扣」的灰色数据**。账面库存比实际多,超卖风险正在累积,而这种不一致**不会报错、不会告警**,它只是静静地躺在两个库之间,等着某天爆成一场超卖事故——这是分布式系统最阴险的灰色失败。
**需要的技能**：最终一致性对账(Reconciliation)、幂等补偿设计、跨服务数据 diff、灰色失败探测。
**开源工具**：PostgreSQL/MySQL、Debezium(CDC)、Apache Kafka、自建对账 job。
**用到的 Agent 特性**：龙虾运行 ClawHub `eventual-consistency-auditor` 技能,定时用 CDC 流把两库的「订单—库存」事件做双向 diff,主动捞出那 2,317 笔对不上的记录(而非等它爆)。它对每笔做**幂等补偿**:核对订单确实有效后,重新触发一次带幂等键的扣库存,避免重复扣。对于 diff 中「订单侧无效但库存已扣」的反向不一致,则生成退补单。子 Agent 把无法自动判定的疑难案例(如订单状态本身就矛盾)单独归档。Multi-Channel Gateway 把「对账发现 2,317 笔不一致、自动修复 2,290 笔、27 笔需人工」做成日报推给财务与业务 owner。
**没有 Agent 的窘境**：根本没人知道有不一致——直到某热销商品超卖、用户付了款却发不出货,才回头挖出三周前那次 MQ 重启,人工写 SQL 对账捞了整整两天。
**效益**：灰色不一致从「事后三周才暴雷」变为「T+1 主动发现」;自动修复率 98.8%,超卖事故归零;人工对账从 2 天 → 后台无感运行。

> 💡 君之一席话
> 「分布式系统里最危险的数据,不是错误的数据,是那些不报错、不告警、安静躺在两个库之间等着爆炸的『对不上』。」

> 🔍 高端点评──道路在哪里
> 这是整章最能体现「灰色失败(Grey Failure)」哲学的案例——故障不是崩溃,而是两个库各自正常、合起来却说谎。龙虾在这里的角色从『救火员』彻底转为『常驻稽核员』,这指向 Agent 最有价值的未来形态:**主动巡检而非被动告警**。工程上的真难题是幂等补偿的正确性——补偿本身若不幂等,Agent 就会从修复者变成放大器。规模化后,对账规则的维护(什么叫『一致』)会变成业务与 Agent 之间持续协商的活契约,而给 Agent 自动运行『退补单』这类涉及金钱的补偿权,将是信任边界被推得最远、也最需要审计留痕的一步。

## 情境 30　时序数据库(TSDB)基数爆炸(Cardinality Explosion)的标签治理
**背景**：可观测性平台用 Prometheus/VictoriaMetrics 存全公司指针,某团队新上线服务时把 `user_id`、`request_id` 当作 label。
**问题**：02:50,监控自身的监控告警:VictoriaMetrics 的 active time series 在 30 分钟内从 800 万暴涨到 **1.2 亿**,内存 OOM 连环重启,查找延迟从 200ms 飙到 30 秒,整个告警系统——这个本该最后倒下的系统——自己先瞎了。根因是高基数 label 让每个唯一 `request_id` 都生成一条独立时间串行,基数呈组合爆炸。
**需要的技能**：时序数据模型与基数原理、高基数 label 归因、指针 relabel/drop 治理、TSDB 容量保护。
**开源工具**：VictoriaMetrics/Prometheus、`vmui`/TSDB status API、Grafana、vmagent relabel。
**用到的 Agent 特性**：龙虾由「active series 增速异常 + TSDB 内存水位」触发,跑 ClawHub `cardinality-buster` 技能,查 TSDB status API 的 top cardinality 报表,40 秒内归因到凶手 metric 的 `request_id` label。它**就地止血**:在 vmagent/Prometheus 的 relabel_config 动态下发一条 `labeldrop`/`drop` 规则,挡掉该高基数 label 的摄入,让基数停止增长、内存回稳;对已写入的爆炸串行挂上加速过期。本地脚本生成「Top 10 高基数 metric/label」清单。Multi-Channel Gateway 把「已 drop 凶手 label、active series 止涨于 1.2 亿、预计 X 小时回落」推到平台群,并 @ 那个把 `request_id` 当 label 的团队附上指针设计规范链接。
**没有 Agent 的窘境**：监控平台自己 OOM,SRE 连 Grafana 都打不开、查不了到底哪个指针爆基数,只能盲目扩内存治标;等手动定位到凶手 label 已是一个多小时后,期间全公司告警「失明」。
**效益**：基数爆炸归因止血 **MTTR 60+ 分钟 → 50 秒**;避免监控系统自身崩溃导致的全公司「告警失明」窗口。

> 💡 君之一席话
> 「当监控系统自己被一个 `request_id` 标签撑爆,你才会懂:守望者也需要被守望——而最先该被治理的高基数,往往是工程师的随手一写。」

> 🔍 高端点评──道路在哪里
> 此案的妙处在于受害者正是监控本身——它逼我们直面「谁来监控监控者」的元问题,而 Agent 恰好能站在这个盲区里出手。这条路指向「可观测性的自我治理」:Agent 不只救火,还把高基数 label 的设计反模式反向推回开发流程(commit 前就拦)。工程难题在于 `drop` label 是个破坏性决定——它会永久丢失某个维度的可观测性,Agent 必须分清「失控的 request_id」与「业务真正需要的高基数维度」。规模化后,指针的『基数预算』会像成本预算一样需要被分配与问责,而 Agent,将是那个既发告警单、又默默帮你把预算守住的人。
