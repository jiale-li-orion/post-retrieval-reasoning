import pytest

from behavior.merge_shards import merge_prediction_rows


def test_merge_restores_canonical_qa_order() -> None:
    shards = [
        [{"qa_id": "q3"}],
        [{"qa_id": "q1"}, {"qa_id": "q2"}],
    ]

    assert merge_prediction_rows(shards, ["q1", "q2", "q3"]) == [
        {"qa_id": "q1"},
        {"qa_id": "q2"},
        {"qa_id": "q3"},
    ]


def test_merge_rejects_duplicate_or_missing_rows() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        merge_prediction_rows([[{"qa_id": "q1"}], [{"qa_id": "q1"}]], ["q1"])

    with pytest.raises(ValueError, match="missing"):
        merge_prediction_rows([[{"qa_id": "q1"}]], ["q1", "q2"])
