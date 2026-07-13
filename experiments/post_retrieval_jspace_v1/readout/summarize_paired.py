#!/usr/bin/env python3
"""Summarize paired C0/C1 ATM behavior and internal readouts."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
if str(EXPERIMENT_ROOT) in sys.path:
    sys.path.remove(str(EXPERIMENT_ROOT))
sys.path.insert(0, str(EXPERIMENT_ROOT))

from core.run_contract import create_run_directory  # noqa: E402


PAIR_KEYS = [
    "qa_id",
    "qtype",
    "layer",
    "normalized_depth",
    "position_type",
    "position_index",
    "readout_kind",
    "target_id",
    "target_text",
    "copyable",
    "derived_candidate",
    "method",
    "eligible_primary",
]


def pair_readouts(c0: pd.DataFrame, c1: pd.DataFrame) -> pd.DataFrame:
    for name, frame in (("C0", c0), ("C1", c1)):
        missing = sorted(set(PAIR_KEYS) - set(frame.columns))
        if missing:
            raise ValueError(f"{name} readout missing columns: {missing}")
        if frame.duplicated(PAIR_KEYS).any():
            raise ValueError(f"{name} readout contains duplicate paired keys")
    value_columns = ["score", "rank", "mrr", "token_set_coverage"]
    paired = c0[PAIR_KEYS + value_columns].merge(
        c1[PAIR_KEYS + value_columns],
        on=PAIR_KEYS,
        how="outer",
        suffixes=("_c0", "_c1"),
        indicator=True,
        validate="one_to_one",
    )
    if not (paired["_merge"] == "both").all():
        raise ValueError("C0/C1 readout keys are not identical")
    paired = paired.drop(columns="_merge")
    for metric in value_columns:
        paired[f"delta_{metric}"] = paired[f"{metric}_c1"] - paired[f"{metric}_c0"]
    return paired


def transition_label(c0_score: float, c1_score: float) -> str:
    c0_correct = float(c0_score) == 1.0
    c1_correct = float(c1_score) == 1.0
    if c0_correct and c1_correct:
        return "stable_success"
    if not c0_correct and c1_correct:
        return "repair"
    if c0_correct and not c1_correct:
        return "degradation"
    return "stable_failure"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--c0-readout", type=Path, required=True)
    parser.add_argument("--c1-readout", type=Path, required=True)
    parser.add_argument("--c0-eval", type=Path, required=True)
    parser.add_argument("--c1-eval", type=Path, required=True)
    parser.add_argument("--report-id", required=True)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("/home/lab/lab/research_artifacts/reports/paired_readout"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = create_run_directory(args.output_root / args.report_id)
    c0 = pd.read_parquet(args.c0_readout)
    c1 = pd.read_parquet(args.c1_readout)
    paired = pair_readouts(c0, c1)
    paired_path = output / "paired_readout_deltas.parquet"
    paired.to_parquet(paired_path, index=False)

    c0_eval = _load_eval(args.c0_eval)
    c1_eval = _load_eval(args.c1_eval)
    if set(c0_eval) != set(c1_eval):
        raise ValueError("C0/C1 deterministic evaluation IDs differ")
    transitions = []
    for qa_id in sorted(c0_eval):
        left, right = c0_eval[qa_id], c1_eval[qa_id]
        transitions.append(
            {
                "qa_id": qa_id,
                "qtype": left["qtype"],
                "c0_score": float(left["accuracy"]),
                "c1_score": float(right["accuracy"]),
                "transition": transition_label(left["accuracy"], right["accuracy"]),
            }
        )
    transitions_path = output / "behavior_transitions.jsonl"
    transitions_path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in transitions) + "\n",
        encoding="utf-8",
    )
    summary = {
        "report_id": args.report_id,
        "status": "complete_deterministic_only",
        "paired_readout_rows": len(paired),
        "primary_eligible_rows": int(paired["eligible_primary"].sum()),
        "deterministic_qa_count": len(transitions),
        "transition_counts": pd.Series(
            [row["transition"] for row in transitions]
        ).value_counts().to_dict(),
        "mean_delta_rank_primary": _safe_mean(
            paired.loc[paired["eligible_primary"], "delta_rank"]
        ),
        "mean_delta_coverage_secondary": _safe_mean(
            paired["delta_token_set_coverage"]
        ),
        "inputs": {
            "c0_readout_sha256": _sha256(args.c0_readout),
            "c1_readout_sha256": _sha256(args.c1_readout),
            "c0_eval_sha256": _sha256(args.c0_eval),
            "c1_eval_sha256": _sha256(args.c1_eval),
        },
        "outputs": {
            "paired_readout_sha256": _sha256(paired_path),
            "transitions_sha256": _sha256(transitions_path),
        },
        "interpretation_boundary": (
            "Open-end questions are pending judge. Multi-token coverage is secondary "
            "and cannot establish representation absence or phrase readability."
        ),
    }
    (output / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(output)
    return 0


def _load_eval(path: Path) -> dict[str, dict[str, Any]]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    selected = {
        str(row["id"]): row
        for row in rows
        if str(row["qtype"]).lower() in {"number", "list_recall"}
    }
    if not selected:
        raise ValueError("evaluation contains no deterministic rows")
    return selected


def _safe_mean(series: pd.Series) -> float | None:
    value = series.mean()
    return None if pd.isna(value) else float(value)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
