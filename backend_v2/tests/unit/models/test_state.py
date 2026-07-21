from unittest.mock import AsyncMock
"""Unit tests for the Event Sourcing State components and StepOutputDTO."""

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.state import StateProjector, StepExecutionEnvelope, TombstoneEvent, TraceEvent


def test_state_projector_fold_trace_happy_path() -> None:
    """Test that valid trace events are folded correctly into StepOutputDTOs."""
    # Create mock events
    event1 = TraceEvent(
        step_name="stp_123",
        event_type="output",
        content={"blk_a": "Some text payload", "blk_b": {"nested": "matrix data"}},
    )

    projector = StateProjector()
    results = projector.fold_trace([event1])

    assert len(results) == 2

    # Text payload inference (Schema driven, type is unknown at projection)
    dto_a = next(dto for dto in results if dto.block_id == "blk_a")
    assert dto_a.step_id == "stp_123"
    assert dto_a.data_type == "unknown"
    assert dto_a.payload == "Some text payload"

    # Matrix payload inference (Schema driven, type is unknown at projection)
    dto_b = next(dto for dto in results if dto.block_id == "blk_b")
    assert dto_b.step_id == "stp_123"
    assert dto_b.data_type == "unknown"
    assert dto_b.payload == {"nested": "matrix data"}


def test_state_projector_snapshot_property() -> None:
    """Test that the snapshot property builds the strictly typed list."""
    event1 = TraceEvent(
        step_name="stp_999",
        event_type="output",
        content={"blk_x": 42},  # Int payload -> "unknown" type
    )

    projector = StateProjector([event1])
    results = projector.snapshot

    assert len(results) == 1
    assert results[0].step_id == "stp_999"
    assert results[0].block_id == "blk_x"
    assert results[0].data_type == "unknown"
    assert results[0].payload == 42


def test_state_projector_tombstone_event() -> None:
    """Test that tombstone events replace content correctly."""
    event_output = TraceEvent(step_name="stp_del", event_type="output", content={"blk_1": "sensitive"})
    event_tombstone = TombstoneEvent(step_name="stp_del", redacted_hash="hash_123")

    # Tombstone is applied AFTER output because it has a newer timestamp (if sorted correctly, or sequentially applied)
    # We pass them sequentially to apply_delta
    projector = StateProjector()
    projector.apply_delta(event_output)
    projector.apply_delta(event_tombstone)

    results = projector.snapshot
    assert len(results) == 2

    redacted = next(dto for dto in results if dto.block_id == "_redacted")
    assert redacted.payload is True

    hash_dto = next(dto for dto in results if dto.block_id == "hash")
    assert hash_dto.payload == "hash_123"


def test_state_projector_fail_fast_on_legacy_data() -> None:
    """Test that the Zero-Compromise Pledge enforces strict dictionary structures."""
    projector = StateProjector()
    # Force inject a legacy non-dict state (simulating a bypass or legacy DB load)
    projector._snapshot["stp_legacy"] = "I am a raw string output from V1"

    with pytest.raises(AppException) as excinfo:
        _ = projector.snapshot

    assert excinfo.value.status_code == 500
    assert excinfo.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED
    assert "Legacy flat trace detected" in excinfo.value.message


def test_step_execution_envelope_strictness() -> None:
    """Test that StepExecutionEnvelope enforces V2CoreBase strictness."""
    dto = StepExecutionEnvelope(execution_id="exec_123", v2_engine=True)
    assert dto.execution_id == "exec_123"
    assert dto.v2_engine is True

    with pytest.raises(ValidationError):
        StepExecutionEnvelope.model_validate({"execution_id": "exec_1", "extra_field": "fail"})


def test_workflow_state_inherits_execution_core_fields() -> None:
    """Phase 2: Verify WorkflowState correctly inherits ExecutionCoreFields SSOT."""
    from backend_v2.models.execution_core import ExecutionCoreFields
    from backend_v2.models.state import ErrorTraceEvent, WorkflowState

    # 1. Verify inheritance chain
    assert issubclass(WorkflowState, ExecutionCoreFields), "WorkflowState must inherit from ExecutionCoreFields"

    # 2. Verify all 5 core fields are accessible
    core_field_names = {
        "status",
        "execution_trace",
        "execution_trace_storage_path",
        "context_variables",
        "context_variables_storage_path",
    }
    ws_fields = set(WorkflowState.model_fields.keys())
    missing = core_field_names - ws_fields
    assert not missing, f"WorkflowState missing inherited core fields: {missing}"

    # 3. Verify execution_trace accepts full union type (parity upgrade)
    error_event = ErrorTraceEvent(step_name="test_step", error_code="ERR_TEST", error_message="test error")
    ws = WorkflowState(workflow_id="wf_testtest1234")
    ws_with_error = ws.add_event(error_event)
    assert len(ws_with_error.execution_trace) == 1
    event = ws_with_error.execution_trace[0]
    assert isinstance(event, ErrorTraceEvent)
    assert event.error_code == "ERR_TEST"
