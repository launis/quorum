import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.core.hook_registry import HookResult
from backend_v2.exceptions import AppException
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.enums import ExecutionStatus, HistoricalContextMode
from backend_v2.models.state import ErrorTraceEvent, TraceEvent
from backend_v2.models.v2_core import I18nText, StepRule, Workflow
from backend_v2.services.orchestrator.dag_executor import DAGExecutor


@pytest.fixture
def mock_repo() -> AsyncMock:
    repo = AsyncMock()

    repo.get_step_by_id.return_value = {
        "id": "stp_1234567890abcdef",
        "type": "logic",
        "model_strategy": "logic",
        "slug": "mock",
        "name": {"translations": {"en": "mock"}},
        "description": {"translations": {"en": "mock"}},
        "hook": "mock_hook",
    }

    # Mock context rehydration
    repo.get_execution.return_value = {
        "id": "exe_1111222233334444",
        "workflow_id": "wf_tg_test",
        "output_profile_id": "prof_dddd1111dddd1111",
        "status": ExecutionStatus.PENDING,
        "target_locale": "en",
        "raw_inputs": {"dynamic_inputs": {"log": "test"}},
        "metadata": {},
    }
    return repo


@pytest.fixture
def mock_compiler() -> AsyncMock:
    return AsyncMock()


