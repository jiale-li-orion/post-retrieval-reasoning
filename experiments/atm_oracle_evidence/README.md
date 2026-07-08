# ATM-Bench Oracle Evidence 实验记录

## 实验结果

MiMo-V2.5 在 ATM-Bench-Hard（31 题）上的 Oracle Evidence 对比，judge: DeepSeek V4 Flash。

| 指标 | SGM Oracle | Raw Oracle | Delta |
|------|-----------|------------|-------|
| EM | 19.35% (6/31) | 38.71% (12/31) | +19.4 |
| ATM 总分 | 40.85% | 64.56% | +23.7 |
| list_recall ATM | 72.2% | 91.8% | +19.6 |
| number ATM | 16.7% | 16.7% | 0 |
| open_end ATM | 23.1% | 61.5% | +38.4 |

### 关键发现

1. **view 压缩是 open_end 的主要瓶颈**：SGM 的 batch_fields 缺少 event_name、conference_name 等字段，模型只能输出时间戳 ID 而不是会议名。Raw 给原图后 open_end 从 23.1% 跳到 61.5%。
2. **list_recall 也有显著提升**：Raw 能看到原图所以召回更全（91.8% vs 72.2%）。
3. **number ATM 完全没变**：不管给原图还是压缩字段，数值推理都是 16.7%。这是纯粹的 decoder 瓶颈——模型不会加法、不会日期推导。

### 对论文框架的验证

SGM 的失败同时包含：
- **view-use failure**（open_end、list_recall）：证据存在但 view 丢失了关键字段
- **decoder-use failure**（number）：view 充分但模型无法执行聚合计算

## 目录结构

```
experiments/atm_oracle_evidence/
├── scripts/
│   ├── run_mimo_v25_sgm_hard.sh    # SGM oracle 入口
│   └── run_mimo_v25_raw_hard.sh    # Raw oracle 入口
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

### Eval（DeepSeek judge）

脚本默认用 gpt-5-mini，需手动跑 DeepSeek judge：

```bash
cd ATM-Bench
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
- ffmpeg 静态二进制在 `/tmp/ffmpeg-static/`
- Raw 数据通过 `HF_ENDPOINT=https://hf-mirror.com` 从 HuggingFace 镜像站下载
- `evaluate_qa.py` 已 patch：支持 `OPENAI_BASE_URL` 环境变量和 `chat.completions.create` fallback

## 官方对比

ATM-Bench 官方报告的 MiMo-V2.5 结果（ATM-Bench 全集，非 Hard）：

- SGM Oracle: 44.6
- Raw Oracle: 52.1

我们的结果在 Hard 子集上，数值不同但趋势一致：Raw > SGM，且差距在 open_end 上最大。
