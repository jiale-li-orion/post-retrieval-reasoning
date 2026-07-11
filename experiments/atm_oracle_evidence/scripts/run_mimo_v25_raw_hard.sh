#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
ATM_DIR="${ATM_BENCH_ROOT:-${ROOT_DIR}/other_repo_references/ATM-Bench}"
RUN_DIR="${ROOT_DIR}/experiments/atm_oracle_evidence/runs/mimo_v25_raw_hard"
PYTHON="${PYTHON:-${ROOT_DIR}/.venv/bin/python3}"

MODEL="${MIMO_MODEL:-mimo-v2.5}"
TAG="${TAG:-mimo_v25_raw_hard}"
MAX_WORKERS="${MAX_WORKERS:-1}"
TIMEOUT="${TIMEOUT:-120}"
JUDGE_MODEL="${JUDGE_MODEL:-gpt-5-mini}"

if [[ -z "${MIMO_API_KEY:-}" ]]; then
  echo "ERROR: MIMO_API_KEY is required and must be supplied via environment variable." >&2
  exit 2
fi
if [[ ! -x "${PYTHON}" ]]; then
  echo "ERROR: Python interpreter not found or not executable: ${PYTHON}" >&2
  echo "Set PYTHON=/path/to/python or create the project venv at ${ROOT_DIR}/.venv" >&2
  exit 2
fi
if [[ ! -d "${ATM_DIR}/memqa" ]]; then
  echo "ERROR: cannot find ATM-Bench repo: ${ATM_DIR}" >&2
  echo "Set ATM_BENCH_ROOT=/path/to/ATM-Bench if it lives elsewhere." >&2
  exit 2
fi

if ! command -v ffmpeg >/dev/null 2>&1 || ! command -v ffprobe >/dev/null 2>&1; then
  echo "ERROR: Oracle raw mode requires ffmpeg and ffprobe for official video frame extraction." >&2
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
  echo "media_source=raw"
  echo "split=atm-bench-hard"
  echo "qa_file=data/atm-bench/atm-bench-hard.json"
  echo "predictions=${RUN_DIR}/predictions/oracle_${TAG}.jsonl"
  echo "eval_dir=${RUN_DIR}/eval"
  echo "max_workers=${MAX_WORKERS}"
  echo "timeout=${TIMEOUT}"
  echo "judge_model=${JUDGE_MODEL}"
  echo "endpoint=${MIMO_ENDPOINT}"
  echo "python=${PYTHON}"
} > "${RUN_DIR}/manifest.env"

cd "${ATM_DIR}"
export PYTHONPATH="${ATM_DIR}${PYTHONPATH:+:${PYTHONPATH}}"

"${PYTHON}" memqa/qa_agent_baselines/oracle/oracle_baseline.py \
  --qa-file "./data/atm-bench/atm-bench-hard.json" \
  --media-source raw \
  --image-batch-results "./output/image/qwen3vl2b/batch_results.json" \
  --video-batch-results "./output/video/qwen3vl2b/batch_results.json" \
  --image-root "./data/raw_memory/image" \
  --video-root "./data/raw_memory/video" \
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

"${PYTHON}" memqa/utils/evaluator/evaluate_qa.py \
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
