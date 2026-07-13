import pytest

from readout.run_atm_readout import merge_target_rows, validate_programs_frozen


def test_formal_readout_rejects_draft_decision_programs() -> None:
    with pytest.raises(ValueError, match="not frozen"):
        validate_programs_frozen(
            [{"qa_id": "q1", "review_status": "draft"}],
            ["q1"],
            allow_draft=False,
        )


def test_smoke_may_explicitly_use_draft_programs() -> None:
    validate_programs_frozen(
        [{"qa_id": "q1", "review_status": "draft"}],
        ["q1"],
        allow_draft=True,
    )


def test_hard_program_targets_override_automatic_targets() -> None:
    rows = merge_target_rows(
        [{"qa_id": "q1", "targets": ["automatic"]}],
        [{"qa_id": "q1", "targets": ["reviewed"]}],
    )

    assert rows["q1"]["targets"] == ["reviewed"]
