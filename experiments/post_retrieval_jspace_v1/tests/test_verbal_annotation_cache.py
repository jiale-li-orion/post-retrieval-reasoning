import hashlib

import pytest

from interventions.verbal_annotation import (
    AnnotationCacheError,
    apply_annotation_cache,
)


def _row(evidence_id: str, text: str, index: int) -> dict:
    return {
        "qa_id": "qa-1",
        "evidence_id": evidence_id,
        "evidence_index": index,
        "sgm_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "comment": f"comment-{evidence_id}",
        "score": 4,
        "parse_ok": True,
    }


def test_annotation_cache_preserves_item_count_and_order() -> None:
    evidence_ids = ("e2", "e1")
    chunks = ["ID: e2\nCaption: second\n", "ID: e1\nCaption: first\n"]

    result = apply_annotation_cache(
        "qa-1", evidence_ids, chunks, [_row("e2", chunks[0], 0), _row("e1", chunks[1], 1)]
    )

    assert len(result) == 2
    assert result[0].startswith(chunks[0])
    assert result[1].startswith(chunks[1])
    assert "comment-e2" in result[0]
    assert "comment-e1" in result[1]


def test_annotation_cache_rejects_sgm_hash_mismatch() -> None:
    with pytest.raises(AnnotationCacheError, match="SGM hash mismatch"):
        apply_annotation_cache(
            "qa-1", ("e1",), ["ID: e1\n"], [_row("e1", "different", 0)]
        )


def test_annotation_cache_rejects_missing_record() -> None:
    with pytest.raises(AnnotationCacheError, match="missing annotation"):
        apply_annotation_cache("qa-1", ("e1",), ["ID: e1\n"], [])


def test_annotation_cache_rejects_duplicate_record() -> None:
    chunk = "ID: e1\n"
    row = _row("e1", chunk, 0)
    with pytest.raises(AnnotationCacheError, match="duplicate annotation"):
        apply_annotation_cache("qa-1", ("e1",), [chunk], [row, row])
