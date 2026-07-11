"""Immutable output and secret-free manifest helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class ManifestError(ValueError):
    """Raised when provenance would expose credentials."""


_SECRET_KEYS = {
    "api_key",
    "authorization",
    "password",
    "secret",
    "token",
}


def create_run_directory(path: Path) -> Path:
    try:
        path.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise FileExistsError(f"refusing to overwrite existing run: {path}") from exc
    return path


def sanitize_manifest(value: Any, *, _path: str = "manifest") -> Any:
    if isinstance(value, dict):
        clean: dict[str, Any] = {}
        for key, item in value.items():
            normalized = str(key).lower()
            if normalized in _SECRET_KEYS:
                raise ManifestError(f"secret field forbidden at {_path}.{key}")
            clean[str(key)] = sanitize_manifest(item, _path=f"{_path}.{key}")
        return clean
    if isinstance(value, list):
        return [sanitize_manifest(item, _path=f"{_path}[]") for item in value]
    return value
