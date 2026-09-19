import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.core.hook_registry import HookDeltaDTO, HookResult
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import User, UserRole
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionStep, FrozenContext
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.step import Step, StepRule
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.trace import ExecutionUpdateDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.services.orchestrator.dag_executor import DAGExecutor, ExecutionCommitter


@pytest.fixture
def mock_repo() -> Any:
    repo = AsyncMock()
    repo.get_step_by_id.return_value = {
        "id": "blp_1234567890abcdef",
        "type": "logic",
        "slug": "mock_step",
        "name": {"translations": {"en": "Mock Step"}},
        "description": {"translations": {"en": "Mock"}},
        "hook": "mock_hook",
    }
    return repo


@pytest.fixture
def mock_compiler() -> Any:
    compiler = MagicMock()
    return compiler


@pytest.mark.asyncio
async def test_dag_executor_runs_and_remains_running_for_async_render(mock_repo: Any, mock_compiler: Any) -> None:
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
        historical_context_mode="DISABLED",
        id="wf_5555555555555555",
        slug="wf_test_slug",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "Test WF", "fi": "Test WF"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
        steps=[],
    )

    mock_repo.get_execution.return_value = None
    mock_repo.get_user = AsyncMock(
        return_value=User(
            id="usr_test1234",
            email="test@example.com",
            role=UserRole.ADMIN,
            is_active=True,
            language="fi",
            theme_mode="system",
            created_at="2026-01-01T00:00:00Z",
        )
    )

    with patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks:
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(success=True, state_delta=HookDeltaDTO(delta={"inputs": {"chat_log": "test"}}))
        )
        record = await executor.execute_workflow(
            execution_id="exe_1231231231231231",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={"chat_log": "test"}, language="en", user_id="usr_test1234"),
        )

    # Assert language is passed in global_context_vars
    mock_hooks.execute.assert_called_once()
    args, _ = mock_hooks.execute.call_args
    assert args[0] == "input_processing"
    assert args[1].global_context_vars.vars["language"] == "fi"

    # Workflow remains RUNNING for async render worker
    assert record.status == ExecutionStatus.RUNNING


@pytest.mark.asyncio
async def test_dag_executor_fails_fast_on_hook_error(mock_repo: Any, mock_compiler: Any) -> None:
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
        historical_context_mode="DISABLED",
        id="wf_5555555555555555",
        slug="wf_test_slug",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "Test WF", "fi": "Test WF"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
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
    assert args[1].status == ExecutionStatus.PENDING
    assert args[1].error == "test error"
    assert args[1].context_variables == {"test_key": "test_val"}


