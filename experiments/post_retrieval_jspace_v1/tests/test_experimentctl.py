import json
from pathlib import Path

from orchestration.state import TaskSpec, derive_status, next_action


def _task(task_id, *, prerequisites=(), kind="run", artifact="task"):
    return TaskSpec(
        task_id=task_id,
        resource="CPU_SAFE",
        kind=kind,
        prerequisites=tuple(prerequisites),
        artifact=artifact,
        command=("echo", task_id),
        required_outputs=("manifest.json",),
    )


def test_complete_and_pending_judge_are_distinct(tmp_path: Path) -> None:
    inference = tmp_path / "inference"
    inference.mkdir()
    (inference / "manifest.json").write_text(
        json.dumps({"status": "complete"}), encoding="utf-8"
    )
    inference_task = _task("inference", artifact="inference")
    judge_task = _task(
        "judge", prerequisites=("inference",), artifact="judge"
    )

    assert derive_status(inference_task, tmp_path) == "complete"
    assert derive_status(judge_task, tmp_path, pending_judge=True) == "pending_judge"


def test_next_action_stops_at_manual_gate(tmp_path: Path) -> None:
    first_dir = tmp_path / "first"
    first_dir.mkdir()
    (first_dir / "manifest.json").write_text(
        json.dumps({"status": "complete"}), encoding="utf-8"
    )
    tasks = [
        _task("first", artifact="first"),
        _task("review", prerequisites=("first",), kind="manual_gate", artifact="review"),
        _task("later", prerequisites=("review",), artifact="later"),
    ]

    action = next_action(tasks, tmp_path)

    assert action.task.task_id == "review"
    assert action.status == "awaiting_review"


def test_next_action_returns_full_command_without_placeholders(tmp_path: Path) -> None:
    task = _task("ready")

    action = next_action([task], tmp_path)

    assert action.status == "ready"
    assert action.command == ("echo", "ready")
    assert all("{" not in part and "}" not in part for part in action.command)
