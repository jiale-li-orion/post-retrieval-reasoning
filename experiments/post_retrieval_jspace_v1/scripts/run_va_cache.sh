#!/usr/bin/env bash
set -euo pipefail

if [[ $# -gt 1 ]]; then
  echo "usage: $0 [CACHE_ID]" >&2
  exit 2
fi

CACHE_ID=${1:-canonical-e1-v1}
PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
PYTHON="$PROJECT_ROOT/.venv/bin/python"
RUNNER="$PROJECT_ROOT/experiments/post_retrieval_jspace_v1/interventions/generate_va_cache.py"
ARTIFACT_ROOT=${RESEARCH_ARTIFACT_ROOT:-/home/lab/lab/research_artifacts}
OUTPUT="$ARTIFACT_ROOT/va_cache/canonical-e1/$CACHE_ID"
LOCK="$ARTIFACT_ROOT/.gpu-experiment.lock"
LOG="$ARTIFACT_ROOT/logs/va-cache-${CACHE_ID}.log"

[[ -x "$PYTHON" ]] || { echo "project environment missing: $PYTHON" >&2; exit 1; }
[[ ! -e "$OUTPUT" ]] || { echo "refusing to overwrite cache: $OUTPUT" >&2; exit 1; }
mkdir -p "$ARTIFACT_ROOT/logs"

exec 9>"$LOCK"
flock -n 9 || { echo "GPU experiment lock is already held: $LOCK" >&2; exit 1; }
if pgrep -af '[f]it_jlens.py|[r]un_behavior.py|[g]enerate_va_cache.py' >/dev/null; then
  echo "refusing to overlap an active GPU experiment" >&2
  pgrep -af '[f]it_jlens.py|[r]un_behavior.py|[g]enerate_va_cache.py' >&2
  exit 1
fi

cd "$PROJECT_ROOT"
export PYTHONPATH=experiments/post_retrieval_jspace_v1
echo "log: $LOG"
"$PYTHON" "$RUNNER" \
  --scope canonical-e1 \
  --cache-id "$CACHE_ID" 2>&1 | tee "$LOG"