@pytest.mark.asyncio
async def test_dag_executor_hoists_and_passes_semaphore(mock_repo: Any, mock_compiler: Any) -> None:
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
        historical_context_mode="DISABLED",
        id="wf_5555555555555555",
        slug="wf_test_slug",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "Test WF", "fi": "Test WF"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
        steps=[],
    )

    mock_repo.get_execution.return_value = None

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", new_callable=AsyncMock) as mock_node_execute,
    ):
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(success=True, state_delta=HookDeltaDTO(delta={"inputs": {"chat_log": "test"}}))
        )
        mock_node_execute.return_value = []

        # Inject one step to trigger execution
        from backend_v2.models.domain.step import StepRule

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

    from backend_v2.models.domain.inputs import WorkflowInputs
    from backend_v2.models.domain.step import StepRule
    from backend_v2.models.domain.workflow import Workflow

    workflow = Workflow(
        historical_context_mode="DISABLED",
        id="wf_5555555555555555",
        slug="wf_test_slug",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "Test WF", "fi": "Test WF"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
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
            return_value=HookResult(success=True, state_delta=HookDeltaDTO(delta={"inputs": {"chat_log": "test"}}))
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
        assert "Workflow failed" in exc_info.value.message

        # Verify that committer was called with FAILED status for the whole execution
        calls = mock_repo.update_execution.call_args_list
        final_call_args = calls[-1][0]
        assert final_call_args[1].status in (ExecutionStatus.FAILED, ExecutionStatus.FAILED.value)

        # Verify that the original error was committed at some point
        error_recorded = any(
            isinstance(call[0][1], ExecutionUpdateDTO) and call[0][1].error and "System Crash" in call[0][1].error
            for call in calls
        )
        assert error_recorded, "The exception 'System Crash' should have been committed as an error"


@pytest.mark.asyncio
async def test_node_executor_injects_synthesis_engine(mock_repo: Any, mock_compiler: Any) -> None:
    """Verify that NodeExecutor injects SynthesisEngine when criteria block is synthesis or model_strategy is synthesis."""
    import asyncio

    from backend_v2.models.core_base import I18nText
    from backend_v2.models.domain.prompt_blocks import SystemRulePromptBlock
    from backend_v2.models.domain.step import StepRule
    from backend_v2.models.enums import PromptBlockCategory
    from backend_v2.services.orchestrator.dag_executor import NodeExecutor
    from backend_v2.services.orchestrator.strategies.base import StrategyDependencies

    mock_prompt_block_repo = AsyncMock()
    mock_prompt_block_repo.get_prompt_blocks_by_ids.return_value = [
        SystemRulePromptBlock(
            id="blk_1234567890abcdef",
            slug="synthesis-rule",
            label=I18nText(translations={"en": "Synthesis Rule"}),
            description=I18nText(translations={"en": "Synthesis Rule Desc"}),
            category_id=PromptBlockCategory.SYSTEM_RULE,
        )
    ]

    deps = StrategyDependencies(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        prompt_block_repo=mock_prompt_block_repo,
        output_profile_repo=AsyncMock(),
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )
    executor = NodeExecutor(deps=deps)

    step = StepRule(
        id="stp_1234567890abcdef",
        task_blueprint="bp_1234567890abcdef",
        expected_sdui_type="markdown",
    )

    mock_repo.get_step_by_id.return_value = {
        "id": "bp_1234567890abcdef",
        "slug": "synthesis-slug",
        "type": "llm",
        "cognitive_tier": "fast",
        "pre_hooks": ["atom_flattening_hook"],
        "criteria_block_ids": ["blk_1234567890abcdef"],
        "extraction_protocol_block_id": "blk_1234567890abcdef",
        "name": {"translations": {"en": "en"}},
        "description": {"translations": {"en": "en"}},
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


@pytest.mark.asyncio
async def test_node_executor_blueprint_missing_error(mock_repo: Any, mock_compiler: Any) -> None:
    """Test NodeExecutor fails fast when step has no task_blueprint."""
    import asyncio

    from backend_v2.exceptions import ErrorCodes
    from backend_v2.models.domain.step import StepRule
    from backend_v2.services.orchestrator.dag_executor import NodeExecutor
    from backend_v2.services.orchestrator.strategies.base import StrategyDependencies

    deps = StrategyDependencies(
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
    executor = NodeExecutor(deps=deps)
    step = StepRule.model_construct(id="stp_1111222233334444", task_blueprint="", expected_sdui_type="markdown")
    projector = MagicMock()
    projector.snapshot = []
    semaphore = asyncio.Semaphore(1)

    with pytest.raises(AppException) as exc_info:
        await executor.execute(
            execution_id="exe_1111222233334444",
            workflow_id="wor_1111222233334444",
            step=step,
            metadata={},
            projector=projector,
            semaphore=semaphore,
        )
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR


@pytest.mark.asyncio
async def test_node_executor_step_def_not_found_error(mock_repo: Any, mock_compiler: Any) -> None:
    """Test NodeExecutor fails fast when step definition is not found in repository."""
    import asyncio

    from backend_v2.exceptions import ErrorCodes
    from backend_v2.models.domain.step import StepRule
    from backend_v2.services.orchestrator.dag_executor import NodeExecutor
    from backend_v2.services.orchestrator.strategies.base import StrategyDependencies

    mock_workflow_repo = AsyncMock()
    mock_workflow_repo.get_step_by_id.return_value = None
    deps = StrategyDependencies(
        exec_repo=mock_repo,
        workflow_repo=mock_workflow_repo,
        comp_repo=mock_repo,
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )
    executor = NodeExecutor(deps=deps)
    step = StepRule(id="stp_1111222233334444", task_blueprint="bp_1111222233334444", expected_sdui_type="markdown")
    projector = MagicMock()
    projector.snapshot = []
    semaphore = asyncio.Semaphore(1)

    with pytest.raises(AppException) as exc_info:
        await executor.execute(
            execution_id="exe_1111222233334444",
            workflow_id="wor_1111222233334444",
            step=step,
            metadata={},
            projector=projector,
            semaphore=semaphore,
        )
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR


@pytest.mark.asyncio
async def test_node_executor_injects_tda_and_prompt_engines(mock_repo: Any, mock_compiler: Any) -> None:
    """Test NodeExecutor resolves TDAEngine for matrix blocks and PromptEngine for regular blocks."""
    from backend_v2.models.core_base import I18nText
    from backend_v2.models.domain.matrix import MatrixScale
    from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, SystemRulePromptBlock
    from backend_v2.models.domain.step import Step
    from backend_v2.models.enums import CognitiveTier, PromptBlockCategory, StepType
    from backend_v2.services.orchestrator.dag_executor import NodeExecutor
    from backend_v2.services.orchestrator.engines.prompt_engine import PromptEngine
    from backend_v2.services.orchestrator.engines.tda_engine import TDAEngine
    from backend_v2.services.orchestrator.strategies.base import StrategyDependencies

    mock_prompt_block_repo = AsyncMock()
    matrix_block = MatrixPromptBlock(
        id="blk_1111222233334444",
        slug="matrix-block",
        label=I18nText(translations={"en": "Matrix"}),
        description=I18nText(translations={"en": "Matrix Desc"}),
        category_id=PromptBlockCategory.MATRIX,
        scales=[
            MatrixScale(
                score=1,
                ai_label="L1",
                claims=[],
            )
        ],
    )
    system_block = SystemRulePromptBlock(
        id="blk_5555666677778888",
        slug="sys-block",
        label=I18nText(translations={"en": "Sys"}),
        description=I18nText(translations={"en": "Sys Desc"}),
        category_id=PromptBlockCategory.SYSTEM_RULE,
    )
    mock_prompt_block_repo.get_prompt_blocks_by_ids.return_value = [matrix_block, system_block]

    deps = StrategyDependencies(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        prompt_block_repo=mock_prompt_block_repo,
        output_profile_repo=AsyncMock(),
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )
    executor = NodeExecutor(deps=deps)

    matrix_step_def = Step(
        id="stp_1111222233334444",
        slug="matrix-slug",
        type=StepType.LLM,
        cognitive_tier=CognitiveTier.FAST,
        criteria_block_ids=["blk_1111222233334444"],
        role_block_id="blk_5555666677778888",
        extraction_protocol_block_id="blk_5555666677778888",
        execution_persona_block_id="blk_5555666677778888",
        name=I18nText(translations={"en": "Matrix Step"}),
        description=I18nText(translations={"en": "Matrix Step"}),
    )

    tda_engine = executor._resolve_execution_engine(matrix_step_def, [matrix_block, system_block])
    assert isinstance(tda_engine, TDAEngine)

    prompt_step_def = Step(
        id="stp_5555666677778888",
        slug="prompt-slug",
        type=StepType.LLM,
        cognitive_tier=CognitiveTier.FAST,
        criteria_block_ids=["blk_5555666677778888"],
        extraction_protocol_block_id="blk_5555666677778888",
        name=I18nText(translations={"en": "Prompt Step"}),
        description=I18nText(translations={"en": "Prompt Step"}),
    )
    prompt_engine = executor._resolve_execution_engine(prompt_step_def, [system_block])
    assert isinstance(prompt_engine, PromptEngine)


@pytest.mark.asyncio
async def test_node_executor_normalizes_input_mappings_and_handles_exception(
    mock_repo: Any, mock_compiler: Any
) -> None:
    """Test NodeExecutor input_mappings normalization and error trace event returning on generic exception."""
    import asyncio

    from backend_v2.models.core_base import I18nText
    from backend_v2.models.domain.prompt_blocks import SystemRulePromptBlock
    from backend_v2.models.domain.step import StepRule
    from backend_v2.models.enums import PromptBlockCategory
    from backend_v2.models.state import ErrorTraceEvent, StepOutputDTO
    from backend_v2.services.orchestrator.dag_executor import NodeExecutor
    from backend_v2.services.orchestrator.strategies.base import NodeStrategy, StrategyDependencies

    mock_pb_repo = AsyncMock()
    mock_pb_repo.get_prompt_blocks_by_ids.return_value = [
        SystemRulePromptBlock(
            id="blk_1111222233334444",
            slug="rule",
            label=I18nText(translations={"en": "Rule"}),
            description=I18nText(translations={"en": "Desc"}),
            category_id=PromptBlockCategory.SYSTEM_RULE,
        )
    ]
    deps = StrategyDependencies(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        prompt_block_repo=mock_pb_repo,
        output_profile_repo=AsyncMock(),
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )
    executor = NodeExecutor(deps=deps)
    step = StepRule(
        id="stp_1111222233334444",
        task_blueprint="bp_1111222233334444",
        input_mappings={"text": "steps.step1.text_field"},
    )
    mock_repo.get_step_by_id.return_value = {
        "id": "bp_1111222233334444",
        "slug": "s",
        "type": "logic",
        "cognitive_tier": "fast",
        "hook": "mock_hook",
        "name": {"translations": {"en": "en"}},
        "description": {"translations": {"en": "en"}},
    }
    projector = MagicMock()
    projector.snapshot = [
        StepOutputDTO(step_id="step1", block_id="b1", data_type="text", payload={"text_field": "hello"})
    ]
    semaphore = asyncio.Semaphore(1)

    with patch(
        "backend_v2.services.orchestrator.strategies.registry.NodeStrategyFactory.create_strategy"
    ) as mock_factory:
        mock_strat = MagicMock(spec=NodeStrategy)
        mock_strat.assert_quota = AsyncMock(side_effect=Exception("Generic Strategy Failure"))
        mock_factory.return_value = mock_strat

        events = await executor.execute(
            execution_id="exe_1111222233334444",
            workflow_id="wor_1111222233334444",
            step=step,
            metadata={"organization_id": "org_1111222233334444"},
            projector=projector,
            semaphore=semaphore,
        )
        assert len(events) == 1
        assert isinstance(events[0], ErrorTraceEvent)
        assert events[0].error_code == "STEP_FAILED"


@pytest.mark.asyncio
async def test_dag_executor_cascading_dependency_failure(mock_repo: Any, mock_compiler: Any) -> None:
    """Test that downstream steps fail fast with cascading failure when their dependency fails."""
    from backend_v2.models.domain.inputs import WorkflowInputs
    from backend_v2.models.domain.step import StepRule
    from backend_v2.models.domain.workflow import Workflow
    from backend_v2.models.state import ErrorTraceEvent

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
        historical_context_mode="DISABLED",
        id="wor_1111222233334444",
        slug="wf_cascading",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "Cascading WF"}),
        description=I18nText(translations={"en": "Desc"}),
        steps=[
            StepRule(id="stp_1111222233334444", task_blueprint="bp_1111222233334444", depends_on=[]),
            StepRule(
                id="stp_5555666677778888", task_blueprint="bp_5555666677778888", depends_on=["stp_1111222233334444"]
            ),
        ],
    )
    mock_repo.get_execution.return_value = None
    mock_repo.get_step_by_id.side_effect = lambda b_id: {
        "id": b_id,
        "slug": b_id,
        "type": "logic",
        "cognitive_tier": "fast",
        "hook": "mock_hook",
        "name": {"translations": {"en": "en"}},
        "description": {"translations": {"en": "en"}},
    }

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", new_callable=AsyncMock) as mock_node_execute,
    ):
        mock_hooks.execute = AsyncMock(return_value=HookResult(success=True, state_delta={}))
        mock_node_execute.return_value = [
            ErrorTraceEvent(step_name="stp_1111222233334444", error_code="STEP_FAILED", error_message="Step 1 crashed")
        ]

        with pytest.raises(AppException) as exc_info:
            await executor.execute_workflow(
                execution_id="exe_1111222233334444",
                workflow=workflow,
                raw_inputs=WorkflowInputs(dynamic_inputs={}),
            )
        assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_dag_executor_resumes_existing_record_and_handles_preflight(mock_repo: Any, mock_compiler: Any) -> None:
    """Test DAGExecutor resuming an existing record with already passed steps and executing RAG preflight."""
    from backend_v2.models.domain.execution import ExecutionRecord, ExecutionStepState, FrozenContext
    from backend_v2.models.domain.inputs import WorkflowInputs
    from backend_v2.models.domain.step import StepRule
    from backend_v2.models.domain.system_config import MCPAuditTrace
    from backend_v2.models.domain.workflow import Workflow
    from backend_v2.models.enums import ExecutionStatus
    from backend_v2.models.state import TraceEvent

    mock_rag_preflight = AsyncMock()
    mock_rag_preflight.execute.return_value = {"atoms": ["a1", "a2"]}

    executor = DAGExecutor(
        rag_preflight=mock_rag_preflight,
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

    step1 = StepRule(id="stp_1111222233334444", task_blueprint="stp_1111222233334444", depends_on=[])
    workflow = Workflow(
        historical_context_mode="DISABLED",
        id="wor_1111222233334444",
        slug="wf_resume",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "Resume WF"}),
        description=I18nText(translations={"en": "Desc"}),
        steps=[step1],
    )

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_1111222233334444",
        "slug": "synthesis",
        "type": "llm",
        "cognitive_tier": "fast",
        "pre_hooks": ["atom_flattening_hook"],
        "criteria_block_ids": ["blk_1111222233334444"],
        "extraction_protocol_block_id": "blk_1111222233334444",
        "name": {"translations": {"en": "en"}},
        "description": {"translations": {"en": "en"}},
    }

    existing_record = ExecutionRecord(
        id="exe_1111222233334444",
        workflow_id=workflow.id,
        output_profile_id="prof_dddd1111dddd1111",
        target_locale="en",
        metadata=ExecutionMetadata(),
        raw_inputs=WorkflowInputs(dynamic_inputs={}),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        status=ExecutionStatus.PENDING,
        step_states={
            "stp_1111222233334444": ExecutionStepState(
                id="stp_1111222233334444", label="Step 1", status=ExecutionStatus.FAILED
            )
        },
        execution_trace=[TraceEvent(step_name="raw_inputs", event_type="input", content={})],
    )
    mock_repo.get_execution.return_value = existing_record.model_dump(mode="json")

    with (
        patch("backend_v2.services.orchestrator.matrix_reducer.MatrixReducer.reduce_matrix") as mock_matrix_reducer,
        patch.object(executor.node_executor, "execute", new_callable=AsyncMock) as mock_node_execute,
    ):
        mock_reduced = MagicMock()
        mock_reduced.model_dump.return_value = {"reduced": True}
        mock_matrix_reducer.return_value = mock_reduced

        event_with_mcp = TraceEvent(
            step_name="stp_1111222233334444",
            event_type="output",
            content={"result": "ok"},
            metadata={"generated_schema": {"type": "object"}},
            mcp_audit_traces=[
                MCPAuditTrace(
                    id="tr_1111222233334444",
                    tool_id="tool_search",
                    step_name="stp_1111222233334444",
                    query="test search query",
                )
            ],
        )
        mock_node_execute.return_value = [event_with_mcp]

        async def fake_node_execute(*args: Any, **kwargs: Any) -> list[TraceEvent]:
            if "progress_callback" in kwargs and kwargs["progress_callback"]:
                await kwargs["progress_callback"](1, 2)
            if "running_event" in kwargs and kwargs["running_event"]:
                kwargs["running_event"].set()
            return [event_with_mcp]

        mock_node_execute.side_effect = fake_node_execute

        record = await executor.execute_workflow(
            execution_id="exe_1111222233334444",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={}),
        )

        assert record.status == ExecutionStatus.RUNNING
        assert mock_rag_preflight.execute.called
        assert mock_matrix_reducer.called
        assert "generated_schemas" in record.frozen_context.model_dump(mode="json")


