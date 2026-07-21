from unittest.mock import AsyncMock
import pytest
from pydantic import ValidationError

from backend_v2.models.domain.overseer import (
    EthicalObservation,
    FactCheckRFI,
    OverseerInput,
    OverseerOutput,
)
from backend_v2.models.enums import EthicalSeverity, VerificationResult


def test_fact_check_rfi_verified_enum() -> None:
    """Test FactCheckRFI calculation of is_verified via Enum."""
    data = {
        "claim": "The sky is blue.",
        "verification_result": VerificationResult.VERIFIED,
        "source_or_reasoning": "Observation",
    }
    rfi = FactCheckRFI.model_validate(data)
    assert rfi.is_verified is True
    assert rfi.verification_result == VerificationResult.VERIFIED


def test_fact_check_rfi_verified_string() -> None:
    """Test FactCheckRFI calculation of is_verified via String."""
    data = {
        "claim": "The sky is blue.",
        "verification_result": "RESULT_VERIFIED",
        "source_or_reasoning": "Observation",
    }
    rfi = FactCheckRFI.model_validate(data)
    assert rfi.is_verified is True
    assert rfi.verification_result == VerificationResult.VERIFIED


def test_ethical_observation_critical_enum() -> None:
    """Test EthicalObservation calculation of is_critical via Enum."""
    data = {
        "issue_type": "Privacy Violation",
        "severity": EthicalSeverity.CRITICAL,
        "description": "User data leaked.",
    }
    obs = EthicalObservation.model_validate(data)
    assert obs.is_critical is True
    assert obs.severity == EthicalSeverity.CRITICAL


def test_ethical_observation_critical_string() -> None:
    """Test EthicalObservation calculation of is_critical via String."""
    data = {
        "issue_type": "Privacy Violation",
        "severity": "SEVERITY_CRITICAL",
        "description": "User data leaked.",
    }
    obs = EthicalObservation.model_validate(data)
    assert obs.is_critical is True
    assert obs.severity == EthicalSeverity.CRITICAL


def test_overseer_input_fails_fast_without_chatlog() -> None:
    """Test that OverseerInput requires chat_log."""
    data = {"step_analyst": None}
    with pytest.raises(ValidationError):
        OverseerInput.model_validate(data)


def test_overseer_output_frozen_and_strict() -> None:
    """Test that OverseerOutput rejects unknown fields and is frozen."""
    data = {
        "overseer_data": {
            "fact_checks": [],
            "ethical_issues": [
                {
                    "issue_type": "Bias",
                    "severity": "SEVERITY_MODERATE",
                    "description": "Minor bias detected.",
                }
            ],
        },
        "reasoning_trace": "Analysis complete.",
        "calculation_log": [],
        "rogue_field": "Should fail",
    }
    with pytest.raises(ValidationError):
        OverseerOutput.model_validate(data)
