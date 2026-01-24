
import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.core.engine import GraphEngine
from backend.models.workflow import WorkflowDefinition, WorkflowStep
from backend.models.state import WorkflowState
from backend.core.registry import TaskRegistry, TaskDefinition
from pydantic import BaseModel

class MockInput(BaseModel):
    pass

async def mock_task_handler(inputs: MockInput, execution_config: dict = None):
    return {"result": "ok"}

@pytest.fixture
def mock_registry():
    # Register a dummy task
    task_def = TaskDefinition(
        name="mock_task",
        description="Mock Task",
        input_schema=MockInput,
        handler=mock_task_handler,
    )
    # We need to patch the singleton registry or ensure it's clean
    # For unit test simplicity, we assume we can register safely or mock the get method
    # But since Registry is a global singleton usually, let's just mock the get call inside Engine
    pass

@pytest.mark.asyncio
async def test_engine_graceful_cancellation():
    # 1. Setup Wrapper / Mocks
    repository = AsyncMock()
    
    # Mock get_execution_status side_effects:
    # 1st call: running (before step 1)
    # 2nd call: cancelled (before step 2)
    repository.get_execution_status.side_effect = ["running", "cancelled"]
    
    # Mock get_execution for hydration (optional, returns empty or valid state)
    repository.get_execution.return_value = {}

    # 2. Setup Workflow Definition
    step1 = WorkflowStep(id="step1", task_key="mock_task", inputs={})
    step2 = WorkflowStep(id="step2", task_key="mock_task", inputs={})
    
    workflow_def = WorkflowDefinition(
        id="test_workflow",
        steps=[step1, step2]
    )
    
    # 3. Setup Task Registry Mock
    # We mock TaskRegistry.get to return our dummy task def
    mock_task_def = TaskDefinition(
        name="mock_task",
        description="Mock",
        input_schema=MockInput,
        handler=mock_task_handler
    )
    
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(TaskRegistry, "get", lambda k: mock_task_def)
        
        # 4. Execute
        engine = GraphEngine()
        initial_input = {"history_text": "start"}
        execution_id = "exec-123"
        
        final_state = await engine.execute_workflow(
            definition=workflow_def,
            initial_input=initial_input,
            repository=repository,
            execution_id=execution_id
        )
        
        # 5. Verify
        # Expected: Step 1 executed, Step 2 NOT executed.
        # Status should be cancelled.
        
        assert "step_results" in final_state
        assert "step1" in final_state["step_results"]
        assert "step2" not in final_state["step_results"]
        assert final_state.get("status") == "cancelled"
        
        # Verify calls
        assert repository.get_execution_status.call_count == 2
