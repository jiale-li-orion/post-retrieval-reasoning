#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
ATM_DIR="${ATM_BENCH_ROOT:-${ROOT_DIR}/other_repo_references/ATM-Bench}"
VERBAL_R3_DIR="${VERBAL_R3_ROOT:-${ROOT_DIR}/other_repo_references/VerbalR3}"
EXP_DIR="${ROOT_DIR}/experiments/atm_oracle_evidence_verbal-R3"

PYTHON="${PYTHON:-${ROOT_DIR}/.venv/bin/python3}"
CONFIG="${CONFIG:-${EXP_DIR}/configs/verbal_r3_official.json}"
CONDITION="${CONDITION:-oracle}"
SPLIT="${SPLIT:-hard}"
NIAH_K="${NIAH_K:-}"
ANSWERER_PROVIDER="${ANSWERER_PROVIDER:-vllm}"
ANSWERER_MODEL="${ANSWERER_MODEL:?Set ANSWERER_MODEL}"
ANSWERER_ENDPOINT="${ANSWERER_ENDPOINT:?Set ANSWERER_ENDPOINT}"
ANSWERER_API_KEY="${ANSWERER_API_KEY:?Set ANSWERER_API_KEY}"
JUDGE_MODEL="${JUDGE_MODEL:-gpt-5-mini}"
RUN_ID="${RUN_ID:-$(date +%Y%m%dT%H%M%S)}"
LIMIT="${LIMIT:-}"

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
if [[ ! -f "${VERBAL_R3_DIR}/utils/reranker_server.py" ]]; then
  echo "ERROR: cannot find VerbalR3 repo: ${VERBAL_R3_DIR}" >&2
  echo "Set VERBAL_R3_ROOT=/path/to/VerbalR3 if it lives elsewhere." >&2
  exit 2
fi

case "${SPLIT}" in
  hard) GT_FILE="${ATM_DIR}/data/atm-bench/atm-bench-hard.json" ;;
  full) GT_FILE="${ATM_DIR}/data/atm-bench/atm-bench.json" ;;
  *) echo "ERROR: SPLIT must be hard or full" >&2; exit 2 ;;
esac

EXTRA_ARGS=()
case "${CONDITION}" in
  oracle)
    QA_FILE="${GT_FILE}"
    CONDITION_TAG="oracle"
    ;;
  niah)
    if [[ "${SPLIT}" != "hard" ]]; then
      echo "ERROR: official NIAH pools are available only for SPLIT=hard" >&2
      exit 2
    fi
    case "${NIAH_K}" in
      25|50|100|200) ;;
      *) echo "ERROR: NIAH_K must be 25, 50, 100, or 200" >&2; exit 2 ;;
    esac
    QA_FILE="${ATM_DIR}/data/atm-bench/niah/atm-bench-hard-niah${NIAH_K}.json"
    CONDITION_TAG="niah-${NIAH_K}"
    EXTRA_ARGS+=(--use-niah-pools)
    ;;
  *) echo "ERROR: CONDITION must be oracle or niah" >&2; exit 2 ;;
esac

if [[ -n "${LIMIT}" ]]; then
  EXTRA_ARGS+=(--limit "${LIMIT}")
fi

MODEL_TAG="$(printf '%s' "${ANSWERER_MODEL}" | tr '/: ' '___' | tr -cd '[:alnum:]_.-')"
RUN_DIR="${EXP_DIR}/runs/${CONDITION_TAG}/${SPLIT}/${MODEL_TAG}/${RUN_ID}"
if [[ -e "${RUN_DIR}" ]]; then
  echo "ERROR: run directory already exists: ${RUN_DIR}" >&2
  exit 2
fi
mkdir -p "${RUN_DIR}/eval" "${RUN_DIR}/logs"

PREDICTIONS="${RUN_DIR}/predictions.jsonl"
ANNOTATIONS="${RUN_DIR}/annotations.jsonl"
STATS="${RUN_DIR}/run_stats.json"
MANIFEST="${RUN_DIR}/manifest.json"

