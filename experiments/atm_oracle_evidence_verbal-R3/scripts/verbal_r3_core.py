"""Pure protocol helpers for the ATM-Bench Verbal Annotation experiment."""

from __future__ import annotations

import json
import re
import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence


class RerankerParseError(ValueError):
    """Raised when a reranker response violates the official output contract."""


@dataclass(frozen=True)
class ParsedAnnotation:
    comment: str
    score: int


@dataclass(frozen=True)
class RerankerConfig:
    model: str
    revision: str
    prompt_source: str
    temperature: float
    top_p: float
    max_new_tokens: int
    seed: int
    max_parse_retries: int


@dataclass(frozen=True)
class AnswererConfig:
    temperature: float
    max_tokens: int
    timeout: int
    max_retries: int
    request_delay: float
    request_body: Mapping[str, Any]


@dataclass(frozen=True)
class EvidenceConfig:
    batch_fields: tuple[str, ...]
    niah_field: str


@dataclass(frozen=True)
class ExperimentConfig:
    protocol_version: str
    reranker: RerankerConfig
    answerer: AnswererConfig
    evidence: EvidenceConfig


def load_experiment_config(path: Path) -> ExperimentConfig:
    raw = json.loads(path.read_text(encoding="utf-8"))
    reranker = RerankerConfig(**raw["reranker"])
    answerer = AnswererConfig(**raw["answerer"])
    evidence_raw = raw["evidence"]
    evidence = EvidenceConfig(
        batch_fields=tuple(evidence_raw["batch_fields"]),
        niah_field=evidence_raw["niah_field"],
    )
    if "thinking" in answerer.request_body:
        raise ValueError("answerer.request_body must not contain thinking")
    if not 1 <= reranker.max_parse_retries:
        raise ValueError("reranker.max_parse_retries must be positive")
    return ExperimentConfig(
        protocol_version=raw["protocol_version"],
        reranker=reranker,
        answerer=answerer,
        evidence=evidence,
    )


def parse_reranker_output(response: str) -> ParsedAnnotation:
    comment_match = re.search(
        r"^\s*Comment\s*:\s*(.+?)\s*$", response, flags=re.IGNORECASE | re.MULTILINE
    )
    score_match = re.search(
        r"^\s*Score\s*:\s*([1-5])(?:\s*/\s*5)?\s*$",
        response,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    if not comment_match or not comment_match.group(1).strip():
        raise RerankerParseError("reranker output is missing a non-empty Comment")
    if not score_match:
        raise RerankerParseError("reranker output is missing a Score in [1, 5]")
    return ParsedAnnotation(
        comment=comment_match.group(1).strip(),
        score=int(score_match.group(1)),
    )


def append_verbal_annotation(chunk: str, comment: str, score: int) -> str:
    if not comment.strip():
        raise ValueError("comment must not be empty")
    if score not in range(1, 6):
        raise ValueError("score must be in [1, 5]")
    return (
        f"{chunk.rstrip()}\n"
        f"Verbal Annotation: {comment.strip()}\n"
        f"Relevance score: {score}\n"
    )


def count_tokens(tokenizer: Any, text: str) -> int:
    return len(tokenizer.encode(text, add_special_tokens=False))


def accumulate_generation_usage(
    *,
    prompt_tokens_per_attempt: int,
    completion_tokens_by_attempt: Sequence[int],
) -> tuple[int, int]:
    return (
        prompt_tokens_per_attempt * len(completion_tokens_by_attempt),
        sum(completion_tokens_by_attempt),
    )


def load_python_string_assignment(path: Path, variable_name: str) -> str:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == variable_name
            for target in node.targets
        ):
            continue
        value = ast.literal_eval(node.value)
        if isinstance(value, str):
            return value
    raise ValueError(f"string assignment {variable_name!r} not found in {path}")


def ensure_outputs_absent(paths: Iterable[Path]) -> None:
    existing = [path for path in paths if path.exists()]
    if existing:
        joined = ", ".join(str(path) for path in existing)
        raise FileExistsError(f"refusing to overwrite existing outputs: {joined}")


def load_evaluation_summary(eval_dir: Path) -> dict[str, Any]:
    summary_paths = sorted(eval_dir.glob("atm_*_summary.json"))
    result_paths = sorted(
        path
        for path in eval_dir.glob("atm_*.json")
        if not path.name.endswith("_summary.json")
    )
    if len(summary_paths) != 1 or len(result_paths) != 1:
        raise ValueError(
            f"expected one ATM summary and one ATM result in {eval_dir}; "
            f"found {len(summary_paths)} and {len(result_paths)}"
        )
    summary = json.loads(summary_paths[0].read_text(encoding="utf-8"))
    rows = json.loads(result_paths[0].read_text(encoding="utf-8"))
    return {
        "atm_qs": summary["accuracy"],
        "count": summary.get("count"),
        "by_qtype": summary.get("by_qtype", {}),
        "judge_fallback_count": sum(
            1 for row in rows if row.get("fallback_model_used") is True
        ),
        "summary_file": summary_paths[0].name,
        "result_file": result_paths[0].name,
    }


def _usage_value(usage: Any, name: str) -> Optional[int]:
    if usage is None:
        return None
    value = getattr(usage, name, None)
    return int(value) if value is not None else None


def build_answer_record(
    *,
    qa: Mapping[str, Any],
    evidence_ids: Sequence[str],
    answer: str,
    usage: Any,
    latency_ms: int,
    requested_model: str,
    returned_model: Optional[str],
) -> dict[str, Any]:
    return {
        "id": str(qa["id"]),
        "qa_id": str(qa["id"]),
        "qtype": qa.get("qtype"),
        "evidence_ids": list(evidence_ids),
        "answer": answer,
        "prompt_tokens": _usage_value(usage, "prompt_tokens"),
        "completion_tokens": _usage_value(usage, "completion_tokens"),
        "reasoning_tokens": _usage_value(usage, "reasoning_tokens"),
        "cached_tokens": _usage_value(usage, "cached_tokens"),
        "total_tokens": _usage_value(usage, "total_tokens"),
        "latency_ms": latency_ms,
        "requested_model": requested_model,
        "returned_model": returned_model,
    }


def build_annotation_record(
    *,
    qa_id: str,
    evidence_id: str,
    evidence_index: int,
    question: str,
    sgm_text: str,
    raw_output: str,
    comment: str,
    score: int,
    retry_count: int,
    prompt_tokens: int,
    completion_tokens: int,
    latency_ms: int,
    model: str,
    checkpoint_revision: str,
) -> dict[str, Any]:
    return {
        "qa_id": qa_id,
        "evidence_id": evidence_id,
        "evidence_index": evidence_index,
        "question": question,
        "sgm_text": sgm_text,
        "raw_output": raw_output,
        "comment": comment,
        "score": score,
        "parse_ok": True,
        "retry_count": retry_count,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "latency_ms": latency_ms,
        "model": model,
        "checkpoint_revision": checkpoint_revision,
    }
