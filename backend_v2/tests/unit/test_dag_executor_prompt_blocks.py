from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.core.hook_registry import HookResult
from backend_v2.models.v2_core import ExecutionStatus, I18nText, StepRule, Workflow
from backend_v2.services.orchestrator.dag_executor import DAGExecutor


@pytest.fixture
def mock_repo() -> Any:
    repo = AsyncMock()
    from backend_v2.models.enums import BlockDataType

    repo.get_all_prompt_blocks.return_value = [
        {
            "id": "blk_0123456789abcdef0123456789ab",
            "slug": "task_bp",
            "label": {"default_locale": "fi", "translations": {"fi": "Testi", "en": "Test"}},
            "description": {"default_locale": "fi", "translations": {"fi": "Kuvaus", "en": "Desc"}},
            "category_id": "test",
            "type": BlockDataType.STRING,
            "allow_decimals": False,
            "output_extensions": [],
        }
    ]
    repo.get_step.return_value = {
        "id": "step_1111111111111111",
        "slug": "task_bp",
        "name": {"default_locale": "fi", "translations": {"fi": "Vaihe", "en": "Step"}},
        "prompt_blocks": ["blk_0123456789abcdef0123456789ab"],
        "model_strategy": "fast",
        "pre_hooks": [],
    }
    repo.get_step_by_id.return_value = repo.get_step.return_value
    repo.get_workflow.return_value = {
        "id": "wf_5555555555555555",
        "slug": "wf_test_slug",
        "status": "draft",
        "version": 1,
        "default_profile_id": "prof_dddd1111dddd1111",
        "name": {"default_locale": "en", "translations": {"en": "Test WF"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "steps": [{"id": "step_1111111111111111", "task_blueprint": "task_bp"}],
    }
    return repo


@pytest.fixture
def mock_compiler() -> Any:
    compiler = MagicMock()
    compiler.build_xml_context.return_value = "<test>context</test>"
    # Mocking a dynamic schema
    schema_mock = MagicMock()
    schema_mock.model_json_schema.return_value = {"type": "object"}
    compiler.build_dynamic_schema.return_value = schema_mock
    return compiler


@pytest.mark.asyncio
async def test_dag_executor_uses_prompt_blocks_instead_of_matrices(mock_repo: Any, mock_compiler: Any) -> None:
    # Setup Executor
    executor = DAGExecutor(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )  # noqa: E501

    # Setup basic valid workflow
    workflow = Workflow(
        id="wf_5555555555555555",
        slug="wf_test_slug",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        name=I18nText(default_locale="en", translations={"en": "Test WF"}),
        description=I18nText(default_locale="en", translations={"en": "Desc"}),
        steps=[StepRule(id="step_1111111111111111", task_blueprint="task_bp")],
    )

    # Execute
    # We mock LLMClient.from_strategy to avoid actual LLM calls
    with patch("backend_v2.llm.client.LLMClient.from_strategy", new_callable=AsyncMock) as mock_strategy:
        mock_bound_client = AsyncMock()
        mock_bound_client.run_structured_task.return_value = (
            MagicMock(model_dump=lambda **kwargs: {"test_res": 1}),
            {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30, "cost_usd": 0.05},
        )
        mock_strategy.return_value = mock_bound_client

        mock_repo.get_execution.return_value = {
            "id": "exe_1231231231231231",
            "workflow_id": "wf_5555555555555555",
            "status": ExecutionStatus.RUNNING,
            "active_profile_id": "prof_dddd1111dddd1111",
            "strictness_level": 50,
            "scoring_strategy": "WATERFALL_FLOOR",
            "raw_inputs": {"chat_log": "dGVzdA=="},
            "metadata": {"target_locale": "fi", "profile_id": "prof_dddd1111dddd1111"},
        }

        # Also mock the hook registry to prevent "Hook not found" errors in isolated tests
        with patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks:
            mock_hooks.execute = AsyncMock(
                return_value=HookResult(success=True, state_delta={"inputs": {"chat_log": "dGVzdA=="}})
            )

            record = await executor.execute_workflow(
                execution_id="exe_1231231231231231", workflow=workflow, raw_inputs={"chat_log": "dGVzdA=="}
            )

    # Assert repo called new method instead of get_all_matrices
    mock_repo.get_all_prompt_blocks.assert_called_once()
    assert not hasattr(mock_repo, "get_all_matrices") or not mock_repo.get_all_matrices.called
    assert record.status == ExecutionStatus.COMPLETED
    from backend_v2.models.state import StateProjector

    projector = StateProjector()
    results = projector.fold_trace(record.execution_trace)
    assert any(
        dto.step_id == "step_1111111111111111" and dto.block_id == "test_res" and dto.payload == 1 for dto in results
    )
