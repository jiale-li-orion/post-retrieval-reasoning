#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
RUNNER="$PROJECT_ROOT/experiments/post_retrieval_jspace_v1/scripts/run_behavior_queue.sh"
ARTIFACT_ROOT=${RESEARCH_ARTIFACT_ROOT:-/home/lab/lab/research_artifacts}
APPROVAL="$ARTIFACT_ROOT/approvals/gate-qwen3-vl-2b-stability/manifest.json"
[[ -f "$APPROVAL" ]] || { echo "stability approval is required: $APPROVAL" >&2; exit 1; }
SHARDS=${E1_FULL_SHARDS:-8}

MODELS=(
  qwen3_8b_ms
  deepseek_r1_distill_llama_8b
  qwen2_5_7b_instruct
  qwen3_vl_2b_instruct
  qwen3_vl_8b_instruct
)
for model in "${MODELS[@]}"; do
  for condition in C0 C1; do
    "$RUNNER" "$model" "$condition" full "e1-full-${model}-${condition}-v1" "$SHARDS"
  done
done
