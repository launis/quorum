from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.core.hook_registry import HookResult
from backend_v2.models.v2_core import ExecutionStatus, I18nText, Workflow
from backend_v2.services.orchestrator.dag_executor import DAGExecutor


@pytest.fixture
def mock_repo() -> Any:
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_compiler() -> Any:
    compiler = MagicMock()
    return compiler


from backend_v2.exceptions import AppException


@pytest.mark.asyncio
async def test_dag_executor_fails_fast_on_missing_strictness(mock_repo: Any, mock_compiler: Any) -> None:
    executor = DAGExecutor(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )

    workflow = Workflow(
        id="wf_5555555555555555",
        slug="wf_test_slug",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        name=I18nText(default_locale="en", translations={"en": "Test WF"}),
        description=I18nText(default_locale="en", translations={"en": "Desc"}),
        steps=[],
    )

    mock_repo.get_execution.return_value = None

    with pytest.raises(AppException) as exc_info:
        await executor.execute_workflow(
            execution_id="exe_1231231231231231", workflow=workflow, raw_inputs={"chat_log": "dGVzdA=="}
        )

    assert exc_info.value.status_code == 400
    assert "Missing 'strictness_level'" in exc_info.value.message


@pytest.mark.asyncio
async def test_dag_executor_creates_record_with_provided_strictness(mock_repo: Any, mock_compiler: Any) -> None:
    executor = DAGExecutor(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )

    workflow = Workflow(
        id="wf_5555555555555555",
        slug="wf_test_slug",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        name=I18nText(default_locale="en", translations={"en": "Test WF"}),
        description=I18nText(default_locale="en", translations={"en": "Desc"}),
        steps=[],
    )

    mock_repo.get_execution.return_value = None

    with patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks:
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(success=True, state_delta={"inputs": {"chat_log": "test"}})
        )
        record = await executor.execute_workflow(
            execution_id="exe_1231231231231231",
            workflow=workflow,
            raw_inputs={"chat_log": "test", "strictness_level": 85},
        )

    assert record.strictness_level == 85
    assert record.status == ExecutionStatus.COMPLETED
