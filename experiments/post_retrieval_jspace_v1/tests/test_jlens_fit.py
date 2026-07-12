import hashlib
import json

import pytest

from jacobian_analysis.fit_jlens import (
    load_frozen_prompts,
    resolve_fit_config,
    source_layers_for_fit,
)


def test_source_layers_stop_before_final_target() -> None:
    assert source_layers_for_fit(5, 4) == [0, 1, 2, 3]


def test_frozen_prompt_loader_uses_nested_prefix(tmp_path) -> None:
    path = tmp_path / "windows.jsonl"
    path.write_text(
        "\n".join(
            json.dumps({"window_index": index, "text": f"p{index}"})
            for index in range(3)
        )
        + "\n"
    )
    digest = hashlib.sha256(path.read_bytes()).hexdigest()

    assert load_frozen_prompts(path, expected_sha256=digest, count=2) == ["p0", "p1"]

    with pytest.raises(ValueError, match="hash mismatch"):
        load_frozen_prompts(path, expected_sha256="0" * 64, count=2)


def test_model_fit_override_changes_only_declared_resource_parameter() -> None:
    config = {
        "dim_batch": 8,
        "max_seq_len": 256,
        "model_overrides": {"large": {"dim_batch": 2}},
    }

    assert resolve_fit_config(config, "small") == {
        "dim_batch": 8,
        "max_seq_len": 256,
    }
    assert resolve_fit_config(config, "large") == {
        "dim_batch": 2,
        "max_seq_len": 256,
    }
