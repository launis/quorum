from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.core.engine import GraphEngine, WorkflowState
from backend.exceptions import AppException, ErrorCodes
from backend.models.workflow import WorkflowDefinition


@pytest.fixture
def engine():
    return GraphEngine()


def test_resolve_inputs_failure(engine):
    """Verify input resolution failure raises AppException."""
    # Test case: Accessing a list with a string key should raise TypeError
    state = WorkflowState(workflow_id="test", context_variables={"data": [1, 2, 3]})
    mapping = {"target": "$data.field"}

    with pytest.raises(AppException) as exc:
        engine._resolve_inputs(mapping, state)

    assert exc.value.error_code == ErrorCodes.INPUT_RESOLUTION_FAILED


@pytest.mark.asyncio
async def test_execute_workflow_task_not_found(engine):
    """Verify missing task raises TASK_NOT_FOUND."""
    workflow = WorkflowDefinition(id="test_wf", name="Test Workflow", description="Test Workflow", status="draft", version=1, is_public=False, organization_id="testorg", steps=["step1"])

    mock_repo = AsyncMock()
    mock_repo.get_step_by_id.return_value = {"id": "step1", "name": "Test Step", "task_key": "test_task"}

    with patch("backend.core.registry.TaskRegistry.get", return_value=None):
        with pytest.raises(AppException) as exc:
            await engine.execute_workflow(workflow, {"inputs": {}}, repository=mock_repo)

        assert exc.value.error_code == ErrorCodes.TASK_NOT_FOUND


@pytest.mark.asyncio
async def test_execute_workflow_input_validation_failed(engine):
    """Verify input validation failure raises AGENT_SCHEMA_VALIDATION_FAILED."""
    workflow = WorkflowDefinition(id="test_wf", name="Test Workflow", description="Test Workflow", status="draft", version=1, is_public=False, organization_id="testorg", steps=["step1"])

    mock_task = MagicMock()
    mock_task.input_schema.model_validate.side_effect = ValueError("Invalid Input")

    mock_repo = AsyncMock()
    mock_repo.get_step_by_id.return_value = {"id": "step1", "name": "Test Step", "task_key": "test_task"}

    with patch("backend.core.registry.TaskRegistry.get", return_value=mock_task):
        with pytest.raises(AppException) as exc:
            await engine.execute_workflow(workflow, {"inputs": {}}, repository=mock_repo)

        assert exc.value.error_code == ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED



