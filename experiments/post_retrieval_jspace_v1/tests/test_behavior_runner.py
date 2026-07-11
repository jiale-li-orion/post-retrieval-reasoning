import pytest

from behavior.run_behavior import build_prediction_row, validate_run_selection


def test_gate_a_runner_rejects_unimplemented_condition() -> None:
    with pytest.raises(NotImplementedError, match="C0 only"):
        validate_run_selection("C1", "hard", {"C1": {"split": ["hard"]}})


def test_gate_a_runner_rejects_unsupported_split() -> None:
    with pytest.raises(ValueError, match="does not support"):
        validate_run_selection("C0", "full", {"C0": {"split": ["hard"]}})


def test_prediction_row_preserves_evidence_order() -> None:
    row = build_prediction_row(
        qa_id="qa-1",
        qtype="number",
        evidence_ids=("e2", "e1"),
        answer="2",
        prompt_tokens=10,
        completion_tokens=2,
        model_id="model",
    )

    assert row["evidence_ids"] == ["e2", "e1"]
    assert row["total_tokens"] == 12
