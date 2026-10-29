"""Unit tests for Overseer Agent Domain Models."""

from __future__ import annotations

from polyfactory.factories.pydantic_factory import ModelFactory
import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.overseer import (
    EthicalObservation,
    FactCheckRFI,
    OverseerData,
    OverseerInput,
    OverseerOutput,
)
from backend_v2.models.enums import EthicalSeverity, VerificationResult


class FactCheckRFIFactory(ModelFactory[FactCheckRFI]):
    """Polyfactory for FactCheckRFI."""

    __model__ = FactCheckRFI
    claim = "The sky is blue."
    verification_result = VerificationResult.VERIFIED
    source_or_reasoning = "Direct atmospheric observation."


class EthicalObservationFactory(ModelFactory[EthicalObservation]):
    """Polyfactory for EthicalObservation."""

    __model__ = EthicalObservation
    issue_type = "Privacy Violation"
    severity = EthicalSeverity.CRITICAL
    description = "User data leaked."


def test_fact_check_rfi_verified_enum() -> None:
    """Test FactCheckRFI calculation of is_verified via Enum."""
    rfi = FactCheckRFIFactory.build(verification_result=VerificationResult.VERIFIED)
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


def test_fact_check_rfi_rejects_empty_claim_or_reasoning() -> None:
    """Test that FactCheckRFI raises AppException on empty or whitespace-only fields."""
    with pytest.raises(AppException) as exc_info:
        FactCheckRFIFactory.build(claim="   ")
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED

    with pytest.raises(AppException) as exc_info_reasoning:
        FactCheckRFIFactory.build(source_or_reasoning="")
    assert exc_info_reasoning.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED


def test_ethical_observation_critical_enum() -> None:
    """Test EthicalObservation calculation of is_critical via Enum."""
    obs = EthicalObservationFactory.build(severity=EthicalSeverity.CRITICAL)
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


def test_ethical_observation_rejects_empty_fields() -> None:
    """Test that EthicalObservation raises AppException on empty or whitespace-only fields."""
    with pytest.raises(AppException) as exc_info:
        EthicalObservationFactory.build(issue_type="   ")
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED

    with pytest.raises(AppException) as exc_info_desc:
        EthicalObservationFactory.build(description="")
    assert exc_info_desc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED


def test_overseer_data_rejects_empty_ethical_issues() -> None:
    """Test that OverseerData raises AppException when ethical_issues list is empty."""
    with pytest.raises(AppException) as exc_info:
        OverseerData(fact_checks=[], ethical_issues=[])
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED


def test_overseer_input_fails_fast_without_chatlog() -> None:
    """Test that OverseerInput requires non-empty chat_log."""
    with pytest.raises(ValidationError):
        OverseerInput.model_validate({"step_analyst": None})

    with pytest.raises(ValidationError):
        OverseerInput.model_validate({"chat_log": ""})


def test_overseer_output_frozen_and_strict() -> None:
    """Test that OverseerOutput rejects unknown fields and enforces immutability."""
    assert OverseerOutput.model_config.get("frozen") is True

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
