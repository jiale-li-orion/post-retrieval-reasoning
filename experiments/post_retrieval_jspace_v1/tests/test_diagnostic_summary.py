import pandas as pd

from readout.summarize_diagnostic import (
    add_last_evidence_label,
    binary_auc,
    output_transition,
    target_margin,
)


def test_binary_auc_is_one_for_perfect_ordering():
    assert binary_auc([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9]) == 1.0


def test_binary_auc_handles_ties():
    assert binary_auc([0, 1], [0.5, 0.5]) == 0.5


def test_last_evidence_is_resolved_per_question():
    frame = pd.DataFrame(
        {
            "qa_id": ["a", "a", "b"],
            "position_type": [
                "P_evidence_end_0",
                "P_evidence_end_1",
                "P_evidence_end_0",
            ],
        }
    )
    labeled = add_last_evidence_label(frame)
    assert labeled["analysis_position"].tolist() == [
        "evidence_end",
        "last_evidence",
        "last_evidence",
    ]


def test_target_margin_pivots_unknown_minus_known():
    frame = pd.DataFrame(
        {
            "qa_id": ["a", "a"],
            "layer": [3, 3],
            "method": ["j_lens", "j_lens"],
            "analysis_position": ["P_a0", "P_a0"],
            "target_id": ["diagnostic_unknown", "diagnostic_known"],
            "score": [4.0, 1.5],
        }
    )
    result = target_margin(frame)
    assert result.iloc[0]["unknown_known_margin"] == 2.5


def test_output_transition_uses_exact_normalized_unknown():
    assert output_transition("answer", " Unknown\n") == "N->U"
    assert output_transition("unknown because...", "answer") == "N->N"
