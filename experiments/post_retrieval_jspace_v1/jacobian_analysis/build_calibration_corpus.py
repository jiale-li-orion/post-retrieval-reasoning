#!/usr/bin/env python3
"""Build frozen, model-specific WikiText-103 token windows."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Iterator

from datasets import load_dataset
from transformers import AutoTokenizer


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = EXPERIMENT_ROOT.parents[1]
WIKITEXT_REVISION = "b08601e04326c79dfdd32d625aee71d232d685c3"
if str(EXPERIMENT_ROOT) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_ROOT))

from core.registry import load_model_registry  # noqa: E402
from core.run_contract import create_run_directory, sanitize_manifest  # noqa: E402


def shuffled_document_windows(
    records: list[dict[str, Any]],
    tokenizer: Any,
    *,
    seed: int,
    window_tokens: int,
) -> Iterator[dict[str, Any]]:
    indices = [index for index, row in enumerate(records) if str(row["text"]).strip()]
    random.Random(seed).shuffle(indices)
    for source_index in indices:
        token_ids = tokenizer.encode(
            str(records[source_index]["text"]), add_special_tokens=False
        )
        for window_index, start in enumerate(
            range(0, len(token_ids) - window_tokens + 1, window_tokens)
        ):
            window = token_ids[start : start + window_tokens]
            text = tokenizer.decode(
                window,
                skip_special_tokens=False,
                clean_up_tokenization_spaces=False,
            )
            roundtrip = tokenizer.encode(text, add_special_tokens=False)
            if roundtrip != window:
                continue
            yield {
                "source_record_index": source_index,
                "document_window_index": window_index,
                "token_count": len(window),
                "token_ids_sha256": _token_ids_sha256(window),
                "text": text,
            }


def take_windows(rows: Iterable[dict[str, Any]], count: int) -> list[dict[str, Any]]:
    selected = []
    for row in rows:
        selected.append(row)
        if len(selected) == count:
            return selected
    raise ValueError(f"only found {len(selected)} valid windows; required {count}")


def take_window_slice(
    rows: Iterable[dict[str, Any]], *, offset: int, count: int
) -> list[dict[str, Any]]:
    if offset < 0 or count <= 0:
        raise ValueError("offset must be non-negative and count must be positive")
    iterator = iter(rows)
    for _ in range(offset):
        try:
            next(iterator)
        except StopIteration as exc:
            raise ValueError(f"window stream ended before offset {offset}") from exc
    return take_windows(iterator, count)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--corpus-id", required=True)
    parser.add_argument("--count", type=int, default=512)
    parser.add_argument("--window-tokens", type=int, default=256)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("/home/lab/lab/research_data/wikitext103/calibration"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.count <= 0 or args.window_tokens <= 0:
        raise ValueError("count and window size must be positive")
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
    selected = take_windows(
        shuffled_document_windows(
            records,
            tokenizer,
            seed=args.seed,
            window_tokens=args.window_tokens,
        ),
        args.count,
    )

    output_dir = create_run_directory(
        args.output_root / args.model_id / args.corpus_id
    )
    windows_path = output_dir / "windows.jsonl"
    with windows_path.open("x", encoding="utf-8") as handle:
        for index, row in enumerate(selected):
            handle.write(
                json.dumps({"window_index": index, **row}, ensure_ascii=False) + "\n"
            )

    manifest = sanitize_manifest(
        {
            "corpus_id": args.corpus_id,
            "status": "complete",
            "project_commit": _git_commit(PROJECT_ROOT),
            "dataset": {
                "repository": "Salesforce/wikitext",
                "configuration": "wikitext-103-raw-v1",
                "revision": WIKITEXT_REVISION,
                "split": "train",
                "record_count": len(records),
                "fingerprint": dataset._fingerprint,
            },
            "model_id": args.model_id,
            "model_revision": model_spec["revision"],
            "model_manifest_sha256": model_spec["file_manifest_sha256"],
            "tokenizer_class": type(tokenizer).__name__,
            "seed": args.seed,
            "window_tokens": args.window_tokens,
            "window_count": len(selected),
            "cross_document_windows": False,
            "drop_incomplete_windows": True,
            "roundtrip_token_check": True,
            "windows_sha256": _file_sha256(windows_path),
            "finished_at": datetime.now().astimezone().isoformat(),
        }
    )
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(output_dir)
    return 0


def _token_ids_sha256(token_ids: list[int]) -> str:
    canonical = json.dumps(token_ids, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(canonical).hexdigest()


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
