"""Unit tests for LogicNodeStrategy orchestration and ISTQB negative boundaries."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.core.hook_registry import HookDeltaDTO, HookResult
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import generate_uuid7
from backend_v2.models.domain.step import StepRule
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.dtos.global_context import GlobalContextVarsDTO
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO
from backend_v2.models.dtos.node_execution import StepOutputContentValue
from backend_v2.models.dtos.step_output import StepOutputDTO
from backend_v2.models.dtos.trace import TraceEventMetadataDTO, TraceScoringPayloadDTO
from backend_v2.models.enums import StepType, VirtualSystemStepID
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import StateProjector, TraceEvent
from backend_v2.services.orchestrator.strategies import logic
from backend_v2.services.orchestrator.strategies.base import StrategyContext, StrategyDependencies
from backend_v2.services.orchestrator.strategies.logic import LogicNodeStrategy
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository

STEP_RULE_ID = "sr_0195f3a0000070008123456789abcdef"
BLUEPRINT_ID = "stp_0195f3a0000070018234567890abcdef"
EXECUTION_ID = "exe_0195f3a0000070028234567890abcdef"
WORKFLOW_ID = "wf_0195f3a0000070038234567890abcdef"
BLOCK_ID = "blk_0195f3a0000070048234567890abcdef"


def _make_step(blueprint_id: str = BLUEPRINT_ID) -> StepRule:
    """Construct a StepRule instance for unit testing.

    Args:
        blueprint_id: Target task blueprint identifier.

    Returns:
        Constructed StepRule model instance.
    """
    return StepRule.model_construct(
        id=STEP_RULE_ID,
        task_blueprint=blueprint_id,
        depends_on=[],
        input_mappings={},
    )


def _make_context(global_vars: GlobalContextVarsDTO | None = None) -> StrategyContext:
    """Construct a StrategyContext instance for unit testing.

    Args:
        global_vars: Optional GlobalContextVarsDTO override.

    Returns:
        Constructed StrategyContext instance.
    """
    return StrategyContext(
        execution_id=EXECUTION_ID,
        workflow_id=WORKFLOW_ID,
        metadata=ExecutionMetadata(),
        global_context_vars=global_vars if global_vars is not None else GlobalContextVarsDTO(),
        context_variables=ContextVariablesDTO(variables={}),
        prompt_blocks=[],
    )


def _make_input_trace_event(
    step_name: str,
    content: dict[str, StepOutputContentValue],
) -> TraceEvent:
    """Construct an input TraceEvent for projector testing.

    Args:
        step_name: Step name for the trace event.
        content: Event payload content dictionary.

    Returns:
        Constructed TraceEvent instance.
    """
    return TraceEvent(
        event_id=generate_uuid7(),
        timestamp=datetime.now(UTC),
        step_name=step_name,
        event_type="input",
        content=content,
        metadata=TraceEventMetadataDTO(mcp_audit_traces=[]),
        mcp_audit_traces=[],
    )


@pytest.fixture
def in_memory_repo() -> InMemoryUnifiedWorkflowRepository:
    """Provide a hermetic InMemoryUnifiedWorkflowRepository instance.

    Returns:
        Fresh InMemoryUnifiedWorkflowRepository instance.
    """
    return InMemoryUnifiedWorkflowRepository()


@pytest.fixture
def logic_strategy(in_memory_repo: InMemoryUnifiedWorkflowRepository) -> LogicNodeStrategy:
    """Provide a LogicNodeStrategy bound to the hermetic in-memory repository.

    Args:
        in_memory_repo: Hermetic in-memory unified workflow repository.

    Returns:
        Configured LogicNodeStrategy instance.
    """
    deps = StrategyDependencies(
        exec_repo=in_memory_repo,
        workflow_repo=in_memory_repo,
        prompt_block_repo=in_memory_repo,
        output_profile_repo=in_memory_repo,
        identity_repo=in_memory_repo,
        audit_repo=in_memory_repo,
        system_repo=in_memory_repo,
        prompt_compiler=AsyncMock(),
    )
    return LogicNodeStrategy(deps=deps)


@pytest.mark.asyncio
async def test_execute_no_blueprint(logic_strategy: LogicNodeStrategy) -> None:
    """Verify LogicNodeStrategy raises CONFIGURATION_ERROR when task_blueprint is empty."""
    step = _make_step(blueprint_id="")
    projector = StateProjector()
    context = _make_context()

    with pytest.raises(AppException) as exc:
        await logic_strategy.execute(step, projector, context)

    assert "has no task_blueprint" in str(exc.value)
    assert exc.value.status_code == 500
    assert exc.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value


@pytest.mark.asyncio
async def test_execute_blueprint_not_found(logic_strategy: LogicNodeStrategy) -> None:
    """Verify LogicNodeStrategy raises CONFIGURATION_ERROR when step blueprint is missing in repository."""
    step = _make_step(blueprint_id=BLUEPRINT_ID)
    projector = StateProjector()
    context = _make_context()

    with pytest.raises(AppException) as exc:
        await logic_strategy.execute(step, projector, context)

    assert "not found" in str(exc.value)
    assert exc.value.status_code == 500
    assert exc.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value


@pytest.mark.asyncio
async def test_execute_passes_global_context_vars(
    logic_strategy: LogicNodeStrategy,
    in_memory_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify LogicNodeStrategy propagates global_context_vars into HookState."""
    step = _make_step()
    projector = StateProjector()
    context = _make_context(global_vars=GlobalContextVarsDTO(language="fi"))

    step_def = {
        "id": BLUEPRINT_ID,
        "slug": "test_slug",
        "name": {"translations": {"en": "Test"}},
        "hook": "test_hook",
        "description": {"translations": {"en": "Test Desc"}},
        "type": StepType.LOGIC,
    }
    in_memory_repo.seed_raw_step(step.task_blueprint, step_def)

    with patch("backend_v2.services.orchestrator.strategies.logic.hook_registry.execute") as mock_execute:
        mock_execute.return_value = HookResult(success=True, state_delta=HookDeltaDTO(delta=None))

        await logic_strategy.execute(step, projector, context)

        mock_execute.assert_called_once()
        hook_name, hook_state, _ = mock_execute.call_args.args
        assert hook_name == "test_hook"
        assert hook_state.global_context_vars.language == "fi"