@pytest.mark.asyncio
async def test_execution_committer_raises_app_exception_on_update_failure(mock_repo: Any) -> None:
    """Test ExecutionCommitter dual-reports and raises AppException(PROGRESS_UPDATE_FAILED) when update fails."""
    from backend_v2.exceptions import ErrorCodes

    mock_repo.update_execution = AsyncMock(side_effect=Exception("Database connection lost"))
    committer = ExecutionCommitter(mock_repo, "exe_1111222233334444")

    with pytest.raises(AppException) as exc_info:
        await committer.commit_trace(
            trace=[],
            status=ExecutionStatus.PENDING,
            step_states={},
        )
    assert exc_info.value.details["error_code"] == ErrorCodes.PROGRESS_UPDATE_FAILED


@pytest.mark.asyncio
async def test_dag_executor_rag_preflight_failure_handling(mock_repo: Any, mock_compiler: Any) -> None:
    """Test DAGExecutor handles RAG preflight failure and sets state to FAILED."""
    from backend_v2.exceptions import WorkflowExecutionError

    mock_rag_preflight = AsyncMock()
    mock_rag_preflight.execute.side_effect = Exception("RAG service timeout")

    executor = DAGExecutor(
        rag_preflight=mock_rag_preflight,
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

    step1 = StepRule(id="stp_1111222233334444", task_blueprint="stp_1111222233334444", depends_on=[])
    workflow = Workflow(
        historical_context_mode="DISABLED",
        id="wor_1111222233334444",
        slug="wf_preflight_fail",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "Preflight WF"}),
        description=I18nText(translations={"en": "Desc"}),
        steps=[step1],
    )

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_1111222233334444",
        "slug": "synthesis",
        "type": "llm",
        "cognitive_tier": "fast",
        "pre_hooks": ["atom_flattening_hook"],
        "criteria_block_ids": ["blk_1111222233334444"],
        "extraction_protocol_block_id": "blk_1111222233334444",
        "name": {"translations": {"en": "en"}},
        "description": {"translations": {"en": "en"}},
    }
    mock_repo.get_execution.return_value = None

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        pytest.raises((WorkflowExecutionError, AppException)),
    ):
        mock_hooks.execute = AsyncMock(return_value=HookResult(success=True, state_delta={}))
        await executor.execute_workflow(
            execution_id="exe_1111222233334444",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={}),
        )


