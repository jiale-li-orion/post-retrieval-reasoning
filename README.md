# Post-Retrieval Reasoning

## 1. 研究问题 / Thesis
- `my_paper/sections/01_introduction.tex` — 问题定义
- `my_paper/main.tex` (abstract) — 概述

## 2. 理论框架（已写）
- `my_paper/sections/02_problem.tex` — AAS 形式化定义
- `my_paper/sections/03_framework.tex` — 两个命题、decision state、harnessed evaluation

## 3. 引用 / 参考工作
- `other_may_help.md` — 文献笔记 + 5 个 benchmark 仓库 README
- `human-reading-doc/现状.md` — 领域背景
- `human-reading-doc/OpenViking_analysis_report.md` — OpenViking 分析报告
- `human-reading-doc/oracle_evidence.md` — oracle evidence 分析
- `0710_j-space讨论/J-Space_README.md` — 推理失败分类框架

## 4. 已有发现（Exp 1 完成）
- `experiments/atm_oracle_evidence/README.md` — 结果数据
- `experiments/README.md` — 实验线状态总表

## 5. 实验代码
- `experiments/atm_oracle_evidence/` — Exp 1 脚本（SGM vs Raw, ATM-Bench Hard）
- `experiments/atm_oracle_evidence_verbal-R3/` — 可复用的 Verbal-R3 annotation pipeline
- `experiments/post_retrieval_jspace_v1/` — 当前正式实验线（E1-E4，首周期止于 Gate C）
- `FINAL_EXPERIMENTAL_PROTOCOL_v1.0.md` — 当前最高层科学合同
- `EXPERIMENT_DESIGN_AND_EXECUTION_PLAN_v1.0.md` — 当前实施合同
- `PROTOCOL.md` — 历史 Verbal Annotation 协议

## 6. 论文草稿
- `my_paper/main.tex` — 完整 LaTeX 结构
- `my_paper/sections/01_introduction.tex` — 已写
- `my_paper/sections/02_problem.tex` — 已写
- `my_paper/sections/03_framework.tex` — 已写
- `my_paper/sections/04_atm_diagnostics.tex` — 骨架 [pending]
- `my_paper/sections/05_stale_case.tex` — 骨架 [pending]
- `my_paper/sections/06_related_work.tex` — 骨架 [pending]
- `my_paper/sections/07_discussion_limitations.tex` — 骨架 [pending]
- `my_paper/sections/08_conclusion.tex` — 骨架 [pending]

## 当前阶段 / Stage
- Exp 1: 完成
- 旧 Exp 2: 作为可复用 VA 模块保留
- 正式实验线: Phase 0，环境与 provenance 准备中
- 论文: Sections 1-3 已写，4-8 待写

## GPT 阅读顺序
1. 本文件（README）
2. `experiments/README.md`
3. `my_paper/sections/01_introduction.tex`
4. `my_paper/sections/02_problem.tex`
5. `my_paper/sections/03_framework.tex`
6. `experiments/atm_oracle_evidence/README.md`
7. `other_may_help.md`
8. `human-reading-doc/现状.md`
9. `FINAL_EXPERIMENTAL_PROTOCOL_v1.0.md`
10. `EXPERIMENT_DESIGN_AND_EXECUTION_PLAN_v1.0.md`
11. `experiments/post_retrieval_jspace_v1/PROTOCOL_ADDENDUM_v1.0.md`
12. `0710_j-space讨论/J-Space_README.md`
