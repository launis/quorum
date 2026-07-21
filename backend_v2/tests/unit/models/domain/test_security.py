import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.domain.security import InputProcessingOutputDTO, SecurityCheck
from backend_v2.models.enums import LaxRiskLevel


def test_security_check_valid() -> None:
    """Test that a valid SecurityCheck model instantiates properly."""
    data = {
        "threat_detected": False,
        "risk_level": LaxRiskLevel.LOW,
        "risk_score": 1.0,
        "simulation_score": 1.0,
        "anonymized": False,
        "pii_findings": [],
    }
    model = SecurityCheck.model_validate(data)
    assert model.threat_detected is False
    assert model.risk_score == 1.0


def test_security_check_invalid_score() -> None:
    """Test that SecurityCheck fails on out of bounds scores."""
    data = {
        "threat_detected": True,
        "risk_level": LaxRiskLevel.HIGH,
        "risk_score": 5.0,  # Invalid
        "simulation_score": 1.0,
        "anonymized": False,
        "pii_findings": [],
    }
    with pytest.raises(AppException) as exc:
        SecurityCheck.model_validate(data)

    assert "Score must be between 1.0 and 3.0 inclusive." in exc.value.message


def test_input_processing_output_valid_safe() -> None:
    """Test that a safe InputProcessingOutputDTO instantiates properly."""
    data = {
        "thought_process": "Checking the inputs for safety...",
        "conclusion": "No threats found.",
        "confidence_score": 0.99,
        "is_safe": True,
        "rejection_reason": None,
    }
    model = InputProcessingOutputDTO.model_validate(data)
    assert model.is_safe is True
    assert model.rejection_reason is None


def test_input_processing_output_valid_unsafe() -> None:
    """Test that an unsafe InputProcessingOutputDTO instantiates properly with a reason."""
    data = {
        "thought_process": "Checking the inputs...",
        "conclusion": "Threat found.",
        "confidence_score": 0.95,
        "is_safe": False,
        "rejection_reason": "Contains malware.",
    }
    model = InputProcessingOutputDTO.model_validate(data)
    assert model.is_safe is False
    assert model.rejection_reason == "Contains malware."


def test_input_processing_output_invalid_unsafe_no_reason() -> None:
    """Test that an unsafe InputProcessingOutputDTO without a reason raises ValidationError."""
    data = {
        "thought_process": "Checking inputs...",
        "conclusion": "Threat found.",
        "confidence_score": 0.99,
        "is_safe": False,
        "rejection_reason": None,
    }
    with pytest.raises(ValidationError) as exc:
        InputProcessingOutputDTO.model_validate(data)

    assert "rejection_reason must be provided if is_safe is False" in str(exc.value)
