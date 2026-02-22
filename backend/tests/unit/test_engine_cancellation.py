import uuid
from unittest.mock import AsyncMock

import pytest
from pydantic import BaseModel

from backend.core.engine import GraphEngine
from backend.core.registry import TaskDefinition, TaskRegistry
from backend.models.workflow import WorkflowDefinition


class MockInput(BaseModel):
    pass


async def mock_task_handler(inputs: MockInput, execution_config: dict | None = None):
    return {"result": "ok"}


@pytest.fixture
def mock_registry():
    # Register a dummy task
    TaskDefinition(
        name="mock_task",
        description="Mock Task",
        input_schema=MockInput,
        output_schema=BaseModel,
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
    # 3rd call: cancelled (after execution loop checking final status)
    repository.get_execution_status.side_effect = ["running", "cancelled", "cancelled"]
    repository.get_execution.return_value = {}
    repository.get_step_by_id = AsyncMock(side_effect=lambda sid: {"id": sid, "task_key": "mock_task", "name": "MOCK"})

    # 2. Setup Workflow Definition
    workflow_def = WorkflowDefinition(
        id="test_workflow", name="Test Workflow", organization_id="org1", description="Test description", status="draft", version=1, is_public=False, steps=["step1", "step2"]
    )

    # 3. Setup Task Registry Mock
    # We mock TaskRegistry.get to return our dummy task def
    mock_task_def = TaskDefinition(
        output_schema=BaseModel, name="mock_task", description="Mock", input_schema=MockInput, handler=mock_task_handler
    )

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(TaskRegistry, "get", lambda k: mock_task_def)

        # 4. Execute
        engine = GraphEngine()
        initial_input = {"history_text": "start"}
        execution_id = str(uuid.uuid4())

        final_state = await engine.execute_workflow(
            definition=workflow_def, initial_input=initial_input, repository=repository, execution_id=execution_id
        )

        # 5. Verify
        # Expected: Step 1 executed, Step 2 NOT executed.
        # Status should be cancelled.

        assert "context_variables" in final_state
        assert final_state.get("status") == "cancelled"

        # Verify calls
        assert repository.get_execution_status.call_count == 2
