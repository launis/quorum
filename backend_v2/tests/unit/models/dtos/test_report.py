import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.report.context import GlobalContextVarsDTO
from backend_v2.models.dtos.report.matrix import (
    MatrixFieldsMixin,
    MatrixObservabilityDTO,
    MatrixObservabilityItem,
    TraceMatrixPayloadDTO,
)
from backend_v2.models.dtos.report.scoring import TraceScoringPayloadDTO
from backend_v2.models.dtos.report.specialists import XaiReportData
from backend_v2.models.dtos.report.synthesis import ReportSynthesisDTO


def test_matrix_fields_mixin_instantiation() -> None:
    """Test that MatrixFieldsMixin can be instantiated and holds values."""
    dto = MatrixFieldsMixin(
        justification="Test reason",
        normalized_score=100.0,
        raw_score=5.0,
        evaluated_atoms={"hash": True},
        extensions={"ext": "value"},
    )
    assert dto.justification == "Test reason"


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


def test_trace_scoring_payload_strictness() -> None:
    """Test TraceScoringPayloadDTO enforces Phase 9 extra='forbid'."""
    dto = TraceScoringPayloadDTO(total_score=5.0)
    assert dto.total_score == 5.0

    with pytest.raises(ValidationError) as exc:
        TraceScoringPayloadDTO(total_score=5.0, extra_field="fail")  # type: ignore
    assert "Extra inputs are not permitted" in str(exc.value)


def test_trace_matrix_payload_strictness() -> None:
    """Test TraceMatrixPayloadDTO enforces strict rules."""
    dto = TraceMatrixPayloadDTO(raw_score=4.5)
    assert dto.raw_score == 4.5

    with pytest.raises(ValidationError):
        TraceMatrixPayloadDTO(raw_score=4.5, extra_field="fail")  # type: ignore


def test_trace_matrix_payload_accepts_allowed_extensions() -> None:
    """Strict TDD: Test that TraceMatrixPayloadDTO accepts allowed_extensions field without raising ValidationError."""
    payload = {
        "raw_score": 4.5,
        "normalized_score": 90.0,
        "justification": "Test justification",
        "allowed_extensions": ["falsification", "coaching", "remediation_steps"],
    }
    # This should succeed without raising any ValidationError
    dto = TraceMatrixPayloadDTO.model_validate(payload)
    assert dto.raw_score == 4.5
    assert dto.allowed_extensions == ["falsification", "coaching", "remediation_steps"]
