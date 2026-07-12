#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 || $# -gt 4 ]]; then
  echo "usage: $0 MODEL_ID {256|512} FIT_ID [--resume]" >&2
  exit 2
fi

MODEL_ID=$1
SAMPLE_COUNT=$2
FIT_ID=$3
RESUME=${4:-}

case "$MODEL_ID" in
  qwen3_8b_ms|deepseek_r1_distill_llama_8b|qwen2_5_7b_instruct|qwen3_vl_2b_instruct|qwen3_vl_8b_instruct) ;;
  *) echo "unknown frozen model ID: $MODEL_ID" >&2; exit 2 ;;
esac
case "$SAMPLE_COUNT" in
  256|512) ;;
  *) echo "sample count must be 256 or 512" >&2; exit 2 ;;
esac
if [[ -n "$RESUME" && "$RESUME" != "--resume" ]]; then
  echo "fourth argument may only be --resume" >&2
  exit 2
fi

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
PYTHON="$PROJECT_ROOT/.venv/bin/python"
RUNNER="$PROJECT_ROOT/experiments/post_retrieval_jspace_v1/jacobian_analysis/fit_jlens.py"
LOCK=/home/lab/lab/research_artifacts/.gpu-experiment.lock
LOG_ROOT=/home/lab/lab/research_artifacts/logs
mkdir -p "$LOG_ROOT"

if [[ ! -x "$PYTHON" ]]; then
  echo "project environment missing: $PYTHON" >&2
  exit 1
fi
if pgrep -af '[f]it_jlens.py|[r]un_behavior.py|[g]enerate_va_cache.py' >/dev/null; then
  echo "refusing to overlap an active GPU experiment:" >&2
  pgrep -af '[f]it_jlens.py|[r]un_behavior.py|[g]enerate_va_cache.py' >&2
  exit 1
fi

exec 9>"$LOCK"
if ! flock -n 9; then
  echo "GPU experiment lock is already held: $LOCK" >&2
  exit 1
fi

cd "$PROJECT_ROOT"
export PYTHONPATH=experiments/post_retrieval_jspace_v1
LOG="$LOG_ROOT/jlens-${MODEL_ID}-n${SAMPLE_COUNT}-${FIT_ID}.log"
echo "log: $LOG"
"$PYTHON" "$RUNNER" \
  --model-id "$MODEL_ID" \
  --sample-count "$SAMPLE_COUNT" \
  --fit-id "$FIT_ID" \
  ${RESUME:+--resume} 2>&1 | tee "$LOG"
