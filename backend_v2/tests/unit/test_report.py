import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.report import (
    GlobalContextVarsDTO,
    MatrixFieldsMixin,
    MatrixObservabilityDTO,
    MatrixObservabilityItem,
    ReportSynthesisDTO,
    XaiReportData,
)


def test_matrix_fields_mixin_instantiation() -> None:
    """Test that MatrixFieldsMixin can be instantiated and holds values."""
    dto = MatrixFieldsMixin(
        justification="Test reason",
        raw_result="5/5",
        normalized_score=100.0,
        raw_score=5.0,
        evaluated_atoms={"hash": True},
        extensions={"ext": "value"},
    )
    assert dto.justification == "Test reason"
    assert dto.raw_result == "5/5"


def test_xai_report_data_strictness() -> None:
    """Test XaiReportData strictness and mixin inheritance."""
    dto = XaiReportData(
        executive_summary="Summary",
        justification="Justification",
    )
    assert dto.executive_summary == "Summary"
    assert dto.justification == "Justification"

    # Should forbid extra fields due to strict=True, extra="forbid"
    with pytest.raises(ValidationError):
        XaiReportData.model_validate({"unknown_field": "fail"})


def test_global_context_vars_dto_strictness() -> None:
    """Test that GlobalContextVarsDTO correctly forbids extra unknown fields."""
    dto = GlobalContextVarsDTO(step_xai=XaiReportData(executive_summary="XAI"))
    assert dto.step_xai is not None
    assert dto.step_xai.executive_summary == "XAI"

    with pytest.raises(ValidationError):
        GlobalContextVarsDTO.model_validate({"step_unknown": "fail"})


def test_matrix_observability_dto() -> None:
    """Test MatrixObservabilityDTO and matrices dictionary structure."""
    dto = MatrixObservabilityDTO(
        true_atoms_count=10,
        false_atoms_count=2,
        matrices={
            "block_1": MatrixObservabilityItem(
                normalized_score=90.0,
                raw_result="9/10",
                justification="Good.",
            )
        },
    )
    assert dto.true_atoms_count == 10
    assert "block_1" in dto.matrices
    assert dto.matrices["block_1"].justification == "Good."

    with pytest.raises(ValidationError):
        MatrixObservabilityDTO.model_validate({"extra_field": True})


def test_report_synthesis_dto() -> None:
    """Test the synthesis wrapper for reports."""
    inputs = MatrixObservabilityDTO()
    gvars = GlobalContextVarsDTO()

    dto = ReportSynthesisDTO(inputs=inputs, global_context_vars=gvars)
    assert dto.inputs.true_atoms_count == 0
    assert dto.global_context_vars.step_xai is None
