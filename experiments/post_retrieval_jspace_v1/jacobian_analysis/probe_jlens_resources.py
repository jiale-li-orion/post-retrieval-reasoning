#!/usr/bin/env python3
"""Measure one-prompt J-lens resource viability before a formal fit."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

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
from jacobian_analysis.fit_jlens import load_frozen_prompts, source_layers_for_fit  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--dim-batch", type=int, required=True)
    parser.add_argument("--probe-id", required=True)
    parser.add_argument(
        "--corpus-root",
        type=Path,
        default=Path("/home/lab/lab/research_data/wikitext103/calibration"),
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("/home/lab/lab/research_artifacts/jlens_resource_probes"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.dim_batch <= 0:
        raise ValueError("--dim-batch must be positive")
    models = load_model_registry(EXPERIMENT_ROOT / "registry/model_registry.yaml")
    model_spec = models[args.model_id]
    calibration_path = EXPERIMENT_ROOT / "registry/jlens_calibration.yaml"
    calibration = yaml.safe_load(calibration_path.read_text(encoding="utf-8"))
    fit_path = EXPERIMENT_ROOT / "registry/jlens_fit.yaml"
    fit_config = yaml.safe_load(fit_path.read_text(encoding="utf-8"))
    windows_path = (
        args.corpus_root
        / args.model_id
        / calibration["corpus_id"]
        / "windows.jsonl"
    )
    prompt = load_frozen_prompts(
        windows_path,
        expected_sha256=calibration["corpora"][args.model_id]["windows_sha256"],
        count=1,
    )[0]
    output = create_run_directory(args.output_root / args.model_id / args.probe_id)
    manifest_path = output / "manifest.json"
    manifest = sanitize_manifest(
        {
            "probe_id": args.probe_id,
            "status": "running",
            "project_commit": _git_commit(),
            "model": model_spec,
            "dim_batch": args.dim_batch,
            "max_seq_len": int(fit_config["max_seq_len"]),
            "skip_first": int(fit_config["skip_first"]),
            "source_layers": "all_before_target",
            "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
            "started_at": datetime.now().astimezone().isoformat(),
        }
    )
    _write_json(manifest_path, manifest)

    adapter = HFModelAdapter.from_local_snapshot(
        Path(model_spec["local_path"]), model_id=args.model_id
    )
    wrapped = jlens.from_hf(adapter.model, adapter.get_text_tokenizer())
    target_layer = wrapped.n_layers - 1
    source_layers = source_layers_for_fit(wrapped.n_layers, target_layer)
    torch.cuda.reset_peak_memory_stats()
    started = time.perf_counter()
    jacobians, seq_len, n_valid = jlens.jacobian_for_prompt(
        wrapped,
        prompt,
        source_layers,
        target_layer=target_layer,
        dim_batch=args.dim_batch,
        max_seq_len=int(fit_config["max_seq_len"]),
        skip_first=int(fit_config["skip_first"]),
    )
    elapsed = time.perf_counter() - started
    manifest.update(
        {
            "status": "complete",
            "target_layer": target_layer,
            "source_layer_count": len(source_layers),
            "d_model": wrapped.d_model,
            "seq_len": seq_len,
            "n_valid_positions": n_valid,
            "jacobian_count": len(jacobians),
            "elapsed_seconds": elapsed,
            "peak_allocated_mib": torch.cuda.max_memory_allocated() / 2**20,
            "peak_reserved_mib": torch.cuda.max_memory_reserved() / 2**20,
            "finished_at": datetime.now().astimezone().isoformat(),
        }
    )
    _write_json(manifest_path, manifest)
    print(output)
    return 0


def _git_commit() -> str:
    return subprocess.check_output(
        ["git", "-C", str(PROJECT_ROOT), "rev-parse", "HEAD"], text=True
    ).strip()


def _write_json(path: Path, payload: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


if __name__ == "__main__":
    raise SystemExit(main())

