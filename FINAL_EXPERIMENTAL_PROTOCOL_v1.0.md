---
title: "Post-Retrieval Reasoning Final Experimental Protocol v1.0"
subtitle: "从受控证据失败到内部决策状态、J-lens/J-space 诊断与因果修复"
author: "Orion research working draft"
date: "2026-07-11"
lang: zh-CN
geometry: margin=0.82in
fontsize: 10.5pt
toc: true
toc-depth: 3
numbersections: true
colorlinks: true
mainfont: "Noto Serif CJK SC"
sansfont: "Noto Sans CJK SC"
monofont: "DejaVu Sans Mono"
CJKmainfont: "Noto Serif CJK SC"
header-includes:
  - |
    \usepackage{booktabs}
    \usepackage{longtable}
    \usepackage{array}
    \usepackage{enumitem}
    \usepackage{microtype}
    \setlist{nosep,leftmargin=*}
---

# 0. 文档身份、版本与适用范围

本文档是 `post-retrieval-reasoning` 项目的**正式实验科学合同（scientific contract）v1.0**。它的作用不是把未来十天甚至整个项目的探索路径写死，而是冻结：研究问题、主要假设、模型与数据范围、主要实验条件、主要指标、统计方法、硬控制、因果证据门槛、结果分级、分支触发规则、复现要求和停止条件。探究性机制扩展可以迭代，但必须由本协议中预先规定的结果触发，并通过版本化 addendum 进入后续确认性实验。

本文档基于以下项目状态与讨论共识：

- 仓库：`jiale-li-orion/post-retrieval-reasoning`，阅读快照以提交 `1b3aa136afd35373a8c02699add37c5071041974` 为基准。
- 论文现状：Introduction、Artifact Access Semantics（AAS）与 Post-Recall Evidence Evaluation 三节已写；实验、分析与相关工作尚待结果驱动完成。
- 已有实验：`atm_oracle_evidence` 已完成 MiMo V2.5 在 ATM-Bench-Hard 上的 SGM Oracle vs Raw Oracle pilot；该结果用于动机与误差分析，不作为最终主结果。
- 已有候选干预：`atm_oracle_evidence_verbal-R3` 已具备协议、配置、脚本、测试与 run provenance 基础；在新协议中降级为一个外部干预家族，而不再独占论文主线。
- J-space 研究共识：J-lens/J-space 被视为一种观察和干预模型内部**可言说、future-output-sensitive、可能被下游灵活复用的公共接口表示**的方法。它不是完整思维空间，也不能用单个 top-k token 读数替代 binding、routing、consumption 或完整因果机制。

## 0.1 本协议与当前 `PROTOCOL.md` 的关系

当前根目录 `PROTOCOL.md`（2026-07-05）冻结的是 ATM-Bench Oracle/NIAH 条件下的 Verbal Annotation 对照实验。新协议扩大为统一的 post-retrieval failure program，覆盖：

1. 行为级受控证据失败图谱；
2. 内部 J-lens/J-space 决策状态追踪；
3. 外部 evidence intervention 到内部 state change 的桥接；
4. ablation / swap / steering / state patching 因果干预；
5. 多模型、题型、证据负载与模态验证；
6. 根据真实结果触发 binding-aware、phase-conditioned、query-conditioned 或 evidence-conditioned 扩展。

因此，新协议在正式主实验中**取代旧协议作为最高层实验合同**。旧协议和已有代码保留为可复用子模块与 provenance 记录。

## 0.2 三种状态：Frozen / Adaptive / Deferred

| 状态 | 含义 | 例子 |
|---|---|---|
| **Frozen：现在冻结** | 不因结果漂亮与否改变；改变必须升协议大版本并解释原因 | RQ、模型集合、ATM split、主要条件、主要指标、统计方法、硬控制、case selection rule |
| **Adaptive：预定义搜索空间** | 可以根据结果触发，但触发条件现在冻结 | binding-aware probe、phase-conditioned lens、evidence-conditioned lens、repair router |
| **Deferred：由结果决定** | 现在不命名、不承诺、不预设 positive claim | 最终新方法名称、最 dominant failure、是否形成 unified internal sufficiency theory、最终标题 |

本项目遵守：

$$
\boxed{
\text{freeze invariants}
+\text{predefine branching rules}
+\text{iterate mechanisms}
+\text{confirm at the end}
}
$$

# 1. 研究定位：保持 memory / post-retrieval 主线，J-space 作为内部机制工具

项目原始问题是：当长期记忆系统已经找到了相关 evidence，甚至 oracle 直接给出 ground-truth evidence 时，模型为什么仍然失败？仓库已有理论将外部生命周期写为：

$$
\text{compression}
\rightarrow
\text{artifact}
\rightarrow
\text{usage semantics}
\rightarrow
\text{access}
\rightarrow
\text{decision-facing view}
\rightarrow
\text{decision}.
$$

现有论文进一步提出：

$$
\mathsf{Success}
=
\mathsf{AccessOK}
\land
\mathsf{ViewOK}
\land
\mathsf{EvalOK}.
$$

J-space 进入后，本项目不改造成纯 reasoning 或 consciousness 工作，而是打开 `EvalOK` 内部的黑箱。新的统一生命周期是：

