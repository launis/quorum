import pytest
from tinydb import TinyDB
from backend.engine import WorkflowEngine
from unittest.mock import MagicMock, patch

@pytest.fixture
def test_db(tmp_path):
    db_path = tmp_path / "test_db.json"
    return str(db_path)

def test_missing_step_definition(test_db):
    """
    Scenario: Workflow refers to a step ID that does not exist in the DB.
    Expectation: The engine should skip the step and complete execution without crashing.
    """
    engine = WorkflowEngine(test_db)
    
    # Insert a workflow with a missing step
    wf_id = engine.workflows_table.insert({
        "name": "BrokenWorkflow",
        "steps": ["STEP_MISSING"]
    })
    
    # Execute
    exec_id = engine.execute_workflow(wf_id, {})
    
    # Check status
    status = engine.get_execution_status(exec_id)
    assert status['status'] == 'COMPLETED'
    assert len(status['step_results']) == 0

def test_empty_prompt_content(test_db):
    """
    Scenario: A step uses a prompt component that has empty content.
    Expectation: The agent should be executed with an empty system instruction.
    """
    engine = WorkflowEngine(test_db)
    
    # 1. Define Step
    engine.steps_table.insert({
        "id": "STEP_TEST",
        "component": "TestAgent",
        "execution_config": {
            "llm_prompts": ["PROMPT_EMPTY"]
        }
    })
    
    # 2. Define Prompt Component (Empty)
    engine.components_table.insert({
        "id": "PROMPT_EMPTY",
        "type": "prompt",
        "content": ""
    })
    
    # 3. Define Workflow
    wf_id = engine.workflows_table.insert({
        "name": "EmptyPromptWorkflow",
        "steps": ["STEP_TEST"]
    })
    
    # 4. Mock Agent Loading and Execution
    # We need to mock importlib.import_module to return a module that has TestAgent
    with patch('backend.engine.importlib.import_module') as mock_import:
        mock_module = MagicMock()
        mock_agent_class = MagicMock()
        mock_agent_instance = MagicMock()
        
        # Setup the mock chain
        mock_import.return_value = mock_module
        setattr(mock_module, "TestAgent", mock_agent_class)
        mock_agent_class.return_value = mock_agent_instance
        mock_agent_instance.execute.return_value = {"output": "success"}
        
        # Execute
        exec_id = engine.execute_workflow(wf_id, {})
        
        # Verify
        status = engine.get_execution_status(exec_id)
        assert status['status'] == 'COMPLETED'
        
        # Verify execute was called with empty system_instruction
        mock_agent_instance.execute.assert_called_once()
        call_args = mock_agent_instance.execute.call_args
        # kwargs['system_instruction'] should be "" (or stripped to "")
        assert call_args.kwargs.get('system_instruction') == ""

def test_missing_prompt_component(test_db):
    """
    Scenario: A step refers to a prompt ID that does not exist.
    Expectation: The agent should be executed with empty system instruction (or partial if others exist).
    """
    engine = WorkflowEngine(test_db)
    
    engine.steps_table.insert({
        "id": "STEP_TEST_MISSING_PROMPT",
        "component": "TestAgent",
        "execution_config": {
            "llm_prompts": ["PROMPT_NONEXISTENT"]
        }
    })
    
    wf_id = engine.workflows_table.insert({
        "name": "MissingPromptWorkflow",
        "steps": ["STEP_TEST_MISSING_PROMPT"]
    })
    
    with patch('backend.engine.importlib.import_module') as mock_import:
        mock_module = MagicMock()
        mock_agent_class = MagicMock()
        mock_agent_instance = MagicMock()
        
        mock_import.return_value = mock_module
        setattr(mock_module, "TestAgent", mock_agent_class)
        mock_agent_class.return_value = mock_agent_instance
        mock_agent_instance.execute.return_value = {"output": "success"}
        
        exec_id = engine.execute_workflow(wf_id, {})
        
        mock_agent_instance.execute.assert_called_once()
        assert mock_agent_instance.execute.call_args.kwargs.get('system_instruction') == ""
