from unittest.mock import AsyncMock
import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.domain.falsifier import ReasoningFidelity
from backend_v2.models.enums import FidelityLevel


def test_falsifier_fail_fast_on_corrupt_fidelity_level() -> None:
    data = {
        "fidelity_score": "INVALID_LEVEL",
        "fidelity_numeric": 2.5,
        "abductive_score": 2.5,
        "plausibility_score": 2.5,
        "justification": "Test",
    }
    with pytest.raises(ValidationError) as exc_info:
        ReasoningFidelity.model_validate(data)
    assert exc_info.value is not None


def test_falsifier_fails_fast_on_invalid_numeric_score() -> None:
    with pytest.raises(AppException):
        ReasoningFidelity(
            fidelity_score=FidelityLevel.UNCERTAIN,
            fidelity_numeric=4.0,
            abductive_score=2.0,
            plausibility_score=2.0,
            justification="Test",
        )
