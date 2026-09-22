"""Unit tests for SensorValidationContextDTO."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.sensor import SensorValidationContextDTO


def test_sensor_validation_context_dto_valid() -> None:
    """Test valid SensorValidationContextDTO initialization and immutability."""
    dto = SensorValidationContextDTO(
        sub_task="extract_atoms",
        execution_id="exe_12345",
        step_id="stp_67890",
    )
    assert dto.sub_task == "extract_atoms"
    assert dto.execution_id == "exe_12345"
    assert dto.step_id == "stp_67890"

    with pytest.raises(ValidationError):
        dto.sub_task = "new_task"  # type: ignore[misc]


def test_sensor_validation_context_dto_missing_required() -> None:
    """Test ValidationError when required sub_task field is omitted."""
    with pytest.raises(ValidationError):
        _ = SensorValidationContextDTO()  # type: ignore[call-arg]


def test_sensor_validation_context_dto_extra_fields() -> None:
    """Test ValidationError when extra forbidden fields are supplied."""
    with pytest.raises(ValidationError):
        _ = SensorValidationContextDTO(sub_task="extract", extra_val="invalid")  # type: ignore[call-arg]


def test_sensor_validation_context_dto_strict_type() -> None:
    """Test ValidationError when non-string type is provided under strict mode."""
    with pytest.raises(ValidationError):
        _ = SensorValidationContextDTO(sub_task=12345)  # type: ignore[arg-type]
