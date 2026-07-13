from behavior.summarize_pair import (
    behavior_stratum,
    correctness_transition,
    list_precision_recall,
    summarize_scores,
)


def test_correctness_transition_uses_perfect_score_as_correct() -> None:
    assert correctness_transition(1.0, 1.0) == "stable_success"
    assert correctness_transition(0.8, 1.0) == "repair"
    assert correctness_transition(1.0, 0.8) == "degradation"
    assert correctness_transition(0.8, 0.6) == "stable_failure"


def test_score_summary_preserves_partial_credit() -> None:
    summary = summarize_scores([1.0, 0.5, 0.0])

    assert summary == {"count": 3, "mean": 0.5, "perfect": 1}


def test_behavior_strata_are_mutually_exclusive() -> None:
    assert behavior_stratum(False, True, 1.0, 0.0) == "correct_to_abstain"
    assert behavior_stratum(False, True, 0.5, 0.0) == "partial_to_abstain"
    assert behavior_stratum(False, True, 0.0, 0.0) == "error_to_abstain"
    assert (
        behavior_stratum(False, True, 0.0, 1.0)
        == "abstention_without_score_harm"
    )
    assert behavior_stratum(True, True, 0.0, 0.0) == "stable_abstention"
    assert behavior_stratum(True, False, 0.0, 1.0) == "abstention_exit"
    assert (
        behavior_stratum(False, False, 1.0, 0.0)
        == "non_abstention_degradation"
    )
    assert behavior_stratum(False, False, 0.0, 0.0) == "stable_non_abstention"
    assert behavior_stratum(False, False, 0.0, 1.0) == "behavioral_repair"


def test_list_precision_recall_preserves_partial_matches() -> None:
    assert list_precision_recall({"a", "b"}, {"b", "c"}) == (0.5, 0.5)
    assert list_precision_recall({"a"}, set()) == (0.0, 0.0)
