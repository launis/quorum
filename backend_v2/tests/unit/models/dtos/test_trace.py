import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.trace import (
    ProgressTracePayloadDTO,
    TraceEventMetadataDTO,
    TraceMatrixPayloadDTO,
    TraceScoringPayloadDTO,
)
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


def test_trace_matrix_payload_accepts_atom_quotes() -> None:
    """Strict TDD: Test that TraceMatrixPayloadDTO accepts atom_quotes field without raising ValidationError."""
    payload_none = {
        "raw_score": 4.5,
        "normalized_score": 90.0,
        "justification": "Test justification",
        "atom_quotes": None,
    }
    dto_none = TraceMatrixPayloadDTO.model_validate(payload_none)
    assert dto_none.atom_quotes is None

    payload_list = {
        "raw_score": 4.5,
        "normalized_score": 90.0,
        "justification": "Test justification",
        "atom_quotes": ["Evidence quote"],
    }
    dto_list = TraceMatrixPayloadDTO.model_validate(payload_list)
    assert dto_list.atom_quotes == ["Evidence quote"]


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


def test_execution_create_and_update_dto_negative_partitions() -> None:
    """Test ExecutionCreateDTO and ExecutionUpdateDTO validation and extra='forbid'."""
    from backend_v2.models.dtos.trace import ExecutionCreateDTO, ExecutionUpdateDTO

    # Positive test ExecutionCreateDTO
    create_dto = ExecutionCreateDTO(
        workflow_id="wor_1234567890abcdef",
        output_profile_id="prof_1234567890abcdef",
    )
    assert create_dto.workflow_id == "wor_1234567890abcdef"
    assert create_dto.output_profile_id == "prof_1234567890abcdef"
    assert create_dto.target_locale == "fi"
    assert create_dto.status == "PENDING"

    # Negative ExecutionCreateDTO: missing workflow_id or output_profile_id
    with pytest.raises(ValidationError):
        ExecutionCreateDTO.model_validate({})

    # ExecutionCreateDTO: output_profile_id is optional per Ingress Decoupling
    valid_no_profile = ExecutionCreateDTO.model_validate({"workflow_id": "wor_1234567890abcdef"})
    assert valid_no_profile.output_profile_id is None

    # Negative ExecutionCreateDTO: extra forbidden field
    with pytest.raises(ValidationError) as exc:
        ExecutionCreateDTO.model_validate(
            {
                "workflow_id": "wor_123",
                "output_profile_id": "prof_123",
                "unknown_field": "fail",
            }
        )
    assert "extra_forbidden" in str(exc.value) or "Extra inputs are not permitted" in str(exc.value)

    # Positive test ExecutionUpdateDTO
    update_dto = ExecutionUpdateDTO(progress=50, current_step="Evaluating atom graph")
    assert update_dto.progress == 50
    assert update_dto.current_step == "Evaluating atom graph"

    # Negative ExecutionUpdateDTO: progress > 100
    with pytest.raises(ValidationError):
        ExecutionUpdateDTO(progress=150)

    # Negative ExecutionUpdateDTO: progress < 0
    with pytest.raises(ValidationError):
        ExecutionUpdateDTO(progress=-10)

    # Negative ExecutionUpdateDTO: extra forbidden field
    with pytest.raises(ValidationError) as exc_up:
        ExecutionUpdateDTO.model_validate({"progress": 20, "unauthorized_extra": True})
    assert "extra_forbidden" in str(exc_up.value) or "Extra inputs are not permitted" in str(exc_up.value)


def test_progress_trace_payload_dto_validation_and_strictness() -> None:
    """Test ProgressTracePayloadDTO happy path, bounds, and extra='forbid'."""
    dto = ProgressTracePayloadDTO(message="Processing atoms", progress_pct=50)
    assert dto.message == "Processing atoms"
    assert dto.progress_pct == 50

    # Bounds: 0 and 100 valid
    assert ProgressTracePayloadDTO(message="Start", progress_pct=0).progress_pct == 0
    assert ProgressTracePayloadDTO(message="Done", progress_pct=100).progress_pct == 100

    # Out of bounds: > 100
    with pytest.raises(ValidationError):
        ProgressTracePayloadDTO(message="Overflow", progress_pct=101)

    # Out of bounds: < 0
    with pytest.raises(ValidationError):
        ProgressTracePayloadDTO(message="Underflow", progress_pct=-1)

    # Extra field forbidden
    with pytest.raises(ValidationError):
        ProgressTracePayloadDTO.model_validate({"message": "Test", "progress_pct": 10, "extra": "bad"})


def test_trace_event_metadata_dto_validation_and_strictness() -> None:
    """Test TraceEventMetadataDTO defaults, typed fields, and extra='forbid'."""
    dto_default = TraceEventMetadataDTO()
    assert dto_default.latency_ms is None
    assert dto_default.is_context_update is False
    assert dto_default.mcp_audit_traces == []
    assert dto_default.step_metadata is None

    dto_full = TraceEventMetadataDTO(
        latency_ms=123.45,
        chunk_size=10,
        context_char_length=5000,
        prompt_contexts=["ctx_1"],
        generated_schema={"type": "object"},
        is_context_update=True,
        estimated_token_count=150,
    )
    assert dto_full.latency_ms == 123.45
    assert dto_full.chunk_size == 10
    assert dto_full.context_char_length == 5000
    assert dto_full.prompt_contexts == ["ctx_1"]
    assert dto_full.generated_schema == {"type": "object"}
    assert dto_full.is_context_update is True
    assert dto_full.estimated_token_count == 150

    # Extra forbidden
    with pytest.raises(ValidationError):
        TraceEventMetadataDTO.model_validate({"latency_ms": 10.0, "unauthorized_extra": True})
