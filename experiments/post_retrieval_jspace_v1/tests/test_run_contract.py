from pathlib import Path

import pytest

from core.run_contract import ManifestError, create_run_directory, sanitize_manifest


def test_run_directory_refuses_existing_output(tmp_path: Path) -> None:
    run_dir = tmp_path / "run-1"
    create_run_directory(run_dir)

    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        create_run_directory(run_dir)


def test_manifest_rejects_secret_fields() -> None:
    with pytest.raises(ManifestError, match="secret field"):
        sanitize_manifest({"provider": {"api_key": "secret"}})


def test_manifest_allows_environment_variable_names() -> None:
    manifest = sanitize_manifest(
        {"provider": {"api_key_env": "MIMO_API_KEY", "endpoint": "https://api"}}
    )

    assert manifest["provider"]["api_key_env"] == "MIMO_API_KEY"
