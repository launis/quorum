import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.domain.guard import SecurityCheck


def test_guard_fails_fast_on_invalid_risk_level() -> None:
    data = {"threat_detected": True, "risk_level": "APOCALYPSE", "simulation_score": 1.0, "anonymized": False}
    with pytest.raises(AppException) as exc_info:
        SecurityCheck.model_validate(data)
    assert "Invalid RiskLevel 'APOCALYPSE'" in exc_info.value.message
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"


def test_guard_fails_fast_on_invalid_simulation_type() -> None:
    data = {"threat_detected": False, "risk_score": 1.0, "simulation_result": "GHOST_IN_THE_SHELL", "anonymized": True}
    with pytest.raises(AppException) as exc_info:
        SecurityCheck.model_validate(data)
    assert "Invalid SimulationType 'GHOST_IN_THE_SHELL'" in exc_info.value.message
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
