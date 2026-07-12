#!/usr/bin/env python3
"""Run immutable API answerer inference without invoking a judge."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = EXPERIMENT_ROOT.parents[1]
if str(EXPERIMENT_ROOT) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_ROOT))

from adapters.api_chat import APIChatAdapter, APIProviderSpec  # noqa: E402
from adapters.atm import ATMAdapter  # noqa: E402
from behavior.run_behavior import (  # noqa: E402
    evidence_ids_for_condition,
    select_condition_items,
    select_ground_truth_rows,
)
from core.registry import load_condition_registry  # noqa: E402
from core.run_contract import create_run_directory, sanitize_manifest  # noqa: E402
from interventions.verbal_annotation import apply_annotation_cache  # noqa: E402

API_CONDITIONS = frozenset({"C1", "C7", "C8", "C9", "C10"})


def validate_api_condition(condition_id: str, split: str) -> None:
    if split != "hard" or condition_id not in API_CONDITIONS:
        raise ValueError("API v1.0 permits only Hard C1/C7-C10")


def response_fields(response: Any) -> dict[str, Any]:
    usage = response.usage
    prompt = int(getattr(usage, "prompt_tokens", 0) or 0)
    completion = int(getattr(usage, "completion_tokens", 0) or 0)
    total = int(getattr(usage, "total_tokens", prompt + completion) or 0)
    details = getattr(usage, "completion_tokens_details", None)
    reasoning = int(getattr(details, "reasoning_tokens", 0) or 0)
    cached_details = getattr(usage, "prompt_tokens_details", None)
    cached = int(getattr(cached_details, "cached_tokens", 0) or 0)
    return {
        "answer": str(response.choices[0].message.content or ""),
        "returned_model": str(response.model),
        "prompt_tokens": prompt,
        "completion_tokens": completion,
        "total_tokens": total,
        "reasoning_tokens": reasoning,
        "cached_tokens": cached,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", required=True)
    parser.add_argument("--condition", choices=sorted(API_CONDITIONS), required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--annotation-cache", type=Path, required=True)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--max-tokens", type=int, default=1000)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument(
        "--atm-root",
        type=Path,
        default=PROJECT_ROOT / "other_repo_references/ATM-Bench",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    validate_api_condition(args.condition, "hard")
    if args.limit is not None and args.limit <= 0:
        raise ValueError("--limit must be positive")
    if not args.annotation_cache.is_file():
        raise FileNotFoundError(args.annotation_cache)

    provider_path = EXPERIMENT_ROOT / "registry/api_provider_registry.yaml"
    provider_rows = yaml.safe_load(provider_path.read_text(encoding="utf-8"))[
        "providers"
    ]
    by_id = {row["id"]: row for row in provider_rows}
    if args.provider not in by_id:
        raise ValueError(f"unknown API provider: {args.provider}")
    # Resolve every required environment value before creating an output directory.
    provider = APIProviderSpec.from_mapping(by_id[args.provider], environ=os.environ)

    conditions = load_condition_registry(
        EXPERIMENT_ROOT / "registry/condition_registry.yaml"
    )
    condition = conditions[args.condition]
    atm = ATMAdapter(args.atm_root)
    items = select_condition_items(atm, "hard", condition)
    if args.limit is not None:
        items = items[: args.limit]
    annotations = _load_jsonl(args.annotation_cache)
    ground_truth = select_ground_truth_rows(
        json.loads(atm.split_path("hard").read_text(encoding="utf-8")),
        [item.qa_id for item in items],
    )

    run_dir = create_run_directory(
        args.run_root / args.condition / "hard" / args.provider / args.run_id
    )
    ground_truth_path = run_dir / "ground_truth_subset.json"
    ground_truth_path.write_text(
        json.dumps(ground_truth, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    predictions_path = run_dir / "predictions.jsonl"
    started_at = datetime.now().astimezone().isoformat()
    adapter = APIChatAdapter(provider)
    with predictions_path.open("x", encoding="utf-8") as handle:
        for item in items:
            evidence_ids = evidence_ids_for_condition(item, condition)
            original_chunks = atm.collect_sgm_chunks(evidence_ids)
            chunks = apply_annotation_cache(
                item.qa_id, evidence_ids, original_chunks, annotations
            )
            messages = atm.build_text_messages(item.question, chunks)
            prompt_payload = json.dumps(
                messages, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            )
            request_started = time.perf_counter()
            response = adapter.generate(
                messages, max_tokens=args.max_tokens, temperature=0.0
            )
            row = response_fields(response)
            row.update(
                {
                    "id": item.qa_id,
                    "qa_id": item.qa_id,
                    "qtype": item.qtype,
                    "evidence_ids": list(evidence_ids),
                    "requested_model": provider.model,
                    "evidence_sha256": [_text_sha256(x) for x in chunks],
                    "prompt": prompt_payload,
                    "prompt_sha256": _text_sha256(prompt_payload),
                    "latency_seconds": time.perf_counter() - request_started,
                }
            )
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()

    manifest = sanitize_manifest(
        {
            "run_id": args.run_id,
            "status": "complete",
            "artifact_kind": "api_inference",
            "project_commit": _git_commit(PROJECT_ROOT),
            "condition": args.condition,
            "split": "hard",
            "provider": provider.manifest_view(),
            "generation": {"max_tokens": args.max_tokens, "temperature": 0.0},
            "prediction_count": len(items),
            "annotation_cache_sha256": _file_sha256(args.annotation_cache),
            "predictions_sha256": _file_sha256(predictions_path),
            "ground_truth_sha256": _file_sha256(ground_truth_path),
            "provider_registry_sha256": _file_sha256(provider_path),
            "started_at": started_at,
            "finished_at": datetime.now().astimezone().isoformat(),
        }
    )
    (run_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(run_dir)
    return 0


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_commit(root: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()


if __name__ == "__main__":
    raise SystemExit(main())

