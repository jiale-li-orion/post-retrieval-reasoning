#!/usr/bin/env python3
"""Merge ATM evaluator outputs into run_stats.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from verbal_r3_core import load_evaluation_summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stats-file", type=Path, required=True)
    parser.add_argument("--eval-dir", type=Path, required=True)
    args = parser.parse_args()

    stats = json.loads(args.stats_file.read_text(encoding="utf-8"))
    stats["evaluation"] = load_evaluation_summary(args.eval_dir)
    args.stats_file.write_text(
        json.dumps(stats, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
