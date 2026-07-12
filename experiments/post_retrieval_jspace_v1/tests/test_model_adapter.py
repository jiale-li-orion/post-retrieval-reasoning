from types import SimpleNamespace

import pytest

from adapters.hf_model import (
    ModelAdapterError,
    _contains_visual_content,
    resolve_residual_modules,
    resolve_text_tokenizer,
)


def test_resolves_causal_lm_residual_blocks() -> None:
    layers = [object(), object()]
    model = SimpleNamespace(model=SimpleNamespace(layers=layers))

    assert resolve_residual_modules(model) is layers


def test_resolves_qwen_vl_language_residual_blocks() -> None:
    layers = [object(), object(), object()]
    model = SimpleNamespace(
        model=SimpleNamespace(language_model=SimpleNamespace(layers=layers))
    )

    assert resolve_residual_modules(model) is layers


def test_unknown_architecture_fails_explicitly() -> None:
    with pytest.raises(ModelAdapterError, match="residual blocks"):
        resolve_residual_modules(SimpleNamespace())


def test_text_tokenizer_unwraps_multimodal_processor() -> None:
    tokenizer = object()

    assert resolve_text_tokenizer(SimpleNamespace(tokenizer=tokenizer)) is tokenizer
    assert resolve_text_tokenizer(tokenizer) is tokenizer


def test_visual_content_detection_accepts_official_atm_image_url_blocks() -> None:
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Evidence"},
                {
                    "type": "image_url",
                    "image_url": {"url": "data:image/jpeg;base64,x"},
                },
            ],
        }
    ]

    assert _contains_visual_content(messages) is True
    assert _contains_visual_content([{"role": "user", "content": "text"}]) is False
