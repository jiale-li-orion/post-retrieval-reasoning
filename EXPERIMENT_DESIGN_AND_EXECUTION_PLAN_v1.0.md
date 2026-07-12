---
title: "Post-Retrieval Reasoning Experiment Design and Execution Plan v1.0"
subtitle: "Repo-aware implementation plan for Codex, 4090/5050 local GPUs, cloud fallback and API models"
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

# 0. 文档目的

本文档把《Final Experimental Protocol v1.0》转化为可交给 Codex 的**工程与实验执行计划**。它不是让 Codex 自主决定研究问题，而是规定：哪些现有代码复用、哪些新模块实现、每个 work package 的输入输出、acceptance criteria、run order、hardware allocation、review gates、branch rules 和 final deliverables。

推荐工作流：

$$
\boxed{
\text{Protocol review}
\rightarrow
\text{Codex implementation}
\rightarrow
\text{behavior baseline}
\rightarrow
\text{J-lens baseline}
\rightarrow
\text{human scientific review}
\rightarrow
\text{triggered extensions}
\rightarrow
\text{confirmatory rerun}
}
$$

# 1. Repo 现状：复用、保留、升级

基于仓库快照 `1b3aa136afd35373a8c02699add37c5071041974`：

## 1.1 直接保留

- `my_paper/sections/01_introduction.tex`
- `my_paper/sections/02_problem.tex`
- `my_paper/sections/03_framework.tex`
- `my_paper/appendix.tex` 中现有两个 formal proofs
- `experiments/atm_oracle_evidence/` 作为 E0 pilot 与 failure-case 资产
- `experiments/atm_oracle_evidence_verbal-R3/` 的 annotation pipeline、配置管理、manifest、测试风格
- 根目录统一 `.venv` 规则
- external repo path 约定
- immutable run directory 原则

## 1.2 升级 / 重新定位

- 根 `PROTOCOL.md`：保留为历史协议；新主协议应放在新的 experiment line 下，并在 README 标记 superseded-by。
- Verbal-R3：从“候选主实验线”重新定位为 intervention family。
- `experiments/README.md`：增加新统一实验线，并把旧两条标记为 pilot / reusable module。
- `my_paper/sections/04_atm_diagnostics.tex`：等待 E1-E4 结果后写，不先写结果导向叙事。
- `my_paper/sections/05_stale_case.tex`：保留 gated secondary 状态。

# 2. 建议新实验目录

建议创建：

```text
experiments/post_retrieval_jspace_v1/
├── README.md
├── PROTOCOL.md
├── DECISION_RULES.md
├── CHANGELOG.md
├── configs/
│   ├── models.yaml
│   ├── datasets.yaml
│   ├── behavior.yaml
│   ├── jlens.yaml
│   ├── interventions.yaml
│   └── judges.yaml
├── registry/
│   ├── model_registry.yaml
│   ├── dataset_registry.yaml
│   └── condition_registry.yaml
├── manifests/
│   ├── target_manifests/
│   └── decision_programs/
├── adapters/
│   ├── atm.py
│   ├── model_base.py
│   ├── hf_causal.py
│   ├── qwen3_vl.py
│   └── api_chat.py
├── behavior/
│   ├── run_behavior.py
│   ├── build_conditions.py
│   └── evaluate.py
├── jlens/
│   ├── fit.py
│   ├── apply.py
│   ├── logit_lens.py
│   ├── storage.py
│   └── validate.py
├── probes/
│   ├── targets.py
│   ├── positions.py
│   ├── trajectory.py
│   ├── metrics.py
│   └── taxonomy.py
├── interventions/
│   ├── ablation.py
│   ├── swap.py
│   ├── steering.py
│   └── state_patching.py
├── analysis/
│   ├── behavior_tables.py
│   ├── internal_tables.py
│   ├── paired_bridge.py
│   ├── causal_analysis.py
│   └── statistics.py
├── scripts/
│   ├── run_e1_behavior.sh
│   ├── run_e2_jlens.sh
│   ├── run_e3_bridge.sh
│   ├── run_e4_causal.sh
│   └── finalize_confirmatory.sh
├── tests/
│   ├── test_atm_adapter.py
│   ├── test_conditions.py
│   ├── test_no_leakage.py
│   ├── test_tokenization.py
│   ├── test_jlens_shapes.py
│   ├── test_logit_baseline.py
│   ├── test_interventions.py
│   └── test_manifest_contract.py
├── runs/
└── reports/
```

