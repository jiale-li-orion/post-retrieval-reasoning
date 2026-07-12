#!/usr/bin/env python3
"""Evaluate nested n256/n512 Jacobian-lens stability without a judge."""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import jlens
import torch
import yaml


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = EXPERIMENT_ROOT.parents[1]
if str(EXPERIMENT_ROOT) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_ROOT))

from adapters.hf_model import HFModelAdapter  # noqa: E402
from core.registry import load_model_registry  # noqa: E402
from core.run_contract import create_run_directory, sanitize_manifest  # noqa: E402


def matrix_cosines(
    first: jlens.JacobianLens, second: jlens.JacobianLens
) -> dict[int, float]:
    if first.source_layers != second.source_layers or first.d_model != second.d_model:
        raise ValueError("lens architectures or source layers differ")
    return {
        layer: float(
            torch.nn.functional.cosine_similarity(
                first.jacobians[layer].float().flatten(),
                second.jacobians[layer].float().flatten(),
                dim=0,
            )
        )
        for layer in first.source_layers
    }


def topk_set_overlap(first: torch.Tensor, second: torch.Tensor, k: int) -> float:
    first_ids = set(torch.topk(first, k=k).indices.tolist())
    second_ids = set(torch.topk(second, k=k).indices.tolist())
    return len(first_ids & second_ids) / k


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--lens-256", type=Path, required=True)
    parser.add_argument("--lens-512", type=Path, required=True)
    parser.add_argument("--evaluation-id", required=True)
    parser.add_argument(
        "--prompt-root",
        type=Path,
        default=Path("/home/lab/lab/research_data/wikitext103/stability"),
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("/home/lab/lab/research_artifacts/jlens_stability"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    models = load_model_registry(EXPERIMENT_ROOT / "registry/model_registry.yaml")
    model_spec = models[args.model_id]
    calibration = _load_yaml(EXPERIMENT_ROOT / "registry/jlens_calibration.yaml")
    fit_config = _load_yaml(EXPERIMENT_ROOT / "registry/jlens_fit.yaml")
    prompt_spec = calibration["stability_prompts"]
    prompts_path = (
        args.prompt_root
        / args.model_id
        / prompt_spec["set_id"]
        / "prompts.jsonl"
    )
    expected_prompt_hash = prompt_spec["corpora"][args.model_id]["prompts_sha256"]
    if _file_sha256(prompts_path) != expected_prompt_hash:
        raise ValueError("held-out stability prompt hash mismatch")
    prompts = [
        json.loads(line)["text"] for line in prompts_path.read_text().splitlines()
    ]
    if len(prompts) != int(prompt_spec["prompt_count"]):
        raise ValueError("held-out stability prompt count mismatch")

    output_dir = create_run_directory(args.output_root / args.model_id / args.evaluation_id)
    lens_256 = jlens.JacobianLens.load(str(args.lens_256))
    lens_512 = jlens.JacobianLens.load(str(args.lens_512))
    cosine_by_layer = matrix_cosines(lens_256, lens_512)

    adapter = HFModelAdapter.from_local_snapshot(
        Path(model_spec["local_path"]), model_id=args.model_id
    )
    wrapped = jlens.from_hf(adapter.model, adapter.get_text_tokenizer())
    overlap_rows = []
    for prompt_index, prompt in enumerate(prompts):
        logits_256, _, _ = lens_256.apply(
            wrapped, prompt, positions=[-1], max_seq_len=256
        )
        logits_512, _, _ = lens_512.apply(
            wrapped, prompt, positions=[-1], max_seq_len=256
        )
        for layer in lens_256.source_layers:
            overlap_rows.append(
                {
                    "prompt_index": prompt_index,
                    "layer": layer,
                    "top25_overlap": topk_set_overlap(
                        logits_256[layer][0], logits_512[layer][0], 25
                    ),
                }
            )

    cosine_median = statistics.median(cosine_by_layer.values())
    overlap_median = statistics.median(
        row["top25_overlap"] for row in overlap_rows
    )
    thresholds = fit_config["stability"]
    report = {
        "model_id": args.model_id,
        "matrix_cosine_by_layer": cosine_by_layer,
        "matrix_cosine_median": cosine_median,
        "top25_overlap_rows": overlap_rows,
        "top25_overlap_median": overlap_median,
        "matrix_gate_pass": cosine_median
        >= float(thresholds["matrix_cosine_median_min"]),
        "top25_gate_pass": overlap_median
        >= float(thresholds["top25_overlap_median_min"]),
    }
    report["gate_pass"] = report["matrix_gate_pass"] and report["top25_gate_pass"]
    report_path = output_dir / "stability.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    manifest = sanitize_manifest(
        {
            "evaluation_id": args.evaluation_id,
            "status": "complete",
            "project_commit": _git_commit(PROJECT_ROOT),
            "model": model_spec,
            "lens_256_sha256": _file_sha256(args.lens_256),
            "lens_512_sha256": _file_sha256(args.lens_512),
            "prompts_sha256": expected_prompt_hash,
            "position": "last_token",
            "top_k": 25,
            "report_sha256": _file_sha256(report_path),
            "finished_at": datetime.now().astimezone().isoformat(),
        }
    )
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(output_dir)
    return 0


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_commit(root: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()


if __name__ == "__main__":
    raise SystemExit(main())
