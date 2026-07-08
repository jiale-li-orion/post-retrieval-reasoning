
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
