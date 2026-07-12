import pytest

from adapters.api_chat import APIAdapterError, APIProviderSpec


def test_api_provider_resolves_secret_without_exposing_value() -> None:
    spec = APIProviderSpec.from_mapping(
        {
            "id": "mimo",
            "model": "mimo-v2.5",
            "base_url": "https://example/v1",
            "api_key_env": "MIMO_API_KEY",
            "max_token_field": "max_completion_tokens",
        },
        environ={"MIMO_API_KEY": "private-value"},
    )

    assert spec.api_key == "private-value"
    assert spec.manifest_view()["api_key_env"] == "MIMO_API_KEY"
    assert "private-value" not in str(spec.manifest_view())


def test_api_provider_requires_declared_environment_key() -> None:
    with pytest.raises(APIAdapterError, match="MIMO_API_KEY"):
        APIProviderSpec.from_mapping(
            {
                "id": "mimo",
                "model": "mimo-v2.5",
                "base_url": "https://example/v1",
                "api_key_env": "MIMO_API_KEY",
                "max_token_field": "max_completion_tokens",
            },
            environ={},
        )


def test_api_provider_rejects_unknown_max_token_field() -> None:
    with pytest.raises(APIAdapterError, match="max token field"):
        APIProviderSpec.from_mapping(
            {
                "id": "bad",
                "model": "model",
                "base_url": "https://example/v1",
                "api_key_env": "KEY",
                "max_token_field": "tokens",
            },
            environ={"KEY": "value"},
        )


def test_api_provider_resolves_endpoint_and_model_from_environment() -> None:
    spec = APIProviderSpec.from_mapping(
        {
            "id": "minimax",
            "model_env": "MINIMAX_MODEL",
            "base_url_env": "MINIMAX_BASE_URL",
            "api_key_env": "MINIMAX_API_KEY",
        },
        environ={
            "MINIMAX_MODEL": "actual-model",
            "MINIMAX_BASE_URL": "https://provider.example/v1",
            "MINIMAX_API_KEY": "secret",
        },
    )

    assert spec.model == "actual-model"
    assert spec.base_url == "https://provider.example/v1"


def test_api_provider_fails_before_use_when_endpoint_is_unset() -> None:
    with pytest.raises(APIAdapterError, match="MINIMAX_BASE_URL"):
        APIProviderSpec.from_mapping(
            {
                "id": "minimax",
                "model_env": "MINIMAX_MODEL",
                "base_url_env": "MINIMAX_BASE_URL",
                "api_key_env": "MINIMAX_API_KEY",
            },
            environ={"MINIMAX_MODEL": "m", "MINIMAX_API_KEY": "secret"},
        )
