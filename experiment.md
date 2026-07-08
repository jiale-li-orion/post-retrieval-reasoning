1.一开始没存对， 这个我们不管了，已有工作做了 


2.意图识别错了导致查询没构造对，
使用语义和查询算子的错配

这个我们也不做了，openviking之类的，已经把access做得很好了。


3.构造对了但是访问原语没找到， 这个是原语性能，工程优化问题，我们不做 



4.找到了但是没呈现好 这个我们做 view-use failure：证据存在但呈现不好； 


5.呈现好了但是模型没用好 这个我们做 decoder-use failure：证据呈现足够但模型没用好

另外补充，4和5的分离，到底envidence view和decoder谁坏的诊断，这个没人做过，也是贡献。 ATM-bench上的实验。

contribution集中在2，4，5，尤其是把4，5做好。



小的实验启发，或者说想要论证的，进而的更大的猜想和观点。


ATM-Bench-Hard 的失败主要集中在 number 和 open_end 类型——这两类问题通常需要跨多条证据的数值聚合或语义推理，而不是简单的"找到匹配项"。

这里注意，我并不是声明统计意义上记忆失败主要是这两类。

SGM 的 batch_fields 格式 type,timestamp,location,short_caption,caption,ocr,tags 把所有多模态证据压平成了文本行。模型拿到的是：
type: image, timestamp: ..., location: ..., short_caption: "a cup of tea", ...
但这没有告诉你：这个图片是 "Teayan Yuese" 的菜单、多少钱、在哪天——你需要模型自己从文本描述中"脑补"视觉信息。这验证了论文的 视图不充分（view-use failure） 论点：证据存在且被选中，但暴露的视图遗漏了决策关键的结构（如 multi-evidence 的数值聚合关系）。
    多模态记忆系统中，对于异构数据压缩成的文本evidence视图，往往会丢失信息。我们始终需要保留对源数据的索引，在不确定时看原始数据。（**信息在 view 里丢了就补不回来**）
    现有记忆系统刷分，分数增益可能更多的是来自于把记忆洗成了结构化图，把搜索空间直接压小，使得模式识别更加容易。而一旦涉及到多证据聚合推理，哪怕是最简单的数值计算，也会出现偏差与错误。

我感觉一大半的多路访问还有检索提升，本质上都是通过洗数据，提升了那类通过匹配就能拿到分数的case的acc，但多证据聚合推理仍然是难题。


这批判的不仅仅是相似度检索，还有那些图检索等等。长期记忆系统的下半场不是更好的答案匹配和证据召回，而是证据聚合推理！！！

从搜索空间的优化到证据聚合推理，我觉得我们可以搞这个。


现在抓到的是一个更具体、更可证伪的命题：

多模态长期记忆系统的上半场是 evidence access，下半场是 evidence aggregation。现有系统的大部分增益来自把检索空间洗干净、把匹配型问题变简单；但在 number / open-ended 这类需要多证据组合、冲突裁决、数值计算、跨模态语义补全的问题上，增益没有真正转化成推理能力。

现在感受最深的就是，LLM回答在无显式“推理”暗示下，依赖语义邻近匹配。 又或者说，LLM就是个语义邻近匹配器，不加“推理”这个语义，它就不推理，你外化系统客观验证，它自己就幻觉偏移。
    包括和GPT，我提到一个命题，之后的一切搜索就被它影响，所有的生成都受到这个命题的邻近引力。这就是为什么一直需要"对齐约束"，需要"外部验证"。

（LLM 的默认行为是沿当前上下文的语义邻近场做高概率延展；所谓推理，只有在提示、任务格式、外部工具、验证器、评分规则把它强行拉到组合/约束执行模式时，才会部分出现。所以它不是稳定的 reasoner，而是一个会被任务语义、提示语、上下文主题强烈牵引的 conditional generator）

所谓幻觉，就是语义空间上顺滑的偏移。

单步匹配题，LLM 很强，因为它正好擅长语义邻近：找到相关字段、复述、匹配、归类、列 ID。

多证据组合题，LLM 开始崩，因为它不能只靠邻近。它必须保持多个变量、执行约束、排除干扰、做计算、检查一致性。除非任务格式强迫它进入这种模式，或者外部系统替它执行这些步骤，否则它会回到最顺的语义路径。

