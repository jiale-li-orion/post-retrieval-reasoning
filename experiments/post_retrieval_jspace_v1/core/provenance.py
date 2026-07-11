"""Deterministic provenance for local and downloaded model snapshots."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path


_IGNORED_PARTS = {".cache", ".git", "._____temp", "__pycache__"}


@dataclass(frozen=True)
class SnapshotManifest:
    root: str
    files: tuple[dict[str, str | int], ...]
    sha256: str


def build_snapshot_manifest(root: Path) -> SnapshotManifest:
    root = root.resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"model snapshot directory not found: {root}")
    rows: list[dict[str, str | int]] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if not path.is_file() or any(part in _IGNORED_PARTS for part in relative.parts):
            continue
        rows.append(
            {
                "path": relative.as_posix(),
                "size": path.stat().st_size,
                "sha256": _file_sha256(path),
            }
        )
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    return SnapshotManifest(
        root=str(root),
        files=tuple(rows),
        sha256=hashlib.sha256(canonical).hexdigest(),
    )


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