$$
\boxed{
\begin{aligned}
\text{artifact}
&\rightarrow \text{access}
\rightarrow \text{decision-facing view}
\rightarrow \text{representation formation}\\
&\rightarrow \text{workspace/public-interface entry}
\rightarrow \text{binding}
\rightarrow \text{composition/operator execution}\\
&\rightarrow \text{downstream consumption}
\rightarrow \text{answer realization}.
\end{aligned}}
$$

更细化地：

$$
\boxed{
\mathsf{Success}
=
\mathsf{AccessOK}
\land
\mathsf{ViewOK}
\land
\mathsf{StateOK}
\land
\mathsf{BindOK}
\land
\mathsf{ComposeOK}
\land
\mathsf{UseOK}
\land
\mathsf{RealizeOK}
}
$$

其中 `StateOK` 不等价于“某个 token 在 J-lens top-k 中出现”。J-lens 是一个操作化测量工具；完整机制判断还需要 logit-lens 对照、位置与阶段控制、因果干预以及 binding/consumption 证据。

# 2. 核心研究问题与主要假设

## 2.1 研究问题

**RQ1 - Behavioral localization（行为级定位）**  
在 ground-truth evidence 已经可用时，post-retrieval failure 在什么外部条件下出现？view 表示、distractor load、模态、题型与 answerer 如何改变失败？

**RQ2 - Internal decision-state tracing（内部决策状态追踪）**  
成功与失败时，decision-critical entity、attribute、operand、operator、intermediate、answer 在模型 residual dynamics 中如何形成、进入 J-readable 公共接口、竞争、持续和传播？

**RQ3 - External-to-internal bridge（外部到内部桥接）**  
当 Raw、Verbal Annotation 或较低 distractor load 修复行为时，是否伴随可预测的内部状态修复，例如更高 gold margin、更早 emergence、更强 persistence、更低 distractor intrusion 或更清晰的 binding/consumption？

**RQ4 - Causal repair（因果修复）**  
对诊断出的 failure stage 进行针对性 ablation、swap、steering 或 successful-state patching，能否以 layer/position/content-specific 的方式改变或修复行为？

**RQ5 - Generalization（跨模型泛化）**  
这些 failure signature 与 repair relationship 是否跨模型家族、规模、题型、evidence condition 和 multimodal/text-only setting 稳定存在？

## 2.2 主要假设

**H1 - View sufficiency hypothesis**  
在 AccessOK 固定时，Raw 或更充分的 evidence view 会修复一部分 SGM failure；修复集中于 SGM 遗失 decision-critical field / relation / modality-specific detail 的题目。

**H2 - Decision-state hypothesis**  
即使 evidence 已存在，成功与失败仍可由内部 decision-critical representation 的 formation、J-readable accessibility、margin、persistence 或 competition 差异区分。

**H3 - Load/competition hypothesis**  
随着 NIAH evidence load 增长，失败不仅表现为 output accuracy 下降，还表现为 gold margin 下降、distractor intrusion 增加、workspace entropy 上升、late emergence 或 persistence 缩短。

**H4 - External repair correspondence hypothesis**  
SGM→Raw、SGM→VA、low-k→high-k 的行为 transition 与特定内部 state transition 对应；不同 intervention 修复不同 failure stage。

**H5 - Causal specificity hypothesis**  
content-specific、layer-specific、position-specific 的 internal intervention 比 matched random / wrong concept / wrong layer control 更稳定地改变相应行为。

**H6 - Heterogeneous mechanism hypothesis**  
post-retrieval failure 不是单一瓶颈。`number`、`list_recall`、`open_end` 会表现出不同的 formation / binding / composition / consumption profile；不同模型也可能具有不同 failure mixture。

# 3. 模型范围与资源角色

## 3.1 开源权重机制模型：所有适用文本实验全跑

以下五个模型构成 primary mechanistic suite：

1. `Qwen3-8B-ms`；
2. `DeepSeek-R1-Distill-Llama-8B`；
3. `Qwen2.5-7B-Instruct`；
4. `Qwen3-VL-2B-Instruct`；
5. `Qwen3-VL-8B-Instruct`。

原则：**五个模型运行所有适用的文本证据实验、J-lens/J-space readout、logit-lens baseline、failure analysis 与 causal intervention。** Raw multimodal condition 仅对真正能直接消费图片/视频的模型运行；其余模型不以“缺失格”解释为失败。

正式 run 前必须在 `model_registry.yaml` 冻结：

- Hugging Face repository / exact provider identifier；
- exact revision / commit；
- tokenizer revision；
- architecture name；
- layer count、hidden size、vocab size；
- dtype；
- attention backend；
- chat template；
- generation config；
- whether reasoning/thinking is enabled；
- quantization status。

五个模型的本地 snapshot 或 Hugging Face revision 及文件 manifest hash 均须在第一次正式 run 前冻结；当前权威值记录在 `experiments/post_retrieval_jspace_v1/registry/model_registry.yaml`。

## 3.2 API 行为模型

Primary behavioral generalization pool：

- MiMo V2.5；
- MiniMax M3；
- Kimi K2.5；

API 模型承担：

- Oracle-SGM / SGM+VA 行为大表；
- ATM-Hard NIAH stress test；
- Raw multimodal 条件（provider 支持时）；
- 强模型 reference；
- 必要的 judge / adjudication。

API 模型不承担 J-space 内部机制结论，因为 hidden states / gradients / activation interventions 不可得。

## 3.3 精度与量化政策

Primary mechanistic results：

