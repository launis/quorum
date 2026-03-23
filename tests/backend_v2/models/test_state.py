import pytest
import uuid
from datetime import datetime, timezone
from backend_v2.models.state import TraceEvent, WorkflowState, TombstoneEvent, StateProjector

def test_workflow_state_initialization():
    state = WorkflowState(workflow_id="test_wf")
    assert state.trace_version == 0
    assert len(state.execution_trace) == 0

def test_add_event_increments_version():
    state = WorkflowState(workflow_id="test_wf")
    event = TraceEvent(step_name="step1", event_type="output", content={"foo": "bar"})
    new_state = state.add_event(event)
    
    assert new_state.trace_version == 1
    assert len(new_state.execution_trace) == 1
    assert new_state.execution_trace[0] == event
    # Ensure original is immutable
    assert state.trace_version == 0

def test_state_projector_fold_trace():
    trace = [
        TraceEvent(step_name="step_a", event_type="output", content={"val": 1}, v=1),
        TraceEvent(step_name="step_b", event_type="input", content={"val": 2}, v=1),
        TraceEvent(step_name="step_a", event_type="output", content={"val": 3}, v=2),
        TombstoneEvent(step_name="step_c", redacted_hash="xyz123", v=2)
    ]
    
    projector = StateProjector(trace)
    
    # step_a should have the latest output
    assert projector.snapshot.get("step_a") == {"val": 3}
    # step_b was an input, our current projector ignores inputs in fold output cache.
    assert "step_b" not in projector.snapshot
    # step_c should be a tombstone
    assert projector.snapshot.get("step_c") == {"_redacted": True, "hash": "xyz123"}
    # Schema version should be max(v)
    assert projector.schema_version == 2

def test_state_projector_apply_delta():
    projector = StateProjector()
    assert projector.schema_version == 0
    
    event1 = TraceEvent(step_name="step_x", event_type="output", content={"data": "test"}, v=1)
    projector.apply_delta(event1)
    
    assert projector.snapshot == {"step_x": {"data": "test"}}
    assert projector.schema_version == 1
