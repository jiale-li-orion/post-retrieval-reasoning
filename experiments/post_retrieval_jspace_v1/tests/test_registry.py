from pathlib import Path

import pytest

from core.registry import RegistryError, load_condition_registry, load_model_registry


def test_model_registry_rejects_moving_revision(tmp_path: Path) -> None:
    path = tmp_path / "models.yaml"
    path.write_text(
        "models:\n"
        "  - id: moving\n"
        "    source: huggingface\n"
        "    repository: org/model\n"
        "    revision: main\n"
        "    local_path: /models/moving\n",
        encoding="utf-8",
    )

    with pytest.raises(RegistryError, match="immutable revision"):
        load_model_registry(path, require_ready=True)


def test_local_snapshot_requires_file_manifest_when_ready(tmp_path: Path) -> None:
    path = tmp_path / "models.yaml"
    path.write_text(
        "models:\n"
        "  - id: local-model\n"
        "    source: local_snapshot\n"
        "    repository: user-provided\n"
        "    revision: local\n"
        "    local_path: /models/local\n",
        encoding="utf-8",
    )

    with pytest.raises(RegistryError, match="file_manifest_sha256"):
        load_model_registry(path, require_ready=True)


def test_condition_registry_requires_exact_c0_to_c10(tmp_path: Path) -> None:
    path = tmp_path / "conditions.yaml"
    rows = "\n".join(
        f"  - id: C{i}\n    evidence: sgm\n    split: hard" for i in range(10)
    )
    path.write_text(f"conditions:\n{rows}\n", encoding="utf-8")

    with pytest.raises(RegistryError, match="C10"):
        load_condition_registry(path)
