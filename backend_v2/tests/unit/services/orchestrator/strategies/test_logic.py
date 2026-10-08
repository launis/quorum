from typing import cast
from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.domain.step import StepRule
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import StateProjector
from backend_v2.services.orchestrator.strategies.base import StrategyContext, StrategyDependencies
from backend_v2.services.orchestrator.strategies.logic import LogicNodeStrategy
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


@pytest.fixture
def logic_strategy() -> LogicNodeStrategy:
    repo = InMemoryUnifiedWorkflowRepository()
    deps = StrategyDependencies(
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
        prompt_compiler=AsyncMock(),
    )
    return LogicNodeStrategy(deps=deps)


@pytest.mark.asyncio
async def test_execute_no_blueprint(logic_strategy: LogicNodeStrategy) -> None:
    # Explicitly using an empty string as task_blueprint to simulate missing configuration
    # while passing strict string type requirements in Pydantic models.
    step = StepRule.model_construct(id="step_1", task_blueprint="")
    projector = StateProjector()
    context = StrategyContext.model_construct(execution_id="e1", workflow_id="w1", metadata=ExecutionMetadata())

    with pytest.raises(AppException) as exc:
        await logic_strategy.execute(step, projector, context)

    assert "has no task_blueprint" in str(exc.value)
    assert exc.value.status_code == 500


@pytest.mark.asyncio
async def test_execute_blueprint_not_found(logic_strategy: LogicNodeStrategy) -> None:
    step = StepRule.model_construct(id="step_1", task_blueprint="bp_missing_123")
    projector = StateProjector()
    context = StrategyContext.model_construct(execution_id="e1", workflow_id="w1", metadata=ExecutionMetadata())

    with pytest.raises(AppException) as exc:
        await logic_strategy.execute(step, projector, context)

    assert "not found" in str(exc.value)
    assert exc.value.status_code == 500


@pytest.mark.asyncio
async def test_execute_passes_global_context_vars(logic_strategy: LogicNodeStrategy) -> None:
    from backend_v2.core.hook_registry import HookDeltaDTO

    step = StepRule.model_construct(id="step_1", task_blueprint="bp_123")
    projector = StateProjector()
    context = StrategyContext(
        execution_id="e1",
        workflow_id="w1",
        metadata=ExecutionMetadata(),
        global_context_vars={"language": "fi"},
    )

    from backend_v2.models.enums import StepType

    step_def = {
        "id": "stp_1234567890abcdef",
        "slug": "test_slug",
        "name": {"translations": {"en": "Test"}},
        "hook": "test_hook",
        "description": {"translations": {"en": "Test Desc"}},
        "type": StepType.LOGIC,
    }
    cast(InMemoryUnifiedWorkflowRepository, logic_strategy.workflow_repo).seed_raw_step(step.task_blueprint, step_def)

    from unittest.mock import patch

    from backend_v2.core.hook_registry import HookResult

    with patch("backend_v2.services.orchestrator.strategies.logic.hook_registry.execute") as mock_execute:
        mock_execute.return_value = HookResult(success=True, state_delta=HookDeltaDTO(delta={}))

        await logic_strategy.execute(step, projector, context)

        # Assert the hook was called with the global_context_vars
        mock_execute.assert_called_once()
        hook_name, hook_state, hook_deps = mock_execute.call_args.args
        assert hook_name == "test_hook"
        assert hook_state.global_context_vars.language == "fi"


@pytest.mark.asyncio
async def test_logic_strategy_execute_without_concurrency(logic_strategy: LogicNodeStrategy) -> None:
    from backend_v2.core.hook_registry import HookDeltaDTO

    step = StepRule.model_construct(id="step_1", task_blueprint="bp_123")
    projector = StateProjector()
    context = StrategyContext(
        execution_id="e1",
        workflow_id="w1",
        metadata=ExecutionMetadata(),
    )

    from backend_v2.models.enums import StepType

    step_def = {
        "id": "stp_1234567890abcdef",
        "slug": "test_slug",
        "name": {"translations": {"en": "Test"}},
        "hook": "test_hook",
        "description": {"translations": {"en": "Test Desc"}},
        "type": StepType.LOGIC,
    }
    cast(InMemoryUnifiedWorkflowRepository, logic_strategy.workflow_repo).seed_raw_step(step.task_blueprint, step_def)

    from unittest.mock import patch

    from backend_v2.core.hook_registry import HookResult

    with patch("backend_v2.services.orchestrator.strategies.logic.hook_registry.execute") as mock_execute:
        mock_execute.return_value = HookResult(
            success=True,
            state_delta=HookDeltaDTO(delta=ExecutionInputsDTO(dynamic_inputs={"test_key": "test_val"})),
        )

        traces = await logic_strategy.execute(step, projector, context)

        assert len(traces) == 1
        assert traces[0].event_type == "output"
        assert traces[0].content["dynamic_inputs"]["test_key"] == "test_val"