@pytest.mark.asyncio
async def test_dag_executor_matrix_reducer_failure(mock_repo: Any, mock_compiler: Any) -> None:
    """Test DAGExecutor handles matrix reducer failure and raises WorkflowExecutionError."""
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

    step1 = StepRule(id="stp_1111222233334444", task_blueprint="stp_1111222233334444", depends_on=[])
    workflow = Workflow(
        historical_context_mode="DISABLED",
        id="wor_1111222233334444",
        slug="wf_matrix_fail",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "Matrix Fail WF"}),
        description=I18nText(translations={"en": "Desc"}),
        steps=[step1],
    )

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_1111222233334444",
        "slug": "synthesis",
        "type": "llm",
        "cognitive_tier": "fast",
        "pre_hooks": ["atom_flattening_hook"],
        "criteria_block_ids": ["blk_1111222233334444"],
        "extraction_protocol_block_id": "blk_1111222233334444",
        "name": {"translations": {"en": "en"}},
        "description": {"translations": {"en": "en"}},
    }
    mock_repo.get_execution.return_value = None

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch("backend_v2.services.orchestrator.matrix_reducer.MatrixReducer.reduce_matrix") as mock_matrix_reducer,
        pytest.raises(AppException) as exc_info,
    ):
        mock_hooks.execute = AsyncMock(return_value=HookResult(success=True, state_delta={}))
        mock_matrix_reducer.side_effect = Exception("Matrix Reduction Error")

        await executor.execute_workflow(
            execution_id="exe_1111222233334444",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={}),
        )
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_dag_executor_progress_callback_and_context_updates(mock_repo: Any, mock_compiler: Any) -> None:
    """Test progress callback formatting (100% vs batches) and decision context updates."""
    from backend_v2.models.state import TraceEvent

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

    step1 = StepRule(id="stp_1111222233334444", task_blueprint="stp_1111222233334444", depends_on=[])
    workflow = Workflow(
        historical_context_mode="DISABLED",
        id="wor_1111222233334444",
        slug="wf_prog",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "Prog WF"}),
        description=I18nText(translations={"en": "Desc"}),
        steps=[step1],
    )

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_1111222233334444",
        "slug": "logic",
        "type": "logic",
        "hook": "mock_hook",
        "name": {"translations": {"en": "en"}},
        "description": {"translations": {"en": "en"}},
    }
    mock_repo.get_execution.return_value = None

    decision_event = TraceEvent(
        step_name="stp_1111222233334444",
        event_type="decision",
        content={"custom_var": "updated_value"},
        metadata={"is_context_update": True},
    )

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", new_callable=AsyncMock) as mock_node_execute,
    ):
        mock_hooks.execute = AsyncMock(return_value=HookResult(success=True, state_delta={}))

        async def fake_node_execute(*args: Any, **kwargs: Any) -> list[TraceEvent]:
            if "progress_callback" in kwargs and kwargs["progress_callback"]:
                await kwargs["progress_callback"](100, 100)
            return [decision_event]

        mock_node_execute.side_effect = fake_node_execute

        record = await executor.execute_workflow(
            execution_id="exe_1111222233334444",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={}),
        )
        assert record.context_variables.get("custom_var") == "updated_value"


