#!/usr/bin/env python3
"""Audit which reviewed decision targets vanilla token J-lens can express."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def classify_text_target(text: str, tokenizer: Any, *, sequence_level: bool) -> str:
    canonical = tokenizer.encode(str(text), add_special_tokens=False)
    if len(canonical) == 1:
        return "A"
    aliases = {
        tuple(tokenizer.encode(variant, add_special_tokens=False))
        for variant in _alias_variants(str(text))
    }
    if any(len(alias) == 1 for alias in aliases):
        return "B"
    return "D" if sequence_level else "C"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--programs", type=Path, required=True)
    parser.add_argument("--tokenizer", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--threshold", type=float, default=0.70)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.output_dir.exists():
        raise FileExistsError(f"refusing to overwrite: {args.output_dir}")
    args.output_dir.mkdir(parents=True)
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer, local_files_only=True)
    programs = _load_jsonl(args.programs)
    rows = []
    covered_questions = set()
    for program in programs:
        qa_id = str(program["qa_id"])
        candidates = _target_candidates(program)
        for candidate in candidates:
            category = (
                "E"
                if candidate["family"] == "binding"
                else classify_text_target(
                    candidate["text"],
                    tokenizer,
                    sequence_level=bool(candidate["sequence_level"]),
                )
                if candidate["text"]
                else "F"
            )
            row = {"qa_id": qa_id, **candidate, "category": category}
            rows.append(row)
            if candidate["family"] in {"gold", "operand", "intermediate"} and category in {"A", "B"}:
                covered_questions.add(qa_id)
    coverage = len(covered_questions) / len(programs) if programs else 0.0
    summary = {
        "program_count": len(programs),
        "target_count": len(rows),
        "category_counts": dict(Counter(row["category"] for row in rows)),
        "mechanism_question_coverage": coverage,
        "threshold": args.threshold,
        "phrase_sequence_extension_triggered": coverage < args.threshold,
        "boundary": (
            "Categories C-F are not negative evidence for representation absence; "
            "first-token rank is not an allowed replacement."
        ),
    }
    (args.output_dir / "targets.jsonl").write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(args.output_dir)
    return 0


def _target_candidates(program: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for target in program.get("targets", []):
        result.append(
            {
                "target_id": str(target.get("target_id", "gold")),
                "family": "gold",
                "text": str(target.get("text", "")),
                "sequence_level": program.get("qtype") == "list_recall",
            }
        )
    for family, id_key in (("operand", "operand_id"), ("intermediate", "intermediate_id")):
        for index, item in enumerate(program.get(f"{family}s", [])):
            text = item.get("value", item.get("text", "")) if isinstance(item, dict) else str(item)
            target_id = item.get(id_key, f"{family}_{index}") if isinstance(item, dict) else f"{family}_{index}"
            result.append(
                {
                    "target_id": str(target_id),
                    "family": family,
                    "text": str(text),
                    "sequence_level": False,
                }
            )
    for index, item in enumerate(program.get("bindings", [])):
        result.append(
            {
                "target_id": f"binding_{index}",
                "family": "binding",
                "text": json.dumps(item, ensure_ascii=False) if isinstance(item, dict) else str(item),
                "sequence_level": False,
            }
        )
    return result


def _alias_variants(text: str) -> list[str]:
    return list(dict.fromkeys([text, f" {text}", text.lower(), f" {text.lower()}", text.capitalize(), f" {text.capitalize()}"]))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


if __name__ == "__main__":
    raise SystemExit(main())
