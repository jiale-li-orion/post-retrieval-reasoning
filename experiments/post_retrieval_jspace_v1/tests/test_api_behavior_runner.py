from types import SimpleNamespace

import pytest

from behavior.run_api_behavior import response_fields, validate_api_condition


def test_api_matrix_is_limited_to_new_hard_va_conditions() -> None:
    validate_api_condition("C1", "hard")
    validate_api_condition("C10", "hard")
    with pytest.raises(ValueError, match="Hard C1/C7-C10"):
        validate_api_condition("C0", "hard")
    with pytest.raises(ValueError, match="Hard C1/C7-C10"):
        validate_api_condition("C1", "full")


def test_api_response_records_usage_and_actual_model() -> None:
    response = SimpleNamespace(
        model="resolved-version",
        choices=[SimpleNamespace(message=SimpleNamespace(content="answer"))],
        usage=SimpleNamespace(
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15,
            completion_tokens_details=SimpleNamespace(reasoning_tokens=2),
            prompt_tokens_details=SimpleNamespace(cached_tokens=3),
        ),
    )

    assert response_fields(response) == {
        "answer": "answer",
        "returned_model": "resolved-version",
        "prompt_tokens": 10,
        "completion_tokens": 5,
        "total_tokens": 15,
        "reasoning_tokens": 2,
        "cached_tokens": 3,
    }
