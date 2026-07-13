# J-lens 夜间运行手册

本文档用于检查和恢复已批准的 J-lens calibration。所有命令都在远程 WSL
服务器执行，不在本地笔记本执行。J-lens 不使用 answer judge，也不需要配置
任何 API key。当前没有获准自动启动的新 fit；不要把本手册当成夜间批量队列。

## 1. 登录与进入项目

```bash
ssh lab@100.121.186.75
cd /home/lab/lab/post-retrieval-reasoning
git pull --ff-only
```

正式分支应为：

```text
experiment/post-retrieval-jspace-v1
```

不要切换分支，不要运行 `git reset`，不要删除 `research_artifacts` 中的
checkpoint。

## 2. 首先检查当前状态

```bash
experiments/post_retrieval_jspace_v1/scripts/check_jlens_status.sh
```

重点查看：

- `Active J-lens processes`：是否仍有 fit 在运行；
- `status=running`：任务尚未完成；
- `status=complete`：lens 和 manifest 已完整落盘；
- `Latest progress`：最近完成到第几个 prompt。

截至 2026-07-13 的冻结状态：

```text
Qwen3-VL-2B n256: complete, selected
Qwen3-VL-2B n512: complete
Qwen3-VL-2B stability: passed
Qwen3-8B n256: complete, exploratory; nested stability not run
Qwen2.5-7B: n256 resumed from atomic prompt-64 checkpoint
DeepSeek-R1-Distill-Llama-8B: not fit
Qwen3-VL-8B: not fit
```

当前后台任务是 `tmux: jlens-qwen2p5-n256-resume`。它从 prompt 64 恢复，
首个恢复样本 prompt 65 用时 105 秒。Qwen3-VL-2B C3-C6 behavior inference
已全部完成 31/31。未获人工批准前不要在 Qwen2.5 之外启动新模型 fit。

## 3. 已完成的 Qwen3-VL-2B Stability Gate

确认以下两个 fit 都显示 `status=complete`：

```text
qwen3_vl_2b_instruct/wikitext103-n256-v2
qwen3_vl_2b_instruct/wikitext103-n512-v1
```

该 gate 已完成，结果为 matrix cosine median `0.9999695`、top-25 overlap
median `0.96`，因此首轮 ATM readout 选择 n256。只有需要验证产物完整性时才
重新读取报告；不要覆盖原目录。复现命令为：

```bash
experiments/post_retrieval_jspace_v1/scripts/run_jlens_stability.sh \
  qwen3_vl_2b_instruct \
  wikitext103-n256-v2 \
  wikitext103-n512-v1 \
  stability-n256-n512-v1
```

查看结果：

```bash
python3 -m json.tool \
  /home/lab/lab/research_artifacts/jlens_stability/qwen3_vl_2b_instruct/stability-n256-n512-v1/stability.json \
  | tail -20
```

关键字段：

```text
matrix_cosine_median
top25_overlap_median
matrix_gate_pass
top25_gate_pass
gate_pass
```

冻结阈值为：

```text
matrix cosine median >= 0.98
top-25 overlap median >= 0.90
```

冻结选择规则为：

- `gate_pass: true`：其余模型使用 `N=256`；
- `gate_pass: false`：其余模型使用 `N=512`；
- stability 命令报错或字段缺失：停止，不自行选择 N。

## 4. 其余模型当前暂停

以下命令仅供 Gate C review 批准扩模型后使用。当前不得执行。获批后 `N`
使用 256，并且每次只运行一个命令。

### Qwen3-8B-ms

```bash
experiments/post_retrieval_jspace_v1/scripts/run_jlens_fit.sh \
  qwen3_8b_ms N wikitext103-nN-v1
```

### DeepSeek-R1-Distill-Llama-8B

```bash
experiments/post_retrieval_jspace_v1/scripts/run_jlens_fit.sh \
  deepseek_r1_distill_llama_8b N wikitext103-nN-v1
```

### Qwen2.5-7B-Instruct

```bash
experiments/post_retrieval_jspace_v1/scripts/run_jlens_fit.sh \
  qwen2_5_7b_instruct N wikitext103-nN-v1
```

### Qwen3-VL-8B-Instruct

```bash
experiments/post_retrieval_jspace_v1/scripts/run_jlens_fit.sh \
  qwen3_vl_8b_instruct N wikitext103-nN-v1
```

Qwen3-8B 已通过一提示资源 probe，并使用 `dim_batch=2` 完成 n256；它还没有
n512 或 nested stability。Qwen2.5-7B 使用 `dim_batch=4`，现有 prompt-64
checkpoint 必须恢复而非重算。其他模型若发生 CUDA OOM，停止并保留日志，
不要改成 4-bit、减层或自行修改协议参数。

## 5. 运行中查看进度

另开一个 SSH 终端执行：

```bash
cd /home/lab/lab/post-retrieval-reasoning
experiments/post_retrieval_jspace_v1/scripts/check_jlens_status.sh
```

也可直接查看最新日志：

```bash
tail -f /home/lab/lab/research_artifacts/logs/jlens-*.log
```

退出 `tail -f` 使用 `Ctrl-C`。这不会停止 fit。

## 6. SSH 断开与断点恢复

通过 `run_jlens_fit.sh` 前台启动时，SSH 意外断开可能终止 Python 进程，但每
8 个 prompts 会保存一次原子 checkpoint。重新登录后先运行状态检查。如果没有
活动进程、对应 manifest 仍为 `running`，使用完全相同的模型、N 和 fit ID，并
在第四个参数添加 `--resume`：

```bash
experiments/post_retrieval_jspace_v1/scripts/run_jlens_fit.sh \
  MODEL_ID N FIT_ID --resume
```

示例：

```bash
experiments/post_retrieval_jspace_v1/scripts/run_jlens_fit.sh \
  qwen3_8b_ms 256 wikitext103-n256-v1 --resume
```

只允许恢复 `status=running` 的任务。`status=complete` 不得恢复或覆盖。

若计划关闭终端后继续运行，可在 `tmux` 中启动：

```bash
tmux new -s jlens
```

在 tmux 中执行 fit 命令后，按 `Ctrl-B`，再按 `D`，即可退出但保持任务运行。
重新进入：

```bash
tmux attach -t jlens
```

## 7. 何时必须停止

遇到以下任一情况，不要自行调整协议：

- CUDA OOM；
- manifest 与 lens hash 不匹配；
- calibration hash mismatch；
- `status=complete` 但没有 `lens.pt`；
- stability 报告缺少 gate 字段；
- 同一模型出现两个正在运行的 fit；
- 需要修改 `dim_batch`、层数、窗口数、dtype 或 tokenizer；
- checkpoint 无法恢复。

保留终端报错和对应日志，然后停止该模型。不要删除失败目录。

## 8. 当前固定配置

```text
model weights: BF16
source layers: final target 之前的全部 residual layers
final layer readout: identity
dim_batch: 8 (Qwen3-8B override: 2; Qwen2.5-7B override: 4)
max_seq_len: 256
skip_first: 16
checkpoint_every: 8 prompts
saved lens dtype: float16
calibration seed: 17
calibration corpus: WikiText-103 raw train
held-out stability prompts: stream offset 512, count 32
```

这些配置由以下文件共同锁定：

```text
registry/model_registry.yaml
registry/jlens_calibration.yaml
registry/jlens_fit.yaml
PROTOCOL_ADDENDUM_v1.0.md
```
