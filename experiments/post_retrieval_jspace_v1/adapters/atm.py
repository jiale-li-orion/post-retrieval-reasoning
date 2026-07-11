"""Strict ATM-Bench data adapter with frozen integrity checks."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class DatasetIntegrityError(ValueError):
    """Raised when an ATM asset differs from the frozen protocol."""


@dataclass(frozen=True)
class ATMItem:
    qa_id: str
    question: str
    qtype: str
    gold_answer: str
    evidence_ids: tuple[str, ...]
    niah_evidence_ids: tuple[str, ...] | None = None


class ATMAdapter:
    EXPECTED_HASHES = {
        "full": "ab6eaa9df62fb4162e0f5eecd98768a7e3ae721e32d2db2cf227ff41e3295762",
        "hard": "acd35f2a172a9741d970d2cf21184ff0af8d79a8bf59967fc8aa33d619f6af4a",
    }
    SPLIT_FILES = {
        "full": Path("data/atm-bench/atm-bench.json"),
        "hard": Path("data/atm-bench/atm-bench-hard.json"),
    }

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def split_path(self, split: str) -> Path:
        try:
            return self.root / self.SPLIT_FILES[split]
        except KeyError as exc:
            raise ValueError(f"unsupported ATM split: {split}") from exc

    def split_sha256(self, split: str) -> str:
        return _sha256(self.split_path(split))

    def load_split(self, split: str) -> list[ATMItem]:
        path = self.split_path(split)
        actual = _sha256(path)
        expected = self.EXPECTED_HASHES[split]
        if actual != expected:
            raise DatasetIntegrityError(
                f"SHA256 mismatch for {split}: expected {expected}, got {actual}"
            )
        return _load_items(path)

    def load_niah(self, k: int) -> list[ATMItem]:
        if k not in {25, 50, 100, 200}:
            raise ValueError(f"unsupported NIAH pool size: {k}")
        path = self.root / f"data/atm-bench/niah/atm-bench-hard-niah{k}.json"
        items = _load_items(path)
        if any(item.niah_evidence_ids is None for item in items):
            raise DatasetIntegrityError(f"NIAH-{k} item is missing niah_evidence_ids")
        return items


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_items(path: Path) -> list[ATMItem]:
    payload: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise DatasetIntegrityError(f"ATM file must contain a list: {path}")
    return [
        ATMItem(
            qa_id=str(row["id"]),
            question=str(row["question"]),
            qtype=str(row["qtype"]),
            gold_answer=str(row["answer"]),
            evidence_ids=tuple(str(item) for item in row["evidence_ids"]),
            niah_evidence_ids=(
                tuple(str(item) for item in row["niah_evidence_ids"])
                if "niah_evidence_ids" in row
                else None
            ),
        )
        for row in payload
    ]
