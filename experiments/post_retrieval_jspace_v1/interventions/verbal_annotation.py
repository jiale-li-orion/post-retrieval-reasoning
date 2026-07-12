"""Apply an answerer-independent Verbal Annotation cache."""

from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from typing import Any, Iterable, Sequence


class AnnotationCacheError(ValueError):
    """Raised when a cache cannot preserve the frozen evidence contract."""


VERBAL_R3_SYSTEM_PROMPT = """You are an evaluator that judges how informative a document is for answering a given question. You will receive a Question and a Document.

Carefully assess relevance and usefulness (reason internally), then output only a score and a brief, evidence-based comment that supports downstream filtering (mention concrete entities/claims/dates/metrics when helpful).

Scoring rubric (1-5):
1 — Unrelated: The document has nothing to do with the question. It does not contain any potentially relevant information or an answer to the question.
2 — Loosely related: Contains information that might potentially help or include the answer to the question, but is unlikely to do so.
3 — Partially informative: Contains information that can potentially help answer the question in some way.
4 — Substantively informative: Related to the question and includes information that is relevant to it.
5 — Direct answer: Clearly related and includes key information that can be used to directly answer the question.

Output format (exactly):
Comment: <concise justification citing specific evidence from the document; e.g., “Since the document states A and B, it is relevant to the question about C.”>
Score: <1-5>
"""


def build_verbal_r3_messages(question: str, document: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": VERBAL_R3_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Question: {question}\nDocument: {document}\n",
        },
    ]


def parse_verbal_r3_output(text: str) -> tuple[str, int]:
    match = re.fullmatch(
        r"\s*Comment:\s*(?P<comment>.+?)\s*Score:\s*(?P<score>\d+)\s*",
        text,
        flags=re.DOTALL,
    )
    if match is None:
        raise AnnotationCacheError("cannot parse Verbal-R3 Comment/Score output")
    comment = match.group("comment").strip()
    score = int(match.group("score"))
    if not comment:
        raise AnnotationCacheError("Verbal-R3 comment is empty")
    if score not in range(1, 6):
        raise AnnotationCacheError(f"Verbal-R3 score outside 1-5: {score}")
    return comment, score


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
        separator = "" if chunk.endswith("\n") else "\n"
        annotated.append(
            f"{chunk}{separator}"
            f"Verbal Annotation: {comment}\n"
            f"Relevance score: {score}\n"
        )
    return annotated
