# Fomulation
In the rest of this paper, we detail the AAS framework (Section 2) 

一个长时程智能体将过去的交互存储为一个带类型的artifact存储。
给定记忆基底，用户输入自然语言意图， 
系统必须先把它编译成某种访问形式，
怎么编译？记忆基底里的artifact，天生有使用语义。诱导出一些列的访问原语，进行查询/访问构造 q = C(u, c)。
然后返回一系列证据，暴露给LLM一个证据试图，最终才生成答案。

“压缩轴有 generalizability-specificity trade-off。  
访问轴也应该有自己的 trade-off性质。
可能是：
	低交互访问成本低，但只能暴露局部相关片段。  
	高交互访问成本高，但能执行、验证、追踪来源、处理冲突。  
	单次访问延迟低，但容易形成不完整视图。  
	多步访问延迟高，但能逐步补足缺失角色。  
	文本化访问通用，但会抹掉 skill/rule/tool 的使用语义。  
	原生接口访问保留使用语义，但需要更复杂的路由和控制。
验证？”
这个trade off不做，做不完，太麻烦了，谁爱做谁做。


所以如果有错误，可能是，
1.一开始没存对，
  这个我们不管了，已有工作做了
2.意图识别错了导致查询没构造对，   
    这个分析时写使用语义和查询算子的错配，批评RAG就完事了。正向例子是Cupmem
3.构造对了但是访问原语没找到，
    这个是原语性能，工程优化问题，我们不做
4.找到了但是没呈现好
这个我们做  view-use failure：证据存在但呈现不好；
5.呈现好了但是模型没用好
这个我们做  decoder-use failure：证据呈现足够但模型没用好

另外补充，4和5的分离，到底envidence view和decoder谁坏的诊断，这个没人做过，也是贡献。 ATM-bench上的实验。

然后我们不承诺给出全链路分析，这不是一篇文章的工作量可以承载的。
我们试着给出基于这套建模的实证分析，优化实践。

---

以下推演本section写入论文的逻辑链。

1.专门写一小节Experience Compression Spectrum，已经定义：
interaction trace $T$ = ${(s_t,a_t,o_t,f_t)}_{t=1}^{N}$
compression function $C_L$:$T→K_L$ 

交互轨迹被压缩成不同层级的知识制品：raw trace、episodic memory、procedural skill、declarative rule。(它关心的是输出制品处在哪个压缩层级，以及压缩带来的泛化性、具体性、成本和信息保留权衡)

然后本文补充定义，一个 compressed artifact 不只是内容载体，它还带有使用语义$a=(ℓ,x,Σ_a​)$
	其中 $ℓ$ 是 compression level，$x$ 是 artifact payload，$\Sigma_a$​ 是这个 artifact 的 usage signature，也就是它在未来决策中允许或期望的使用方式。
	episodic memory 的 signature 可能包含 read、retrieve、filter-by-time；
	procedural skill 的 signature 可能包含 instantiate、execute、adapt；
	declarative rule 的 signature 可能包含 inject、constrain、check；
	raw trace 的 signature 可能包含 search、replay、source-trace；workspace file 的 signature 可能包含 locate、read、edit、test、verify。
过去交互已被压缩成 reusable artifacts，不同 artifact 使用语义也不同。
	raw trace 的使用语义是回放、搜索、定位、来源追踪。  
	episodic memory 的使用语义是检索、读取、按时间或实体过滤。  
	state summary 的使用语义是查当前承诺、查当前约束、查当前项目状态。  
	procedural skill 的使用语义是调用、实例化、执行、修正。  
	declarative rule 的使用语义是注入、约束、检查、拒绝违规动作。  
	workspace artifact 的使用语义是定位、读取、编辑、测试、验证。  
	execution graph 的使用语义是追踪、归因、最小修复。

压缩轴回答：interaction trace 被压成什么artifact。 


2.再定义 access interface，
访问轴应该回答：当前任务通过什么 interface 使用这些 artifact。

访问接口可以只是一次性选择相关文本，也可以读取状态，也可以追踪来源，也可以遍历轨迹，也可以执行技能，也可以调用工具验证，也可以强制注入规则。

多路访问是“不同 artifact 不能用同一个访问接口抹平”。
    如果统一用 top-k text retrieval 访问，就会把 read、lookup、walk、execute、inject、verify 等不同语义压扁，

