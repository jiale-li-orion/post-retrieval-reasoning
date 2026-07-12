import hashlib

import pytest

from adapters.atm import ATMItem
from interventions.generate_va_cache import build_annotation_work

from interventions.verbal_annotation import (
    AnnotationCacheError,
    apply_annotation_cache,
    build_verbal_r3_messages,
    parse_verbal_r3_output,
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
    assert result[0][: len(chunks[0])] == chunks[0]
    assert result[1][: len(chunks[1])] == chunks[1]
    assert "comment-e2" in result[0]
    assert "comment-e1" in result[1]


def test_annotation_cache_rejects_sgm_hash_mismatch() -> None:
    with pytest.raises(AnnotationCacheError, match="SGM hash mismatch"):
        apply_annotation_cache(
            "qa-1", ("e1",), ["ID: e1\n"], [_row("e1", "different", 0)]
        )


def test_annotation_cache_preserves_trailing_sgm_whitespace() -> None:
    chunk = "ID: e1\nCaption: first\n\n"

    result = apply_annotation_cache("qa-1", ("e1",), [chunk], [_row("e1", chunk, 0)])

    assert result[0].startswith(chunk)


def test_annotation_cache_rejects_missing_record() -> None:
    with pytest.raises(AnnotationCacheError, match="missing annotation"):
        apply_annotation_cache("qa-1", ("e1",), ["ID: e1\n"], [])


def test_annotation_cache_rejects_duplicate_record() -> None:
    chunk = "ID: e1\n"
    row = _row("e1", chunk, 0)
    with pytest.raises(AnnotationCacheError, match="duplicate annotation"):
        apply_annotation_cache("qa-1", ("e1",), [chunk], [row, row])


def test_canonical_annotation_is_reusable_at_a_different_pool_position() -> None:
    first = "ID: e2\n"
    second = "ID: e1\n"
    row = _row("e1", second, 0)

    result = apply_annotation_cache(
        "qa-1", ("e2", "e1"), [first, second], [_row("e2", first, 4), row]
    )

    assert result[1].startswith(second)


def test_official_server_prompt_wraps_question_and_document() -> None:
    messages = build_verbal_r3_messages("When?", "ID: e1\nTimestamp: today")

    assert messages[0]["role"] == "system"
    assert "reason internally" in messages[0]["content"]
    assert messages[1] == {
        "role": "user",
        "content": "Question: When?\nDocument: ID: e1\nTimestamp: today\n",
    }


def test_verbal_r3_parser_requires_exact_comment_and_score() -> None:
    parsed = parse_verbal_r3_output(
        "Comment: The document gives the requested date.\nScore: 5"
    )
    assert parsed == ("The document gives the requested date.", 5)

    with pytest.raises(AnnotationCacheError, match="cannot parse"):
        parse_verbal_r3_output("This seems relevant: 5")

    with pytest.raises(AnnotationCacheError, match="outside 1-5"):
        parse_verbal_r3_output("Comment: relevant\nScore: 6")


class _FakeATM:
    def load_split(self, split):
        assert split == "full"
        return [ATMItem("qa", "question", "number", "2", ("e1",))]

    def load_niah(self, k):
        return [
            ATMItem(
                "qa",
                "question",
                "number",
                "2",
                ("e1",),
                ("e2", "e1"),
            )
        ]

    def collect_sgm_chunks(self, evidence_ids):
        return [f"ID: {evidence_id}\n" for evidence_id in evidence_ids]


def test_canonical_work_deduplicates_full_and_all_niah_conditions() -> None:
    work = build_annotation_work(_FakeATM(), "canonical-e1")

    assert [(row["qa_id"], row["evidence_id"]) for row in work] == [
        ("qa", "e1"),
        ("qa", "e2"),
    ]
    assert work[0]["source_conditions"] == ["C1", "C7", "C8", "C9", "C10"]
