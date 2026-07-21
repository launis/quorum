from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import backend_v2.llm.client
from backend_v2.core.hook_registry import HookResult
from backend_v2.models.v2_core import ExecutionStatus, I18nText, Step, StepRule, Workflow, WorkflowInputs
from backend_v2.services.orchestrator.dag_executor import DAGExecutor
from backend_v2.services.orchestrator.rag_preflight_service import RAGPreflightService


@pytest.fixture
def mock_repo() -> MagicMock:
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
def mock_compiler() -> MagicMock:
    return MagicMock()


@pytest.mark.asyncio
async def test_dag_executor_preflight_skip(mock_repo: MagicMock, mock_compiler: MagicMock) -> None:
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
        historical_context_mode="DISABLED",
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
    ):
        mock_hooks.execute = AsyncMock(return_value=HookResult(success=True, state_delta={"inputs": {}}))

        await executor.execute_workflow(
            execution_id="exe_1234567890abcdef",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={"k": "v"}),
        )

        executor.rag_preflight.execute.assert_not_called()


@pytest.mark.asyncio
async def test_dag_executor_preflight_execution(mock_repo: MagicMock, mock_compiler: MagicMock) -> None:
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
        historical_context_mode="DISABLED",
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
            )
        ],
    )

    mock_repo.get_execution.return_value = None
    mock_repo.get_step_by_id.return_value["model_strategy"] = "synthesis"

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", new_callable=AsyncMock),
    ):
        mock_hooks.execute = AsyncMock(return_value=HookResult(success=True, state_delta={"inputs": {}}))
        executor.rag_preflight.execute.return_value = {"atoms_by_input": {}}

        record = await executor.execute_workflow(
            execution_id="exe_1234567890abcdef",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={"k": "v"}),
        )

        executor.rag_preflight.execute.assert_called_once()
        assert "__GLOBAL_ATOM_BLACKBOARD__" in record.context_variables


@pytest.mark.asyncio
async def test_dag_executor_preflight_triggered_by_model_strategy(
    mock_repo: MagicMock, mock_compiler: MagicMock
) -> None:
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
        historical_context_mode="DISABLED",
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
            )
        ],
    )

    mock_repo.get_execution.return_value = None
    mock_repo.get_step_by_id.return_value = {
        "id": "blp_1234567890abcdef",
        "type": "logic",
        "model_strategy": "synthesis",
        "slug": "synthesis_step",
        "name": {"default_locale": "en", "translations": {"en": "Synth"}},
        "description": {"default_locale": "en", "translations": {"en": "Mock"}},
        "hook": "mock_hook",
    }

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", new_callable=AsyncMock),
    ):
        mock_hooks.execute = AsyncMock(return_value=HookResult(success=True, state_delta={"inputs": {}}))
        executor.rag_preflight.execute.return_value = {"atoms_by_input": {}}

        record = await executor.execute_workflow(
            execution_id="exe_1234567890abcdef",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={"k": "v"}),
        )

        executor.rag_preflight.execute.assert_called_once()
        assert "__GLOBAL_ATOM_BLACKBOARD__" in record.context_variables


@pytest.mark.asyncio
async def test_dag_executor_virtual_step(mock_repo: MagicMock, mock_compiler: MagicMock) -> None:
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
        historical_context_mode="DISABLED",
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
            )
        ],
    )

    mock_repo.get_execution.return_value = None
    mock_repo.get_step_by_id.return_value["model_strategy"] = "synthesis"

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", new_callable=AsyncMock),
    ):
        mock_hooks.execute = AsyncMock(return_value=HookResult(success=True, state_delta={"inputs": {}}))
        executor.rag_preflight.execute.return_value = {"atoms_by_input": {}}

        record = await executor.execute_workflow(
            execution_id="exe_1234567890abcdef",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={"k": "v"}),
        )

        virtual_steps = [s for k, s in record.step_states.items() if s.label == "system.rag.preflight"]
        assert len(virtual_steps) == 1
        assert virtual_steps[0].status == ExecutionStatus.PASSED


@pytest.mark.asyncio
async def test_dag_executor_preflight_ignores_system_keys(mock_repo: MagicMock, mock_compiler: MagicMock) -> None:
    executor = DAGExecutor(
        rag_preflight=RAGPreflightService(
            system_repo=mock_repo, prompt_compiler=mock_compiler, workflow_repo=mock_repo
        ),
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

    from backend_v2.models.v2_core import ExecutionRecord

    workflow = Workflow(
        allowed_exports=["pdf"],
        historical_context_mode="DISABLED",
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
            )
        ],
    )

    mock_repo.get_execution.return_value = None
    mock_repo.get_step_by_id = AsyncMock(
        return_value={
            "id": "stp_1234567890abcdef",
            "slug": "blp_test",
            "name": {"default_locale": "en", "translations": {"en": "blp_test"}},
            "model_strategy": "fast",
            "criteria_block_ids": ["blk_1234567890abcdef"],
            "extraction_protocol_block_id": "blk_1234567890abcdef",
            "type": "llm",
        }
    )

    exec_record = ExecutionRecord(
        id="exe_1234567890abcdef",
        workflow_id="wf_1234567890abcdef",
        raw_inputs=WorkflowInputs(language="en", dynamic_inputs={"product_text": "This is valid document text."}),
    )

    from backend_v2.models.domain.blackboard import DraftAtomList

    with (
        patch("backend_v2.llm.client.LLMClient.from_strategy"),
        patch("backend_v2.services.orchestrator.rag_preflight_service.TwoPassAtomizer") as mock_atomizer_cls,
    ):
        mock_atomizer = mock_atomizer_cls.return_value
        mock_client = AsyncMock()
        mock_client._config.provider = "openai"
        mock_client.run_structured_task = AsyncMock(
            return_value=(MagicMock(), {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0})
        )
        backend_v2.llm.client.LLMClient.from_strategy.return_value = mock_client
        mock_atomizer.execute_phase_0 = AsyncMock(return_value={})
        mock_atomizer.execute_phase_1_drafts = AsyncMock(return_value=DraftAtomList(atoms=[]))

        await executor.rag_preflight.execute(
            target_step=workflow.steps[0],
            step_def=Step.model_validate(mock_repo.get_step_by_id.return_value),
            exec_record=exec_record,
            emit_progress=AsyncMock(),
        )

        # It should ONLY process dynamic_inputs, not system keys like 'language'
        # Currently, it processes 'en' and then crashes.
        calls = mock_atomizer.execute_phase_0.call_args_list
        # Extract the text chunks passed to execute_phase_0
        processed_chunks = [call.args[1] for call in calls]

        assert len(processed_chunks) == 1
        assert processed_chunks[0] == "[B0] This is valid document text."
