from types import SimpleNamespace

from targets.builder import (
    build_decision_program_draft,
    build_target_rows,
    build_target_strings,
    tokenize_aliases,
)
from targets.enrich_decision_programs import (
    decision_program_response_format,
    merge_enrichment,
    request_parsed_enrichment,
)
from targets.audit_expressibility import classify_text_target


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


def test_enriched_program_remains_unreviewed_and_preserves_frozen_fields() -> None:
    original = {
        "qa_id": "q1",
        "qtype": "number",
        "review_status": "draft",
        "required_evidence_ids": ["e1"],
        "final_answer": "3",
        "targets": [{"target_id": "answer_0"}],
    }
    enrichment = {
        "required_evidence_ids": ["e1"],
        "entities": [{"name": "hotel", "evidence_ids": ["e1"]}],
        "attributes": [],
        "operands": [{"operand_id": "o1", "value": "1", "evidence_ids": ["e1"]}],
        "operators": [{"operator": "sum", "inputs": ["o1"], "output": "i1"}],
        "intermediates": [{"intermediate_id": "i1", "value": "3"}],
        "bindings": [],
        "decoys": [],
        "evidence_provenance": [{"evidence_id": "e1", "supports": ["o1"]}],
    }

    result = merge_enrichment(original, enrichment, oracle_evidence_ids={"e1"})

    assert result["qa_id"] == "q1"
    assert result["final_answer"] == "3"
    assert result["targets"] == original["targets"]
    assert result["review_status"] == "draft_enriched"
    assert result["operands"][0]["operand_id"] == "o1"


def test_enrichment_normalizes_provenance_mapping() -> None:
    original = {
        "qa_id": "q1",
        "qtype": "open_end",
        "review_status": "draft",
        "required_evidence_ids": ["e1"],
        "final_answer": "x",
        "targets": [],
    }
    enrichment = {
        "required_evidence_ids": ["e1"],
        "entities": [],
        "attributes": [],
        "operands": [],
        "operators": [],
        "intermediates": [],
        "bindings": [],
        "decoys": [],
        "evidence_provenance": {"e1": ["answer"]},
    }

    result = merge_enrichment(original, enrichment, oracle_evidence_ids={"e1"})

    assert result["evidence_provenance"] == [
        {"evidence_id": "e1", "supports": ["answer"]}
    ]


def test_expressibility_distinguishes_single_token_alias_and_phrase() -> None:
    tokenizer = FakeTokenizer()

    assert classify_text_target("hotel", tokenizer, sequence_level=False) == "A"
    assert classify_text_target("Hotel", tokenizer, sequence_level=False) == "B"
    assert classify_text_target("long phrase", tokenizer, sequence_level=False) == "C"
    assert classify_text_target("long phrase", tokenizer, sequence_level=True) == "D"


def test_decision_program_response_format_requires_all_fields() -> None:
    response_format = decision_program_response_format()

    assert response_format["type"] == "json_schema"
    assert set(response_format["schema"]["required"]) == {
        "required_evidence_ids",
        "entities",
        "attributes",
        "operands",
        "operators",
        "intermediates",
        "bindings",
        "decoys",
        "evidence_provenance",
    }


def test_enrichment_retries_malformed_structured_output() -> None:
    valid = {
        "required_evidence_ids": ["e1"],
        "entities": [],
        "attributes": [],
        "operands": [],
        "operators": [],
        "intermediates": [],
        "bindings": [],
        "decoys": [],
        "evidence_provenance": [],
    }

    class Responses:
        def __init__(self):
            self.calls = 0

        def create(self, **kwargs):
            self.calls += 1
            self.last_kwargs = kwargs
            text = '{"required_evidence_ids": ["e1"]' if self.calls == 1 else __import__("json").dumps(valid)
            return SimpleNamespace(output_text=text, model="gpt", usage=None)

    responses = Responses()
    client = SimpleNamespace(responses=responses)

    response, enrichment, failures = request_parsed_enrichment(
        client,
        model="gpt",
        prompt="prompt",
        oracle_evidence_ids={"e1"},
        max_retries=2,
        delay=0,
    )

    assert response.model == "gpt"
    assert enrichment == valid
    assert responses.calls == 2
    assert responses.last_kwargs["max_output_tokens"] == 8000
    assert failures[0]["error_type"] == "ValueError"
    assert len(failures[0]["output_sha256"]) == 64


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