不建议把新代码直接塞进旧 `atm_oracle_evidence_verbal-R3`，因为新主线已经超出 VA。

# 3. Codex Work Packages

## WP0 - Freeze repository snapshot and provenance

### 任务

- 创建新实验目录；
- 将两份 protocol 文档放入目录；
- 记录 project commit / dirty diff；
- 读取现有 ATM/Verbal-R3 pins 与 data hashes；
- 建立 registry schema。

### Acceptance criteria

- `python -m ... --print-config` 可打印完整 resolved config；
- 每个 model / dataset / condition 有唯一 ID；
- 无隐式默认值散落在 Bash 和 Python；
- 所有正式 run 可回溯到 exact code/data/model revision。

## WP1 - Unified ATM adapter

### 任务

统一读取：

- Full 1013；
- Hard 31；
- ground-truth `evidence_ids`；
- NIAH pools；
- SGM image/video batch results；
- email evidence；
- Raw media path；
- qtype；
- gold answer。

### 输出对象

```python
@dataclass
class ATMItem:
    qa_id: str
    question: str
    qtype: str
    gold_answer: str
    evidence_ids: list[str]
    evidence_items: list[EvidenceItem]
    niah_pool_ids: list[str] | None
```

### Acceptance criteria

- Full/Hard counts 与 hash 对齐；
- 与 ATM official `collect_text_evidence()` 逐题一致；
- evidence order 不改变；
- NIAH pool 不重新采样；
- SGM chunk text hash 可验证。

## WP2 - Unified model adapters

### 模型

- Qwen3-8B-ms；
- DeepSeek-R1-Distill-Llama-8B；
- Qwen2.5-7B-Instruct；
- Qwen3-VL-2B-Instruct；
- Qwen3-VL-8B-Instruct；
- MiMo V2.5；
- MiniMax M3；
- Kimi K2.5；

### Adapter contract

```python
class ModelAdapter:
    def build_messages(...): ...
    def generate(...): ...
    def get_tokenizer(...): ...
    def forward_hidden(...): ...        # open-weight only
    def get_unembedding(...): ...       # open-weight only
    def get_residual_modules(...): ...  # open-weight only
```

### Acceptance criteria

- 同一 ATM prompt contract；
- provider unsupported params 显式记录；
- returned model id 保留；
- local models 支持 hidden-state hook 与 activation intervention；
- Qwen3-VL text-SGM 与 Raw 两种输入都能走统一 result schema。

## WP3 - Behavioral runner E1

### Condition builder

必须支持：C0-C10。

VA 直接复用现有 pipeline 逻辑，但重构为 model-independent cached intervention：

```text
question + evidence item
    -> annotation cache
    -> same annotation reused across answerers
```

### Primary run order

1. Hard C0 all models；
2. Hard C1 all models；
3. Hard NIAH C3-C10；
4. Qwen3-VL Raw C2；
5. Full C0 all models；
6. Full C1 all models；
7. API expanded runs。

### Acceptance criteria

- 每个 run immutable；
- predictions / eval / manifest / run_stats 齐全；
- same condition exact input hash 保存；
- paired baseline 可恢复；
- no published aggregate used as paired substitute。

## WP4 - Target manifest builder

### Full auto targets

从 ATM metadata 与 gold answers 生成：

- answer tokens；
- evidence IDs；
- numeric values；
- dates；
- named entities where deterministic；
- copyable/derived flag；
- tokenizer aliases per model。

### Hard decision programs

Codex 先生成草稿；人工审核后冻结 `decision_programs_v1.jsonl`。

### Acceptance criteria

