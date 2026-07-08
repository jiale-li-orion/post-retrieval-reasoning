#!/usr/bin/env bash
set -euo pipefail

# Evidence View Realization — ATM-Bench Oracle SGM
#
# Usage:
#   bash run_experiments.sh              # Hard set only (default)
#   bash run_experiments.sh full          # Full set + Hard
#
# Prerequisites:
#   - vLLM serving Qwen/Qwen3-VL-8B-Instruct-FP8 at VLLM_ENDPOINT
#   - ATM-Bench data downloaded (bash scripts/download_data.sh)
#   - conda env with pip install -r requirements.txt && pip install -e .
#
# Env overrides:
#   VLLM_ENDPOINT    (default: http://127.0.0.1:8000/v1/chat/completions)
#   TEMPERATURE      (default: 0, deterministic)
#   ATM_BENCH_ROOT   (default: ./ATM-Bench or .)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="${ATM_BENCH_ROOT:-${SCRIPT_DIR}}"
if [ ! -d "${REPO_ROOT}/memqa" ]; then
  REPO_ROOT="${SCRIPT_DIR}/ATM-Bench"
fi
if [ ! -d "${REPO_ROOT}/memqa" ]; then
  echo "ERROR: cannot find ATM-Bench repo (set ATM_BENCH_ROOT or run from repo parent)"
  echo "  Tried: ${ATM_BENCH_ROOT:-${SCRIPT_DIR}}"
  echo "  Tried: ${SCRIPT_DIR}/ATM-Bench"
  exit 1
fi

cd "${REPO_ROOT}"

VLLM_ENDPOINT="${VLLM_ENDPOINT:-http://127.0.0.1:8000/v1/chat/completions}"
TEMPERATURE="${TEMPERATURE:-0}"
MAX_WORKERS="${MAX_WORKERS:-8}"
TIMEOUT="${TIMEOUT:-120}"

ANSWERER_MODEL="Qwen/Qwen3-VL-8B-Instruct-FP8"
BATCH_FIELDS="type,timestamp,location,short_caption,caption,ocr,tags"

QA_FILE_HARD="./data/atm-bench/atm-bench-hard.json"
QA_FILE_FULL="./data/atm-bench/atm-bench.json"
IMAGE_BATCH="./output/image/qwen3vl2b/batch_results.json"
VIDEO_BATCH="./output/video/qwen3vl2b/batch_results.json"
EMAIL_FILE="./data/raw_memory/email/emails.json"

OUTPUT_BASE="output/QA_Agent/Oracle/qwen3vl8b_SGM"

# ---- Prerequisite checks ----
echo "====================================="
echo " Evidence View — ATM Oracle SGM"
echo "====================================="
echo "REPO:       ${REPO_ROOT}"
echo "VLLM:       ${VLLM_ENDPOINT}"
echo "TEMPERATURE: ${TEMPERATURE}"
echo ""

# Check vLLM endpoint
if ! curl -sf --connect-timeout 3 --max-time 5 "${VLLM_ENDPOINT}" -o /dev/null 2>/dev/null; then
  echo "WARNING: vLLM endpoint not reachable at ${VLLM_ENDPOINT}"
  echo "  Start vLLM: vllm serve ${ANSWERER_MODEL} --port 8000 --max-model-len 32768 --dtype float16 &"
  echo ""
fi

# Check data files
missing=0
for f in "${QA_FILE_HARD}" "${IMAGE_BATCH}" "${VIDEO_BATCH}" "${EMAIL_FILE}"; do
  if [ ! -f "$f" ]; then
    echo "MISSING: $f"
    missing=1
  fi
done
if [ "$missing" -ne 0 ]; then
  echo "ERROR: missing data files — run bash scripts/download_data.sh first"
  exit 1
fi

# ---- Helper ----
oracle_sgm() {
  local qa_file="$1"
  local output_file="$2"
  local tag="$3"

  mkdir -p "$(dirname "${output_file}")"

  echo ""
  echo "--- Oracle SGM: ${tag} ---"
  echo "  QA:    ${qa_file}"
  echo "  Out:   ${output_file}"
  echo "  Start: $(date)"

  python memqa/qa_agent_baselines/oracle/oracle_baseline.py \
    --qa-file "${qa_file}" \
    --media-source batch_results \
    --batch-fields "${BATCH_FIELDS}" \
    --image-batch-results "${IMAGE_BATCH}" \
    --video-batch-results "${VIDEO_BATCH}" \
    --email-file "${EMAIL_FILE}" \
    --provider vllm \
    --vllm-endpoint "${VLLM_ENDPOINT}" \
    --model "${ANSWERER_MODEL}" \
    --temperature "${TEMPERATURE}" \
    --max-workers "${MAX_WORKERS}" \
    --timeout "${TIMEOUT}" \
    --output-file "${output_file}"

  echo "  Done:  $(date)"
  echo "  Lines: $(wc -l < "${output_file}") predictions"
}

# ---- Run ----
MODE="${1:-hard}"

if [ "${MODE}" = "hard" ] || [ "${MODE}" = "all" ]; then
  PRED_HARD="${OUTPUT_BASE}/hard/oracle_qwen3vl8b_SGM.jsonl"
  oracle_sgm "${QA_FILE_HARD}" "${PRED_HARD}" "Hard (31 QA)"
fi

if [ "${MODE}" = "full" ] || [ "${MODE}" = "all" ]; then
  PRED_FULL="${OUTPUT_BASE}/atmbench/oracle_qwen3vl8b_SGM.jsonl"
  oracle_sgm "${QA_FILE_FULL}" "${PRED_FULL}" "Full (1013 QA)"
fi

echo ""
echo "====================================="
echo " All done!"
echo " Predictions:"
find "${OUTPUT_BASE}" -name "*.jsonl" 2>/dev/null | sort
echo "====================================="
