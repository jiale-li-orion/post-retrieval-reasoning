#!/usr/bin/env python3
"""Evaluate a frozen behavior run with ATM-Bench's official evaluator."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = EXPERIMENT_ROOT.parents[1]
DEFAULT_JUDGE_MODEL = "gpt-5-mini"
DEFAULT_REASONING_EFFORT = "minimal"

if str(EXPERIMENT_ROOT) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_ROOT))

from core.run_contract import create_run_directory, sanitize_manifest  # noqa: E402


def requires_llm_judge(ground_truth: list[dict[str, Any]]) -> bool:
    return any(str(row.get("qtype", "")).lower() == "open_end" for row in ground_truth)


def select_deterministic_pairs(
    ground_truth: list[dict[str, Any]], predictions: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    selected_ground_truth = [
        row
        for row in ground_truth
        if str(row.get("qtype", "")).lower() in {"number", "list_recall"}
    ]
    selected_ids = {str(row["id"]) for row in selected_ground_truth}
    selected_predictions = [
        row for row in predictions if str(row.get("qa_id", row.get("id"))) in selected_ids
    ]
    if {str(row.get("qa_id", row.get("id"))) for row in selected_predictions} != selected_ids:
        raise ValueError("deterministic predictions do not match ground truth IDs")
    return selected_ground_truth, selected_predictions


def build_evaluator_command(
    *,
    atm_root: Path,
    run_dir: Path,
    eval_dir: Path,
    judge_model: str,
    reasoning_effort: str,
    fallback_model: str,
    max_retries: int,
    request_delay: float,
) -> list[str]:
    return [
        sys.executable,
        str(atm_root / "memqa/utils/evaluator/evaluate_qa.py"),
        "--ground-truth",
        str(run_dir / "ground_truth_subset.json"),
        "--predictions",
        str(run_dir / "predictions.jsonl"),
        "--output-dir",
        str(eval_dir),
        "--metrics",
        "em",
        "atm",
        "--judge-provider",
        "openai",
        "--judge-model",
        judge_model,
        "--judge-reasoning-effort",
        reasoning_effort,
        "--judge-fallback-model",
        fallback_model,
        "--judge-fallback-after-retries",
        "0",
        "--judge-max-retries",
        str(max_retries),
        "--request-delay",
        str(request_delay),
        "--max-workers",
        "1",
    ]


def failed_judge_rows(
    rows: list[dict[str, Any]], requested_model: str
) -> list[dict[str, Any]]:
    failures = []
    for row in rows:
        if str(row.get("qtype", "")).lower() != "open_end":
            continue
        if (
            row.get("failed")
            or row.get("error")
            or row.get("fallback_model_used")
            or str(row.get("judge_model", "")) != requested_model
        ):
            failures.append(row)
    return failures


def build_evaluator_environment(
    atm_root: Path, environ: dict[str, str] | None = None
) -> dict[str, str]:
    source = os.environ if environ is None else environ
    env = dict(source)
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(atm_root) + (os.pathsep + existing if existing else "")
    return env


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--eval-id", required=True)
    parser.add_argument("--judge-model", default=DEFAULT_JUDGE_MODEL)
    parser.add_argument("--judge-reasoning-effort", default=DEFAULT_REASONING_EFFORT)
    parser.add_argument("--judge-max-retries", type=int, default=3)
    parser.add_argument("--request-delay", type=float, default=10.0)
    parser.add_argument("--deterministic-only", action="store_true")
    parser.add_argument(
        "--atm-root",
        type=Path,
        default=PROJECT_ROOT / "other_repo_references/ATM-Bench",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ground_truth_path = args.run_dir / "ground_truth_subset.json"
    predictions_path = args.run_dir / "predictions.jsonl"
    inference_manifest_path = args.run_dir / "manifest.json"
    for path in (ground_truth_path, predictions_path, inference_manifest_path):
        if not path.is_file():
            raise FileNotFoundError(f"frozen inference artifact missing: {path}")

    eval_dir = create_run_directory(args.run_dir / "evaluations" / args.eval_id)
    ground_truth = json.loads(ground_truth_path.read_text(encoding="utf-8"))
    command_run_dir = args.run_dir
    if args.deterministic_only:
        predictions = [
            json.loads(line)
            for line in predictions_path.read_text(encoding="utf-8").splitlines()
            if line
        ]
        ground_truth, predictions = select_deterministic_pairs(
            ground_truth, predictions
        )
        command_run_dir = eval_dir / "inputs"
        command_run_dir.mkdir()
        (command_run_dir / "ground_truth_subset.json").write_text(
            json.dumps(ground_truth, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (command_run_dir / "predictions.jsonl").write_text(
            "\n".join(json.dumps(row, ensure_ascii=False) for row in predictions)
            + "\n",
            encoding="utf-8",
        )
    needs_judge = requires_llm_judge(ground_truth)
    if needs_judge and not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is required only because this run contains open_end items"
        )

    started_at = datetime.now().astimezone().isoformat()
    command = build_evaluator_command(
        atm_root=args.atm_root,
        run_dir=command_run_dir,
        eval_dir=eval_dir,
        judge_model=args.judge_model,
        reasoning_effort=args.judge_reasoning_effort,
        fallback_model="",
        max_retries=args.judge_max_retries,
        request_delay=args.request_delay,
    )
    subprocess.run(
        command,
        cwd=args.atm_root,
        env=build_evaluator_environment(args.atm_root),
        check=True,
    )

    judge_failures: list[dict[str, Any]] = []
    if needs_judge:
        model_tag = "".join(
            char if char.isalnum() or char in "-_" else "_"
            for char in args.judge_model
        )
        atm_path = eval_dir / f"atm_{model_tag}.json"
        if not atm_path.is_file():
            raise FileNotFoundError(f"official ATM output missing: {atm_path}")
        judge_failures = failed_judge_rows(
            json.loads(atm_path.read_text(encoding="utf-8")), args.judge_model
        )

    manifest = sanitize_manifest(
        {
            "eval_id": args.eval_id,
            "status": "incomplete" if judge_failures else "complete",
            "project_commit": _git_commit(PROJECT_ROOT),
            "atm_commit": _git_commit(args.atm_root),
            "inference_run": str(args.run_dir.resolve()),
            "inputs": {
                "inference_manifest_sha256": _sha256(inference_manifest_path),
                "ground_truth_sha256": _sha256(ground_truth_path),
                "predictions_sha256": _sha256(predictions_path),
            },
            "judge": {
                "required": needs_judge,
                "provider": "openai",
                "model": args.judge_model,
                "reasoning_effort": args.judge_reasoning_effort,
            },
            "evaluation_scope": (
                "deterministic_only" if args.deterministic_only else "all"
            ),
            "evaluated_count": len(ground_truth),
            "command": command,
            "started_at": started_at,
            "finished_at": datetime.now().astimezone().isoformat(),
            "outputs": _output_hashes(eval_dir),
            "judge_failure_ids": [str(row.get("id")) for row in judge_failures],
        }
    )
    (eval_dir / "eval_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(eval_dir)
    return 2 if judge_failures else 0


def _git_commit(root: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _output_hashes(eval_dir: Path) -> dict[str, str]:
    return {
        str(path.relative_to(eval_dir)): _sha256(path)
        for path in sorted(eval_dir.rglob("*"))
        if path.is_file() and path.name != "eval_manifest.json"
    }


if __name__ == "__main__":
    raise SystemExit(main())
