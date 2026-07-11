import pytest

from behavior.run_behavior import (
    build_prediction_row,
    select_ground_truth_rows,
    validate_run_selection,
)
from behavior.evaluate import build_evaluator_command, requires_llm_judge


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


def test_smoke_ground_truth_contains_only_selected_predictions() -> None:
    rows = [{"id": "qa-1"}, {"id": "qa-2"}, {"id": "qa-3"}]

    selected = select_ground_truth_rows(rows, ["qa-2", "qa-1"])

    assert selected == [{"id": "qa-2"}, {"id": "qa-1"}]


def test_judge_key_is_required_only_for_open_end() -> None:
    deterministic = [{"id": "n", "qtype": "number"}]
    mixed = [*deterministic, {"id": "o", "qtype": "open_end"}]

    assert requires_llm_judge(deterministic) is False
    assert requires_llm_judge(mixed) is True


def test_official_evaluator_command_uses_frozen_inference_inputs(tmp_path) -> None:
    run_dir = tmp_path / "inference"
    eval_dir = tmp_path / "evaluation"
    command = build_evaluator_command(
        atm_root=tmp_path / "ATM-Bench",
        run_dir=run_dir,
        eval_dir=eval_dir,
        judge_model="gpt-5-mini",
        reasoning_effort="minimal",
    )

    assert command[1].endswith("memqa/utils/evaluator/evaluate_qa.py")
    assert command[command.index("--ground-truth") + 1] == str(
        run_dir / "ground_truth_subset.json"
    )
    assert command[command.index("--predictions") + 1] == str(
        run_dir / "predictions.jsonl"
    )
    assert command[command.index("--output-dir") + 1] == str(eval_dir)
    assert command[command.index("--judge-model") + 1] == "gpt-5-mini"
    assert command[command.index("--judge-reasoning-effort") + 1] == "minimal"