访问轴的核心是当前意图选择何种 usage interface，使过去artifact以合适方式进入当前决策。


当前系统映射的结构性问题分析：
	RAG / memory retrieval：passive top-k selection。  
	stateful memory / MemoryOS 类：state lookup / structured read。  
	graph memory / Mnemis 类：graph traversal / hierarchical selection。  
	GrepSeek / Direct Corpus Interaction：interactive corpus search。  
	code agents：workspace interaction with read/search/edit/test。  
	skill agents：skill retrieval plus execution。  
	rule systems / CLAUDE.md / .cursorrules：mandatory injection / constraint checking。  

>访问轴是artifact的使用语义的运行时展开。
>压缩轴：interaction experience 被压缩成什么 artifact。  
>使用语义：这个 artifact 在未来决策中应该如何发挥作用。  
>访问轴：当前意图通过什么接口实现这种使用语义。
>compression → artifact → usage semantics → access interface → future decision

声明，本文只…………

3.AAS framework
artifact substrate：过去交互外化后的基底；
artifact access semantics：不同 artifact 的使用语义；
access primitive：retrieve / read / lookup / walk / invoke / inject / verify / trace；
decision-facing view/state：访问结果暴露给 decoder 的形式；
view-use failure：证据存在但呈现不好；
decoder-use failure：证据呈现足够但模型没用好。


我们将这些运行时使用方式形式化为 typed access primitives。设系统暴露的原语集合为 $P$。一个原语 $\rho\in P$ 可以写成  
$$
\rho=(\mathrm{dom}, \mathrm{in}, \mathrm{out}),
$$
其中 $\mathrm{dom}$ 表示该原语适用的 artifact 类型，$\mathrm{in}$ 表示输入参数类型，$\mathrm{out}$ 表示返回结果或运行时效果类型。比如，top-$k$ retrieval 作用于文本化 memory records，输入 query 和 $k$，返回 ranked items；hierarchical browse 作用于 category graph，输入 query 和当前节点，返回被选择的子节点或子树；trace primitive 作用于 ordered traces，返回时间链或来源链；skill primitive 作用于 procedural artifacts，返回执行结果；rule primitive 作用于 declarative artifacts，返回约束注入结果或合规判定；workspace primitive 作用于 files、logs 和 tests，返回读取、修改或测试结果。

一次运行时访问是一条 primitive trace：  
$$
p=((\rho_1,\theta_1,r_1),\ldots,(\rho_T,\theta_T,r_T)).
$$  
其中第 $i$ 步选择原语 $\rho_i$，给定参数 $\theta_i$，得到返回结果 $r_i$。**后续步骤的参数可以依赖之前的返回结果**。因此，primitive trace 可以表示多种真实系统中的访问过程：相似度检索、层级浏览、shell-command 搜索、文件读写测试、状态查询、trace 追踪等。

给定一组 primitives $P$，所有可由这些原语及其组合规则形成的 primitive traces 构成一个诱导的访问程序空间，记为 $\mathcal L(P)$。这里 $\mathcal L(P)$ 不需要被显式枚举；实验中实际观测和记录的是由某个访问策略产生的一条具体 trace。
> [!warning]
> 因为“组合访问程序空间”太理论化，我们无法证明整个空间的性质。真正能实验记录的是 trace，不是空间。空间 $\mathcal L(P)$ 只在定义里出现：
> $\mathcal L(P): \text{all primitive traces induced by } P$
> 然后回到实际：
> $\pi(u,h_t)\rightarrow(\rho_t,\theta_t),\quad \tau_\pi\in\mathcal L(P)$
> 
给定一个意图 $u$，一个访问策略 $\pi$ 生成一个原语轨迹
$$
p_\pi(u,D)=((\rho_1,\theta_1,r_1),\ldots,(\rho_T,\theta_T,r_T)),
$$
其中每一步选择一个原语 $\rho_t$，提供参数 $\theta_t$，并获得结果 $r_t$。该轨迹必须满足一个预算协议 $\beta$，该协议可能限制调用次数、返回项数、遍历深度、上下文长度、延迟或工具使用轮次。

轨迹返回的信息随后被序列化为一个证据视图：
$$
v = V(u,p_\pi(D)).
$$

下游模型 $g$ 接收当前意图、可选上下文 $c$ 以及证据视图：
$$
\hat y = g(u,c,v).
$$

