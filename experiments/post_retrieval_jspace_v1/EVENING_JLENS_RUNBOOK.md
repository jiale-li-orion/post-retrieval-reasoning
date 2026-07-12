# J-lens 夜间运行手册

本文档用于服务器 GPU 空闲时继续运行 J-lens calibration。所有命令都在远程
WSL 服务器执行，不在本地笔记本执行。J-lens 不使用 answer judge，也不需要
配置任何 API key。

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

当前正在运行的任务应为：

```text
qwen3_vl_2b_instruct / wikitext103-n512-v1
```

只要它仍显示为 `running`，不要启动其他 GPU 实验。运行脚本自身也会检测并
拒绝并发。

## 3. Qwen3-VL-2B n512 完成后运行 Stability Gate

确认以下两个 fit 都显示 `status=complete`：

```text
qwen3_vl_2b_instruct/wikitext103-n256-v2
qwen3_vl_2b_instruct/wikitext103-n512-v1
```

然后执行：

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

选择规则：

- `gate_pass: true`：其余模型使用 `N=256`；
- `gate_pass: false`：其余模型使用 `N=512`；
- stability 命令报错或字段缺失：停止，不自行选择 N。

## 4. 依次运行其余四个模型

以下命令中的 `N` 必须替换为上一节确定的 `256` 或 `512`。每次只运行一个
命令，前一个完成后再次执行状态检查，再运行下一个。

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

建议先运行三个 7B/8B 文本模型，最后运行 Qwen3-VL-8B。8B 模型的正式
Jacobian fit 尚未做完整资源测量；若发生 CUDA OOM，停止并保留日志，不要改成
4-bit，不要减层，不要自行修改 `dim_batch`。

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
dim_batch: 8
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