这个其实就已经给出了当前LLM增强的两种范式了。
1是提示词工程，包括COT等等推理增强，然后其实，广义上，预训练也算吧。
    软控制，改变模型的条件分布，让它更可能进入某种行为模式——塑造模型内部的概率倾向。区别只是作用尺度不同。pretraining 改整个 prior，prompt 改当前 conditional prior，CoT 触发某类轨迹分布。
pretraining
instruction tuning
RLHF / preference tuning
prompting
few-shot examples
CoT / self-consistency
schema-in-prompt
role prompt
“请仔细推理”

2是外部system约束，也可以说是harness吧。
    硬约束 / harness，交给外部系统执行、检查、约束、记录。
calculator
code interpreter
verifier
schema validator

让模型在语言里模拟变量操作。它可能做对，也可能顺着最强语义邻近项跑偏，这是很蠢的。模型可以负责意图识别、查询规划、自然语言表达，但不能独自保管所有中间状态。

把模型放进一个不会完全漂移的轨道里，这应该是2026后续AI发展的共识。

LLM 默认不是一个稳定执行约束的 reasoning machine；
    它确实能在特定条件下进入更强的推理模式。比如 CoT、Auto-CoT、reasoning-style prompting 都能改变输出轨迹；Auto-CoT 论文也明确说“let’s think step by step”能生成推理链，但生成链可能出错，需要通过多样性等机制缓解。 这说明模型不是完全不会推理，而是推理行为不稳定，依赖触发条件、格式、上下文、验证机制（这些也会随着上下文的增长，效果稀释）
它更像一个会被上下文语义场牵引的 conditional generator。



---





文章在说什么


现在的记忆系统很会"找证据"，但不会"用证据"。我们证明了这个"不会用"是可以拆解、可以测量、可以修复的。


开头：从一个反常现象说起
你让 GPT-5 回答"我在葡萄牙住酒店花了多少钱"。你把正确的收据、邮件、发票全部塞进 context（Oracle evidence，完美证据）。GPT-5 看着这些证据，回答："€408 + €445.26 = €853.26"。
答案是 €842.97。
证据就在那里，一个 token 都没少。模型就是算不对。

这不是检索的问题——证据找到了。这是找到之后的问题。你的证据在 model 眼里长什么样？model 能不能从这个"长相"里把该绑定的变量绑对、该执行的操作执行对？


第一步：把 memory use 拆成三段
以前做记忆的人主要在想一件事：怎么把证据找到。GraphRAG、reranking、hierarchical retrieval，全是检索优化。

但一个完整的记忆系统其实要过三关：
1. Access：证据在不在 memory 里？能不能被检索到？
2. View：检索到的证据，以什么格式暴露给 model？展开了哪些字段、隐藏了哪些关系？
3. Eval：model 拿着这个 view，能不能算出正确答案？
以前的研究基本只在第一关上使劲。我们证明了第二关和第三关才是 Hard set 上的真正瓶颈。

第二步：定义什么是"对的"
一个 query 的答案不是 model 随便说的一个句子。证据结构 $\mathcal{A}$ 严格定义了哪些答案是合法的。
比如"葡萄牙酒店花了多少钱"：
- 证据里有两笔：€408（booking confirmation）和 €445.26（invoice）
- 但 €408 是旧的 booking，€445.26 是更新后的 invoice
- 正确答案是 €842.97（两笔之和），还是 €445.26（只算最新的）？取决于 gold program 怎么定义
我们给每个 case 标注了一个 gold evaluation program $P_q$：它规定了该用哪些字段、执行什么操作、按什么优先级。答案只有在 $\eta(y)in\mathcal{Z}_q(\mathcal{A})$ 时才对——不是 model 觉得对就对，是证据结构说了算。


第三步：view collapse——信息在 view 里丢了就补不回来
这是理论核心。
证据不是直接喂给 model 的。它先经过一个 view pipeline：哪些字段展开了、哪些关系标出来了、什么格式呈现的。
比如 ATM-Bench 的 SGM（Schema-Guided Memory）把每张图片压缩成：
ID: 20231210_111815
Timestamp: 2023-12-10 11:18:15
Location: Ernest N. Morial Convention Center, New Orleans...
OCR: NeurIPS 2023
Tags: neurips 2023, conference, event...
看起来信息很全。但有个 case 是这样的：query 问"Grace 陪我吃饭的照片有哪些"。SGM 的 tags 里有 breakfast, dessert, pastry, cafe——没有 "Grace" 这个人名。entities 字段里检测到的全是 "café"（重复了 70 多次），没有人名。
所以 model 看到这些证据，回答 "Unknown"。不是 model 笨，是 view 里根本就没有 "Grace" 这个变量。
Definition 1 说的就是这件事：如果两个不同世界的证据经过 view 后变成了一样的输出，那任何 decoder 都不可能同时答对两个世界。信息在 view 里丢了，就补不回来。
我们的实验验证了：给原图（Raw oracle）之后，这个 case 直接从 0 分跳到满分。说明证据里有 Grace 的信息，只是 SGM 的 view 把它压掉了。