分析的核心对象并非相关制品是否存在于 $D$ 中，也非检索到的项与查询的相似度高低。核心对象是：原语轨迹是否暴露了一个对决策充分的证据视图。

对于每个任务 $u$，定义一组所需的视图角色：
$$
R_u=\{r_1,\ldots,r_k\}.
$$
这些角色描述了在当前决策得到支持时，证据视图中必须可观察到的内容。在个人记忆问答中，典型角色包括证据可见性、源身份、时间定位、空间定位、指代绑定、多证据聚合、冲突权威性、时效性和弃权支持。一个视图 $v$ 暴露了角色 $r$，如果该角色出现在模型可见的内容中，而不仅仅是内部存储。令$\Gamma(v)$表示 $v$ 暴露的角色集合。当$R_u \subseteq \Gamma(v)$时，视图对于任务 $u$ 是充分的。

这给出了一个视图级别的失败分解。如果所需artifact在 $D$ 中缺失，则为基底失败。如果artifact存在但没有任何预算可行的原语轨迹能暴露它，则为访问失败。如果轨迹暴露了相关证据，但序列化视图缺少必要的绑定、权威关系、聚合结构或定位线索，则为视图构建失败。如果视图暴露了所有所需角色而模型仍然回答错误，则将失败归因于下游解码或推理。

这一区分将存储、访问、视图构建和解码分开：
$$
D \xrightarrow{p_\pi} p_\pi(D) \xrightarrow{V} v \xrightarrow{g} \hat y.
$$
因此，同一artifact存储可以在不同的原语集、预算、轨迹或视图构造器下支持不同的结果。相反，两个系统可能检索到相同的证据项，但最终视图是否暴露了任务所需的角色可能不同。






# 初稿

## 2 Artifact Access Semantics

The *Experience Compression Spectrum* (ECS) studies how an agent's interaction trace is transformed into reusable artifacts \cite{experience_compression_spectrum}. Following ECS, let an interaction trace be $T=\{(s_t,a_t,o_t,f_t)\}_{t=1}^{N}$, and let a level-$L$ compression function be

$$
C_L:T\rightarrow K_L .
$$

Different choices of $L$ produce artifacts at different abstraction levels, such as raw traces, episodic memories, procedural skills, declarative rules, state summaries, or workspaces. This compression axis answers a storage-side question: what does past interaction become?

We study the complementary access-side question: once past interaction has been compressed into artifacts, how does a current intent use them for a future decision? A compressed artifact is not merely a content payload. It also carries usage semantics: the ways in which the artifact is expected to participate in later decisions. For example, a trace is searched or replayed; a state is queried; a graph is traversed; a skill is invoked; a rule is injected or checked; a workspace is read, edited, or verified.

We call this problem *Artifact Access Semantics* (AAS). AAS studies how reusable artifacts derived from past interaction are accessed according to their usage semantics and exposed so that they can support future agent decisions. Its core chain is:

$$
\begin{aligned}
\text{compression}
&\rightarrow
\text{artifact}
\rightarrow
\text{usage semantics} \\
&\rightarrow
\text{access interface}
\rightarrow
\text{decision}.
\end{aligned}
$$

Thus, while the compression axis asks how experience is retained, the access axis asks how retained experience becomes actionable.

### 2.1 Typed Artifacts

Let $\mathcal{A}=\{a_i\}_{i=1}^{M}$ denote the artifact substrate available to an agent at runtime. We write each artifact as

$$
a_i=(\ell_i,x_i,\Sigma_i),
$$

where $\ell_i$ denotes its abstraction or compression level, $x_i$ is the artifact payload, and $\Sigma_i$ is its usage signature. The usage signature specifies which operations the artifact naturally supports and how it is expected to affect future decisions.

Different artifact types induce different signatures. Raw traces support search, replay, and source tracing. Episodic memories support retrieval, reading, and filtering by time or entity. State summaries support lookup of current commitments, constraints, and project state. Procedural skills support invocation, instantiation, execution, and adaptation. Declarative rules support injection, constraint checking, and violation prevention. Workspace artifacts support locating, reading, editing, testing, and verification. Execution graphs support tracing, attribution, and minimal repair.

The access axis is the runtime unfolding of these usage signatures. If all artifacts are exposed through the same top-$k$ text interface, distinct semantics such as read, lookup, walk, invoke, inject, verify, and trace are collapsed into a single retrieval primitive.

