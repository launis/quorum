"""Unit tests for the FlatFileService."""

import pytest
import json
import uuid
from backend_v2.services.flattener import FlatFileService
from backend_v2.models.v2_core import ExecutionRecord
from backend_v2.models.state import TraceEvent
from backend_v2.models.enums import ExecutionStatus

def test_flat_file_service_flatten_results() -> None:
    """Test that execution traces are flattened correctly according to V2 specs."""
    execution_id = f"exe_{uuid.uuid4().hex}"
    
    event1 = TraceEvent(
        step_name="stp_1",
        event_type="output",
        content={"blk_a": "Some text", "blk_b": {"nested_key": 100}}
    )
    
    # We create a dummy ExecutionRecord
    record = ExecutionRecord(
        id=execution_id,
        workflow_id="wf_test",
        status=ExecutionStatus.COMPLETED,
        execution_trace=[event1]
    )
    
    flat_data = FlatFileService.flatten_results(record)
    
    assert flat_data["execution_id"] == execution_id
    assert flat_data["workflow_id"] == "wf_test"
    assert flat_data["status"] == "completed"
    
    # Check flattened trace data
    assert flat_data["stp_1_blk_a"] == "Some text"
    # Dictionaries should be JSON serialized
    assert flat_data["stp_1_blk_b"] == '{"nested_key": 100}'

def test_flat_file_service_empty_results() -> None:
    """Test flat file service with no trace results."""
    execution_id = f"exe_{uuid.uuid4().hex}"
    record = ExecutionRecord(
        id=execution_id,
        workflow_id="wf_empty",
        status=ExecutionStatus.FAILED,
        execution_trace=[]
    )
    
    flat_data = FlatFileService.flatten_results(record)
    
    assert flat_data["execution_id"] == execution_id
    assert flat_data["workflow_id"] == "wf_empty"
    assert flat_data["status"] == "failed"
    # No extra keys
    assert "stp_1_blk_a" not in flat_data
