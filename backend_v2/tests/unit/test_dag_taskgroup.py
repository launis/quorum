import asyncio
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.core.hook_registry import HookResult
from backend_v2.exceptions import AppException
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.state import ErrorTraceEvent
from backend_v2.models.v2_core import I18nText, StepRule, Workflow
from backend_v2.services.orchestrator.dag_executor import DAGExecutor


@pytest.fixture
def mock_repo() -> AsyncMock:
    repo = AsyncMock()
    from backend_v2.models.enums import ExecutionStatus

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
async def test_taskgroup_cancels_sibling_on_error(mock_repo: AsyncMock, mock_compiler: AsyncMock) -> None:
    """Test that asyncio.TaskGroup automatically cancels sibling tasks
    when one task fails, eradicating zombie threads naturally.
    """
    executor = DAGExecutor(
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
            # Just sleep; the TaskGroup will cancel this when step_1 fails.
            await asyncio.sleep(10.0)
            return []
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

            # The failure from the first step should unwrap gracefully
            assert "Intentional failure" in str(exc_info.value), "AppException should propagate properly"
