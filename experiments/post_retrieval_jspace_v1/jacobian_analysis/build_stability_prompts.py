#!/usr/bin/env python3
"""Freeze held-out prompts used only for 256/512 lens stability checks."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from datasets import load_dataset
from transformers import AutoTokenizer


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = EXPERIMENT_ROOT.parents[1]
if str(EXPERIMENT_ROOT) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_ROOT))

from core.registry import load_model_registry  # noqa: E402
from core.run_contract import create_run_directory, sanitize_manifest  # noqa: E402
from jacobian_analysis.build_calibration_corpus import (  # noqa: E402
    WIKITEXT_REVISION,
    shuffled_document_windows,
    take_window_slice,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--set-id", required=True)
    parser.add_argument("--offset", type=int, default=512)
    parser.add_argument("--count", type=int, default=32)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--window-tokens", type=int, default=256)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("/home/lab/lab/research_data/wikitext103/stability"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    models = load_model_registry(EXPERIMENT_ROOT / "registry/model_registry.yaml")
    model_spec = models[args.model_id]
    tokenizer = AutoTokenizer.from_pretrained(
        model_spec["local_path"], local_files_only=True
    )
    dataset = load_dataset(
        "Salesforce/wikitext",
        "wikitext-103-raw-v1",
        split="train",
        revision=WIKITEXT_REVISION,
    )
    records = [{"text": text} for text in dataset["text"]]
    selected = take_window_slice(
        shuffled_document_windows(
            records,
            tokenizer,
            seed=args.seed,
            window_tokens=args.window_tokens,
        ),
        offset=args.offset,
        count=args.count,
    )
    output_dir = create_run_directory(args.output_root / args.model_id / args.set_id)
    prompts_path = output_dir / "prompts.jsonl"
    with prompts_path.open("x", encoding="utf-8") as handle:
        for index, row in enumerate(selected):
            handle.write(
                json.dumps(
                    {"evaluation_prompt_index": index, **row}, ensure_ascii=False
                )
                + "\n"
            )
    manifest = sanitize_manifest(
        {
            "set_id": args.set_id,
            "status": "complete",
            "project_commit": _git_commit(PROJECT_ROOT),
            "dataset_revision": WIKITEXT_REVISION,
            "dataset_fingerprint": dataset._fingerprint,
            "model_id": args.model_id,
            "model_revision": model_spec["revision"],
            "seed": args.seed,
            "window_tokens": args.window_tokens,
            "stream_offset": args.offset,
            "prompt_count": args.count,
            "fit_overlap": 0,
            "position_protocol": "last_token",
            "prompts_sha256": _file_sha256(prompts_path),
            "finished_at": datetime.now().astimezone().isoformat(),
        }
    )
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(output_dir)
    return 0


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_commit(root: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()


if __name__ == "__main__":
    raise SystemExit(main())
