"""Apply an answerer-independent Verbal Annotation cache."""

from __future__ import annotations

import hashlib
from collections import defaultdict
from typing import Any, Iterable, Sequence


class AnnotationCacheError(ValueError):
    """Raised when a cache cannot preserve the frozen evidence contract."""


def apply_annotation_cache(
    qa_id: str,
    evidence_ids: Sequence[str],
    sgm_chunks: Sequence[str],
    records: Iterable[dict[str, Any]],
) -> list[str]:
    if len(evidence_ids) != len(sgm_chunks):
        raise AnnotationCacheError("evidence IDs and SGM chunks differ in length")
    by_key: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        by_key[(str(row["qa_id"]), str(row["evidence_id"]))].append(row)

    annotated: list[str] = []
    for index, (evidence_id, chunk) in enumerate(
        zip(evidence_ids, sgm_chunks, strict=True)
    ):
        matches = by_key[(qa_id, evidence_id)]
        if not matches:
            raise AnnotationCacheError(
                f"missing annotation for qa={qa_id}, evidence={evidence_id}"
            )
        if len(matches) != 1:
            raise AnnotationCacheError(
                f"duplicate annotation for qa={qa_id}, evidence={evidence_id}"
            )
        row = matches[0]
        if row.get("parse_ok") is not True:
            raise AnnotationCacheError(
                f"unparsed annotation for qa={qa_id}, evidence={evidence_id}"
            )
        if int(row["evidence_index"]) != index:
            raise AnnotationCacheError(
                f"evidence index mismatch for qa={qa_id}, evidence={evidence_id}"
            )
        actual_hash = hashlib.sha256(chunk.encode("utf-8")).hexdigest()
        if row.get("sgm_sha256") != actual_hash:
            raise AnnotationCacheError(
                f"SGM hash mismatch for qa={qa_id}, evidence={evidence_id}"
            )
        score = int(row["score"])
        comment = str(row["comment"]).strip()
        if score not in range(1, 6) or not comment:
            raise AnnotationCacheError(
                f"invalid annotation payload for qa={qa_id}, evidence={evidence_id}"
            )
        annotated.append(
            f"{chunk.rstrip()}\n"
            f"Verbal Annotation: {comment}\n"
            f"Relevance score: {score}\n"
        )
    return annotated
