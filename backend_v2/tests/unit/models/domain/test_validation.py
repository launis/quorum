import pytest
from pydantic import ValidationError

from backend_v2.models.domain.validation import (
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


def test_system_warnings_state_extracts_and_ignores_extra() -> None:
    """Test that SystemWarningsStateDTO extracts _system_warnings and ignores other state fields."""
    warning_data = {
        "type": "Error",
        "title": "State Error",
        "error_code": "ERR_002",
        "detail": "State is corrupted.",
    }
    data = {
        "_system_warnings": [warning_data],
        "random_execution_state_field": "Value",
        "another_field": 123,
    }
    state = SystemWarningsStateDTO.model_validate(data)
    # The extra fields are ignored
    assert len(state.system_warnings) == 1
    with pytest.raises(AttributeError):
        _ = state.random_execution_state_field  # type: ignore[attr-defined]
