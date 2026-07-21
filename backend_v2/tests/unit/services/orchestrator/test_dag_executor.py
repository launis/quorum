from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.core.hook_registry import HookResult
from backend_v2.exceptions import AppException
from backend_v2.models.v2_core import ExecutionStatus, I18nText, Workflow, WorkflowInputs
from backend_v2.services.orchestrator.dag_executor import DAGExecutor, ExecutionCommitter


@pytest.fixture
def mock_repo() -> Any:
    repo = AsyncMock()
    repo.get_step_by_id.return_value = {
        "id": "blp_1234567890abcdef",
        "type": "logic",
        "model_strategy": "logic",
        "slug": "mock_step",
        "name": {"default_locale": "en", "translations": {"en": "Mock Step"}},
        "description": {"default_locale": "en", "translations": {"en": "Mock"}},
        "hook": "mock_hook",
    }
    return repo


@pytest.fixture
def mock_compiler() -> Any:
    compiler = MagicMock()
    return compiler


@pytest.mark.asyncio
async def test_dag_executor_runs_and_remains_running_for_async_render(mock_repo: Any, mock_compiler: Any) -> None:
    executor = DAGExecutor(rag_preflight=MagicMock(), 
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
        historical_context_mode="DISABLED",
        id="wf_5555555555555555",
        slug="wf_test_slug",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        name=I18nText(default_locale="en", translations={"en": "Test WF", "fi": "Test WF"}),
        description=I18nText(default_locale="en", translations={"en": "Desc", "fi": "Desc"}),
        steps=[],
    )

    mock_repo.get_execution.return_value = None
    mock_repo.get_user = AsyncMock(return_value={"language": "fi"})

    with patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks:
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(success=True, state_delta={"inputs": {"chat_log": "test"}})
        )
        record = await executor.execute_workflow(
            execution_id="exe_1231231231231231",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={"chat_log": "test"}, language="en", user_id="usr_test123"),
        )

    # Assert language is passed in global_context_vars
    mock_hooks.execute.assert_called_once()
    args, _ = mock_hooks.execute.call_args
    assert args[0] == "input_processing"
    assert args[1].global_context_vars.get("language") == "fi"

    # Epic 47 Phase 2: Workflow remains RUNNING for async render worker
    assert record.status == ExecutionStatus.RUNNING


@pytest.mark.asyncio
async def test_dag_executor_fails_fast_on_hook_error(mock_repo: Any, mock_compiler: Any) -> None:
    executor = DAGExecutor(rag_preflight=MagicMock(), 
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
        historical_context_mode="DISABLED",
        id="wf_5555555555555555",
        slug="wf_test_slug",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        name=I18nText(default_locale="en", translations={"en": "Test WF", "fi": "Test WF"}),
        description=I18nText(default_locale="en", translations={"en": "Desc", "fi": "Desc"}),
        steps=[],
    )

    mock_repo.get_execution.return_value = None

    with patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks:
        mock_hooks.execute.side_effect = Exception("Hook failed internally")

        with pytest.raises(AppException) as exc_info:
            await executor.execute_workflow(
                execution_id="exe_1231231231231231",
                workflow=workflow,
                raw_inputs=WorkflowInputs(dynamic_inputs={"chat_log": "test"}),
            )

        assert exc_info.value.status_code == 400
        assert "Pre-Hydration failed: Hook failed internally" in exc_info.value.message


@pytest.mark.asyncio
async def test_execution_committer_commit_trace(mock_repo: Any) -> None:
    committer = ExecutionCommitter(mock_repo, "exec_123")

    await committer.commit_trace(
        trace=[],
        status=ExecutionStatus.PENDING,
        step_states={},
        error="test error",
        context_variables={"test_key": "test_val"},
    )

    mock_repo.update_execution.assert_called_once()
    args, kwargs = mock_repo.update_execution.call_args
    assert args[0] == "exec_123"
    assert args[1]["status"] == "PENDING"
    assert args[1]["error"] == "test error"
    assert args[1]["context_variables"] == {"test_key": "test_val"}


