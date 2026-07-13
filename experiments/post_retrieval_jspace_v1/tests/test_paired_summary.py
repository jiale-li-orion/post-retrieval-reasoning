import pandas as pd

from readout.summarize_paired import pair_readouts, transition_label


def test_pair_readouts_computes_condition_delta_on_identical_keys() -> None:
    base = {
        "qa_id": "q",
        "qtype": "number",
        "layer": 1,
        "normalized_depth": 0.5,
        "position_type": "P_q",
        "position_index": 3,
        "readout_kind": "jacobian",
        "target_id": "answer_0",
        "target_text": "42",
        "copyable": False,
        "derived_candidate": True,
        "method": "j_lens",
        "eligible_primary": True,
        "rank": 5,
        "mrr": 0.2,
        "score": 1.0,
        "token_set_coverage": 0.5,
    }
    c0 = pd.DataFrame([base])
    c1 = pd.DataFrame(
        [
            {
                **base,
                "rank": 2,
                "mrr": 0.5,
                "score": 4.0,
                "token_set_coverage": 1.0,
            }
        ]
    )

    paired = pair_readouts(c0, c1)

    assert paired.iloc[0]["delta_score"] == 3.0
    assert paired.iloc[0]["delta_rank"] == -3
    assert paired.iloc[0]["delta_token_set_coverage"] == 0.5


def test_transition_requires_perfect_deterministic_score() -> None:
    assert transition_label(0.5, 1.0) == "repair"
    assert transition_label(1.0, 0.5) == "degradation"
    assert transition_label(0.5, 0.7) == "stable_failure"
    assert transition_label(1.0, 1.0) == "stable_success"
