#!/usr/bin/env python3
"""Generate immutable Full targets and unreviewed Hard decision programs."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from transformers import AutoTokenizer

EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = EXPERIMENT_ROOT.parents[1]
if str(EXPERIMENT_ROOT) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_ROOT))

from adapters.atm import ATMAdapter  # noqa: E402
from core.registry import load_model_registry  # noqa: E402
from core.run_contract import create_run_directory, sanitize_manifest  # noqa: E402
from targets.builder import build_decision_program_draft, build_target_rows  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-id", default="atm-targets-v1")
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument(
        "--atm-root",
        type=Path,
        default=PROJECT_ROOT / "other_repo_references/ATM-Bench",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    models = load_model_registry(EXPERIMENT_ROOT / "registry/model_registry.yaml")
    tokenizers = {
        model_id: AutoTokenizer.from_pretrained(
            spec["local_path"], local_files_only=True, trust_remote_code=True
        )
        for model_id, spec in models.items()
    }
    atm = ATMAdapter(args.atm_root)
    full = atm.load_split("full")
    hard = atm.load_split("hard")
    output = create_run_directory(args.output_root / args.target_id)
    targets_path = output / "targets.jsonl"
    programs_path = output / "hard_decision_programs.draft.jsonl"
    target_count = 0
    program_count = 0
    with (
        targets_path.open("x", encoding="utf-8") as target_handle,
        programs_path.open("x", encoding="utf-8") as program_handle,
    ):
        for item in full:
            chunks = atm.collect_sgm_chunks(item.evidence_ids)
            targets = build_target_rows(
                gold_answer=item.gold_answer,
                qtype=item.qtype,
                evidence_chunks=chunks,
                tokenizers=tokenizers,
            )
            row = {
                "qa_id": item.qa_id,
                "qtype": item.qtype,
                "gold_answer": item.gold_answer,
                "evidence_ids": list(item.evidence_ids),
                "targets": targets,
            }
            target_handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            target_count += 1
        for item in hard:
            chunks = atm.collect_sgm_chunks(item.evidence_ids)
            targets = build_target_rows(
                gold_answer=item.gold_answer,
                qtype=item.qtype,
                evidence_chunks=chunks,
                tokenizers=tokenizers,
            )
            program = build_decision_program_draft(
                qa_id=item.qa_id,
                qtype=item.qtype,
                gold_answer=item.gold_answer,
                evidence_ids=item.evidence_ids,
                targets=targets,
            )
            program["targets"] = targets
            program_handle.write(json.dumps(program, ensure_ascii=False) + "\n")
            program_count += 1

    if target_count != 1013 or program_count != 31:
        raise ValueError(
            f"ATM target counts changed: Full={target_count}, Hard={program_count}"
        )
    model_contract = {
        model_id: {
            "repository": spec["repository"],
            "revision": spec["revision"],
            "file_manifest_sha256": spec["file_manifest_sha256"],
        }
        for model_id, spec in models.items()
    }
    manifest = sanitize_manifest(
        {
            "target_id": args.target_id,
            "status": "complete",
            "project_commit": _git_commit(PROJECT_ROOT),
            "target_count": target_count,
            "hard_program_count": program_count,
            "hard_review_status": "draft",
            "models": model_contract,
            "dataset": {
                "full_sha256": atm.split_sha256("full"),
                "hard_sha256": atm.split_sha256("hard"),
            },
            "targets_sha256": _sha256(targets_path),
            "hard_programs_sha256": _sha256(programs_path),
            "created_at": datetime.now().astimezone().isoformat(),
        }
    )
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(output)
    return 0


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_commit(root: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()


if __name__ == "__main__":
    raise SystemExit(main())