@pytest.mark.asyncio
async def test_dag_executor_hoists_and_passes_semaphore(mock_repo: Any, mock_compiler: Any) -> None:
    executor = DAGExecutor(rag_preflight=MagicMock(), 
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
        historical_context_mode="DISABLED",
        id="wf_5555555555555555",
        slug="wf_test_slug",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        name=I18nText(default_locale="en", translations={"en": "Test WF", "fi": "Test WF"}),
        description=I18nText(default_locale="en", translations={"en": "Desc", "fi": "Desc"}),
        steps=[],
    )

    mock_repo.get_execution.return_value = None

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", new_callable=AsyncMock) as mock_node_execute,
    ):
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(success=True, state_delta={"inputs": {"chat_log": "test"}})
        )
        mock_node_execute.return_value = []

        # Inject one step to trigger execution
        from backend_v2.models.v2_core import StepRule

        workflow = workflow.model_copy(
            update={
                "steps": [
                    StepRule(
                        id="stp_1234567890abcdef",
                        task_blueprint="blp_1234567890abcdef",
                        input_mappings={},
                        depends_on=[],
                    )
                ]
            }
        )

        await executor.execute_workflow(
            execution_id="exe_1231231231231231",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={"chat_log": "test"}),
        )

        mock_node_execute.assert_called_once()
        _, call_kwargs = mock_node_execute.call_args
        assert "semaphore" in call_kwargs
        import asyncio

        assert isinstance(call_kwargs["semaphore"], asyncio.Semaphore)


@pytest.mark.asyncio
async def test_dag_executor_exceptiongroup_dlq_routing(mock_repo: Any, mock_compiler: Any) -> None:
    """Test that an unhandled exception inside a step triggers ExceptionGroup cascade and DLQ routing."""
    executor = DAGExecutor(rag_preflight=MagicMock(), 
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

    from backend_v2.models.v2_core import StepRule, Workflow, WorkflowInputs

    workflow = Workflow(
        allowed_exports=["pdf"],
        historical_context_mode="DISABLED",
        id="wf_5555555555555555",
        slug="wf_test_slug",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        name=I18nText(default_locale="en", translations={"en": "Test WF", "fi": "Test WF"}),
        description=I18nText(default_locale="en", translations={"en": "Desc", "fi": "Desc"}),
        steps=[
            StepRule(
                id="stp_1234567890abcdef",
                task_blueprint="blp_1234567890abcdef",
                input_mappings={},
                depends_on=[],
            )
        ],
    )

    mock_repo.get_execution.return_value = None

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", new_callable=AsyncMock) as mock_node_execute,
    ):
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(success=True, state_delta={"inputs": {"chat_log": "test"}})
        )
        # Force the node executor to raise a generic exception to trigger the TaskGroup crash
        mock_node_execute.side_effect = Exception("System Crash")

        with pytest.raises(AppException) as exc_info:
            await executor.execute_workflow(
                execution_id="exe_1231231231231231",
                workflow=workflow,
                raw_inputs=WorkflowInputs(dynamic_inputs={"chat_log": "test"}),
            )

        assert exc_info.value.status_code == 500
        assert "System Crash" in exc_info.value.message

        # Verify that committer was called with FAILED status for the whole execution
        args, kwargs = mock_repo.update_execution.call_args
        assert args[1]["status"] == ExecutionStatus.FAILED.value
        assert "System Crash" in args[1]["error"]


@pytest.mark.asyncio
async def test_node_executor_injects_synthesis_engine(mock_repo: Any, mock_compiler: Any) -> None:
    """Verify that NodeExecutor match/case injects SynthesisEngine when override is SYNTHESIS."""
    import asyncio

    from backend_v2.models.v2_core import StepRule
    from backend_v2.services.orchestrator.dag_executor import NodeExecutor

    executor = NodeExecutor(
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

    step = StepRule(
        id="stp_1234567890abcdef",
        task_blueprint="bp_1234567890abcdef",
        expected_sdui_type="markdown",
    )

    mock_repo.get_step_by_id.return_value = {
        "id": "bp_1234567890abcdef",
        "slug": "synthesis-slug",
        "type": "llm",
        "model_strategy": "synthesis",
        "criteria_block_ids": ["blk_1234567890abcdef"],
        "extraction_protocol_block_id": "blk_1234567890abcdef",
        "name": {"default_locale": "en", "translations": {"en": "en"}},
        "description": {"default_locale": "en", "translations": {"en": "en"}},
    }
    projector = MagicMock()
    projector.snapshot = {}
    semaphore = asyncio.Semaphore(1)

    with (
        patch("backend_v2.services.orchestrator.engines.synthesis_engine.SynthesisEngine") as mock_engine_class,
        patch(
            "backend_v2.services.orchestrator.strategies.llm.LLMNodeStrategy.execute", new_callable=AsyncMock
        ) as mock_strategy_execute,
    ):
        mock_strategy_execute.return_value = []

        await executor.execute(
            execution_id="exe_1",
            workflow_id="wf_1",
            step=step,
            metadata={},
            expected_inputs=[],
            projector=projector,
            semaphore=semaphore,
            context_variables={},
        )

        mock_engine_class.assert_called_once()
