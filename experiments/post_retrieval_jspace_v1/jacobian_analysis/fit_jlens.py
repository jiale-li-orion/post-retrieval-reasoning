#!/usr/bin/env python3
"""Fit a resumable Jacobian lens on a frozen calibration corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
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


def source_layers_for_fit(n_layers: int, target_layer: int) -> list[int]:
    if target_layer <= 0 or target_layer >= n_layers:
        raise ValueError("target layer must be a non-initial model layer")
    return list(range(target_layer))


def load_frozen_prompts(
    windows_path: Path, *, expected_sha256: str, count: int
) -> list[str]:
    actual = _file_sha256(windows_path)
    if actual != expected_sha256:
        raise ValueError(
            f"calibration hash mismatch: expected {expected_sha256}, got {actual}"
        )
    rows = [json.loads(line) for line in windows_path.read_text().splitlines()]
    if count > len(rows):
        raise ValueError(f"requested {count} prompts from corpus of {len(rows)}")
    selected = rows[:count]
    if any(int(row["window_index"]) != index for index, row in enumerate(selected)):
        raise ValueError("calibration windows are not in canonical order")
    return [str(row["text"]) for row in selected]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--sample-count", type=int, choices=[256, 512], required=True)
    parser.add_argument("--fit-id", required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument(
        "--corpus-root",
        type=Path,
        default=Path("/home/lab/lab/research_data/wikitext103/calibration"),
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("/home/lab/lab/research_artifacts/jlens_fits"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    models = load_model_registry(EXPERIMENT_ROOT / "registry/model_registry.yaml")
    model_spec = models[args.model_id]
    calibration = _load_yaml(EXPERIMENT_ROOT / "registry/jlens_calibration.yaml")
    fit_config = _load_yaml(EXPERIMENT_ROOT / "registry/jlens_fit.yaml")
    corpus_dir = (
        args.corpus_root / args.model_id / calibration["corpus_id"]
    )
    windows_path = corpus_dir / "windows.jsonl"
    prompts = load_frozen_prompts(
        windows_path,
        expected_sha256=calibration["corpora"][args.model_id]["windows_sha256"],
        count=args.sample_count,
    )

    output_dir = args.output_root / args.model_id / args.fit_id
    if args.resume:
        if not output_dir.is_dir():
            raise FileNotFoundError(f"fit directory cannot be resumed: {output_dir}")
        state = json.loads((output_dir / "manifest.json").read_text())
        if state.get("status") != "running":
            raise ValueError("only an interrupted running fit can be resumed")
    else:
        create_run_directory(output_dir)
    checkpoint_path = output_dir / "fit.ckpt"
    lens_path = output_dir / "lens.pt"
    manifest_path = output_dir / "manifest.json"
    started_at = datetime.now().astimezone().isoformat()
    running_manifest = sanitize_manifest(
        {
            "fit_id": args.fit_id,
            "status": "running",
            "project_commit": _git_commit(PROJECT_ROOT),
            "model": model_spec,
            "sample_count": args.sample_count,
            "corpus_sha256": _file_sha256(windows_path),
            "fit_config": fit_config,
            "fit_config_sha256": _file_sha256(
                EXPERIMENT_ROOT / "registry/jlens_fit.yaml"
            ),
            "started_at": started_at,
        }
    )
    _write_json(manifest_path, running_manifest)

    adapter = HFModelAdapter.from_local_snapshot(
        Path(model_spec["local_path"]), model_id=args.model_id
    )
    wrapped = jlens.from_hf(adapter.model, adapter.get_text_tokenizer())
    target_layer = wrapped.n_layers - 1
    source_layers = source_layers_for_fit(wrapped.n_layers, target_layer)
    lens = jlens.fit(
        wrapped,
        prompts,
        source_layers=source_layers,
        target_layer=target_layer,
        dim_batch=int(fit_config["dim_batch"]),
        max_seq_len=int(fit_config["max_seq_len"]),
        skip_first=int(fit_config["skip_first"]),
        checkpoint_path=str(checkpoint_path),
        checkpoint_every=int(fit_config["checkpoint_every"]),
        resume=args.resume,
    )
    lens.save(str(lens_path), dtype=torch.float16)
    checkpoint_path.unlink()
    complete_manifest = {
        **running_manifest,
        "status": "complete",
        "source_layers": source_layers,
        "target_layer": target_layer,
        "n_prompts": lens.n_prompts,
        "d_model": lens.d_model,
        "lens_sha256": _file_sha256(lens_path),
        "finished_at": datetime.now().astimezone().isoformat(),
    }
    _write_json(manifest_path, complete_manifest)
    print(output_dir)
    return 0


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


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
