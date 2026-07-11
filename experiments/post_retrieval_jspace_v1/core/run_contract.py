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

_COMPLETE_MANIFEST_FIELDS = {
    "run_id",
    "status",
    "project_commit",
    "git_dirty",
    "condition",
    "split",
    "model",
    "generation",
    "dataset",
    "config_hashes",
    "environment",
    "started_at",
    "finished_at",
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


def validate_manifest_completeness(manifest: dict[str, Any]) -> None:
    clean = sanitize_manifest(manifest)
    missing = sorted(_COMPLETE_MANIFEST_FIELDS - clean.keys())
    if missing:
        raise ManifestError(f"complete manifest missing fields: {missing}")
    if clean["status"] != "complete":
        raise ManifestError("manifest status must be complete")
