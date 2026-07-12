#!/usr/bin/env python3
"""Human-facing control plane for manifest-driven experiment execution."""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = EXPERIMENT_ROOT.parents[1]
ARTIFACT_ROOT = Path("/home/lab/lab/research_artifacts")
if str(EXPERIMENT_ROOT) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_ROOT))

from orchestration.state import (  # noqa: E402
    TaskSpec,
    derive_status,
    next_action,
)


def task_specs() -> list[TaskSpec]:
    scripts = EXPERIMENT_ROOT / "scripts"
    return [
        TaskSpec(
            task_id="jlens.qwen3_vl_2b.n512",
            resource="GPU_GRADIENT",
            kind="run",
            prerequisites=(),
            artifact="jlens_fits/qwen3_vl_2b_instruct/wikitext103-n512-v1",
            command=(
                str(scripts / "run_jlens_fit.sh"),
                "qwen3_vl_2b_instruct",
                "512",
                "wikitext103-n512-v1",
                "--resume",
            ),
            required_outputs=("manifest.json", "lens.pt"),
            log="logs/jlens-qwen3vl2b-n512-v1.log",
        ),
        TaskSpec(
            task_id="stability.qwen3_vl_2b",
            resource="GPU_INFERENCE",
            kind="run",
            prerequisites=("jlens.qwen3_vl_2b.n512",),
            artifact="jlens_stability/qwen3_vl_2b_instruct/stability-n256-n512-v1",
            command=(
                str(scripts / "run_jlens_stability.sh"),
                "qwen3_vl_2b_instruct",
                "wikitext103-n256-v2",
                "wikitext103-n512-v1",
                "stability-n256-n512-v1",
            ),
            required_outputs=("manifest.json", "stability.json"),
        ),
        TaskSpec(
            task_id="gate.qwen3_vl_2b_stability",
            resource="MANUAL_GATE",
            kind="manual_gate",
            prerequisites=("stability.qwen3_vl_2b",),
            artifact="approvals/gate-qwen3-vl-2b-stability",
            command=(
                str(scripts / "experimentctl"),
                "approve",
                "gate.qwen3_vl_2b_stability",
            ),
        ),
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="experimentctl")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status")
    subparsers.add_parser("next")
    for name in ("verify", "resume", "tail", "approve"):
        child = subparsers.add_parser(name)
        child.add_argument("task_id")
    start = subparsers.add_parser("start")
    start.add_argument("task_id")
    start.add_argument("--tmux", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tasks = task_specs()
    by_id = {task.task_id: task for task in tasks}
    if args.command == "status":
        for task in tasks:
            print(f"{task.task_id}: {derive_status(task, ARTIFACT_ROOT)} [{task.resource}]")
        return 0
    if args.command == "next":
        action = next_action(tasks, ARTIFACT_ROOT)
        if action is None:
            print("No pending registered task.")
            return 0
        print(f"task: {action.task.task_id}")
        print(f"status: {action.status}")
        print("command: " + shlex.join(action.command))
        return 0
    task = by_id.get(args.task_id)
    if task is None:
        raise SystemExit(f"unknown task ID: {args.task_id}")
    if args.command == "verify":
        status = derive_status(task, ARTIFACT_ROOT)
        print(f"{task.task_id}: {status}")
        return 0 if status == "complete" else 1
    if args.command == "tail":
        if not task.log:
            raise SystemExit(f"task has no registered log: {task.task_id}")
        subprocess.run(["tail", "-n", "30", str(ARTIFACT_ROOT / task.log)], check=True)
        return 0
    if args.command == "approve":
        return _approve(task, tasks)
    if args.command in {"start", "resume"}:
        command = list(task.command)
        if args.command == "start":
            action = next_action(tasks, ARTIFACT_ROOT)
            if action is None or action.task.task_id != task.task_id or action.status != "ready":
                raise SystemExit("start requires this task to be the next ready action")
        if args.command == "resume" and derive_status(task, ARTIFACT_ROOT) != "running":
            raise SystemExit("resume requires a running manifest")
        use_tmux = getattr(args, "tmux", False)
        if use_tmux:
            session = task.task_id.replace(".", "-").replace("_", "-")[:60]
            subprocess.run(
                ["tmux", "new-session", "-d", "-s", session, shlex.join(command)],
                cwd=PROJECT_ROOT,
                check=True,
            )
            print(f"tmux session: {session}")
            return 0
        return subprocess.run(command, cwd=PROJECT_ROOT).returncode
    raise AssertionError(args.command)


def _approve(task: TaskSpec, tasks: list[TaskSpec]) -> int:
    if task.kind != "manual_gate":
        raise SystemExit("approve accepts only manual-gate tasks")
    by_id = {item.task_id: item for item in tasks}
    upstream = [by_id[item] for item in task.prerequisites]
    if any(derive_status(item, ARTIFACT_ROOT) != "complete" for item in upstream):
        raise SystemExit("manual gate prerequisites are not complete")
    artifact_dir = ARTIFACT_ROOT / task.artifact
    artifact_dir.mkdir(parents=True, exist_ok=False)
    upstream_hashes = {
        item.task_id: _sha256(ARTIFACT_ROOT / item.artifact / "manifest.json")
        for item in upstream
    }
    payload = {
        "status": "complete",
        "approved": True,
        "task_id": task.task_id,
        "upstream_manifest_sha256": upstream_hashes,
        "project_commit": _git_commit(),
        "approved_at": datetime.now().astimezone().isoformat(),
    }
    (artifact_dir / "manifest.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(artifact_dir)
    return 0


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_commit() -> str:
    return subprocess.check_output(
        ["git", "-C", str(PROJECT_ROOT), "rev-parse", "HEAD"], text=True
    ).strip()


if __name__ == "__main__":
    raise SystemExit(main())
