"""Deterministic target extraction independent of model trajectories."""

from __future__ import annotations

import re
from typing import Any, Iterable, Sequence


_LIST_SPLIT = re.compile(r"\s*(?:,|;|\band\b|/)\s*", re.IGNORECASE)
_NUMBER = re.compile(r"(?<!\w)[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?!\w)")
_DATE = re.compile(r"\b(?:19|20)\d{2}[-/]\d{1,2}[-/]\d{1,2}\b")


def build_target_strings(gold_answer: str, qtype: str) -> list[str]:
    answer = str(gold_answer).strip()
    if qtype == "list_recall":
        return _dedupe(
            item.strip() for item in _LIST_SPLIT.split(answer) if item.strip()
        )
    candidates = [answer]
    candidates.extend(match.group(0).replace(",", "") for match in _NUMBER.finditer(answer))
    candidates.extend(match.group(0) for match in _DATE.finditer(answer))
    return _dedupe(item for item in candidates if item)


def tokenize_aliases(text: str, tokenizer: Any) -> dict[str, Any]:
    variants = _dedupe(
        [
            text,
            f" {text}",
            text.lower(),
            f" {text.lower()}",
            text.capitalize(),
            f" {text.capitalize()}",
        ]
    )
    aliases = []
    single_ids = []
    for variant in variants:
        token_ids = [
            int(item)
            for item in tokenizer.encode(variant, add_special_tokens=False)
        ]
        aliases.append({"text": variant, "token_ids": token_ids})
        if len(token_ids) == 1 and token_ids[0] not in single_ids:
            single_ids.append(token_ids[0])
    return {"aliases": aliases, "single_token_ids": single_ids}


def is_copyable(target: str, evidence_chunks: Sequence[str]) -> bool:
    normalized_target = _normalize_space(target).casefold()
    return any(
        normalized_target in _normalize_space(chunk).casefold()
        for chunk in evidence_chunks
    )


def build_decision_program_draft(
    *,
    qa_id: str,
    qtype: str,
    gold_answer: str,
    evidence_ids: Sequence[str],
    targets: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    copyable = [row["target_id"] for row in targets if row["copyable"]]
    derived = [row["target_id"] for row in targets if not row["copyable"]]
    operator = {
        "number": "unreviewed_numeric_operation",
        "list_recall": "selection",
        "open_end": "unreviewed_composition",
    }.get(qtype, "unreviewed")
    return {
        "qa_id": qa_id,
        "qtype": qtype,
        "review_status": "draft",
        "required_evidence_ids": list(evidence_ids),
        "entities": [],
        "attributes": [],
        "operands": [],
        "operators": [operator],
        "intermediates": [],
        "final_answer": gold_answer,
        "bindings": [],
        "copyable_targets": copyable,
        "derived_targets": derived,
    }


def _normalize_space(text: str) -> str:
    return " ".join(str(text).split())


def _dedupe(values: Iterable[str]) -> list[str]:
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result
