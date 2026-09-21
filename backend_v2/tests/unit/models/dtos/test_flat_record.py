"""Unit tests for FlatExecutionRecordDTO."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.flat_record import FlatExecutionRecordDTO


def test_flat_execution_record_dto_defaults() -> None:
    """Verify FlatExecutionRecordDTO default values and field assignment."""
    dto = FlatExecutionRecordDTO(
        execution_id="exe_test123",
        workflow_id="wor_alpha",
        status="COMPLETED",
    )
    assert dto.execution_id == "exe_test123"
    assert dto.workflow_id == "wor_alpha"
    assert dto.status == "COMPLETED"
    assert dto.global_score is None
    assert dto.has_warning is False
    assert dto.matrix_metrics == {}


def test_flat_execution_record_dto_to_csv_dict() -> None:
    """Verify to_csv_dict merges base fields and matrix metrics into flat mapping."""
    dto = FlatExecutionRecordDTO(
        execution_id="exe_test456",
        workflow_id="wor_beta",
        status="FAILED",
        global_score=78.5,
        has_warning=True,
        matrix_metrics={"score_leadership": 4.5, "badge": "gold", "passed": True},
    )
    csv_dict = dto.to_csv_dict()
    assert csv_dict["execution_id"] == "exe_test456"
    assert csv_dict["workflow_id"] == "wor_beta"
    assert csv_dict["status"] == "FAILED"
    assert csv_dict["global_score"] == 78.5
    assert csv_dict["has_warning"] is True
    assert csv_dict["score_leadership"] == 4.5
    assert csv_dict["badge"] == "gold"
    assert csv_dict["passed"] is True


def test_flat_execution_record_dto_extra_fields_forbid() -> None:
    """Verify FlatExecutionRecordDTO rejects extra fields fail-fast."""
    with pytest.raises(ValidationError):
        FlatExecutionRecordDTO(
            execution_id="exe_test789",
            workflow_id="wor_gamma",
            status="COMPLETED",
            extra_field="invalid",  # type: ignore[call-arg]
        )


def test_flat_execution_record_dto_type_validation_fail_fast() -> None:
    """Verify FlatExecutionRecordDTO rejects invalid types fail-fast."""
    with pytest.raises(ValidationError):
        FlatExecutionRecordDTO(
            execution_id=12345,  # type: ignore[arg-type]
            workflow_id="wor_delta",
            status="COMPLETED",
        )
