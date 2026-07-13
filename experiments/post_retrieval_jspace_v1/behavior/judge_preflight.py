#!/usr/bin/env python3
"""Run a secret-safe GPT judge transport smoke and record response metadata."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any


def response_record(response: Any, *, requested_model: str, latency: float) -> dict:
    usage = getattr(response, "usage", None)
    if hasattr(usage, "model_dump"):
        usage = usage.model_dump()
    elif usage is None:
        usage = {}
    return {
        "response_id": str(getattr(response, "id", "")),
        "requested_model": requested_model,
        "returned_model": str(getattr(response, "model", "")),
        "output_text": str(getattr(response, "output_text", "") or ""),
        "usage": usage,
        "latency_seconds": float(latency),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", default="gpt-5-mini:stable")
    parser.add_argument("--prompt-file", type=Path)
    parser.add_argument("--expect-judge-json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite: {args.output}")
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    if not api_key or not base_url:
        raise RuntimeError("OPENAI_API_KEY and OPENAI_BASE_URL are required")
    prompt = (
        args.prompt_file.read_text(encoding="utf-8")
        if args.prompt_file
        else 'Return only {"ok": true}.'
    )
    from openai import OpenAI

    client = OpenAI(api_key=api_key, base_url=base_url)
    started = time.perf_counter()
    response = client.responses.create(
        model=args.model,
        input=prompt,
        reasoning={"effort": "minimal"},
        max_output_tokens=600,
    )
    row = response_record(
        response, requested_model=args.model, latency=time.perf_counter() - started
    )
    if not row["output_text"].strip():
        raise RuntimeError("judge transport returned empty output")
    if args.expect_judge_json:
        payload = _parse_json_blob(row["output_text"])
        if normalize_accuracy(payload.get("accuracy")) is None:
            raise RuntimeError("judge response lacks boolean accuracy")
        payload["accuracy"] = normalize_accuracy(payload["accuracy"])
        row["parsed"] = payload
    row["base_url_sha256"] = hashlib.sha256(base_url.encode()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n")
    print(args.output)
    return 0


def _parse_json_blob(text: str) -> dict:
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise RuntimeError("judge response contains no JSON object")
    return json.loads(text[start : end + 1])


def normalize_accuracy(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.strip().casefold() in {"true", "false"}:
        return value.strip().casefold() == "true"
    return None


if __name__ == "__main__":
    raise SystemExit(main())
