from pathlib import Path

from core.provenance import build_snapshot_manifest


def test_snapshot_manifest_is_sorted_and_ignores_download_state(tmp_path: Path) -> None:
    (tmp_path / "config.json").write_text("{}", encoding="utf-8")
    (tmp_path / "model.safetensors").write_bytes(b"weights")
    cache = tmp_path / ".cache" / "huggingface"
    cache.mkdir(parents=True)
    (cache / "partial").write_bytes(b"unfinished")

    manifest = build_snapshot_manifest(tmp_path)

    assert [row["path"] for row in manifest.files] == [
        "config.json",
        "model.safetensors",
    ]
    assert len(manifest.sha256) == 64


def test_snapshot_manifest_changes_when_weights_change(tmp_path: Path) -> None:
    weights = tmp_path / "model.safetensors"
    weights.write_bytes(b"first")
    before = build_snapshot_manifest(tmp_path)
    weights.write_bytes(b"second")
    after = build_snapshot_manifest(tmp_path)

    assert before.sha256 != after.sha256
