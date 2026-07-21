import pytest
from pydantic import ValidationError

from backend_v2.models.domain.guard import SecurityCheck


def test_guard_fails_fast_on_invalid_risk_level() -> None:
    data = {"threat_detected": True, "risk_level": "APOCALYPSE", "simulation_score": 1.0, "anonymized": False}
    with pytest.raises(ValidationError) as exc_info:
        SecurityCheck.model_validate(data)
    assert "Input should be 'RISK_LOW', 'RISK_MEDIUM' or 'RISK_HIGH'" in str(exc_info.value)


def test_guard_fails_fast_on_invalid_simulation_type() -> None:
    data = {
        "threat_detected": False,
        "risk_level": "LOW",
        "simulation_score": 1.0,
        "simulation_result": "GHOST_IN_THE_SHELL",
        "anonymized": True,
    }
    with pytest.raises(ValidationError) as exc_info:
        SecurityCheck.model_validate(data)
    assert "Input should be 'SIM_PASSIVE', 'SIM_ACTIVE' or 'SIM_MALICIOUS'" in str(exc_info.value)