@pytest.mark.asyncio
async def test_logic_strategy_execute_without_concurrency(
    logic_strategy: LogicNodeStrategy,
    in_memory_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify LogicNodeStrategy executes without concurrency semaphores and serializes state deltas."""
    step = _make_step()
    projector = StateProjector()
    context = _make_context()

    step_def = {
        "id": BLUEPRINT_ID,
        "slug": "test_slug",
        "name": {"translations": {"en": "Test"}},
        "hook": "test_hook",
        "description": {"translations": {"en": "Test Desc"}},
        "type": StepType.LOGIC,
    }
    in_memory_repo.seed_raw_step(step.task_blueprint, step_def)

    delta_dto = ExecutionInputsDTO(dynamic_inputs={"test_key": "test_val"}, raw_inputs={})

    with patch("backend_v2.services.orchestrator.strategies.logic.hook_registry.execute") as mock_execute:
        mock_execute.return_value = HookResult(
            success=True,
            state_delta=HookDeltaDTO(delta=delta_dto),
        )

        traces = await logic_strategy.execute(step, projector, context)

        assert len(traces) == 1
        assert traces[0].event_type == "output"
        assert traces[0].content == {
            **delta_dto.model_dump(mode="json", exclude_none=True),
            "_step_metadata": {"task_blueprint": BLUEPRINT_ID},
        }


@pytest.mark.asyncio
async def test_execute_merges_state_delta(
    logic_strategy: LogicNodeStrategy,
    in_memory_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify LogicNodeStrategy merges HookDeltaDTO outputs into emitted TraceEvents."""
    await test_logic_strategy_execute_without_concurrency(logic_strategy, in_memory_repo)


@pytest.mark.asyncio
async def test_execute_hook_failure_raises_app_exception(
    logic_strategy: LogicNodeStrategy,
    in_memory_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify LogicNodeStrategy raises AGENT_EXECUTION_CRITICAL when primary hook returns success=False."""
    step = _make_step()
    projector = StateProjector()
    context = _make_context()

    step_def = {
        "id": BLUEPRINT_ID,
        "slug": "test_slug",
        "name": {"translations": {"en": "Test"}},
        "hook": "test_hook",
        "description": {"translations": {"en": "Test Desc"}},
        "type": StepType.LOGIC,
    }
    in_memory_repo.seed_raw_step(step.task_blueprint, step_def)

    with patch("backend_v2.services.orchestrator.strategies.logic.hook_registry.execute") as mock_execute:
        mock_execute.return_value = HookResult(success=False, state_delta=None)

        with pytest.raises(AppException) as exc_info:
            await logic_strategy.execute(step, projector, context)

        assert exc_info.value.status_code == 500
        assert exc_info.value.details["error_code"] == ErrorCodes.AGENT_EXECUTION_CRITICAL.value
        assert "returned success=False" in exc_info.value.message


@pytest.mark.asyncio
async def test_execute_missing_hook_raises_app_exception(
    logic_strategy: LogicNodeStrategy,
    in_memory_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify LogicNodeStrategy raises VALIDATION_FAILED when step definition has no native hook."""
    step = _make_step()
    projector = StateProjector()
    context = _make_context()

    step_def = {
        "id": BLUEPRINT_ID,
        "slug": "test_slug",
        "name": {"translations": {"en": "Test"}},
        "hook": None,
        "criteria_block_ids": [BLOCK_ID],
        "extraction_protocol_block_id": BLOCK_ID,
        "description": {"translations": {"en": "Test Desc"}},
        "type": StepType.LLM,
    }
    in_memory_repo.seed_raw_step(step.task_blueprint, step_def)

    with pytest.raises(AppException) as exc_info:
        await logic_strategy.execute(step, projector, context)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "has no native hook defined" in exc_info.value.message


@pytest.mark.asyncio
async def test_execute_with_base_model_delta(
    logic_strategy: LogicNodeStrategy,
    in_memory_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify LogicNodeStrategy serializes BaseModel hook deltas with exclude_none=True."""
    step = _make_step()
    projector = StateProjector()
    context = _make_context()

    step_def = {
        "id": BLUEPRINT_ID,
        "slug": "test_slug",
        "name": {"translations": {"en": "Test"}},
        "hook": "test_hook",
        "description": {"translations": {"en": "Test Desc"}},
        "type": StepType.LOGIC,
    }
    in_memory_repo.seed_raw_step(step.task_blueprint, step_def)

    delta_instance = StepOutputDTO(step_id=BLUEPRINT_ID, block_id=BLOCK_ID, data_type="text", payload="hello")

    with patch("backend_v2.services.orchestrator.strategies.logic.hook_registry.execute") as mock_execute:
        mock_execute.return_value = HookResult(success=True, state_delta=HookDeltaDTO(delta=delta_instance))

        traces = await logic_strategy.execute(step, projector, context)

        assert len(traces) == 1
        assert traces[0].event_type == "output"
        assert traces[0].content == {
            **delta_instance.model_dump(mode="json", exclude_none=True),
            "_step_metadata": {"task_blueprint": BLUEPRINT_ID},
        }


@pytest.mark.asyncio
async def test_execute_with_trace_scoring_payload_dto(
    logic_strategy: LogicNodeStrategy,
    in_memory_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify LogicNodeStrategy populates SCORING_RESULT and top-level keys from TraceScoringPayloadDTO."""
    step = _make_step()
    projector = StateProjector()
    context = _make_context()

    step_def = {
        "id": BLUEPRINT_ID,
        "slug": "scoring_slug",
        "name": {"translations": {"en": "Scoring"}},
        "hook": "apply_scoring_logic",
        "description": {"translations": {"en": "Scoring Desc"}},
        "type": StepType.LOGIC,
    }
    in_memory_repo.seed_raw_step(step.task_blueprint, step_def)

    delta_instance = TraceScoringPayloadDTO(
        total_score=9.8,
        final_score=9.8,
        penalties_applied=[],
        aggregation_status="Commensurate Average",
    )

    with patch("backend_v2.services.orchestrator.strategies.logic.hook_registry.execute") as mock_execute:
        mock_execute.return_value = HookResult(success=True, state_delta=HookDeltaDTO(delta=delta_instance))

        traces = await logic_strategy.execute(step, projector, context)

        assert len(traces) == 1
        assert traces[0].event_type == "output"
        expected_scoring = delta_instance.model_dump(mode="json", exclude_none=True)
        assert "normalized_score" not in expected_scoring
        assert traces[0].content == {
            VirtualSystemStepID.SCORING_RESULT.value: expected_scoring,
            **expected_scoring,
            "_step_metadata": {"task_blueprint": BLUEPRINT_ID},
        }
        scoring_payload = TraceScoringPayloadDTO.model_validate(expected_scoring)
        assert scoring_payload.total_score == 9.8


def test_logic_exports() -> None:
    """Verify __all__ exports LogicNodeStrategy."""
    assert "__all__" in dir(logic)
    assert "LogicNodeStrategy" in logic.__all__


@pytest.mark.asyncio
async def test_execute_succeeds_with_projector_raw_inputs_event(
    logic_strategy: LogicNodeStrategy,
    in_memory_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify LogicNodeStrategy extracts inputs when StateProjector contains both raw_inputs and inputs events."""
    step = _make_step()
    projector = StateProjector()
    projector.apply_delta(
        _make_input_trace_event(
            step_name="raw_inputs",
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
        _make_input_trace_event(
            step_name="inputs",
            content={
                "chat_log": "# Chat history",
                "product_text": "Product text",
            },
        )
    )
    context = _make_context()

    step_def = {
        "id": BLUEPRINT_ID,
        "slug": "scoring_engine",
        "name": {"translations": {"en": "Scoring Engine"}},
        "hook": "apply_scoring_logic",
        "description": {"translations": {"en": "Scoring"}},
        "type": StepType.LOGIC,
    }
    in_memory_repo.seed_raw_step(step.task_blueprint, step_def)

    with patch("backend_v2.services.orchestrator.strategies.logic.hook_registry.execute") as mock_execute:
        mock_execute.return_value = HookResult(success=True, state_delta=HookDeltaDTO(delta=None))

        traces = await logic_strategy.execute(step, projector, context)

        assert len(traces) == 1
        assert traces[0].event_type == "output"
        mock_execute.assert_called_once()
        hook_name, hook_state, _ = mock_execute.call_args.args
        assert hook_name == "apply_scoring_logic"
        assert isinstance(hook_state.inputs, ExecutionInputsDTO)
        assert "steps" in hook_state.inputs.dynamic_inputs


@pytest.mark.asyncio
async def test_execute_extracts_raw_inputs_when_inputs_event_absent(
    logic_strategy: LogicNodeStrategy,
    in_memory_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify LogicNodeStrategy extracts dynamic_inputs and non-reserved blocks from raw_inputs when inputs is absent."""
    step = _make_step()
    projector = StateProjector()
    projector.apply_delta(
        _make_input_trace_event(
            step_name="raw_inputs",
            content={
                "simulation_mode": False,
                "language": "en",
                "custom_doc": "Direct custom document",
                "dynamic_inputs": {
                    "chat_log": "# Chat history",
                    "product_text": "Product text",
                },
            },
        )
    )
    context = _make_context()

    step_def = {
        "id": BLUEPRINT_ID,
        "slug": "scoring_engine",
        "name": {"translations": {"en": "Scoring Engine"}},
        "hook": "apply_scoring_logic",
        "description": {"translations": {"en": "Scoring"}},
        "type": StepType.LOGIC,
    }
    in_memory_repo.seed_raw_step(step.task_blueprint, step_def)

    with patch("backend_v2.services.orchestrator.strategies.logic.hook_registry.execute") as mock_execute:
        mock_execute.return_value = HookResult(success=True, state_delta=HookDeltaDTO(delta=None))

        await logic_strategy.execute(step, projector, context)

        _, hook_state, _ = mock_execute.call_args.args
        assert hook_state.inputs.raw_inputs["chat_log"] == "# Chat history"
        assert hook_state.inputs.raw_inputs["custom_doc"] == "Direct custom document"
        assert "simulation_mode" not in hook_state.inputs.raw_inputs


@pytest.mark.asyncio
async def test_logic_strategy_rejects_semaphore_argument(logic_strategy: LogicNodeStrategy) -> None:
    """Verify LogicNodeStrategy.execute rejects deprecated semaphore keyword argument."""
    step = _make_step()
    projector = StateProjector()
    context = _make_context()

    with pytest.raises(TypeError, match="unexpected keyword argument 'semaphore'"):
        await logic_strategy.execute(step, projector, context, **{"semaphore": MagicMock()})


@pytest.mark.asyncio
async def test_logic_strategy_rejects_running_event_argument(logic_strategy: LogicNodeStrategy) -> None:
    """Verify LogicNodeStrategy.execute rejects deprecated running_event keyword argument."""
    step = _make_step()
    projector = StateProjector()
    context = _make_context()

    with pytest.raises(TypeError, match="unexpected keyword argument 'running_event'"):
        await logic_strategy.execute(step, projector, context, **{"running_event": MagicMock()})


@pytest.mark.asyncio
async def test_strategy_rejects_semaphore_argument(logic_strategy: LogicNodeStrategy) -> None:
    """Verify NodeStrategy interface rejects semaphore argument on LogicNodeStrategy."""
    await test_logic_strategy_rejects_semaphore_argument(logic_strategy)


@pytest.mark.asyncio
async def test_strategy_rejects_running_event_argument(logic_strategy: LogicNodeStrategy) -> None:
    """Verify NodeStrategy interface rejects running_event argument on LogicNodeStrategy."""
    await test_logic_strategy_rejects_running_event_argument(logic_strategy)
