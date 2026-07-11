#!/usr/bin/env python3
"""Run ATM-Bench QA with fixed SGM evidence and Verbal-R3 annotations."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Iterable, Optional

import torch
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer

from memqa.qa_agent_baselines.oracle.oracle_baseline import (
    OracleLLM,
    apply_niah_pools,
    build_batch_index,
    build_text_messages,
    classify_evidence_id,
    collect_text_evidence,
    extract_evidence_ids,
    load_json,
    load_qa_list,
)

from verbal_r3_core import (
    ExperimentConfig,
    RerankerParseError,
    accumulate_generation_usage,
    append_verbal_annotation,
    build_annotation_record,
    build_answer_record,
    ensure_outputs_absent,
    load_experiment_config,
    load_python_string_assignment,
    parse_reranker_output,
)


SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = SCRIPT_DIR.parent
WORKSPACE_ROOT = EXPERIMENT_ROOT.parents[1]
DEFAULT_CONFIG = EXPERIMENT_ROOT / "configs/verbal_r3_official.json"
DEFAULT_VERBAL_R3_ROOT = WORKSPACE_ROOT / "other_repo_references/VerbalR3"


class VerbalReranker:
    """Thin adapter around the official Verbal-R3 question-document interface."""

    def __init__(
        self,
        config: ExperimentConfig,
        system_prompt: str,
        device: str,
    ) -> None:
        self.config = config.reranker
        self.system_prompt = system_prompt
        target = device
        if target == "auto":
            target = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if str(target).startswith("cuda") else torch.float32
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.model,
            revision=self.config.revision,
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model,
            revision=self.config.revision,
            dtype=dtype,
        )
        self.model = self.model.to(target)
        self.model.eval()
        torch.manual_seed(self.config.seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(self.config.seed)

    @torch.inference_mode()
    def annotate(self, question: str, document: str) -> dict[str, Any]:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "user",
                "content": f"Question: {question}\nDocument: {document}",
            },
        ]
        input_ids = self.tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt",
        ).to(self.model.device)
        prompt_tokens = int(input_ids.shape[-1])
        started = time.perf_counter()
        last_error: Optional[Exception] = None
        completion_tokens_by_attempt: list[int] = []

        for retry_count in range(self.config.max_parse_retries):
            outputs = self.model.generate(
                input_ids,
                max_new_tokens=self.config.max_new_tokens,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )
            generated_ids = outputs[0][prompt_tokens:]
            completion_tokens_by_attempt.append(int(generated_ids.shape[-1]))
            raw_output = self.tokenizer.decode(
                generated_ids,
                skip_special_tokens=True,
            ).strip()
            try:
                parsed = parse_reranker_output(raw_output)
                total_prompt_tokens, total_completion_tokens = (
                    accumulate_generation_usage(
                        prompt_tokens_per_attempt=prompt_tokens,
                        completion_tokens_by_attempt=completion_tokens_by_attempt,
                    )
                )
                return {
                    "raw_output": raw_output,
                    "comment": parsed.comment,
                    "score": parsed.score,
                    "retry_count": retry_count,
                    "prompt_tokens": total_prompt_tokens,
                    "completion_tokens": total_completion_tokens,
                    "latency_ms": round((time.perf_counter() - started) * 1000),
                }
            except RerankerParseError as exc:
                last_error = exc

        raise RerankerParseError(
            f"failed to parse reranker output after "
            f"{self.config.max_parse_retries} attempts: {last_error}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ATM-Bench SGM QA with Verbal-R3 annotations"
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--verbal-r3-root", type=Path, default=DEFAULT_VERBAL_R3_ROOT)
    parser.add_argument("--qa-file", type=Path, required=True)
    parser.add_argument("--image-batch-results", type=Path, required=True)
    parser.add_argument("--video-batch-results", type=Path, required=True)
    parser.add_argument("--email-file", type=Path, required=True)
    parser.add_argument("--use-niah-pools", action="store_true")
    parser.add_argument("--niah-field", default=None)
    parser.add_argument("--limit", type=int, default=None)

    parser.add_argument(
        "--provider", choices=["openai", "vllm", "vllm_local"], default="vllm"
    )
    parser.add_argument("--model", required=True)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--vllm-endpoint", default=None)
    parser.add_argument("--reranker-device", default="auto")

    parser.add_argument("--output-file", type=Path, required=True)
    parser.add_argument("--annotations-file", type=Path, default=None)
    parser.add_argument("--stats-file", type=Path, default=None)
    return parser.parse_args()


def resolve_output_paths(args: argparse.Namespace) -> tuple[Path, Path, Path]:
    predictions = args.output_file
    annotations = args.annotations_file or predictions.with_name("annotations.jsonl")
    stats = args.stats_file or predictions.with_name("run_stats.json")
    return predictions, annotations, stats


def write_jsonl_row(handle: Any, row: dict[str, Any]) -> None:
    handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    handle.flush()


def build_llm(args: argparse.Namespace, config: ExperimentConfig) -> OracleLLM:
    answerer = config.answerer
    llm_config: dict[str, Any] = {
        "provider": args.provider,
        "model": args.model,
        "api_key": args.api_key,
        "endpoint": args.vllm_endpoint,
        "max_tokens": answerer.max_tokens,
        "temperature": answerer.temperature,
        "timeout": answerer.timeout,
        "max_retries": answerer.max_retries,
        "request_delay": answerer.request_delay,
    }
    llm_config.update(answerer.request_body)
    return OracleLLM(args.provider, llm_config)


def sum_numeric(rows: Iterable[dict[str, Any]], key: str) -> Optional[int]:
    values = [row[key] for row in rows if row.get(key) is not None]
    return sum(values) if values else None


def main() -> int:
    args = parse_args()
    config = load_experiment_config(args.config)
    predictions_path, annotations_path, stats_path = resolve_output_paths(args)
    partial_predictions = predictions_path.with_suffix(predictions_path.suffix + ".partial")
    partial_annotations = annotations_path.with_suffix(annotations_path.suffix + ".partial")
    ensure_outputs_absent(
        [
            predictions_path,
            annotations_path,
            stats_path,
            partial_predictions,
            partial_annotations,
        ]
    )

    prompt_path = args.verbal_r3_root / "utils/reranker_server.py"
    system_prompt = load_python_string_assignment(prompt_path, "system_prompt")

    qas = load_qa_list(load_json(args.qa_file))
    niah_field = args.niah_field or config.evidence.niah_field
    if args.use_niah_pools:
        apply_niah_pools(qas, niah_field, strict=True)
    if args.limit is not None:
        if args.limit <= 0:
            raise ValueError("--limit must be positive")
        qas = qas[: args.limit]
    selected_ids = [extract_evidence_ids(qa) for qa in qas]
    all_evidence_ids = [evidence_id for ids in selected_ids for evidence_id in ids]

    email_index: dict[str, dict[str, Any]] = {}
    if any(classify_evidence_id(item) == "email" for item in all_evidence_ids):
        email_index = {
            item["id"]: item
            for item in load_json(args.email_file)
            if item.get("id")
        }
    image_index = build_batch_index(load_json(args.image_batch_results), "image_path")
    video_index = build_batch_index(load_json(args.video_batch_results), "video_path")

    reranker = VerbalReranker(config, system_prompt, args.reranker_device)
    llm = build_llm(args, config)
    predictions: list[dict[str, Any]] = []
    annotations: list[dict[str, Any]] = []

    predictions_path.parent.mkdir(parents=True, exist_ok=True)
    annotations_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with partial_predictions.open("x", encoding="utf-8") as prediction_handle, \
             partial_annotations.open("x", encoding="utf-8") as annotation_handle:
            for qa, evidence_ids in tqdm(
                list(zip(qas, selected_ids, strict=True)),
                desc="ATM QA",
            ):
                question = str(qa["question"])
                chunks = collect_text_evidence(
                    evidence_ids,
                    email_index,
                    image_index,
                    video_index,
                    list(config.evidence.batch_fields),
                )
                if len(chunks) != len(evidence_ids):
                    raise ValueError(
                        f"QA {qa['id']} resolved {len(chunks)} chunks for "
                        f"{len(evidence_ids)} evidence IDs"
                    )

                annotated_chunks: list[str] = []
                for index, (evidence_id, chunk) in enumerate(
                    zip(evidence_ids, chunks, strict=True)
                ):
                    generated = reranker.annotate(question, chunk)
                    annotation = build_annotation_record(
                        qa_id=str(qa["id"]),
                        evidence_id=evidence_id,
                        evidence_index=index,
                        question=question,
                        sgm_text=chunk,
                        raw_output=generated["raw_output"],
                        comment=generated["comment"],
                        score=generated["score"],
                        retry_count=generated["retry_count"],
                        prompt_tokens=generated["prompt_tokens"],
                        completion_tokens=generated["completion_tokens"],
                        latency_ms=generated["latency_ms"],
                        model=config.reranker.model,
                        checkpoint_revision=config.reranker.revision,
                    )
                    annotations.append(annotation)
                    write_jsonl_row(annotation_handle, annotation)
                    annotated_chunks.append(
                        append_verbal_annotation(
                            chunk,
                            generated["comment"],
                            generated["score"],
                        )
                    )

                messages = build_text_messages(question, annotated_chunks)
                started = time.perf_counter()
                answer, usage = llm.chat_with_usage(messages)
                answer_record = build_answer_record(
                    qa=qa,
                    evidence_ids=evidence_ids,
                    answer=answer,
                    usage=usage,
                    latency_ms=round((time.perf_counter() - started) * 1000),
                    requested_model=args.model,
                    returned_model=None,
                )
                predictions.append(answer_record)
                write_jsonl_row(prediction_handle, answer_record)

        os.replace(partial_predictions, predictions_path)
        os.replace(partial_annotations, annotations_path)
    except Exception:
        print(
            f"Run failed; partial outputs retained at {partial_predictions} "
            f"and {partial_annotations}",
            file=sys.stderr,
        )
        raise

    stats = {
        "protocol_version": config.protocol_version,
        "qa_count": len(predictions),
        "annotation_count": len(annotations),
        "condition": "niah" if args.use_niah_pools else "oracle",
        "niah_field": niah_field if args.use_niah_pools else None,
        "reranker": {
            "model": config.reranker.model,
            "revision": config.reranker.revision,
            "prompt_source": str(prompt_path),
            "temperature": config.reranker.temperature,
            "top_p": config.reranker.top_p,
            "max_new_tokens": config.reranker.max_new_tokens,
            "seed": config.reranker.seed,
            "prompt_tokens": sum_numeric(annotations, "prompt_tokens"),
            "completion_tokens": sum_numeric(annotations, "completion_tokens"),
            "total_tokens": sum_numeric(annotations, "total_tokens"),
            "total_latency_ms": sum_numeric(annotations, "latency_ms"),
            "parse_retries": sum_numeric(annotations, "retry_count"),
        },
        "answerer": {
            "requested_model": args.model,
            "temperature": config.answerer.temperature,
            "max_tokens": config.answerer.max_tokens,
            "prompt_tokens": sum_numeric(predictions, "prompt_tokens"),
            "completion_tokens": sum_numeric(predictions, "completion_tokens"),
            "reasoning_tokens": sum_numeric(predictions, "reasoning_tokens"),
            "cached_tokens": sum_numeric(predictions, "cached_tokens"),
            "total_tokens": sum_numeric(predictions, "total_tokens"),
            "total_latency_ms": sum_numeric(predictions, "latency_ms"),
        },
    }
    stats_path.parent.mkdir(parents=True, exist_ok=True)
    with stats_path.open("x", encoding="utf-8") as handle:
        json.dump(stats, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    print(f"Predictions: {predictions_path}")
    print(f"Annotations: {annotations_path}")
    print(f"Run stats: {stats_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
