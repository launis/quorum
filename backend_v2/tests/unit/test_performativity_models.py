from typing import Any
import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.domain.performativity import PerformativityAnalysis


def test_performativity_fails_fast_on_invalid_authenticity() -> None:
    data = {
        "performativity_heuristics": [{"heuristic_name": "Test", "flag_raised": False, "description": "Desc"}],
        "pre_mortem_analysis": {"performed": True, "weak_signals": ["signal1"]},
        "authenticity_assessment": "INVALID",
        "description": "Desc",
    }
    with pytest.raises(AppException) as exc_info:
        PerformativityAnalysis.model_validate(data)
    assert "Invalid AuthenticityLevel 'INVALID'" in exc_info.value.message
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
