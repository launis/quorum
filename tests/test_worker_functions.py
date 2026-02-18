
import pytest
import sys
from unittest.mock import MagicMock, AsyncMock, patch, mock_open

# Mock logfire before importing backend.worker if possible, or inside the test
mock_logfire = MagicMock()
sys.modules["logfire"] = mock_logfire
mock_logfire.span.return_value.__enter__.return_value = None

from datetime import datetime
from backend.worker import execute_workflow_job, WorkerSettings

@pytest.mark.asyncio
async def test_execute_workflow_job_success_with_debug_dump():
    """
    Verifies that execute_workflow_job runs successfully and handles the debug dump correctly,
    even when the engine returns a dict (which caused the previous crash).
    """
    # Mock Context
    mock_engine = MagicMock()
    mock_repo = AsyncMock()
    ctx = {
        "engine": mock_engine,
        "repository": mock_repo
    }

    # Mock Engine Output (Dict, NOT Pydantic Model - simulating the crash condition)
    # The crash was: 'dict' object has no attribute 'model_dump_json'
    engine_result = {
        "execution_id": "exec-123",
        "status": "completed",
        "context_variables": {"some": "data"},
        "timestamp": datetime.now() # Complex object to test serialization
    }
    mock_engine.execute_workflow = AsyncMock(return_value=engine_result)

    # Mock Repository Calls
    mock_repo.get_workflow.return_value = MagicMock(id="wf-1")
    
    # Mock File I/O to prevent writing to C:\Users\risto\Downloads
    # We want to verify that the code *attempts* to write and doesn't crash
    m_open = mock_open()
    
    with patch("builtins.open", m_open):
        with patch("backend.worker.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 2, 18, 12, 0, 0)
            mock_dt.strftime.return_value = "20260218_120000"
            
            # Execute
            result = await execute_workflow_job(
                ctx=ctx,
                workflow_id="test-workflow",
                inputs={"input": "val"},
                execution_id="exec-123"
            )

    # Assertions
    assert result == engine_result
    
    # Verify Repository Update
    mock_repo.update_execution.assert_called()
    
    # Verify Debug Dump was written
    # Check that open was called with the expected path
    # Note: user has hardcoded path in worker.py, so we check if open was called at all
    assert m_open.called
    handle = m_open()
    
    # Verify write was called (meaning serialization worked)
    # We don't strictly check content here, just that it didn't crash and tried to write
    handle.write.assert_called()
    
    # Verify log message (optional, but good for confirmation)
    # We'd need to mock logger, but ensuring no exception raised is the main test.

@pytest.mark.asyncio
async def test_execute_workflow_job_handles_pydantic_result():
    """
    Verifies that execute_workflow_job works if the engine returns a Pydantic model (forward compatibility).
    """
    mock_engine = MagicMock()
    mock_repo = AsyncMock()
    ctx = {"engine": mock_engine, "repository": mock_repo}

    class MockState:
        def model_dump_json(self, indent=2):
            return '{"status": "model"}'
    
    engine_result = MockState()
    mock_engine.execute_workflow = AsyncMock(return_value=engine_result)
    mock_repo.get_workflow.return_value = MagicMock(id="wf-1")

    m_open = mock_open()
    with patch("builtins.open", m_open):
        result = await execute_workflow_job(ctx, "wf-1", {}, "exec-1")

    assert result == engine_result
    handle = m_open()
    handle.write.assert_called_with('{"status": "model"}')
