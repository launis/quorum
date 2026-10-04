import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.domain.security import (
    InputProcessingOutputDTO,
    SanitizationResultDTO,
    SecurityCheck,
    SecurityPayloadDTO,
)
from backend_v2.models.enums import LaxRiskLevel


def test_security_payload_dto_from_dict() -> None:
    """Test SecurityPayloadDTO validation wrapping raw dictionary into root."""
    raw = {"input_key": "some text"}
    dto = SecurityPayloadDTO.model_validate(raw)
    assert dto.root == raw


def test_security_payload_dto_from_instance() -> None:
    """Test SecurityPayloadDTO validation preserving existing instance."""
    original = SecurityPayloadDTO(root={"input_key": "clean"})
    validated = SecurityPayloadDTO.model_validate(original)
    assert validated.root == {"input_key": "clean"}


def test_sanitization_result_dto_valid() -> None:
    """Test SanitizationResultDTO valid instantiation."""
    data = {
        "sanitized_inputs": {"k": "v"},
        "security_status": "CLEAN",
        "threat_detected": False,
    }
    model = SanitizationResultDTO.model_validate(data)
    assert model.security_status == "CLEAN"
    assert model.threat_detected is False


def test_sanitization_result_dto_empty_status() -> None:
    """Test SanitizationResultDTO fails on empty security_status."""
    data = {
        "sanitized_inputs": {"k": "v"},
        "security_status": "",
        "threat_detected": False,
    }
    with pytest.raises(ValidationError):
        SanitizationResultDTO.model_validate(data)


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


def test_security_check_exact_boundaries() -> None:
    """Test SecurityCheck accepts exact 1.0 and 3.0 boundary scores."""
    data = {
        "threat_detected": False,
        "risk_level": LaxRiskLevel.LOW,
        "risk_score": 3.0,
        "simulation_score": 1.0,
        "anonymized": False,
    }
    model = SecurityCheck.model_validate(data)
    assert model.risk_score == 3.0


def test_security_check_lower_boundary_score() -> None:
    """Test that SecurityCheck fails on score lower than 1.0."""
    data = {
        "threat_detected": True,
        "risk_level": LaxRiskLevel.HIGH,
        "risk_score": 0.9,
        "simulation_score": 1.0,
        "anonymized": False,
    }
    with pytest.raises(AppException) as exc:
        SecurityCheck.model_validate(data)

    assert "Score must be between 1.0 and 3.0 inclusive." in exc.value.message


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


def test_security_extra_fields_forbidden() -> None:
    """Test that all security models reject unknown extra fields."""
    with pytest.raises(ValidationError):
        SanitizationResultDTO.model_validate(
            {"sanitized_inputs": {}, "security_status": "OK", "threat_detected": False, "extra": 1}
        )

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
