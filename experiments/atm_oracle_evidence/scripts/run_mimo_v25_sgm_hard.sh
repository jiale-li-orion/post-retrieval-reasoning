#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
ATM_DIR="${ROOT_DIR}/ATM-Bench"
RUN_DIR="${ROOT_DIR}/experiments/atm_oracle_evidence/runs/mimo_v25_sgm_hard"

MODEL="${MIMO_MODEL:-mimo-v2.5}"
TAG="${TAG:-mimo_v25_sgm_hard}"
MAX_WORKERS="${MAX_WORKERS:-1}"
TIMEOUT="${TIMEOUT:-120}"
JUDGE_MODEL="${JUDGE_MODEL:-gpt-5-mini}"

if [[ -z "${MIMO_API_KEY:-}" ]]; then
  echo "ERROR: MIMO_API_KEY is required and must be supplied via environment variable." >&2
  exit 2
fi

if [[ -z "${MIMO_ENDPOINT:-}" ]]; then
  if [[ -n "${MIMO_BASE_URL:-}" ]]; then
    MIMO_ENDPOINT="${MIMO_BASE_URL%/}/chat/completions"
  else
    MIMO_ENDPOINT="https://api.xiaomimimo.com/v1/chat/completions"
  fi
fi

mkdir -p "${RUN_DIR}/predictions" "${RUN_DIR}/eval" "${RUN_DIR}/logs"

{
  echo "run_id=${TAG}"
  echo "started_at=$(date -Is)"
  echo "model=${MODEL}"
  echo "media_source=batch_results"
  echo "split=atm-bench-hard"
  echo "qa_file=data/atm-bench/atm-bench-hard.json"
  echo "predictions=${RUN_DIR}/predictions/oracle_${TAG}.jsonl"
  echo "eval_dir=${RUN_DIR}/eval"
  echo "max_workers=${MAX_WORKERS}"
  echo "timeout=${TIMEOUT}"
  echo "judge_model=${JUDGE_MODEL}"
  echo "endpoint=${MIMO_ENDPOINT}"
} > "${RUN_DIR}/manifest.env"

cd "${ATM_DIR}"
export PYTHONPATH="${ATM_DIR}${PYTHONPATH:+:${PYTHONPATH}}"

python memqa/qa_agent_baselines/oracle/oracle_baseline.py \
  --qa-file "./data/atm-bench/atm-bench-hard.json" \
  --media-source batch_results \
  --batch-fields "type,timestamp,location,short_caption,caption,ocr,tags" \
  --image-batch-results "./output/image/qwen3vl2b/batch_results.json" \
  --video-batch-results "./output/video/qwen3vl2b/batch_results.json" \
  --email-file "./data/raw_memory/email/emails.json" \
  --provider vllm \
  --vllm-endpoint "${MIMO_ENDPOINT}" \
  --api-key "${MIMO_API_KEY}" \
  --model "${MODEL}" \
  --max-workers "${MAX_WORKERS}" \
  --thinking disabled \
  --timeout "${TIMEOUT}" \
  --output-file "${RUN_DIR}/predictions/oracle_${TAG}.jsonl" \
  2>&1 | tee "${RUN_DIR}/logs/oracle.log"

python memqa/utils/evaluator/evaluate_qa.py \
  --ground-truth "./data/atm-bench/atm-bench-hard.json" \
  --predictions "${RUN_DIR}/predictions/oracle_${TAG}.jsonl" \
  --output-dir "${RUN_DIR}/eval" \
  --metrics em atm \
  --judge-provider openai \
  --judge-model "${JUDGE_MODEL}" \
  --judge-reasoning-effort minimal \
  --max-workers 2 \
  2>&1 | tee "${RUN_DIR}/logs/eval.log"

echo "finished_at=$(date -Is)" >> "${RUN_DIR}/manifest.env"
