"""Secret-safe OpenAI-compatible API adapter."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Mapping

from openai import OpenAI


class APIAdapterError(ValueError):
    """Raised when an API provider is not fully configured."""


@dataclass(frozen=True)
class APIProviderSpec:
    provider_id: str
    model: str
    base_url: str
    api_key_env: str
    api_key: str = field(repr=False)
    max_token_field: str = "max_tokens"
    extra_body: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(
        cls,
        row: Mapping[str, Any],
        *,
        environ: Mapping[str, str] | None = None,
    ) -> "APIProviderSpec":
        active_env = os.environ if environ is None else environ
        key_name = str(row["api_key_env"])
        api_key = active_env.get(key_name)
        if not api_key:
            raise APIAdapterError(f"required environment variable is unset: {key_name}")
        token_field = str(row.get("max_token_field", "max_tokens"))
        if token_field not in {"max_tokens", "max_completion_tokens"}:
            raise APIAdapterError(f"unsupported max token field: {token_field}")
        return cls(
            provider_id=str(row["id"]),
            model=str(row["model"]),
            base_url=str(row["base_url"]),
            api_key_env=key_name,
            api_key=api_key,
            max_token_field=token_field,
            extra_body=dict(row.get("extra_body", {})),
        )

    def manifest_view(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "model": self.model,
            "base_url": self.base_url,
            "api_key_env": self.api_key_env,
            "max_token_field": self.max_token_field,
            "extra_body": dict(self.extra_body),
        }


class APIChatAdapter:
    def __init__(self, spec: APIProviderSpec) -> None:
        self.spec = spec
        self.client = OpenAI(api_key=spec.api_key, base_url=spec.base_url)

    def generate(
        self,
        messages: list[dict[str, Any]],
        *,
        max_tokens: int,
        temperature: float,
    ) -> Any:
        request: dict[str, Any] = {
            "model": self.spec.model,
            "messages": messages,
            "temperature": temperature,
            self.spec.max_token_field: max_tokens,
        }
        if self.spec.extra_body:
            request["extra_body"] = dict(self.spec.extra_body)
        return self.client.chat.completions.create(**request)
