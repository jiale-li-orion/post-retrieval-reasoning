import jlens

from jacobian_analysis.build_calibration_corpus import (
    WIKITEXT_REVISION,
    shuffled_document_windows,
    take_windows,
)


def test_wikitext_source_revision_is_immutable() -> None:
    assert len(WIKITEXT_REVISION) == 40


def test_external_jlens_package_is_not_shadowed() -> None:
    assert hasattr(jlens, "from_hf")
    assert "jacobian-lens" in str(jlens.__file__)


class _Tokenizer:
    def encode(self, text, add_special_tokens=False):
        assert add_special_tokens is False
        return [int(piece) for piece in text.split()]

    def decode(self, ids, skip_special_tokens=False, clean_up_tokenization_spaces=False):
        assert skip_special_tokens is False
        assert clean_up_tokenization_spaces is False
        return " ".join(str(item) for item in ids)


def test_calibration_windows_are_deterministic_and_do_not_cross_documents() -> None:
    records = [
        {"text": "0 1 2 3 4"},
        {"text": "10 11 12 13"},
        {"text": ""},
    ]

    first = list(
        shuffled_document_windows(records, _Tokenizer(), seed=17, window_tokens=2)
    )
    second = list(
        shuffled_document_windows(records, _Tokenizer(), seed=17, window_tokens=2)
    )

    assert first == second
    assert all(row["token_count"] == 2 for row in first)
    assert all("4 10" not in row["text"] for row in first)
    assert {row["source_record_index"] for row in first} == {0, 1}


def test_calibration_selection_fails_if_valid_windows_are_insufficient() -> None:
    try:
        take_windows(iter([{"text": "only"}]), 2)
    except ValueError as exc:
        assert "required 2" in str(exc)
    else:
        raise AssertionError("insufficient calibration windows must be fatal")
