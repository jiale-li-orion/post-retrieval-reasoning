from behavior.summarize_pair import correctness_transition, summarize_scores


def test_correctness_transition_uses_perfect_score_as_correct() -> None:
    assert correctness_transition(1.0, 1.0) == "stable_success"
    assert correctness_transition(0.8, 1.0) == "repair"
    assert correctness_transition(1.0, 0.8) == "degradation"
    assert correctness_transition(0.8, 0.6) == "stable_failure"


def test_score_summary_preserves_partial_credit() -> None:
    summary = summarize_scores([1.0, 0.5, 0.0])

    assert summary == {"count": 3, "mean": 0.5, "perfect": 1}
