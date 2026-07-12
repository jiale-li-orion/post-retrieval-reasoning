#!/usr/bin/env python3
"""Merge complete behavior shards into one immutable inference artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
if str(EXPERIMENT_ROOT) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_ROOT))

from core.run_contract import create_run_directory, sanitize_manifest  # noqa: E402


def merge_prediction_rows(
    shards: list[list[dict[str, Any]]], canonical_ids: list[str]
) -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for shard in shards:
        for row in shard:
            qa_id = str(row["qa_id"])
            if qa_id in by_id:
                raise ValueError(f"duplicate prediction row: {qa_id}")
            by_id[qa_id] = row
    missing = [qa_id for qa_id in canonical_ids if qa_id not in by_id]
    unexpected = sorted(set(by_id) - set(canonical_ids))
    if missing:
        raise ValueError(f"missing prediction rows: {missing}")
    if unexpected:
        raise ValueError(f"unexpected prediction rows: {unexpected}")
    return [by_id[qa_id] for qa_id in canonical_ids]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard-dir", type=Path, action="append", required=True)
    parser.add_argument("--canonical-ground-truth", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifests = [_load_json(path / "manifest.json") for path in args.shard_dir]
    _validate_manifests(manifests, len(args.shard_dir))
    canonical_ground_truth = _load_json(args.canonical_ground_truth)
    canonical_ids = [str(row["id"]) for row in canonical_ground_truth]
    shard_rows = [_load_jsonl(path / "predictions.jsonl") for path in args.shard_dir]
    predictions = merge_prediction_rows(shard_rows, canonical_ids)

    output_dir = create_run_directory(args.output_dir)
    predictions_path = output_dir / "predictions.jsonl"
    with predictions_path.open("x", encoding="utf-8") as handle:
        for row in predictions:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    ground_truth_path = output_dir / "ground_truth_subset.json"
    ground_truth_path.write_text(
        json.dumps(canonical_ground_truth, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    first = manifests[0]
    manifest = sanitize_manifest(
        {
            "run_id": output_dir.name,
            "status": "complete",
            "artifact_kind": "merged_inference",
            "project_commit": first["project_commit"],
            "condition": first["condition"],
            "split": first["split"],
            "model": first["model"],
            "generation": first["generation"],
            "dataset": first["dataset"],
            "config_hashes": first["config_hashes"],
            "environment": first["environment"],
            "input_shards": [
                {
                    "path": str(path.resolve()),
                    "manifest_sha256": _sha256(path / "manifest.json"),
                    "predictions_sha256": _sha256(path / "predictions.jsonl"),
                }
                for path in args.shard_dir
            ],
            "prediction_count": len(predictions),
            "predictions_sha256": _sha256(predictions_path),
            "ground_truth_sha256": _sha256(ground_truth_path),
            "started_at": datetime.now().astimezone().isoformat(),
            "finished_at": datetime.now().astimezone().isoformat(),
        }
    )
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(output_dir)
    return 0


def _validate_manifests(manifests: list[dict[str, Any]], expected_count: int) -> None:
    if any(row.get("status") != "complete" for row in manifests):
        raise ValueError("all shard manifests must be complete")
    keys = ("project_commit", "condition", "split", "model", "generation", "config_hashes")
    reference = {key: manifests[0][key] for key in keys}
    if any({key: row[key] for key in keys} != reference for row in manifests[1:]):
        raise ValueError("shard contracts differ")
    shard_indices = sorted(int(row["shard"]["index"]) for row in manifests)
    shard_counts = {int(row["shard"]["count"]) for row in manifests}
    if shard_counts != {expected_count} or shard_indices != list(range(expected_count)):
        raise ValueError("shard index/count contract is incomplete")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
