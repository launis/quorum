from unittest.mock import AsyncMock
import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.trace import TraceMatrixPayloadDTO, TraceScoringPayloadDTO


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
