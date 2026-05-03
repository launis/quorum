from unittest.mock import MagicMock

import pytest

from backend_v2.exceptions import AppException
from backend_v2.services.orchestrator.strategies.logic import LogicNodeStrategy


@pytest.mark.asyncio
async def test_logic_strategy_missing_blueprint() -> None:
    repo = MagicMock()
    compiler = MagicMock()
    strategy = LogicNodeStrategy(
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
        prompt_compiler=compiler,
    )  # noqa: E501

    step = MagicMock()
    step.task_blueprint = None
    step.id = "step_123"

    projector = MagicMock()
    projector.snapshot = {}

    context = MagicMock()

from unittest.mock import MagicMock

import pytest

from backend_v2.exceptions import AppException
from backend_v2.services.orchestrator.strategies.logic import LogicNodeStrategy


@pytest.mark.asyncio
async def test_logic_strategy_missing_blueprint() -> None:
    repo = MagicMock()
    compiler = MagicMock()
    strategy = LogicNodeStrategy(
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
        prompt_compiler=compiler,
    )  # noqa: E501

    step = MagicMock()
    step.task_blueprint = None
    step.id = "step_123"

    projector = MagicMock()
    projector.snapshot = {}

    context = MagicMock()

    with pytest.raises(AppException) as excinfo:
        await strategy.execute(step, projector, context, None, [])

    assert "has no task_blueprint configured" in str(excinfo.value.message)


@pytest.mark.asyncio
async def test_logic_strategy_raw_inputs_extraction_bug() -> None:
    from backend_v2.models.state import StepOutputDTO
    from backend_v2.services.orchestrator.strategies.logic import LogicNodeStrategy
    from unittest.mock import AsyncMock

    repo = AsyncMock()
    # Mock get_step_by_id to return a valid step def
    repo.get_step_by_id.return_value = {"id": "st_1234567890123456"}
    
    compiler = MagicMock()
    strategy = LogicNodeStrategy(
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
        prompt_compiler=compiler,
    )

    step = MagicMock()
    step.id = "step_123"
    step.task_blueprint = "blueprint_123"
    step.input_mappings = {}

    projector = MagicMock()
    # Simulate StateProjector flattening the raw_inputs dictionary
    projector.snapshot = [
        StepOutputDTO(step_id="raw_inputs", block_id="chat_log", data_type="text", payload="**Gemini Chat**..."),
        StepOutputDTO(step_id="raw_inputs", block_id="organization_id", data_type="text", payload="org-123"),
        StepOutputDTO(step_id="inputs", block_id="chat_log", data_type="text", payload="**Gemini Chat**..."),
    ]

    context = MagicMock()
    context.execution_id = "exe_1"
    context.workflow_id = "wf_1"
    context.metadata = {}

    # Mock the hook registry so it doesn't actually try to execute "some_hook"
    from backend_v2.core.hook_registry import hook_registry, HookResult
    hook_registry.execute = AsyncMock(return_value=HookResult(success=True, state_delta={}))

    # Mock V2Step.model_validate
    from backend_v2.models.v2_core import Step as V2Step
    v2_step_mock = MagicMock()
    v2_step_mock.hook = "some_hook"
    V2Step.model_validate = MagicMock(return_value=v2_step_mock)

    # We expect `strategy.execute` to correctly extract `raw_inputs` as a DICTIONARY:
    # {"chat_log": "**Gemini Chat**...", "organization_id": "org-123"}
    # Because of the bug, it will just extract the string "**Gemini Chat**...".
    
    await strategy.execute(step, projector, context, None, [])
    
    # Verify what was passed to the hook registry
    hook_state = hook_registry.execute.call_args[0][1]
    
    assert isinstance(hook_state.inputs["raw_inputs"], dict), f"Bug! raw_inputs is {type(hook_state.inputs['raw_inputs'])} instead of dict"
    assert hook_state.inputs["raw_inputs"]["chat_log"] == "**Gemini Chat**..."
