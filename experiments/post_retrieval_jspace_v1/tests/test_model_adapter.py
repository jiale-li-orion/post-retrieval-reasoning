from types import SimpleNamespace

import pytest

from adapters.hf_model import ModelAdapterError, resolve_residual_modules


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
