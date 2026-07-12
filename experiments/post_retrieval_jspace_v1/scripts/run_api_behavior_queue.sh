#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "usage: $0 PROVIDER_ID VA_CACHE_PATH RUN_FAMILY" >&2
  echo "providers: mimo_v25, minimax_m3, kimi_k25" >&2
  exit 2
fi
PROVIDER=$1
VA_CACHE=$2
RUN_FAMILY=$3
case "$PROVIDER" in mimo_v25|minimax_m3|kimi_k25) ;; *) echo "unknown provider: $PROVIDER" >&2; exit 2 ;; esac
[[ -f "$VA_CACHE" ]] || { echo "VA cache missing: $VA_CACHE" >&2; exit 1; }

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
PYTHON="$PROJECT_ROOT/.venv/bin/python"
RUNNER="$PROJECT_ROOT/experiments/post_retrieval_jspace_v1/behavior/run_api_behavior.py"
RUN_ROOT=${API_RUN_ROOT:-$PROJECT_ROOT/research_artifacts/api_runs}
[[ -x "$PYTHON" ]] || { echo "project environment missing: $PYTHON" >&2; exit 1; }

cd "$PROJECT_ROOT"
export PYTHONPATH=experiments/post_retrieval_jspace_v1
for condition in C1 C7 C8 C9 C10; do
  RUN_ID="${RUN_FAMILY}-${condition}"
  RUN_DIR="$RUN_ROOT/$condition/hard/$PROVIDER/$RUN_ID"
  RESUME=()
  if [[ -f "$RUN_DIR/manifest.json" ]]; then
    STATUS=$("$PYTHON" -c 'import json,sys; print(json.load(open(sys.argv[1]))["status"])' "$RUN_DIR/manifest.json")
    case "$STATUS" in
      complete) echo "skip complete API run: $RUN_ID"; continue ;;
      running) RESUME=(--resume) ;;
      *) echo "refusing inconsistent API run: $RUN_DIR" >&2; exit 1 ;;
    esac
  elif [[ -e "$RUN_DIR" ]]; then
    echo "refusing API directory without manifest: $RUN_DIR" >&2
    exit 1
  fi
  "$PYTHON" "$RUNNER" \
    --provider "$PROVIDER" --condition "$condition" --run-id "$RUN_ID" \
    --annotation-cache "$VA_CACHE" --run-root "$RUN_ROOT" \
    "${RESUME[@]}"
done
