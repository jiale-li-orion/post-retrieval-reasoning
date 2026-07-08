逻辑线：

# Introduction：
（配图figure）

1.智能体未来决策必然依赖过去长期交互，
    做扩展超长上下文的，这一类现在大家还在做，得引用。记不住，忘不掉，上下文中的召回…………等等上下文的使用问题，这个问题存在，也有人在解决
（这里早期也有工作，必须引用）

起：Large Language Models (LLMs) have …………

2.（这是已有范式）Recent research has…………

怎么留下要用的evidence!!!!!!!!!!!!!!!!!承：
完整过去不可能每次全部放进上下文，系统必须把过去外部化、压缩、维护，作为一个substrate
	这里已经有大量已有工作：早先的GSW等等…………近来比较热门的是写入时记忆管理，主要聚焦在如何把记忆啊经验啊，先写成一个更适合后续访问的状态（包括但不限于，关系数据库/虚拟文件系统/图结构关联结构），以及提前管理好状态，并及时进行状态更新，可以看到的是，从[Beyond Fact Retrieval: Episodic Memory for RAG with Generative Semantic Workspaces](https://arxiv.org/abs/2511.07587)到2026主流的记忆论文和工业界的产品：[A-Mem](https://github.com/WujiangXu/A-mem)/[mem0](https://github.com/mem0ai/mem0)/[MemoryOS](https://github.com/BAI-LAB/MemoryOS)/[HippoRAG2](https://github.com/OSU-NLP-Group/HippoRAG)/[MemPalace](https://github.com/MemPalace/mempalace)/[SimpleMem](https://github.com/aiming-lab/SimpleMem)，anthropic/openai/字节/腾讯等等的产品。
> 存好了，方便检索的。
Past interaction must be externalized into reusable artifacts for long-horizon agents.（大量文献分类列举）
_Experience Compression Spectrum_ 已经定义：
interaction trace $T$ = ${(s_t,a_t,o_t,f_t)}_{t=1}^{N}$
compression function $C_L$:$T→K_L$ 
交互轨迹被压缩成不同层级的知识制品：raw trace、episodic memory、procedural skill、declarative rule。(它关心的是输出制品处在哪个压缩层级，以及压缩带来的泛化性、具体性、成本和信息保留权衡)

---
怎么更好地找evidence!!!!!!!!!!!!!!!!!!!!!!!!

值得注意的是，系统终究还是在某个被识别出来的模式下访问记忆，只是先前大家默认就是做检索这种单一方式，做RAG，优化检索召回精度成本等等，后来做混合检索与重排，多阶段级联平衡召回率、精度和成本
哇！，家默认使用的访问接口是检索，经典的RAG检索范式，持续优化检索，混合检索等等，一大堆的GraphRAG，各种RAG优化召回率…………（哇，怎么可以就这样全部用RAG呢！！！RAG是不够的！！！）

看看隔壁code agent！！！code agent领域RAG早已不是主要地位…………，近来也有grepseek系统化分析，接口塑造智能体的思考方式，如果接口是 top-k passages，智能体的动作空间就是改写查询、阅读返回文档；如果接口变成 raw corpus + shell pipeline，智能体可以做固定字符串匹配、级联过滤、计数、截断、排序。code agent 的 grep/read/bash/LSP 工具链完全对上。

咱们记忆也有这个多路访问的趋势了——同时，ACL mnemis,也构造层级关系substrate，用基于图的访问…………System-1 相似度检索加 System-2 的层级全局选择，最后两条路的结果合并重排再喂给 LLM。

ATM-bench又发现，给了oracle evidence，仍然回答不出来!!!!!!!!!!!!!


3.局限性，混乱性！！！转：However…………

首先指出，这些工作需要一个清晰的分类和范式统一！！！大家现在在不同的子领域解决不同的子问题，社区极度混乱！！！没有人给一个统一范式。
咱们归结起来，就是一个共同问题：处理过去交互信息，如何影响未来决策——当前意图如何访问并暴露这些信息来支持决策。
>就叫Artifact Access Semantics Framework吧

上下文的扩展和使用………
    这个也要回应，我还见过一些对超长上下文做检索优化推理的…………
外化记忆系统………
    主要回答“过去交互如何被沉淀”。interaction traces 被压缩成什么artifact，压缩比例如何，泛化性和具体性如何权衡，生命周期如何维护。
    但压缩之后，未来决策仍然面临一个运行时问题：当前自然语言意图必须选择、访问、组织这些外部知识；否则系统即使拥有正确经验，也可能无法在当前决策中使用它。
RAG的优化…………
    过去交互已被压缩成 reusable artifacts，不同 artifact 使用语义也不同。
	raw trace 的使用语义是回放、搜索、定位、来源追踪。  
	episodic memory 的使用语义是检索、读取、按时间或实体过滤。  
	state summary 的使用语义是查当前承诺、查当前约束、查当前项目状态。  
	procedural skill 的使用语义是调用、实例化、执行、修正。  
	declarative rule 的使用语义是注入、约束、检查、拒绝违规动作。  
	workspace artifact 的使用语义是定位、读取、编辑、测试、验证。  
	execution graph 的使用语义是追踪、归因、最小修复。
    如果统一用 top-k text retrieval 访问，就会把 read、lookup、walk、execute、inject、verify 等不同语义压扁
    基于现有的substrate，RAG看来，只是记忆系统的单一原语


4.然后，we proposal，合，To address the above limitations，并且给出一个干净的framing, 

Our positon:Given reusable artifacts compressed from past interaction, how should a current intent access them so that they can influence future agent decisions?

We propose………… AAS Framework
一个长时程智能体将过去的交互存储为一个带类型的artifact存储。
给定记忆基底，用户输入自然语言意图，
系统必须先把它编译成某种访问形式，
怎么编译？记忆基底里的artifact，天生有使用语义。诱导出一些列的访问原语，进行查询/访问构造 q = C(u, c)。
然后返回一系列证据，暴露给LLM一个证据试图，最终才生成答案。

所以如果有错误，可能是，
1.一开始没存对，
  这个我们不管了，已有工作做了
2.意图识别错了导致查询没构造对，   
    这个分析时写使用语义和查询算子的错配，批评RAG就完事了。正向例子是Cupmem
3.构造对了但是访问原语没找到，
    这个是原语性能，工程优化问题，我们不做
4.找到了但是没呈现好
这个我们做  
5.呈现好了但是模型没用好
这个我们做

另外补充，4和5的分离，到底envidence view和decoder谁坏的诊断，这个没人做过，也是贡献。 ATM-bench上的实验。

然后我们不承诺给出全链路分析，这不是一篇文章的工作量可以承载的。
我们试着给出基于这套建模的实证分析，优化实践。
    
    
The contributions of this paper are as follow：


引用，贡献的具体表达，后期再修。


# 初稿

Large Language Model agents are moving from single-session assistants to persistent systems that act across long horizons, multiple tasks, and evolving user states. In such settings, future decisions depend on past interaction: user preferences, task commitments, tool outcomes, failed attempts, environmental changes, and previously learned procedures. Scaling the context window is an incomplete solution. Even when longer histories can be provided, relevant information may be buried, outdated, distracted by irrelevant context, or present but unused. Long-horizon agents therefore need mechanisms not only for retaining past interaction, but for making it usable at decision time.

Recent work has addressed the retention side of this problem by externalizing interaction history into reusable memory substrates. Agent memory systems extract user states, episodic records, summaries, relational stores, graphs, and semantic workspaces; skill and rule systems distill execution traces into reusable procedures or decision principles; production systems increasingly maintain persistent personalized memory outside the model context. Experience-compression frameworks make this trend explicit: raw interaction traces can be compressed into artifacts at different abstraction levels, trading specificity for reusability and lower context cost.

At runtime, however, most systems still expose these artifacts through retrieval. A current input is converted into a query, top-ranked memories or passages are retrieved, and the selected text is appended to the prompt. This interface has driven progress in RAG, hybrid retrieval, reranking, GraphRAG, and structured memory retrieval. But retrieval is only one way to access past experience. Code and corpus-search agents already rely on richer interfaces—grep, read, shell pipelines, execution, and navigation—that let agents search, filter, traverse, test, and verify. Memory systems are beginning to show the same pattern: hierarchical graphs support global selection, semantic workspaces return structured state summaries, and execution graphs support tracing and attribution.
    这一段，现在得小修了，mnemis，openviking等等，已经把多路访问做成了主流，目前这个已经是主流范式了。GraphRAG也早就不仅仅是更好的组织，而变成了更好的访问，按图访问。这篇文章的introduction还得压一下，我们的gap不从这里开始，这里不必"however",however在下面那个层级。



These developments expose a missing abstraction. Existing work studies how history is stored, compressed, retrieved, structured, or debugged, but lacks a unified account of how a current intent should access heterogeneous memory artifacts for decision-making. This matters because different artifacts imply different operations: traces are replayed or traced, episodes are read and composed, states are queried, skills are invoked, rules are injected or checked, workspaces are edited or verified, and execution graphs are traversed. Treating all of them as top-(k) text chunks collapses distinct access semantics into a single retrieval primitive.
    这一段还行，但是可以削弱语气，因为这个只是讲故事的语言而已，不是理论贡献。

This missing access layer also limits diagnosis. A memory-augmented agent may fail because the relevant experience was never stored, because the current intent selected the wrong access operation, because the access primitive missed the artifact, because the correct evidence was exposed in a poor view, or because the decoder failed to use a sufficient view. End-to-end memory QA accuracy cannot distinguish these cases. Failures under oracle-evidence conditions make the limitation especially clear: even when retrieval is bypassed, memory use can fail at the level of evidence presentation or decoder use.

This paper studies runtime access over reusable memory artifacts. Our position is that past interaction must be externalized for long-horizon agents, but reusable artifacts do not become useful merely by existing. A current intent must be compiled into artifact-appropriate access operations, and the accessed information must be organized into a decision-facing view or state before it can affect the next action. We therefore model long-term memory use as typed access over externalized artifacts, where retrieval is one primitive among a broader set of operations such as read, lookup, walk, execute, inject, verify, and trace.
    这里可以削弱claim，因为主贡献不在这里。
    我的意思大概是，写一个完整的system map，然后openviking是目前算是从query到access最全的，但是它也缺evidence-view。我们这篇文章就研究这个。大概就是，先展示system 演进过程，然后清晰地建模分类各个特性，然后给出gap。


We instantiate this framing on long-term personalized memory QA. Using controlled evidence conditions, we decompose failures across access, evidence selection, view realization, and decoder use. We then test whether alternative evidence views make the same evidence more usable, and use lightweight internal evidence-use probes to examine whether improved views increase the decoder’s use of gold evidence. 

contribution as follow…………

（具体后面再修）

---

Large language model agents are moving from single-session assistants to persistent systems that act across long horizons, multiple tasks, and evolving user states. In such settings, future decisions depend on past interaction—user preferences, task commitments, tool outcomes, and previously learned procedures—making it necessary not only to retain interaction history but to make it usable at decision time.

Recent work has made strong progress on the first part of this problem. Agent memory systems externalize interaction history into reusable substrates: user states, episodic records, relational stores, graphs, semantic workspaces, skills, rules, and compressed experience artifacts. Runtime access has also advanced beyond flat top-k retrieval. Modern systems combine retrieval with reranking, graph traversal, hierarchical selection, tool execution, source reading, and trace-based attribution. Different artifacts imply different operations—traces are replayed, states are queried, rules are checked, and execution graphs are traversed—and recent systems increasingly avoid collapsing all memory access into a single retrieval primitive.

These developments sharpen the access layer, but they also expose its limit. The field has become good at making evidence easier to find. It has not solved what happens after evidence is found. In long-term personalized memory QA, aggregation-heavy questions—numeric reasoning and open-ended queries requiring cross-evidence composition—still fail under oracle evidence conditions, where the correct evidence is already present. This is not a retrieval failure. It is a post-access failure. Existing memory systems optimize the geometry of access, but hard memory use requires the algebra of evaluation.

We study this post-access regime. Access determines which evidence reaches the model; post-access evaluation determines whether that evidence is exposed in a decision-sufficient view, whether variables are stably bound across multiple evidence items, and whether the final answer is constrained to the evidence-defined valid set. A flattened textual view may present a timestamp and a caption but omit the relations, quantities, source pointers, or modality-specific structure needed for aggregation. The evidence is in context, but the view is not decision-sufficient.

This distinction matters because language-only decoding is a weak evaluator over recalled evidence. Without explicit variable binding and constraint enforcement, the model defaults to semantic proximity: it matches, paraphrases, and classifies fluently, but it does not reliably execute multi-variable aggregation, conflict resolution, or discrete computation. Soft controls—pretraining, instruction tuning, prompting, chain-of-thought—can bias the model toward aggregation-like trajectories, but they do not make the output evidence-valid. They reshape the proposal distribution; they do not enforce the answer set.

This paper instantiates the access-evaluation decomposition in long-term personalized memory QA. Using controlled evidence conditions, we isolate failures across access, evidence view, and decoder use. We test whether alternative evidence views make the same evidence more usable, and whether improved views increase the model's use of gold evidence. Our analysis centers on aggregation-heavy cases—numeric and open-ended questions—where evidence is present but answering requires cross-evidence binding, numerical aggregation, conflict resolution, or multimodal source inspection. In these cases, flattened textual views and language-only decoding leave the model to implicitly maintain variables, execute constraints, and perform calculations, producing a class of failures that better retrieval cannot fix.

The broader thesis is simple: the first half of multimodal long-term memory systems is evidence access; the second half is evidence aggregation. Existing systems have advanced the first half substantially. The second half—view construction, variable binding, discrete operator execution, and evidence-valid decoding—remains the bottleneck.

Contributions as follows. [To be revised.]


大型语言模型智能体正从单次会话的助手，演变为在长时间跨度、多任务和不断演变的用户状态中持续运行的系统。在此类场景中，未来的决策依赖于过去的交互——用户偏好、任务承诺、工具执行结果以及先前学到的流程——这使得系统不仅需要保留交互历史，还需要在决策时刻使其可用。

近期工作在问题的前半部分取得了显著进展。智能体记忆系统将交互历史外化为可复用的基底：用户状态、情节记录、关系存储、图谱、语义工作区、技能、规则以及压缩后的经验制品。运行时访问也已超越了扁平的top-k检索。现代系统将检索与重排序、图谱遍历、层级选择、工具执行、源数据读取以及基于溯源追踪的归因结合起来。不同的制品意味着不同的操作——追踪记录被回放，状态被查询，规则被检查，执行图谱被遍历——近期系统越来越多地避免将所有记忆访问坍缩为单一的检索原语。

这些进展强化了访问层，但也暴露了它的局限。领域内已经擅长让证据更容易被找到，但尚未解决证据被找到之后发生了什么。在长期个性化记忆问答中，即使在理想证据条件下（正确的证据已经存在），聚合密集型问题——数值推理和需要跨证据组合的开放式查询——仍然会失败。这不是检索失败，而是检索后失败。现有记忆系统优化的是访问的几何，但困难的记忆使用需要的是求值的代数。

我们研究的是这一检索后的阶段。访问决定了哪些证据能够到达模型；检索后评估则决定了这些证据是否以决策充分的视图被呈现，变量是否在多个证据条目之间被稳定绑定，以及最终答案是否被约束在证据定义的有效集内。一个被压平的文本视图可能呈现了时间戳和标题，却遗漏了聚合所需的关系、数量、来源指针或模态特定的结构。证据就在上下文中，但视图并不决策充分。

这一区分之所以重要，是因为纯语言解码对已召回的证据而言是一个薄弱的评估器。在缺乏显式变量绑定和约束强制执行的情况下，模型默认走向语义邻近：它流畅地匹配、转述和分类，但无法可靠地执行多变量聚合、冲突消解或离散计算。软控制——预训练、指令微调、提示工程、思维链——可以将模型偏向聚合类轨迹，但它们不会使输出证据有效。它们重塑的是提议分布，而不是强制执行答案集。

本文将访问-评估分解实例化到长期个性化记忆问答中。通过受控的证据条件，我们将失败分解到访问、证据视图和解码器使用这三个维度上。我们测试了不同的证据视图是否使相同的证据变得更有用，以及改进后的视图是否提高了模型对金标准证据的使用。我们的分析聚焦于聚合密集型案例——数值题和开放式问题——在这些案例中，证据虽然存在，但回答需要跨证据绑定、数值聚合、冲突消解或多模态来源检查。在这些情况下，被压平的文本视图和纯语言解码让模型隐式地维护变量、执行约束并进行计算，从而产生了一类更好的检索无法修复的失败。

更宏观的论点是简洁的：多模态长期记忆系统的上半场是证据访问，下半场是证据聚合。现有系统已经大幅推进了上半场。下半场——视图构建、变量绑定、离散算子执行以及证据有效的解码——仍然是瓶颈。

贡献如下。[待修订]