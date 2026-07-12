#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 4 ]]; then
  echo "usage: $0 MODEL_ID FIT_256_ID FIT_512_ID EVALUATION_ID" >&2
  exit 2
fi

MODEL_ID=$1
FIT_256_ID=$2
FIT_512_ID=$3
EVALUATION_ID=$4
PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
PYTHON="$PROJECT_ROOT/.venv/bin/python"
ARTIFACT_ROOT=/home/lab/lab/research_artifacts
FIT_ROOT="$ARTIFACT_ROOT/jlens_fits/$MODEL_ID"

if pgrep -af '[f]it_jlens.py|[r]un_behavior.py|[g]enerate_va_cache.py' >/dev/null; then
  echo "refusing to run stability while a GPU experiment is active" >&2
  exit 1
fi

for fit_id in "$FIT_256_ID" "$FIT_512_ID"; do
  manifest="$FIT_ROOT/$fit_id/manifest.json"
  if [[ ! -f "$manifest" ]] || ! grep -q '"status": "complete"' "$manifest"; then
    echo "fit is not complete: $FIT_ROOT/$fit_id" >&2
    exit 1
  fi
done

cd "$PROJECT_ROOT"
export PYTHONPATH=experiments/post_retrieval_jspace_v1
"$PYTHON" experiments/post_retrieval_jspace_v1/jacobian_analysis/evaluate_stability.py \
  --model-id "$MODEL_ID" \
  --lens-256 "$FIT_ROOT/$FIT_256_ID/lens.pt" \
  --lens-512 "$FIT_ROOT/$FIT_512_ID/lens.pt" \
  --evaluation-id "$EVALUATION_ID"