- targets 在查看内部 trajectories 前冻结；
- source field 记录自动/人工；
- single/multi-token 明确；
- 每个 target 可追溯到 gold answer / evidence / human rationale。

## WP5 - J-lens fitter

### 要求

基于 Anthropic reference semantics 实现/移植：

- average Jacobian transport；
- future positions accumulation；
- skip first 16 sink positions；
- per-layer fit；
- checkpoint / merge；
- storage hash；
- calibration stability comparison 256 vs 512 sequences。

### 资源策略

- 每次只处理一个 layer / chunk；
- BF16 model weights；
- Jacobian artifact 可 fp32 保存；
- CPU offload；
- no full-vocab direction dictionary 全层常驻 GPU。

### Acceptance criteria

- shape tests；
- identity / toy-network numerical sanity；
- deterministic repeat on small batch；
- 256/512 stability report；
- exact calibration corpus indices preserved。

## WP6 - Readout and logit-lens baseline

### 输出

对指定 `layer × position × target`：

- J-lens score；
- logit-lens score；
- rank；
- top-k；
- margin；
- entropy；
- emergence；
- persistence。

### 强制 leakage test

- P_q/P_a0 必须位于生成前；
- generated positions 单独标记；
- target 已经显式出现在 evidence 时必须标 `copyable=true`。

### Acceptance criteria

- J/logit 同一 activation 输入；
- no answer tokens accidentally appended；
- layer normalization semantics 与模型 architecture 对齐；
- cross-model normalized depth 输出。

## WP7 - Full E2 readout

### Full 1013

五个 open models：C0，P_q/P_a0，全层。

输出：

- `probe_metrics.parquet`；
- success/failure aggregates；
- qtype tables；
- J vs logit comparison；
- output confidence baseline。

### Hard 31

五模型 C0/C1/C3-C10；Qwen3-VL 增加 Raw。

输出完整 trajectory tensors 与 heatmaps。

### Acceptance criteria

- all Hard items analyzed；
- no “best layer only” reporting；
- selected summary band 的选择规则在报告中可追溯。

## WP8 - Failure taxonomy engine

Codex 不自动决定科学真相，但可根据冻结规则生成 candidate labels：

```text
V0 view insufficiency
F1 formation/entry
F2 binding/competition
F3 composition/operator
F4 consumption
F5 realization/output
```

以及 A-J subtypes。

### 输出

- evidence supporting label；
- uncertainty；
- alternative diagnosis；
- human review field。

### Acceptance criteria

- label rule 版本化；
- 不允许只因为 gold rank > k 就自动判“模型不知道”；
- format unreadability / multi-token limitation 显式保留。

## WP9 - E3 paired bridge analysis

### Transition strata

- SGM wrong → Raw correct；
- SGM wrong → VA correct；
- Oracle correct → NIAH fail；
- low-k correct → high-k fail；
- stable success；
- stable failure。

### 输出

paired distributions：

- Δrank；
- Δmargin；
- Δemergence；
- Δpersistence；
- Δentropy；
- Δdecoy intrusion；
- Δoutput confidence。

### Acceptance criteria

- case inclusion 只由 behavior transition 决定；
- no cherry-picking by internal result；
- no causal mediation wording。

## WP10 - E4 interventions

### Ablation

- gold direction；
- wrong concept；
- random matched norm；
- wrong layer/position。

### Swap

- gold ↔ decoy；
- operand ↔ wrong operand；
- binding swap where valid。

### Steering

- fixed alpha grid；
- dose-response。

### State patching

- Raw success → SGM failure；
- VA success → SGM failure；
- low-k success → high-k failure。

### Acceptance criteria

- all interventions save pre/post activation norm；
- answer logprob before/after；
- generation output；
- control outcomes；
- reversible or dose-responsive when expected。

## WP11 - Statistics and paper-ready reports

生成：

- Table 1 behavioral matrix；
- Table 2 internal cross-model metrics；
- transition table；
- failure-mixture table；
- causal repair table；
- per-model appendix tables；
- bootstrap CI；
- McNemar；
- Holm correction；
- judge agreement。

