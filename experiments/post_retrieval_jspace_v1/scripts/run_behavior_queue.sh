#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 4 || $# -gt 5 ]]; then
  echo "usage: $0 MODEL_ID CONDITION SPLIT RUN_FAMILY [NUM_SHARDS]" >&2
  exit 2
fi

MODEL_ID=$1
CONDITION=$2
SPLIT=$3
RUN_FAMILY=$4
NUM_SHARDS=${5:-1}
case "$CONDITION" in C0|C1|C3|C4|C5|C6|C7|C8|C9|C10) ;; *) echo "unsupported condition: $CONDITION" >&2; exit 2 ;; esac
case "$SPLIT" in full|hard) ;; *) echo "split must be full or hard" >&2; exit 2 ;; esac
[[ "$NUM_SHARDS" =~ ^[1-9][0-9]*$ ]] || { echo "NUM_SHARDS must be positive" >&2; exit 2; }

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
PYTHON="$PROJECT_ROOT/.venv/bin/python"
RUNNER="$PROJECT_ROOT/experiments/post_retrieval_jspace_v1/behavior/run_behavior.py"
MERGER="$PROJECT_ROOT/experiments/post_retrieval_jspace_v1/behavior/merge_shards.py"
ARTIFACT_ROOT=${RESEARCH_ARTIFACT_ROOT:-/home/lab/lab/research_artifacts}
RUN_ROOT="$ARTIFACT_ROOT/runs"
LOCK="$ARTIFACT_ROOT/.gpu-experiment.lock"
LOG="$ARTIFACT_ROOT/logs/behavior-${RUN_FAMILY}.log"
VA_CACHE=${VA_CACHE_PATH:-$ARTIFACT_ROOT/va_cache/canonical-e1/canonical-e1-v1/annotations.jsonl}

[[ -x "$PYTHON" ]] || { echo "project environment missing: $PYTHON" >&2; exit 1; }
if [[ "$CONDITION" =~ ^C(1|7|8|9|10)$ && ! -f "$VA_CACHE" ]]; then
  echo "canonical VA cache missing: $VA_CACHE" >&2
  exit 1
fi
mkdir -p "$ARTIFACT_ROOT/logs"

exec 9>"$LOCK"
flock -n 9 || { echo "GPU experiment lock is already held: $LOCK" >&2; exit 1; }
if pgrep -af '[f]it_jlens.py|[r]un_behavior.py|[g]enerate_va_cache.py' >/dev/null; then
  echo "refusing to overlap an active GPU experiment" >&2
  exit 1
fi

cd "$PROJECT_ROOT"
export PYTHONPATH=experiments/post_retrieval_jspace_v1
exec > >(tee -a "$LOG") 2>&1

SHARD_DIRS=()
for ((index=0; index<NUM_SHARDS; index++)); do
  RUN_ID="${RUN_FAMILY}-shard-${index}-of-${NUM_SHARDS}"
  RUN_DIR="$RUN_ROOT/$CONDITION/$SPLIT/$MODEL_ID/$RUN_ID"
  SHARD_DIRS+=("$RUN_DIR")
  RESUME=()
  if [[ -f "$RUN_DIR/manifest.json" ]]; then
    STATUS=$("$PYTHON" -c 'import json,sys; print(json.load(open(sys.argv[1]))["status"])' "$RUN_DIR/manifest.json")
    case "$STATUS" in
      complete) echo "skip complete shard: $RUN_ID"; continue ;;
      running) RESUME=(--resume) ;;
      *) echo "refusing inconsistent shard status $STATUS: $RUN_DIR" >&2; exit 1 ;;
    esac
  elif [[ -e "$RUN_DIR" ]]; then
    echo "refusing shard directory without manifest: $RUN_DIR" >&2
    exit 1
  fi

  ANNOTATION=()
  [[ "$CONDITION" =~ ^C(1|7|8|9|10)$ ]] && ANNOTATION=(--annotation-cache "$VA_CACHE")
  "$PYTHON" "$RUNNER" \
    --model-id "$MODEL_ID" --condition "$CONDITION" --split "$SPLIT" \
    --run-id "$RUN_ID" --run-root "$RUN_ROOT" \
    --shard-index "$index" --num-shards "$NUM_SHARDS" \
    "${ANNOTATION[@]}" "${RESUME[@]}"
done

MERGED="$RUN_ROOT/$CONDITION/$SPLIT/$MODEL_ID/${RUN_FAMILY}-merged"
[[ ! -e "$MERGED" ]] || { echo "refusing to overwrite merged run: $MERGED" >&2; exit 1; }
MERGE_ARGS=()
for shard_dir in "${SHARD_DIRS[@]}"; do MERGE_ARGS+=(--shard-dir "$shard_dir"); done
"$PYTHON" "$MERGER" "${MERGE_ARGS[@]}" --output-dir "$MERGED"

