# ATM Hard-31 Solvability Audit

本目录审计 ATM-Bench Hard 31 在官方 SGM Oracle 输入下是否可解。主审计不运行
answerer；复查层读取已有冻结回答，不发起新推理。可解性判断只允许使用官方 answerer
实际获得的 `Question + SGM evidence`；数据集中的 `notes` 不提供给审计者，也不进入产物。

分类合同：

- `A`：输入自包含；证据可逐项直接读取或枚举，不需要恢复隐藏关系。
- `B`：必须联合证据完成绑定、消歧、聚合或状态更新，但整组输入足够。
- `C`：缺少指代映射或必要状态，需输入之外的信息才能得到 gold。
- `D`：当前输入支持多个不同答案，无法唯一决定 gold。
- `E`：gold answer、SGM view、evidence IDs、问题或评分口径不一致。

生成产物：

```bash
PYTHONPATH=experiments/post_retrieval_jspace_v1 \
  uv run python experiments/atm_hard31_solvability_audit/build_audit.py
uv run python experiments/atm_hard31_solvability_audit/build_model_answer_crosscheck.py
```

- `HARD31_SOLVABILITY_AUDIT.md`：31 行总表与逐题完整 evidence。
- `audit_rows.json`：同一审计的结构化版本。
- `audit_labels.json`：人工判定源；后续 review 只修改此文件再重新生成。
- `MODEL_ANSWER_CROSSCHECK.md`：三份冻结模型回答、ATM 分数与重点病例复查。
- `model_answer_rows.json`：完整回答对照的结构化版本。
- `model_answer_findings.json`：人工复查结论源。
