#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "usage: $0 MODEL_ID DIM_BATCH PROBE_ID" >&2
  exit 2
fi
MODEL_ID=$1
DIM_BATCH=$2
PROBE_ID=$3
[[ "$DIM_BATCH" =~ ^[1-9][0-9]*$ ]] || { echo "DIM_BATCH must be positive" >&2; exit 2; }

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
PYTHON="$PROJECT_ROOT/.venv/bin/python"
RUNNER="$PROJECT_ROOT/experiments/post_retrieval_jspace_v1/jacobian_analysis/probe_jlens_resources.py"
ARTIFACT_ROOT=${RESEARCH_ARTIFACT_ROOT:-/home/lab/lab/research_artifacts}
LOCK="$ARTIFACT_ROOT/.gpu-experiment.lock"
LOG="$ARTIFACT_ROOT/logs/jlens-probe-${MODEL_ID}-db${DIM_BATCH}-${PROBE_ID}.log"
OUTPUT="$ARTIFACT_ROOT/jlens_resource_probes/$MODEL_ID/$PROBE_ID"

[[ -x "$PYTHON" ]] || { echo "project environment missing: $PYTHON" >&2; exit 1; }
[[ ! -e "$OUTPUT" ]] || { echo "refusing to overwrite probe: $OUTPUT" >&2; exit 1; }
mkdir -p "$ARTIFACT_ROOT/logs"
exec 9>"$LOCK"
flock -n 9 || { echo "GPU experiment lock is already held" >&2; exit 1; }
if pgrep -af '[f]it_jlens.py|[p]robe_jlens_resources.py|[r]un_behavior.py|[g]enerate_va_cache.py' >/dev/null; then
  echo "refusing to overlap an active GPU experiment" >&2
  exit 1
fi

cd "$PROJECT_ROOT"
export PYTHONPATH=experiments/post_retrieval_jspace_v1
"$PYTHON" "$RUNNER" \
  --model-id "$MODEL_ID" --dim-batch "$DIM_BATCH" --probe-id "$PROBE_ID" \
  2>&1 | tee "$LOG"
