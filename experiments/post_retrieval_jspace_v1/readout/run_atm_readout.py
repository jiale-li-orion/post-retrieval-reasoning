#!/usr/bin/env python3
"""Run immutable paired J-lens/logit-lens readout on frozen ATM behavior runs."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import jlens
import pandas as pd
import torch


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = EXPERIMENT_ROOT.parents[1]
if str(EXPERIMENT_ROOT) in sys.path:
    sys.path.remove(str(EXPERIMENT_ROOT))
sys.path.insert(0, str(EXPERIMENT_ROOT))

from adapters.atm import ATMAdapter  # noqa: E402
from adapters.hf_model import HFModelAdapter  # noqa: E402
from behavior.run_behavior import (  # noqa: E402
    evidence_ids_for_condition,
    validate_run_selection,
)
from core.registry import load_condition_registry, load_model_registry  # noqa: E402
from core.run_contract import create_run_directory, sanitize_manifest  # noqa: E402
from interventions.verbal_annotation import apply_annotation_cache  # noqa: E402
from readout.core import compute_paired_readouts  # noqa: E402
from readout.metrics import summarize_target  # noqa: E402
from readout.positions import resolve_text_positions  # noqa: E402


def validate_programs_frozen(
    programs: list[dict[str, Any]], qa_ids: list[str], *, allow_draft: bool
) -> None:
    by_id = {str(row["qa_id"]): row for row in programs}
    missing = [qa_id for qa_id in qa_ids if qa_id not in by_id]
    if missing:
        raise ValueError(f"decision programs missing QA IDs: {missing}")
    draft = [
        qa_id
        for qa_id in qa_ids
        if by_id[qa_id].get("review_status") != "frozen"
    ]
    if draft and not allow_draft:
        raise ValueError(f"decision programs are not frozen: {draft}")


def merge_target_rows(
    automatic: list[dict[str, Any]], programs: list[dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    """Use human-reviewed Hard targets over automatic Full targets."""
    by_id = {str(row["qa_id"]): row for row in automatic}
    by_id.update(
        {
            str(row["qa_id"]): row
            for row in programs
            if isinstance(row.get("targets"), list)
        }
    )
    return by_id


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--condition", choices=["C0", "C1"], required=True)
    parser.add_argument("--behavior-run", type=Path, required=True)
    parser.add_argument("--lens", type=Path, required=True)
    parser.add_argument("--targets", type=Path, required=True)
    parser.add_argument("--decision-programs", type=Path, required=True)
    parser.add_argument("--annotation-cache", type=Path)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--allow-draft-programs", action="store_true")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("/home/lab/lab/research_artifacts/readouts"),
    )
    parser.add_argument(
        "--atm-root",
        type=Path,
        default=PROJECT_ROOT / "other_repo_references/ATM-Bench",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.allow_draft_programs and args.limit is None:
        raise ValueError("draft programs are allowed only for an explicit smoke limit")
    conditions = load_condition_registry(
        EXPERIMENT_ROOT / "registry/condition_registry.yaml"
    )
    condition = validate_run_selection(args.condition, "hard", conditions)
    if condition["annotation"] == "verbal_r3" and args.annotation_cache is None:
        raise ValueError("C1 readout requires --annotation-cache")
    if condition["annotation"] == "none" and args.annotation_cache is not None:
        raise ValueError("C0 readout does not accept an annotation cache")

    behavior_manifest = _load_json(args.behavior_run / "manifest.json")
    if behavior_manifest.get("status") != "complete":
        raise ValueError("behavior run is not complete")
    if behavior_manifest.get("condition") != args.condition:
        raise ValueError("behavior condition does not match readout condition")
    if behavior_manifest.get("model", {}).get("id") != args.model_id:
        raise ValueError("behavior model does not match readout model")
    predictions = _load_jsonl(args.behavior_run / "predictions.jsonl")
    if args.limit is not None:
        predictions = predictions[: args.limit]
    qa_ids = [str(row["qa_id"]) for row in predictions]

    programs = _load_jsonl(args.decision_programs)
    validate_programs_frozen(
        programs, qa_ids, allow_draft=args.allow_draft_programs
    )
    targets_by_id = merge_target_rows(
        _load_jsonl(args.targets), programs
    )
    missing_targets = [qa_id for qa_id in qa_ids if qa_id not in targets_by_id]
    if missing_targets:
        raise ValueError(f"target manifest missing QA IDs: {missing_targets}")

    models = load_model_registry(EXPERIMENT_ROOT / "registry/model_registry.yaml")
    model_spec = models[args.model_id]
    output_dir = create_run_directory(
        args.output_root / args.condition / args.model_id / args.run_id
    )
    manifest_path = output_dir / "manifest.json"
    manifest = sanitize_manifest(
        {
            "run_id": args.run_id,
            "status": "running",
            "project_commit": _git_commit(PROJECT_ROOT),
            "git_dirty": _git_dirty(PROJECT_ROOT),
            "model": model_spec,
            "condition": args.condition,
            "split": "hard",
            "behavior_manifest_sha256": _file_sha256(
                args.behavior_run / "manifest.json"
            ),
            "predictions_sha256": _file_sha256(
                args.behavior_run / "predictions.jsonl"
            ),
            "lens_sha256": _file_sha256(args.lens),
            "targets_sha256": _file_sha256(args.targets),
            "decision_programs_sha256": _file_sha256(args.decision_programs),
            "annotation_cache_sha256": (
                _file_sha256(args.annotation_cache) if args.annotation_cache else None
            ),
            "allow_draft_programs": args.allow_draft_programs,
            "limit": args.limit,
            "positions": ["P_evidence_end_i", "P_q", "P_a0"],
            "environment": {
                "python": sys.version,
                "platform": platform.platform(),
                "torch": torch.__version__,
                "cuda": torch.version.cuda,
                "gpu": torch.cuda.get_device_name(0),
            },
            "started_at": datetime.now().astimezone().isoformat(),
        }
    )
    _write_json(manifest_path, manifest)

    adapter = HFModelAdapter.from_local_snapshot(
        Path(model_spec["local_path"]), model_id=args.model_id
    )
    wrapped_model = jlens.from_hf(adapter.model, adapter.get_text_tokenizer())
    lens = jlens.JacobianLens.load(str(args.lens))
    if lens.d_model != wrapped_model.d_model:
        raise ValueError("lens hidden size does not match model")
    tokenizer = adapter.get_text_tokenizer()
    atm = ATMAdapter(args.atm_root)
    items = {item.qa_id: item for item in atm.load_split("hard")}
    annotations = _load_jsonl(args.annotation_cache) if args.annotation_cache else []
    prediction_by_id = {str(row["qa_id"]): row for row in predictions}
    metric_rows: list[dict[str, Any]] = []
    position_rows: list[dict[str, Any]] = []

    for qa_id in qa_ids:
        item = items[qa_id]
        evidence_ids = evidence_ids_for_condition(item, condition)
        chunks = tuple(atm.collect_sgm_chunks(evidence_ids))
        if condition["annotation"] == "verbal_r3":
            chunks = tuple(
                apply_annotation_cache(qa_id, evidence_ids, chunks, annotations)
            )
        prediction = prediction_by_id[qa_id]
        if list(evidence_ids) != prediction["evidence_ids"]:
            raise ValueError(f"behavior evidence IDs changed for {qa_id}")
        if [_text_sha256(chunk) for chunk in chunks] != prediction["evidence_sha256"]:
            raise ValueError(f"behavior evidence bytes changed for {qa_id}")
        messages = atm.build_text_messages(item.question, list(chunks))
        rendered = adapter.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        if _text_sha256(rendered) != prediction["prompt_sha256"]:
            raise ValueError(f"behavior prompt changed for {qa_id}")
        inputs = adapter.build_inputs(messages)
        positions = resolve_text_positions(
            rendered,
            question=item.question,
            evidence_chunks=chunks,
            tokenizer=tokenizer,
            actual_input_ids=inputs["input_ids"],
        )
        named_positions = {
            **{
                f"P_evidence_end_{index}": value
                for index, value in enumerate(positions.evidence_ends)
            },
            "P_q": positions.p_q,
            "P_a0": positions.p_a0,
        }
        with torch.inference_mode():
            output = adapter.model(
                **inputs,
                output_hidden_states=True,
                use_cache=False,
                return_dict=True,
            )
        activations = {
            layer: output.hidden_states[layer + 1].detach()
            for layer in [*lens.source_layers, max(lens.source_layers) + 1]
        }
        paired = compute_paired_readouts(
            activations,
            positions=named_positions,
            lens=lens,
            model=wrapped_model,
            target_layer=max(lens.source_layers) + 1,
        )
        position_rows.extend(
            {
                "qa_id": qa_id,
                "condition": args.condition,
                "position_type": name,
                "position_index": index,
            }
            for name, index in named_positions.items()
        )
        target_rows = targets_by_id[qa_id]["targets"]
        for readout in paired:
            for target in target_rows:
                tokenization = target["tokenization"][args.model_id]
                token_set = sorted(
                    {
                        int(token_id)
                        for alias in tokenization["aliases"]
                        for token_id in alias["token_ids"]
                    }
                )
                common = {
                    "qa_id": qa_id,
                    "condition": args.condition,
                    "qtype": item.qtype,
                    "layer": readout["layer"],
                    "normalized_depth": readout["layer"]
                    / (max(lens.source_layers) + 1),
                    "position_type": readout["position_type"],
                    "position_index": readout["position_index"],
                    "readout_kind": readout["readout_kind"],
                    "target_id": target["target_id"],
                    "target_text": target["text"],
                    "copyable": target["copyable"],
                    "derived_candidate": target["derived_candidate"],
                }
                for method, logits in (
                    ("j_lens", readout["j_logits"]),
                    ("logit_lens", readout["logit_logits"]),
                ):
                    metric_rows.append(
                        {
                            **common,
                            "method": method,
                            **summarize_target(
                                logits,
                                single_token_ids=tokenization["single_token_ids"],
                                token_set_ids=token_set,
                                top_k=25,
                            ),
                        }
                    )
        del output, activations, paired
        torch.cuda.empty_cache()

    metrics_path = output_dir / "readout.parquet"
    positions_path = output_dir / "positions.parquet"
    pd.DataFrame(metric_rows).to_parquet(metrics_path, index=False)
    pd.DataFrame(position_rows).to_parquet(positions_path, index=False)
    manifest.update(
        {
            "status": "complete",
            "qa_count": len(qa_ids),
            "metric_row_count": len(metric_rows),
            "readout_sha256": _file_sha256(metrics_path),
            "positions_sha256": _file_sha256(positions_path),
            "finished_at": datetime.now().astimezone().isoformat(),
        }
    )
    _write_json(manifest_path, manifest)
    print(output_dir)
    return 0


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _git_commit(root: Path) -> str:
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()


def _git_dirty(root: Path) -> bool:
    return bool(subprocess.check_output(["git", "-C", str(root), "status", "--porcelain"], text=True).strip())


if __name__ == "__main__":
    raise SystemExit(main())