$$
\boxed{\text{BF16 full-weight first; no 4-bit primary mechanism claims}}
$$

理由：J-lens 与因果干预依赖局部几何、Jacobian、activation direction 与 logprob change。4-bit 量化可能改变这些量。

- 2B 模型：8GB RTX 5050 可承担开发、小批 readout、部分全量 inference；
- 7B/8B：24GB RTX 4090 为主；batch=1，按层/位置分块，activation 及时 CPU offload；
- Raw multimodal 8B gradient/Jacobian 若超过 24GB，则使用 AutoDL 更大显存卡；
- 量化仅用于非主要 smoke/debug 或纯行为探索，并明确标记。

# 4. 数据、split 与冻结版本

## 4.1 ATM-Bench 为主 benchmark

Primary benchmark 是 ATM-Bench。沿用仓库当前协议中已冻结的数据：

| Split | 题数 | qtype 分布 | 主要角色 |
|---|---:|---|---|
| Full | 1013 | open_end 514；number 360；list_recall 139 | 主行为统计、基础内部 readout、多模型表 |
| Hard | 31 | open_end 13；number 6；list_recall 12 | 深度 trajectory、paired transitions、NIAH、Raw、causal analysis |

冻结数据 hash：

- Full：`ab6eaa9df62fb4162e0f5eecd98768a7e3ae721e32d2db2cf227ff41e3295762`
- Hard：`acd35f2a172a9741d970d2cf21184ff0af8d79a8bf59967fc8aa33d619f6af4a`

冻结外部代码版本延续当前 repo 记录：

- ATM-Bench commit：`3a1a606b872c4502e5efc632dcd1c076a220ed4a`
- Verbal-R3 commit：`62c88a67c13d05cafbc5b7dbbd9ebe436d1d4e92`

若未来不得不升级 external repo，必须形成 protocol addendum，并保留旧 commit 可复现结果。

## 4.2 ATM evidence representations

Primary textual evidence representation：Schema-Guided Memory（SGM，模式引导记忆表示）：

```text
type,timestamp,location,short_caption,caption,ocr,tags
```

Raw condition：原始图片 / 视频 / email。用于 multimodal view sufficiency 与 paired repair。

NIAH：复用 ATM-Bench 固定 evidence pools，不重新采样 distractors。默认：

$$
k\in\{25,50,100,200\}.
$$

## 4.3 STALE 的定位

当前 paper skeleton 包含 `Cumulative State Validity [pending]`。v1.0 不把 STALE 写成核心 claim 的必备条件，也不删除它。

**冻结 inclusion gate：** 只有当 ATM 主实验已完成 E1-E4 baseline，且 STALE 能复用同一 `decision-facing view → internal decision state → behavior` 分析框架、不需要另起一套方法时，才通过 `protocol_v1.1_stale.md` 纳入 secondary external-validity track。未触发时，主论文可以取消该 section 或移入 future work，不影响主协议有效性。

# 5. 证据条件与主实验矩阵

## 5.1 条件定义

统一 condition IDs：

- `C0 = ORACLE_SGM`
- `C1 = ORACLE_SGM_VA`
- `C2 = ORACLE_RAW`
- `C3 = NIAH25_SGM`
- `C4 = NIAH50_SGM`
- `C5 = NIAH100_SGM`
- `C6 = NIAH200_SGM`
- `C7 = NIAH25_SGM_VA`
- `C8 = NIAH50_SGM_VA`
- `C9 = NIAH100_SGM_VA`
- `C10 = NIAH200_SGM_VA`

`VA` 是 query-conditioned Verbal Annotation。它保留原始 SGM item、evidence IDs 与顺序，只附加 verbal comment 与 relevance score；score 不筛选、不删除、不重排 evidence。

## 5.2 旧 protocol 的关键修正：primary paired claims 必须自己重跑 baseline

旧 `PROTOCOL.md` 允许直接复用官方 aggregate SGM baseline。新 integrated protocol 做如下修正：

> 任何逐题 transition、内部 state comparison、J-space bridge、causal mediation-like analysis 都必须拥有本项目在**同一模型版本、同一 prompt、同一 generation config、同一 evidence pool**下生成的逐题 baseline 输出。

因此：

- 官方 leaderboard / paper aggregate 只作 contextual reference；
- primary paired analysis 不得用 aggregate baseline 替代逐题 rerun；
- 所有五个开源机制模型的 C0 与相关对照必须自己重跑；
- API 模型若只保留 aggregate baseline，则只能报告绝对结果，不能做 paired transition 或 internal correspondence claim。

## 5.3 E0：已有 pilot，仅作动机

现有 MiMo V2.5 / ATM-Bench-Hard：

| 指标 | SGM Oracle | Raw Oracle | Delta |
|---|---:|---:|---:|
| EM | 19.35 | 38.71 | +19.36 |
| ATM/QS | 40.85 | 64.56 | +23.71 |
| list_recall | 72.2 | 91.8 | +19.6 |
| number | 16.7 | 16.7 | 0 |
| open_end | 23.1 | 61.5 | +38.4 |

该 pilot 支持两种存在性现象：一部分错误来自 view insufficiency，一部分 residual errors 在更丰富 Raw view 下仍存在。由于模型、judge 与 run 条件不构成最终全矩阵，它不作为 primary confirmatory result。

## 5.4 E1：Behavioral Oracle Failure Landscape

