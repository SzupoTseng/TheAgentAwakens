# 代理覺醒 · The Agent Awakens

<p align="center">
  <img src="TheAgentAwakens.png" alt="代理覺醒 · The Agent Awakens — 封面海報 / cover poster" width="620">
</p>

**🌐 Language / 語言：[繁體中文](#繁體中文) · [English](#english) · [简体中文](#简体中文) · [日本語](#日本語)**

---

<a id="繁體中文"></a>
## 繁體中文

> **龍蝦 OpenClaw 與 Hermes Agent，兩種 AI Agent 設計哲學，以及 SRE / 半導體實戰百景。**

二〇二五年底，一隻叫 **OpenClaw（龍蝦 🦞）** 的開源 AI 代理在 GitHub 爆紅——牠能一口氣串起二十幾種通訊軟體、靠社群技能庫接上整個網路，**廣度驚人**，卻每天失憶、外掛還會夾毒。於是「**棄蝦養馬**」的風潮悄悄颳起：那匹馬，是主打「越用越省、越用越懂你」的 **Hermes Agent（愛馬仕 🐴）**。

這本書，寫給站在這個十字路口的你。它不是行銷文，也不替任何一邊傳教，只做三件事：**拆解兩種哲學、給出開機 SOP、再以一位 Google L7 SRE 的視角走過約 300 個真實戰場**——從多雲網路、金絲雀發布、混沌工程，到晶圓廠機台、研發 HPC。

> 💡 **全書的核心命題**
> 自動化的盡頭，不是「沒有人」，而是「**人只需要做最後那個決定**」。

### 兩種哲學，一張表看懂

| 維度 | 🦞 OpenClaw（龍蝦） | 🐴 Hermes Agent（愛馬仕） |
|------|------------------|------------------------|
| 核心信仰 | **廣度優先**：能連的越多越好 | **深度優先**：自主學習與長期記憶 |
| 技能系統 | 社群人工編寫，13,000+ 現成技能 | AI 依你的工作流**自動寫出**技能 |
| 記憶 | 單次會話為主，容易失憶 | 長期記憶，越用越懂你 |
| 成本 | 每次重餵脈絡，Token 費較高 | 優化解題流程，實測可省約 90% |

### 三篇結構

| 篇 | 內容 |
|----|------|
| **第一篇 兩種哲學** | 棄蝦養馬、龍蝦 OpenClaw、Hermes 自我進化（`00`–`03`） |
| **第二篇 開機儀式** | 一行指令把代理裝進電腦：Linux / macOS / WSL2 / Windows（`04`） |
| **第三篇 實戰百景** | SRE（`05`–`14`）· 晶圓廠 Fab（`15`–`24`）· 研發 Lab（`25`–`34`） |
| **附錄** | A 情境總索引 · B 開源工具速查 · **C 資深工程師的現實校準** |

每個情境採同一副骨架：**背景 → 問題 → 需要的技能 → 開源工具 → 用到的 Agent 特性 → 沒有 Agent 為什麼不方便 → 帶來的效益**，末附一句「君之一席話」。

### 這本書給誰

要決定「該養哪一隻 Agent」的工程師；想知道 Agent 在多雲、混沌工程、晶圓廠、研發 HPC 等戰場上**能做到哪、做不到哪**的人。附錄 C 更替你補上「快樂路徑」之外的現實校準——六條讓自主行動安全落地的鐵律。

### 怎麼讀 / 怎麼建置

照順序讀完哲學，或直接翻到讓你半夜睡不著的那個情境——每一景都自成一篇。建置為純 Python、無第三方依賴：

```bash
python _build.py            # 合併單檔 .md + 帶側欄目錄的 .html（PDF 由 HTML 列印）
```

### 語言版本

| 語言 | 狀態 | 位置 |
|------|------|------|
| 繁體中文 | ✅ 完成 | 倉庫根目錄 |
| English | ✅ 完成 | [`en/`](en/) |
| 简体中文 | ✅ 完成 | [`cn/`](cn/) |
| 日本語 | 🚧 規劃中 | — |

---

<a id="english"></a>
## English

> **Two AI-agent design philosophies — OpenClaw vs. Hermes Agent — and a hundred real-world battles across SRE and semiconductors.**

In late 2025 an open-source AI agent called **OpenClaw (the Lobster 🦞)** went viral on GitHub. It could wire together two dozen messaging platforms and reach the entire web through a community skill library — **breathtaking breadth** — yet it forgot everything daily and its plugins shipped malware. So a quiet shift began, "**drop the lobster, raise the horse**": that horse is **Hermes Agent (🐴)**, built on the promise of *the agent that grows with you*.

This book is for anyone standing at that crossroads. It isn't marketing and it preaches for neither side. It does three things: **dissect the two philosophies, give you a one-line install SOP, and walk ~300 real battlefields through the eyes of a Google L7 SRE** — from multi-cloud networking, canary releases and chaos engineering to fab tools and R&D HPC.

> 💡 **The book's central thesis**
> The end of automation isn't "no humans" — it's "**a human only has to make the final call**."

### Two philosophies at a glance

| Dimension | 🦞 OpenClaw (Lobster) | 🐴 Hermes Agent |
|-----------|----------------------|-----------------|
| Core belief | **Breadth first** — connect to everything | **Depth first** — self-learning & long-term memory |
| Skills | 13,000+ community-written, ready-made | **Auto-written** by the AI from your workflow |
| Memory | Mostly stateless, forgets context | Long-term memory, learns you over time |
| Cost | Re-feeds context every time, higher tokens | Optimizes the loop, ~90% token savings measured |

### Structure

| Part | Contents |
|------|----------|
| **I — Two Philosophies** | Drop the lobster, OpenClaw, Hermes evolves (`00`–`03`) |
| **II — The Boot Ritual** | One command to install the agent: Linux / macOS / WSL2 / Windows (`04`) |
| **III — A Hundred Battles** | SRE (`05`–`14`) · Fab (`15`–`24`) · R&D Lab (`25`–`34`) |
| **Appendices** | A index · B open-source toolkit · **C a senior engineer's reality check** |

Every scenario follows one skeleton: **context → problem → skills needed → open-source tools → agent capabilities used → why it's painful without an agent → the payoff**, closing with a one-line takeaway.

### Who it's for

Engineers deciding *which agent to raise*; readers who want to know what an agent **can and cannot do** across multi-cloud, chaos engineering, the fab floor and R&D HPC. Appendix C adds the reality beyond the happy path — six iron rules for letting autonomous action land safely in production.

### How to read / build

Read the philosophy in order, or jump straight to the scenario keeping you up at night — each stands alone. The build is pure Python with no third-party dependencies:

```bash
cd en && python _build.py   # merged .md + HTML with a sidebar TOC (PDF printed from HTML)
```

### Language editions

| Language | Status | Location |
|----------|--------|----------|
| 繁體中文 (Traditional Chinese) | ✅ Done | repo root |
| English | ✅ Done | [`en/`](en/) |
| 简体中文 (Simplified Chinese) | ✅ Done | [`cn/`](cn/) |
| 日本語 (Japanese) | 🚧 Planned | — |

---

<a id="简体中文"></a>
## 简体中文

> **龙虾 OpenClaw 与 Hermes Agent，两种 AI Agent 设计哲学，以及 SRE / 半导体实战百景。**

二〇二五年底，一只叫 **OpenClaw（龙虾 🦞）** 的开源 AI 代理在 GitHub 爆红——它能一口气串起二十几种通讯软件、靠社群技能库接上整个网络，**广度惊人**，却每天失忆、插件还会夹带恶意代码。于是「**弃虾养马**」的风潮悄然刮起：那匹马，是主打「越用越省、越用越懂你」的 **Hermes Agent（爱马仕 🐴）**。

这本书，写给站在这个十字路口的你。它不是营销文，也不替任何一边布道，只做三件事：**拆解两种哲学、给出开机 SOP，再以一位 Google L7 SRE 的视角走过约 300 个真实战场**——从多云网络、金丝雀发布、混沌工程，到晶圆厂机台、研发 HPC。

> 💡 **全书的核心命题**
> 自动化的尽头，不是「没有人」，而是「**人只需要做最后那个决定**」。

### 两种哲学，一张表看懂

| 维度 | 🦞 OpenClaw（龙虾） | 🐴 Hermes Agent（爱马仕） |
|------|------------------|------------------------|
| 核心信仰 | **广度优先**：能连的越多越好 | **深度优先**：自主学习与长期记忆 |
| 技能系统 | 社群人工编写，13,000+ 现成技能 | AI 依你的工作流**自动写出**技能 |
| 记忆 | 单次会话为主，容易失忆 | 长期记忆，越用越懂你 |
| 成本 | 每次重喂上下文，Token 费较高 | 优化解题流程，实测可省约 90% |

### 三篇结构

| 篇 | 内容 |
|----|------|
| **第一篇 两种哲学** | 弃虾养马、龙虾 OpenClaw、Hermes 自我进化（`00`–`03`） |
| **第二篇 开机仪式** | 一行指令把代理装进电脑：Linux / macOS / WSL2 / Windows（`04`） |
| **第三篇 实战百景** | SRE（`05`–`14`）· 晶圆厂 Fab（`15`–`24`）· 研发 Lab（`25`–`34`） |
| **附录** | A 情境总索引 · B 开源工具速查 · **C 资深工程师的现实校准** |

每个情境采用同一副骨架：**背景 → 问题 → 需要的技能 → 开源工具 → 用到的 Agent 特性 → 没有 Agent 为什么不方便 → 带来的效益**，末附一句「君之一席话」。

### 这本书给谁

要决定「该养哪一只 Agent」的工程师；想知道 Agent 在多云、混沌工程、晶圆厂、研发 HPC 等战场上**能做到哪、做不到哪**的人。附录 C 更替你补上「快乐路径」之外的现实校准——六条让自主行动安全落地的铁律。

### 怎么读 / 怎么构建

按顺序读完哲学，或直接翻到让你半夜睡不着的那个情境——每一景都自成一篇。构建为纯 Python、无第三方依赖：

```bash
cd cn && python _build.py   # 合并单档 .md + 带侧栏目录的 .html（PDF 由 HTML 打印）
```

> 简体中文版由繁体中文版以 OpenCC（tw2sp，含台湾用语转大陆用语）转换生成；转换脚本见仓库根目录 `_convert_cn.py`。

---

<a id="日本語"></a>
## 日本語

> **OpenClaw と Hermes Agent ——二つの AI エージェント設計思想、そして SRE と半導体の実戦百景。**

二〇二五年末、**OpenClaw（ロブスター 🦞）** という名のオープンソース AI エージェントが GitHub で大ブレイクした。二十数種のメッセージアプリを一挙につなぎ、コミュニティのスキルライブラリでウェブ全体に手を伸ばす——その**広さは驚異的**。だが毎日記憶を失い、プラグインにはマルウェアが紛れ込んだ。こうして静かに「**ロブスターを捨て、馬を育てる**」潮流が起きる。その馬こそ、「使うほど賢く、あなたを理解する」を掲げる **Hermes Agent（🐴）** だ。

本書は、その岐路に立つあなたへ。マーケティングでも、どちらかの布教でもない。やることは三つ——**二つの思想を解剖し、ワンコマンドの導入 SOP を示し、Google L7 SRE の視点で約 300 の実戦場を巡る**。マルチクラウドネットワーク、カナリアリリース、カオスエンジニアリングから、ファブの装置、研究開発の HPC まで。

> 💡 **本書の中心命題**
> 自動化の終着点は「人がいない」ことではなく、「**人は最後の決断だけをすればよい**」ことだ。

### 二つの思想、一覧表で

| 観点 | 🦞 OpenClaw（ロブスター） | 🐴 Hermes Agent |
|------|------------------------|-----------------|
| 中核思想 | **広さ優先**：つなげるほど良い | **深さ優先**：自律学習と長期記憶 |
| スキル | コミュニティ手作り、13,000+ の既製品 | ワークフローから AI が**自動生成** |
| 記憶 | 単発セッション中心、忘れやすい | 長期記憶、使うほどあなたを理解 |
| コスト | 毎回文脈を再投入、トークン高め | ループを最適化、実測で約 90% 削減 |

### 三部構成

| 部 | 内容 |
|----|------|
| **第一部 二つの思想** | ロブスターを捨てる、OpenClaw、Hermes の進化（`00`–`03`） |
| **第二部 起動の儀式** | ワンコマンド導入：Linux / macOS / WSL2 / Windows（`04`） |
| **第三部 実戦百景** | SRE（`05`–`14`）· ファブ Fab（`15`–`24`）· 研究開発 Lab（`25`–`34`） |
| **付録** | A シナリオ索引 · B OSS ツール早見表 · **C ベテランエンジニアの現実補正** |

各シナリオは同じ骨格で展開する：**背景 → 課題 → 必要なスキル → OSS ツール → 使うエージェント機能 → エージェントが無いと何が辛いか → 得られる効果**、最後に一言のまとめ。

### 読者対象

「どのエージェントを育てるか」を決めたいエンジニア。マルチクラウド、カオスエンジニアリング、ファブ、研究開発 HPC でエージェントが**何をでき、何をできないか**を知りたい人。付録 C は「ハッピーパス」の先の現実——自律行動を安全に本番投入するための六つの鉄則を補う。

### 読み方 / ビルド

思想を順に読んでも、夜も眠れないあのシナリオに直行してもよい——どの景も独立している。ビルドは純粋な Python、サードパーティ依存なし：

```bash
python _build.py            # 単一 .md + サイドバー目次付き .html（PDF は HTML から印刷）
```

> 日本語版の原稿は計画中です。現時点では繁体字中文版をご覧ください。

---

## 教育・研究目的の声明 / Disclaimer

本書は教育および研究目的のみ。書中の OpenClaw / Hermes Agent / ClawHub 等の名称は叙述上の symbol です。
This work is for educational and research purposes only; the framework names herein are narrative symbols.
本书仅供教育与研究用途；书中框架名称为叙事示意。本書僅供教育與研究用途；書中框架名稱為敘事示意。