ATM_COMMIT="$(git -C "${ATM_DIR}" rev-parse HEAD)"
VERBAL_COMMIT="$(git -C "${VERBAL_R3_DIR}" rev-parse HEAD)"
RERANKER_MODEL="$("${PYTHON}" -c 'import json,sys; print(json.load(open(sys.argv[1]))["reranker"]["model"])' "${CONFIG}")"
RERANKER_REVISION="$("${PYTHON}" -c 'import json,sys; print(json.load(open(sys.argv[1]))["reranker"]["revision"])' "${CONFIG}")"
cat > "${MANIFEST}" <<EOF
{
  "run_id": "${RUN_ID}",
  "condition": "${CONDITION_TAG}",
  "split": "${SPLIT}",
  "qa_file": "${QA_FILE}",
  "qa_sha256": "$(sha256sum "${QA_FILE}" | cut -d' ' -f1)",
  "config": "${CONFIG}",
  "config_sha256": "$(sha256sum "${CONFIG}" | cut -d' ' -f1)",
  "atm_commit": "${ATM_COMMIT}",
  "verbal_r3_commit": "${VERBAL_COMMIT}",
  "verbal_r3_root": "${VERBAL_R3_DIR}",
  "reranker_model": "${RERANKER_MODEL}",
  "reranker_revision": "${RERANKER_REVISION}",
  "python": "${PYTHON}",
  "image_sgm_sha256": "$(sha256sum "${ATM_DIR}/output/image/qwen3vl2b/batch_results.json" | cut -d' ' -f1)",
  "video_sgm_sha256": "$(sha256sum "${ATM_DIR}/output/video/qwen3vl2b/batch_results.json" | cut -d' ' -f1)",
  "email_sha256": "$(sha256sum "${ATM_DIR}/data/raw_memory/email/emails.json" | cut -d' ' -f1)",
  "answerer_provider": "${ANSWERER_PROVIDER}",
  "answerer_model": "${ANSWERER_MODEL}",
  "judge_model": "${JUDGE_MODEL}",
  "started_at": "$(date -Is)"
}
EOF

cd "${ATM_DIR}"
export PYTHONPATH="${ATM_DIR}:${EXP_DIR}/scripts${PYTHONPATH:+:${PYTHONPATH}}"

"${PYTHON}" "${EXP_DIR}/scripts/verbal_r3_oracle.py" \
  --config "${CONFIG}" \
  --verbal-r3-root "${VERBAL_R3_DIR}" \
  --qa-file "${QA_FILE}" \
  --image-batch-results "${ATM_DIR}/output/image/qwen3vl2b/batch_results.json" \
  --video-batch-results "${ATM_DIR}/output/video/qwen3vl2b/batch_results.json" \
  --email-file "${ATM_DIR}/data/raw_memory/email/emails.json" \
  --provider "${ANSWERER_PROVIDER}" \
  --vllm-endpoint "${ANSWERER_ENDPOINT}" \
  --api-key "${ANSWERER_API_KEY}" \
  --model "${ANSWERER_MODEL}" \
  --output-file "${PREDICTIONS}" \
  --annotations-file "${ANNOTATIONS}" \
  --stats-file "${STATS}" \
  "${EXTRA_ARGS[@]}" \
  2>&1 | tee "${RUN_DIR}/logs/inference.log"

"${PYTHON}" memqa/utils/evaluator/evaluate_qa.py \
  --ground-truth "${GT_FILE}" \
  --predictions "${PREDICTIONS}" \
  --output-dir "${RUN_DIR}/eval" \
  --metrics em atm \
  --judge-provider openai \
  --judge-model "${JUDGE_MODEL}" \
  --judge-reasoning-effort minimal \
  --max-workers 2 \
  2>&1 | tee "${RUN_DIR}/logs/eval.log"

"${PYTHON}" "${EXP_DIR}/scripts/finalize_run.py" \
  --stats-file "${STATS}" \
  --eval-dir "${RUN_DIR}/eval"

"${PYTHON}" - "${MANIFEST}" <<'PY'
import json
import sys
from datetime import datetime
from pathlib import Path

path = Path(sys.argv[1])
manifest = json.loads(path.read_text())
manifest["finished_at"] = datetime.now().astimezone().isoformat()
manifest["status"] = "complete"
path.write_text(json.dumps(manifest, indent=2) + "\n")
PY

echo "Run complete: ${RUN_DIR}"