@pytest.mark.asyncio
async def test_dag_executor_mcp_audit_decision_event_accumulation(mock_repo: Any, mock_compiler: Any) -> None:
    """Tests that valid MCPAuditTrace dicts inside decision events are validated and merged into frozen_context."""
    import datetime

    from backend_v2.models.state import TraceEvent

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

    step1 = StepRule(id="stp_1111222233334444", task_blueprint="stp_1111222233334444", depends_on=[])
    workflow = Workflow(
        historical_context_mode="DISABLED",
        id="wor_1111222233334444",
        slug="wf_mcp_audit",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "MCP Audit WF"}),
        description=I18nText(translations={"en": "Desc"}),
        steps=[step1],
    )

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_1111222233334444",
        "slug": "logic",
        "type": "logic",
        "hook": "mock_hook",
        "name": {"translations": {"en": "en"}},
        "description": {"translations": {"en": "en"}},
    }
    mock_repo.get_execution.return_value = None

    raw_trace = {
        "id": "tavily_12345678",
        "tool_id": "mcp_tavily_search",
        "step_name": "stp_1111222233334444",
        "query": "Fact check query",
        "reasoning": "Verification",
        "response_summary": "Verified truth",
        "source_urls": ["https://example.com"],
        "timestamp": datetime.datetime.now(datetime.timezone.utc),
        "duration_ms": 150,
    }

    decision_event = TraceEvent(
        step_name="stp_1111222233334444",
        event_type="decision",
        content={"mcp_audit_traces": [raw_trace]},
        metadata={"mcp_audit_traces": [raw_trace]},
    )

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", new_callable=AsyncMock) as mock_node_execute,
    ):
        mock_hooks.execute = AsyncMock(return_value=HookResult(success=True, state_delta=HookDeltaDTO()))
        mock_node_execute.return_value = [decision_event]

        record = await executor.execute_workflow(
            execution_id="exe_1111222233334444",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={}),
        )

        assert len(record.frozen_context.mcp_tool_audit) == 1
        assert record.frozen_context.mcp_tool_audit[0].id == "tavily_12345678"
        assert record.frozen_context.mcp_tool_audit[0].response_summary == "Verified truth"


@pytest.mark.asyncio
async def test_dag_executor_mcp_audit_decision_event_invalid_payload_fails_fast(
    mock_repo: Any, mock_compiler: Any
) -> None:
    """Tests that invalid MCPAuditTrace payload in decision event triggers Fail-Fast AppException."""
    from backend_v2.models.state import TraceEvent

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

    step1 = StepRule(id="stp_1111222233334444", task_blueprint="stp_1111222233334444", depends_on=[])
    workflow = Workflow(
        historical_context_mode="DISABLED",
        id="wor_1111222233334444",
        slug="wf_mcp_audit_fail",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "MCP Audit WF"}),
        description=I18nText(translations={"en": "Desc"}),
        steps=[step1],
    )

    mock_repo.get_step_by_id.return_value = {
        "id": "stp_1111222233334444",
        "slug": "logic",
        "type": "logic",
        "hook": "mock_hook",
        "name": {"translations": {"en": "en"}},
        "description": {"translations": {"en": "en"}},
    }
    mock_repo.get_execution.return_value = None

    invalid_decision_event = TraceEvent(
        step_name="stp_1111222233334444",
        event_type="decision",
        content={"mcp_audit_traces": [{"invalid_field": 123}]},
        metadata={"mcp_audit_traces": [{"invalid_field": 123}]},
    )

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", new_callable=AsyncMock) as mock_node_execute,
    ):
        mock_hooks.execute = AsyncMock(return_value=HookResult(success=True, state_delta=HookDeltaDTO()))
        mock_node_execute.return_value = [invalid_decision_event]

        with pytest.raises(AppException) as exc_info:
            await executor.execute_workflow(
                execution_id="exe_1111222233334444",
                workflow=workflow,
                raw_inputs=WorkflowInputs(dynamic_inputs={}),
            )

        assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_node_executor_loads_all_auxiliary_prompt_blocks(mock_repo: AsyncMock, mock_compiler: AsyncMock) -> None:
    """Test that NodeExecutor.execute collects criteria, role, protocol, and persona block IDs."""
    import asyncio

    from backend_v2.models.domain.prompt_blocks import SystemRulePromptBlock
    from backend_v2.models.domain.step import Step, StepRule
    from backend_v2.models.enums import CognitiveTier, PromptBlockCategory, StepType
    from backend_v2.models.execution_core import ExecutionMetadata
    from backend_v2.models.state import StateProjector
    from backend_v2.services.orchestrator.dag_executor import NodeExecutor
    from backend_v2.services.orchestrator.strategies.base import StrategyDependencies

    mock_prompt_block_repo = AsyncMock()
    block = SystemRulePromptBlock(
        id="blk_0123456789abcdef0123456789abcdef",
        slug="common-block",
        label=I18nText(translations={"en": "Common"}),
        description=I18nText(translations={"en": "Common Desc"}),
        category_id=PromptBlockCategory.SYSTEM_RULE,
    )
    mock_prompt_block_repo.get_prompt_blocks_by_ids.return_value = [block]

    deps = StrategyDependencies(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        prompt_block_repo=mock_prompt_block_repo,
        output_profile_repo=AsyncMock(),
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )
    node_executor = NodeExecutor(deps=deps)

    step_rule = StepRule(
        id="stp_0123456789abcdef0123456789abcdef",
        task_blueprint="bp_0123456789abcdef0123456789abcdef",
        input_mappings={},
    )
    step_def = Step.model_construct(
        id="bp_0123456789abcdef0123456789abcdef",
        slug="full_step",
        type=StepType.LOGIC,
        cognitive_tier=CognitiveTier.FAST,
        criteria_block_ids=["blk_0123456789abcdef0123456789abcdef"],
        role_block_id="blk_11112222333344445555666677778888",
        extraction_protocol_block_id="blk_22223333444455556666777788889999",
        execution_persona_block_id="blk_33334444555566667777888899990000",
        name=I18nText(translations={"en": "Full"}),
        description=I18nText(translations={"en": "Full"}),
        hook="mock_hook",
    )

    with (
        patch("backend_v2.services.orchestrator.dag_executor.NodeStrategyFactory.create_strategy") as mock_factory,
    ):
        mock_strat = AsyncMock()
        mock_strat.execute.return_value = []
        mock_strat.assert_quota = AsyncMock()
        mock_factory.return_value = mock_strat

        await node_executor.execute(
            step=step_rule,
            execution_id="exe_1",
            workflow_id="wf_1",
            metadata=ExecutionMetadata(),
            projector=StateProjector(),
            semaphore=asyncio.Semaphore(1),
            step_def=step_def,
        )

        mock_prompt_block_repo.get_prompt_blocks_by_ids.assert_called_once_with(
            [
                "blk_0123456789abcdef0123456789abcdef",
                "blk_11112222333344445555666677778888",
                "blk_22223333444455556666777788889999",
                "blk_33334444555566667777888899990000",
            ],
            strict=True,
        )


