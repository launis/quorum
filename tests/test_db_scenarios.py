import pytest
import asyncio
from backend.core.engine import WorkflowEngine
from backend.database.repository import TinyDBRepository
from backend.database.wrapper import TinyDBClient
from unittest.mock import MagicMock, patch

@pytest.fixture
def test_db_path(tmp_path):
    return str(tmp_path / "test_db.json")

@pytest.fixture
def engine(test_db_path):
    client = TinyDBClient(test_db_path)
    repo = TinyDBRepository(client)
    # Initialize Engine with explicit repository (bypassing auto-wiring)
    # Initialize Engine with explicit repository (bypassing auto-wiring)
    from backend.services.agent_registry import AgentRegistry
    from backend.services.prompt_builder import PromptBuilder
    from backend.services.storage import LocalFileStorage
    from backend.services.document_service import DocumentService

    storage = LocalFileStorage()
    registry = AgentRegistry(repo)
    # We must explicitly discover agents for the test scenarios to work
    # Since registry.discover() is async, and this is a sync fixture, we might have issues.
    # However, tests use 'mock_agent_instance' injected directly into registry.agents_map later.
    # So skip automated discovery for now or rely on manual injection.
    
    prompt_builder = PromptBuilder(repo, registry)
    doc_service = DocumentService(storage)

    return WorkflowEngine(
        db_path=test_db_path,
        repository=repo,
        registry=registry,
        prompt_builder=prompt_builder,
        storage_client=storage,
        document_service=doc_service
    )

def test_missing_step_definition(engine):
    """
    Scenario: Workflow refers to a step ID that does not exist in the DB.
    Expectation: The engine should skip the step or fail gracefully. V2 logic might raise error or skip.
    """
    # Insert a workflow with a missing step
    # Use synchronous DB access for setup
    
    # Direct table access for sync setup
    engine.repository.workflows.insert({
        "id": "wf_missing_step",
        "name": "BrokenWorkflow",
        "steps": ["STEP_MISSING"]
    })

    async def run_test():
        # Execute
        # In V2, execution creation checks workflow existence.
        exec_id = await engine.create_execution("wf_missing_step", {})
        
        # Call execute_workflow_task directly to verify the separated logic
        await engine.execute_workflow_task(exec_id, "wf_missing_step", {})

        # Fetch record to verify status
        record = await engine.repository.get_execution(exec_id)
        
        assert record['status'] == 'failed'
        assert "No steps defined" in record['error']

    asyncio.run(run_test())

def test_empty_prompt_content(engine):
    """
    Scenario: A step uses a prompt component that has empty content.
    Expectation: The agent should be executed with an empty system instruction.
    """
    # 1. Define Step
    engine.repository.steps.insert({
        "id": "STEP_TEST",
        "component": "TestAgent",
        "execution_config": {
            "llm_prompts": ["PROMPT_EMPTY"]
        }
    })
    
    # 2. Define Prompt Component (Empty)
    engine.repository.components.insert({
        "id": "PROMPT_EMPTY",
        "type": "prompt",
        "content": ""
    })
    
    # 0. Seed Model Registry (Required for V2 resolution)
    engine.repository.system_config.insert({
        "type": "model_registry",
        "models": {"mock_provider": {"mock_model": {"model_name": "mock", "provider": "mock"}}}
    })

    # ... (Defined Step) ...
    # 3. Define Workflow
    engine.repository.workflows.insert({
        "id": "wf_empty_prompt",
        "name": "EmptyPromptWorkflow",
        "steps": ["STEP_TEST"],
        "default_model_mapping": {"STEP_TEST": "mock_model"}
    })
    
    # 4. Mock Agent Loading via Injection (V2 Pattern)
    mock_agent_instance = MagicMock()
    async def mock_execute(state, *args, **kwargs):
        return state
    mock_agent_instance.execute.side_effect = mock_execute
    
    # Inject into registry directly
    engine.registry.agents_map["TestAgent"] = mock_agent_instance
    
    async def run():
        exec_id = await engine.create_execution("wf_empty_prompt", {})
        # Verify direct execution
        await engine.execute_workflow_task(exec_id, "wf_empty_prompt", {})
        return await engine.repository.get_execution(exec_id)

    result = asyncio.run(run())
    
    assert result['status'] == 'completed'
    
    # Verify execute was called
    mock_agent_instance.execute.assert_called_once()

def test_missing_prompt_component(engine):
    """
    Scenario: A step refers to a prompt ID that does not exist.
    Expectation: The agent should be executed with empty system instruction.
    """
    engine.repository.steps.insert({
        "id": "STEP_TEST_MISSING_PROMPT",
        "component": "TestAgent",
        "execution_config": {
            "llm_prompts": ["PROMPT_NONEXISTENT"]
        }
    })
    
    # Seed Registry
    engine.repository.system_config.insert({
        "type": "model_registry",
        "models": {"mock_provider": {"mock_model": {"model_name": "mock", "provider": "mock"}}}
    })

    engine.repository.workflows.insert({
        "id": "wf_missing_prompt",
        "name": "MissingPromptWorkflow",
        "steps": ["STEP_TEST_MISSING_PROMPT"],
        "default_model_mapping": {"STEP_TEST_MISSING_PROMPT": "mock_model"}
    })
    
    mock_agent_instance = MagicMock()
    async def mock_execute(state, *args, **kwargs): return state
    mock_agent_instance.execute.side_effect = mock_execute
    
    # Inject
    engine.registry.agents_map["TestAgent"] = mock_agent_instance
    
    async def run():
        exec_id = await engine.create_execution("wf_missing_prompt", {})
        await engine.execute_workflow_task(exec_id, "wf_missing_prompt", {})
        return await engine.repository.get_execution(exec_id)

    result = asyncio.run(run())
    assert result['status'] == 'completed'
