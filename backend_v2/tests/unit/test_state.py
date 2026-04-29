"""Unit tests for the Event Sourcing State components and StepOutputDTO."""

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.state import StateProjector, TombstoneEvent, TraceEvent


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

    # Text payload inference
    dto_a = next(dto for dto in results if dto.block_id == "blk_a")
    assert dto_a.step_id == "stp_123"
    assert dto_a.data_type == "text"
    assert dto_a.payload == "Some text payload"

    # Matrix payload inference
    dto_b = next(dto for dto in results if dto.block_id == "blk_b")
    assert dto_b.step_id == "stp_123"
    assert dto_b.data_type == "matrix"
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
