#!/usr/bin/env python3
"""Create a paired C0/C1 behavior audit from frozen ATM outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Sequence


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
if str(EXPERIMENT_ROOT) in sys.path:
    sys.path.remove(str(EXPERIMENT_ROOT))
sys.path.insert(0, str(EXPERIMENT_ROOT))

from core.run_contract import create_run_directory  # noqa: E402


def correctness_transition(c0_score: float, c1_score: float) -> str:
    left, right = float(c0_score) == 1.0, float(c1_score) == 1.0
    if left and right:
        return "stable_success"
    if not left and right:
        return "repair"
    if left and not right:
        return "degradation"
    return "stable_failure"


def behavior_stratum(
    c0_abstention: bool,
    c1_abstention: bool,
    c0_score: float,
    c1_score: float,
) -> str:
    left, right = float(c0_score), float(c1_score)
    if c0_abstention and c1_abstention:
        return "stable_abstention"
    if c0_abstention and not c1_abstention:
        return "abstention_exit"
    if not c0_abstention and c1_abstention:
        if right < left and left == 1.0:
            return "correct_to_abstain"
        if right < left and 0.0 < left < 1.0:
            return "partial_to_abstain"
        if left == 0.0 and right == 0.0:
            return "error_to_abstain"
        return "abstention_without_score_harm"
    if right < left:
        return "non_abstention_degradation"
    if right > left:
        return "behavioral_repair"
    return "stable_non_abstention"


def summarize_scores(scores: Sequence[float]) -> dict[str, float | int]:
    values = [float(score) for score in scores]
    return {
        "count": len(values),
        "mean": statistics.fmean(values) if values else 0.0,
        "perfect": sum(score == 1.0 for score in values),
    }


def list_precision_recall(
    ground_truth_items: set[str], prediction_items: set[str]
) -> tuple[float, float]:
    overlap = len(ground_truth_items & prediction_items)
    precision = overlap / len(prediction_items) if prediction_items else 0.0
    recall = overlap / len(ground_truth_items) if ground_truth_items else 0.0
    return precision, recall


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--c0-run", type=Path, required=True)
    parser.add_argument("--c1-run", type=Path, required=True)
    parser.add_argument("--c0-atm", type=Path, required=True)
    parser.add_argument("--c1-atm", type=Path, required=True)
    parser.add_argument("--annotation-cache", type=Path, required=True)
    parser.add_argument("--report-id", required=True)
    parser.add_argument(
        "--atm-root",
        type=Path,
        default=EXPERIMENT_ROOT.parents[1] / "other_repo_references/ATM-Bench",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("/home/lab/lab/research_artifacts/reports/behavior_pair"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    sys.path.insert(0, str(args.atm_root))
    from memqa.utils.evaluator.evaluate_qa import _prediction_list_items
    from memqa.utils.evaluator.normalizer import is_abstention
    from memqa.utils.evaluator.normalizer import split_list_items

    output = create_run_directory(args.output_root / args.report_id)
    predictions = {
        condition: _by_id(_load_jsonl(run / "predictions.jsonl"), "qa_id")
        for condition, run in (("C0", args.c0_run), ("C1", args.c1_run))
    }
    scores = {
        "C0": _by_id(_load_json(args.c0_atm), "id"),
        "C1": _by_id(_load_json(args.c1_atm), "id"),
    }
    qa_ids = set(predictions["C0"])
    if any(
        set(rows) != qa_ids
        for rows in (predictions["C1"], scores["C0"], scores["C1"])
    ):
        raise ValueError("paired behavior/evaluation QA IDs differ")
    annotations: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in _load_jsonl(args.annotation_cache):
        annotations[str(row["qa_id"])].append(row)

    items = []
    for qa_id in sorted(qa_ids):
        left, right = predictions["C0"][qa_id], predictions["C1"][qa_id]
        if left["evidence_ids"] != right["evidence_ids"]:
            raise ValueError(f"paired evidence IDs differ for {qa_id}")
        c0_score = float(scores["C0"][qa_id]["accuracy"])
        c1_score = float(scores["C1"][qa_id]["accuracy"])
        annotation_rows = annotations[qa_id]
        c0_answer = str(left["answer"])
        c1_answer = str(right["answer"])
        c0_exact_unknown = c0_answer.strip().casefold() == "unknown"
        c1_exact_unknown = c1_answer.strip().casefold() == "unknown"
        c0_abstention = bool(is_abstention(c0_answer))
        c1_abstention = bool(is_abstention(c1_answer))
        broad_only = (c0_abstention != c0_exact_unknown) or (
            c1_abstention != c1_exact_unknown
        )
        list_metrics: dict[str, float | None] = {
            "c0_list_precision": None,
            "c0_list_recall": None,
            "c1_list_precision": None,
            "c1_list_recall": None,
        }
        if str(left["qtype"]).lower() == "list_recall":
            gold_items = {
                item
                for item in split_list_items(
                    str(scores["C0"][qa_id].get("ground_truth", ""))
                )
                if item
            }
            c0_precision, c0_recall = list_precision_recall(
                gold_items, set(_prediction_list_items(c0_answer))
            )
            c1_precision, c1_recall = list_precision_recall(
                gold_items, set(_prediction_list_items(c1_answer))
            )
            list_metrics = {
                "c0_list_precision": c0_precision,
                "c0_list_recall": c0_recall,
                "c1_list_precision": c1_precision,
                "c1_list_recall": c1_recall,
            }
        items.append(
            {
                "qa_id": qa_id,
                "qtype": left["qtype"],
                "c0_answer": c0_answer,
                "c1_answer": c1_answer,
                "c0_exact_unknown": c0_exact_unknown,
                "c1_exact_unknown": c1_exact_unknown,
                "exact_unknown_transition": _binary_transition(
                    c0_exact_unknown, c1_exact_unknown
                ),
                "c0_atm_abstention": c0_abstention,
                "c1_atm_abstention": c1_abstention,
                "atm_abstention_transition": _binary_transition(
                    c0_abstention, c1_abstention
                ),
                "broad_only_review_required": broad_only,
                "broad_only_review_status": "pending" if broad_only else "not_needed",
                "c0_score": c0_score,
                "c1_score": c1_score,
                "delta": c1_score - c0_score,
                "transition": correctness_transition(c0_score, c1_score),
                "full_credit_transition": correctness_transition(c0_score, c1_score),
                "behavior_stratum": behavior_stratum(
                    c0_abstention, c1_abstention, c0_score, c1_score
                ),
                "c0_prompt_tokens": int(left["prompt_tokens"]),
                "c1_prompt_tokens": int(right["prompt_tokens"]),
                "prompt_token_delta": int(right["prompt_tokens"])
                - int(left["prompt_tokens"]),
                "c0_judge_model": scores["C0"][qa_id].get("judge_model"),
                "c1_judge_model": scores["C1"][qa_id].get("judge_model"),
                "c0_judge_retry": int(scores["C0"][qa_id].get("retry_count", 0)),
                "c1_judge_retry": int(scores["C1"][qa_id].get("retry_count", 0)),
                "c0_judge_failed": bool(scores["C0"][qa_id].get("failed", False)),
                "c1_judge_failed": bool(scores["C1"][qa_id].get("failed", False)),
                "annotation_scores": [int(row["score"]) for row in annotation_rows],
                "annotation_low_count": sum(
                    int(row["score"]) <= 2 for row in annotation_rows
                ),
                "annotation_epistemic_count": sum(
                    _contains_epistemic_language(str(row.get("comment", "")))
                    for row in annotation_rows
                ),
                **list_metrics,
            }
        )
    items_path = output / "paired_items.jsonl"
    items_path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in items) + "\n",
        encoding="utf-8",
    )
    by_qtype = {}
    for qtype in sorted({row["qtype"] for row in items}):
        subset = [row for row in items if row["qtype"] == qtype]
        by_qtype[qtype] = {
            "C0": summarize_scores([row["c0_score"] for row in subset]),
            "C1": summarize_scores([row["c1_score"] for row in subset]),
        }
    summary = {
        "report_id": args.report_id,
        "status": "complete_primary_judge",
        "qa_count": len(items),
        "C0": summarize_scores([row["c0_score"] for row in items]),
        "C1": summarize_scores([row["c1_score"] for row in items]),
        "by_qtype": by_qtype,
        "transition_counts": dict(Counter(row["transition"] for row in items)),
        "behavior_stratum_counts": dict(
            Counter(row["behavior_stratum"] for row in items)
        ),
        "exact_unknown_transition_counts": dict(
            Counter(row["exact_unknown_transition"] for row in items)
        ),
        "atm_abstention_transition_counts": dict(
            Counter(row["atm_abstention_transition"] for row in items)
        ),
        "negative_delta_count": sum(row["delta"] < 0 for row in items),
        "positive_delta_count": sum(row["delta"] > 0 for row in items),
        "c1_exact_unknown_count": sum(row["c1_exact_unknown"] for row in items),
        "c1_atm_abstention_count": sum(row["c1_atm_abstention"] for row in items),
        "broad_only_review_count": sum(
            row["broad_only_review_required"] for row in items
        ),
        "mean_prompt_token_delta": statistics.fmean(
            row["prompt_token_delta"] for row in items
        ),
        "inputs": {
            "c0_predictions_sha256": _sha256(args.c0_run / "predictions.jsonl"),
            "c1_predictions_sha256": _sha256(args.c1_run / "predictions.jsonl"),
            "c0_atm_sha256": _sha256(args.c0_atm),
            "c1_atm_sha256": _sha256(args.c1_atm),
            "annotation_cache_sha256": _sha256(args.annotation_cache),
        },
        "paired_items_sha256": _sha256(items_path),
        "boundary": (
            "Primary judge is complete. Broad-only abstention rows require explicit "
            "human review before final behavior claims."
        ),
    }
    (output / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    _write_report(output / "REPORT.md", summary, items)
    print(output)
    return 0


def _write_report(path: Path, summary: dict[str, Any], items: list[dict[str, Any]]) -> None:
    degraded = sorted(
        (row for row in items if row["delta"] < 0),
        key=lambda row: row["delta"],
    )
    lines = [
        "# C0/C1 Primary Behavior Audit",
        "",
        f"- Questions: {summary['qa_count']} (all Hard question types)",
        f"- C0 ATM mean: {summary['C0']['mean']:.4f}",
        f"- C1 ATM mean: {summary['C1']['mean']:.4f}",
        f"- Behavior strata: `{summary['behavior_stratum_counts']}`",
        f"- Exact-Unknown transitions: `{summary['exact_unknown_transition_counts']}`",
        f"- ATM-abstention transitions: `{summary['atm_abstention_transition_counts']}`",
        f"- Positive / negative deltas: {summary['positive_delta_count']} / "
        f"{summary['negative_delta_count']}",
        "",
        "This report is behavioral and does not infer an internal mechanism. "
        "Broad-only abstention rows remain human-review items.",
        "",
        "## Degraded Questions",
        "",
        "| QA | Type | C0 | C1 | Delta | Stratum | C1 abstains | Low annotations |",
        "| --- | --- | ---: | ---: | ---: | --- | ---: |",
    ]
    lines.extend(
        f"| `{row['qa_id']}` | {row['qtype']} | {row['c0_score']:.3f} | "
        f"{row['c1_score']:.3f} | {row['delta']:.3f} | "
        f"{row['behavior_stratum']} | {row['c1_atm_abstention']} | "
        f"{row['annotation_low_count']} |"
        for row in degraded
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _load_json(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _by_id(rows: list[dict[str, Any]], field: str) -> dict[str, dict[str, Any]]:
    result = {str(row[field]): row for row in rows}
    if len(result) != len(rows):
        raise ValueError(f"duplicate {field} values")
    return result


def _binary_transition(left: bool, right: bool) -> str:
    return f"{'U' if left else 'N'}->{'U' if right else 'N'}"


def _contains_epistemic_language(text: str) -> bool:
    normalized = text.casefold()
    phrases = (
        "insufficient",
        "not enough",
        "does not directly answer",
        "cannot answer",
        "missing",
        "uncertain",
        "irrelevant",
        "not relevant",
    )
    return any(phrase in normalized for phrase in phrases)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
