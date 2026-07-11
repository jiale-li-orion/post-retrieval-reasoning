from pathlib import Path

import yaml

from core.registry import load_condition_registry, load_model_registry


ROOT = Path(__file__).resolve().parents[1]


def test_frozen_model_suite_matches_protocol_addendum() -> None:
    models = load_model_registry(ROOT / "registry/model_registry.yaml")

    assert set(models) == {
        "qwen3_8b_ms",
        "deepseek_r1_distill_llama_8b",
        "qwen2_5_7b_instruct",
        "qwen3_vl_2b_instruct",
        "qwen3_vl_8b_instruct",
    }


def test_frozen_conditions_encode_va_without_reordering() -> None:
    conditions = load_condition_registry(ROOT / "registry/condition_registry.yaml")

    assert conditions["C1"]["annotation"] == "verbal_r3"
    assert conditions["C1"]["evidence_order"] == "preserve"
    assert conditions["C7"]["niah_k"] == 25
    assert conditions["C10"]["niah_k"] == 200


def test_official_api_reference_is_hard_sgm_only() -> None:
    payload = yaml.safe_load(
        (ROOT / "registry/official_atm_reference.yaml").read_text(encoding="utf-8")
    )

    assert payload["split"] == "hard"
    assert payload["evidence_view"] == "sgm"
    assert payload["judge"]["model"] == "gpt-5-mini"
    assert payload["results"]["kimi_k2_5"]["C0"] == 44.5
    assert payload["results"]["mimo_v2_5"]["C6"] == 26.8
    assert payload["results"]["minimax_m3"]["C6"] == 50.6