@pytest.mark.asyncio
async def test_execute_merges_state_delta(logic_strategy: LogicNodeStrategy) -> None:
    await test_logic_strategy_execute_without_concurrency(logic_strategy)


@pytest.mark.asyncio
async def test_execute_hook_failure_raises_app_exception(logic_strategy: LogicNodeStrategy) -> None:
    step = StepRule.model_construct(id="step_1", task_blueprint="bp_123")
    projector = StateProjector()
    context = StrategyContext(
        execution_id="e1",
        workflow_id="w1",
        metadata=ExecutionMetadata(),
    )

    from backend_v2.models.enums import StepType

    step_def = {
        "id": "stp_1234567890abcdef",
        "slug": "test_slug",
        "name": {"translations": {"en": "Test"}},
        "hook": "test_hook",
        "description": {"translations": {"en": "Test Desc"}},
        "type": StepType.LOGIC,
    }
    cast(InMemoryUnifiedWorkflowRepository, logic_strategy.workflow_repo).seed_raw_step(step.task_blueprint, step_def)

    from unittest.mock import patch

    from backend_v2.core.hook_registry import HookResult

    with patch("backend_v2.services.orchestrator.strategies.logic.hook_registry.execute") as mock_execute:
        mock_execute.return_value = HookResult(success=False, state_delta=None)

        with pytest.raises(AppException) as exc_info:
            await logic_strategy.execute(step, projector, context)

        assert exc_info.value.status_code == 500
        assert "returned success=False" in exc_info.value.message


@pytest.mark.asyncio
async def test_execute_missing_hook_raises_app_exception(logic_strategy: LogicNodeStrategy) -> None:
    step = StepRule.model_construct(id="step_1", task_blueprint="bp_123")
    projector = StateProjector()
    context = StrategyContext(
        execution_id="e1",
        workflow_id="w1",
        metadata=ExecutionMetadata(),
    )

    from backend_v2.models.enums import StepType

    step_def = {
        "id": "stp_1234567890abcdef",
        "slug": "test_slug",
        "name": {"translations": {"en": "Test"}},
        "hook": None,
        "criteria_block_ids": ["blk_0123456789abcdef"],
        "extraction_protocol_block_id": "blk_0123456789abcdef",
        "description": {"translations": {"en": "Test Desc"}},
        "type": StepType.LLM,
    }
    cast(InMemoryUnifiedWorkflowRepository, logic_strategy.workflow_repo).seed_raw_step(step.task_blueprint, step_def)

    with pytest.raises(AppException) as exc_info:
        await logic_strategy.execute(step, projector, context)

    assert exc_info.value.status_code == 500
    assert "has no native hook defined" in exc_info.value.message


@pytest.mark.asyncio
async def test_execute_with_base_model_delta(logic_strategy: LogicNodeStrategy) -> None:
    from backend_v2.core.hook_registry import HookDeltaDTO, HookResult
    from backend_v2.models.dtos.step_output import StepOutputDTO
    from backend_v2.models.enums import StepType

    step = StepRule.model_construct(id="step_1", task_blueprint="bp_123")
    projector = StateProjector()
    context = StrategyContext(
        execution_id="e1",
        workflow_id="w1",
        metadata=ExecutionMetadata(),
    )

    step_def = {
        "id": "stp_1234567890abcdef",
        "slug": "test_slug",
        "name": {"translations": {"en": "Test"}},
        "hook": "test_hook",
        "description": {"translations": {"en": "Test Desc"}},
        "type": StepType.LOGIC,
    }
    cast(InMemoryUnifiedWorkflowRepository, logic_strategy.workflow_repo).seed_raw_step(step.task_blueprint, step_def)

    delta_instance = StepOutputDTO(step_id="stp_1", block_id="blk_1", data_type="text", payload="hello")

    with patch("backend_v2.services.orchestrator.strategies.logic.hook_registry.execute") as mock_execute:
        mock_execute.return_value = HookResult(success=True, state_delta=HookDeltaDTO(delta=delta_instance))

        traces = await logic_strategy.execute(step, projector, context)

        assert len(traces) == 1
        assert traces[0].event_type == "output"
        assert traces[0].content["step_id"] == "stp_1"
        assert traces[0].content["payload"] == "hello"


