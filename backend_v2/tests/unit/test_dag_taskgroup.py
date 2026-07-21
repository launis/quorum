import asyncio
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.core.hook_registry import HookResult
from backend_v2.exceptions import AppException
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.enums import ExecutionStatus
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
        "name": {"default_locale": "en", "translations": {"en": "mock"}},
        "description": {"default_locale": "en", "translations": {"en": "mock"}},
        "hook": "mock_hook",
    }

    # Mock context rehydration
    repo.get_execution.return_value = {
        "id": "exe_1111222233334444",
        "workflow_id": "wf_tg_test",
        "status": ExecutionStatus.PENDING,
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
        historical_context_mode="DISABLED",
        id="wf_4444444444444444",
        slug="wf_tg",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        name=I18nText(default_locale="en", translations={"en": "TG Test", "fi": "TG Test"}),
        description=I18nText(default_locale="en", translations={"en": "Desc", "fi": "Desc"}),
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
        mock_hooks.execute = AsyncMock(return_value=HookResult(success=True, state_delta={"log": "test"}))

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
            assert payload["step_states"]["step_5555222255552222"]["status"] == ExecutionStatus.PASSED.value
            assert payload["step_states"]["step_ffff1111ffff1111"]["status"] == ExecutionStatus.FAILED.value


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
        historical_context_mode="DISABLED",
        id="wf_4444444444444444",
        slug="wf_tg_dep",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        name=I18nText(default_locale="en", translations={"en": "TG Test", "fi": "TG Test"}),
        description=I18nText(default_locale="en", translations={"en": "Desc", "fi": "Desc"}),
        steps=[
            StepRule(id="step_A", task_blueprint="bp_fail"),
            StepRule(id="step_C", task_blueprint="bp_dep", depends_on=["step_A"]),
        ],
    )

    async def mock_execute(step: StepRule, *args: Any, **kwargs: Any) -> list[Any]:
        if step.id == "step_A":
            return [
                ErrorTraceEvent(
                    step_name=step.id, error_code="MOCK_FAIL", error_message="Intentional failure", content={}
                )
            ]
        elif step.id == "step_C":
            raise ValueError("Step C should not have executed")
        return []

    # Bypass the hook registry safely
    with patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks:
        mock_hooks.execute = AsyncMock(return_value=HookResult(success=True, state_delta={"log": "test"}))

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
            assert payload["step_states"]["step_A"]["status"] == ExecutionStatus.FAILED.value
            assert payload["step_states"]["step_C"]["status"] == ExecutionStatus.FAILED.value
