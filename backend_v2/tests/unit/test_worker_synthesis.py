import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from backend_v2.worker import execute_workflow_job
from backend_v2.models.v2_core import Workflow, WorkflowInputs
from backend_v2.core.hook_registry import HookResult

@pytest.mark.asyncio
async def test_worker_invokes_synthesis_hook():
    """Test that the worker invokes the text_consolidation_hook and updates the execution record."""
    ctx = {
        "engine": AsyncMock(),
        "repository": AsyncMock()
    }
    workflow_id = "wkf_abcd1234abcd1234"
    workflow_dict = {
        "id": workflow_id,
        "slug": "test_workflow",
        "name": "W1",
        "version": 1,
        "description": "D",
        "status": "draft",
        "default_profile_id": "default",
        "steps": []
    }
    ctx["repository"].get_workflow.return_value = workflow_dict
    
    from backend_v2.models.state import TraceEvent
    trace_mock = TraceEvent(step_name="step_1", event_type="output", content={"data": 123}, v=1)
    ctx["engine"].execute_workflow.return_value.execution_trace = [trace_mock]

    with patch("backend_v2.core.hook_registry.hook_registry.execute") as mock_execute:
        # Mock a successful text consolidation hook result
        mock_execute.return_value = HookResult(success=True, state_delta={"synthesized_markdown": "Test MD"})
        
        result = await execute_workflow_job(
            ctx=ctx,
            workflow_id=workflow_id,
            inputs={"test": "data"},
            execution_id="exec_1"
        )
        
        assert result["status"] == "COMPLETED"
        assert result["execution_id"] == "exec_1"
        mock_execute.assert_called_once()
        call_args = mock_execute.call_args
        assert call_args[0][0] == "text_consolidation_hook"
        
        # Verify that the DB was updated with the markdown
        ctx["repository"].update_execution.assert_any_call("exec_1", {"synthesized_markdown": "Test MD"})
