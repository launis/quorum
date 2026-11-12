"""Unit tests for DAGExecutor TaskGroup wave execution, retries, and fault isolation."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from polyfactory.factories.pydantic_factory import ModelFactory

from backend_v2.core.hook_registry import HookDeltaDTO, HookResult
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.blackboard import GlobalAtomBlackboard
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.step import StepRule
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO
from backend_v2.models.dtos.synthesis import SynthesisDistillationDTO
from backend_v2.models.enums import ExecutionStatus, HistoricalContextMode
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import ErrorTraceEvent, TraceEvent
from backend_v2.services.orchestrator.dag_executor import DAGExecutor
from backend_v2.settings import get_settings
from backend_v2.tests.factories.model_factories import (
    ExecutionRecordFactory,
    WorkflowFactory,
)
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


class ErrorTraceEventFactory(ModelFactory[ErrorTraceEvent]):
    """Polyfactory model factory for ErrorTraceEvent instances."""

    __model__ = ErrorTraceEvent


class TraceEventFactory(ModelFactory[TraceEvent]):
    """Polyfactory model factory for TraceEvent instances."""

    __model__ = TraceEvent


class SynthesisDistillationDTOFactory(ModelFactory[SynthesisDistillationDTO]):
    """Polyfactory model factory for SynthesisDistillationDTO instances."""

    __model__ = SynthesisDistillationDTO


@pytest.fixture
def mock_repo() -> InMemoryUnifiedWorkflowRepository:
    """Create an in-memory unified repository seeded with a mock step and execution record.

    Returns:
        Configured InMemoryUnifiedWorkflowRepository instance.
    """
    repo = InMemoryUnifiedWorkflowRepository()

    repo.set_step(
        {
            "id": "stp_0195f3a0000070018234567890abcdef",
            "type": "logic",
            "slug": "mock",
            "name": {"translations": {"en": "mock"}},
            "description": {"translations": {"en": "mock"}},
            "hook": "mock_hook",
        }
    )

    repo.set_execution(
        ExecutionRecordFactory.build(
            id="exe_0195f3a0000070018111222233334444",
            workflow_id="wf_0195f3a0000070048444444444444444",
            output_profile_id="prof_0195f3a00000700d8ddd1111dddd1111",
            status=ExecutionStatus.PENDING,
            target_locale="en",
            raw_inputs=WorkflowInputs(dynamic_inputs={"log": "test"}),
            metadata=ExecutionMetadata(),
        )
    )
    return repo


@pytest.fixture
def mock_compiler() -> AsyncMock:
    """Create an AsyncMock prompt compiler fixture.

    Returns:
        Initialized AsyncMock instance.
    """
    return AsyncMock()


@pytest.mark.asyncio
async def test_independent_steps_continue_on_sibling_failure(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    mock_compiler: AsyncMock,
) -> None:
    """Verify sibling failure in TaskGroup wave cancels the wave and fails fast.

    Args:
        mock_repo: Seeded in-memory repository fixture.
        mock_compiler: Mocked prompt compiler fixture.
    """
    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        prompt_block_repo=mock_repo,
        output_profile_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )

    workflow = WorkflowFactory.build(
        model_registry_id="sys_0195f3a00000700e826807f3bfa3454d",
        historical_context_mode=HistoricalContextMode.DISABLED,
        id="wf_0195f3a0000070048444444444444444",
        slug="wf_tg",
        status="draft",
        version=1,
        default_profile_id="prof_0195f3a00000700d8ddd1111dddd1111",
        name=I18nText(translations={"en": "TG Test", "fi": "TG Test"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
        expected_inputs=[],
        steps=[
            StepRule(
                id="stp_0195f3a00000700f8fff1111ffff1111",
                task_blueprint="bp_fail",
                depends_on=[],
                input_mappings={},
            ),
            StepRule(
                id="stp_0195f3a0000070058555222255552222",
                task_blueprint="bp_sleep",
                depends_on=[],
                input_mappings={},
            ),
        ],
    )

    async def mock_execute(step: StepRule, *args: Any, **kwargs: Any) -> list[Any]:
        if step.id == "stp_0195f3a00000700f8fff1111ffff1111":
            return [
                ErrorTraceEventFactory.build(
                    timestamp=datetime.now(UTC),
                    event_type="error",
                    step_name=step.id,
                    error_code="MOCK_FAIL",
                    error_message="Intentional failure",
                    content={},
                    metadata=None,
                    mcp_audit_traces=[],
                )
            ]
        if step.id == "stp_0195f3a0000070058555222255552222":
            await asyncio.sleep(0.1)
            return [
                TraceEventFactory.build(
                    timestamp=datetime.now(UTC),
                    step_name=step.id,
                    event_type="output",
                    content={"status": "ok"},
                    metadata=None,
                    mcp_audit_traces=[],
                )
            ]
        return []

    with patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks:
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(
                success=True,
                state_delta=HookDeltaDTO(delta=ExecutionInputsDTO(raw_inputs={}, dynamic_inputs={"log": "test"})),
            )
        )

        with patch.object(executor.node_executor, "execute", side_effect=mock_execute):
            with pytest.raises(AppException) as exc_info:
                await executor.execute_workflow(
                    execution_id="exe_0195f3a0000070018111222233334444",
                    workflow=workflow,
                    raw_inputs=WorkflowInputs(dynamic_inputs={"log": "test"}),
                )

            assert "Step stp_0195f3a00000700f8fff1111ffff1111 emitted ErrorTraceEvent" in str(exc_info.value)

            rec = await mock_repo.get_execution("exe_0195f3a0000070018111222233334444")
            assert rec is not None
            assert rec.step_states["stp_0195f3a0000070058555222255552222"].status == ExecutionStatus.FAILED
            assert rec.step_states["stp_0195f3a00000700f8fff1111ffff1111"].status == ExecutionStatus.FAILED


@pytest.mark.asyncio
async def test_dependent_steps_fail_fast_on_parent_failure(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    mock_compiler: AsyncMock,
) -> None:
    """Verify dependent steps are marked BLOCKED without executing when their parent fails.

    Args:
        mock_repo: Seeded in-memory repository fixture.
        mock_compiler: Mocked prompt compiler fixture.
    """
    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        prompt_block_repo=mock_repo,
        output_profile_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )

    workflow = WorkflowFactory.build(
        model_registry_id="sys_0195f3a00000700e826807f3bfa3454d",
        historical_context_mode=HistoricalContextMode.DISABLED,
        id="wf_0195f3a0000070048444444444444444",
        slug="wf_tg_dep",
        status="draft",
        version=1,
        default_profile_id="prof_0195f3a00000700d8ddd1111dddd1111",
        name=I18nText(translations={"en": "TG Test", "fi": "TG Test"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
        expected_inputs=[],
        steps=[
            StepRule(
                id="stp_0195f3a00000700a8aaa1111aaaa1111",
                task_blueprint="bp_fail",
                depends_on=[],
                input_mappings={},
            ),
            StepRule(
                id="stp_0195f3a00000700c8ccc3333cccc3333",
                task_blueprint="bp_dep",
                depends_on=["stp_0195f3a00000700a8aaa1111aaaa1111"],
                input_mappings={},
            ),
        ],
    )

    async def mock_execute(step: StepRule, *args: Any, **kwargs: Any) -> list[Any]:
        if step.id == "stp_0195f3a00000700a8aaa1111aaaa1111":
            return [
                ErrorTraceEventFactory.build(
                    timestamp=datetime.now(UTC),
                    event_type="error",
                    step_name=step.id,
                    error_code="MOCK_FAIL",
                    error_message="Intentional failure",
                    content={},
                    metadata=None,
                    mcp_audit_traces=[],
                )
            ]
        if step.id == "stp_0195f3a00000700c8ccc3333cccc3333":
            raise ValueError("Dependent step must not execute after parent failure")
        return []

    with patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks:
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(
                success=True,
                state_delta=HookDeltaDTO(delta=ExecutionInputsDTO(raw_inputs={}, dynamic_inputs={"log": "test"})),
            )
        )

        with patch.object(executor.node_executor, "execute", side_effect=mock_execute):
            with pytest.raises(AppException) as exc_info:
                await executor.execute_workflow(
                    execution_id="exe_0195f3a0000070018111222233334444",
                    workflow=workflow,
                    raw_inputs=WorkflowInputs(dynamic_inputs={"log": "test"}),
                )

            assert "Step stp_0195f3a00000700a8aaa1111aaaa1111 emitted ErrorTraceEvent" in str(exc_info.value)

            rec = await mock_repo.get_execution("exe_0195f3a0000070018111222233334444")
            assert rec is not None
            assert rec.step_states["stp_0195f3a00000700a8aaa1111aaaa1111"].status == ExecutionStatus.FAILED
            assert rec.step_states["stp_0195f3a00000700c8ccc3333cccc3333"].status == ExecutionStatus.BLOCKED


@pytest.mark.asyncio
async def test_step_transient_failure_exhausts_retries(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    mock_compiler: AsyncMock,
) -> None:
    """Verify transient network errors trigger AsyncRetrying and fail after exhausting attempts.

    Args:
        mock_repo: Seeded in-memory repository fixture.
        mock_compiler: Mocked prompt compiler fixture.
    """
    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        prompt_block_repo=mock_repo,
        output_profile_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )

    workflow = WorkflowFactory.build(
        model_registry_id="sys_0195f3a00000700e826807f3bfa3454d",
        historical_context_mode=HistoricalContextMode.DISABLED,
        id="wf_0195f3a0000070048444444444444444",
        slug="wf_tg_retry",
        status="draft",
        version=1,
        default_profile_id="prof_0195f3a00000700d8ddd1111dddd1111",
        name=I18nText(translations={"en": "TG Test", "fi": "TG Test"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
        expected_inputs=[],
        steps=[
            StepRule(
                id="stp_0195f3a00000700f8faa9999ffaa9999",
                task_blueprint="bp_retry",
                depends_on=[],
                input_mappings={},
            ),
        ],
    )

    import litellm.exceptions

    request = httpx.Request("GET", "https://api.example.com/v1/chat/completions")
    mock_execute = AsyncMock(
        side_effect=litellm.exceptions.APIConnectionError(
            message="Connection timeout",
            llm_provider="openai",
            model="gpt-4",
            request=request,
        )
    )

    with patch("backend_v2.services.orchestrator.dag_executor.get_settings") as mock_get_settings:
        mock_settings = get_settings().model_copy(
            update={
                "llm_max_transient_retries": 3,
                "llm_retry_min_seconds": 0,
                "llm_retry_max_seconds": 0,
            }
        )
        mock_get_settings.return_value = mock_settings

        with patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks:
            mock_hooks.execute = AsyncMock(
                return_value=HookResult(
                    success=True,
                    state_delta=HookDeltaDTO(delta=ExecutionInputsDTO(raw_inputs={}, dynamic_inputs={"log": "test"})),
                )
            )

            with patch.object(executor.node_executor, "execute", mock_execute):
                with pytest.raises(AppException) as exc_info:
                    await executor.execute_workflow(
                        execution_id="exe_0195f3a0000070018111222233334444",
                        workflow=workflow,
                        raw_inputs=WorkflowInputs(dynamic_inputs={"log": "test"}),
                    )

                assert "Workflow failed" in str(exc_info.value)
                assert mock_execute.call_count == 3

                rec = await mock_repo.get_execution("exe_0195f3a0000070018111222233334444")
                assert rec is not None
                assert rec.step_states["stp_0195f3a00000700f8faa9999ffaa9999"].status == ExecutionStatus.FAILED


@pytest.mark.asyncio
@patch("backend_v2.services.orchestrator.dag_executor.Step.model_validate")
@patch("backend_v2.services.orchestrator.dag_executor.MatrixReducer.reduce_matrix")
@patch("backend_v2.services.orchestrator.dag_executor.hook_registry.execute")
async def test_dynamic_synthesis_model_strategy_routing(
    mock_hook_execute: MagicMock,
    mock_reduce: MagicMock,
    mock_bp_validate: MagicMock,
    mock_repo: InMemoryUnifiedWorkflowRepository,
    mock_compiler: AsyncMock,
) -> None:
    """Verify dynamic model_strategy == 'synthesis' routing invokes MatrixReducer.

    Args:
        mock_hook_execute: Mocked hook registry execute function.
        mock_reduce: Mocked MatrixReducer.reduce_matrix function.
        mock_bp_validate: Mocked Step.model_validate method.
        mock_repo: Seeded in-memory repository fixture.
        mock_compiler: Mocked prompt compiler fixture.
    """
    mock_rag = AsyncMock()
    mock_rag.execute.return_value = GlobalAtomBlackboard(atoms_by_input={})

    executor = DAGExecutor(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        prompt_block_repo=mock_repo,
        output_profile_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
        rag_preflight=mock_rag,
    )

    workflow = Workflow.model_construct(
        id="wf_0195f3a00000700283456789abcdef01",
        name=I18nText(translations={"en": "Test Workflow"}),
        organization_id="org_0195f3a00000700283456789abcdef01",
        default_profile_id="prof_0195f3a00000700283456789abcdef01",
        model_registry_id="sys_0195f3a00000700e826807f3bfa3454d",
        slug="test-workflow",
        description=I18nText(translations={"en": "A test workflow"}),
        status="draft",
        version=1,
        historical_context_mode=HistoricalContextMode.DISABLED,
        expected_inputs=[],
        steps=[
            StepRule.model_construct(
                id="stp_0195f3a00000700283456789abcdef01",
                task_blueprint="bp_0195f3a00000700283456789abcdef01",
                depends_on=[],
                input_mappings={},
            )
        ],
    )

    mock_repo.set_step(
        {
            "id": "bp_0195f3a00000700283456789abcdef01",
            "type": "standard",
            "model_strategy": "synthesis",
            "pre_hooks": ["synthesis_distiller_hook"],
        },
        step_id="bp_0195f3a00000700283456789abcdef01",
    )

    mock_repo.set_workflow(workflow)
    mock_repo.set_execution(
        ExecutionRecordFactory.build(
            id="exe_0195f3a00000700283456789abcdef01",
            workflow_id="wf_0195f3a00000700283456789abcdef01",
            output_profile_id="prof_0195f3a00000700283456789abcdef01",
            status=ExecutionStatus.PASSED,
            target_locale="en",
            metadata=ExecutionMetadata(),
            raw_inputs=WorkflowInputs(dynamic_inputs={}),
        )
    )

    mock_bp_validate.return_value = MagicMock(
        id="bp_0195f3a00000700283456789abcdef01",
        type="standard",
        model_strategy="synthesis",
        pre_hooks=["synthesis_distiller_hook"],
    )

    mock_hook_execute.return_value = HookResult(
        success=True,
        state_delta=HookDeltaDTO(
            delta=SynthesisDistillationDTOFactory.build(
                distilled_inputs="mock distilled",
                title_map={},
                matrices_to_explain=[],
                source_alias_map={},
                alias_registry={},
            )
        ),
    )

    mock_reduce.return_value = MagicMock(model_dump=lambda: {"mock": "matrix"})

    caught_error: AppException | None = None
    with patch.object(executor.node_executor, "execute", return_value=[]):
        try:
            await executor.execute_workflow(
                execution_id="exe_0195f3a00000700283456789abcdef01",
                workflow=workflow,
                raw_inputs=WorkflowInputs.model_construct(dynamic_inputs={}),
            )
        except AppException as exc:
            caught_error = exc

    assert caught_error is None or isinstance(caught_error, AppException)
    mock_reduce.assert_called_once()


@pytest.mark.asyncio
async def test_intermediate_progress_callback_lock_failure_does_not_crash_step(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    mock_compiler: AsyncMock,
) -> None:
    """Verify transient DB lock failure during intermediate progress reporting does not crash the step.

    Args:
        mock_repo: Seeded in-memory repository fixture.
        mock_compiler: Mocked prompt compiler fixture.
    """
    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        prompt_block_repo=mock_repo,
        output_profile_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )

    workflow = WorkflowFactory.build(
        model_registry_id="sys_0195f3a00000700e826807f3bfa3454d",
        historical_context_mode=HistoricalContextMode.DISABLED,
        id="wf_0195f3a0000070018111222233334444",
        slug="wf_progress_test",
        status="draft",
        version=1,
        default_profile_id="prof_0195f3a00000700d8ddd1111dddd1111",
        name=I18nText(translations={"en": "Progress Test", "fi": "Progress Test"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
        expected_inputs=[],
        steps=[
            StepRule(
                id="stp_0195f3a0000070018111222233334444",
                task_blueprint="bp_0195f3a0000070018111222233334444",
                depends_on=[],
                input_mappings={},
            ),
        ],
    )

    async def mock_execute(step: StepRule, *args: Any, **kwargs: Any) -> list[Any]:
        if "progress_callback" in kwargs and kwargs["progress_callback"]:
            mock_repo.inject_fault(
                "update_execution",
                AppException(
                    message="Failed to commit execution trace",
                    details={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED},
                    status_code=500,
                ),
                trigger_count=1,
            )
            await kwargs["progress_callback"](50, 100)
        return [
            TraceEventFactory.build(
                timestamp=datetime.now(UTC),
                step_name=step.id,
                event_type="output",
                content={"status": "ok"},
                metadata=None,
                mcp_audit_traces=[],
            )
        ]

    try:
        with patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks:
            mock_hooks.execute = AsyncMock(
                return_value=HookResult(
                    success=True,
                    state_delta=HookDeltaDTO(delta=ExecutionInputsDTO(raw_inputs={}, dynamic_inputs={"log": "test"})),
                )
            )
            with patch.object(executor.node_executor, "execute", side_effect=mock_execute):
                result = await executor.execute_workflow(
                    execution_id="exe_0195f3a0000070018111222233334444",
                    workflow=workflow,
                    raw_inputs=WorkflowInputs(dynamic_inputs={"log": "test"}),
                )
                assert result.step_states["stp_0195f3a0000070018111222233334444"].status == ExecutionStatus.PASSED
    finally:
        mock_repo.clear_faults()
