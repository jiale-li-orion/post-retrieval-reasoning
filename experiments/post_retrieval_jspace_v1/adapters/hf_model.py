"""Open-weight model adapter shared by behavior and mechanism runners."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoProcessor,
    AutoTokenizer,
    Qwen3VLForConditionalGeneration,
)


class ModelAdapterError(RuntimeError):
    """Raised when a model cannot satisfy the mechanism adapter contract."""


@dataclass(frozen=True)
class GenerationResult:
    text: str
    prompt_tokens: int
    completion_tokens: int


def resolve_residual_modules(model: Any) -> Sequence[Any]:
    backbone = getattr(model, "model", None)
    direct = getattr(backbone, "layers", None)
    if direct is not None:
        return direct
    language_model = getattr(backbone, "language_model", None)
    vl_layers = getattr(language_model, "layers", None)
    if vl_layers is not None:
        return vl_layers
    raise ModelAdapterError(
        f"cannot locate residual blocks for {type(model).__name__}"
    )


class HFModelAdapter:
    def __init__(self, model: Any, processor: Any, model_id: str, device: str) -> None:
        self.model = model
        self.processor = processor
        self.model_id = model_id
        self.device = device

    @classmethod
    def from_local_snapshot(
        cls,
        path: Path,
        *,
        model_id: str,
        device: str = "cuda",
        dtype: torch.dtype = torch.bfloat16,
    ) -> "HFModelAdapter":
        config = _read_model_type(path)
        common = {
            "pretrained_model_name_or_path": str(path),
            "local_files_only": True,
            "torch_dtype": dtype,
        }
        if config == "qwen3_vl":
            processor = AutoProcessor.from_pretrained(
                path, local_files_only=True
            )
            model = Qwen3VLForConditionalGeneration.from_pretrained(**common)
        else:
            processor = AutoTokenizer.from_pretrained(
                path, local_files_only=True
            )
            model = AutoModelForCausalLM.from_pretrained(**common)
        model = model.to(device).eval()
        resolve_residual_modules(model)
        if model.get_output_embeddings() is None:
            raise ModelAdapterError(f"{model_id} has no output embedding")
        return cls(model, processor, model_id, device)

    def build_inputs(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        rendered = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = self.processor(text=[rendered], return_tensors="pt")
        return {key: value.to(self.device) for key, value in inputs.items()}

    @torch.inference_mode()
    def generate(
        self,
        messages: list[dict[str, Any]],
        *,
        max_new_tokens: int,
        temperature: float = 0.0,
    ) -> GenerationResult:
        inputs = self.build_inputs(messages)
        prompt_tokens = int(inputs["input_ids"].shape[-1])
        kwargs: dict[str, Any] = {
            "max_new_tokens": max_new_tokens,
            "do_sample": temperature > 0,
        }
        if temperature > 0:
            kwargs["temperature"] = temperature
        output_ids = self.model.generate(**inputs, **kwargs)
        generated_ids = output_ids[:, prompt_tokens:]
        text = self.processor.batch_decode(
            generated_ids, skip_special_tokens=True
        )[0].strip()
        return GenerationResult(
            text=text,
            prompt_tokens=prompt_tokens,
            completion_tokens=int(generated_ids.shape[-1]),
        )

    def get_unembedding(self) -> Any:
        return self.model.get_output_embeddings()

    def get_residual_modules(self) -> Sequence[Any]:
        return resolve_residual_modules(self.model)

    def forward_hidden(self, messages: list[dict[str, Any]]) -> Any:
        inputs = self.build_inputs(messages)
        return self.model(
            **inputs,
            output_hidden_states=True,
            use_cache=False,
            return_dict=True,
        )


def _read_model_type(path: Path) -> str:
    import json

    config_path = path / "config.json"
    try:
        return str(json.loads(config_path.read_text(encoding="utf-8"))["model_type"])
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as exc:
        raise ModelAdapterError(f"invalid model config: {config_path}") from exc
