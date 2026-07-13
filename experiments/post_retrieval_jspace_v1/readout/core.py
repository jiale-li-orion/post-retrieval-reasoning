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
    target_layer: int,
) -> list[dict[str, Any]]:
    generated = [name for name in positions if name.lower().startswith("generated")]
    if generated:
        raise ValueError(
            f"generated positions are secondary and cannot enter primary readout: {generated}"
        )
    rows = []
    layers = [*lens.source_layers, target_layer]
    position_items = list(positions.items())
    position_indices = [index for _, index in position_items]
    for layer in layers:
        if layer not in activations:
            raise ValueError(f"captured activation missing source layer {layer}")
        full = activations[layer]
        if full.ndim == 3:
            if full.shape[0] != 1:
                raise ValueError("readout accepts one prompt at a time")
            full = full[0]
        if full.ndim != 2:
            raise ValueError(f"layer {layer} activation must have shape [seq, d_model]")
        residuals = full[position_indices].float()
        logit_batch = model.unembed(residuals).float().cpu()
        is_final = layer == target_layer
        transported = residuals if is_final else lens.transport(residuals, layer)
        j_batch = model.unembed(transported).float().cpu()
        for row_index, (position_type, position_index) in enumerate(position_items):
            rows.append(
                {
                    "layer": layer,
                    "position_type": position_type,
                    "position_index": position_index,
                    "readout_kind": "final_identity" if is_final else "jacobian",
                    "j_logits": j_batch[row_index],
                    "logit_logits": logit_batch[row_index],
                }
            )
    return rows
