"""Pure task-state derivation used by the experiment control CLI."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    resource: str
    kind: str
    prerequisites: tuple[str, ...]
    artifact: str
    command: tuple[str, ...]
    required_outputs: tuple[str, ...] = ("manifest.json",)


@dataclass(frozen=True)
class TaskAction:
    task: TaskSpec
    status: str
    command: tuple[str, ...]


def derive_status(
    task: TaskSpec,
    artifact_root: Path,
    *,
    pending_judge: bool = False,
) -> str:
    artifact_dir = artifact_root / task.artifact
    manifest_path = artifact_dir / "manifest.json"
    if not manifest_path.is_file():
        if pending_judge:
            return "pending_judge"
        return "pending"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "failed"
    status = str(manifest.get("status", "failed"))
    if status == "complete":
        if all((artifact_dir / name).is_file() for name in task.required_outputs):
            return "complete"
        return "failed"
    if status in {"running", "failed", "blocked"}:
        return status
    return "failed"


def next_action(tasks: list[TaskSpec], artifact_root: Path) -> TaskAction | None:
    statuses = {
        task.task_id: derive_status(task, artifact_root) for task in tasks
    }
    for task in tasks:
        status = statuses[task.task_id]
        if status == "complete":
            continue
        if status in {"running", "failed", "blocked", "pending_judge"}:
            return TaskAction(task=task, status=status, command=task.command)
        prerequisites_complete = all(
            statuses.get(task_id) == "complete"
            for task_id in task.prerequisites
        )
        if not prerequisites_complete:
            continue
        if task.kind == "manual_gate":
            return TaskAction(
                task=task,
                status="awaiting_review",
                command=task.command,
            )
        if any("{" in part or "}" in part for part in task.command):
            raise ValueError(f"task {task.task_id} contains unresolved placeholders")
        return TaskAction(task=task, status="ready", command=task.command)
    return None
