from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.core.hook_registry import HookResult
from backend_v2.models.enums import EngineOverrideStrategy
from backend_v2.models.v2_core import ExecutionStatus, I18nText, StepRule, Workflow, WorkflowInputs
from backend_v2.services.orchestrator.dag_executor import DAGExecutor


@pytest.fixture
def mock_repo() -> MagicMock:
    return AsyncMock()


@pytest.fixture
def mock_compiler() -> MagicMock:
    return MagicMock()


@pytest.mark.asyncio
async def test_dag_executor_preflight_skip(mock_repo: MagicMock, mock_compiler: MagicMock) -> None:
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
    )

    workflow = Workflow(
        id="wf_1234567890abcdef",
        slug="test",
        status="draft",
        version=1,
        default_profile_id="prof_1234567890abcde",
        name=I18nText(default_locale="en", translations={"en": "test"}),
        description=I18nText(default_locale="en", translations={"en": "test"}),
        steps=[
            StepRule(id="stp_1234567890abcdef", task_blueprint="blp_1234567890abcdef", input_mappings={}, depends_on=[])
        ],
    )

    mock_repo.get_execution.return_value = None

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", new_callable=AsyncMock),
        patch.object(executor, "_execute_rag_preflight", new_callable=AsyncMock) as mock_preflight,
    ):
        mock_hooks.execute = AsyncMock(return_value=HookResult(success=True, state_delta={"inputs": {}}))

        await executor.execute_workflow(
            execution_id="exe_1234567890abcdef",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={"k": "v"}),
        )

        mock_preflight.assert_not_called()


@pytest.mark.asyncio
async def test_dag_executor_preflight_execution(mock_repo: MagicMock, mock_compiler: MagicMock) -> None:
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
    )

    workflow = Workflow(
        id="wf_1234567890abcdef",
        slug="test",
        status="draft",
        version=1,
        default_profile_id="prof_1234567890abcde",
        name=I18nText(default_locale="en", translations={"en": "test"}),
        description=I18nText(default_locale="en", translations={"en": "test"}),
        steps=[
            StepRule(
                id="stp_1234567890abcdef",
                task_blueprint="blp_1234567890abcdef",
                input_mappings={},
                depends_on=[],
                engine_override=EngineOverrideStrategy.PRE_HYDRATED_SYNTHESIS,
            )
        ],
    )

    mock_repo.get_execution.return_value = None

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", new_callable=AsyncMock),
        patch.object(executor, "_execute_rag_preflight", new_callable=AsyncMock) as mock_preflight,
    ):
        mock_hooks.execute = AsyncMock(return_value=HookResult(success=True, state_delta={"inputs": {}}))
        mock_preflight.return_value = {"atoms_by_input": {}}

        record = await executor.execute_workflow(
            execution_id="exe_1234567890abcdef",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={"k": "v"}),
        )

        mock_preflight.assert_called_once()
        assert "__GLOBAL_ATOM_BLACKBOARD__" in record.context_variables


@pytest.mark.asyncio
async def test_dag_executor_virtual_step(mock_repo: MagicMock, mock_compiler: MagicMock) -> None:
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
    )

    workflow = Workflow(
        id="wf_1234567890abcdef",
        slug="test",
        status="draft",
        version=1,
        default_profile_id="prof_1234567890abcde",
        name=I18nText(default_locale="en", translations={"en": "test"}),
        description=I18nText(default_locale="en", translations={"en": "test"}),
        steps=[
            StepRule(
                id="stp_1234567890abcdef",
                task_blueprint="blp_1234567890abcdef",
                input_mappings={},
                depends_on=[],
                engine_override=EngineOverrideStrategy.PRE_HYDRATED_SYNTHESIS,
            )
        ],
    )

    mock_repo.get_execution.return_value = None

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", new_callable=AsyncMock),
        patch.object(executor, "_execute_rag_preflight", new_callable=AsyncMock) as mock_preflight,
    ):
        mock_hooks.execute = AsyncMock(return_value=HookResult(success=True, state_delta={"inputs": {}}))
        mock_preflight.return_value = {"atoms_by_input": {}}

        record = await executor.execute_workflow(
            execution_id="exe_1234567890abcdef",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={"k": "v"}),
        )

        virtual_steps = [s for k, s in record.step_states.items() if s.label == "system.rag.preflight"]
        assert len(virtual_steps) == 1
        assert virtual_steps[0].status == ExecutionStatus.PASSED
