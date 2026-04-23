import pytest
from unittest.mock import AsyncMock, MagicMock

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.services.orchestrator.strategies.llm import LLMNodeStrategy


@pytest.fixture
def mock_repo() -> MagicMock:
    repo = MagicMock()
    repo.get_step_by_id = AsyncMock()
    repo.get_all_prompt_blocks = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def mock_compiler() -> MagicMock:
    return MagicMock()


@pytest.fixture
def llm_strategy(mock_repo: MagicMock, mock_compiler: MagicMock) -> LLMNodeStrategy:
    return LLMNodeStrategy(repository=mock_repo, prompt_compiler=mock_compiler)


@pytest.mark.asyncio
async def test_execute_fails_fast_if_no_blueprint(llm_strategy: LLMNodeStrategy) -> None:
    """Test that LLMNodeStrategy fails fast if task_blueprint is missing."""
    
    # Create a step without task_blueprint
    step = MagicMock()
    step.id = "step_1"
    del step.task_blueprint

    projector = MagicMock()
    projector.snapshot = {}

    context = MagicMock()
    context.execution_id = "exec_1"
    
    with pytest.raises(AppException) as exc_info:
        await llm_strategy.execute(
            step=step,
            projector=projector,
            context=context,
            frozen_ctx=None,
            trace=[]
        )
    
    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value
    assert "has no task_blueprint configured" in exc_info.value.message


@pytest.mark.asyncio
async def test_execute_fails_fast_if_blueprint_not_found(llm_strategy: LLMNodeStrategy, mock_repo: MagicMock) -> None:
    """Test that LLMNodeStrategy fails fast if task_blueprint is not found in database."""
    
    step = MagicMock()
    step.id = "step_1"
    step.task_blueprint = "invalid_blueprint_id"

    projector = MagicMock()
    projector.snapshot = {}

    context = MagicMock()
    context.execution_id = "exec_1"

    # Mock DB returning None
    mock_repo.get_step_by_id.return_value = None

    with pytest.raises(AppException) as exc_info:
        await llm_strategy.execute(
            step=step,
            projector=projector,
            context=context,
            frozen_ctx=None,
            trace=[]
        )
    
    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value
    assert "not found" in exc_info.value.message


