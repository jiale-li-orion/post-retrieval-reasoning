"""Pure metric helpers shared by J-lens and logit-lens readout."""

from __future__ import annotations

from typing import Sequence

import torch


def rank_and_hits(logits: torch.Tensor, target_id: int) -> dict[str, float | int | bool]:
    if logits.ndim != 1:
        raise ValueError("rank metrics require one vocabulary-logit vector")
    score = logits[int(target_id)]
    rank = int((logits > score).sum().item()) + 1
    return {
        "score": float(score),
        "rank": rank,
        "mrr": 1.0 / rank,
        "top1": rank <= 1,
        "top5": rank <= 5,
        "top10": rank <= 10,
        "top25": rank <= 25,
    }


def candidate_entropy(logits: torch.Tensor, candidate_ids: Sequence[int]) -> float:
    if not candidate_ids:
        raise ValueError("candidate entropy requires a non-empty frozen set")
    selected = logits[torch.tensor(candidate_ids, device=logits.device)]
    probabilities = torch.softmax(selected.float(), dim=0)
    return float(-(probabilities * probabilities.log()).sum())


def summarize_trajectory(ranks: Sequence[int], *, top_k: int) -> dict[str, float | int | None]:
    if not ranks:
        raise ValueError("trajectory must contain at least one layer")
    hits = [rank <= top_k for rank in ranks]
    first = next((index for index, hit in enumerate(hits) if hit), None)
    return {
        "first_emergence_layer": first,
        "persistence": sum(hits) / len(hits),
    }


def summarize_target(
    logits: torch.Tensor,
    *,
    single_token_ids: Sequence[int],
    token_set_ids: Sequence[int],
    top_k: int = 25,
) -> dict[str, float | int | bool | None | list[int]]:
    """Summarize a frozen target without promoting multi-token phrases to ranks."""
    if logits.ndim != 1:
        raise ValueError("target summary requires one vocabulary-logit vector")
    k = min(int(top_k), int(logits.numel()))
    top_ids = [int(item) for item in torch.topk(logits, k=k).indices.tolist()]
    top_set = set(top_ids)
    frozen_set = {int(item) for item in token_set_ids}
    coverage = (
        len(frozen_set & top_set) / len(frozen_set) if frozen_set else None
    )
    candidates = []
    for token_id in dict.fromkeys(int(item) for item in single_token_ids):
        metrics = rank_and_hits(logits, token_id)
        candidates.append((int(metrics["rank"]), token_id, metrics))
    if not candidates:
        return {
            "eligible_primary": False,
            "best_token_id": None,
            "score": None,
            "rank": None,
            "mrr": None,
            "top1": False,
            "top5": False,
            "top10": False,
            "top25": False,
            "token_set_coverage": coverage,
            "top_token_ids": top_ids,
        }
    _, best_token_id, best = min(candidates, key=lambda item: item[0])
    return {
        "eligible_primary": True,
        "best_token_id": best_token_id,
        **best,
        "token_set_coverage": coverage,
        "top_token_ids": top_ids,
    }
