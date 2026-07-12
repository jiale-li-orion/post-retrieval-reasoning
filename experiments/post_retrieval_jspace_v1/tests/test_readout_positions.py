from types import SimpleNamespace

import pytest

from readout.positions import PositionError, resolve_text_positions


class CharacterTokenizer:
    def __call__(self, text, **kwargs):
        assert kwargs["add_special_tokens"] is False
        assert kwargs["return_offsets_mapping"] is True
        return {
            "input_ids": [ord(char) for char in text],
            "offset_mapping": [(index, index + 1) for index in range(len(text))],
        }


def test_positions_resolve_question_evidence_ends_and_answer_boundary() -> None:
    question = "What total?"
    chunks = ["ID: e1\nValue: 2", "ID: e2\nValue: 3"]
    rendered = (
        "<system>rules</system><user>Question: What total?\n\nEvidence:\n"
        "Evidence 1:\nID: e1\nValue: 2\n\n"
        "Evidence 2:\nID: e2\nValue: 3\n\nanswer</user><assistant>"
    )

    positions = resolve_text_positions(
        rendered,
        question=question,
        evidence_chunks=chunks,
        tokenizer=CharacterTokenizer(),
        actual_input_ids=[ord(char) for char in rendered],
    )

    assert rendered[positions.p_q] == "?"
    assert [rendered[index] for index in positions.evidence_ends] == ["2", "3"]
    assert positions.p_a0 == len(rendered) - 1


def test_position_resolution_rejects_tokenization_mismatch() -> None:
    with pytest.raises(PositionError, match="input IDs"):
        resolve_text_positions(
            "Question: q",
            question="q",
            evidence_chunks=[],
            tokenizer=CharacterTokenizer(),
            actual_input_ids=[1],
        )


def test_position_resolution_requires_unique_question() -> None:
    with pytest.raises(PositionError, match="question span"):
        resolve_text_positions(
            "Question: q Question: q",
            question="q",
            evidence_chunks=[],
            tokenizer=CharacterTokenizer(),
            actual_input_ids=[ord(char) for char in "Question: q Question: q"],
        )