### Full split 主表

所有五个 open-weight models + API behavioral pool：

- C0 Oracle-SGM；
- C1 Oracle-SGM+VA。

若某 API / VL 模型可稳定跑 Raw，Full Raw 为 optional expanded result；不作为 v1.0 最低要求。

### Hard split 深度行为表

所有模型运行：

- C0, C1；
- C3-C10（NIAH 25/50/100/200，SGM 与 SGM+VA）。

Raw：

- Qwen3-VL-2B-Instruct；
- Qwen3-VL-8B-Instruct；
- 支持 Raw 的 API multimodal models。

Raw NIAH 不作为 primary requirement，因为 payload/context/server image-count limits 会混入 serving failure。

### E1 输出

- overall ATM/QS；
- number EM；
- list_recall Jaccard、precision、recall；
- open_end primary judge score；
- paired repair rate；
- paired degradation rate；
- stable-success / stable-failure / repair / degradation transition matrix；
- token/cost/latency。

# 6. J-lens / J-space 机制协议

## 6.1 术语硬约束

本论文必须严格区分：

1. **J-lens readout**：平均 Jacobian transport 后的 token readout；
2. **J-readable concept**：某概念在预先定义的位置、层、tokenization protocol 下可被 J-lens 稳定读出；
3. **J-space component**：显式计算 sparse nonnegative reconstruction / J-space decomposition 后得到的 component；
4. **workspace-like mechanism claim**：需要 readout + selective behavior + causal intervention + controls。

不得因为某 token 在 J-lens top-k 中出现，就直接写“该概念进入 J-space”。正文默认使用更谨慎的 `J-readable state`，只有在真正计算 J-space decomposition 或引用原论文定义时使用 `J-space component`。

## 6.2 全局 J-lens baseline

对每个开源模型、每个 residual layer $\ell$，拟合平均 Jacobian：