### 2.2 A System Map of Runtime Access

Current systems instantiate different parts of the access axis, often without making the axis explicit. The table sketches several common substrate-interface-view patterns. The purpose of the map is not to exhaust the design space, but to show that retrieval is one access interface rather than the general form of memory use.

| Line of work                   | Artifact substrate                   | Runtime access interface                 | Exposed decision view                | AAS perspective                                                             |
| ------------------------------ | ------------------------------------ | ---------------------------------------- | ------------------------------------ | --------------------------------------------------------------------------- |
| Long-context agents            | Raw interaction history              | Full-context reading                     | Long prompt context                  | History is present but not necessarily localized, updated, or used.         |
| RAG / memory retrieval         | Text chunks or memory records        | Top-$k$ retrieval and reranking          | Ranked evidence passages             | Retrieval exposes local relevance but may miss required roles or structure. |
| GraphRAG / hierarchical memory | Entity, relation, or category graphs | Graph traversal or global selection      | Graph-selected evidence              | Access begins to depend on artifact structure, not only similarity.         |
| Episodic / workspace memory    | Actor-state-event workspaces         | Entity or state lookup                   | Structured episodic summaries        | The artifact returns state-like views rather than raw chunks.               |
| Memory operating systems       | Persistent user or task states       | State lookup and memory update           | Personalized memory context          | Stronger substrate management, but runtime use may still be retrieval-like. |
| Direct corpus / code agents    | Raw corpora, files, repositories     | grep, read, shell, execution, navigation | Composed evidence or verified result | The interface expands the agent's action space beyond top-$k$ passages.     |

### 2.3 Runtime Access as Primitive Traces

We formalize runtime access as a trace of typed access primitives. Let $\mathcal{P}$ be the set of primitives exposed by a memory system. A primitive $\rho\in\mathcal{P}$ is written as

$$
\rho=(\mathrm{dom},\mathrm{in},\mathrm{out}),
$$

where $\mathrm{dom}$ specifies the artifact type it operates on, $\mathrm{in}$ specifies its input parameter type, and $\mathrm{out}$ specifies the returned observation or runtime effect. Examples include top-$k$ retrieval over text records, structured state lookup, hierarchical graph traversal, temporal or source-chain tracing, skill invocation, rule injection, file reading, execution, and verification.

At runtime, a current intent $u$ induces an access process over the artifact substrate. We represent this process as a primitive trace:

$$
\tau_\pi(u,\mathcal{A})
=
((\rho_1,\theta_1,r_1),\ldots,(\rho_T,\theta_T,r_T)),
$$

where $\rho_t$ is the access primitive selected at step $t$, $\theta_t$ is its parameterization, and $r_t$ is its returned result. The trace may be single-step, as in standard retrieval, or multi-step, as in graph traversal, corpus search, workspace interaction, or provenance tracing. Later parameters may depend on earlier results, so the trace can represent iterative access rather than a one-shot query.

The returned results are then organized into a decision-facing view:

$$
v=\mathcal{V}(u,\tau_\pi),
$$

which is passed to the downstream decoder:

$$
\hat y=g_\theta(u,v).
$$

The central object of AAS is not whether a relevant artifact exists, nor whether a retrieved passage is similar to the query. The central object is whether the access trace exposes a view that supports the current decision.

### 2.4 Diagnostic Scope

Existing work has made substantial progress on the construction side of long-term memory: how past interactions are compressed, written, updated, retrieved, and traced across memory systems. AAS builds on these advances by focusing on the subsequent runtime boundary where available artifacts are accessed and exposed for a current decision. We therefore analyze memory use after relevant artifacts or oracle evidence are available, asking whether failures arise from how evidence is presented to the decoder or from the decoder's use of an otherwise sufficient view.

We distinguish two downstream failure modes. A view-use failure occurs when the needed evidence exists and can be accessed, but the exposed view omits decision-critical structure, such as referential bindings, temporal cues, source relations, aggregation structure, freshness, or conflict authority. A decoder-use failure occurs when the view exposes the required information, but the decoder still fails to produce the correct answer or action.

This focus turns end-to-end memory QA failures into a more diagnostic question: beyond whether the system retrieves the right evidence, does it expose that evidence in a decision-facing form, and does the decoder actually use it?

































