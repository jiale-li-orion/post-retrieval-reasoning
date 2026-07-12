import pytest

from behavior.run_behavior import (
    build_prediction_row,
    evidence_ids_for_condition,
    select_shard,
    select_condition_items,
    select_ground_truth_rows,
    validate_run_selection,
    validate_resume_prefix,
)
from adapters.atm import ATMItem
from behavior.evaluate import (
    build_evaluator_command,
    build_evaluator_environment,
    requires_llm_judge,
)


def test_gate_a_runner_rejects_unimplemented_condition() -> None:
    with pytest.raises(NotImplementedError, match="Raw"):
        validate_run_selection(
            "C2", "hard", {"C2": {"split": ["hard"], "evidence": "raw"}}
        )


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
        evidence_chunks=("chunk-2", "chunk-1"),
        prompt_payload="rendered prompt",
        latency_seconds=1.25,
    )

    assert row["evidence_ids"] == ["e2", "e1"]
    assert row["total_tokens"] == 12
    assert len(row["prompt_sha256"]) == 64
    assert len(row["evidence_sha256"]) == 2
    assert row["latency_seconds"] == 1.25


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


def test_official_evaluator_environment_exposes_atm_package(tmp_path) -> None:
    env = build_evaluator_environment(
        tmp_path / "ATM-Bench", {"PYTHONPATH": "/existing"}
    )

    assert env["PYTHONPATH"].split(":") == [
        str(tmp_path / "ATM-Bench"),
        "/existing",
    ]


def test_niah_conditions_use_frozen_niah_evidence() -> None:
    item = ATMItem(
        qa_id="qa",
        question="q",
        qtype="number",
        gold_answer="1",
        evidence_ids=("gold",),
        niah_evidence_ids=("distractor", "gold"),
    )

    assert evidence_ids_for_condition(item, {"evidence_selector": "evidence_ids"}) == (
        "gold",
    )
    assert evidence_ids_for_condition(
        item, {"evidence_selector": "niah_evidence_ids"}
    ) == ("distractor", "gold")


class _FakeATM:
    def load_split(self, split: str):
        return ["oracle", split]

    def load_niah(self, k: int):
        return ["niah", k]


def test_condition_selects_official_oracle_or_niah_dataset() -> None:
    assert select_condition_items(_FakeATM(), "hard", {}) == ["oracle", "hard"]
    assert select_condition_items(_FakeATM(), "hard", {"niah_k": 50}) == [
        "niah",
        50,
    ]


def test_shards_are_disjoint_and_cover_canonical_order() -> None:
    rows = list(range(10))
    shards = [select_shard(rows, index, 3) for index in range(3)]

    assert shards == [rows[:4], rows[4:7], rows[7:]]
    assert [item for shard in shards for item in shard] == rows


def test_resume_requires_existing_predictions_to_be_canonical_prefix() -> None:
    validate_resume_prefix(["q1", "q2"], ["q1", "q2", "q3"])

    with pytest.raises(ValueError, match="prefix"):
        validate_resume_prefix(["q2"], ["q1", "q2"])
