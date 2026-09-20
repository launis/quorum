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
