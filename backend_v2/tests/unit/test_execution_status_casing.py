from unittest.mock import AsyncMock
import pytest
from pydantic import ValidationError

from backend_v2.models.v2_core import ExecutionRecord


def test_execution_record_status_casing() -> None:
    """Test that ExecutionRecord strictly requires uppercase status values."""
    # This should fail because 'running' is lowercase
    with pytest.raises(ValidationError) as exc:
        ExecutionRecord(
            id="exe_1234567890123456",
            workflow_id="wor_1234567890123456",
            status="running",
        )
    assert "Input should be" in str(exc.value)

    # This should succeed because 'RUNNING' is uppercase
    record = ExecutionRecord(
        id="exe_1234567890123456",
        workflow_id="wor_1234567890123456",
        status="RUNNING",
    )
    assert record.status == "RUNNING"
