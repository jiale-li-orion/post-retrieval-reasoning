#!/usr/bin/env python3
"""Write a deterministic manifest for one model snapshot."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
if str(EXPERIMENT_ROOT) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_ROOT))

from core.provenance import build_snapshot_manifest  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    manifest = build_snapshot_manifest(args.snapshot)
    payload = {
        "root": manifest.root,
        "file_manifest_sha256": manifest.sha256,
        "files": list(manifest.files),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(manifest.sha256)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