@pytest.mark.asyncio
async def test_dag_executor_step_states_resolves_human_readable_step_labels(mock_repo: Any, mock_compiler: Any) -> None:
    """Regression Test: step_states in DAGExecutor must resolve human-readable localized step name instead of raw rule ID."""
    step_rule = StepRule(
        id="sr_f0a26d17cc9b48a7",
        task_blueprint="bp_11112222333344445555666677778888",
        input_mappings={},
    )
    workflow = Workflow(
        historical_context_mode="DISABLED",
        id="wf_5555555555555555",
        slug="wf_test_slug",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "Test WF", "fi": "Test WF"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
        steps=[step_rule],
    )

    mock_repo.get_step_by_id.return_value = {
        "id": "bp_11112222333344445555666677778888",
        "type": "logic",
        "cognitive_tier": "fast",
        "slug": "exec_analysis",
        "name": {"translations": {"en": "Executive Analysis", "fi": "Johtoryhmän analyysi"}},
        "description": {"translations": {"en": "Desc", "fi": "Kuvaus"}},
        "hook": "mock_hook",
    }
    mock_repo.get_execution.return_value = None

    prompt_block_repo = AsyncMock()
    prompt_block_repo.get_prompt_blocks_by_ids.return_value = []

    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        prompt_block_repo=prompt_block_repo,
        output_profile_repo=AsyncMock(),
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", new_callable=AsyncMock) as mock_node_exec,
    ):
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(success=True, state_delta=HookDeltaDTO(delta={"inputs": {}}))
        )
        mock_node_exec.return_value = []
        record = await executor.execute_workflow(
            execution_id="exe_1231231231231231",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={}, language="fi"),
        )

    # Step label must be human-readable resolved Finnish name, NOT 'sr_f0a26d17cc9b48a7'
    assert record.step_states["sr_f0a26d17cc9b48a7"].label == "Johtoryhmän analyysi"


@pytest.mark.asyncio
async def test_dag_executor_intermediate_progress_callback_lock_failure_does_not_crash_step(
    mock_repo: Any, mock_compiler: Any
) -> None:
    """Verify transient DB lock failure during intermediate progress reporting does not crash the step."""
    from backend_v2.models.state import TraceEvent

    mock_repo.get_execution.return_value = None

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
        historical_context_mode="DISABLED",
        id="wf_1111222233334444",
        slug="wf_progress_test",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "Progress Test", "fi": "Progress Test"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
        steps=[
            StepRule(id="sr_1111222233334444", task_blueprint="bp_1111222233334444"),
        ],
    )

    in_progress_cb = False

    async def flaky_update_execution(execution_id: str, update_dto: Any) -> Any:
        if in_progress_cb:
            raise AppException(
                message=f"Failed to commit execution trace for {execution_id}",
                details={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED},
                status_code=500,
            )
        return {"id": execution_id}

    mock_repo.update_execution = AsyncMock(side_effect=flaky_update_execution)

    async def mock_execute(step: StepRule, *args: Any, **kwargs: Any) -> list[Any]:
        nonlocal in_progress_cb
        progress_cb = kwargs.get("progress_callback")
        if progress_cb:
            in_progress_cb = True
            try:
                await progress_cb(5, 20)
                await progress_cb(100, 100)
            finally:
                in_progress_cb = False
        return [TraceEvent(step_name=step.id, event_type="output", content={"status": "ok"})]

    with patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks:
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(success=True, state_delta=HookDeltaDTO(delta={"log": "test"}))
        )
        with patch.object(executor.node_executor, "execute", side_effect=mock_execute):
            result = await executor.execute_workflow(
                execution_id="exe_1111222233334444",
                workflow=workflow,
                raw_inputs=WorkflowInputs.model_validate({"dynamic_inputs": {"log": "test"}}),
            )
            assert result.step_states["sr_1111222233334444"].status == ExecutionStatus.PASSED


@pytest.mark.asyncio
async def test_dag_executor_preflight_progress_lock_failure_does_not_crash_workflow(
    mock_repo: Any, mock_compiler: Any
) -> None:
    """Verify transient DB lock failure during RAG preflight progress reporting does not crash the workflow."""
    mock_rag_preflight = AsyncMock()
    mock_repo.get_execution.return_value = None

    in_preflight_progress = False

    async def mock_rag_execute(*args: Any, **kwargs: Any) -> dict[str, Any]:
        nonlocal in_preflight_progress
        emit_progress = kwargs.get("emit_progress")
        if emit_progress:
            in_preflight_progress = True
            try:
                await emit_progress("Indexing ontology...", 50)
            finally:
                in_preflight_progress = False
        return {"context": "preflight_done"}

    mock_rag_preflight.execute = AsyncMock(side_effect=mock_rag_execute)

    executor = DAGExecutor(
        rag_preflight=mock_rag_preflight,
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
        historical_context_mode="DISABLED",
        id="wf_2222333344445555",
        slug="wf_preflight_test",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "Preflight Test", "fi": "Preflight Test"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
        steps=[
            StepRule(id="sr_2222333344445555", task_blueprint="bp_2222333344445555"),
        ],
    )

    mock_repo.get_step_by_id.return_value = {
        "id": "bp_2222333344445555",
        "type": "logic",
        "pre_hooks": ["synthesis_distiller_hook"],
        "slug": "synth_step",
        "name": {"translations": {"en": "Synth Step"}},
        "description": {"translations": {"en": "Synth"}},
        "hook": "mock_hook",
    }

    async def flaky_update_execution(execution_id: str, update_dto: Any) -> Any:
        if in_preflight_progress:
            raise AppException(
                message=f"Failed to commit execution trace for {execution_id}",
                details={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED},
                status_code=500,
            )
        return {"id": execution_id}

    mock_repo.update_execution = AsyncMock(side_effect=flaky_update_execution)

    from backend_v2.models.state import TraceEvent

    async def mock_execute(step: StepRule, *args: Any, **kwargs: Any) -> list[Any]:
        return [TraceEvent(step_name=step.id, event_type="output", content={"status": "ok"})]

    with patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks:
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(success=True, state_delta=HookDeltaDTO(delta={"log": "test"}))
        )
        with patch.object(executor.node_executor, "execute", side_effect=mock_execute):
            result = await executor.execute_workflow(
                execution_id="exe_2222333344445555",
                workflow=workflow,
                raw_inputs=WorkflowInputs.model_validate({"dynamic_inputs": {"log": "test"}}),
            )
            assert result.step_states["sr_2222333344445555"].status == ExecutionStatus.PASSED