禁止手工复制数字进 LaTeX。所有表应由 machine-readable run artifacts 自动生成。

## WP12 - Confirmatory freeze

在 exploratory review 后：

- freeze configs；
- freeze lens artifacts；
- freeze decision programs；
- freeze alpha grids；
- freeze branch addenda；
- new run IDs；
- confirmatory rerun。

# 4. 运行矩阵：最低要求与 expanded matrix

## 4.1 Primary open-model matrix

五个 open models：

| Experiment | Full | Hard | Conditions |
|---|---|---|---|
| Behavior | Yes | Yes | C0/C1；Hard additionally C3-C10 |
| Raw behavior | Qwen3-VL only optional Full | Qwen3-VL required | C2 |
| Basic J/readout | Yes | Yes | C0 |
| Deep trajectory | No | Yes | C0/C1/C3-C10；Qwen3-VL C2 |
| Causal interventions | No | all qualifying Hard cases | pre-defined strata |

## 4.2 API matrix

Primary：

- Full C0/C1；
- Hard C0/C1/C3-C10；
- Raw where supported。

API 不做 hidden-state mechanism。

# 5. Hardware allocation

## 5.1 8GB RTX 5050 notebook

适合：

- Qwen3-VL-2B behavior；
- data preprocessing；
- target manifests；
- unit tests；
- report generation；
- small J-lens debug；
- CPU/GPU mixed validation。

不作为 7B/8B primary Jacobian machine。

## 5.2 24GB RTX 4090

主力：

- 7B/8B SGM behavior；
- all-layer hidden capture；
- J-lens fit by layer/chunk；
- causal intervention；
- Qwen3-VL Raw forward（显存允许时）。

Primary precision：BF16。

推荐工程约束：

- batch size 1；
- Flash Attention where compatible；
- `torch.inference_mode()` for readout-only forward；
- gradient stages isolated；
- activation immediately CPU-offloaded；
- no storing all layers × all positions on GPU；
- parquet/zarr/npy chunked storage；
- OOM automatic retry cannot silently change dtype or quantization。

## 5.3 AutoDL fallback

触发：

- Raw multimodal 8B gradient OOM；
- 4090 上 J-lens fit 无法在合理 wall-clock 完成；
- confirmatory rerun 需要并行。

迁移时保持 exact model/config/lens semantics，不为加速改研究定义。

## 5.4 API budget

用户预算足够，可全量跑 MiMo/MiniMax/Kimi 等。GPT 仅用于：

- selected strong behavioral reference；
- primary judge `gpt-5-mini`；
- second-stage adjudication / subset validation。

# 6. 推荐十天执行节奏

该时间表是项目管理建议，不是科学 stopping rule。

## Day 0 - Protocol review and freeze

- 用户审核两份文档；
- 验证五个 open-weight snapshot 的 revision、文件 hash 与 BF16 forward；
- 决定是否立即纳入 STALE；
- 创建 experiment branch / tag。

## Day 1 - WP0/WP1/WP2

- registry；
- ATM adapter；
- model adapters；
- tests。

## Day 2 - WP3 behavior Hard matrix

- C0/C1；
- NIAH；
- Qwen3-VL Raw；
- 验证 eval / provenance。

## Day 3 - Full behavior + targets

- Full C0/C1；
- target manifests；
- Hard decision program draft。

## Day 4 - J-lens fitter validation

- 2B first；
- 256/512 stability；
- 8B/7B fit parallelization。

## Day 5 - Full basic readout

- five open models；
- J vs logit；
- success/failure aggregates。

## Day 6 - Scientific Review Gate D

人工审查：

- positive/negative evidence；
- late-only artifact；
- dominant failure stages；
- triggered extensions。

不在这一天修改 frozen metrics。

## Day 7 - Deep Hard trajectories / bridge

- C0/C1/NIAH/Raw；
- paired transitions；
- failure taxonomy。

## Day 8 - Causal interventions

- ablation；
- steering；
- state patching；
- swap where valid。

## Day 9 - Triggered extensions / cross-model completion

