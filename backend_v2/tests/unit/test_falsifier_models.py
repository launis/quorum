import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.domain.falsifier import ReasoningFidelity


def test_falsifier_fail_fast_on_corrupt_fidelity_level() -> None:
    data = {
        "fidelity_score": "INVALID_LEVEL",
        "abductive_score": 2.5,
        "plausibility_score": 2.5,
        "justification": "Test",
    }
    with pytest.raises(AppException) as exc_info:
        ReasoningFidelity.model_validate(data)
    assert "Invalid FidelityLevel" in exc_info.value.message
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"


def test_falsifier_fails_fast_on_invalid_numeric_score() -> None:
    with pytest.raises(AppException) as exc_info:
        ReasoningFidelity.validate_falsifier_scores(4.0)
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
