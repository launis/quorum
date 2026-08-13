import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.trace import TraceMatrixPayloadDTO, TraceScoringPayloadDTO
from backend_v2.models.enums import ExecutionStatus


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


def test_trace_matrix_payload_coerces_failed_string() -> None:
    """Test that TraceMatrixPayloadDTO correctly coerces 'FAILED' string to ExecutionStatus.FAILED."""
    payload = {"raw_score": 4.5, "evaluated_atoms": {"a0": "FAILED", "a1": "PASSED"}}
    dto = TraceMatrixPayloadDTO.model_validate(payload)
    assert dto.evaluated_atoms is not None
    assert dto.evaluated_atoms["a0"] == ExecutionStatus.FAILED
    assert dto.evaluated_atoms["a1"] == ExecutionStatus.PASSED


def test_trace_matrix_payload_rejects_raw_bool() -> None:
    """Test that TraceMatrixPayloadDTO explicitly rejects raw bool values (True/False)."""
    payload = {"raw_score": 4.5, "evaluated_atoms": {"a0": False}}
    with pytest.raises(ValidationError) as exc:
        TraceMatrixPayloadDTO.model_validate(payload)
    assert "Input should be" in str(exc.value)

    payload_true = {"raw_score": 4.5, "evaluated_atoms": {"a0": True}}
    with pytest.raises(ValidationError) as exc_true:
        TraceMatrixPayloadDTO.model_validate(payload_true)
    assert "Input should be" in str(exc_true.value)
