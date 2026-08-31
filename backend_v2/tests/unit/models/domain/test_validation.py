import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.domain.validation import (
    HardeningRetryDirectiveDTO,
    SystemWarningsStateDTO,
    ValidationHookPayloadDTO,
    ValidationResultDTO,
    ValidationWarningDTO,
)


def test_validation_hook_payload_accepts_dict() -> None:
    """Test that ValidationHookPayloadDTO accepts a dictionary."""
    data = {"key": "value", "another": 123}
    payload = ValidationHookPayloadDTO.model_validate(data)
    assert payload.root == data


def test_validation_hook_payload_rejects_non_dict() -> None:
    """Test that ValidationHookPayloadDTO rejects non-dictionary data."""
    data = ["list", "of", "items"]
    with pytest.raises(ValidationError):
        ValidationHookPayloadDTO.model_validate(data)


def test_validation_warning_requires_fields() -> None:
    """Test that ValidationWarningDTO requires type, title, error_code, detail."""
    data = {"type": "Error"}
    with pytest.raises(ValidationError):
        ValidationWarningDTO.model_validate(data)


def test_validation_warning_forbids_extra() -> None:
    """Test that ValidationWarningDTO forbids extra fields."""
    data = {
        "type": "Error",
        "title": "Invalid Data",
        "error_code": "ERR_001",
        "detail": "Data is invalid.",
        "extra_field": "Should fail",
    }
    with pytest.raises(ValidationError):
        ValidationWarningDTO.model_validate(data)


def test_validation_result_valid() -> None:
    """Test ValidationResultDTO with valid data."""
    warning_data = {
        "type": "Error",
        "title": "Invalid Data",
        "error_code": "ERR_001",
        "detail": "Data is invalid.",
    }
    data = {
        "is_valid": False,
        "errors": [warning_data],
    }
    result = ValidationResultDTO.model_validate(data)
    assert result.is_valid is False
    assert len(result.errors) == 1


def test_system_warnings_state_extracts_and_forbids_extra() -> None:
    """Test that SystemWarningsStateDTO extracts _system_warnings and rejects extra fields."""
    warning_data = {
        "type": "Error",
        "title": "State Error",
        "error_code": "ERR_002",
        "detail": "State is corrupted.",
    }
    data = {
        "_system_warnings": [warning_data],
    }
    state = SystemWarningsStateDTO.model_validate(data)
    assert len(state.system_warnings) == 1

    # Extra fields raise ValidationError due to extra="forbid"
    with pytest.raises(ValidationError):
        SystemWarningsStateDTO.model_validate(
            {
                "_system_warnings": [warning_data],
                "random_execution_state_field": "Value",
            }
        )


def test_validation_warning_telemetry() -> None:
    """Test that ValidationWarningDTO accepts optional entropy and telemetry_code."""
    data = {
        "type": "Warning",
        "title": "Low confidence score",
        "error_code": "WARN_045",
        "detail": "The LLM output exhibits high entropy.",
        "entropy": 4.12,
        "telemetry_code": "TELE_ENTROPY_HIGH",
    }
    warning = ValidationWarningDTO.model_validate(data)
    assert warning.entropy == 4.12
    assert warning.telemetry_code == "TELE_ENTROPY_HIGH"


def test_hardening_retry_directive() -> None:
    """Test that HardeningRetryDirectiveDTO enforces bounds and schemas."""
    data = {
        "retry_allowed": True,
        "max_retries": 3,
        "current_retry_count": 1,
        "target_block_ids": ["blk_1234567890123456"],
        "strictness_override": 80,
        "reason": "Verify exact match quote failed.",
    }
    directive = HardeningRetryDirectiveDTO.model_validate(data)
    assert directive.retry_allowed is True
    assert directive.max_retries == 3
    assert directive.current_retry_count == 1
    assert directive.strictness_override == 80

    # Test strictness validation constraint (>100 fails)
    invalid_data = data.copy()
    invalid_data["strictness_override"] = 150
    with pytest.raises(AppException):
        HardeningRetryDirectiveDTO.model_validate(invalid_data)

    # Test max_retries limit bounds
    invalid_max = data.copy()
    invalid_max["max_retries"] = 10
    with pytest.raises(AppException):
        HardeningRetryDirectiveDTO.model_validate(invalid_max)
