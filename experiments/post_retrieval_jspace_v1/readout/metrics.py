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