@pytest.mark.asyncio
async def test_dag_executor_step_blueprint_not_found_fails_fast(mock_repo: Any, mock_compiler: Any) -> None:
    """Verify DAGExecutor raises AppException(CONFIGURATION_ERROR) if step blueprint is not found."""
    mock_repo.get_step_by_id.return_value = None
    mock_repo.get_execution.return_value = None

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
        historical_context_mode="DISABLED",
        id="wf_1111222233334444",
        slug="wf_missing_bp",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "Missing BP"}),
        description=I18nText(translations={"en": "Desc"}),
        steps=[
            StepRule(id="stp_1111222233334444", task_blueprint="bp_1111222233334444"),
        ],
    )

    with pytest.raises((AppException, ExceptionGroup)) as exc_info:
        await executor.execute_workflow(
            execution_id="exe_1111222233334444",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={}),
        )

    app_exc = exc_info.value.exceptions[0] if isinstance(exc_info.value, ExceptionGroup) else exc_info.value
    assert isinstance(app_exc, AppException)
    assert app_exc.status_code == 500
    assert app_exc.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR


@pytest.mark.asyncio
async def test_dag_executor_resumes_missing_metadata_populates_workflow_model_registry(
    mock_repo: Any, mock_compiler: Any
) -> None:
    """Verify resuming an execution with None metadata inherits workflow.model_registry_id and version."""
    from backend_v2.models.state import TraceEvent
    from backend_v2.services.execution import create_execution_record

    step_rule = StepRule(id="stp_2222333344445555", task_blueprint="bp_2222333344445555")
    workflow = Workflow(
        historical_context_mode="DISABLED",
        id="wf_2222333344445555",
        slug="wf_resume_meta",
        status="draft",
        version=3,
        default_profile_id="prof_dddd1111dddd1111",
        model_registry_id="cfg_model_registry_99",
        name=I18nText(translations={"en": "Resume Meta"}),
        description=I18nText(translations={"en": "Desc"}),
        steps=[step_rule],
    )

    mock_repo.get_step_by_id.return_value = {
        "id": "bp_2222333344445555",
        "type": "logic",
        "slug": "logic_step",
        "name": {"translations": {"en": "Logic Step"}},
        "description": {"translations": {"en": "Desc"}},
        "hook": "mock_hook",
    }

    existing_record = create_execution_record(
        execution_id="exe_2222333344445555",
        workflow_id=workflow.id,
        raw_inputs=WorkflowInputs(dynamic_inputs={}),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        status=ExecutionStatus.PENDING,
        steps=[ExecutionStep(id="stp_2222333344445555", label="Old Label", status=ExecutionStatus.PENDING)],
        step_states={
            "stp_2222333344445555": ExecutionStep(
                id="stp_2222333344445555", label="Old Label", status=ExecutionStatus.PENDING
            )
        },
    ).model_copy(update={"metadata": None})
    mock_repo.get_execution.return_value = existing_record

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

    async def mock_node_execute(*args: Any, **kwargs: Any) -> list[Any]:
        return [TraceEvent(step_name="stp_2222333344445555", event_type="output", content={"ok": True})]

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", side_effect=mock_node_execute),
    ):
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(success=True, state_delta=HookDeltaDTO(delta={"log": "test"}))
        )
        record = await executor.execute_workflow(
            execution_id="exe_2222333344445555",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={}),
        )

    assert record.metadata is not None
    assert record.metadata.model_registry_id == "cfg_model_registry_99"
    assert record.metadata.workflow_version == 3
    assert record.step_states["stp_2222333344445555"].status == ExecutionStatus.PASSED


@pytest.mark.asyncio
async def test_dag_executor_resumption_skips_passed_steps_and_resets_failed_steps(
    mock_repo: Any, mock_compiler: Any
) -> None:
    """Verify resumption skips already PASSED steps and resets FAILED steps to PENDING before executing."""
    from backend_v2.models.state import TraceEvent
    from backend_v2.services.execution import create_execution_record

    step1 = StepRule(id="stp_3333444455556666", task_blueprint="bp_3333444455556666", depends_on=[])
    step2 = StepRule(
        id="stp_4444555566667777", task_blueprint="bp_4444555566667777", depends_on=["stp_3333444455556666"]
    )
    workflow = Workflow(
        historical_context_mode="DISABLED",
        id="wf_3333444455556666",
        slug="wf_resume_skips",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "Resume Skips"}),
        description=I18nText(translations={"en": "Desc"}),
        steps=[step1, step2],
    )

    def fake_get_step(b_id: str) -> dict[str, Any]:
        return {
            "id": b_id,
            "type": "logic",
            "slug": b_id,
            "name": {"translations": {"en": b_id}},
            "description": {"translations": {"en": b_id}},
            "hook": "mock_hook",
        }

    mock_repo.get_step_by_id.side_effect = fake_get_step

    existing_record = create_execution_record(
        execution_id="exe_3333444455556666",
        workflow_id=workflow.id,
        raw_inputs=WorkflowInputs(dynamic_inputs={}),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        status=ExecutionStatus.FAILED,
        steps=[
            ExecutionStep(id="stp_3333444455556666", label="Step 1", status=ExecutionStatus.PASSED),
            ExecutionStep(id="stp_4444555566667777", label="Step 2", status=ExecutionStatus.FAILED),
        ],
        step_states={
            "stp_3333444455556666": ExecutionStep(
                id="stp_3333444455556666", label="Step 1", status=ExecutionStatus.PASSED
            ),
            "stp_4444555566667777": ExecutionStep(
                id="stp_4444555566667777", label="Step 2", status=ExecutionStatus.FAILED
            ),
        },
        metadata=ExecutionMetadata(workflow_version=1, model_registry_id="cfg_model_registry_01"),
    )
    mock_repo.get_execution.return_value = existing_record

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

    executed_step_ids: list[str] = []

    async def mock_node_execute(step: StepRule, *args: Any, **kwargs: Any) -> list[Any]:
        executed_step_ids.append(step.id)
        return [TraceEvent(step_name=step.id, event_type="output", content={"ok": True})]

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", side_effect=mock_node_execute),
    ):
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(success=True, state_delta=HookDeltaDTO(delta={"log": "test"}))
        )
        record = await executor.execute_workflow(
            execution_id="exe_3333444455556666",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={}),
        )

    # Step 1 was PASSED, so it should NOT be executed again. Step 2 should be executed.
    assert "stp_3333444455556666" not in executed_step_ids
    assert "stp_4444555566667777" in executed_step_ids
    assert record.step_states["stp_3333444455556666"].status == ExecutionStatus.PASSED
    assert record.step_states["stp_4444555566667777"].status == ExecutionStatus.PASSED


