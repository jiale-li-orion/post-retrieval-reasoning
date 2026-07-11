# Other Materials That May Help

This file aggregates literature notes and third-party repository READMEs for GPT decision context.

---


# Literature Notes


### AdaMEM: Test-Time Adaptive Memory for Language Agents

| 字段 | 内容 |
|------|------|
| **标题** | AdaMEM: Test-Time Adaptive Memory for Language Agents |
| **arXiv** | [2606.05684](https://arxiv.org/abs/2606.05684) |
| **日期** | 2026-06-04 |
| **会议** | **ICML 2026** |
| **标签** | memory, test-time adaptation, hybrid memory, long-horizon, ICML |

**作者与背景：**

| 作者 | 单位 |
|------|------|
| Yunxiang Zhang (一作) | University of Michigan (LAUNCH Lab) |
| Yiheng Li | University of Michigan |
| Ali Payani | Cisco Research |
| Lu Wang (通讯) | University of Michigan (LAUNCH Lab) |

**核心发现：**
- 现有记忆系统限制检索在 episode 初始化时执行，导致长程任务中策略逐渐与实际情况脱节
- 提出 AdaMEM：双层混合记忆架构，离线存储原始经验轨迹，在线动态合成短程策略记忆
- 三种推理模式（懒加载 / 主动刷新 / 每步刷新），支持 token 效率与自适应能力的权衡
- 提出 STEP-MFT：process-level filtering 训练策略，无需额外 critic 或 rollout 开销
- ALFWorld 相对提升最高 17%，WebShop 最高 13%，HotpotQA 持续领先静态基线
---

### SuperMemory-VQA: Egocentric VQA Benchmark for Long-Horizon Memory

| 字段 | 内容 |
|------|------|
| **标题** | SuperMemory-VQA: An Egocentric Visual Question-Answering Benchmark for Long-Horizon Memory |
| **arXiv** | [2606.00825](https://arxiv.org/abs/2606.00825) |
| **日期** | 2026-05-30 |
| **标签** | benchmark, VQA, egocentric, long-horizon, memory, ACM |

**作者与背景：**

| 作者 | 单位 |
|------|------|
| Samiul Alam (一作) | Ohio State University |
| Shakhrul Iman Siam | Ohio State University |
| Michael J. Proulx | — |
| James Fort | — |
| Richard Newcombe | **Meta Reality Labs** |
| Hyo Jin Kim | Meta Reality Labs |
| Mi Zhang (通讯) | Ohio State University |

**核心发现：**
- Benchmark，非方法论文
- 52.9 小时 Meta Aria Glasses 第一视角录制，4,853 个 QA 对
- 覆盖：物体/位置记忆、意图回忆、视觉场景回忆、时间线重建、对话记忆、上下文检索
- 每个问题带 "unanswerable" 选项测幻觉鲁棒性
- 现有 agent 框架和 LLM backbone 在此 benchmark 上表现均不理想

---

### MemConflict: Evaluating Long-Term Memory Systems Under Memory Conflicts

| 字段 | 内容 |
|------|------|
| **标题** | MemConflict: Evaluating Long-Term Memory Systems Under Memory Conflicts |
| **arXiv** | [2605.20926](https://arxiv.org/abs/2605.20926) |
| **日期** | 2026-05-20 |
| **标签** | benchmark, conflict, evaluation, temporal, retrieval |

**作者与背景：**

| 作者 | 单位 |
|------|------|
| Zhen Tao (一作) | 中国人民大学 (RUC) |
| Jinxiang Zhao | 中国人民大学 |
| Peng Liu | 中国人民大学 |
| Dinghao Xi | 上海财经大学 |
| Yanfang Chen | 中国人民大学 |
| Wei Xu | — |
| Zhiyu Li (通讯) | — |

**核心发现：**
- Benchmark，非方法论文。专注于记忆冲突场景
- 三类冲突：动态冲突（事实被更新）、静态冲突（错误不应覆盖正确）、条件冲突（多条有效记忆在不同条件下冲突）
- 从用户 profile 模拟多 session 历史，注入跨 session 冲突 + 语义干扰项
- 黑盒（答案对错）+ 白盒（检索召回和排序质量）
- 6 个记忆系统表现参差不齐，答案正确性与检索质量之间存在偏差
- 更长历史、更多干扰项、隐式 query、更大冲突距离 → 性能全面下降
- 失败原因：检索不到支撑记忆 / 检索到了但没用上

### MedMemoryBench: Benchmarking Agent Memory in Personalized Healthcare

| 字段 | 内容 |
|------|------|
| **标题** | MedMemoryBench: Benchmarking Agent Memory in Personalized Healthcare |
| **arXiv** | [2605.11814](https://arxiv.org/abs/2605.11814) |
| **日期** | 2026-05-12 |
| **会议** | **NeurIPS 2026 Datasets & Benchmarks Track** |
| **标签** | benchmark, healthcare, memory, medical, NeurIPS |

**作者与背景：**

| 作者 | 单位 |
|------|------|
| Yihao Wang (一作) | AQ-MedAI（阿里系医疗 AI） |
| 其余 12 位 | AQ-MedAI / 合作方 |

**核心发现：**
- 医疗垂直领域的 memory benchmark，NeurIPS 2026 DB Track 接收
- 20 个慢性病 persona，~2,020 个 session，~16,000 轮交互，~1,986 个查询
- 中英双语，时间跨度 12 个月，20.74M tokens
- 六类查询：实体匹配/时间定位/状态追踪/推理生成/选择题/多跳临床推理
- 提出"记忆饱和"（memory saturation）概念：持续信息输入会降低检索和推理鲁棒性
- "evaluate-while-constructing" 流式评估协议，模拟生产环境动态记忆积累
- 14 个基线系统对比，涵盖 Mem0、Letta、MemOS、GraphRAG、HippoRAG 等
- 发现主流架构在复杂医疗推理和噪声鲁棒性上存在严重瓶颈

**用途：** 医疗垂直领域 agent memory 评测基准。如果涉及医疗场景或高可靠性要求的记忆系统，可参考其"记忆饱和"评测方法和流式评估协议。14 个基线的对比结果可用作选型参考。

---

### 层级记忆结构三篇

| 标题 | arXiv | 会议 | 单位 |
|------|-------|:----:|------|
| StructMem: Structured Memory for Long-Horizon Behavior in LLMs | [2604.21748](https://arxiv.org/abs/2604.21748) | **ACL 2026 Main** | 浙江大学 + 蚂蚁集团 |
| Hierarchical Long-Term Semantic Memory for LinkedIn's Hiring Agent | [2604.26197](https://arxiv.org/abs/2604.26197) | **KDD 2026 ADS** | LinkedIn |
| HiGMem: A Hierarchical and LLM-Guided Memory System | [2604.18349](https://arxiv.org/abs/2604.18349) | **ACL 2026 Findings** | — |
| APEX-MEM: Agentic Semi-Structured Memory with Temporal Reasoning | [2604.14362](https://arxiv.org/abs/2604.14362) | **ACL 2026 Main** | Amazon |
| HyperMem: Hypergraph Memory for Long-Term Conversations | [2604.08256](https://arxiv.org/abs/2604.08256) | **ACL 2026 Main** | 中科院信工所 + UCAS |

---

### Externalization in LLM Agents: A Unified Review

| 字段 | 内容 |
|------|------|
| **标题** | Externalization in LLM Agents: A Unified Review of Memory, Skills, Protocols and Harness Engineering |
| **arXiv** | [2604.08224](https://arxiv.org/abs/2604.08224) |
| **日期** | 2026-04-09 |
| **标签** | survey, externalization, memory, skills, protocols, harness |

**作者：** 21 位，通讯 Weinan Zhang（上海交通大学）

**核心：** 54 页综述。论述 LLM Agent 的能力正在从模型参数内部"外化"到记忆存储、可复用技能、交互协议和 harness 工程中。memory 外化跨时间的状态，skills 外化程序性知识，protocols 外化交互结构，harness 工程作为统一层协调它们。梳理了从 weights → context → harness 的历史演进。

---

### GSW: Episodic Memory for RAG with Generative Semantic Workspaces

| 字段 | 内容 |
|------|------|
| **标题** | Beyond Fact Retrieval: Episodic Memory for RAG with Generative Semantic Workspaces |
| **arXiv** | [2511.07587](https://arxiv.org/abs/2511.07587) |
| **日期** | 2025-11-10 (v2 2026-02-16) |
| **会议** | **AAAI 2026 Oral** |
| **标签** | episodic memory, RAG, generative, semantic workspace, AAAI |

**作者与背景：**

| 作者 | 单位 |
|------|------|
| Shreyas Rajesh (一作) | **UCLA** |
| Pavan Holur | UCLA |
| Chenda Duan | UCLA |
| David Chong | UCLA |
| Vwani Roychowdhury (通讯) | UCLA |

**核心发现：**
- 提出 Generative Semantic Workspace (GSW)：神经启发的生成式记忆框架，构建结构化、可解释的演化情境表示
- Operator 将输入映射为中间语义结构，Reconciler 整合到持久工作空间中，强制时间/空间/逻辑一致性
- EpBench（100k-1M tokens）上超越 RAG 基线最高 **20%**
- query-time context tokens 减少 **51%**
- 代码开源：github.com/roychowdhuryresearch/gsw-memory

---

### TruthfulRAG: Resolving Factual Conflicts in RAG with KGs

| 字段 | 内容 |
|------|------|
| **标题** | TruthfulRAG: Resolving Factual-level Conflicts in Retrieval-Augmented Generation with Knowledge Graphs |
| **arXiv** | [2511.10375](https://arxiv.org/abs/2511.10375) |
| **日期** | 2025-11-13 |
| **会议** | **AAAI 2026** |
| **标签** | RAG, conflict, knowledge graph, truthfulness, AAAI |

**作者与背景：**

| 作者 | 单位 |
|------|------|
| Shuyi Liu (一作) | — |
| Yuming Shang | — |
| Xi Zhang | — |

**核心发现：**
- 用知识图谱解决 RAG 中检索外部知识 vs LLM 内部知识的冲突
- 从检索内容提取三元组构建 KG，query-based 图检索定位冲突元素，熵基过滤缓解事实不一致
- AAAI 2026 接收

---

### Overcoming the Impedance Mismatch: FM × KG 的理论鸿沟

| 字段 | 内容 |
|------|------|
| **标题** | Overcoming the Impedance Mismatch: A Theoretical Roadmap for Fusing Foundation Models and Knowledge Graphs |
| **arXiv** | [2606.15656](https://arxiv.org/abs/2606.15656) |
| **日期** | 2026-04-21 |
| **会议** | **ACL 2026** Workshop on Towards Knowledgeable Foundation Models |
| **标签** | neuro-symbolic, KG, theory, impedance-mismatch, VSA, good-paper |

**作者与背景：**

| 作者 | 单位 | 角色 |
|------|------|------|
| Sahil Rajesh Dhayalkar (唯一作者) | **Brain Corporation** (Staff Autonomy Engineer) / ASU 硕士 | 工业界独立理论研究者，1300+ 商用机器人感知系统负责人，7 项美国专利 |

**核心贡献：**
- **形式化「阻抗失配」I**：将连续空间(FM)与离散图(KG)之间的结构扭曲量化为一个数学量，I≫1 证明完美融合不可能
- **三级整合层次 + 理论瓶颈：**
  - L1 词法注入 (RAG) → **O(b^k) > L** 词法瓶颈，上下文窗口必然截断推理路径
  - L2 表征对齐 (图嵌入) → **I ≥ Ω(log\|V\|)** Bourgain 定理保证拓扑坍缩随 |V| 增长
  - L3 架构整合 (图引导注意力) → **(A_soft)^k** softmax 泄漏 δ 指数级累积
- **三大不可解瓶颈：** 可微逻辑的诅咒（梯度饱和+逻辑等价性崩溃）、结构与几何干扰（连续空间无法隔离无关事实）、符号接地不对称性（唯一 ID vs 分布式 token）
- **路线图：** 结构化残差流（预训练）+ VSA 潜在子图注入（推理）+ 正交子空间编辑（更新）
- **暴论：** RAG 只是 superficial patch，不是真正解决 FM×KG 融合的方案

**评价：** 论文质量高。理论推导干净（Bourgain 定理、softmax 泄漏分析），批判有力（RAG 序列化图结构丢失数学原理），但纯理论无实验。ACL Workshop 篇幅受限（12页），意犹未尽。作者是工业界独立研究者，背景独特（机器人感知工程 × 理论深度学习）。

---

### Substrate Asymmetry in User-Side Memory: A Diagnostic Framework

| 字段 | 内容 |
|------|------|
| **标题** | Substrate Asymmetry in User-Side Memory: A Diagnostic Framework |
| **arXiv** | [2606.11712](https://arxiv.org/abs/2606.11712) |
| **日期** | 2026-06-10 |
| **代码** | [github.com/EpistemicaLab/substrate-asymmetry-memory](https://github.com/EpistemicaLab/substrate-asymmetry-memory) |
| **标签** | memory, personalization, diagnosis, LoRA, RAG, asymmetry, good-paper, notable-author |

**作者与背景：**

| 作者 | 单位 | 角色 |
|:----:|:----|:-----|
| Youwang Deng (唯一作者) | **Amazon SE II** / **EpistemicaLab** 创始人 | 独立研究者，北航→USC→Amazon，44页超详细实验 |

**核心发现：**
- **「个性化」不是单指标。** 分解为三个正交轴：行为一致性（风格）、事实存在性（记忆）、事实缺失性（弃权）
- **基底不对称：** γ-LoRA 学风格（+0.473 nat/tok）但编造（8.7% TPR），RAG 不学风格但会弃权（99.0% TPR）——同一训练历史，相反方向
- **因果机制：** L21-L35 q_proj 是承重波段——归零它们：absence-TPR ↑33pp, presence-TPR ↓20pp
- **对齐税：** 更强 RLHF (Llama-3.1) 加剧而非治愈不对称
- **路由是分类不是校准：** DistilBERT 看问题文本就胜过所有基于置信度的路由方案
- **LaMP-3 真实数据：** γ-LoRA 打不过多数类基线（31.5% vs 59.5%）——诊断出是 instruction-following collapse 而非基底失败

**评价：** 实验密度极高（44页），因果推断有说服力（band zeroing），对齐税概念有实用价值。作者是同一个人连发三篇的 Youwang Deng（EpistemicaLab）

---

### Entity Collision: Attributing Retrieval Lift in Agent Memory

| 字段 | 内容 |
|------|------|
| **标题** | Entity Collision: A Stratified Protocol for Attributing Retrieval Lift in Agent Memory |
| **arXiv** | [2605.29630](https://arxiv.org/abs/2605.29630) |
| **日期** | 2026-05-28 |
| **代码** | [github.com/youwangd/engram](https://github.com/youwangd/engram) |
| **标签** | retrieval, evaluation, benchmark, protocol, attribution, notable-author |

**作者：** Youwang Deng（同 #20 #21）

**核心发现：**
- 提出 entity-collision 评估协议：固定 BM25 基线 → 构造干扰项共享答案实体 token → 隔离可归因于编码器的检索增益
- **双轴模式：** 词法标签（service/tool）深度碰撞时哈希三元组就够用；意图标签（preference/project）需要密集编码器
- **反直觉：** BGE-large（1024d）在意图类胜出但在词法类反而输给 MiniLM（384d）——2.7 倍参数不保证全面优势
- 48页，26张结果表，37个可复现脚本

**评价：** 方法论文，解决的是「检索增益到底来自编码器还是词法泄漏」这个归因问题。不如前两篇惊艳但方法论干净。同系列三篇一起看可以全面了解 Youwang Deng 的能力范围。

---

#### 📌 作者追踪：Youwang Deng

| 时间 | 成果 | 作者位次 |
|:----:|:----|:--------:|
| 2026-05-28 | **Entity Collision** (#22)：检索增益归因协议 | 唯一作者 |

**身份路线图：** 北航 → USC CSSE 中心 → **Amazon SE II**（西雅图）→ **EpistemicaLab**（独立研究实验室，创始人）

**风格特征：**
- **白天大厂，晚上独立研究**——3 篇 arXiv 在 2 周内密集发表
- **反常识+实验驱动**——发现都从数据中长出来，而非从理论推下来
- **超长篇文档风**——44/21/48页，每篇都给你看全部细节和表格
- **博客也硬核**（youwangd.github.io）：《技能吞噬了框架》《MCP 税》《编排泡沫》——反跟风工程哲学
- 论元化能力出众（「别信模型，信结构」）——三篇论文共享同一个工程世界观

**标签：** `independent-researcher`, `anti-hype`, `verification-first`, `engineering-meets-theory`

---

### Memory is Reconstructed, Not Retrieved: Graph Memory for LLM Agents

| 字段 | 内容 |
|------|------|
| **标题** | Memory is Reconstructed, Not Retrieved: Graph Memory for LLM Agents |
| **arXiv** | [2606.06036](https://arxiv.org/abs/2606.06036) |
| **代码** | [github.com/Ji-shuo/MRAgent](https://github.com/Ji-shuo/MRAgent) |
| **日期** | 2026-06-05 |
| **会议** | **ICML 2026** |
| **标签** | memory, agent, graph, active-retrieval, neurosymbolic, good-paper |

**作者与背景：**

| 作者 | 单位 | 角色 |
|:----:|:----|:-----|
| Shuo Ji | NUS | 一作 |
| Yibo Li | NUS | |
| Bryan Hooi | NUS | |

**核心发现：**
- **主动记忆重建（Active Memory Reconstruction）**：检索不应该是推理前的单次匹配，而应是推理过程中多轮、动态的图遍历——每发现新线索就调整下一步检索方向
- **Cue-Tag-Content 三段式记忆架构：** 记忆不存 flat text，而是存为 (cue, tag, content) 三元组；cue 触发检索，tag 提供下一步关联线索，content 是实际内容
- **定理 4.1（形式化）：** 主动检索在预算 T ≥ 2 下严格比被动检索更具表达能力——存在被动检索解不了的任务，主动检索能解
- **Caroline/Nate 案例：** 被动检索只能找到"电竞比赛"相关片段，漏掉"七月"这个时间锚点；主动重建先定位 Nate 比赛 → 提取"七月"tag → 定位 Caroline 七月的行程
- **结果：** LOCOMO/LongMemEval 上比 RAG/A-Mem/MemoryOS/LangMem/Mem0 等最高提 **23%**，同时 token 消耗大幅降低（LongMemEval 上 118k vs A-Mem 的 632k）

**评价：** 和 #19 的讨论直接相关——主动重建不压平证据链，让 KG 成为 LLM 思考的接口而非外部证据投喂器。形式上逃掉了 #19 的大部分批判（L2/L3 不适用，L1 部分绕过）。但弊端也明显：路径依赖（早期决策失误不可逆）、推理深度=调用次数、依赖 tag 标注质量。ICML 2026 接收，审稿人认可方向。



### #24 — MemTrace: Tracing and Attributing Errors in LLM Memory Systems

| 字段 | 内容 |
|------|------|
| **标题** | MemTrace: Tracing and Attributing Errors in Large Language Model Memory Systems |
| **arXiv** | [2605.28732](https://arxiv.org/abs/2605.28732) |
| **日期** | 2026-05-27 |
| **代码** | [github.com/zjunlp/MemTrace](https://github.com/zjunlp/MemTrace) |
| **标签** | memory, error-tracing, attribution, benchmark, diagnosis, debugging |

**作者与背景：**

| 作者 | 单位 | 角色 |
|:----:|:----|:-----|
| Xinle Deng (一作) | **浙江大学** + 阿里巴巴 | Core Contributor |
| Ruobin Zhong | 浙江大学 | Core Contributor |
| Hujin Peng | 浙江大学 | Core Contributor |
| Ningyu Zhang (通讯) | 浙江大学 ZJUNLP | 教授，知名 LLM 知识方向团队负责人 |
| 其余 13 位 | 浙江大学 / 阿里巴巴集团 | — |

**单位：** 浙江大学 ZJUNLP 实验室 + 阿里巴巴集团校企合作，18 位作者，4 位 Core Contributor。

**核心发现：**

- **新问题定义：** LLM 记忆系统的错误追踪与归因（failure attribution）。与 stateless agent 不同，记忆系统的错误可能源于很久以前的构造/更新/删除操作，到后面才暴露——线性 log 不足以恢复因果路径。
- **执行图（Execution Graph）：** 将记忆 pipeline 转化为**有向无环操作-变量二分图**，显式记录变量如何被操作消费、修改、覆盖、传播。`smartcomment` 工具插桩实现，非侵入式。
- **MemTraceBench：** 从 Long-Context / RAG / Mem0 / EverMemOS 四个记忆系统 + LoCoMo / LongMemEval / RealMem 三个数据集收集，**160 个人工标注失败案例**（每个包含 QA、执行图、错误类型、故障操作、人工解释）。错误类型 7 类：Annotation / LLM-as-Judge / Extraction / Update / Retrieval / Response / Deletion。
- **MemTrace 方法：** 将归因转化为 agentic 图探索问题。混合检索初始化起点（RRF 融合稠密+稀疏）、迭代跟随信息流遍历子图、上下文窗口管理（分页/正则搜索/摘要）。变体 MemTrace-OBS 用全局正则搜索代替图遍历，省 token 但有损准确性。
- **结果：** 最差操作定位准确率严重偏低——**OIA 最高仅 46.25%**（GPT-5.4 + MemTrace-OBS），说明定位精确故障操作极其困难。错误类型预测（ETA）最高 53.75%。图遍历（MemTrace）在小模型上 ETA 明显优于搜索方式（GPT-4.1 mini: 36.46% vs 20.00%）。MemTrace-OBS 在 token 成本上优势巨大（长上下文子集仅 MemTrace 的 15.25% tokens）。
- **错误分布因记忆系统而异：** RAG 无 extraction error（没有 extraction 模块），EverMemOS extraction 极鲁棒但 retrieval 和 response 有问题，Mem0 extraction 丢细节+时间戳重分配错误，长上下文本质问题在上下文更新中信息丢失。所有系统都有 response error——即使用到了相关记忆，最终答案仍失败。
- **闭环应用：** 归因信号指导 prompt optimization，端任务提升最高 **7.62%**。
- **高价值发现：** LLM-as-Judge 判错极少，但过于严格——把正确的冗长/不够具体回答也判错。人工标注本身困难，三个数据集都有标注错误。

**评价：** 乌镇->浙大->阿里系标准校企产出，人多工程大。问题定义清晰（记忆系统的错误归因和 stateless agent 不同），实验设计全面但结果并不好（OIA 不到一半），说明问题难。闭环应用 7.62% 提升不算特别大（记忆系统本身效果就有限时这个幅度可能只是回到基线）。核心价值在于**打开了记忆系统可调试性（debuggability）这个方向**，给了形式化的问题定义和评测基准。

**用途：** 如果要搭建或评估记忆系统，MemTraceBench 可用作诊断工具集。但注意 benchmark 仅 160 例、7 类错误、假设 singleton decisive error set（实际可能多因一果）。

### [Related Work 合集] 记忆系统七篇

| 项目 | 论文 | GitHub | 会议 |
|------|------|--------|:----:|
| **A-Mem** | A-Mem: Agentic Memory for LLM Agents ([2502.12110](https://arxiv.org/abs/2502.12110)) | [WujiangXu/A-mem](https://github.com/WujiangXu/A-mem) | **NeurIPS 2025** |
| **mem0** | Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory ([2504.19413](https://arxiv.org/abs/2504.19413)) | [mem0ai/mem0](https://github.com/mem0ai/mem0) | **ECAI 2025** |
| **MemoryOS** | Memory OS of AI Agent ([2506.06326](https://arxiv.org/abs/2506.06326)) | [BAI-LAB/MemoryOS](https://github.com/BAI-LAB/MemoryOS) | **EMNLP 2025 Oral** |
| **HippoRAG 1** | HippoRAG: Neurobiologically Inspired Long-Term Memory for LLMs ([2405.14831](https://arxiv.org/abs/2405.14831)) | [OSU-NLP-Group/HippoRAG](https://github.com/OSU-NLP-Group/HippoRAG) | **NeurIPS 2024** |
| **HippoRAG 2** | From RAG to Memory: Non-Parametric Continual Learning for LLMs ([2502.14802](https://arxiv.org/abs/2502.14802)) | 同上 | **ICML 2025** |
| **MemPalace** | ❌ 无论文，纯工程产品 | [MemPalace/mempalace](https://github.com/MemPalace/mempalace) | — |
| **SimpleMem** | SimpleMem: Efficient Lifelong Memory for LLM Agents ([2601.02553](https://arxiv.org/abs/2601.02553)) | [aiming-lab/SimpleMem](https://github.com/aiming-lab/SimpleMem) | **ICLR 2026 Workshop** (MemAgents Oral / RSI Spotlight) |

**备注：**
- **A-Mem**：基于 Zettelkasten 原则的动态记忆组织，agent 驱动记忆管理。NeurIPS 2025。
- **mem0**：59k stars 的工业级记忆层。内存效率导向（91% p95 延迟降低，90%+ token 节省）。ECAI 2025。2026年4月发布新算法（single-pass ADD-only + entity linking + 多信号检索），LoCoMo 71.4→91.6。
- **MemoryOS**：类 OS 的分层存储架构（短/中/长期记忆），北京邮电大学 白婷团队，EMNLP 2025 Oral。1.5k stars。
- **HippoRAG 1 & 2**：神经科学启发的记忆框架，用 KG + Personalized PageRank 做多跳检索。OSU 俞  Su 组。v1 NeurIPS 2024，v2 ICML 2025。3.8k stars。
- **MemPalace**：56k stars，纯工程产品无对应论文。本地优先、逐字存储、pluggable 后端（ChromaDB/Qdrant/PGVector）。LongMemEval R@5=96.6%（零 LLM）。有 MCP server。
- **SimpleMem**：UNC Chapel Hill 姚华修组。三段式语义无损压缩（结构化压缩+在线合成+意图感知检索）。LoCoMo F1 43.24%，token 降 30×。也做了多模态扩展（Omni-SimpleMem）和自演化检索（EvolveMem）。ICLR 2026 Workshop 两连中。

---

### Mnemis: Dual-Route Retrieval on Hierarchical Graphs for Long-Term LLM Memory

| 字段 | 内容 |
|------|------|
| **标题** | Mnemis: Dual-Route Retrieval on Hierarchical Graphs for Long-Term LLM Memory |
| **arXiv** | [2602.15313](https://arxiv.org/abs/2602.15313) |
| **日期** | 2026-02-17 (v1), 2026-04-10 (v2) |
| **代码** | [github.com/microsoft/Mnemis](https://github.com/microsoft/Mnemis) |
| **会议** | **ACL 2026 Main Conference** |
| **标签** | memory, graph, dual-route, system-1, system-2, hierarchical |

**作者与背景：**

12 位作者，全部来自 **Microsoft**。代码仓库归 microsoft org。

| 作者 | 单位 | 角色 |
|:----:|:----|:-----|
| Zihao Tang (一作) | Microsoft | — |
| Xin Yu (通讯) | Microsoft | Corresponding Author |
| 其余 10 位 | Microsoft | — |

**核心发现：**

- **问题：** RAG / Graph-RAG 都是 similarity-based 检索（System-1），在需要全局推理或全面覆盖的场景下表现差。
- **Mnemis 双路架构：**
  - **System-1（相似性搜索）**：基于 base graph 的语义检索，和传统方法一样快
  - **System-2（Global Selection）**：在 hierarchical graph 上做 top-down 逐层遍历，在抽象语义层级上做全局选择，找回 System-1 遗漏但结构相关的记忆
  - 两个 graph 从同一记忆构建：base graph 负责细粒度语义关联，hierarchical graph 通过 Minimum Concept Abstraction + Many-to-Many Mapping + Compression Efficiency Constraint 三点约束保证层级质量
- **SOTA 结果：**
  - **LoCoMo：93.9**（GPT-4.1-mini）
  - **LongMemEval-S：91.6**（GPT-4.1-mini）
  - 全面超越所有对比方法（含 mem0、HippoRAG、MemoryOS 等）
- 基于 [Graphiti](https://github.com/getzep/graphiti) 实现。
- **ACL 2026 Main Conference 接收。**
- 代码开源但还比较早期（12 commits，96 stars，4 forks）。

**评价：** Microsoft 出品，ACL 2026 Main。System-1 + System-2 的提法不算新（Kahneman 框架），但落地干净——hierarchical graph 上做 top-down selection 而不是 flat retrieval，直觉上确实能弥补纯语义匹配的盲区。93.9 的 LoCoMo 分数是目前看到最高的（高于 mem0 新算法的 91.6）。但注意是用 GPT-4.1-mini 测的，和其他用不同 backbone 的对比需要谨慎。整体属于工程扎实、创新不过度夸张的论文。

---

### GrepSeek: Training Search Agents for Direct Corpus Interaction

| 字段 | 内容 |
|------|------|
| **标题** | GrepSeek: Training Search Agents for Direct Corpus Interaction |
| **arXiv** | 2605.29307 |
| **日期** | 2026-05-28 |
| **标签** | `search agent` `GRPO` `retrieval` `no-index` `shell search` |

**作者与背景：**

| 作者 | 单位 | 角色 |
|------|------|------|
| Alireza Salemi | UMass Amherst (CIIR) | 一作 |
| Chang Zeng | UMass Amherst (CIIR) | 合作 |
| Atharva Nijasure | Princeton | 合作 |
| Jui-Hui Chung | CMU | 合作 |
| Razieh Rahimi | Princeton | 指导 |
| Fernando Diaz | CMU | 指导 |
| Hamed Zamani | UMass Amherst (CIIR) | 通讯 |

**Affiliation:** Center for Intelligent Information Retrieval (CIIR) @ UMass Amherst + Princeton + CMU

**核心发现：**

- **核心思路：** 不做 RAG（检索器 + 读文档 → 答），而是训练一个小 LLM agent（Llama-3.2-3B）直接用 shell 命令（`rg`/`grep`）在语料库上搜索，像人一样翻找信息。
- **两阶段训练：**
  1. **SFT：** 用 GPT-4o 生成搜索轨迹（给 query → 预期搜索路径 → 预期答案）做监督微调。
  2. **GRPO RL：** 让 agent 自由探索搜索路径，根据最终答案正确性和搜索效率给 reward，学出有效的搜索策略。
- **结果：** 在 4/7 个公开域 QA 基准上达到 SOTA（NQ, HotpotQA, 2Wiki, MuSiQue），整体 micro-average F1 = 0.5691 最高。
- **效率：** sharded-parallel 执行加速 shell 检索 7.6x；每 query 平均 8.6s（A100）；不需要离线索引。
- **意义：** 证明了对于某些检索场景，放弃 dense retriever 的 embedding 匹配，直接用 agent + shell 搜索可能更优——特别是当语料中有大量不符合分布、embedding 难以泛化的文本时。

**Conference:** 未标注（2026年5月提交，可能还在审）

---

### Experience Compression Spectrum: Unifying Memory, Skills, and Rules in LLM Agents

| 字段 | 内容 |
|------|------|
| **标题** | Experience Compression Spectrum: Unifying Memory, Skills, and Rules in LLM Agents |
| **arXiv** | 2604.15877v1 |
| **日期** | 2026-04-17 |
| **标签** | `memory` `skill discovery` `experience compression` `survey` `unification` |

**作者与背景：**

| 作者 | 单位 | 角色 |
|------|------|------|
| Xing Zhang | AWS / HSBC（推测） | 一作 |
| Guanghui Wang | AWS / HSBC（推测） | 合作 |
| Yanwei Cui | AWS / HSBC（推测） | 合作 |
| Wei Qiu | AWS / HSBC（推测） | 合作 |
| Ziyuan Li | AWS / HSBC（推测） | 合作 |
| Bing Zhu | AWS / HSBC（推测） | 合作 |
| Peiyang He | AWS / HSBC（推测） | 合作 |

> 注：arXiv 页面未标注单位，第三方评论（alphaXiv）提及 "researchers at AWS and HSBC"。

**核心发现：**

- **核心主张：** 把 agent memory（记忆系统）和 agent skill discovery（技能发现）统一到一条"经验压缩谱系"上——episodic memory（5–20×压缩）、procedural skill（50–500×）、declarative rule（1000×+），三者只是压缩率不同的同一种能力。
- **跨社区隔离：** 对 22 篇主论文的 1,136 条参考文献做引用分析，发现记忆社区和技能社区互相引用率 **<1%**。记忆论文引用技能仅 0.7%（4/566），技能论文引用记忆仅 1.2%（7/570）。
- **Missing Diagonal（缺失对角线）：** 映射了 20+ 系统后，发现每个系统都在固定压缩级别上工作——**没有系统支持自适应跨级别压缩**（即根据经验价值自动选择存为记忆/技能/规则）。这是最大的空白。
- **四大发现：**
  1. 专业化不够——两个社区各自独立解决相同的子问题但不交换方案。
  2. 评估方法与压缩级别强绑定（不同级别的系统无法公平对比）。
  3. 可迁移性随压缩率上升但特异性下降（trade-off）。
  4. 知识生命周期管理（何时升级/降级/遗忘）基本被忽略。

**评价：** 这是一篇 survey/position paper，核心贡献不是新系统而是提供了一个统一框架。最有力的点是引用分析量化了社区隔阂（<1% 互相引用让人惊讶）。"Missing Diagonal" 的提法也很形象——确实现有系统都是设计时就定死了输出形式（记忆条目 vs 技能 vs 规则），缺乏自适应。但对工业界的 immediate impact 有限，更偏学术启发性。

---

### ATM-Bench / According to Me: Long-Term Personalized Referential Memory QA

| 字段 | 内容 |
|------|------|
| **标题** | According to Me: Long-Term Personalized Referential Memory QA |
| **arXiv** | 2603.01990 |
| **日期** | 2026-03-02 |
| **标签** | `benchmark` `memory QA` `personalized` `multimodal` `long-term` |

**作者与背景：**

| 作者 | 单位 | 角色 |
|------|------|------|
| Jingbiao Mei | University of Cambridge | 一作 |
| Jinghong Chen | University of Cambridge | 合作 |
| Guangyu Yang | University of Cambridge | 合作 |
| Xinyu Hou | University of Cambridge | 合作 |
| Margaret Li | University of Cambridge | 合作 |
| Bill Byrne | University of Cambridge | 通讯 |

**核心发现：**

- **ATM-Bench 定位：** 第一个多模态、多源的个性化指代性记忆 QA 基准。区别于已有基准（只测对话历史），ATM-Bench 覆盖 **~4 年真实生活记忆**，包含图像、视频、邮件三种来源，总计 ~12k 记忆条目和 ~1,038 条人工标注 QA 对。
- **挑战维度：**
  - **指代消解**（"Grace 想偷偷摸摸的时候的照片"）
  - **多证据组合**（~30% 的 QA 需要跨源推理）
  - **冲突证据处理**（新旧信息矛盾时怎么做）
  - **时空定位**（通过时间和地点线索回忆）
  - **有依据的弃权**（证据不足时应拒绝回答）
- **上下文规模：** 2.25M token（真正的 long-context 规模，不是短窗口）。
- **现有系统表现：** Hard 集上最好系统 **<20% 准确率**——说明现有记忆系统在真实个性化记忆场景下远不够用。
- **Schema-Guided Memory (SGM)：** 提出结构化记忆表示（按 Schema 组织多源记忆），优于之前常用的 Descriptive Memory 范式。

**Code & Data:** GitHub 开源 + HuggingFace 数据集 + 在线 Leaderboard

**评价：** 剑桥出品，项目工程化做得很完整（数据集、代码、leaderboard 都有）。最大的价值在于它定义了一个更真实的记忆评测场景——不是 synthetic 的对话摘要，而是真人 4 年跨模态数据。Hard 集 <20% 这个数字很有冲击力，说明个性化记忆是个 open problem。跟 LoCoMo 比，ATM-Bench 更侧重「个性化指代」和「真实性(真人数据)」，LoCoMo 更侧重「长故事叙事」。

---

### STALE: Can LLM Agents Know When Their Memories Are No Longer Valid?

| 字段 | 内容 |
|------|------|
| **标题** | STALE: Can LLM Agents Know When Their Memories Are No Longer Valid? |
| **arXiv** | 2605.06527 |
| **日期** | 2026-05-07 |
| **标签** | `memory staleness` `implicit conflict` `benchmark` `personalized memory` `state tracking` |

**作者与背景：**

| 作者 | 单位 | 角色 |
|------|------|------|
| Hanxiang Chao | Wuhan University | 共同一作 |
| Yihan Bai | Wuhan University | 共同一作 |
| Rui Sheng | HKUST | 合作 |
| Tianle Li | CUHK | 合作 |
| Yushi Sun | HKUST | 通讯 |

**Affiliation:** Wuhan University + CUHK + HKUST

**核心发现：**

- **核心问题：** 现有记忆 benchmark 只测静态事实检索，但 LLM agent 需要能**发现记忆过时了**——新的信息在没有明确否定旧信息的情况下就 invalidate 了之前的记忆（Implicit Conflict）。
- **STALE Benchmark：** 400 个专家验证的冲突场景，1,200 条评估 query（三个探测维度），覆盖 100+ 日常话题，上下文最长 150K tokens。
- **三维探测框架：**
  1. **State Resolution (SR)：** 能否发现旧 belief 已过时。
  2. **Premise Resistance (PR)：** 能否拒绝那些假设了过时状态的 query。
  3. **Implicit Policy Adaptation (IPA)：** 能否主动将更新后的状态应用到下游行为。
- **主要发现：** 最好的模型整体准确率仅 **55.2%**。模型经常接受用户 query 中隐含的过时假设；且模型难以识别「一个属性的变化应该级联失效相关的记忆」。
- **CUP-Mem：** 提出的原型方案，在 write 端通过结构化状态整合（structured state consolidation）和传播感知搜索（propagation-aware search）来加强记忆更新——即在写入时就判断新信息是否应该覆盖/级联更新已有记忆。
- **核心 insight：** "retrieving updated evidence ≠ acting on it"——检索到新证据不代表模型会用它。

**Code:** https://github.com/icedreamc/STALE（开源）

**评价：** 这篇抓住了记忆系统一个很实际但被忽视的问题——记忆会过期，而现有系统只检查"有没有"不检查"还对不对"。STALE 的三维探测设计得不错（SR/PR/IPA 区分了不同层次的失效感知能力）。CUP-Mem 的 write-time adjudication 思路也有道理（在写入时解决冲突比在读取时解决更可靠）。和 ATM-Bench (#29) 互补——ATM-Bench 测多模态个性化检索，STALE 测记忆时效性和冲突检测。

---

### Are LLMs Really Not Knowledgeable? Mining the Submerged Knowledge in LLMs' Memory

| 字段 | 内容 |
|------|------|
| **标题** | Are LLMs Really Not Knowledgeable? Mining the Submerged Knowledge in LLMs' Memory |
| **arXiv** | 2412.20846 |
| **日期** | 2024-12-30 |
| **会议** | **ICLR 2026** |
| **标签** | `LLM knowledge` `knowledge base` `latent knowledge` `Hits@k` `unsure suppression` |

**作者与背景：**

| 作者 | 单位 | 角色 |
|------|------|------|
| Xingjian Tao | HKUST (Guangzhou) | 一作 |
| Yiwei Wang | UC Merced | 合作 |
| Yujun Cai | The University of Queensland | 合作 |
| Zhicheng Yang | HKUST (Guangzhou) | 合作 |
| Jing Tang | HKUST (Guangzhou) / HKUST | 通讯 |

**核心发现：**

- **核心问题：** LLM 做 QA 时经常答错或说"不确定"，已有工作归因于参数知识缺失。这篇提出一个**互补现象**：LLM 其实存着正确答案，只是没有表达出来。
- **Hits@k 指标：** 不依赖表面答案正确性，检查正确答案是否出现在模型 top-k token 的概率分布中。LLaMA3 在 DBPedia 上 Hits@1 仅 17.2%（标准准确率），但 Hits@5 达到 57.9%——说明模型内部藏着大量知识但没有成功输出。
- **"Unsure" 抑制效应：** 允许模型输出"不确定"的 prompt 策略会**无意中抑制正确答案**——模型因为保守解码或过度谨慎的不确定阈值，选择不输出它实际知道的内容。
- **SkipUnsure 方法：** 通过过滤 uninformative tokens 来恢复被遮蔽的潜在知识，在 DBPedia 上准确率提升最高 11.8%，IMDB 上提升 6.3%。
- **关键 insight：** 正确知识的存储 ≠ 正确知识的表达。模型参数量大并不必然等于好的 QA 表现，解码策略和 prompt 设计对知识表达有显著影响。

**评价：** ICLR 2026 Poster。这篇的角度很有意思——不是"模型不知道"，而是"模型知道但不说"。Hits@k 作为诊断指标很有价值，可以帮人判断一个模型是真的不知道还是表达不出来。不过 SkipUnsure 更多是分析工具而非部署方案（作者也承认了），实际价值在于揭示了 prompt/decoding 对知识 recall 的抑制效应。跟常见的"模型幻觉"文献形成互补视角。

---

### SURE-RAG: Sufficiency and Uncertainty-Aware Evidence Verification for Selective Retrieval-Augmented Generation

| 字段 | 内容 |
|------|------|
| **标题** | SURE-RAG: Sufficiency and Uncertainty-Aware Evidence Verification for Selective RAG |
| **arXiv** | 2605.03534 |
| **日期** | 2026-05-05 |
| **会议** | IEEE PRAI 2026（投稿） |
| **标签** | `RAG` `evidence verification` `selective answering` `abstention` `auditability` |

**作者与背景：**

| 作者 | 单位 | 角色 |
|------|------|------|
| Jingxi Qiu | Georgetown University | 一作 |
| Zeyu Han | 待确认 | 合作 |
| Cheng Huang | 待确认 | 通讯 |

> 注：一作 Jingxi Qiu 为 Georgetown 数据科学硕士；三位作者在 biomedical AI 方向亦有合作（视网膜血管分割等），可能来自 Georgetown 医学院或相关机构。arXiv 页面未明确列出单位全称。

**核心发现：**

- **核心问题：** RAG 中检索到相关段落 ≠ 段落足以支撑答案。现有 RAG 系统缺一层"证据充分性验证"——给定 q、候选答案 a、检索到的证据 E，判断证据是支持/反驳/不足，只有足够支撑才回答。
- **关键 insight：** 证据充分性是 **set-level 属性**而非 passage-level——缺跳（missing hops）和冲突（conflicts）无法通过独立 passage 打分检测出来。
- **SURE-RAG 方法：**
  - **Pair-level：** DeBERTa cross-encoder 对每个 (claim, passage) 对打分 → 输出 support/refute/neutral 分布
  - **Answer-level 聚合：** 聚合出 5 个可解释信号——coverage（覆盖度）、relation strength（关系强度）、disagreement（分歧）、conflict（冲突）、retrieval uncertainty（检索不确定性）
  - **三路决策：** Support → 答；Refute/Insufficient → 弃权
  - **完全可审计（auditable）：** 每个决策可追溯到哪些 passage 支持/反对
- **结果（HotpotQA-RAG v3）：** 校准后 Macro-F1 **0.9075**，远超 DeBERTa mean-pooling（0.6516）和 GPT-4o judge（0.7284），匹配 concat cross-encoder（0.8888）但完全透明可审计。30% coverage 下 unsafe 答案减少 37%。
- **HaluBench 对比：** SURE-RAG 在受控充分性验证上强，但在开放世界幻觉检测上不如 GPT-4o——证实两者是不同问题。

**评价：** 8页 short paper，工程扎实，适合 IEEE 风格的 conference。最核心的贡献是"检索 ≠ 验证"的框架和 set-level 聚合方法。可审计性是一个加分项——在需要合规的场景（医疗、金融）尤其有价值。局限在于只在受控 benchmark 上验证，且只测短答案多跳场景，长文本 claim 覆盖未验证。



### VikingMem: A Memory Base Management System for Stateful LLM-based Applications

| 字段 | 内容 |
|------|------|
| **标题** | VikingMem: A Memory Base Management System for Stateful LLM-based Applications |
| **arXiv** | 2605.29640 |
| **日期** | 2026-05-28（v1），2026-06-12（v3） |
| **标签** | `memory management` `vector database` `stateful LLM` `memory base` `temporal compression` |

**作者与背景：**

| 作者 | 单位 | 角色 |
|------|------|------|
| Jiajie Fu | Zhejiang University + ByteDance | 共同一作 |
| Junwen Chen | ByteDance | 共同一作 |
| Mengzhao Wang | Zhejiang University | 合作 |
| Aoxiang He | ByteDance | 合作 |
| Maojia Sheng | ByteDance | 合作 |
| Xiangyu Ke | Zhejiang University | 指导/合作 |
| Yifan Zhu | Zhejiang University | 合作 |
| Yunjun Gao | Zhejiang University | 通讯（教授） |

**Affiliation:** Zhejiang University (DBLAB, Prof. Yunjun Gao 组) + ByteDance 联合产出。Jiajie Fu 为浙大硕士，核心成员参与开源项目 OpenViking（22.6k stars）。

**核心发现：**

- **核心问题：** 现有 LLM memory 方案要么用简单的提取方法导致记忆不完整，要么用针对单一场景（如 chatbot）的 rigid prompt，缺乏通用性。需要一个通用的 data management 范式来管理长期交互的持久化状态。
- **Memory Base 范式：** 三个核心原则：
  1. **选择性提取（Selective Extraction）：** 从原始信息流中提取高价值记忆
  2. **有状态演化（Stateful Evolution）：** 记忆逐步摘要、修正、时间加权（优先近期）
  3. **通用抽象（Generalizable Abstraction）：** 可跨应用（教育、推荐、agent memory）迁移
- **VikingMem 实现：** 基于 VikingDB 向量引擎的端到端 Memory Base 管理系统。核心设计：
  - **Event-centric memory extraction：** 以事件为中心处理复杂信息流
  - **Entity 动态更新：** 实体被事件驱动更新，实现 stateful evolution
  - **时序压缩（Temporal Compression）：** 通过 topic-wise timeline + time-weighted recall，逐步产生高层次摘要记忆，优先近期内容，压缩和衰减旧内容
- **结果：** 在长期记忆 benchmark 上记忆检索有效度比 baseline 提升最多 **30%**，同时保持低延迟。



补充：

### Attractor Geometry of Transformer Memory: From Conflict Arbitration to Confident Hallucination

| 字段 | 内容 |
|------|------|
| **标题** | Attractor Geometry of Transformer Memory: From Conflict Arbitration to Confident Hallucination |
| **arXiv** | 2605.05686 |
| **日期** | 2026-05-07（v1），2026-05-14（v2） |
| **标签** | `attractor dynamics` `parametric memory` `working memory` `hallucination` `geometric margin` `mechanistic interpretability` |

**作者与背景：**

| 作者 | 单位 | 角色 |
|------|------|------|
| Qiyao Liang | MIT | 一作 |
| Risto Miikkulainen | UT Austin / Cognizant | 合作（进化计算/神经网络泰斗） |
| Ila Fiete | MIT | 通讯（计算神经科学教授） |

**核心发现：**

- **核心框架：** 将 LLM 的自回归生成建模为输入条件化的离散时间动力系统 h_{t+1} = F(h_t; x, y_≤t)。Parametric Memory（PM，权重中固化的事实）= 持久 attractor basins；Working Memory（WM，上下文信息）= transient steering。
- **两种失效模式：** Conflict（PM 与 WM 冲突时的竞争）和 Hallucination（query 事实从未被学到），两者都产生 confident output，output-based 监控对此盲视。
- **Jacobian 分解：** J = S + A，S 为对称部分（刻画局部收缩/扩张），A 为反对称部分（旋转/transport）。发现 VO 对称性强（φ≈0.59），QK 接近无结构（φ≈0），MLP 的 ‖S‖²_F 比其他模块大 25×——据此分配组件角色：QK routing、VO write-back、MLP basin shaping。
- **LoRA 因果干预验证：** 用 4 种 LoRA placement（QK-only / VO-only / MLP-only / Full）做 causal probe。Brittle PM 下：QK 保留 WM（99.5%）、VO 逐 digit 退化（digit 3 起）、MLP/Full 在 position 4-5 陡降；Robust PM 下：MLP/Full 达到 100% format-invariant PM 但 WM 掉到 0%（context deafness）。
- **几何 margin：** δ(x) = min_i ‖h(x) - m_i‖₂ 直接读出 hidden-state 到最近记忆 basin 的距离。在 synthetic 任务上 AUROC 0.993 vs entropy 0.968；在自然语言 factual query 上 AUROC 1.000 vs entropy 0.622——完美分离正确召回和幻觉。
- **LM head epistemic bottleneck：** 固定线性投影 W_U 将数千维的 representation geometry 压缩为 logit gap，basin proximity 信息在此过程中被擦除。Softmax 随规模扩大而饱和，使得 confident hallucination 比例 C = exp(-c/Δ̄) 随规模增长。
- **八步论证逻辑：** 定义 PM/WM → 动力系统建模 → attractor hypothesis → Jacobian 组件角色 → LoRA 因果干预 → 区分 conflict（basin competition）和 hallucination（basin absence）→ 几何 margin 检测 → LM head 信息瓶颈 + scaling law。完整且自洽。

**评价：** MIT（Qiyao Liang + Ila Fiete）+ UT Austin（Risto Miikkulainen）出品，论证质量极高。它的理论类型不是纯数学定理证明，而是"机制假设 → 可区分预测 → 因果干预 → 几何读出验证"的 mechanistic argument。每个概念都落到可操作的实验变量上：LoRA placement 检验组件角色、hidden-state margin 检验 basin occupancy、entropy 和 margin 的对比说明为什么 output-based 方法不可靠。文中提到的模型包含 Qwen 2.5 系列（验证了 scaling law）。

---

# ATM-Bench

<div align="center">

# ATM-Bench: Long-Term Personalized Referential Memory QA

**The first benchmark for multimodal, multi-source personalized referential memory QA over long time horizons (~4 years), with evidence-grounded retrieval and answering.**

[🇬🇧 English](README.md) • [🇨🇳 中文](README_zh.md)

[![arXiv](https://img.shields.io/badge/arXiv-2603.01990-b31b1b.svg?logo=arxiv&logoColor=white)](https://arxiv.org/abs/2603.01990)
[![Project Page](https://img.shields.io/badge/🌐_Project-atmbench.github.io-1f6feb.svg)](https://atmbench.github.io/)
[![Live Leaderboard](https://img.shields.io/badge/🏆_Leaderboard-Live-orange.svg)](https://atmbench.github.io/leaderboard.html)
[![Hugging Face](https://img.shields.io/badge/🤗_HuggingFace-Dataset-FFD21E.svg)](https://huggingface.co/datasets/Jingbiao/ATM-Bench)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[🚀 Quick Start](#-quick-start) • [🤖 Agent Results](#-general-purpose-agent-results) • [🧠 Memory Systems](#-memory-system-baseline-results) • [📊 Oracle / NIAH](#-oracle-and-niah-results) • [🏆 Live Leaderboard](https://atmbench.github.io/leaderboard.html) • [📖 Citation](#-citation)

</div>

<video src="https://atmbench.github.io/static/videos/ATM-Bench-demo.mp4" controls width="100%"></video>

> 📄 **Paper:** [According to Me: Long-Term Personalized Referential Memory QA](https://arxiv.org/abs/2603.01990)  
> 🌐 **Project Page:** [https://atmbench.github.io/](https://atmbench.github.io/)  
> 🏆 **Live Leaderboard:** [https://atmbench.github.io/leaderboard.html](https://atmbench.github.io/leaderboard.html)

## Table of Contents

- [🗓️ Timeline](#️-timeline)
- [🤖 General-Purpose Agent Results](#-general-purpose-agent-results)
- [🧠 Memory-System Baseline Results](#-memory-system-baseline-results)
- [📊 Oracle and NIAH Results](#-oracle-and-niah-results)
- [📋 Overview](#-overview)
- [🚀 Quick Start](#-quick-start)
- [📁 Repository Structure](#-repository-structure)
- [📚 Documentation](#-documentation)
- [📖 Citation](#-citation)
- [🔗 Links](#-links)
- [📝 License](#-license)

<a id="timeline"></a>
## 🗓️ Timeline

- **2026-03-03:** arXiv paper release ([2603.01990](https://arxiv.org/abs/2603.01990))
- **2026-03-04:** Initial codebase release, including baseline implementations for MMRAG, Oracle, NIAH, and four ported third-party baselines (A-Mem, HippoRAG2, mem0, MemoryOS).
- **2026-03-12:** Initial General-Purpose Agent benchmark results release for Claude Code, Codex, and OpenCode.
- **2026-03-12:** ATM-Bench data release on Hugging Face ([ATM-Bench](https://huggingface.co/datasets/Jingbiao/ATM-Bench)).
- **2026-03-13:** Fixed Opencode Token Accounting and updated OpenClaw results.
- **2026-05-15:** Released the MemPalace port and added memory-system comparison results.
- **2026-05-27:** Released the SimpleMem port and added memory-system comparison results.
- **2026-05-28:** Released the Pi Agent Benchmark results.
- **2026-05-30:** Released the General-Purpose Agent benchmark harness (`agent_systems/`) — isolated, per-question runners for Claude Code, Codex, Pi, OpenCode, and OpenClaw.
- **2026-06-07:** Updated with more NIAH results and analysis, including the SGM vs. Raw comparison across various multimodal answerers.

<a id="General-Purpose-Agent-results"></a>
## 🤖 General-Purpose Agent Results

> 🏆 **The most up-to-date numbers live on the [ATM-Bench Live Leaderboard](https://atmbench.github.io/leaderboard.html).** The static snapshot below may lag behind new submissions.

General-Purpose Agent results on ATM-Bench-Hard are summarized below. The QS score here uses `gpt-5-mini` as the primary judge.

| Agent | Model | QS (Acc.) ↑ | Total Tokens ↓ |
|-------|-------|------------:|---------------:|
| Claude Code | Claude Opus 4.6 | 33.8% | 4.9M |
| Claude Code | Claude Opus 4.7 | 39.5% | 5.0M |
| Claude Code | Claude Opus 4.7 (w/o SGM) | 23.1% | 17.0M |
| Claude Code | Claude Opus 4.8 | 41.6% | 4.4M |
| Codex | GPT-5.2 | 39.7% | 15.5M |
| Codex | GPT-5.2 (w/o SGM) | 16.3% | 22.2M |
| Codex | GPT-5.5 | 41.4% | 16.1M |
| OpenCode | GLM-5 | 27.0% | 16.9M |
| OpenCode | Qwen3.5-397B-A17B | 24.5% | 12.1M |
| OpenCode | Kimi K2.5 | 30.3% | 8.5M |
| OpenCode | Kimi K2.5 (w/o SGM) | 6.5% | 21.4M |
| OpenCode | MiniMax M2.5 | 22.9% | 14.5M |
| OpenCode | MiniMax M2.7 | 27.8% | 13.5M |
| OpenClaw 🦞 | Kimi K2.5 | 25.4% | 9.6M |
| Pi | GLM-5.1 | 38.8% | 8.2M |
| Pi | Kimi K2.5 | 37.8% | 9.9M |
| Pi | MiMo v2.5 | 36.1% | 18.2M |
| Pi | MiniMax M3 | 43.2% | 15.6M |
| Pi | Qwen3.6-27B | 38.5% | 7.1M |
| Pi | Qwen3.6-27B (w/o SGM) | 16.6% | 20.8M |

* All coding agents use their default configuration, including the reasoning effort.

The coding agents still struggle on ATM-Bench-Hard, although they perform much better than various agentic memory baselines.

To reproduce these runs, see the General-Purpose Agent harness under [`agent_systems/`](agent_systems/README.md), which provides isolated, per-question runners for Claude Code, Codex, Pi, OpenCode, and OpenClaw.

<a id="memory-system-baseline-results"></a>
## 🧠 Memory-System Baseline Results

Memory-system baselines below use `Qwen3-VL-8B-Instruct-FP8` as the answerer, `Qwen3-VL-2B-Instruct` as the memory processor. ATM-Bench-Hard uses the `atm-bench-hard` release set, the results may differ from the original preprint.

| System | Index Time (hr) ↓ | ATM-Bench QS ↑ | ATM-Bench Recall@10 ↑ | ATM-Bench-Hard QS ↑ | ATM-Bench-Hard Recall@10 ↑ |
|--------|------------------:|---------------:|----------------------:|--------------------:|---------------------------:|
| [A-Mem](https://github.com/WujiangXu/A-mem) | 12.6 | 44.8 | 66.4 | 9.9 | 31.7 |
| [mem0](https://github.com/mem0ai/mem0) | 16.7 | 43.5 | 61.9 | 9.2 | 23.7 |
| [MemoryOS](https://github.com/BAI-LAB/MemoryOS) | 36.6 | 47.2 | 59.2 | 13.7 | 32.7 |
| [HippoRAG2](https://github.com/OSU-NLP-Group/HippoRAG) | 1.5 | 42.9 | 66.4 | 9.4 | 31.9 |
| [MemPalace](https://github.com/MemPalace/mempalace) | 0.5 | 56.8 | 76.4 | 9.7 | 28.3 |
| [SimpleMem](https://github.com/aiming-lab/SimpleMem) | 15.7 | 27.3 | 23.3 | 3.2 | 7.0 |
| **ATM-RAG (Ours)** | 0.5 | 51.0 | 68.7 | 8.4 | 28.8 |

<a id="oracle-and-niah-results"></a>
## 📊 Oracle and NIAH Results

We report QS for the Oracle ceiling and the NIAH haystack sweep (k=25/50/100) for multimodal answerers under both SGM and Raw (real images/video) settings, on the 31-question ATM-Bench-Hard split (`gpt-5-mini` judge).

For the full report, see the [ATM-Bench Live Leaderboard](https://atmbench.github.io/leaderboard.html).

### SGM

| Model | Context Window | Parameters | Oracle | NIAH-25 | NIAH-50 | NIAH-100 |
|-------|---------------:|------------|-------:|--------:|--------:|---------:|
| Qwen3-VL-8B-Instruct | 256K | 8B LM (~9B total) | 28.0 | 16.3 | 15.8 | 12.7 |
| MiniMax-M3 | 1M | Not disclosed | 60.5 | 45.9 | 55.1 | 43.4 |
| MiMo-V2.5 | 1M | 310B total / 15B active | 44.6 | 39.1 | 34.5 | 31.8 |
| Kimi-K2.5 | 256K | 1T total / 32B active | 41.9 | 47.9 | 39.6 | 33.5 |
| Qwen3.6-27B | 262K | 27B LM | 42.8 | 39.2 | 29.6 | 27.4 |
| ≈ input context depth | — | — | ≈4.5K | ≈12K | ≈22K | ≈44K |

### Raw (images/video)

| Model | Context Window | Parameters | Oracle | NIAH-25 | NIAH-50 | NIAH-100 |
|-------|---------------:|------------|-------:|--------:|--------:|---------:|
| Qwen3-VL-8B-Instruct | 256K | 8B LM (~9B total) | 40.1 | 25.4 | 24.9 | 10.9 |
| MiniMax-M3 | 1M | Not disclosed | 61.8 | 41.8 | 34.2 | 35.2 |
| MiMo-V2.5 | 1M | 310B total / 15B active | 52.1 | 43.3 | 33.1 | 23.6 |
| Kimi-K2.5 | 256K | 1T total / 32B active | 57.1 | 45.4 | failed | failed |
| Qwen3.6-27B | 262K | 27B LM | 62.3 | 50.5 | failed | failed |
| ≈ input context depth | — | — | ≈6.5K | ≈18K | ≈31K | ≈60K |

> **Why SGM, not raw?** Raw outperforms SGM at the Oracle ceiling. But that advantage collapses under realistic conditions: as the haystack fills with distractors, raw degrades and even fails (payload/context limits), and under agentic retrieval the gap is stark — every "w/o SGM" (raw) agent lands far below its SGM run. SGM is the representation that holds up once there is noise under realistic conditions.

> **failed** = the request exceeded the model's maximum allowed image/video count, or the API server's maximum upload/payload size, so that pool could not be served — a serving limit, not a model-quality result.



<a id="overview"></a>
## 📋 Overview

Existing long-term memory benchmarks focus primarily on dialogue history, failing to capture realistic personalized references grounded in lived experience. ATM-Bench addresses this gap with:

- 🖼️ **Multimodal and multi-source data:** Images, videos, emails
- 📅 **Long-term horizon:** ~4 years of personal memory
- 🎯 **Referential queries:** Resolving personalized references (e.g., "Show me the moments where Grace was trying to be sneaky...")
- 🔍 **Evidence-grounded:** Human-annotated QA pairs with ground-truth memory evidence
- 🧩 **Multi-evidence reasoning:** Queries requiring evidence from multiple sources
- ⚡ **Conflicting evidence:** Handling contradictory information

![ATM-Bench Overview](docs/images/ATM-Bench-Demo.png)

<a id="memory-ingestion"></a>
## Memory Ingestion

**Memory Ingestion** is decomposed into:

1. **Memory preprocessing** (how each memory item is represented)
2. **Memory organization** (how items are structured/linked)

<p align="center">
  <img src="docs/images/ATM-Method.png" alt="ATM Method" width="50%" />
</p>

### Memory Preprocessing
We compare two preprocessing representations:

- **Descriptive Memory (DM):** each memory item is represented as one natural-language description.
- **Schema-Guided Memory (SGM):** each memory item is represented with fixed text-based key-value fields under a schema.

In SGM, schema fields are modality-aware. For example:

- **Image/Video memory:** `time`, `location`, `entities`, `ocr`, `tags`
- **Email memory:** `time`, `summary`, `body`

DM and SGM contain the same underlying information but use different formats.

In this codebase, DM is implemented as caption/description-style text, while SGM is implemented as schema-based key-value text fields.

### Memory Organization
For organization of the memory store:

- **Piled Memory:** items are stored without explicit links.
- **Linked Memory:** items are linked with inferred relations (graph structure); agentic systems can additionally update existing items during organization.

<a id="niah-evaluation-setup"></a>
## NIAH Evaluation Setup

In addition to end-to-end retrieval + generation evaluation, we provide **NIAH (Needle In A Haystack)**:

- Each question is paired with a fixed evidence pool (`niah_evidence_ids`) that contains all ground-truth items.
- The rest of the pool is filled with realistic distractors.
- This isolates answer generation/reasoning quality from retrieval quality.

See:
- [`docs/niah.md`](docs/niah.md)


<a id="quick-start"></a>
## 🚀 Quick Start

### Download Dataset

ATM-Bench is hosted on Hugging Face at [`Jingbiao/ATM-Bench`](https://huggingface.co/datasets/Jingbiao/ATM-Bench). A one-shot script downloads the full released dataset and stages the files where the evaluation scripts expect them.

**Full download (~3.3 GB)** — includes QA, NIAH pools, preprocessed memory, emails, raw images, raw videos, and the GPS reverse-geocoding cache:

```bash
bash scripts/download_data.sh
```

This populates:

```
data/atm-bench/atm-bench.json
data/atm-bench/atm-bench-hard.json
data/atm-bench/niah/...
data/raw_memory/email/emails.json                   # emails
data/raw_memory/image/...                           # raw images
data/raw_memory/video/...                           # raw videos
data/raw_memory/geocoding_cache/...                 # GPS reverse-geocoding cache
output/image/qwen3vl2b/batch_results.json           # preprocessed image memory
output/video/qwen3vl2b/batch_results.json           # preprocessed video memory
```

The HF files `data/processed_memory/{image,video}_batch_results.json` are automatically renamed/copied into `output/image/qwen3vl2b/batch_results.json` and `output/video/qwen3vl2b/batch_results.json` by the script.

The script uses the `huggingface_hub` Python package (installed automatically if missing). If the dataset is private, run `huggingface-cli login` first.

### Installation

```bash
conda create -n atmbench python=3.11 -y
conda activate atmbench
pip install -r requirements.txt
pip install -e .
```

### API Keys

Set via environment variables:
```bash
export OPENAI_API_KEY="your-key"
export VLLM_API_KEY="your-key"
```

Or use local key files (gitignored):
- `api_keys/.openai_key`
- `api_keys/.vllm_key`

### Prepare Memory Files

Before running baselines, the image/video `batch_results.json` files must exist under `output/{image,video}/qwen3vl2b/`. You have two options:

**Option A (recommended): download the preprocessed memory from Hugging Face.**

If you already ran `bash scripts/download_data.sh` above, the preprocessed memory files are already staged at:

- `output/image/qwen3vl2b/batch_results.json`
- `output/video/qwen3vl2b/batch_results.json`

Nothing more to do — you can skip straight to the Quick commands.

**Option B: regenerate the memory files from raw images/videos.**

Only needed if you want to re-run preprocessing (for example, to try a different VLM or your own raw memory). Requires raw images under `data/raw_memory/image/` and videos under `data/raw_memory/video/`:

```bash
# Optional but recommended: preload reverse-geocoding cache
# Cache files are keyed by media filename stem, so the cache bundle must match
# the current image/video filenames.
bash scripts/memory_processor/image/copy_gps_cache.sh output/image/qwen3vl2b/cache
bash scripts/memory_processor/video/copy_gps_cache.sh output/video/qwen3vl2b/cache

# Generate memory itemization results
bash scripts/memory_processor/image/memory_itemize/run_qwen3vl2b.sh
bash scripts/memory_processor/video/memory_itemize/run_qwen3vl2b.sh
```


### Quick commands (MMRAG + Oracle)

```bash
# MMRAG (runs both ATM-bench and ATM-bench-hard)
#   Needs: `bash scripts/download_data.sh`
#        + a running vLLM endpoint at http://127.0.0.1:8000/v1/chat/completions
#          serving Qwen/Qwen3-VL-8B-Instruct-FP8 (override with VLLM_ENDPOINT /
#          ANSWERER_MODEL env vars).
bash scripts/QA_Agent/MMRAG/run.sh

# Oracle with Qwen3-VL-8B on raw images/videos (local upper bound)
#   Needs: `bash scripts/download_data.sh`
#        + a running vLLM endpoint serving Qwen/Qwen3-VL-8B-Instruct-FP8.
bash scripts/QA_Agent/Oracle/run_oracle_qwen3vl8b_raw.sh

# Oracle with GPT-5 on raw images/videos (no local GPU / vLLM)
#   Needs: `bash scripts/download_data.sh`
#        + OPENAI_API_KEY set in the environment or api_keys/.openai_key.
bash scripts/QA_Agent/Oracle/run_oracle_gpt5.sh
```

### Baseline Compatibility and Environments

- Core baselines (`MMRAG`, `Oracle`, `NIAH`) are tested in the main `atmbench` environment.
- Third-party memory-system baselines in this repo include:
  - `A-Mem`
  - `HippoRAG2`
  - `mem0`
  - `MemoryOS`
  - `MemPalace`
  - `SimpleMem`
- `MemoryOS` and `MemPalace` are strongly recommended to run in separate conda environments. `MemoryOS` uses a FAISS / sentence-transformers stack, while `MemPalace` uses ChromaDB / ONNX-backed local embeddings; isolating them avoids dependency collisions with the core baseline environment and each other.
- `A-Mem`, `HippoRAG2`, and `mem0` are tested to be compatible with the core baseline environment, but separate environments are still safer for reproducibility and dependency isolation.
- `SimpleMem` runs against a sibling clone of the upstream repo (LanceDB + Tantivy FTS stack); see [`memqa/qa_agent_baselines/SimpleMem/README.md`](memqa/qa_agent_baselines/SimpleMem/README.md). Pinned upstream commit: [`094027eca4c890dc9912be8cee1da04428de8076`](https://github.com/aiming-lab/SimpleMem/commit/094027eca4c890dc9912be8cee1da04428de8076) (verified by `scripts/QA_Agent/SimpleMem/run.sh`).
- Setup references for the vendored baselines are under `third_party/`:
  - `third_party/A-mem/`
  - `third_party/HippoRAG/`
  - `third_party/mem0/`
  - `third_party/MemoryOS/`
- `MemPalace` ships as a PyPI package (`mempalace==3.3.5`) and is installed via `memqa/qa_agent_baselines/Mempalace/requirements.txt` — no `third_party/` vendoring.
- `SimpleMem` is **not** vendored under `third_party/`. Clone the upstream repo at the pinned commit alongside ATMBench and point `SIMPLEMEM_DIR` at it (defaults to `../SimpleMem`):

  ```bash
  git clone https://github.com/aiming-lab/SimpleMem.git ../SimpleMem
  git -C ../SimpleMem checkout 094027eca4c890dc9912be8cee1da04428de8076
  pip install -r ../SimpleMem/requirements.txt
  pip install -r memqa/qa_agent_baselines/SimpleMem/requirements.txt
  ```
- The General-Purpose Agent evaluation harness for all five agents (Claude Code, Codex, Pi, OpenCode, OpenClaw) ships under [`agent_systems/`](agent_systems/README.md).

For detailed setup, data layout, and reproducibility settings, see:
- [`docs/README.md`](docs/README.md)
- [`docs/data.md`](docs/data.md)
- [`docs/reproducibility.md`](docs/reproducibility.md)
- [`docs/baseline.md`](docs/baseline.md)
- [`docs/niah.md`](docs/niah.md)

<a id="repository-structure"></a>
## 📁 Repository Structure

```
ATMBench/
├── memqa/              # Core memory QA implementation
├── scripts/            # Experiment scripts
├── docs/               # Documentation
├── data/               # Data directory (user-provided)
├── third_party/        # Vendored agentic memory systems
└── output/             # Experiment outputs (gitignored)
```

<a id="documentation"></a>
## 📚 Documentation

- [`docs/README.md`](docs/README.md) - Getting started guide
- [`docs/data.md`](docs/data.md) - Data format and preparation
- [`docs/baseline.md`](docs/baseline.md) - Baseline implementations
- [`docs/niah.md`](docs/niah.md) - NIAH protocol and usage
- [`docs/metrics.md`](docs/metrics.md) - Evaluation metrics
- [`docs/reproducibility.md`](docs/reproducibility.md) - Reproduction instructions
- [`docs/repo_structure.md`](docs/repo_structure.md) - Repository organization

<a id="citation"></a>
## 📖 Citation

If you use ATM-Bench in your research, please cite:

```bibtex
@article{mei2026atm,
  title={According to Me: Long-Term Personalized Referential Memory QA},
  author={Mei, Jingbiao and Chen, Jinghong and Yang, Guangyu and Hou, Xinyu and Li, Margaret and Byrne, Bill},
  journal={arXiv preprint arXiv:2603.01990},
  year={2026},
  url={https://arxiv.org/abs/2603.01990},
  doi={10.48550/arXiv.2603.01990}
}
```

<a id="links"></a>
## 🔗 Links

- 📄 **Paper:** https://arxiv.org/abs/2603.01990
- 🌐 **Project Page:** https://atmbench.github.io/
- 🏆 **Live Leaderboard:** https://atmbench.github.io/leaderboard.html
- 🤗 **Dataset:** https://huggingface.co/datasets/Jingbiao/ATM-Bench
- 💻 **Code:** https://github.com/JingbiaoMei/ATM-Bench
- 🐛 **Issues:** https://github.com/JingbiaoMei/ATM-Bench/issues

<a id="license"></a>
## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

# Mnemis

# Mnemis: Dual-Route Retrieval on Hierarchical Graphs for Long-Term LLM Memory
<div align="center" style="line-height: 1;">
  <a href="LICENSE" style="margin: 2px;">
    <img alt="License" src="https://img.shields.io/badge/License-MIT-f5de53?color=f5de53" style="display: inline-block; vertical-align: middle;"/>
  </a>
  <a href="https://arxiv.org/abs/2602.15313" style="margin: 2px;">
    <img alt="arXiv" src="https://img.shields.io/badge/arXiv-2602.15313-b31b1b.svg" style="display: inline-block; vertical-align: middle;"/>
  </a>
  <a href="https://huggingface.co/papers/2602.15313" style="margin: 2px;">
    <img alt="Hugging Face" src="https://img.shields.io/badge/🤗-HuggingFace-blue" style="display: inline-block; vertical-align: middle;"/>
  </a>
  <br>
</div>

## News
- 🎉🎉🎉 Apr 2026: Mnemis has been accepted to the ACL 2026 Main Conference!

--- 

## 1. Introduction
This is official repostory of paper "Mnemis: Dual-Route Retrieval on Hierarchical Graphs for Long-Term LLM Memory"

> **Abstract**: AI Memory, specifically how models organizes and retrieves historical messages,  becomes increasingly valuable to Large Language Models (LLMs), yet existing methods (RAG and Graph-RAG) primarily retrieve memory through similarity-based mechanisms. While efficient, such System-1-style retrieval struggles with scenarios that require global reasoning or comprehensive coverage of all relevant information. In this work, We propose Mnemis, a novel memory framework that integrates System-1 similarity search with a complementary System-2 mechanism, termed Global Selection. Mnemis organizes memory into a base graph for similarity retrieval and a hierarchical graph that enables top-down, deliberate traversal over semantic hierarchies. By combining the complementary strength from both retrieval routes, Mnemis retrieves memory items that are both semantically and structurally relevant. Mnemis achieves state-of-the-art performance across all compared methods on long-term memory benchmarks, scoring 93.9 on LoCoMo and 91.6 on LongMemEval-S using GPT-4.1-mini.

**Key Contributions**:
1. We introduce Mnemis, a novel framework that integrates System-1 similarity search with System-2 global selection to perform both semantic retrieval and deliberate, top-down reasoning over memory;
2. We improve the base graph extraction and construct a hierarchical graph for global selection, guided by Minimum Concept Abstraction, Many-to-Many Mapping, and Compression Efficiency Constraint to maintain hierarchical quality;
3. We perform comprehensive experiments to demonstrate the effectiveness of Mnemis. Mnemis achieves SOTA performance across all compared methods on long-term memory benchmarks, scoring 93.9 on LoCoMo and 91.6 on LongMemEval-S using GPT-4.1-mini.

## 2. Framework
Mnemis constructs two major components: a base graph and a hierarchical graph and two key memory retrieval mechanisms: System-1 Similarity Search and System-2 Global Selection.
<p align="center">
  <img width="85%" src="figures/figure_intro.png" alt="Mnemis Architecture">
</p>

**Detailed Blog**: `blog_mnemis.md`.

## 3. Evaluation Results
**LoCoMo Results**:
<p align="center">
  <img width="90%" src="figures/results_locomo.png" alt="LoCoMo Results">
</p>

**LongMemEval-S Results**:
<p align="center">
  <img width="90%" src="figures/results_lme_s.png" alt="LoCoMo Results">
</p>

**Human Evaluation Results**: `results\human_evaluation`


## 4. Case Studies
LoCoMo User 8 QA 11:
<p align="center">
  <img width="90%" src="figures/figure_case_0.png" alt="LoCoMo Results">
</p>

LongMemEval-S QA 262:
<p align="center">
  <img width="90%" src="figures/figure_case_1.png" alt="LongMem-S Results">
</p>

## 5. Reproduction
We implement Mnemis based on [Graphiti](https://github.com/getzep/graphiti). The core prompts used in our system are provided in the Appendix of the paper.

Evaluation results, along with the memory contexts generated by Mnemis, are available in the `results` directory. The implementation of global selection is provided in `global_selection`.

## 6. Citation
If you find this work useful, please cite it as follows::
```citation
@inproceedings{tang2026mnemis,
  title     = {Mnemis: Dual-Route Retrieval on Hierarchical Graphs for Long-Term LLM Memory},
  author    = {Tang, Zihao and Yu, Xin and Xiao, Ziyu and Wen, Zengxuan and Li, Zelin and Zhou, Jiaxi and Wang, Hualei and Wang, Haohua and Huang, Haizhen and Deng, Weiwei and Sun, Feng and Zhang, Qi},
  booktitle = {Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (ACL 2026)},
  year      = {2026},
  address   = {San Diego, California, USA},
  publisher = {Association for Computational Linguistics},
  note      = {Accepted to ACL 2026 Main Conference},
  url       = {https://arxiv.org/abs/2602.15313}
}
```

---

# OpenViking

<div align="center">

<a href="https://openviking.ai/" target="_blank">
  <picture>
    <img alt="OpenViking" src="docs/images/ov-logo.png" width="200px" height="auto">
  </picture>
</a>

### OpenViking: The Context Database for AI Agents

English / [中文](README_CN.md) / [日本語](README_JA.md)

<a href="https://www.openviking.ai">Website</a> · <a href="https://github.com/volcengine/OpenViking">GitHub</a> · <a href="https://github.com/volcengine/OpenViking/issues">Issues</a> · <a href="./docs">Docs</a>

[![](https://img.shields.io/github/v/release/volcengine/OpenViking?color=369eff\&labelColor=black\&logo=github\&style=flat-square)](https://github.com/volcengine/OpenViking/releases)
[![](https://img.shields.io/github/stars/volcengine/OpenViking?labelColor\&style=flat-square\&color=ffcb47)](https://github.com/volcengine/OpenViking)
[![](https://img.shields.io/github/issues/volcengine/OpenViking?labelColor=black\&style=flat-square\&color=ff80eb)](https://github.com/volcengine/OpenViking/issues)
[![](https://img.shields.io/github/contributors/volcengine/OpenViking?color=c4f042\&labelColor=black\&style=flat-square)](https://github.com/volcengine/OpenViking/graphs/contributors)
[![](https://img.shields.io/badge/license-AGPLv3-white?labelColor=black\&style=flat-square)](https://github.com/volcengine/OpenViking/blob/main/LICENSE)
[![](https://img.shields.io/github/last-commit/volcengine/OpenViking?color=c4f042\&labelColor=black\&style=flat-square)](https://github.com/volcengine/OpenViking/commits/main)

👋 Join our Community

📱 <a href="./docs/en/about/01-about-us.md#lark-group">Lark Group</a> · <a href="./docs/en/about/01-about-us.md#wechat-group">WeChat</a> · <a href="https://discord.com/invite/eHvx8E9XF3">Discord</a> · <a href="https://x.com/openvikingai">X</a>

<a href="https://trendshift.io/repositories/19668" target="_blank"><img src="https://trendshift.io/api/badge/repositories/19668" alt="volcengine%2FOpenViking | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>

</div>

***

✨ **May 2026 Update**: Updated OpenViking benchmark results across User Memory, Agent Memory, and Knowledge Base QA scenarios. → See [Evaluation Highlights](#evaluation-highlights).

## Overview

### Challenges in Agent Development

In the AI era, data is abundant, but high-quality context is hard to come by. When building AI Agents, developers often face these challenges:

- **Fragmented Context**: Memories are in code, resources are in vector databases, and skills are scattered, making them difficult to manage uniformly.
- **Surging Context Demand**: An Agent's long-running tasks produce context at every execution. Simple truncation or compression leads to information loss.
- **Poor Retrieval Effectiveness**: Traditional RAG uses flat storage, lacking a global view and making it difficult to understand the full context of information.
- **Unobservable Context**: The implicit retrieval chain of traditional RAG is like a black box, making it hard to debug when errors occur.
- **Limited Memory Iteration**: Current memory is just a record of user interactions, lacking Agent-related task memory.

### The OpenViking Solution

**OpenViking** is an open-source **Context Database** designed specifically for AI Agents.

We aim to define a minimalist context interaction paradigm for Agents, allowing developers to completely say goodbye to the hassle of context management. OpenViking abandons the fragmented vector storage model of traditional RAG and innovatively adopts a **"file system paradigm"** to unify the structured organization of memories, resources, and skills needed by Agents.

With OpenViking, developers can build an Agent's brain just like managing local files:

- **Filesystem Management Paradigm** → **Solves Fragmentation**: Unified context management of memories, resources, and skills based on a filesystem paradigm.
- **Tiered Context Loading** → **Reduces Token Consumption**: L0/L1/L2 three-tier structure, loaded on demand, significantly saving costs.
- **Directory Recursive Retrieval** → **Improves Retrieval Effect**: Supports native filesystem retrieval methods, combining directory positioning with semantic search to achieve recursive and precise context acquisition.
- **Visualized Retrieval Trajectory** → **Observable Context**: Supports visualization of directory retrieval trajectories, allowing users to clearly observe the root cause of issues and guide retrieval logic optimization.
- **Automatic Session Management** → **Context Self-Iteration**: Automatically compresses content, resource references, tool calls, etc., in conversations, extracting long-term memory, making the Agent smarter with use.

## Quick Start

### Local Deployment

#### Prerequisites

Before starting with OpenViking, please ensure your environment meets the following requirements:

- **Python Version**: 3.10 or higher
- **Rust Toolchain**: Cargo (Required for building RAGFS and CLI components from source)
- **C++ Compiler**: GCC 9+ or Clang 11+ (Required for building core extensions)
- **Operating System**: Linux, macOS, Windows
- **Network Connection**: A stable network connection is required (for downloading dependencies and accessing model services)

#### 1. Installation

##### Python Package

```bash
pip install openviking --upgrade --force-reinstall
```

##### Rust CLI (Optional)

```bash
npm i -g @openviking/cli
```

Or build from source:

```bash
cargo install --git https://github.com/volcengine/OpenViking ov_cli
```

#### 2. Model Preparation

OpenViking requires the following model capabilities:

- **VLM Model**: For image and content understanding
- **Embedding Model**: For vectorization and semantic retrieval

##### Supported VLM Providers

OpenViking supports multiple VLM providers:

| Provider       | Description              | Setup                                                                                                                                                                                                              |
| -------------- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `volcengine`   | Volcengine Doubao Models | [Volcengine Console](https://console.volcengine.com/ark/region:ark+cn-beijing/overview?briefPage=0\&briefType=introduce\&type=new\&utm_content=OpenViking\&utm_medium=devrel\&utm_source=OWO\&utm_term=OpenViking) |
| `openai`       | OpenAI Official API      | [OpenAI Platform](https://platform.openai.com)                                                                                                                                                                     |
| `openai-codex` | Codex VLM                | Use `openviking-server init`                                                                                                                                                                                       |
| `kimi`         | Kimi Code Membership     | Use `openviking-server init`                                                                                                                                                                                       |
| `glm`          | GLM Coding Plan          | Use `openviking-server init`                                                                                                                                                                                       |

##### Provider-Specific Notes

<details>
<summary><b>Volcengine (Doubao)</b></summary>

Volcengine supports both model names and endpoint IDs. Using model names is recommended for simplicity:

```json
{
  "vlm": {
    "provider": "volcengine",
    "model": "doubao-seed-2-0-pro-260215",
    "api_key": "your-api-key",
    "api_base": "https://ark.cn-beijing.volces.com/api/v3"
  }
}
```

You can also use endpoint IDs (found in [Volcengine ARK Console](https://console.volcengine.com/ark/region:ark+cn-beijing/overview?briefPage=0\&briefType=introduce\&type=new\&utm_content=OpenViking\&utm_medium=devrel\&utm_source=OWO\&utm_term=OpenViking):

```json
{
  "vlm": {
    "provider": "volcengine",
    "model": "ep-20241220174930-xxxxx",
    "api_key": "your-api-key",
    "api_base": "https://ark.cn-beijing.volces.com/api/v3"
  }
}
```

</details>

<details>
<summary><b>OpenAI</b></summary>

Use OpenAI's official API:

```json
{
  "vlm": {
    "provider": "openai",
    "model": "gpt-4o",
    "api_key": "your-api-key",
    "api_base": "https://api.openai.com/v1"
  }
}
```

You can also use a custom OpenAI-compatible endpoint:

```json
{
  "vlm": {
    "provider": "openai",
    "model": "gpt-4o",
    "api_key": "your-api-key",
    "api_base": "https://your-custom-endpoint.com/v1"
  }
}
```

</details>

<details>
<summary><b>OpenAI Codex (OAuth)</b></summary>

Use this provider when you want OpenViking to call Codex VLM through your ChatGPT/Codex OAuth session instead of a standard OpenAI API key:

```bash
openviking-server init
# choose OpenAI Codex when prompted
openviking-server doctor
```

```json
{
  "vlm": {
    "provider": "openai-codex",
    "model": "gpt-5.3-codex",
    "api_base": "https://chatgpt.com/backend-api/codex",
    "temperature": 0.0,
    "max_retries": 2
  }
}
```

> 💡 **Tip**:
>
> - `openai-codex` does not require `vlm.api_key` when Codex OAuth is available
> - OpenViking stores its own Codex auth state at `~/.openviking/codex_auth.json`
> - `openviking-server doctor` validates that the current Codex auth is usable

</details>

<details>
<summary><b>Kimi Coding (Subscription)</b></summary>

Use this provider when you want OpenViking to call the dedicated Kimi Coding subscription endpoint directly:

```bash
openviking-server init
# choose Kimi Coding when prompted
openviking-server doctor
```

```json
{
  "vlm": {
    "provider": "kimi",
    "model": "kimi-code",
    "api_key": "your-kimi-subscription-api-key",
    "api_base": "https://api.kimi.com/coding",
    "temperature": 0.0,
    "max_retries": 2
  }
}
```

> 💡 **Tip**:
>
> - `kimi` applies the recommended Kimi Coding defaults automatically, including the default Kimi Coding user agent
> - `kimi-code` and `kimi-coding` are accepted aliases for the provider name
> - `kimi-code` is normalized to Kimi's upstream coding model automatically

</details>

<details>
<summary><b>GLM Coding Plan (Subscription)</b></summary>

Use this provider when you want OpenViking to call Z.AI's OpenAI-compatible Coding Plan endpoint directly:

```bash
openviking-server init
# choose GLM Coding Plan when prompted
openviking-server doctor
```

```json
{
  "vlm": {
    "provider": "glm",
    "model": "glm-4.6v",
    "api_key": "your-zai-api-key",
    "api_base": "https://api.z.ai/api/coding/paas/v4",
    "temperature": 0.0,
    "max_retries": 2
  }
}
```

> 💡 **Tip**:
>
> - `glm`, `zhipu`, `zai`, `z-ai`, and `z.ai` all resolve to the same first-class GLM provider
> - The default endpoint is the Coding Plan endpoint, not the general Z.AI endpoint
> - Use a vision-capable model such as `glm-4.6v` or `glm-5v-turbo` for multimodal parsing

</details>

#### 3. Environment Configuration

##### Quick Setup for Local Models (Ollama)

If you want to run OpenViking with local models via [Ollama](https://ollama.ai), the interactive setup wizard handles everything automatically:

```bash
openviking-server init
```

The wizard will:

- Detect and install Ollama if needed
- Recommend and pull suitable embedding and VLM models for your hardware
- Generate a ready-to-use `ov.conf` configuration file

To validate your setup at any time:

```bash
openviking-server doctor
```

`doctor` checks local prerequisites (config file, Python version, embedding/VLM provider connectivity, disk space) without requiring a running server.

> For cloud API providers (Volcengine, OpenAI, Gemini, etc.), continue with the manual configuration below.

##### Server Configuration Template

The recommended first-time flow is:

```bash
openviking-server init
openviking-server doctor
```

If you choose `OpenAI Codex` inside `openviking-server init`, the wizard can import existing Codex auth or start the Codex sign-in flow for you.

If you prefer manual configuration, create `~/.openviking/ov.conf`, remove the comments before copy:

```json
{
  "storage": {
    "workspace": "/home/your-name/openviking_workspace"
  },
  "log": {
    "level": "INFO",
    "output": "stdout"                 // Log output: "stdout" or "file"
  },
  "embedding": {
    "dense": {
      "api_base" : "<api-endpoint>",   // API endpoint address
      "api_key"  : "<your-api-key>",   // Model service API Key
      "provider" : "<provider-type>",  // Provider type: "volcengine" or "openai" (currently supported)
      "dimension": 1024,               // Vector dimension
      "model"    : "<model-name>"      // Embedding model name (e.g., doubao-embedding-vision-251215 or text-embedding-3-large)
    },
    "max_concurrent": 10,              // Max concurrent embedding requests (default: 10)
    "text_source": "content_only",     // Text file vectorization source: content_only|summary_first|summary_only
    "max_input_tokens": 4096           // Max estimated raw text tokens sent to embedding
  },
  "vlm": {
    "api_base" : "<api-endpoint>",     // API endpoint address
    "api_key"  : "<your-api-key>",     // Model service API Key (optional for openai-codex)
    "provider" : "<provider-type>",    // Provider type (volcengine, openai, openai-codex, kimi, glm, etc.)
    "model"    : "<model-name>",       // VLM model name (e.g., doubao-seed-2-0-pro-260215 or gpt-4-vision-preview)
    "max_concurrent": 64              // Max concurrent LLM calls for semantic processing (default: 64)
  }
}
```

> **Note**: For embedding models, supported providers are `volcengine` (Doubao), `openai`, `azure`, `jina`, `ollama`, `voyage`, `dashscope`, `minimax`, `cohere`, `vikingdb`, `gemini` (requires `pip install "google-genai>=1.0.0"`), `litellm`, and `local`. For VLM models, common providers include `volcengine`, `openai`, `openai-codex`, `kimi`, and `glm`.

##### Server Configuration Examples

👇 Expand to see the configuration example for your model service:

<details>
<summary><b>Example 1: Using Volcengine (Doubao Models)</b></summary>

```json
{
  "storage": {
    "workspace": "/home/your-name/openviking_workspace"
  },
  "log": {
    "level": "INFO",
    "output": "stdout"                 // Log output: "stdout" or "file"
  },
  "embedding": {
    "dense": {
      "api_base" : "https://ark.cn-beijing.volces.com/api/v3",
      "api_key"  : "your-volcengine-api-key",
      "provider" : "volcengine",
      "dimension": 1024,
      "model"    : "doubao-embedding-vision-251215"
    },
    "max_concurrent": 10
  },
  "vlm": {
    "api_base" : "https://ark.cn-beijing.volces.com/api/v3",
    "api_key"  : "your-volcengine-api-key",
    "provider" : "volcengine",
    "model"    : "doubao-seed-2-0-pro-260215",
    "max_concurrent": 64
  }
}
```

</details>

<details>
<summary><b>Example 2: Using OpenAI Models</b></summary>

```json
{
  "storage": {
    "workspace": "/home/your-name/openviking_workspace"
  },
  "log": {
    "level": "INFO",
    "output": "stdout"                 // Log output: "stdout" or "file"
  },
  "embedding": {
    "dense": {
      "api_base" : "https://api.openai.com/v1",
      "api_key"  : "your-openai-api-key",
      "provider" : "openai",
      "dimension": 3072,
      "model"    : "text-embedding-3-large"
    },
    "max_concurrent": 10
  },
  "vlm": {
    "api_base" : "https://api.openai.com/v1",
    "api_key"  : "your-openai-api-key",
    "provider" : "openai",
    "model"    : "gpt-4-vision-preview",
    "max_concurrent": 64
  }
}
```

</details>

<details>
<summary><b>Example 3: Using Google Gemini Embedding</b></summary>

Install the required package first:

```bash
pip install "google-genai>=1.0.0"
```

```json
{
  "storage": {
    "workspace": "/home/your-name/openviking_workspace"
  },
  "embedding": {
    "dense": {
      "provider": "gemini",
      "api_key": "your-google-api-key",
      "model": "gemini-embedding-2-preview",
      "dimension": 3072
    },
    "max_concurrent": 10
  },
  "vlm": {
    "api_base" : "https://api.openai.com/v1",
    "api_key"  : "your-openai-api-key",
    "provider" : "openai",
    "model"    : "gpt-4o",
    "max_concurrent": 64
  }
}
```

Get your Google API key at <https://aistudio.google.com/apikey>

</details>

<details>
<summary><b>Example 4: Using Volcengine Embedding + Codex VLM</b></summary>

Use `openviking-server init` and choose `OpenAI Codex`, then run `openviking-server doctor`.

```json
{
  "storage": {
    "workspace": "/home/your-name/openviking_workspace"
  },
  "embedding": {
    "dense": {
      "api_base" : "https://ark.cn-beijing.volces.com/api/v3",
      "api_key"  : "your-volcengine-api-key",
      "provider" : "volcengine",
      "dimension": 1024,
      "model"    : "doubao-embedding-vision-251215"
    }
  },
  "vlm": {
    "api_base" : "https://chatgpt.com/backend-api/codex",
    "provider" : "openai-codex",
    "model"    : "gpt-5.3-codex",
    "max_concurrent": 64
  }
}
```

</details>

##### Set Server Configuration Environment Variable

After creating the configuration file, set the environment variable to point to it (Linux/macOS):

```bash
export OPENVIKING_CONFIG_FILE=~/.openviking/ov.conf # by default
```

On Windows, use one of the following:

PowerShell:

```powershell
$env:OPENVIKING_CONFIG_FILE = "$HOME/.openviking/ov.conf"
```

Command Prompt (cmd.exe):

```bat
set "OPENVIKING_CONFIG_FILE=%USERPROFILE%\.openviking\ov.conf"
```

> 💡 **Tip**: You can also place the configuration file in other locations, just specify the correct path in the environment variable.

##### CLI/Client Configuration Examples

You can initialize the configuration of the CLI/client interactively through the `ov config` command. If you have multiple openviking servers, you can also switch to other configurations using the `ov config switch` command.

👇 Expand to see the configuration example for your CLI/Client:
<details>
<summary><b>Example: ovcli.conf for visiting localhost server</b></summary>


```json
{
  "url": "http://localhost:1933",
  "timeout": 60.0
}
```

After creating the configuration file, set the environment variable to point to it (Linux/macOS):

```bash
export OPENVIKING_CLI_CONFIG_FILE=~/.openviking/ovcli.conf # by default
```

On Windows, use one of the following:

PowerShell:

```powershell
$env:OPENVIKING_CLI_CONFIG_FILE = "$HOME/.openviking/ovcli.conf"
```

Command Prompt (cmd.exe):

```bat
set "OPENVIKING_CLI_CONFIG_FILE=%USERPROFILE%\.openviking\ovcli.conf"
```
</details>

#### 4. Run Your First Example

> 📝 **Prerequisite**: Ensure you have completed the configuration (ov.conf and ovcli.conf) in the previous step.

Now let's run a complete example to experience the core features of OpenViking.

##### Launch Server

```bash
openviking-server doctor
openviking-server
```

If you configured `provider=openai-codex`, `openviking-server doctor` already validates Codex auth.

or you can run in background

```bash
nohup openviking-server > /data/log/openviking.log 2>&1 &
```

##### Run the CLI

```bash
ov status
ov add-resource https://github.com/volcengine/OpenViking # --wait
ov ls viking://resources/
ov tree viking://resources/volcengine -L 2
# wait some time for semantic processing if not --wait
ov find "what is openviking"
ov grep "openviking" --uri viking://resources/volcengine/OpenViking/docs/zh
```

Congratulations! You have successfully run OpenViking 🎉

### Commercial Access

OpenViking Personal is now officially available. Compared with the open-source edition, the Service version is officially hosted and ready to use, scales far beyond local hardware with VikingDB, and comes with richer integrations plus professional support. It includes a free trial for up to 50 files, and existing open-source users can move over smoothly with our migration tool.

### VikingBot Quick Start

VikingBot is an AI agent framework built on top of OpenViking. Here's how to get started:

```bash
# Option 1: Install VikingBot from PyPI (recommended for most users)
pip install "openviking[bot]"

# Option 2: Install VikingBot from source (for development)
uv pip install -e ".[bot]"

# Start OpenViking server with Bot enabled
openviking-server --with-bot

# In another terminal, start interactive chat
ov chat
```

If you use the official Docker image, `vikingbot` is already bundled in the image and starts by default together with the OpenViking server and console UI. You can disable it at runtime with either `--without-bot` or `-e OPENVIKING_WITH_BOT=0`.

***

## Server Deployment Details

For production environments, we recommend running OpenViking as a standalone HTTP service to provide persistent, high-performance context support for your AI Agents.

🚀 **Deploy OpenViking on Cloud**:
To ensure optimal storage performance and data security, we recommend deploying on **Volcengine Elastic Compute Service (ECS)** using the **veLinux** operating system. We have prepared a detailed step-by-step guide to get you started quickly.

👉 **[View: Server Deployment & ECS Setup Guide](./docs/en/getting-started/03-quickstart-server.md)**

---

## Evaluation Highlights

OpenViking 0.3.22 has been evaluated across three scenarios: long-conversation user memory, agent experience memory, and knowledge-base QA.

### 1. User Memory on LoCoMo

On the LoCoMo benchmark, OpenViking improves long-context QA accuracy while reducing both latency and token usage across multiple agent integrations:

| Integration | Accuracy | Avg. Query Time | Total Input Tokens |
|:-----------:|---------:|----------------:|-------------------:|
| OpenClaw + native memory | 24.20% | 95.14s | 392,559,404 |
| OpenClaw + OpenViking | **82.08%** | 38.8s | 37,423,456 |
| Hermes native memory | 33.38% | 82.4s | 79,228,398 |
| Hermes + OpenViking | **82.86%** | **27.9s** | 52,026,755 |
| Claude Code auto-memory | 57.21% | 49.1s | 353,306,422 |
| Claude Code + OpenViking | **80.32%** | **20.4s** | 129,968,899 |

#### 1.1 Key Efficiency Improvements

| Agent | Accuracy Improvement | Latency Reduction | Token Reduction |
|:-----:|---------------------:|------------------:|----------------:|
| OpenClaw | 24.20% → 82.08% (+3.39×) | -59.22% | **-91.0%** |
| Hermes | 33.38% → 82.86% (+2.48×) | -66.10% | -34.3% |
| Claude Code | 57.21% → 80.32% (+1.40×) | -58.45% | -63.2% |

### 2. Agent Experience Memory on tau2-bench

For multi-turn agent tasks on tau2-bench, OpenViking's experience memory improves task success in both retail and airline domains:

| Setting | Retail Accuracy | Airline Accuracy |
|:-------:|----------------:|-----------------:|
| LLM without memory | 70.94% | 54.38% |
| LLM + OpenViking experience memory | **77.81%** (+6.87pp) | **66.25%** (+11.87pp) |

### 3. Knowledge Base QA on HotpotQA

On multi-hop RAG tasks from HotpotQA, increasing OpenViking retrieval from top-5 to top-20 delivers the highest accuracy in this comparison while keeping retrieval latency low:

| Method | Retrieval Pattern | Accuracy | Tokens / QA | Latency / QA |
|:------:|:-----------------:|---------:|------------:|-------------:|
| Naive RAG | Vector retrieval | 62.50% | 1,290 | **0.11s** |
| HippoRAG 2 | Vector + knowledge graph | 61.00% | 726 | 20s |
| LightRAG | Vector + knowledge graph | 89.00% | 28,443 | 75s |
| LangChain SQL (Agent) | SQL agent | 78.00% | 4,776 | 132s |
| OpenViking (top-5) | Vector retrieval | 72.75% | 3,154 | 0.22s |
| OpenViking (top-20) | Vector retrieval | **91.00%** | 12,533 | 0.23s |
| Nanobot + OpenViking (Agent) | Vector retrieval + Agent | 87.00% | 71,300 | 61.6s |

#### 3.1 Single-turn RAG Across 5 Open-source Datasets

| Method | Retrieval Pattern | Average Accuracy | Indexing Tokens | Tokens / QA | Retrieval Latency |
|:------:|:-----------------:|-----------------:|----------------:|------------:|------------------:|
| Naive RAG | Vector retrieval | 53.93% | 2,755,356 | 1,435 | **0.13s** |
| PageIndex | Vector + tree structure | 36.75% | 5,609,206 | 710,480 | 84.60s |
| HippoRAG 2 | Vector + knowledge graph | 44.50% | 124,963,618 | **637** | 18.83s |
| LightRAG | Vector + knowledge graph | **76.00%** | 62,705,469 | 27,035 | 9.19s |
| **OpenViking** | **Vector retrieval** | **66.87%** | **8,671,538** | **3,060** | **0.19s** |

> Datasets: FinanceBench, NaturalQuestions, ClapNQ, Qasper, and SyllabusQA. OpenViking reaches 66.87% average accuracy with very low retrieval latency (0.19s), while indexing cost is only 13.8% of LightRAG.

---

## Academic Backing

OpenViking open-sources a subset of the core capabilities described in the `VikingMem` paper, making the context database and memory management ideas accessible to AI agent developers.

> **VikingMem: A Memory Base Management System for Stateful LLM-based Applications**
> Jiajie Fu, Junwen Chen, Mengzhao Wang, Aoxiang He, Maojia Sheng, Xiangyu Ke, Yifan Zhu, and Yunjun Gao.
> arXiv:2605.29640, 2026. Accepted by VLDB 2026.
>
> 📄 [Read the paper on arXiv](https://arxiv.org/abs/2605.29640)

## Core Concepts

After running the first example, let's dive into the design philosophy of OpenViking. These five core concepts correspond one-to-one with the solutions mentioned earlier, together building a complete context management system:

### 1. Filesystem Management Paradigm → Solves Fragmentation

We no longer view context as flat text slices but unify them into an abstract virtual filesystem. Whether it's memories, resources, or capabilities, they are mapped to virtual directories under the `viking://` protocol, each with a unique URI.

This paradigm gives Agents unprecedented context manipulation capabilities, enabling them to locate, browse, and manipulate information precisely and deterministically through standard commands like `ls` and `find`, just like a developer. This transforms context management from vague semantic matching into intuitive, traceable "file operations". Learn more: [Viking URI](./docs/en/concepts/04-viking-uri.md) | [Context Types](./docs/en/concepts/02-context-types.md)

```
viking://
├── resources/              # Resources: project docs, repos, web pages, etc.
│   ├── my_project/
│   │   ├── docs/
│   │   │   ├── api/
│   │   │   └── tutorials/
│   │   └── src/
│   └── ...
├── user/                   # User: personal preferences, habits, etc.
│   └── {user_id}/
│       ├── memories/
│       │   ├── preferences/
│       │   │   ├── writing_style
│       │   │   └── coding_habits
│       │   └── ...
│       ├── resources/
│       │   └── private_project/
│       ├── skills/
│       │   ├── search_code
│       │   └── analyze_data
│       └── peers/
│           └── web-visitor-alice/
│               ├── memories/
│               └── resources/
```

### 2. Tiered Context Loading → Reduces Token Consumption

Stuffing massive amounts of context into a prompt all at once is not only expensive but also prone to exceeding model windows and introducing noise. OpenViking automatically processes context into three levels upon writing:

- **L0 (Abstract)**: A one-sentence summary for quick retrieval and identification.
- **L1 (Overview)**: Contains core information and usage scenarios for Agent decision-making during the planning phase.
- **L2 (Details)**: The full original data, for deep reading by the Agent when absolutely necessary.

Learn more: [Context Layers](./docs/en/concepts/03-context-layers.md)

```
viking://resources/my_project/
├── .abstract               # L0 Layer: Abstract (~100 tokens) - Quick relevance check
├── .overview               # L1 Layer: Overview (~2k tokens) - Understand structure and key points
├── docs/
│   ├── .abstract          # Each directory has corresponding L0/L1 layers
│   ├── .overview
│   ├── api/
│   │   ├── .abstract
│   │   ├── .overview
│   │   ├── auth.md        # L2 Layer: Full content - Load on demand
│   │   └── endpoints.md
│   └── ...
└── src/
    └── ...
```

### 3. Directory Recursive Retrieval → Improves Retrieval Effect

Single vector retrieval struggles with complex query intents. OpenViking has designed an innovative **Directory Recursive Retrieval Strategy** that deeply integrates multiple retrieval methods:

1. **Intent Analysis**: Generate multiple retrieval conditions through intent analysis.
2. **Initial Positioning**: Use vector retrieval to quickly locate the high-score directory where the initial slice is located.
3. **Refined Exploration**: Perform a secondary retrieval within that directory and update high-score results to the candidate set.
4. **Recursive Drill-down**: If subdirectories exist, recursively repeat the secondary retrieval steps layer by layer.
5. **Result Aggregation**: Finally, obtain the most relevant context to return.

This "lock high-score directory first, then refine content exploration" strategy not only finds the semantically best-matching fragments but also understands the full context where the information resides, thereby improving the globality and accuracy of retrieval. Learn more: [Retrieval Mechanism](./docs/en/concepts/07-retrieval.md)

### 4. Visualized Retrieval Trajectory → Observable Context

OpenViking's organization uses a hierarchical virtual filesystem structure. All context is integrated in a unified format, and each entry corresponds to a unique URI (like a `viking://` path), breaking the traditional flat black-box management mode with a clear hierarchy that is easy to understand.

The retrieval process adopts a directory recursive strategy. The trajectory of directory browsing and file positioning for each retrieval is fully preserved, allowing users to clearly observe the root cause of problems and guide the optimization of retrieval logic. Learn more: [Retrieval Mechanism](./docs/en/concepts/07-retrieval.md)

### 5. Automatic Session Management → Context Self-Iteration

OpenViking has a built-in memory self-iteration loop. At the end of each session, developers can actively trigger the memory extraction mechanism. The system will asynchronously analyze task execution results and user feedback, and automatically update them to the User and Agent memory directories.

- **User Memory Update**: Update memories related to user preferences, making Agent responses better fit user needs.
- **Agent Experience Accumulation**: Extract core content such as operational tips and tool usage experience from task execution experience, aiding efficient decision-making in subsequent tasks.

This allows the Agent to get "smarter with use" through interactions with the world, achieving self-evolution. Learn more: [Session Management](./docs/en/concepts/08-session.md)

***

## Advanced Reading

### Documentation

For more details, please visit our [Full Documentation](./docs/en/).

### Community & Team

For more details, please see: **[About Us](./docs/en/about/01-about-us.md)**

### Join the Community

OpenViking is still in its early stages, and there are many areas for improvement and exploration. We sincerely invite every developer passionate about AI Agent technology:

- Light up a precious **Star** for us to give us the motivation to move forward.
- Visit our **[Website](https://www.openviking.ai)** to understand the philosophy we convey, and use it in your projects via the **[Documentation](https://www.openviking.ai/docs)**. Feel the change it brings and give us feedback on your truest experience.
- Join our community to share your insights, help answer others' questions, and jointly create an open and mutually helpful technical atmosphere:
  - 📱 **Lark Group**: Scan the QR code to join → [View QR Code](./docs/en/about/01-about-us.md#lark-group)
  - 💬 **WeChat Group**: Scan the QR code to add assistant → [View QR Code](./docs/en/about/01-about-us.md#wechat-group)
  - 🎮 **Discord**: [Join Discord Server](https://discord.com/invite/eHvx8E9XF3)
  - 🐦 **X (Twitter)**：[Follow us](https://x.com/openvikingai)
- Become a **Contributor**, whether submitting a bug fix or contributing a new feature, every line of your code will be an important cornerstone of OpenViking's growth.

Let's work together to define and build the future of AI Agent context management. The journey has begun, looking forward to your participation!

### Star Trend

[![Star History Chart](https://api.star-history.com/svg?repos=volcengine/OpenViking\&type=timeline\&legend=top-left)](https://www.star-history.com/#volcengine/OpenViking\&type=timeline\&legend=top-left)

## Security and privacy

This project takes security seriously.
For vulnerability reporting and supported versions, see [SECURITY.md](SECURITY.md)

## License

The OpenViking project uses different licenses for different components:

- **Main Project**: AGPLv3 - see the [LICENSE](./LICENSE) file for details
- **crates/ov\_cli**: Apache 2.0 - see the [LICENSE](./crates/LICENSE) for details
- **examples**: Apache 2.0 - see the [LICENSE](./examples/LICENSE) for details
- **third\_party**: Respective original licenses of third-party projects

<!-- Link Definitions -->

---

# STALE

[![arXiv](https://img.shields.io/badge/arXiv-2605.06527-b31b1b.svg)](https://arxiv.org/abs/2605.06527)

# STALE and CUP-Mem

This repository contains the code and resources for our paper:

**STALE: Can LLM Agents Know When Their Memories Are No Longer Valid?**  
[arXiv:2605.06527](https://arxiv.org/abs/2605.06527)

- `STALE/`: dataset generation and evaluation scripts for the STALE benchmark.
- `cup_mem/`: the CUP-Mem memory pipeline for session-by-session profile updates and conflict-aware query answering.

## Main Results

We evaluate each model on two implicit-conflict types and three probing dimensions:
State Resolution (SR), Premise Resistance (PR), and Implicit Policy Adaptation (IPA).
Overall denotes the average accuracy across all six settings.

| Model | Type I SR | Type I PR | Type I IPA | Type II SR | Type II PR | Type II IPA | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|
| GPT-4o-mini* | 30.0 | 0.0 | 11.0 | 9.5 | 0.0 | 1.5 | 8.7 |
| GPT-5.4-nano | 20.5 | 1.5 | 21.5 | 9.0 | 0.0 | 6.5 | 9.8 |
| GPT-5.4 | 35.0 | 2.0 | 29.0 | 9.0 | 2.0 | 17.0 | 15.7 |
| Gemini-3.1-flash-lite | 41.0 | 1.5 | 42.0 | 25.0 | 1.5 | 23.5 | 22.4 |
| Gemini-3.1-pro | 92.0 | 30.0 | 71.0 | 69.0 | 14.0 | 55.0 | 55.2 |
| Claude-Opus-4.6 | 50.5 | 10.0 | 42.5 | 21.0 | 9.0 | 36.5 | 28.3 |
| Llama-3.3-70B-Instruct* | 6.5 | 0.0 | 3.0 | 6.0 | 0.0 | 0.0 | 2.6 |
| Qwen3.5-9B | 36.0 | 1.0 | 21.5 | 21.5 | 0.0 | 7.5 | 14.6 |
| Qwen3.5-27B | 76.0 | 4.0 | 39.0 | 42.0 | 3.5 | 23.0 | 31.3 |
| MiniMax-M2.5 | 10.5 | 1.5 | 8.0 | 5.5 | 5.0 | 2.5 | 5.5 |
| LightMem | 52.5 | 1.0 | 23.5 | 21.5 | 0.5 | 7.5 | 17.8 |
| Zep | 10.0 | 0.0 | 19.0 | 3.0 | 1.0 | 3.0 | 6.0 |
| LiCoMemory | 15.5 | 0.5 | 22.5 | 1.5 | 1.5 | 4.0 | 7.6 |
| A-mem | 13.5 | 0.0 | 7.5 | 8.0 | 0.0 | 1.5 | 5.1 |
| mem-0 | 17.0 | 1.0 | 22.0 | 3.5 | 0.0 | 6.5 | 8.3 |
| **CUPMem (Ours)** | 91.0 | **78.0** | 32.0 | **89.0** | **75.0** | 43.0 | **68.0** |

All numbers are accuracies (%).  
`*` indicates settings where evidence-preserving truncation was applied because the full context exceeded the model's context window.

## Setup

Use Python 3.10 or newer. Create one environment for each component:

```bash
cd STALE
conda create -n stale python=3.10 -y
conda activate stale
python -m pip install -r requirements.txt
cp .env.example .env
```

```bash
cd cup_mem
conda create -n cupmem python=3.10 -y
conda activate cupmem
python -m pip install -r requirements.txt
```

Fill `STALE/.env` with provider keys and local paths before running generation or evaluation.

## Components

`STALE/` provides:

- ontology-seed based data generation
- timestamp and haystack assembly
- target-model response generation
- automatic response judging and performance summaries

See `STALE/README.md` for commands and expected input/output formats.

`cup_mem/` provides:

- structured memory write and invalidation logic
- retrieval and premise verification
- conflict-aware readout for memory-dependent queries
- OpenAI-compatible and Responses API client wrappers
- a single-sample runner that can consume `STALE/outputs/*_MAIN.json` directly

See `cup_mem/README.md` for minimal usage.

---

# VerbalR3

# Verbal-R3: Verbal Reranker as the Missing Bridge between Retrieval and Reasoning

Official implementation for **Verbal-R3: Verbal Reranker as the Missing Bridge between Retrieval and Reasoning**.

## Links

- 📄 **Paper**: [arXiv](http://arxiv.org/abs/XXXX.XXXXX)
- 🤗 **Models**:
  - [Reranker 1.5B SFT](https://huggingface.co/0k9d0h1/reranker1.5b-sft)
  - [Reranker 3B SFT](https://huggingface.co/0k9d0h1/reranker3b-sft)
  - [3B Planner + 1.5B Reranker](https://huggingface.co/0k9d0h1/3b-planner-1.5b-reranker-nq-hotpotqa-filtered-tp-reranker)
  - [7B Planner + 1.5B Reranker](https://huggingface.co/0k9d0h1/7b-planner-1.5b-reranker-nq-hotpotqa-filtered-tp-reranker)

---

## Overview

This repository contains code for:

- **Verbal Reranker training and inference**
- **Planner RL training**
- **Planner generation / evaluation**
- **Retriever indexing and serving**

The overall pipeline consists of three components:

1. **Retriever**: serves document retrieval over the indexed corpus
2. **Verbal Reranker**: scores and annotates retrieved documents
3. **Planner**: performs retrieval-augmented reasoning and generation

---

## Environment Setup

### 1. Planner Environment

```bash
conda create -n planner python=3.10 -y
conda activate planner

conda install -c conda-forge cuda-toolkit=12.4

cd verl
scripts/install_vllm_sglang_mcore.sh
pip install --no-deps -e .

pip install grpcio==1.74.0
pip install ray==2.49.0
```

### 2. Retriever Environment

```bash
conda create -n retriever python=3.10 -y
conda activate retriever

# We recommend installing torch with conda for faiss-gpu
conda install pytorch==2.4.0 torchvision==0.19.0 torchaudio==2.4.0 pytorch-cuda=12.1 -c pytorch -c nvidia
pip install transformers datasets pyserini

# Install the GPU version of faiss to guarantee efficient RL rollout
conda install -c pytorch -c nvidia faiss-gpu=1.8.0

# API server dependencies
pip install uvicorn fastapi
```

### 3. Reranker Environment

We recommend using `uv` for fast and reliable package management.

```bash
conda create -n reranker python=3.12 -y
conda activate reranker

pip install uv
uv pip install ms-swift==3.7.3
uv pip install deepspeed==0.16.9
uv pip install vllm==0.10.1.1
uv pip install huggingface_hub[cli] hf_transfer
uv pip install wandb
uv pip install scikit-learn
pip install flash-attn==2.7.4.post1 --no-build-isolation
```

---

## Retriever Data Preparation

### 1. Download Retriever Data

```bash
save_path=/the/path/to/save
python utils/download.py --save_path $save_path
cat $save_path/part_* > $save_path/e5_Flat.index
gzip -d $save_path/wiki-18.jsonl.gz
```

### 2. Data Preprocessing

Run the following preprocessing scripts:

```bash
python utils/data_preprocess/planner_test_merge.py
python utils/data_preprocess/planner_train_merge.py
python utils/make_filtering_indices.py
python utils/filter_dataset.py
```

---

## Reranker Training

The Verbal Reranker is trained using distilled trajectories from GPT-OSS-120B. The training pipeline consists of the following steps.

### 1. Retrieve Data

After starting the retriever server, retrieve NQ data:

```bash
python src/retrieve_nq.py --search_url {SEARCH_URL}
```

### 2. Format Batches

Form batches for LLM input from the retrieved data:

```bash
python src/format_batch.py
```

### 3. Run Inference with Teacher Model

Launch a vLLM server with GPT-OSS-120B (this can be replaced with another teacher model if desired):

```bash
CUDA_VISIBLE_DEVICES=0,1,2,3 vllm serve openai/gpt-oss-120b \
    --port 8017 \
    --tensor_parallel_size 4 \
    --data_parallel_size 1 \
    --served_model_name rerank
```

Run inference against the server (supports automatic resume):

```bash
python src/inference.py \
    --model_name rerank \
    --base_url "http://localhost:8017/v1/" \
    --api_key EMPTY \
    --max_tokens 16384 \
    --max_workers 256 \
    --input_path batch.jsonl \
    --output_path vllm_output.jsonl \
    --messages_key "messages"
```

### 4. Build SFT Data

Reformat the output for SFT distillation. Filtering is applied automatically, but train/val splitting must be done manually.

```bash
python src/build_sft_data.py \
    --input vllm_output.jsonl \
    --output sft_data.jsonl
```

### 5. Fine-tune the Reranker

```bash
WANDB_PROJECT="RERANK" NPROC_PER_NODE=4 \
swift sft \
    --model Qwen/Qwen2.5-3B-Instruct \
    --train_type full \
    --dataset /path/to/sft_data.jsonl \
    --torch_dtype bfloat16 \
    --num_train_epochs 3 \
    --per_device_train_batch_size 4 \
    --gradient_accumulation_steps 8 \
    --learning_rate 1e-5 \
    --save_strategy epoch \
    --logging_steps 1 \
    --max_length 2048 \
    --output_dir saves/reranker_sft_3b \
    --warmup_ratio 0.05 \
    --dataloader_num_workers 4 \
    --dataset_num_proc 4 \
    --report_to wandb \
    --run_name reranker_sft_3b \
    --use_hf true \
    --deepspeed zero3 \
    --attn_impl flash_attn
```

---

## Serving

### 1. Retriever Server

Launch the retriever server with:

```bash
scripts/retriever_launch.sh
```

### 2. Reranker Server

We provide two serving modes:

```bash
scripts/dp_serving.sh
scripts/serving.sh
```

- `dp_serving.sh` uses **data parallelism** and is generally faster.
- However, we observed that it can be **unstable during planner RL training**.
- If you encounter instability during planner training, we recommend using `serving.sh` instead.

---

## Planner Training and Evaluation

The planner relies on the retriever and reranker servers during both training and evaluation.

- For **planner RL training**, we use the **1.5B reranker**.
- For **planner evaluation**, we use the **3B reranker**.

### 1. Planner RL Training

```bash
scripts/training.sh
```

### 2. Planner Generation

```bash
scripts/generation.sh
```

### 3. Evaluation

```bash
python utils/evaluation_from_jsonl.py
```

Before evaluation, make sure to modify the `input_file` path accordingly.

---

## Reranker Usage

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

model_id = "your-username/your-model-name"  # Replace with your model path
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto")

SYSTEM_PROMPT = """You are an evaluator that judges how informative a document is for answering a given question. You will receive a Question and a Document.

Carefully assess relevance and usefulness with a brief, evidence-based comment that supports downstream filtering (mention concrete entities/claims/dates/metrics when helpful), and then a score of relevance.

Scoring rubric (1-5):
1 — Unrelated: The document has nothing to do with the question.
2 — Loosely related: Contains information that might potentially help, but is unlikely to.
3 — Partially informative: Contains information that can potentially help answer the question.
4 — Substantively informative: Related and includes relevant information.
5 — Direct answer: Clearly related and includes key information to directly answer the question.

Output format (exactly):
Comment: <concise assessment citing specific evidence>
Score: <1-5>"""


def evaluate(question: str, document: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Question: {question}\nDocument: {document}"},
    ]

    inputs = tokenizer.apply_chat_template(
        messages, tokenize=True, add_generation_prompt=True, return_tensors="pt"
    ).to(model.device)

    outputs = model.generate(
        inputs, max_new_tokens=256, temperature=1.0, top_p=0.95
    )

    response = tokenizer.decode(
        outputs[0][inputs.shape[-1]:], skip_special_tokens=True
    )
    return response


# Example
question = "When was the Eiffel Tower built?"
document = (
    "The Eiffel Tower is a wrought-iron lattice tower in Paris, "
    "constructed from 1887 to 1889 as the centerpiece of the 1889 World's Fair."
)

result = evaluate(question, document)
print(result)
```

---

## TODO

- Add test-time scaling implementation and usage instructions.

---

## Acknowledgement

This codebase is built upon:

- [Search-R1](https://github.com/PeterGriffinJin/Search-R1)

We thank the authors for open-sourcing their code.

---

## Citation

```bibtex
@article{verbal-r3,
  title={Verbal-R3: Verbal Reranker as the Missing Bridge between Retrieval and Reasoning},
  author={},
  journal={arXiv preprint arXiv:XXXX.XXXXX},
  year={2025}
}
```