第四步：binding error 会传播
Decoder 不是一步到位的。它要一步一步来：先找到相关证据，再绑定变量，再执行操作。
每一步都可能绑错。关键是错误会传播。
比如算葡萄牙酒店总花费：
1. Step 1：找到两笔费用。如果这一步把 €408 的 booking confirmation 当成了"有效"费用（实际应该被 invoice 覆盖），就绑错了。
2. Step 2：把两笔加起来。€408 + €445.26 = €853.26。
3. Step 3：输出答案。
第一步的 binding error 传播到第二步的 sum 操作，最终输出错误答案。
Proposition 2 给了一个 bound：最终误差 $e_T$ 取决于 binding count（绑定几个变量）、operator count（执行几个操作）、override depth（覆盖链多长）。操作越多、绑定越多，误差越容易累积。
我们的实验验证了：算术聚合（MONEY/DURATION/COUNT，需要 sum、subtraction、count 操作）在 Raw oracle 下仍然 25%/0%/0%，而列举聚合（LIST-AGG，只需要 collect）在 Raw oracle 下到 91%。操作越复杂，失败率越高，完全符合 bound 的预言。


第五步：Harness 可以修
Prompting/CoT 只是让 model "更努力地想"，但不改变 model 的 interface。它还是在 proposal distribution 上做文章。
Harness 改变了 interface：
- Operator harness：不让 model 自己加法，而是提取出数字后外部执行 sum。这绕过了 model 的算术弱点。
- Verifier harness：model 给出候选答案后，外部检查它是否满足 evidence-defined 约束（比如数值是否在 evidence 里出现过、格式是否合法）。不满足就拒绝。
§3.4 的预言是：harness 应该比 prompting 更有效地降低 semantic invalid rate，因为它不依赖 model 的内部计算能力。
我们还没跑 harness 实验，但 Raw oracle 的数据暗示了可能性：CASE 4（葡萄牙酒店）Raw 输出了 "408.00 EUR and 445.26 EUR"——它把两个数字都列出来了，只是没加对。如果 harness 接管加法，这个 case 就能修。



实验设计：怎么证明上面说的不是废话
§4 设计了三组诊断实验：
H1：complexity 预测 failure
给每个 case 标注 $k$（binding count）、$o$（operator count）、$c$（override depth）、$m$（conflict degree）。画 accuracy vs complexity 的曲线。如果曲线单调下降，说明 post-recall failure 不是随机的，而是可以被 evaluation complexity 预测的。
H2：view insufficiency 预测 error
定义 VIR（View Insufficiency Rate）：view 缺少 required variable 的比例。如果 VIR 高的 case 错误率也高，说明 view 是瓶颈。
比较 flat view vs source-indexed view vs state view。如果 state view（暴露了所有需要的变量和关系）比 flat view 好，说明 view 确实是瓶颈。
H3：harness 降低 semantic invalidity
比较 direct answering / CoT / scratchpad vs operator harness / verifier harness。如果 harness 的 invalid rate 更低，说明 evaluation-centric 干预比 proposal-shaping 更有效。


总结：文章的逻辑链
Oracle evidence 给了还是错
        ↓
说明瓶颈不在 access，在 post-access
        ↓
拆成 ViewOK（view 够不够）和 EvalOK（decoder 会不会算）
        ↓
ViewOK：view collapse 理论 + 实验验证（SGM vs Raw）
EvalOK：binding error propagation 理论 + 实验验证（complexity curve）
        ↓
干预：view 升级（state view）+ harness（operator/verifier）
        ↓
预言：两个干预独立有效，且不依赖 retrieval 质量


1.ViewOK（view 够不够）  这个的最优解就是，默认最简单的方式，检测出信息不够的时候，成功干预出什么时候不够，然后去找源数据，回答。这个不新奇。

2.
软：cot等等，reasoning模式等等
硬：给它tool，让system可验证