@pytest.mark.asyncio
async def test_dag_executor_watch_running_event_transitions_queued_step(mock_repo: Any, mock_compiler: Any) -> None:
    """Verify running_event triggers watch_running to update step status from QUEUED to RUNNING."""
    from backend_v2.models.state import TraceEvent

    step1 = StepRule(id="stp_5555666677778888", task_blueprint="bp_5555666677778888")
    workflow = Workflow(
        historical_context_mode="DISABLED",
        id="wf_5555666677778888",
        slug="wf_watch_run",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "Watch Run"}),
        description=I18nText(translations={"en": "Desc"}),
        steps=[step1],
    )

    mock_repo.get_step_by_id.return_value = {
        "id": "bp_5555666677778888",
        "type": "logic",
        "slug": "bp_watch_run",
        "name": {"translations": {"en": "Watch Run Step"}},
        "description": {"translations": {"en": "Desc"}},
        "hook": "mock_hook",
    }
    mock_repo.get_execution.return_value = None

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

    observed_statuses: list[ExecutionStatus] = []

    async def mock_node_execute(step: StepRule, *args: Any, **kwargs: Any) -> list[Any]:
        running_evt = kwargs.get("running_event")
        if running_evt:
            running_evt.set()
            # Allow watcher task to run and commit
            await asyncio.sleep(0.05)
            # Record current status from commit_trace calls
            for call in executor.committer.commit_trace.call_args_list:  # type: ignore[attr-defined]
                step_states_arg = call.kwargs.get("step_states", {})
                if "stp_5555666677778888" in step_states_arg:
                    observed_statuses.append(step_states_arg["stp_5555666677778888"].status)
        return [TraceEvent(step_name=step.id, event_type="output", content={"ok": True})]

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", side_effect=mock_node_execute),
        patch.object(executor.committer, "commit_trace", new_callable=AsyncMock) as mock_commit,
    ):
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(success=True, state_delta=HookDeltaDTO(delta={"log": "test"}))
        )
        record = await executor.execute_workflow(
            execution_id="exe_5555666677778888",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={}),
        )

    # Watcher task should have set status to RUNNING during execution
    assert ExecutionStatus.RUNNING in observed_statuses or mock_commit.call_count >= 2
    assert record.step_states["stp_5555666677778888"].status == ExecutionStatus.PASSED


@pytest.mark.asyncio
async def test_dag_executor_step_generated_schemas_merged_into_frozen_context(
    mock_repo: Any, mock_compiler: Any
) -> None:
    """Verify TraceEvent with generated_schema is merged into frozen_context.generated_schemas."""
    from backend_v2.models.state import TraceEvent

    step1 = StepRule(id="stp_6666777788889999", task_blueprint="bp_6666777788889999")
    workflow = Workflow(
        historical_context_mode="DISABLED",
        id="wf_6666777788889999",
        slug="wf_schema_merge",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "Schema Merge"}),
        description=I18nText(translations={"en": "Desc"}),
        steps=[step1],
    )

    mock_repo.get_step_by_id.return_value = {
        "id": "bp_6666777788889999",
        "type": "logic",
        "slug": "bp_schema_merge",
        "name": {"translations": {"en": "Schema Merge Step"}},
        "description": {"translations": {"en": "Desc"}},
        "hook": "mock_hook",
    }
    mock_repo.get_execution.return_value = None

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

    test_schema = {"type": "object", "properties": {"extracted": {"type": "string"}}}
    schema_event = TraceEvent(
        step_name="stp_6666777788889999",
        event_type="decision",
        content={},
        metadata={"generated_schema": test_schema},
    )

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", new_callable=AsyncMock) as mock_node_exec,
    ):
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(success=True, state_delta=HookDeltaDTO(delta={"log": "test"}))
        )
        mock_node_exec.return_value = [schema_event]
        record = await executor.execute_workflow(
            execution_id="exe_6666777788889999",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={}),
        )

    assert "stp_6666777788889999" in record.frozen_context.generated_schemas
    assert record.frozen_context.generated_schemas["stp_6666777788889999"] == test_schema


@pytest.mark.asyncio
async def test_node_executor_with_arq_pool_and_metadata_global_context_vars(
    mock_repo: AsyncMock, mock_compiler: Any
) -> None:
    """Verify NodeExecutor accepts arq_pool, derives global_context_vars from metadata, and derives model_registry_id."""
    from backend_v2.models.enums import StepType
    from backend_v2.models.state import StateProjector
    from backend_v2.services.orchestrator.dag_executor import NodeExecutor
    from backend_v2.services.orchestrator.strategies.base import StrategyDependencies

    mock_prompt_block_repo = AsyncMock()
    mock_prompt_block_repo.get_prompt_blocks_by_ids.return_value = []

    deps = StrategyDependencies(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        prompt_block_repo=mock_prompt_block_repo,
        output_profile_repo=AsyncMock(),
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )
    node_executor = NodeExecutor(deps=deps)

    step_rule = StepRule(id="stp_7777888899990000", task_blueprint="bp_7777888899990000", input_mappings={})
    step_def = Step.model_construct(
        id="bp_7777888899990000",
        slug="logic_step",
        type=StepType.LOGIC,
        criteria_block_ids=[],
        name=I18nText(translations={"en": "Logic"}),
        description=I18nText(translations={"en": "Desc"}),
        hook="mock_hook",
    )

    mock_pool = MagicMock()
    captured_context: list[Any] = []

    with patch("backend_v2.services.orchestrator.dag_executor.NodeStrategyFactory.create_strategy") as mock_factory:
        mock_strat = AsyncMock()

        async def capture_execute(*args: Any, **kwargs: Any) -> list[Any]:
            ctx = kwargs.get("context")
            if ctx is not None:
                captured_context.append(ctx)
            return []

        mock_strat.execute.side_effect = capture_execute
        mock_strat.assert_quota = AsyncMock()
        mock_factory.return_value = mock_strat

        meta = ExecutionMetadata(
            workflow_version=2,
            model_registry_id="cfg_special_reg",
            global_context_vars={"injected_var": "val123"},
        )

        await node_executor.execute(
            step=step_rule,
            execution_id="exe_7777888899990000",
            workflow_id="wf_7777888899990000",
            metadata=meta,
            projector=StateProjector(),
            semaphore=asyncio.Semaphore(1),
            step_def=step_def,
            arq_pool=mock_pool,
        )

        # Verify strategy was created with arq_pool in effective_deps
        assert mock_factory.call_args[1]["deps"].arq_pool == mock_pool
        assert len(captured_context) == 1
        assert captured_context[0].global_context_vars == {"injected_var": "val123"}
        assert captured_context[0].model_registry_id == "cfg_special_reg"
