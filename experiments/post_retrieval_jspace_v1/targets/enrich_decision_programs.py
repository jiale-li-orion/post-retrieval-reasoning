#!/usr/bin/env python3
"""Generate reviewable Hard-31 decision programs without freezing them."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any


ENRICHMENT_FIELDS = (
    "required_evidence_ids",
    "entities",
    "attributes",
    "operands",
    "operators",
    "intermediates",
    "bindings",
    "decoys",
    "evidence_provenance",
)


def decision_program_response_format() -> dict[str, Any]:
    properties: dict[str, Any] = {
        "required_evidence_ids": {"type": "array", "items": {"type": "string"}}
    }
    properties.update(
        {
            field: {
                "type": "array",
                "items": {"type": "object", "additionalProperties": True},
            }
            for field in ENRICHMENT_FIELDS
            if field != "required_evidence_ids"
        }
    )
    return {
        "type": "json_schema",
        "name": "atm_decision_program",
        "schema": {
            "type": "object",
            "properties": properties,
            "required": list(ENRICHMENT_FIELDS),
            "additionalProperties": False,
        },
        "strict": False,
    }


def merge_enrichment(
    original: dict[str, Any],
    enrichment: dict[str, Any],
    *,
    oracle_evidence_ids: set[str],
) -> dict[str, Any]:
    enrichment = dict(enrichment)
    provenance = enrichment.get("evidence_provenance")
    if isinstance(provenance, dict):
        enrichment["evidence_provenance"] = [
            {"evidence_id": str(evidence_id), "supports": supports}
            for evidence_id, supports in provenance.items()
        ]
    missing = [field for field in ENRICHMENT_FIELDS if field not in enrichment]
    if missing:
        raise ValueError(f"enrichment missing fields: {missing}")
    for field in ENRICHMENT_FIELDS:
        if not isinstance(enrichment[field], list):
            raise ValueError(f"enrichment field must be a list: {field}")
    required = {str(item) for item in enrichment["required_evidence_ids"]}
    if not required or not required <= oracle_evidence_ids:
        raise ValueError("required evidence must be a non-empty oracle subset")
    result = dict(original)
    result.update({field: enrichment[field] for field in ENRICHMENT_FIELDS})
    result["review_status"] = "draft_enriched"
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--programs", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model", default="gpt-5-mini:stable")
    parser.add_argument("--atm-root", type=Path, required=True)
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--request-delay", type=float, default=10.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    if not api_key or not base_url:
        raise RuntimeError("OPENAI_API_KEY and OPENAI_BASE_URL are required")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_path = args.output_dir / "enrichments.jsonl"
    merged_path = args.output_dir / "hard_decision_programs.enriched.jsonl"
    if merged_path.exists():
        raise FileExistsError(f"refusing to overwrite: {merged_path}")

    import sys

    experiment_root = Path(__file__).resolve().parents[1]
    if str(experiment_root) not in sys.path:
        sys.path.insert(0, str(experiment_root))
    from adapters.atm import ATMAdapter
    from openai import OpenAI

    programs = _load_jsonl(args.programs)
    atm = ATMAdapter(args.atm_root)
    hard = {item.qa_id: item for item in atm.load_split("hard")}
    if len(programs) != 31 or set(hard) != {str(row["qa_id"]) for row in programs}:
        raise ValueError("enrichment requires canonical Hard 31")
    existing = {
        str(row["qa_id"]): row for row in _load_jsonl(output_path)
    } if output_path.exists() else {}
    client = OpenAI(api_key=api_key, base_url=base_url)

    for index, program in enumerate(programs, start=1):
        qa_id = str(program["qa_id"])
        if qa_id in existing:
            continue
        item = hard[qa_id]
        chunks = atm.collect_sgm_chunks(item.evidence_ids)
        prompt = _build_prompt(item, chunks)
        response, enrichment, retry_failures = request_parsed_enrichment(
            client,
            model=args.model,
            prompt=prompt,
            oracle_evidence_ids=set(item.evidence_ids),
            max_retries=args.max_retries,
            delay=args.request_delay,
        )
        usage = response.usage.model_dump() if response.usage else {}
        record = {
            "qa_id": qa_id,
            "requested_model": args.model,
            "returned_model": str(response.model),
            "usage": usage,
            "retry_count": len(retry_failures),
            "retry_failures": retry_failures,
            "enrichment": enrichment,
        }
        _append_jsonl(output_path, record)
        existing[qa_id] = record
        print(f"[{index}/31] {qa_id}", flush=True)
        time.sleep(args.request_delay)

    merged = []
    for program in programs:
        qa_id = str(program["qa_id"])
        item = hard[qa_id]
        merged.append(
            merge_enrichment(
                program,
                existing[qa_id]["enrichment"],
                oracle_evidence_ids=set(item.evidence_ids),
            )
        )
    merged_path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in merged) + "\n",
        encoding="utf-8",
    )
    print(merged_path)
    return 0


def _build_prompt(item: Any, chunks: list[str]) -> str:
    evidence = "\n\n".join(
        f"[Evidence {evidence_id}]\n{chunk}"
        for evidence_id, chunk in zip(item.evidence_ids, chunks, strict=True)
    )
    return f"""You are preparing a human-reviewable decision program for an ATM-Bench question. Do not judge a model response and do not infer from model trajectories. Use only the question, gold answer, and oracle evidence below.

Return one JSON object with exactly these list-valued fields:
required_evidence_ids, entities, attributes, operands, operators, intermediates, bindings, decoys, evidence_provenance.

Use structured objects, not vague prose. Every factual object must cite evidence_ids. Give operands stable IDs; operators name inputs and outputs; intermediates state their derivation. Decoys must be plausible evidence-grounded alternatives, not invented facts. Empty lists are allowed only when a field is genuinely inapplicable. required_evidence_ids must be a non-empty subset of the supplied IDs. Do not include review_status or final_answer.

Question type: {item.qtype}
Question: {item.question}
Gold answer: {item.gold_answer}

{evidence}
"""


def request_parsed_enrichment(
    client: Any,
    *,
    model: str,
    prompt: str,
    oracle_evidence_ids: set[str],
    max_retries: int,
    delay: float,
) -> tuple[Any, dict[str, Any], list[dict[str, Any]]]:
    error: Exception | None = None
    failures: list[dict[str, Any]] = []
    for attempt in range(max_retries):
        response: Any | None = None
        try:
            response = client.responses.create(
                model=model,
                input=prompt,
                reasoning={"effort": "minimal"},
                max_output_tokens=8000,
                text={"format": decision_program_response_format()},
            )
            enrichment = _parse_json_blob(response.output_text)
            validated = merge_enrichment(
                {}, enrichment, oracle_evidence_ids=oracle_evidence_ids
            )
            normalized = {field: validated[field] for field in ENRICHMENT_FIELDS}
            return response, normalized, failures
        except Exception as exc:
            error = exc
            output_text = str(getattr(response, "output_text", "") or "")
            failures.append(
                {
                    "attempt": attempt + 1,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "output_sha256": (
                        hashlib.sha256(output_text.encode()).hexdigest()
                        if output_text
                        else None
                    ),
                }
            )
            if attempt + 1 < max_retries:
                time.sleep(delay * (2**attempt))
    raise RuntimeError(f"decision-program enrichment failed after {max_retries} attempts") from error


def _parse_json_blob(text: str) -> dict[str, Any]:
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("enrichment response contains no JSON object")
    payload = json.loads(text[start : end + 1])
    if not isinstance(payload, dict):
        raise ValueError("enrichment response must be an object")
    return payload


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


if __name__ == "__main__":
    raise SystemExit(main())
