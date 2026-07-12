from targets.builder import (
    build_decision_program_draft,
    build_target_rows,
    build_target_strings,
    tokenize_aliases,
)


class FakeTokenizer:
    def encode(self, text, add_special_tokens=False):
        assert add_special_tokens is False
        table = {"42": [42], " 42": [1, 42], "hotel": [7], " Hotel": [8]}
        return table.get(text, [100, 101])


def test_number_targets_include_full_answer_and_numeric_value() -> None:
    targets = build_target_strings("I paid EUR 42.50", "number")

    assert "I paid EUR 42.50" in targets
    assert "42.50" in targets


def test_list_targets_preserve_individual_items() -> None:
    targets = build_target_strings("e1, e2", "list_recall")

    assert targets == ["e1", "e2"]


def test_token_aliases_record_single_and_multi_token_variants() -> None:
    result = tokenize_aliases("42", FakeTokenizer())

    assert result["single_token_ids"] == [42]
    assert any(len(alias["token_ids"]) == 2 for alias in result["aliases"])


def test_decision_program_is_explicitly_unreviewed() -> None:
    draft = build_decision_program_draft(
        qa_id="qa",
        qtype="number",
        gold_answer="42",
        evidence_ids=["e1"],
        targets=[{"target_id": "answer_0", "text": "42", "copyable": False}],
    )

    assert draft["review_status"] == "draft"
    assert draft["required_evidence_ids"] == ["e1"]
    assert draft["derived_targets"] == ["answer_0"]


def test_target_rows_record_copyability_and_each_model_tokenization() -> None:
    rows = build_target_rows(
        gold_answer="42",
        qtype="number",
        evidence_chunks=["Price: 42"],
        tokenizers={"model-a": FakeTokenizer(), "model-b": FakeTokenizer()},
    )

    assert rows[0]["copyable"] is True
    assert rows[0]["derived_candidate"] is False
    assert set(rows[0]["tokenization"]) == {"model-a", "model-b"}