$$
J_\ell
=
\mathbb E_{x,t,t'\ge t}
\left[
\frac{\partial h_{L,t'}}{\partial h_{\ell,t}}
\right].
$$

读出：

$$
s^J_{\ell,p,y}
=
w_y^\top J_\ell h_{\ell,p},
$$

其中 $w_y$ 是 unembedding row。

同位置、同层必须计算 plain logit lens：

$$
s^{\mathrm{logit}}_{\ell,p,y}
=
w_y^\top h_{\ell,p}.
$$

### Calibration corpus

Primary global lens 使用独立于 ATM 的公共文本校准集，默认：

- WikiText-103 raw train；
- model-specific tokenizer；
- 256-token windows；
- deterministic shuffle seed = 17；
- 排除前 16 个 sink positions；
- 遵循官方 future-position accumulation 语义。

### Calibration sample size stability gate

先拟合 256 sequences 与 512 sequences 的 lens subset。若在所有层中：

- matrix / transported-direction cosine median ≥ 0.98；
- fixed evaluation prompts top-25 overlap median ≥ 0.90；

则 final fit 可使用 256；否则使用 512。该 gate 由数值稳定性决定，不根据 ATM accuracy 或 J-space positive result 决定。

### Layer coverage

最终 primary readout 使用所有 transformer blocks。跨模型比较使用 normalized depth：

$$
\tilde \ell=\frac{\ell}{L-1}.
$$

仅开发阶段允许 coarse layer grid；最终结果不得按结果挑“最好看的 layer”。

## 6.3 Qwen3-VL 的 multimodal 处理

对 Qwen3-VL：

- J-lens 定义在 language backbone residual stream；
- global lens 以 text-only calibration 拟合；
- SGM 与 Raw inference 使用同一 lens，以测试不同 external view 是否导致不同 internal state；
- Raw evidence 的 vision encoder / projector 只作为上游 input pathway，不改变 `J_ell` 的定义；
- 若 Raw multimodal activation / gradient 超过 24GB，迁移到更大显存 GPU，不使用 4-bit 替代 primary mechanism run。

## 6.4 Full 与 Hard 的 target 构造

### Full 1013：自动 target manifest

每道题自动生成 `target_manifest.json`，只从 benchmark metadata / gold answer / ground-truth evidence IDs 派生，至少包括：

- qtype；
- gold answer string；
- gold evidence IDs；
- answer constituent tokens；
- numeric values；
- date/time values；
- named entities 可自动抽取时记录；
- whether target is literally exposed in evidence；
- tokenizer aliases；
- single-token / multi-token flag。

Full split primary mechanistic statistics只对**预先可自动定义且可复现的 target**报告，避免按模型内部结果人工挑 concept。

### Hard 31：human-reviewed decision programs

对 31 道 Hard 题全部建立 `decision_program.json`，由规则/LLM 草拟，人工逐题审核。字段：

```json
{
  "qa_id": "...",
  "qtype": "number|list_recall|open_end",
  "required_evidence_ids": ["..."],
  "entities": ["..."],
  "attributes": ["..."],
  "operands": ["..."],
  "operators": ["sum|count|latest|override|join|..."],
  "intermediates": ["..."],
  "final_answer": "...",
  "bindings": [["entity", "relation", "value"]],
  "copyable_targets": ["..."],
  "derived_targets": ["..."]
}
```

Hard 31 的 decision programs 必须在查看 J-lens trajectories 和 causal results 之前冻结版本。

## 6.5 读取位置

Primary silent positions：

1. `P_evidence_end_i`：每个 evidence item 最后一个内容 token；
2. `P_q`：question 结束、answer generation 之前；
3. `P_a0`：answer 起始边界，第一个生成 answer token 之前。

Secondary positions：

- explicit reasoning / thinking step end；
- generated positions，仅用于 trajectory，不作为 silent-state 主要证据。

任何强 workspace claim 必须保证主要证据出现在目标概念被自然语言写出之前。

## 6.6 Copyable 与 derived target 分层

ATM evidence 中很多 gold entity / ID / number 直接出现在 prompt。为避免把 prompt copyability 当 reasoning：

- `copyable target`：目标字符串或其规范化等价形式已经出现在 evidence；
- `derived target`：必须通过 aggregation、count、date difference、latest/override、join 或跨证据组合得到。

Primary reasoning mechanism claim 优先基于 derived targets。list_recall 的机制解释聚焦 selection、competition、coverage，而不声称 evidence ID 的出现本身证明 reasoning。

## 6.7 Tokenizer 与 multi-token 规则

J-lens 的 single-token limitation 是协议硬边界：

- single-token target：进入 primary rank/margin analysis；
- multi-token target：进入 secondary token-set coverage / phrase extension；
- 不得把 multi-token phrase 未命中解释为 representation absent；
- 必须记录每个模型的 tokenizer mapping；
- word-start token、alias、大小写与前导空格规则冻结在 `tokenization_spec.md`。

# 7. 内部主指标

给定层 $\ell$、位置 $p$、概念 $c$，记 J-lens score 为 $s_{\ell,p,c}$。

## 7.1 Rank 与 top-k recovery

$$
\operatorname{rank}_{\ell,p}(c)
=
\text{concept }c\text{ 在读出中的排名}.
$$

报告：top-1 / top-5 / top-10 / top-25 hit rate，MRR。

## 7.2 Gold-decoy margin

$$
\operatorname{margin}_{\ell,p}(c,d)
=
s_{\ell,p,c}-s_{\ell,p,d}.
$$

Decoys 必须来自预先定义的同类集合，例如：

- wrong evidence entity；
- same-category entity；
- wrong numeric operand；
- prior/world-knowledge alternative；
- wrong operator。

## 7.3 First emergence

$$
\ell^*(c)
=
\min\{\ell:\operatorname{rank}_{\ell,p}(c)\le k\}.
$$

跨模型报告 normalized depth $\tilde\ell^*$。

## 7.4 Persistence

$$
\operatorname{Persistence}(c)
=
\frac{1}{|B|}
\sum_{\ell\in B}
\mathbf 1[\operatorname{rank}_{\ell,p}(c)\le k].
$$

## 7.5 Workspace/readout entropy

对预定义 candidate distribution $q_{\ell,p,c}$：

$$
H_{\ell,p}
=-\sum_c q_{\ell,p,c}\log q_{\ell,p,c}.
$$

必须说明 candidate set 与 normalization，不能混用 full-vocab entropy 与 target-subset entropy。

## 7.6 J-lens over logit-lens advantage

$$
\mathrm{JLA}(c)
=
\operatorname{rank}^{\mathrm{logit}}(c)
-
\operatorname{rank}^{J}(c),
$$

或以 margin difference 报告：

$$
\Delta m
=
m^J-m^{\mathrm{logit}}.
$$

如果 J-lens 在 silent middle layers 没有系统优于 logit lens，workspace claim 必须降级。

## 7.7 Condition delta

对同一道题、同一模型、两个条件 $a,b$：

$$
\Delta s=s_b-s_a,
\quad
\Delta \mathrm{rank}=\mathrm{rank}_b-\mathrm{rank}_a,
\quad
\Delta \mathrm{Persistence}=P_b-P_a.
$$

用于 SGM→Raw、SGM→VA、low-k→high-k paired bridge。

## 7.8 三维 trajectory tensor

完整分析对象：

$$
S\in\mathbb R^{L\times P\times C},
\qquad
S_{\ell,p,c}=s_{\ell,p,c}.
$$

Transformer 可并行形成多个中间态，因此逻辑依赖顺序不要求严格一层一层串行出现。

# 8. 失败分类：论文主分类与内部子分类

## 8.1 五阶段 primary taxonomy

为适应 AAAI 7 页叙事，正文 primary taxonomy 冻结为五类：

| ID | Stage | 诊断问题 | 主要证据 |
|---|---|---|---|
| F1 | Formation / Entry | 正确 decision-critical state 是否形成并进入可读公共接口？ | rank、margin、emergence、persistence |
| F2 | Binding / Competition | entity/value/operator 是否正确绑定；distractor 是否侵入？ | contrastive target、swap、competition metrics |
| F3 | Composition / Operator | operands 在，但 derived result 没形成？ | operand→intermediate→answer trajectory |
| F4 | Consumption | gold state 已形成，但后续行为未使用？ | ablation weak / patch strong / present-but-unused |
| F5 | Realization / Output | 内部状态和 answer logprob 是否正确，但表面输出/format 失败？ | output constraint、format errors、verifier |

外部 view insufficiency 单独记为 `V0`，位于 F1 之前。

## 8.2 A-J secondary taxonomy

内部报告保留更细的十类：

- A gold intermediate absent；
- B wrong/decoy entry；
- C late emergence；
- D low margin/crowding；
- E non-J / inaccessible format；
- F binding failure；
- G present-but-unused；
- H externalization dependence；
- I phase mismatch；
- J horizon mismatch。

A-J 不是互斥标签；primary F1-F5 用于正文聚合，A-J 用于分析与附录。

## 8.3 五种“读不出”

任何 negative result 都必须区分：

1. rank unreadable；
2. margin unreadable；
3. statistically unreadable；
4. causally unreadable；
5. format unreadable。

“J-lens 没命中”不能单独证明模型内部不存在相关 representation。

# 9. E2：Internal Decision-State Tracing

## 9.1 Full 1013 基础 readout

五个 open-weight models，在 C0 Oracle-SGM 上：

- behavior output；
- all-layer J-lens；
- all-layer logit lens；
- P_q / P_a0；
- automatic target manifest；
- correctness-conditioned aggregate；
- qtype stratification。

Primary questions：

- success vs failure 的 gold rank/margin 是否不同？
- derived targets 是否在正确答案前更早、更稳定出现？
- internal metrics 是否提供超越 output confidence 的 predictive information？
- J-lens 是否在 middle silent layers 优于 logit lens？

## 9.2 Hard 31 深度 trajectory

五个 open-weight models：

- C0/C1/C3-C10 全部做 deep tracing；
- Qwen3-VL-2B/8B 增加 C2 Raw deep tracing；
- 使用 human-reviewed decision programs；
- 保存 $L\times P\times C$ tensor；
- 给每个 question-model-condition pair 标 primary F1-F5 与 secondary A-J diagnosis。

# 10. E3：External-to-Internal Bridge

预先冻结四类 paired transition strata：

1. `SGM wrong → Raw correct`；
2. `SGM wrong → VA correct`；
3. `Oracle correct → NIAH fail`；
4. `low-k correct → higher-k fail`。

还保留两类 control strata：

5. stable success；
6. stable failure。

对每个 stratum 比较：

- gold rank/margin；
- decoy intrusion；
- first emergence；
- persistence；
- entropy；
- J-vs-logit advantage；
- operator/intermediate formation；
- output confidence。

**禁止**把这些分析表述为严格统计 causal mediation，除非未来另行设计 mediator assumptions。正文使用 `external-to-internal correspondence/bridge`。

# 11. E4：Causal Intervention and Repair

## 11.1 Case selection：不 cherry-pick

Hard 31 中所有满足预定义 transition strata 的 cases 都进入 causal candidate pool。

若某 stratum 过大：按 qa_id deterministic sort 后使用全部或预先冻结 cap；不得按内部 trajectory 是否漂亮挑选。

额外加入等量：

- stable-success controls；
- stable-failure controls。

## 11.2 Projection ablation

对 direction $v$：

$$
h'
=
h-
\alpha
\frac{\langle h,v\rangle}{\|v\|^2}v.
$$

Primary outcomes：

- correct-answer logprob delta；
- behavior change；
- fluency/perplexity side effect；
- content specificity。

## 11.3 Coordinate swap

$$
V=[v_s\;v_t],
\quad c=V^\dagger h,
\quad
h'=h+V(\sigma(c)-c).
$$

优先使用：

- gold ↔ same-category decoy；
- correct operand ↔ wrong operand；
- context-correct ↔ prior alternative；
- entity/value binding swap（仅在可定义时）。

## 11.4 Steering repair

$$
h'=h+\alpha\hat v_{\mathrm{gold}}.
$$

对失败样本做预定义 $\alpha$ sweep，报告 dose-response。最强证据是：对应 failure class 在正确 layer/position 被最小干预系统修复，而 wrong layer / wrong concept / random direction 不产生同样效果。

## 11.5 Successful-state patching

对同 question、同 model、不同 condition：

$$
h^{\mathrm{success}}_{\ell,P}
\rightarrow
h^{\mathrm{failure}}_{\ell,P}.
$$

重点：

- Raw-success → SGM-failure；
- VA-success → SGM-failure；
- low-k success → high-k failure。

因为 prefix length 不同，patch 按语义边界位置对齐，优先 `P_q` / `P_a0`，不按 absolute token index 生硬对齐。

## 11.6 因果 control family

每个 primary causal experiment 至少包含：

- matched-norm random direction；
- same-category wrong concept；
- wrong layer；
- wrong position；
- wrong phase（若 applicable）；
- same-condition sham patch；
- unrelated-question success-state patch；
- dose-response；
- reversibility where feasible。

单次 greedy continuation 可能对小 perturbation 混沌敏感，因此 primary causal outcome 同时报告 logprob-level effect；行为采样作为 secondary robustness。

# 12. Binding、operator 与 consumption：严格边界

## 12.1 Token bag 不等于 binding

`Alice`、`Paris`、`Bob`、`London` 同时可读，不证明 `Alice→Paris` 与 `Bob→London` 绑定正确。

因此 primary vanilla J-lens 只测 concept availability / accessibility。Binding claim 需要至少一种额外证据：

- contrastive relation score；
- entity-value swap；
- activation patching；
- relation-specific gradient/readout；
- controlled binding counterfactual。

## 12.2 ATM 中的 operator families

Hard decision programs 至少尝试标注：

- lookup；
- count；
- sum；
- date difference；
- latest；
- override；
- join / cross-evidence composition；
- conflict resolution；
- missingness / abstention。

对 `number` 题，必须区分：

1. operands 不可得；
2. operands 可读但 binding 错；
3. operands 与 operator 可得但 result 不形成；
4. result 可读但未被 consumed；
5. output formatting 失败。

# 13. Verbal Annotation 的最终角色

VA 被定义为：

$$
\boxed{\text{query-conditioned external semantic highlighting intervention}}
$$

冻结规则：

- evidence IDs 不变；
- evidence order 不变；
- 原 SGM 文本不改写；
- 只附加 comment + score；
- score 不筛选、不删除、不重排；
- annotation cache 与 answerer 解耦，同一 question-evidence pair 的 annotation 复用于所有 answerer；
- annotation model / checkpoint / prompt / seed / decoding 记录 provenance。

主要科学问题从“VA 提分多少”升级为：

> VA 修复了 formation、workspace entry、competition、binding、composition 还是 downstream consumption？

# 14. Adaptive method extensions：只按结果触发

## 14.1 Binding-aware extension gate

触发条件：

- gold entity/value individually J-readable；
- concept-set coverage 高；
- 但 answer 仍系统错误，且错误符合 cross-binding；
- vanilla J-lens 无法区分正确/错误 relation。

触发后创建 `protocol_v1.1_binding.md`。

## 14.2 Phase-conditioned lens gate

触发条件：

- thinking/reasoning model 在不同 phase 的同一 gold concept rank/margin 差异稳定；
- global lens 对 phase-specific success/failure 解释不足；
- phase label 可无歧义定义。

定义候选：

$$
J_\ell^{\mathrm{think}}
\neq
J_\ell^{\mathrm{answer}}.
$$

## 14.3 Query-conditioned lens gate

触发条件：同一 evidence 内容在不同 query demand 下需要不同 internal transport，global J-lens 对这种差异系统失真。

## 14.4 Evidence-conditioned lens gate

触发条件：外部 view intervention 显著改变行为，但 global J-lens readout 不能解释；且变化与特定 evidence role / modality 相关。

## 14.5 Strong negative gate：降级 J-space claim

若同时出现：

- signal 仅在 late/motor layers；
- plain logit lens 同样好或更好；
- silent position 无信号；
- 目标词写出后才出现；
- content-specific intervention 不改变行为；
- random/wrong controls 同样大；
- success/failure trajectory 无系统差异；

则停止 workspace-mechanism 强解释，转为：

- J-lens readout limitation；
- representation-format mismatch；
- general failure analysis；
- non-J-space computation。

负结果本身进入论文，不为追求 positive story 改指标。

# 15. 统计协议

## 15.1 Primary unit

- 行为：`question × model × condition`；
- paired comparison：同一 `question × model`；
- cross-model pooled analysis 必须按 question cluster 处理，避免把同一道题在多个模型上当完全独立样本。

## 15.2 行为统计

- paired binary correctness：McNemar exact test；
- continuous / partial score：paired bootstrap，10,000 resamples；
- 95% confidence interval；
- report absolute delta + relative delta + transition counts。

## 15.3 内部连续指标

Primary：paired bootstrap 95% CI。Secondary：permutation test / rank-biserial effect。

不得只报告 p-value；必须报告 effect size 与 sample count。

## 15.4 Multiple comparison

Primary families 预先定义：

1. model-wise behavior；
2. qtype-wise behavior；
3. internal primary metrics；
4. causal interventions。

Family 内默认 Holm-Bonferroni。Exploratory plots 不做 confirmatory significance claim。

## 15.5 Output confidence baseline

测试 J-space features 是否增加预测信息时，必须先有：

- output probability / logprob；
- entropy；
- answer length；
- qtype；

然后比较 adding J-space features 的增益。不得把“预测错误”直接解释为因果机制。

## 15.6 Judge policy

- number：Exact Match；
- list_recall：官方 normalized Jaccard；同时报告 precision/recall；
- open_end：官方 primary judge prompt + `gpt-5-mini`；
- Hard 31 全部使用 second judge 做 agreement check；
- Full open_end 至少固定随机 10% 做 secondary judge agreement；
- judge disagreement 记录，不静默覆盖。

# 16. 硬控制与证伪标准

Primary mechanistic claims最低满足：

1. J-lens vs logit-lens 同层同位置比较；
2. silent position；
3. prompt/answer matched controls；
4. copyable vs derived target stratification；
5. concept-type stratification；
6. tokenizer robustness；
7. phase/horizon alignment；
8. 至少一种 content-specific causal intervention；
9. matched random / wrong concept controls；
10. model-family robustness；
11. lens fit quality 与 calibration provenance；
12. 不做 consciousness overclaim。

证据阶梯：

$$
\text{readout}
<
\text{behavioral correlation}
<
\text{selective ablation}
<
\text{content swap}
<
\text{state patch}
<
\text{systematic repair}.
$$

论文必须明确每个结论停在哪一级。

# 17. Reproducibility 与 run contract

每个正式 run 必须不可覆盖，并至少保存：

```text
runs/<experiment>/<condition>/<split>/<model>/<run-id>/
├── manifest.json
├── config_snapshot.json
├── git_state.json
├── predictions.jsonl
├── target_manifest.jsonl        # 若 applicable
├── probe_metrics.parquet        # 若 applicable
├── trajectories/                # 若 applicable
├── interventions.jsonl          # 若 applicable
├── eval/
├── logs/
└── run_stats.json
```

`manifest.json` 至少记录：

- project git commit；
- dirty status / patch hash；
- ATM commit + data hashes；
- Verbal-R3 commit + checkpoint revision；
- model repo/revision/tokenizer；
- dtype/quantization/device；
- prompt hash；
- generation config；
- lens calibration config + lens artifact hash；
- seeds；
- Python / CUDA / PyTorch / transformers version；
- GPU model；
- start/finish timestamp；
- cost / token accounting。

输出已存在时必须失败，不自动覆盖。

# 18. 执行顺序与 protocol gates

## Gate A - Infrastructure accepted

通过条件：

- 统一 ATM loader；
- 五个 open-model adapters；
- API adapter；
- immutable runs；
- manifest 完整；
- 评测脚本与当前 ATM official logic 对齐；
- tests 全过。

## Gate B - Behavioral matrix complete

先跑 E1。此时只看真实 failure landscape，不改 primary metrics。

## Gate C - J-lens baseline validated

通过条件：

- fit reproducible；
- numerical sanity checks；
- J-lens/logit-lens 同位置输出；
- silent positions 正确；
- no generated-token leakage；
- calibration stability gate 通过。

## Gate D - First scientific review

我们共同检查：

- 哪些 hypotheses survive；
- 哪些 failure stages dominant；
- J-lens 是否优于简单 baseline；
- 是否存在 late-only artifact；
- 哪些 adaptive extension 被触发。

## Gate E - Causal / extension branches

只运行被预先定义 gate 触发的 extension；记录 addendum。

## Gate F - Confirmatory rerun

最终锁定：

- code commit；
- configs；
- lenses；
- target manifests；
- decision programs；
- intervention strengths；
- seeds。

重新生成论文主表与主图。

# 19. Primary、Secondary 与 Exploratory 结果分级

## Primary confirmatory

- E1 full behavioral table；
- E2 vanilla J-lens vs logit-lens；
- success/failure internal metric differences；
- NIAH load/competition trend；
- E4 causal necessity/sufficiency/repair；
- cross-model comparison。

## Secondary confirmatory

仅在预定义 gate 触发后：

- binding-aware；
- phase-conditioned；
- query-conditioned；
- evidence-conditioned；
- STALE secondary validation。

## Exploratory

- unexpected failure modes；
- qualitative trajectories；
- newly invented readouts；
- speculative repair router；
- prior-vs-context source identification。

Exploratory 结果可以进入 analysis / appendix，但不能伪装成预注册 primary claim。

# 20. AAAI 7 页论文映射

建议正文实验叙事保持高度压缩：

1. **Setup / Protocol**：models、ATM Full/Hard、conditions、J-lens + controls；
2. **Behavioral failure landscape**：主大表；
3. **Internal decision-state analysis**：一张跨模型表 + trajectory figure；
4. **External-to-internal bridge**：paired repair/degradation；
5. **Causal repair**：ablation/steering/patch；
6. **Analysis + Related Work + Limitations + Conclusion** 合并压缩。

正文主图建议：

- Figure 1：external evidence lifecycle → internal decision-state lifecycle；
- Table 1：multi-model behavioral matrix；
- Figure 2：success/failure trajectory + NIAH load effect；
- Table 2：cross-model internal metrics / failure mixture；
- Figure 3：causal repair/patch results。

详细 A-J taxonomy、全部 layer curves、decision programs、额外 model/condition tables 放附录。

# 21. 当前 review blockers

在交给 Codex 开始正式实现前，用户只需审核以下事项：

1. 是否接受本协议对旧 `PROTOCOL.md` 的 supersede 关系；
2. 是否接受 primary baseline 全部自己重跑，而不是只复用 leaderboard aggregate；
3. 是否接受 WikiText-103 + stability gate 作为 global J-lens calibration；
4. 是否接受 Full 1013 做基础 readout、Hard 31 全部做人审 decision programs；
5. 是否接受 STALE 作为 gated secondary track；
6. 是否接受本文的五阶段 primary failure taxonomy + A-J secondary taxonomy；
7. 是否接受 BF16 full-weight 作为 primary mechanism precision policy。

审核通过后，Codex 的工作对象不是“自由发挥实现”，而是下一份《Experiment Design and Execution Plan v1.0》中定义的 work packages、acceptance tests 与 run gates。

# 22. Source map

本协议直接吸收并对齐以下项目文件与已有研究资产：

- `README.md`
- `experiments/README.md`
- `my_paper/sections/01_introduction.tex`
- `my_paper/sections/02_problem.tex`
- `my_paper/sections/03_framework.tex`
- `my_paper/appendix.tex`
- `experiments/atm_oracle_evidence/README.md`
- `experiments/atm_oracle_evidence_verbal-R3/README.md`
- `PROTOCOL.md`
- `human-reading-doc/现状.md`
- `0710_j-space讨论/J-Space_README.md`
- `J-Space_终极研究笔记_2026-07-10.pdf`
- `jspace_atomic_notes.pdf`
- `jspace_atomic_notes_supplement.pdf`
- `J-Space_去伪实验方案_图片识别汇总版.pdf`

本文档刻意保留了现有 repo 的理论主线：access geometry vs evaluation algebra、decision-sufficient view、view-collapse impossibility、dynamic binding error、decision state 与 harnessed evaluation；J-space 被放入 post-access black box，成为 probe → trajectory diagnosis → causal validation → repair 的内部机制工具。