def test_logic_exports() -> None:
    from backend_v2.services.orchestrator.strategies import logic

    assert "__all__" in dir(logic)
    assert "LogicNodeStrategy" in logic.__all__


@pytest.mark.asyncio
async def test_execute_succeeds_with_projector_raw_inputs_event(logic_strategy: LogicNodeStrategy) -> None:
    """Regression test: LogicNodeStrategy must not crash with ExecutionInputsDTO ValidationError.

    when StateProjector contains raw_inputs and inputs TraceEvents from DAGExecutor.
    """
    from backend_v2.core.hook_registry import HookDeltaDTO, HookResult
    from backend_v2.models.enums import StepType
    from backend_v2.models.state import TraceEvent

    step = StepRule.model_construct(id="step_scoring", task_blueprint="bp_scoring")
    projector = StateProjector()
    projector.apply_delta(
        TraceEvent(
            step_name="raw_inputs",
            event_type="input",
            content={
                "simulation_mode": False,
                "language": "en",
                "dynamic_inputs": {
                    "chat_log": "# Chat history",
                    "product_text": "Product text",
                    "document_date": "2026-07-22T08:57:19Z",
                },
            },
        )
    )
    projector.apply_delta(
        TraceEvent(
            step_name="inputs",
            event_type="input",
            content={
                "chat_log": "# Chat history",
                "product_text": "Product text",
            },
        )
    )
    context = StrategyContext(
        execution_id="e1",
        workflow_id="w1",
        metadata=ExecutionMetadata(),
    )

    step_def = {
        "id": "stp_0123456789abcdef",
        "slug": "scoring_engine",
        "name": {"translations": {"en": "Scoring Engine"}},
        "hook": "apply_scoring_logic",
        "description": {"translations": {"en": "Scoring"}},
        "type": StepType.LOGIC,
    }
    cast(InMemoryUnifiedWorkflowRepository, logic_strategy.workflow_repo).seed_raw_step(step.task_blueprint, step_def)

    with patch("backend_v2.services.orchestrator.strategies.logic.hook_registry.execute") as mock_execute:
        mock_execute.return_value = HookResult(success=True, state_delta=HookDeltaDTO(delta=None))

        traces = await logic_strategy.execute(step, projector, context)

        assert len(traces) == 1
        assert traces[0].event_type == "output"
        mock_execute.assert_called_once()
        hook_name, hook_state, hook_deps = mock_execute.call_args.args
        assert hook_name == "apply_scoring_logic"
        assert isinstance(hook_state.inputs, ExecutionInputsDTO)
        assert "steps" in hook_state.inputs.dynamic_inputs


@pytest.mark.asyncio
async def test_logic_strategy_rejects_semaphore_argument(logic_strategy: LogicNodeStrategy) -> None:
    from unittest.mock import MagicMock

    step = StepRule.model_construct(id="step_1", task_blueprint="bp_123")
    projector = StateProjector()
    context = StrategyContext.model_construct(execution_id="e1", workflow_id="w1", metadata=ExecutionMetadata())

    with pytest.raises(TypeError, match="unexpected keyword argument 'semaphore'"):
        await logic_strategy.execute(step, projector, context, **{"semaphore": MagicMock()})


@pytest.mark.asyncio
async def test_logic_strategy_rejects_running_event_argument(logic_strategy: LogicNodeStrategy) -> None:
    from unittest.mock import MagicMock

    step = StepRule.model_construct(id="step_1", task_blueprint="bp_123")
    projector = StateProjector()
    context = StrategyContext.model_construct(execution_id="e1", workflow_id="w1", metadata=ExecutionMetadata())

    with pytest.raises(TypeError, match="unexpected keyword argument 'running_event'"):
        await logic_strategy.execute(step, projector, context, **{"running_event": MagicMock()})


@pytest.mark.asyncio
async def test_strategy_rejects_semaphore_argument(logic_strategy: LogicNodeStrategy) -> None:
    await test_logic_strategy_rejects_semaphore_argument(logic_strategy)


@pytest.mark.asyncio
async def test_strategy_rejects_running_event_argument(logic_strategy: LogicNodeStrategy) -> None:
    await test_logic_strategy_rejects_running_event_argument(logic_strategy)
