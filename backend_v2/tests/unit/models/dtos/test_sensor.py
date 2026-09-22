"""Unit tests for SensorValidationContextDTO and EnsembleCallResultDTO."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.dag_models import AtomEvaluationResultDTO
from backend_v2.models.dtos.sensor import EnsembleCallResultDTO, SensorValidationContextDTO
from backend_v2.models.enums import ExecutionStatus


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


def test_ensemble_call_result_dto_defaults() -> None:
    """Test default values and immutability of EnsembleCallResultDTO."""
    dto = EnsembleCallResultDTO()
    assert dto.evaluations is None
    assert dto.usage.total_tokens == 0

    with pytest.raises(ValidationError):
        dto.evaluations = {}  # type: ignore[misc]


def test_ensemble_call_result_dto_with_evaluations() -> None:
    """Test EnsembleCallResultDTO with populated evaluations and usage."""
    atom_res = AtomEvaluationResultDTO(status=ExecutionStatus.PASSED, reasoning="Test passed")
    usage = TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15)
    dto = EnsembleCallResultDTO(
        evaluations={"tda_1": atom_res},
        usage=usage,
    )
    assert dto.evaluations is not None
    assert "tda_1" in dto.evaluations
    assert dto.evaluations["tda_1"].status == ExecutionStatus.PASSED
    assert dto.usage.total_tokens == 15


def test_ensemble_call_result_dto_extra_fields_forbidden() -> None:
    """Test that extra fields trigger ValidationError."""
    with pytest.raises(ValidationError):
        _ = EnsembleCallResultDTO(extra_field="disallowed")  # type: ignore[call-arg]