@pytest.mark.asyncio
async def test_execute_fails_fast_on_missing_profile_id(llm_strategy: LLMNodeStrategy, mock_repo: MagicMock) -> None:
    """Test that execution fails fast if metadata is missing profile_id."""
    
    step = MagicMock()
    step.id = "step_1"
    step.task_blueprint = "bp_1"

    projector = MagicMock()
    projector.snapshot = {}

    context = MagicMock()
    context.execution_id = "exec_1"
    context.workflow_id = "wf_1"
    context.metadata = {}  # MISSING profile_id

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_0123456789abcdef0123456789abcdef",
        "slug": "test_step",
        "name": {"default_locale": "en", "translations": {"en": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Test"}},
        "prompt_blocks": ["block_1"],
        "model_strategy": "standard",
    }
    
    # Needs to bypass pre-hooks smoothly
    mock_hook_state = MagicMock()
    mock_hook_state.inputs = {}
    llm_strategy.run_pre_hooks = AsyncMock(return_value=mock_hook_state)

    from backend_v2.exceptions import ConfigurationError
    with pytest.raises(ConfigurationError) as exc_info:
        await llm_strategy.execute(
            step=step,
            projector=projector,
            context=context,
            frozen_ctx=None,
            trace=[]
        )
        
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value
    assert "missing mandatory 'profile_id'" in exc_info.value.message


@pytest.mark.asyncio
async def test_execute_fails_fast_on_missing_prompt_block(llm_strategy: LLMNodeStrategy, mock_repo: MagicMock) -> None:
    """Test that execution fails fast if a referenced prompt block is missing from database."""
    
    step = MagicMock()
    step.id = "step_1"
    step.task_blueprint = "bp_1"
    step.input_mappings = {}

    projector = MagicMock()
    projector.snapshot = {}

    context = MagicMock()
    context.execution_id = "exec_1"
    context.workflow_id = "wf_1"
    context.metadata = {"profile_id": "prof_123"}

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_0123456789abcdef0123456789abcdef",
        "slug": "test_step",
        "name": {"default_locale": "en", "translations": {"en": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Test"}},
        "prompt_blocks": ["missing_block_999"],
        "model_strategy": "standard",
    }
    
    # DB returns no blocks
    mock_repo.get_all_prompt_blocks.return_value = [{"id": "other_block"}]
    
    # Needs to bypass pre-hooks smoothly
    mock_hook_state = MagicMock()
    mock_hook_state.inputs = {}
    llm_strategy.run_pre_hooks = AsyncMock(return_value=mock_hook_state)

    with pytest.raises(AppException) as exc_info:
        await llm_strategy.execute(
            step=step,
            projector=projector,
            context=context,
            frozen_ctx=None,
            trace=[]
        )
        
    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "PromptBlock 'missing_block_999' not found" in exc_info.value.message


@pytest.mark.asyncio
async def test_execute_success_path_structured_output(llm_strategy: LLMNodeStrategy, mock_repo: MagicMock, mock_compiler: MagicMock) -> None:
    """Test a successful execution path using structured output to cover core orchestration."""
    
    step = MagicMock()
    step.id = "step_success"
    step.task_blueprint = "bp_success"
    step.input_mappings = {"$test": "path.to.test"}
    step.allowed_mcp_tools = []

    projector = MagicMock()
    projector.snapshot = {"path": {"to": {"test": "value"}}}

    context = MagicMock()
    context.execution_id = "exec_1"
    context.workflow_id = "wf_1"
    context.metadata = {"profile_id": "prof_123", "target_locale": "en"}
    context.model_strategy = "standard"
    context.expected_inputs = []

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_0123456789abcdef0123456789abcdef",
        "slug": "test_step",
        "name": {"default_locale": "en", "translations": {"en": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Test"}},
        "prompt_blocks": ["block_1"],
        "model_strategy": "standard",
    }
    
    mock_repo.get_all_prompt_blocks.return_value = [{"id": "block_1", "category_id": "llm"}]
    
    # Needs to bypass pre-hooks smoothly
    mock_hook_state = MagicMock()
    mock_hook_state.inputs = {"path": {"to": {"test": "value"}}}
    llm_strategy.run_pre_hooks = AsyncMock(return_value=mock_hook_state)
    llm_strategy.run_post_hooks = AsyncMock(return_value={"blocks": []})
    
    # Mock Compiler returns
    mock_compiler.compile_static_instructions.return_value = "static"
    mock_compiler.compile_dynamic_instructions.return_value = "dynamic"
    mock_compiler.compile_blind_system_instruction.return_value = "blind"
    mock_compiler.generate_mcp_instruction.return_value = ""
    mock_compiler.build_xml_context.return_value = "<xml></xml>"
    mock_schema = MagicMock()
    mock_schema.model_json_schema.return_value = {}
    mock_compiler.build_dynamic_schema.return_value = mock_schema
    mock_compiler.compile_xml_rubrics.return_value = "rubrics"
    
    # Mock LLM Client
    mock_client = AsyncMock()
    mock_result = MagicMock()
    mock_result.model_dump.return_value = {"blocks": []}
    mock_client.run_structured_task.return_value = (mock_result, {"total_tokens": 100})
    
    from unittest.mock import patch
    with patch("backend_v2.services.orchestrator.strategies.llm.LLMClient.from_strategy", new_callable=AsyncMock) as mock_from_strategy:
        mock_from_strategy.return_value = mock_client
        
        traces = await llm_strategy.execute(
            step=step,
            projector=projector,
            context=context,
            frozen_ctx=None,
            trace=[]
        )
        
    assert len(traces) == 1
    assert traces[0].event_type == "output"
    assert "blocks" in traces[0].content
