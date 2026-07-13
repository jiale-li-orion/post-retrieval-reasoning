#!/usr/bin/env python3
"""Render Hard decision-program drafts for human review before trajectories."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = EXPERIMENT_ROOT.parents[1]
if str(EXPERIMENT_ROOT) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_ROOT))

from adapters.atm import ATMAdapter  # noqa: E402
from core.run_contract import create_run_directory  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--programs", type=Path, required=True)
    parser.add_argument("--packet-id", required=True)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("/home/lab/lab/research_artifacts/decision_program_review"),
    )
    parser.add_argument(
        "--atm-root",
        type=Path,
        default=PROJECT_ROOT / "other_repo_references/ATM-Bench",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = create_run_directory(args.output_root / args.packet_id)
    programs = _load_jsonl(args.programs)
    atm = ATMAdapter(args.atm_root)
    hard = {item.qa_id: item for item in atm.load_split("hard")}
    if len(programs) != 31 or set(hard) != {str(row["qa_id"]) for row in programs}:
        raise ValueError("review packet requires exactly the canonical Hard 31")

    editable_path = output / "hard_decision_programs.review.jsonl"
    editable_path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in programs) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Hard 31 Decision-Program Review",
        "",
        "正式 trajectory 前逐题核对。审核完成后，把 JSONL 中每条 "
        "`review_status` 改为 `frozen`；不得在查看 trajectory 后修改。",
        "",
    ]
    by_id = {str(row["qa_id"]): row for row in programs}
    for index, item in enumerate(hard.values(), start=1):
        program = by_id[item.qa_id]
        chunks = atm.collect_sgm_chunks(item.evidence_ids)
        lines.extend(
            [
                f"## {index}. `{item.qa_id}`",
                "",
                f"**Qtype:** `{item.qtype}`",
                "",
                f"**Question:** {item.question}",
                "",
                f"**Gold:** {item.gold_answer}",
                "",
                "**Program draft:**",
                "",
                "```json",
                json.dumps(program, ensure_ascii=False, indent=2),
                "```",
                "",
                "**Oracle evidence:**",
                "",
            ]
        )
        for evidence_id, chunk in zip(item.evidence_ids, chunks, strict=True):
            lines.extend(
                [
                    f"### `{evidence_id}`",
                    "",
                    "```text",
                    chunk,
                    "```",
                    "",
                ]
            )
        lines.extend(
            [
                "**Review checklist:** entities / attributes / operands / "
                "operators / intermediates / bindings / phrase aliases / decoys",
                "",
                "---",
                "",
            ]
        )
    review_path = output / "REVIEW.md"
    review_path.write_text("\n".join(lines), encoding="utf-8")
    manifest = {
        "packet_id": args.packet_id,
        "status": "awaiting_human_review",
        "program_count": len(programs),
        "programs_input_sha256": _sha256(args.programs),
        "editable_programs_sha256": _sha256(editable_path),
        "review_markdown_sha256": _sha256(review_path),
        "hard_split_sha256": atm.split_sha256("hard"),
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(output)
    return 0


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
