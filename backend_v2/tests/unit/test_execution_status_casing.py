import pytest
from pydantic import ValidationError

from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.v2_core import ExecutionRecord


def test_execution_record_status_casing() -> None:
    """Test that ExecutionRecord strictly requires uppercase status values."""
    # This should fail because 'running' is lowercase
    with pytest.raises(ValidationError) as exc:
        ExecutionRecord(
            id="exe_1234567890123456",
            workflow_id="wor_1234567890123456",
            status="running",
            target_locale="fi",
            metadata=ExecutionMetadata(),
        )
    assert "Input should be" in str(exc.value)

    # This should succeed because 'RUNNING' is uppercase
    record = ExecutionRecord(
        id="exe_1234567890123456",
        workflow_id="wor_1234567890123456",
        output_profile_id="prof_1",
        status="RUNNING",
        target_locale="fi",
        metadata=ExecutionMetadata(),
    )
    assert record.status == "RUNNING"
