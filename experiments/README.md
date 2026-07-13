# Experiments

这个目录只管理实验资产：协议、脚本、运行输出、评测结果和 failure analysis。论文正文、文献笔记和写作草稿不放这里。

## 当前实验线

| ID | 状态 | 作用 | 是否论文主实验 | 可信度 |
|---|---|---|---|---|
| `atm_oracle_evidence` | 已完成（历史 pilot） | ATM-Bench Hard 上的 SGM vs Raw oracle 对照，用来定位 view-use / decoder-use failure | 否，作为动机和误差分析素材 | predictions 可复用；当前以 GPT-5-mini 补评结果为准 |
| `atm_oracle_evidence_verbal-R3` | 可复用模块 | 生成 query-conditioned Verbal Annotation；供正式实验线复用 | 否，不再独立承担主实验 | 官方 prompt/interface 已核对；canonical cache 由正式实验线管理 |
| `post_retrieval_jspace_v1` | Phase 1 已闭合，Gate C 进行中 | E1 行为图谱、J-lens/J-space tracing、bridge 与 gated causal repair | 是 | Qwen3-VL-2B C0/C1 行为锚点与首个稳定 lens 已完成 |

## 已完成结果

`atm_oracle_evidence` 已跑完。完整 GPT-5-mini 官方协议补评是当前主记录；
早期 DeepSeek 结果仅保留为 secondary pilot：

| Run | Evidence | Judge | ATM | number | list_recall | open_end |
|---|---|---|---:|---:|---:|---:|
| `mimo_v25_sgm_hard` | SGM oracle | GPT-5-mini | 44.08 | 16.67 | 72.20 | 30.77 |
| `mimo_v25_raw_hard` | Raw oracle | GPT-5-mini | 58.11 | 16.67 | 91.78 | 46.15 |

两组均覆盖 Hard 31/31，其中各含 13 道 `open_end`；无 judge failure 或
fallback。冻结结果位于
`/home/orion/research_artifacts/frozen_behavior/mimo-v25-legacy-oracle-v1/`，
不提交完整 predictions。

关键观察：

- Raw 相比 SGM 在 `open_end` 和 `list_recall` 上提升明显，说明 SGM view 可能丢掉了一部分决策所需信息；该 pilot 不能单独定位每道题的因果机制。
- `number` 在 Raw 和 SGM 下都是 16.7%，说明一部分失败不是 evidence access，而是 decoder/evaluation 能力问题。
- 这组结果用于形成理论假设和 failure taxonomy，不作为最终 Verbal Annotation 主实验结论。

## 当前正式实验

`post_retrieval_jspace_v1` 是当前主线。Gate A 已通过，Qwen3-VL-2B Hard
C0/C1 的 GPT-5-mini 行为闭环已完成，C3-C6 NIAH control inference 均完成
31/31。Gate B 尚未通过；第一实施周期仍在 Gate C 停止并等待人工 review。
旧 VA pipeline 只作为该主线的 external evidence intervention 模块。

其中 VA 子实验保持：

```text
controlled SGM evidence
  -> SGM-only answer
  -> SGM + query-conditioned Verbal Annotation answer
```

当前边界：

- 测 post-access / post-retrieval evidence use。
- 不测 retrieval、reranking top-k、完整 Verbal-R3 planner、generator training。
- Oracle 与 NIAH 都使用 ATM-Bench 控制证据。
- API answerer 只跑 Hard C1/C7-C10，官方 C0/C3-C6 aggregate 仅作参考。
- 五个 open-weight 模型自行重跑正式 baseline。
- Primary ATM judge 严格使用官方 `gpt-5-mini` 配置。

## 目录约定

每条实验线使用同一套结构：

```text
<experiment_id>/
├── README.md          # 工作区状态、运行入口、结果索引
├── PROTOCOL.md        # 只有正式实验线需要；实验设计合同
├── configs/           # 固定配置，模型、prompt、字段、参数
├── scripts/           # 可运行脚本；脚本名必须表达模型/条件/阶段
├── tests/             # 协议行为和代码接口测试
├── runs/              # 运行输出；不手工编辑
└── reports/           # 由脚本生成或人工整理的实验报告
```

清理规则：

- 不在实验目录下保留 `.venv`、`__pycache__`、临时下载、空的 run 目录。
- 不在根目录放 `run_experiments.sh` 这类无归属脚本。
- 新脚本必须放进对应实验线的 `scripts/`，并在该实验线 README 登记。
- 每个正式 run 必须有 manifest、prediction、eval、logs；输出已存在时应失败而不是覆盖。

## Python 环境

整个实验区只使用一个 Python 虚拟环境：

```text
/home/orion/research/agent_memory_paper/.venv
```

脚本约定：

- 所有实验入口默认使用 `${ROOT_DIR}/.venv/bin/python3`。
- 如需临时切换解释器，只能通过 `PYTHON=/path/to/python` 显式覆盖。
- 禁止在 `experiments/` 子目录下创建 `.venv`、`venv` 或其他局部环境。
- run manifest 必须记录实际使用的 `python` 路径。

外部代码仓库统一从这里读取：

```text
/home/orion/research/agent_memory_paper/other_repo_references/ATM-Bench
/home/orion/research/agent_memory_paper/other_repo_references/VerbalR3
```

脚本约定：

- `ATM_BENCH_ROOT=/path/to/ATM-Bench` 可覆盖 ATM-Bench 路径。
- `VERBAL_R3_ROOT=/path/to/VerbalR3` 可覆盖 VerbalR3 路径。
- 实验脚本不再假设根目录下存在 `ATM-Bench/` 或 `VerbalR3/`。

当前已清理：

- `experiments/atm_oracle_evidence/.venv`
- 空的 `notes/`、`eval/`、`reports/`、`runs/` 占位目录

## 当前待办

1. 对已冻结的 Qwen3-VL-2B C3-C6 predictions 分阶段执行 ATM evaluator 与
   GPT-5-mini `open_end` judge，不重跑 inference。
2. canonical VA cache 从本地 2727 条完整记录继续生成；恢复前先复核唯一键、
   尾行和温控参数。
3. 人工审核并冻结 Hard 31 decision programs。目前仅 9/31 题具有 A/B 类
   机制 target，必须先设计 phrase/sequence readout extension。
4. Gate C review 前暂停新增模型拟合和正式 trajectory；Qwen3-8B 的行为
   preflight 还需先冻结 reasoning-output contract。
