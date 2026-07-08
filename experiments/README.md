# Experiment Registry

## Active Experiments

| ID | Status | Purpose | Benchmark | Primary Question |
| --- | --- | --- | --- | --- |
| `atm_oracle_evidence` | **done** | SGM vs Raw Oracle evidence 条件对比 | ATM-Bench Hard (31) | View 压缩是否是记忆使用的主要瓶颈？ |

## Results Summary

MiMo-V2.5 × ATM-Bench-Hard × DeepSeek V4 Flash judge:

| | SGM Oracle | Raw Oracle |
|---|---|---|
| EM | 19.35% | 38.71% |
| ATM | 40.85% | 64.56% |
| open_end ATM | 23.1% | 61.5% |
| number ATM | 16.7% | 16.7% |

**结论**：view 压缩是 open_end/list_recall 的主要瓶颈（view-use failure），number 是纯 decoder 瓶颈（decoder-use failure）。

## Directory Rules

- `scripts/`: runnable scripts. Copy official benchmark scripts before modifying.
- `runs/`: run-specific logs, manifest, predictions, and eval results.
- `notes/`: short analysis notes and failure taxonomies.

## Run Discipline

For each run, record in `manifest.env`:
- exact command, model, endpoint
- dataset file, evidence condition
- prediction path, eval path
- judge model and API provider
- known deviations from official benchmark scripts
