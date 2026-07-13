# ATM-Bench Verbal Annotation 实验

该目录是早期 Verbal Annotation pipeline 和可复用接口，不再是顶层正式实验
协议。当前协议、condition contract、canonical cache 与正式运行状态统一由
[`../post_retrieval_jspace_v1/`](../post_retrieval_jspace_v1/) 管理。

本模块固定 ATM-Bench 的 Oracle/NIAH evidence，只测试在 SGM 中加入
Verbal-R3 annotation 后的回答表现；不测 retrieval 或 top-k。这里的旧运行
命令用于模块复现和 smoke，不应直接作为当前正式 E1 运行入口。

## 代码结构

```text
configs/verbal_r3_official.json  # reranker、answerer 与 evidence 固定配置
scripts/verbal_r3_core.py        # 无外部模型依赖的协议逻辑
scripts/verbal_r3_oracle.py      # ATM/VerbalR3 接口编排
scripts/run_experiment.sh        # Oracle 与 NIAH 统一运行入口
tests/                           # 协议行为测试
```

代码直接复用 ATM-Bench 的 `collect_text_evidence()`、`build_text_messages()`、`OracleLLM` 和 `evaluate_qa.py`。Verbal prompt 从锁定版本的 `other_repo_references/VerbalR3/utils/reranker_server.py` 读取，不在实验脚本中维护副本。

## 运行

所有脚本默认使用项目根目录 `.venv`：

```text
/home/orion/research/agent_memory_paper/.venv/bin/python3
```

如需临时覆盖解释器，使用 `PYTHON=/path/to/python`。正式 run 的 `manifest.json` 会记录实际 Python 路径。

外部 repo 默认路径：

```text
/home/orion/research/agent_memory_paper/other_repo_references/ATM-Bench
/home/orion/research/agent_memory_paper/other_repo_references/VerbalR3
```

如需覆盖，使用 `ATM_BENCH_ROOT=/path/to/ATM-Bench` 或 `VERBAL_R3_ROOT=/path/to/VerbalR3`。

MiMo Oracle Hard 示例：

```bash
ANSWERER_MODEL=mimo-v2.5 \
ANSWERER_ENDPOINT=https://api.xiaomimimo.com/v1/chat/completions \
ANSWERER_API_KEY="$MIMO_API_KEY" \
CONDITION=oracle SPLIT=hard \
bash experiments/atm_oracle_evidence_verbal-R3/scripts/run_experiment.sh
```

NIAH-50 示例：

```bash
ANSWERER_MODEL=mimo-v2.5 \
ANSWERER_ENDPOINT=https://api.xiaomimimo.com/v1/chat/completions \
ANSWERER_API_KEY="$MIMO_API_KEY" \
CONDITION=niah SPLIT=hard NIAH_K=50 \
bash experiments/atm_oracle_evidence_verbal-R3/scripts/run_experiment.sh
```

两题 smoke test 增加 `LIMIT=2`。每次运行创建独立目录；目录或输出已存在时直接失败。

## 输出

```text
runs/<condition>/<split>/<model>/<run-id>/
├── manifest.json
├── predictions.jsonl
├── annotations.jsonl
├── run_stats.json
├── eval/
└── logs/
```

`annotations.jsonl` 逐 evidence 保存 comment、score、token、延迟和 checkpoint provenance；`predictions.jsonl` 保留 ATM evaluator 所需的 `id`、`answer`，同时保存协议规定的 answerer usage 字段。

## 测试

```bash
/home/orion/research/agent_memory_paper/.venv/bin/python3 -m unittest discover \
  -s experiments/atm_oracle_evidence_verbal-R3/tests -v
```
