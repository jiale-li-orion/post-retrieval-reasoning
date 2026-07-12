#!/usr/bin/env python3
"""Run immutable open-weight ATM behavior jobs."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import torch
import transformers


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = EXPERIMENT_ROOT.parents[1]
if str(EXPERIMENT_ROOT) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_ROOT))

from adapters.atm import ATMAdapter  # noqa: E402
from adapters.atm import ATMItem  # noqa: E402
from adapters.hf_model import HFModelAdapter  # noqa: E402
from core.registry import load_condition_registry, load_model_registry  # noqa: E402
from core.run_contract import (  # noqa: E402
    create_run_directory,
    sanitize_manifest,
    validate_manifest_completeness,
)
from interventions.verbal_annotation import apply_annotation_cache  # noqa: E402


def validate_run_selection(
    condition_id: str,
    split: str,
    conditions: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    condition = conditions[condition_id]
    if split not in condition["split"]:
        raise ValueError(f"{condition_id} does not support split {split}")
    if condition["evidence"] == "raw":
        raise NotImplementedError("Raw multimodal conditions use a separate runner")
    return condition


def select_condition_items(
    atm: ATMAdapter, split: str, condition: dict[str, Any]
) -> list[ATMItem]:
    if "niah_k" in condition:
        return atm.load_niah(int(condition["niah_k"]))
    return atm.load_split(split)


def evidence_ids_for_condition(
    item: ATMItem, condition: dict[str, Any]
) -> tuple[str, ...]:
    if condition["evidence_selector"] == "evidence_ids":
        return item.evidence_ids
    if condition["evidence_selector"] == "niah_evidence_ids":
        if item.niah_evidence_ids is None:
            raise ValueError(f"NIAH evidence absent for {item.qa_id}")
        return item.niah_evidence_ids
    raise ValueError(f"unsupported evidence selector: {condition['evidence_selector']}")


def select_shard(items: list[Any], shard_index: int, num_shards: int) -> list[Any]:
    if num_shards <= 0 or not 0 <= shard_index < num_shards:
        raise ValueError("shard index must be within a positive shard count")
    base, remainder = divmod(len(items), num_shards)
    start = shard_index * base + min(shard_index, remainder)
    size = base + (1 if shard_index < remainder else 0)
    return items[start : start + size]


def validate_resume_prefix(
    existing_ids: list[str], canonical_ids: list[str]
) -> None:
    if canonical_ids[: len(existing_ids)] != existing_ids:
        raise ValueError("existing predictions are not a canonical prefix")


def build_prediction_row(
    *,
    qa_id: str,
    qtype: str,
    evidence_ids: tuple[str, ...],
    answer: str,
    prompt_tokens: int,
    completion_tokens: int,
    model_id: str,
    evidence_chunks: tuple[str, ...],
    prompt_payload: str,
    latency_seconds: float,
) -> dict[str, Any]:
    return {
        "id": qa_id,
        "qa_id": qa_id,
        "qtype": qtype,
        "evidence_ids": list(evidence_ids),
        "answer": answer,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "requested_model": model_id,
        "returned_model": model_id,
        "evidence_sha256": [_text_sha256(chunk) for chunk in evidence_chunks],
        "prompt": prompt_payload,
        "prompt_sha256": _text_sha256(prompt_payload),
        "latency_seconds": latency_seconds,
    }


def select_ground_truth_rows(
    rows: list[dict[str, Any]], qa_ids: list[str]
) -> list[dict[str, Any]]:
    by_id = {str(row["id"]): row for row in rows}
    missing = [qa_id for qa_id in qa_ids if qa_id not in by_id]
    if missing:
        raise ValueError(f"ground truth missing selected IDs: {missing}")
    return [by_id[qa_id] for qa_id in qa_ids]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--condition", default="C0")
    parser.add_argument("--split", choices=["full", "hard"], default="hard")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--max-new-tokens", type=int, default=1000)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--annotation-cache", type=Path)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--num-shards", type=int, default=1)
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Continue an interrupted run whose predictions form a canonical prefix",
    )
    parser.add_argument(
        "--run-root",
        type=Path,
        default=Path("/home/lab/lab/research_artifacts/runs"),
    )
    parser.add_argument(
        "--atm-root",
        type=Path,
        default=PROJECT_ROOT / "other_repo_references/ATM-Bench",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.limit is not None and args.limit <= 0:
        raise ValueError("--limit must be positive")
    if args.num_shards <= 0 or not 0 <= args.shard_index < args.num_shards:
        raise ValueError("invalid shard index/count")
    conditions = load_condition_registry(
        EXPERIMENT_ROOT / "registry/condition_registry.yaml"
    )
    condition = validate_run_selection(args.condition, args.split, conditions)
    if condition["annotation"] == "verbal_r3" and args.annotation_cache is None:
        raise ValueError(f"{args.condition} requires --annotation-cache")
    if condition["annotation"] == "none" and args.annotation_cache is not None:
        raise ValueError(f"{args.condition} does not accept --annotation-cache")
    models = load_model_registry(EXPERIMENT_ROOT / "registry/model_registry.yaml")
    model_spec = models[args.model_id]
    if model_spec["revision"] in {"pending", "main", "latest"}:
        raise ValueError(f"model {args.model_id} is not revision-frozen")
    if model_spec.get("file_manifest_sha256") in {None, "pending"}:
        raise ValueError(f"model {args.model_id} is missing snapshot provenance")

    run_dir = args.run_root / args.condition / args.split / args.model_id / args.run_id
    if args.resume:
        if not run_dir.is_dir():
            raise FileNotFoundError(f"resume run does not exist: {run_dir}")
    else:
        run_dir = create_run_directory(run_dir)
    manifest_path = run_dir / "manifest.json"
    predictions_path = run_dir / "predictions.jsonl"
    ground_truth_path = run_dir / "ground_truth_subset.json"
    expected_manifest = sanitize_manifest(
        {
            "run_id": args.run_id,
            "status": "running",
            "project_commit": _git_commit(PROJECT_ROOT),
            "git_dirty": _git_dirty(PROJECT_ROOT),
            "condition": args.condition,
            "condition_spec": condition,
            "split": args.split,
            "limit": args.limit,
            "shard": {
                "index": args.shard_index,
                "count": args.num_shards,
            },
            "model": model_spec,
            "generation": {
                "max_new_tokens": args.max_new_tokens,
                "temperature": 0.0,
            },
            "dataset": {
                "atm_commit": _git_commit(args.atm_root),
                "split_sha256": ATMAdapter(args.atm_root).split_sha256(args.split),
                "prompt_contract_sha256": _file_sha256(
                    args.atm_root / "memqa/qa_agent_baselines/oracle/config.py"
                ),
            },
            "config_hashes": {
                "models": _file_sha256(
                    EXPERIMENT_ROOT / "registry/model_registry.yaml"
                ),
                "conditions": _file_sha256(
                    EXPERIMENT_ROOT / "registry/condition_registry.yaml"
                ),
                "datasets": _file_sha256(
                    EXPERIMENT_ROOT / "registry/dataset_registry.yaml"
                ),
            },
            "environment": {
                "python": sys.version,
                "platform": platform.platform(),
                "torch": torch.__version__,
                "transformers": transformers.__version__,
                "cuda": torch.version.cuda,
                "gpu": torch.cuda.get_device_name(0),
            },
            "started_at": datetime.now().astimezone().isoformat(),
        }
    )
    atm = ATMAdapter(args.atm_root)
    items = select_condition_items(atm, args.split, condition)
    if args.limit is not None:
        items = items[: args.limit]
    items = select_shard(items, args.shard_index, args.num_shards)
    raw_ground_truth = json.loads(
        atm.split_path(args.split).read_text(encoding="utf-8")
    )
    selected_ground_truth = select_ground_truth_rows(
        raw_ground_truth, [item.qa_id for item in items]
    )
    if args.resume:
        manifest = _load_resume_manifest(manifest_path, expected_manifest)
        if not ground_truth_path.is_file() or not predictions_path.is_file():
            raise FileNotFoundError("resume requires ground truth and predictions")
        if _file_sha256(ground_truth_path) != manifest["dataset"].get(
            "ground_truth_subset_sha256"
        ):
            raise ValueError("resume ground truth hash mismatch")
        existing_rows = _load_jsonl(predictions_path)
        validate_resume_prefix(
            [str(row["qa_id"]) for row in existing_rows],
            [item.qa_id for item in items],
        )
    else:
        manifest = expected_manifest
        _write_json_list(ground_truth_path, selected_ground_truth)
        manifest["dataset"]["ground_truth_subset_sha256"] = _file_sha256(
            ground_truth_path
        )
        existing_rows = []
    annotation_rows = (
        _load_jsonl(args.annotation_cache) if args.annotation_cache else []
    )
    if args.annotation_cache:
        annotation_contract = {
            "path": str(args.annotation_cache.resolve()),
            "sha256": _file_sha256(args.annotation_cache),
        }
        if args.resume and manifest.get("annotation_cache") != annotation_contract:
            raise ValueError("resume annotation cache contract mismatch")
        manifest["annotation_cache"] = annotation_contract

    if not args.resume:
        _write_json(manifest_path, manifest)
        predictions_path.touch(exist_ok=False)

    adapter = HFModelAdapter.from_local_snapshot(
        Path(model_spec["local_path"]), model_id=args.model_id
    )

    with predictions_path.open("a", encoding="utf-8") as handle:
        for item in items[len(existing_rows) :]:
            evidence_ids = evidence_ids_for_condition(item, condition)
            chunks = atm.collect_sgm_chunks(evidence_ids)
            if condition["annotation"] == "verbal_r3":
                chunks = apply_annotation_cache(
                    item.qa_id,
                    evidence_ids,
                    chunks,
                    annotation_rows,
                )
            messages = atm.build_text_messages(item.question, chunks)
            prompt_payload = adapter.processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            generation_started = time.perf_counter()
            result = adapter.generate(
                messages, max_new_tokens=args.max_new_tokens, temperature=0.0
            )
            latency_seconds = time.perf_counter() - generation_started
            row = build_prediction_row(
                qa_id=item.qa_id,
                qtype=item.qtype,
                evidence_ids=evidence_ids,
                answer=result.text,
                prompt_tokens=result.prompt_tokens,
                completion_tokens=result.completion_tokens,
                model_id=args.model_id,
                evidence_chunks=tuple(chunks),
                prompt_payload=prompt_payload,
                latency_seconds=latency_seconds,
            )
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()

    manifest["status"] = "complete"
    manifest["finished_at"] = datetime.now().astimezone().isoformat()
    manifest["prediction_count"] = len(items)
    validate_manifest_completeness(manifest)
    _write_json(manifest_path, manifest)
    print(run_dir)
    return 0


def _git_commit(root: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid JSONL at {path}:{line_number}") from exc
    return rows


def _load_resume_manifest(
    path: Path, expected: dict[str, Any]
) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"resume manifest does not exist: {path}")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("status") != "running":
        raise ValueError("only interrupted running manifests can be resumed")
    for key in (
        "run_id",
        "condition",
        "condition_spec",
        "split",
        "limit",
        "shard",
        "model",
        "generation",
        "config_hashes",
    ):
        if manifest.get(key) != expected.get(key):
            raise ValueError(f"resume manifest contract mismatch: {key}")
    for key in ("atm_commit", "split_sha256", "prompt_contract_sha256"):
        if manifest.get("dataset", {}).get(key) != expected["dataset"].get(key):
            raise ValueError(f"resume dataset contract mismatch: {key}")
    return sanitize_manifest(manifest)


def _text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _git_dirty(root: Path) -> bool:
    output = subprocess.check_output(
        ["git", "-C", str(root), "status", "--porcelain"], text=True
    )
    return bool(output.strip())


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def _write_json_list(path: Path, payload: list[dict[str, Any]]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


if __name__ == "__main__":
    raise SystemExit(main())
