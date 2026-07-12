import hashlib
import json

import pytest

from jacobian_analysis.fit_jlens import load_frozen_prompts, source_layers_for_fit


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
