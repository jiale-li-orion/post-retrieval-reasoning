"""Resolve silent readout positions against the exact rendered prompt."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence


class PositionError(ValueError):
    """Raised when a semantic prompt span cannot be mapped to model tokens."""


@dataclass(frozen=True)
class ReadoutPositions:
    evidence_ends: tuple[int, ...]
    p_q: int
    p_a0: int


def resolve_text_positions(
    rendered_prompt: str,
    *,
    question: str,
    evidence_chunks: Sequence[str],
    tokenizer: Any,
    actual_input_ids: Any,
) -> ReadoutPositions:
    encoded = tokenizer(
        rendered_prompt,
        add_special_tokens=False,
        return_offsets_mapping=True,
    )
    token_ids = _flat_ids(encoded["input_ids"])
    actual_ids = _flat_ids(actual_input_ids)
    if token_ids != actual_ids:
        raise PositionError("offset tokenizer input IDs differ from model input IDs")
    offsets = [tuple(pair) for pair in encoded["offset_mapping"]]
    if len(offsets) != len(actual_ids):
        raise PositionError("offset count differs from model input IDs")

    question_marker = f"Question: {question}"
    question_starts = _all_occurrences(rendered_prompt, question_marker)
    if len(question_starts) != 1:
        raise PositionError(
            f"question span must occur exactly once; found {len(question_starts)}"
        )
    question_end = question_starts[0] + len(question_marker)

    evidence_ends = []
    cursor = question_end
    for index, chunk in enumerate(evidence_chunks):
        start = rendered_prompt.find(chunk, cursor)
        if start < 0:
            raise PositionError(f"evidence span {index} was not found after prior span")
        evidence_ends.append(_token_at_char(offsets, _last_content_char(rendered_prompt, start, start + len(chunk))))
        cursor = start + len(chunk)

    return ReadoutPositions(
        evidence_ends=tuple(evidence_ends),
        p_q=_token_at_char(
            offsets,
            _last_content_char(
                rendered_prompt, question_starts[0], question_end
            ),
        ),
        p_a0=len(actual_ids) - 1,
    )


def _flat_ids(value: Any) -> list[int]:
    if hasattr(value, "tolist"):
        value = value.tolist()
    if value and isinstance(value[0], list):
        if len(value) != 1:
            raise PositionError("position resolver accepts one prompt at a time")
        value = value[0]
    return [int(item) for item in value]


def _all_occurrences(text: str, needle: str) -> list[int]:
    starts = []
    cursor = 0
    while True:
        found = text.find(needle, cursor)
        if found < 0:
            return starts
        starts.append(found)
        cursor = found + 1


def _last_content_char(text: str, start: int, end: int) -> int:
    while end > start and text[end - 1].isspace():
        end -= 1
    if end == start:
        raise PositionError("semantic span contains no content characters")
    return end - 1


def _token_at_char(offsets: Sequence[tuple[int, int]], char_index: int) -> int:
    for token_index, (start, end) in enumerate(offsets):
        if start <= char_index < end:
            return token_index
    raise PositionError(f"no model token covers character index {char_index}")
