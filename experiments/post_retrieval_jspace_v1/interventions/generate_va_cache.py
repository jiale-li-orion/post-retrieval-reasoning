#!/usr/bin/env python3
"""Generate an immutable, answerer-independent Verbal Annotation cache."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import torch
import yaml
from transformers import AutoModelForCausalLM, AutoTokenizer


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = EXPERIMENT_ROOT.parents[1]
if str(EXPERIMENT_ROOT) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_ROOT))

from adapters.atm import ATMAdapter  # noqa: E402
from core.run_contract import create_run_directory, sanitize_manifest  # noqa: E402
from interventions.verbal_annotation import (  # noqa: E402
    VERBAL_R3_SYSTEM_PROMPT,
    build_verbal_r3_messages,
    parse_verbal_r3_output,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=["full", "hard"], required=True)
    parser.add_argument("--cache-id", required=True)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument(
        "--cache-root",
        type=Path,
        default=Path("/home/lab/lab/research_artifacts/va_cache"),
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
    config_path = EXPERIMENT_ROOT / "registry/verbal_annotation.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    model_spec = config["model"]
    model_path = Path(model_spec["local_path"])
    output_dir = create_run_directory(args.cache_root / args.split / args.cache_id)
    records_path = output_dir / "annotations.jsonl"
    started_at = datetime.now().astimezone().isoformat()

    random.seed(args.seed)
    torch.manual_seed(args.seed)
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        local_files_only=True,
        dtype=torch.bfloat16,
    ).to("cuda").eval()

    atm = ATMAdapter(args.atm_root)
    items = atm.load_split(args.split)
    if args.limit is not None:
        items = items[: args.limit]
    record_count = 0
    with records_path.open("x", encoding="utf-8") as handle:
        for item in items:
            chunks = atm.collect_sgm_chunks(item.evidence_ids)
            for index, (evidence_id, chunk) in enumerate(
                zip(item.evidence_ids, chunks, strict=True)
            ):
                row = _annotate(
                    model=model,
                    tokenizer=tokenizer,
                    question=item.question,
                    document=chunk,
                    max_retries=args.max_retries,
                    decoding=config["decoding"],
                )
                row.update(
                    {
                        "qa_id": item.qa_id,
                        "evidence_id": evidence_id,
                        "evidence_index": index,
                        "sgm_sha256": _text_sha256(chunk),
                    }
                )
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                handle.flush()
                record_count += 1

    manifest = sanitize_manifest(
        {
            "cache_id": args.cache_id,
            "status": "complete",
            "project_commit": _git_commit(PROJECT_ROOT),
            "split": args.split,
            "limit": args.limit,
            "seed": args.seed,
            "record_count": record_count,
            "model": model_spec,
            "decoding": config["decoding"],
            "prompt_source": config["prompt_source"],
            "prompt_sha256": _text_sha256(VERBAL_R3_SYSTEM_PROMPT),
            "config_sha256": _file_sha256(config_path),
            "dataset_sha256": atm.split_sha256(args.split),
            "annotations_sha256": _file_sha256(records_path),
            "started_at": started_at,
            "finished_at": datetime.now().astimezone().isoformat(),
        }
    )
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(output_dir)
    return 0


@torch.inference_mode()
def _annotate(
    *,
    model: Any,
    tokenizer: Any,
    question: str,
    document: str,
    max_retries: int,
    decoding: dict[str, Any],
) -> dict[str, Any]:
    messages = build_verbal_r3_messages(question, document)
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        started = time.perf_counter()
        output = model.generate(
            **inputs,
            do_sample=True,
            temperature=float(decoding["temperature"]),
            top_p=float(decoding["top_p"]),
            max_new_tokens=int(decoding["max_new_tokens"]),
        )
        generated = output[:, inputs["input_ids"].shape[-1] :]
        raw = tokenizer.batch_decode(generated, skip_special_tokens=True)[0].strip()
        try:
            comment, score = parse_verbal_r3_output(raw)
            return {
                "comment": comment,
                "score": score,
                "raw_output": raw,
                "parse_ok": True,
                "attempt": attempt + 1,
                "prompt_tokens": int(inputs["input_ids"].shape[-1]),
                "completion_tokens": int(generated.shape[-1]),
                "latency_seconds": time.perf_counter() - started,
            }
        except Exception as exc:  # retry is part of the frozen protocol
            last_error = exc
    raise RuntimeError(f"Verbal-R3 parse failed after retries: {last_error}")


def _git_commit(root: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()


def _text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