- binding-aware / phase-conditioned only if gate triggered；
- API completion。

## Day 10 - Confirmatory freeze and reports

- lock configs；
- rerun critical results；
- auto-generate tables/figures；
- produce paper-ready artifacts。

如果结果显示基础假设不成立，Day 7-10 转为 negative-result diagnosis，而不人为制造新 positive metric。

# 7. Data and artifact schemas

## 7.1 Run manifest

```json
{
  "run_id": "...",
  "experiment_id": "E2",
  "condition_id": "C0",
  "split": "full",
  "qa_hash": "...",
  "project_commit": "...",
  "project_dirty_patch_hash": "...",
  "atm_commit": "...",
  "model_repo": "...",
  "model_revision": "...",
  "tokenizer_revision": "...",
  "dtype": "bfloat16",
  "quantization": null,
  "device": "RTX 4090",
  "prompt_hash": "...",
  "generation_config": {},
  "lens_id": "...",
  "lens_hash": "...",
  "seed": 0,
  "started_at": "...",
  "finished_at": "..."
}
```

## 7.2 Probe row

```json
{
  "qa_id": "...",
  "model_id": "...",
  "condition_id": "C0",
  "layer": 18,
  "normalized_depth": 0.5,
  "position_type": "P_q",
  "position_index": 1024,
  "target_id": "operand_2",
  "target_text": "42",
  "target_kind": "number",
  "copyable": true,
  "single_token": true,
  "j_score": 0.0,
  "j_rank": 0,
  "logit_score": 0.0,
  "logit_rank": 0,
  "gold_decoy_margin": 0.0,
  "top25": false
}
```

## 7.3 Intervention row

```json
{
  "qa_id": "...",
  "model_id": "...",
  "condition_id": "C0",
  "intervention": "steering",
  "target_id": "derived_answer",
  "layer": 20,
  "position_type": "P_a0",
  "alpha": 1.0,
  "control_type": null,
  "pre_correct_logprob": 0.0,
  "post_correct_logprob": 0.0,
  "pre_answer": "...",
  "post_answer": "...",
  "pre_correct": false,
  "post_correct": true
}
```

# 8. Decision rules for adaptive research

建议创建 `DECISION_RULES.md`，至少包含：

```text
IF gold entities/values are J-readable but relation remains unresolved
THEN trigger binding-aware addendum.

IF thinking/answer phase changes gold rank/margin systematically
THEN trigger phase-conditioned lens addendum.

IF external view repairs behavior but global J-lens does not track state change
THEN evaluate evidence-conditioned or query-conditioned transport.

IF J-lens is late-only and not better than logit lens
THEN downgrade workspace claim; do not invent a new lens solely to rescue it.

IF behavioral repair aligns with internal state repair
THEN prioritize causal state patching.

IF steering repairs without content/layer specificity
THEN treat as generic perturbation, not mechanism-specific repair.
```

# 9. Tests Codex 必须先写

至少：

1. Full/Hard count and hash；
2. evidence order preservation；
3. NIAH fixed pool preservation；
4. VA does not delete/reorder/rewrite SGM；
5. P_q/P_a0 no answer leakage；
6. target manifest reproducibility；
7. tokenizer alias mapping；
8. J-lens tensor shapes；
9. logit-lens same activation input；
10. intervention sham identity；
11. zero-alpha steering identity；
12. ablation numerical projection check；
13. state patch alignment by semantic boundary；
14. immutable output refusal；
15. manifest completeness。

# 10. First review package after baseline runs

Codex 不应一口气跑到最后再交结果。Gate D 前必须生成一个 review bundle：

```text
reports/review_gate_D/
├── README.md
├── behavior_summary.csv
├── behavior_transitions.csv
├── internal_primary_metrics.csv
├── j_vs_logit.csv
├── late_layer_artifact_check.csv
├── hard_trajectory_index.md
├── failure_candidate_labels.csv
├── triggered_branch_recommendations.md
└── figures/
```

我们届时只回答：

