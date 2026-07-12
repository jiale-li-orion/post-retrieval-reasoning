import pytest
import torch

from readout.metrics import candidate_entropy, rank_and_hits, summarize_trajectory


def test_rank_and_hits_use_one_based_competition_rank() -> None:
    result = rank_and_hits(torch.tensor([1.0, 3.0, 2.0]), target_id=2)

    assert result["rank"] == 2
    assert result["mrr"] == 0.5
    assert result["top1"] is False
    assert result["top5"] is True


def test_candidate_entropy_normalizes_only_frozen_candidates() -> None:
    entropy = candidate_entropy(torch.tensor([100.0, 0.0, 0.0]), [1, 2])

    assert entropy == pytest.approx(0.693147, rel=1e-5)


def test_trajectory_summary_reports_first_emergence_and_persistence() -> None:
    summary = summarize_trajectory([30, 20, 5, 4], top_k=10)

    assert summary["first_emergence_layer"] == 2
    assert summary["persistence"] == 0.5


def test_trajectory_without_emergence_is_explicit() -> None:
    summary = summarize_trajectory([30, 20], top_k=10)

    assert summary["first_emergence_layer"] is None
    assert summary["persistence"] == 0.0