@pytest.mark.asyncio
async def test_independent_steps_continue_on_sibling_failure(mock_repo: AsyncMock, mock_compiler: AsyncMock) -> None:
    """Test that independent steps continue executing even if a sibling step fails."""
    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )  # noqa: E501

    workflow = Workflow(
        allowed_exports=["pdf"],
        historical_context_mode=HistoricalContextMode.DISABLED,
        id="wf_4444444444444444",
        slug="wf_tg",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        name=I18nText(translations={"en": "TG Test", "fi": "TG Test"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
        steps=[
            # Two independent steps running in parallel without depends_on
            StepRule(id="step_ffff1111ffff1111", task_blueprint="bp_fail"),
            StepRule(id="step_5555222255552222", task_blueprint="bp_sleep"),
        ],
    )

    async def mock_execute(step: StepRule, *args: Any, **kwargs: Any) -> list[Any]:
        if step.id == "step_ffff1111ffff1111":
            # Simulate a quick failure that raises AppException via ErrorTraceEvent
            return [
                ErrorTraceEvent(
                    step_name=step.id, error_code="MOCK_FAIL", error_message="Intentional failure", content={}
                )
            ]
        elif step.id == "step_5555222255552222":
            await asyncio.sleep(0.1)
            return [TraceEvent(step_name=step.id, event_type="output", content={"status": "ok"})]
        return []

    # Bypass the hook registry safely
    with patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks:
        from backend_v2.core.hook_registry import HookDeltaDTO

        mock_hooks.execute = AsyncMock(
            return_value=HookResult(success=True, state_delta=HookDeltaDTO(delta={"log": "test"}))
        )

        # Patch the actual task execution
        with patch.object(executor.node_executor, "execute", side_effect=mock_execute):
            with pytest.raises(AppException) as exc_info:
                await executor.execute_workflow(
                    execution_id="exe_1111222233334444",
                    workflow=workflow,
                    raw_inputs=WorkflowInputs.model_validate({"dynamic_inputs": {"log": "test"}}),
                )

            assert "Workflow completed with failed steps" in str(exc_info.value), "Should fail fast at workflow level"

            calls = mock_repo.update_execution.call_args_list
            final_call_args = calls[-1][0]
            payload = final_call_args[1]
            assert payload.step_states["step_5555222255552222"].status in (
                ExecutionStatus.PASSED,
                ExecutionStatus.PASSED.value,
            )
            assert payload.step_states["step_ffff1111ffff1111"].status in (
                ExecutionStatus.FAILED,
                ExecutionStatus.FAILED.value,
            )


@pytest.mark.asyncio
async def test_dependent_steps_fail_fast_on_parent_failure(mock_repo: AsyncMock, mock_compiler: AsyncMock) -> None:
    """Test that dependent steps fail gracefully without executing if their parent fails."""
    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )  # noqa: E501

    workflow = Workflow(
        allowed_exports=["pdf"],
        historical_context_mode=HistoricalContextMode.DISABLED,
        id="wf_4444444444444444",
        slug="wf_tg_dep",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        name=I18nText(translations={"en": "TG Test", "fi": "TG Test"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
        steps=[
            StepRule(id="step_aaaa1111aaaa1111", task_blueprint="bp_fail"),
            StepRule(id="step_cccc3333cccc3333", task_blueprint="bp_dep", depends_on=["step_aaaa1111aaaa1111"]),
        ],
    )

    async def mock_execute(step: StepRule, *args: Any, **kwargs: Any) -> list[Any]:
        if step.id == "step_aaaa1111aaaa1111":
            return [
                ErrorTraceEvent(
                    step_name=step.id, error_code="MOCK_FAIL", error_message="Intentional failure", content={}
                )
            ]
        elif step.id == "step_cccc3333cccc3333":
            raise ValueError("Step C should not have executed")
        return []

    # Bypass the hook registry safely
    with patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks:
        from backend_v2.core.hook_registry import HookDeltaDTO

        mock_hooks.execute = AsyncMock(
            return_value=HookResult(success=True, state_delta=HookDeltaDTO(delta={"log": "test"}))
        )

        # Patch the actual task execution
        with patch.object(executor.node_executor, "execute", side_effect=mock_execute):
            with pytest.raises(AppException) as exc_info:
                await executor.execute_workflow(
                    execution_id="exe_1111222233334444",
                    workflow=workflow,
                    raw_inputs=WorkflowInputs.model_validate({"dynamic_inputs": {"log": "test"}}),
                )

            assert "Workflow completed with failed steps" in str(exc_info.value), "Should fail fast at workflow level"

            calls = mock_repo.update_execution.call_args_list
            final_call_args = calls[-1][0]
            payload = final_call_args[1]
            assert payload.step_states["step_aaaa1111aaaa1111"].status in (
                ExecutionStatus.FAILED,
                ExecutionStatus.FAILED.value,
            )
            assert payload.step_states["step_cccc3333cccc3333"].status in (
                ExecutionStatus.FAILED,
                ExecutionStatus.FAILED.value,
            )


@pytest.mark.asyncio
async def test_step_transient_failure_exhausts_retries(mock_repo: AsyncMock, mock_compiler: AsyncMock) -> None:
    """Test that transient network errors trigger the AsyncRetrying loop and eventually fail."""
    import httpx
    import litellm.exceptions

    from backend_v2.settings import get_settings

    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )

    workflow = Workflow(
        allowed_exports=["pdf"],
        historical_context_mode=HistoricalContextMode.DISABLED,
        id="wf_4444444444444444",
        slug="wf_tg_retry",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        name=I18nText(translations={"en": "TG Test", "fi": "TG Test"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
        steps=[
            StepRule(id="step_ffaa9999ffaa9999", task_blueprint="bp_retry"),
        ],
    )

    request = httpx.Request("GET", "http://test")
    mock_execute = AsyncMock(
        side_effect=litellm.exceptions.APIConnectionError(
            message="Connection timeout", llm_provider="openai", model="gpt-4", request=request
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
            from backend_v2.core.hook_registry import HookDeltaDTO

            mock_hooks.execute = AsyncMock(
                return_value=HookResult(success=True, state_delta=HookDeltaDTO(delta={"log": "test"}))
            )

            with patch.object(executor.node_executor, "execute", mock_execute):
                with pytest.raises(AppException) as exc_info:
                    await executor.execute_workflow(
                        execution_id="exe_1111222233334444",
                        workflow=workflow,
                        raw_inputs=WorkflowInputs.model_validate({"dynamic_inputs": {"log": "test"}}),
                    )

                assert "Workflow completed with failed steps" in str(exc_info.value)

                # stop_after_attempt(3) means 3 total attempts
                assert mock_execute.call_count == 3

                calls = mock_repo.update_execution.call_args_list
                final_call_args = calls[-1][0]
                payload = final_call_args[1]
                assert payload.step_states["step_ffaa9999ffaa9999"].status in (
                    ExecutionStatus.FAILED,
                    ExecutionStatus.FAILED.value,
                )


@pytest.mark.asyncio
@patch("backend_v2.services.orchestrator.dag_executor.Step.model_validate")
@patch("backend_v2.services.orchestrator.dag_executor.MatrixReducer.reduce_matrix")
@patch("backend_v2.services.orchestrator.dag_executor.hook_registry.execute")
async def test_dynamic_synthesis_model_strategy_routing(
    mock_hook_execute: MagicMock,
    mock_reduce: MagicMock,
    mock_bp_validate: MagicMock,
    mock_repo: AsyncMock,
    mock_compiler: AsyncMock,
) -> None:
    """PROMISE: Validate dynamic model_strategy == 'synthesis' routing logic invokes MatrixReducer."""
    from backend_v2.models.enums import HistoricalContextMode
    from backend_v2.models.v2_core import StepRule
    from backend_v2.services.orchestrator.dag_executor import DAGExecutor

    executor = DAGExecutor(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        prompt_block_repo=mock_repo,
        output_profile_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
        rag_preflight=AsyncMock(),
    )

    workflow = Workflow.model_construct(
        id="wf_0123456789abcdef01",
        name="Test Workflow",
        organization_id="org_1",
        default_profile_id="prof_1",
        slug="test-workflow",
        description="A test workflow",
        status="DRAFT",
        version=1,
        allowed_exports=[],
        historical_context_mode=HistoricalContextMode.DISABLED,
        steps=[
            StepRule.model_construct(
                id="stp_0123456789abcdef01", task_blueprint="bp_0123456789abcdef01", input_mappings={}
            )
        ],
    )

    mock_repo.get_step_by_id.return_value = {
        "id": "bp_0123456789abcdef01",
        "type": "standard",
        "model_strategy": "synthesis",
    }

    mock_repo.get_workflow_by_id.return_value = workflow.model_dump()
    mock_repo.get_execution.return_value = {
        "id": "exe_0123456789abcdef01",
        "workflow_id": "wf_0123456789abcdef01",
        "output_profile_id": "prof_1",
        "status": "PASSED",
        "target_locale": "en",
        "metadata": {},
        "raw_inputs": {"dynamic_inputs": {}},
    }

    mock_bp_validate.return_value = MagicMock(id="bp_0123456789abcdef01", type="standard", model_strategy="synthesis")

    from backend_v2.core.hook_registry import HookDeltaDTO, HookResult

    mock_hook_execute.return_value = HookResult(success=True, state_delta=HookDeltaDTO(delta={"distilled_inputs": {}}))

    mock_reduce.return_value = MagicMock(model_dump=lambda: {"mock": "matrix"})

    with patch.object(executor.node_executor, "execute", return_value=[]):
        try:
            await executor.execute_workflow(
                execution_id="exe_0123456789abcdef01",
                workflow=workflow,
                raw_inputs=WorkflowInputs.model_construct(dynamic_inputs={}),
            )
        except Exception as e:
            print(f"Exception caught in test: {e}")
            pass

    mock_reduce.assert_called_once()
