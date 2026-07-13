# ATM-Bench Oracle Evidence 历史 Pilot

该目录保留 MiMo V2.5 在 ATM-Bench Hard 上的 SGM/Raw oracle predictions、
早期 DeepSeek judge 和 failure analysis。它不是当前正式实验线；完整
GPT-5-mini 补评结果是该 pilot 的当前权威评分记录。

## 当前权威评分

两组冻结 predictions 均使用 ATM 官方 evaluator，`open_end` 使用
GPT-5-mini、`reasoning_effort=minimal`，无 fallback。完整快照位于：

```text
/home/orion/research_artifacts/frozen_behavior/mimo-v25-legacy-oracle-v1/
```

| 指标 | SGM Oracle | Raw Oracle | Delta |
|------|-----------:|-----------:|------:|
| ATM 总分 | 44.08% | 58.11% | +14.03 |
| list_recall ATM | 72.20% | 91.78% | +19.58 |
| number ATM | 16.67% | 16.67% | 0 |
| open_end ATM | 30.77% | 46.15% | +15.38 |

两组均完成 31/31，其中各含 13 道 `open_end`；无 API failure、fallback 或
模型标识不一致。仓库内旧 `eval/atm_gpt-5-mini.json` 只覆盖 18 道确定性题，
不能作为完整评分使用。

## 早期 DeepSeek Pilot

MiMo-V2.5 在 ATM-Bench-Hard（31 题）上的 Oracle Evidence 对比，judge: DeepSeek V4 Flash。

| 指标 | SGM Oracle | Raw Oracle | Delta |
|------|-----------|------------|-------|
| EM | 19.35% (6/31) | 38.71% (12/31) | +19.4 |
| ATM 总分 | 40.85% | 64.56% | +23.7 |
| list_recall ATM | 72.2% | 91.8% | +19.6 |
| number ATM | 16.7% | 16.7% | 0 |
| open_end ATM | 23.1% | 61.5% | +38.4 |

### 当时的观察

1. **SGM/Raw 差异集中在 open_end 与 list_recall**：具体字段缺失只能作为 failure-case 假设，不能仅凭 aggregate 分数断言主因。
2. **list_recall 也有显著提升**：Raw 能看到原图所以召回更全（91.8% vs 72.2%）。
3. **number ATM 完全没变**：不管给原图还是压缩字段，数值题都是 16.7%。这提示 post-access evaluation failure，但不能仅凭该结果排除 view insufficiency。

### 在当前论文中的用途

这组 pilot 用于提出并筛选 view insufficiency、binding/composition failure 和
decoder-use failure 假设，不作为这些机制的验证。正式机制诊断在
`../post_retrieval_jspace_v1/` 中进行。

## 目录结构

```
experiments/atm_oracle_evidence/
├── scripts/
│   ├── run_mimo_v25_sgm_hard.sh    # SGM oracle 入口
│   ├── run_mimo_v25_raw_hard.sh    # Raw oracle 入口
│   └── run_qwen3vl8b_sgm_oracle.sh # Qwen3-VL-8B vLLM SGM oracle 入口
├── runs/
│   ├── mimo_v25_sgm_hard/
│   │   ├── manifest.env
│   │   ├── predictions/oracle_mimo_v25_sgm_hard.jsonl
│   │   ├── eval_ds/                # DeepSeek judge 结果
│   │   └── logs/
│   └── mimo_v25_raw_hard/
│       ├── manifest.env
│       ├── predictions/oracle_mimo_v25_raw_hard.jsonl
│       ├── eval_ds/                # DeepSeek judge 结果
│       └── logs/
└── README.md
```

## 运行方式

所有脚本默认使用项目根目录 `.venv`：

```text
/home/orion/research/agent_memory_paper/.venv/bin/python3
```

需要临时覆盖时使用 `PYTHON=/path/to/python`。不要在本实验目录下创建局部 `.venv`。

ATM-Bench 默认路径：

```text
/home/orion/research/agent_memory_paper/other_repo_references/ATM-Bench
```

如需覆盖，使用 `ATM_BENCH_ROOT=/path/to/ATM-Bench`。

### SGM Oracle

```bash
MIMO_API_KEY=<key> bash experiments/atm_oracle_evidence/scripts/run_mimo_v25_sgm_hard.sh
```

### Raw Oracle

需要 ffmpeg + ffprobe + 完整 raw 数据。

```bash
export PATH="/tmp/ffmpeg-static:$PATH"
MIMO_API_KEY=<key> bash experiments/atm_oracle_evidence/scripts/run_mimo_v25_raw_hard.sh
```

### Qwen3-VL-8B SGM Oracle

这是早期本地 vLLM baseline 入口，只跑 SGM oracle prediction，输出统一放在：

```text
experiments/atm_oracle_evidence/runs/qwen3vl8b_sgm_oracle/
```

```bash
VLLM_ENDPOINT=http://127.0.0.1:8000/v1/chat/completions \
bash experiments/atm_oracle_evidence/scripts/run_qwen3vl8b_sgm_oracle.sh hard
```

### Eval（DeepSeek judge）

脚本默认用 gpt-5-mini，需手动跑 DeepSeek judge：

```bash
cd other_repo_references/ATM-Bench
PYTHONPATH="$(pwd):${PYTHONPATH:-}" \
OPENAI_BASE_URL=https://api.deepseek.com/v1 \
OPENAI_API_KEY=<deepseek-key> \
python3 memqa/utils/evaluator/evaluate_qa.py \
  --ground-truth "./data/atm-bench/atm-bench-hard.json" \
  --predictions "../experiments/atm_oracle_evidence/runs/<run_dir>/predictions/<pred>.jsonl" \
  --output-dir "../experiments/atm_oracle_evidence/runs/<run_dir>/eval_ds" \
  --metrics em atm \
  --judge-provider openai \
  --judge-model deepseek-v4-flash \
  --judge-reasoning-effort minimal \
  --max-workers 2
```

## 环境说明

- MiMo API key 在 `~/.bashrc` 的 `MIMO_API_KEY` 变量中
- DeepSeek API key 在 `~/.bashrc` 的 `DEEPSEEK_API_KEY` 变量中
- Python 统一使用项目根目录 `.venv`
- ATM-Bench 统一从 `other_repo_references/ATM-Bench` 读取
- ffmpeg 静态二进制在 `/tmp/ffmpeg-static/`
- Raw 数据通过 `HF_ENDPOINT=https://hf-mirror.com` 从 HuggingFace 镜像站下载
- `evaluate_qa.py` 已 patch：支持 `OPENAI_BASE_URL` 环境变量和 `chat.completions.create` fallback

## 官方对比

ATM-Bench 官方报告的 MiMo-V2.5 结果（ATM-Bench 全集，非 Hard）：

- SGM Oracle: 44.6
- Raw Oracle: 52.1

我们的结果在 Hard 子集上，数值不同但趋势一致：Raw > SGM，且差距在 open_end 上最大。
