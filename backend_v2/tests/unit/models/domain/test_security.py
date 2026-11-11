"""Unit tests for SecurityCheck and InputProcessingOutputDTO domain models."""

from __future__ import annotations

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.security import (
    InputProcessingOutputDTO,
    SecurityCheck,
)
from backend_v2.models.enums import LaxRiskLevel


class SecurityCheckFactory(ModelFactory[SecurityCheck]):
    """Polyfactory model factory for SecurityCheck domain model."""

    __model__ = SecurityCheck
    threat_detected: bool = False
    risk_level: LaxRiskLevel = LaxRiskLevel.LOW
    risk_score: float = 1.0
    simulation_score: float = 1.0
    anonymized: bool = False


class InputProcessingOutputDTOFactory(ModelFactory[InputProcessingOutputDTO]):
    """Polyfactory model factory for InputProcessingOutputDTO domain model."""

    __model__ = InputProcessingOutputDTO
    thought_process: str = "Checking the inputs for safety..."
    conclusion: str = "No threats found."
    confidence_score: float = 0.99
    is_safe: bool = True
    rejection_reason: str | None = None
    security_check: SecurityCheck | None = None


def test_security_check_valid() -> None:
    """Test that a valid SecurityCheck model instantiates properly."""
    model = SecurityCheckFactory.build(
        threat_detected=False,
        risk_level=LaxRiskLevel.LOW,
        risk_score=1.0,
        simulation_score=1.0,
        anonymized=False,
        pii_findings=[],
    )
    assert model.threat_detected is False
    assert model.risk_score == 1.0


def test_security_check_exact_boundaries() -> None:
    """Test SecurityCheck accepts exact 1.0 and 3.0 boundary scores."""
    model = SecurityCheckFactory.build(
        threat_detected=False,
        risk_level=LaxRiskLevel.LOW,
        risk_score=3.0,
        simulation_score=1.0,
        anonymized=False,
    )
    assert model.risk_score == 3.0
    assert model.simulation_score == 1.0


def test_security_check_lower_boundary_score() -> None:
    """Test that SecurityCheck fails on score lower than 1.0."""
    with pytest.raises(AppException) as exc:
        SecurityCheck.model_validate(
            {
                "threat_detected": True,
                "risk_level": LaxRiskLevel.HIGH,
                "risk_score": 0.9,
                "simulation_score": 1.0,
                "anonymized": False,
            }
        )

    assert "Score must be between 1.0 and 3.0 inclusive." in exc.value.message
    assert exc.value.details == {"error_code": ErrorCodes.VALIDATION_FAILED.value}


def test_security_check_invalid_score() -> None:
    """Test that SecurityCheck fails on out of bounds scores."""
    with pytest.raises(AppException) as exc:
        SecurityCheck.model_validate(
            {
                "threat_detected": True,
                "risk_level": LaxRiskLevel.HIGH,
                "risk_score": 5.0,
                "simulation_score": 1.0,
                "anonymized": False,
                "pii_findings": [],
            }
        )

    assert "Score must be between 1.0 and 3.0 inclusive." in exc.value.message
    assert exc.value.details == {"error_code": ErrorCodes.VALIDATION_FAILED.value}


def test_input_processing_output_valid_safe() -> None:
    """Test that a safe InputProcessingOutputDTO instantiates properly."""
    model = InputProcessingOutputDTOFactory.build(
        thought_process="Checking the inputs for safety...",
        conclusion="No threats found.",
        confidence_score=0.99,
        is_safe=True,
        rejection_reason=None,
    )
    assert model.is_safe is True
    assert model.rejection_reason is None


def test_input_processing_output_valid_unsafe() -> None:
    """Test that an unsafe InputProcessingOutputDTO instantiates properly with a reason."""
    model = InputProcessingOutputDTOFactory.build(
        thought_process="Checking the inputs...",
        conclusion="Threat found.",
        confidence_score=0.95,
        is_safe=False,
        rejection_reason="Contains malware.",
    )
    assert model.is_safe is False
    assert model.rejection_reason == "Contains malware."


def test_input_processing_output_invalid_unsafe_no_reason() -> None:
    """Test that an unsafe InputProcessingOutputDTO without a reason raises AppException."""
    with pytest.raises(AppException) as exc:
        InputProcessingOutputDTO.model_validate(
            {
                "thought_process": "Checking inputs...",
                "conclusion": "Threat found.",
                "confidence_score": 0.99,
                "is_safe": False,
                "rejection_reason": None,
            }
        )

    assert "rejection_reason must be provided if is_safe is False" in exc.value.message
    assert exc.value.details == {"error_code": ErrorCodes.VALIDATION_FAILED.value}


def test_security_extra_fields_forbidden() -> None:
    """Test that all security models reject unknown extra fields."""
    with pytest.raises(ValidationError):
        SecurityCheck.model_validate(
            {
                "threat_detected": False,
                "risk_level": LaxRiskLevel.LOW,
                "risk_score": 1.0,
                "simulation_score": 1.0,
                "anonymized": False,
                "extra": 1,
            }
        )

    with pytest.raises(ValidationError):
        InputProcessingOutputDTO.model_validate(
            {
                "thought_process": "T",
                "conclusion": "C",
                "confidence_score": 1.0,
                "is_safe": True,
                "extra": 1,
            }
        )
