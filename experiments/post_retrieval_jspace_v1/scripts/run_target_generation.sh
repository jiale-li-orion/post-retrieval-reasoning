#!/usr/bin/env bash
set -euo pipefail

if [[ $# -gt 1 ]]; then
  echo "usage: $0 [TARGET_ID]" >&2
  exit 2
fi
TARGET_ID=${1:-atm-targets-v1}
PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
ARTIFACT_ROOT=${RESEARCH_ARTIFACT_ROOT:-/home/lab/lab/research_artifacts}
PYTHON="$PROJECT_ROOT/.venv/bin/python"
RUNNER="$PROJECT_ROOT/experiments/post_retrieval_jspace_v1/targets/generate_targets.py"
[[ -x "$PYTHON" ]] || { echo "project environment missing: $PYTHON" >&2; exit 1; }
cd "$PROJECT_ROOT"
export PYTHONPATH=experiments/post_retrieval_jspace_v1
exec "$PYTHON" "$RUNNER" \
  --target-id "$TARGET_ID" \
  --output-root "$ARTIFACT_ROOT/targets"
