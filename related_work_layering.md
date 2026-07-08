# Related Work 分类表

依据：`references.md` 当前条目。

口径：

- `references.md` 当前共有 **32 个独立 reference**。
- 本表覆盖 **32/32**。
- 每篇只进入一个主类；后续正文可以跨段引用，但分类表不重复计数。
- BibTeX / citation 原文见 [related_work_citations.md](/home/orion/research/agent_memory_paper/related_work_citations.md)。其中明确标注了哪些来自作者/官方 README 或论文页，哪些只是 arXiv fallback。

## 分类总表

| # | 主类 | Work | 主贡献 | Citation key | Citation 来源 |
| ---: | --- | --- | --- | --- | --- |
| 1 | 理论/统一框架 | Experience Compression Spectrum | 将 memory、skill、rule 统一为 experience compression spectrum；定义 trace 与 compression function。 | `zhang2026experiencecompressionspectrumunifying` | arXiv fallback，未找到作者自标 |
| 2 | 理论/统一框架 | Externalization in LLM Agents | 综述 agent 能力从 weights/context 外化到 memory、skills、protocols、harness。 | `zhou2026externalizationllmagentsunified` | arXiv fallback，未找到作者自标 |
| 3 | 理论/统一框架 | Overcoming the Impedance Mismatch | 理论批判 FM × KG 融合中的结构失真、序列化瓶颈、softmax 泄漏。 | `dhayalkar2026overcomingimpedancemismatchtheoretical` | arXiv fallback，未找到作者自标 |
| 4 | 记忆基底/写入结构 | GSW / Beyond Fact Retrieval | 将 episodic memory 整合为 Generative Semantic Workspace。 | `rajesh2026factretrievalepisodicmemory` | arXiv fallback，未找到作者自标 |
| 5 | 记忆基底/写入结构 | StructMem | Structured memory for long-horizon behavior。 | `xu2026structmemstructuredmemorylonghorizon` | arXiv fallback，未找到作者自标 |
| 6 | 记忆基底/写入结构 | LinkedIn Hierarchical Long-Term Semantic Memory | 工业 hiring agent 中的层级语义记忆。 | `xu2026hierarchicallongtermsemanticmemory` | arXiv fallback，未找到作者自标 |
| 7 | 记忆基底/写入结构 | HiGMem | Hierarchical and LLM-guided memory system for long-term conversational agents。 | `cao2026higmemhierarchicalllmguidedmemory` | arXiv fallback，未找到作者自标 |
| 8 | 记忆基底/写入结构 | APEX-MEM | Agentic semi-structured memory with temporal reasoning。 | `banerjee2026apexmemagenticsemistructuredmemory` | arXiv fallback，未找到作者自标 |
| 9 | 记忆基底/写入结构 | HyperMem | Hypergraph memory for long-term conversations。 | `yue2026hypermemhypergraphmemorylongterm` | arXiv fallback，未找到作者自标 |
| 10 | 记忆基底/写入结构 | A-Mem | Agentic long-term memory organization。 | `xu2025amem` | 作者 GitHub README |
| 11 | 记忆基底/写入结构 | mem0 | Production-ready scalable long-term memory layer。 | `mem0` | 作者 GitHub README |
| 12 | 记忆基底/写入结构 | MemoryOS | 类 OS 的分层 agent memory 架构。 | `kang2025memoryosaiagent` | 作者 GitHub README |
| 13 | 记忆基底/写入结构 | HippoRAG | KG + Personalized PageRank 的长期记忆/RAG 框架。 | `gutiérrez2024hipporag` | 作者 GitHub README |
| 14 | 记忆基底/写入结构 | HippoRAG 2 / From RAG to Memory | 非参数 continual learning memory framework。 | `gutiérrez2025ragmemorynonparametriccontinual` | 作者 GitHub README |
| 15 | 记忆基底/写入结构 | SimpleMem | Efficient lifelong memory with compression and intent-aware retrieval。 | `simplemem2026` | 作者 GitHub README |
| 16 | 记忆基底/写入结构 | VikingMem | Memory Base management system with selective extraction, stateful evolution, temporal compression。 | `fu2026vikingmemmemorybasemanagement` | arXiv fallback，未找到作者自标 |
| 17 | 记忆基底/写入结构 | MemPalace | 工程产品型 memory substrate；无论文 citation。 | 待补/无论文 | 未找到论文 citation |
| 18 | 运行时访问/检索/搜索 | AdaMEM | Test-time adaptive memory；离线原始经验 + 在线短程策略记忆。 | `zhang2026adamem` | 作者 GitHub README |
| 19 | 运行时访问/检索/搜索 | Mnemis | Dual-route retrieval: similarity search + hierarchical global selection。 | `tang2026mnemis` | 作者 GitHub README |
| 20 | 运行时访问/检索/搜索 | Memory is Reconstructed, Not Retrieved / MRAgent | 主动记忆重建；检索变成推理中的多轮 graph traversal。 | `ji2026memoryreconstructedretrievedgraph` | arXiv fallback，未找到作者自标 |
| 21 | 运行时访问/检索/搜索 | GrepSeek | 训练 search agent 直接用 grep/shell 与 corpus 交互。 | `salemi2026grepseektrainingsearchagents` | arXiv fallback，未找到作者自标 |
| 22 | 运行时访问/检索/搜索 | TruthfulRAG | 用 KG 处理 RAG 中 factual-level conflicts。 | `liu2025truthfulragresolvingfactuallevelconflicts` | arXiv fallback，未找到作者自标 |
| 23 | 状态有效性/冲突/持续累积 | STALE | 测 memory 是否失效，覆盖隐式冲突和下游行为适配。 | `chao2026stalellmagentsknow` | arXiv fallback，repo 未标 citation |
| 24 | 状态有效性/冲突/持续累积 | MemConflict | 长期记忆冲突评测：动态、静态、条件冲突。 | `tao2026memconflictevaluatinglongtermmemory` | arXiv fallback，未找到作者自标 |
| 25 | 状态有效性/冲突/持续累积 | MedMemoryBench | 医疗个性化长期记忆；提出 memory saturation / streaming evaluation。 | `wang2026medmemorybenchbenchmarkingagentmemory` | arXiv fallback，未找到作者自标 |
| 26 | 证据使用/上下文表达 | Are LLMs Really Not Knowledgeable? | 正确知识存在不等于正确表达；Hits@k 诊断 submerged knowledge。 | `tao2026llmsreallyknowledgeablemining` | arXiv fallback，未找到作者自标 |
| 27 | 证据使用/上下文表达 | SURE-RAG | 证据充分性验证；sufficiency 是 set-level property。 | `qiu2026sureragsufficiencyuncertaintyawareevidence` | arXiv fallback，未找到作者自标 |
| 28 | 诊断/归因协议 | Substrate Asymmetry in User-Side Memory | 诊断 LoRA/RAG 等 substrate 在个性化记忆中的不对称失败。 | `deng2026substrateasymmetryusersidememory` | arXiv fallback，repo 未标 citation |
| 29 | 诊断/归因协议 | Entity Collision | 检索增益归因协议，区分 encoder lift 与 lexical/entity leakage。 | `deng2026entity` | 作者 GitHub README |
| 30 | 诊断/归因协议 | MemTrace | memory-system failure tracing 与 faulty operation attribution。 | `deng2026memtracetracingattributingerrors` | 作者 GitHub README |
| 31 | 长程个性化记忆 Benchmark | ATM-Bench / According to Me | 多模态、多源、真实长期个性化指代 memory QA benchmark。 | `mei2026atm` | 作者 GitHub README |
| 32 | 长程个性化记忆 Benchmark | SuperMemory-VQA | 第一视角 long-horizon memory VQA benchmark。 | `alam2026supermemoryvqaegocentricvisualquestionanswering` | arXiv fallback，未找到作者自标 |

## 数量核对

| 主类 | 数量 |
| --- | ---: |
| 理论/统一框架 | 3 |
| 记忆基底/写入结构 | 14 |
| 运行时访问/检索/搜索 | 5 |
| 状态有效性/冲突/持续累积 | 3 |
| 证据使用/上下文表达 | 2 |
| 诊断/归因协议 | 3 |
| 长程个性化记忆 Benchmark | 2 |
| **合计** | **32** |