- 哪些原假设有支持？
- 哪些负结果是真负结果，哪些是 readout limitation？
- 哪些分支被 gate 触发？
- causal intervention 应优先在哪些 strata 上做？

# 11. Paper-ready table/figure targets

## Table 1 - Multi-model behavioral failure landscape

Columns：model × C0/C1/NIAH load × qtype。

## Figure 1 - Unified lifecycle

```text
artifact
→ access
→ decision-facing view
→ representation formation
→ workspace/public-interface entry
→ binding
→ composition/operator
→ consumption
→ answer
```

## Figure 2 - Internal trajectories

选择预定义 strata：

- success；
- SGM fail→Raw repair；
- SGM fail→VA repair；
- Oracle success→NIAH fail。

展示 normalized layer × target score/margin。

## Table 2 - Cross-model internal diagnostics

- gold rank；
- margin；
- emergence；
- persistence；
- J-vs-logit advantage；
- failure mixture。

## Figure 3 - Causal repair

- ablation degradation；
- steering repair；
- success-state patching；
- matched controls。

# 12. 风险清单与 mitigation

## Risk 1 - J-lens 只读到 output/motor signal

Mitigation：silent positions、middle-layer analysis、logit-lens baseline、late-layer negative gate。

## Risk 2 - ATM gold answer 多为 multi-token

Mitigation：Full 只做自动 token-set/basic metrics；Hard 做 human-reviewed decision programs；multi-token negative 不解释为 absent。

## Risk 3 - Binding 无法由 token bag 识别

Mitigation：vanilla J-lens 不宣称 binding；由真实失败触发 binding-aware branch。

## Risk 4 - 24GB OOM

Mitigation：BF16、batch 1、layer/chunk processing、CPU offload、AutoDL fallback；不以 4-bit 代替 primary gradient claims。

## Risk 5 - API baseline 与官方 aggregate 不可逐题对齐

Mitigation：primary paired claims自己重跑；aggregate 只作 reference。

## Risk 6 - 31 Hard questions 太少

Mitigation：Full 1013 做基础统计；Hard 31 做深度 paired/causal analysis；不从 31 题推 general scaling law。

## Risk 7 - 太多实验导致叙事散

Mitigation：所有实验统一回答一个生命周期问题。正文只保留 E1-E4 主线；模型多只是 robustness，不产生多条故事。

## Risk 8 - Positive-result chasing

Mitigation：Frozen primary metrics、branch gates、negative gate、confirmatory rerun、protocol changelog。

# 13. Codex handoff checklist

Codex 开工前，用户审核并勾选：

- [ ] Protocol v1.0 overall accepted
- [x] Five open-weight model snapshots frozen and BF16-validated
- [ ] Own-rerun baseline policy accepted
- [ ] WikiText calibration + stability gate accepted
- [ ] Full 1013 basic readout accepted
- [ ] Hard 31 human-reviewed decision programs accepted
- [ ] STALE gated-secondary policy accepted
- [ ] BF16 no-primary-quantization policy accepted
- [ ] Five-stage taxonomy accepted
- [ ] New experiment directory layout accepted

Codex 第一阶段只实现 WP0-WP6，并在 Gate C 停止。不要自动继续到所有 causal/extension experiments，除非用户审核 baseline 实现和数值 sanity。

# 14. 最终交付物

完成整个 program 后，仓库应至少拥有：

- frozen protocol + changelog；
- model/dataset/condition registries；
- exact target manifests；
- Hard decision programs；
- fitted lens artifacts + hashes；
- all behavioral predictions；
- all probe metrics；
- all intervention records；
- statistical reports；
- paper-ready tables/figures；
- negative-result logs；
- branch addenda；
- confirmatory run manifests。

最终成功标准不是“J-space 一定得到 positive result”，而是：

$$
\boxed{
\text{外部 evidence 条件}
\rightarrow
\text{内部 decision-state 变化}
\rightarrow
\text{行为结果}
}
$$

这条链能否被清晰地定位、证伪、干预，并跨模型复现。若不能，也要能明确说明失败发生在 view、probe、binding、composition、consumption 还是当前 J-lens 的表示边界。
