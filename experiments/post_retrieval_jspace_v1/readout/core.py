"""Paired J-lens and logit-lens computation from one activation capture."""

from __future__ import annotations

from typing import Any, Mapping

import torch


@torch.no_grad()
def compute_paired_readouts(
    activations: Mapping[int, torch.Tensor],
    *,
    positions: Mapping[str, int],
    lens: Any,
    model: Any,
) -> list[dict[str, Any]]:
    generated = [name for name in positions if name.lower().startswith("generated")]
    if generated:
        raise ValueError(
            f"generated positions are secondary and cannot enter primary readout: {generated}"
        )
    rows = []
    for layer in lens.source_layers:
        if layer not in activations:
            raise ValueError(f"captured activation missing source layer {layer}")
        full = activations[layer]
        if full.ndim == 3:
            if full.shape[0] != 1:
                raise ValueError("readout accepts one prompt at a time")
            full = full[0]
        if full.ndim != 2:
            raise ValueError(f"layer {layer} activation must have shape [seq, d_model]")
        for position_type, position_index in positions.items():
            residual = full[position_index].float()
            logit_logits = model.unembed(residual).float().cpu()
            transported = lens.transport(residual, layer)
            j_logits = model.unembed(transported).float().cpu()
            rows.append(
                {
                    "layer": layer,
                    "position_type": position_type,
                    "position_index": position_index,
                    "j_logits": j_logits,
                    "logit_logits": logit_logits,
                }
            )
    return rows
