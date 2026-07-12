#!/usr/bin/env bash
set -euo pipefail

ARTIFACT_ROOT=/home/lab/lab/research_artifacts
echo "Active J-lens processes:"
pgrep -af '[f]it_jlens.py' || echo "none"
echo
echo "Fit manifests:"
find "$ARTIFACT_ROOT/jlens_fits" -mindepth 3 -maxdepth 3 -name manifest.json \
  -print0 2>/dev/null | sort -z | while IFS= read -r -d '' manifest; do
    python3 - "$manifest" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
row = json.loads(path.read_text())
print(
    f"{path.parent}: status={row.get('status')} "
    f"n={row.get('n_prompts', row.get('sample_count'))} "
    f"lens={row.get('lens_sha256', 'pending')}"
)
PY
  done
echo
echo "Latest progress:"
for log in "$ARTIFACT_ROOT"/logs/jlens-*.log; do
  [[ -f "$log" ]] || continue
  printf '%s: ' "$(basename "$log")"
  grep 'prompt [0-9]' "$log" | tail -1 || echo "no prompt completed"
done
