import pytest

from readout.run_atm_readout import validate_programs_frozen


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
