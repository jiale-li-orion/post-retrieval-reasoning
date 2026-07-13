import pytest
import torch

from readout.metrics import (
    candidate_entropy,
    rank_and_hits,
    summarize_target,
    summarize_trajectory,
)


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


def test_target_summary_uses_best_single_token_alias() -> None:
    result = summarize_target(
        torch.tensor([0.0, 4.0, 3.0, 2.0]),
        single_token_ids=[2, 1],
        token_set_ids=[1, 2],
        top_k=2,
    )

    assert result["eligible_primary"] is True
    assert result["best_token_id"] == 1
    assert result["rank"] == 1
    assert result["token_set_coverage"] == 1.0


def test_multitoken_target_reports_coverage_without_primary_rank() -> None:
    result = summarize_target(
        torch.tensor([0.0, 4.0, 3.0, 2.0]),
        single_token_ids=[],
        token_set_ids=[1, 3],
        top_k=2,
    )

    assert result["eligible_primary"] is False
    assert result["rank"] is None
    assert result["token_set_coverage"] == 0.5
