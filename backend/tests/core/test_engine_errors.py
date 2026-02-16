
import pytest
from unittest.mock import MagicMock, patch
from backend.core.engine import GraphEngine, WorkflowState
from backend.exceptions import AppException, ErrorCodes
from backend.models.workflow import WorkflowDefinition, WorkflowStep

@pytest.fixture
def engine():
    return GraphEngine()

def test_resolve_inputs_failure(engine):
    """Verify input resolution failure raises AppException."""
    # Test case: Accessing a list with a string key should raise TypeError
    state = WorkflowState(
        workflow_id="test",
        context_variables={"data": [1, 2, 3]}
    )
    mapping = {"target": "$data.field"}
    
    with pytest.raises(AppException) as exc:
        engine._resolve_inputs(mapping, state)
    
    assert exc.value.error_code == ErrorCodes.INPUT_RESOLUTION_FAILED



@pytest.mark.asyncio
async def test_execute_workflow_task_not_found(engine):
    """Verify missing task raises TASK_NOT_FOUND."""
    workflow = WorkflowDefinition(
        id="test_wf",
        description="Test Workflow",
        steps=[WorkflowStep(id="step1", task_key="missing.task", inputs={})]
    )
    
    with patch("backend.core.registry.TaskRegistry.get", return_value=None):
        with pytest.raises(AppException) as exc:
            await engine.execute_workflow(workflow, {"inputs": {}})
        
        assert exc.value.error_code == ErrorCodes.TASK_NOT_FOUND

@pytest.mark.asyncio
async def test_execute_workflow_input_validation_failed(engine):
    """Verify input validation failure raises AGENT_SCHEMA_VALIDATION_FAILED."""
    workflow = WorkflowDefinition(
        id="test_wf",
        description="Test Workflow",
        steps=[WorkflowStep(id="step1", task_key="valid.task", inputs={})]
    )
    
    mock_task = MagicMock()
    mock_task.input_schema.model_validate.side_effect = ValueError("Invalid Input")
    
    with patch("backend.core.registry.TaskRegistry.get", return_value=mock_task):
        with pytest.raises(AppException) as exc:
            await engine.execute_workflow(workflow, {"inputs": {}})
            
        assert exc.value.error_code == ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED

@pytest.mark.asyncio
async def test_execute_workflow_chat_parsing_failed(engine):
    """Verify chat log parsing failure raises INVALID_JSON_PAYLOAD."""
    workflow = WorkflowDefinition(
        id="test_wf",
        description="Test Workflow",
        steps=[]
    )
    
    # Mock bad input that triggers parser
    inputs = {"history_text": "bad_chat_log"}
    
    # Mock ChatLogParser to fail
    with patch("backend.services.chat_log_parser.ChatLogParser.parse", side_effect=ValueError("Parsing Failed")):
         with pytest.raises(AppException) as exc:
            await engine.execute_workflow(workflow, {"inputs": inputs})
            
         assert exc.value.error_code == ErrorCodes.INVALID_JSON_PAYLOAD

