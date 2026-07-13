#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 5 || $# -gt 6 ]]; then
  echo "usage: $0 CONDITION BEHAVIOR_RUN LENS RUN_ID PROGRAMS [LIMIT]" >&2
  exit 2
fi

CONDITION=$1
BEHAVIOR_RUN=$2
LENS=$3
RUN_ID=$4
PROGRAMS=$5
LIMIT=${6:-}
PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
PYTHON="$PROJECT_ROOT/.venv/bin/python"
ARTIFACT_ROOT=/home/lab/lab/research_artifacts
TARGETS="$ARTIFACT_ROOT/targets/atm-targets-v1/targets.jsonl"
ARGS=(
  --model-id qwen3_vl_2b_instruct
  --condition "$CONDITION"
  --behavior-run "$BEHAVIOR_RUN"
  --lens "$LENS"
  --targets "$TARGETS"
  --decision-programs "$PROGRAMS"
  --run-id "$RUN_ID"
)

if [[ "$CONDITION" == C1 ]]; then
  ARGS+=(--annotation-cache "$ARTIFACT_ROOT/va_cache/oracle-hard/local-v1/annotations.jsonl")
fi
if [[ -n "$LIMIT" ]]; then
  ARGS+=(--limit "$LIMIT" --allow-draft-programs)
fi

cd "$PROJECT_ROOT"
export PYTHONPATH=experiments/post_retrieval_jspace_v1
"$PYTHON" experiments/post_retrieval_jspace_v1/readout/run_atm_readout.py "${ARGS[@]}"
