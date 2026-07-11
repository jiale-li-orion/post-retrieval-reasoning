"""Load and validate frozen experiment registries."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class RegistryError(ValueError):
    """Raised when a registry cannot support a reproducible run."""


def _load_rows(path: Path, key: str) -> list[dict[str, Any]]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get(key), list):
        raise RegistryError(f"{path} must contain a {key!r} list")
    rows = payload[key]
    ids = [row.get("id") for row in rows if isinstance(row, dict)]
    if len(ids) != len(rows) or any(not item for item in ids):
        raise RegistryError(f"every {key} row must have a non-empty id")
    if len(set(ids)) != len(ids):
        raise RegistryError(f"duplicate ids in {path}")
    return rows


def load_model_registry(
    path: Path, *, require_ready: bool = False
) -> dict[str, dict[str, Any]]:
    rows = _load_rows(path, "models")
    for row in rows:
        source = row.get("source")
        if source not in {"huggingface", "local_snapshot"}:
            raise RegistryError(f"unsupported model source for {row['id']}")
        for field in ("repository", "revision", "local_path"):
            if not row.get(field):
                raise RegistryError(f"model {row['id']} is missing {field}")
        if not require_ready:
            continue
        if source == "huggingface" and row["revision"] in {"main", "latest", "pending"}:
            raise RegistryError(f"model {row['id']} requires an immutable revision")
        if source == "local_snapshot" and not row.get("file_manifest_sha256"):
            raise RegistryError(
                f"local model {row['id']} requires file_manifest_sha256"
            )
    return {row["id"]: row for row in rows}


def load_condition_registry(path: Path) -> dict[str, dict[str, Any]]:
    rows = _load_rows(path, "conditions")
    by_id = {row["id"]: row for row in rows}
    expected = {f"C{i}" for i in range(11)}
    missing = sorted(expected - by_id.keys())
    extra = sorted(by_id.keys() - expected)
    if missing or extra:
        raise RegistryError(f"condition IDs mismatch; missing={missing}, extra={extra}")
    return by_id
