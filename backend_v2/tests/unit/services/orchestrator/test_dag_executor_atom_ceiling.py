from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.core.hook_registry import HookResult
from backend_v2.exceptions import AppException
from backend_v2.models.domain.blackboard import DraftAtomList, DraftExtractedAtom
from backend_v2.models.v2_core import (
    I18nText,
    ModelProfile,
    StepRule,
    SystemConfigModelRegistry,
    Workflow,
    WorkflowInputs,
)
from backend_v2.services.orchestrator.dag_executor import DAGExecutor


@pytest.fixture
def mock_repo() -> MagicMock:
    return AsyncMock()


@pytest.fixture
def mock_compiler() -> MagicMock:
    compiler = MagicMock()
    compiler.compile_llm_prompt = AsyncMock(
        return_value="This is a sufficiently long mocked prompt to pass the fail-fast check"
    )
    compiler.compile_prompt_block = AsyncMock(
        return_value="This is a sufficiently long mocked prompt to pass the fail-fast check"
    )
    return compiler


@pytest.mark.asyncio
async def test_dag_executor_atom_ceiling(mock_repo: MagicMock, mock_compiler: MagicMock) -> None:
    executor = DAGExecutor(rag_preflight=AsyncMock(), 
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

    mock_repo.update_execution = AsyncMock()

    mock_repo.get_execution.return_value = None

    mock_repo.get_system_config_model_registry = AsyncMock()
    model_registry_data = SystemConfigModelRegistry(
        id="sys_1234567890abcdef",
        type="model_registry",
        slug="models",
        models={
            "test_strategy": ModelProfile(
                provider="openai", model_name="gpt-4o", tpm_limit=40000, rpm_limit=100, temperature=0.0, max_tokens=4000
            )
        },
    ).model_dump(mode="json")
    mock_repo.get_system_config_model_registry.return_value = model_registry_data
    mock_repo.get_model_registry = AsyncMock()
    mock_repo.get_model_registry.return_value = model_registry_data
    mock_repo.get_step_by_id.return_value = {
        "id": "blp_1234567890abcdef",
        "slug": "test_step",
        "organization_id": "org_1",
        "name": {"default_locale": "en", "translations": {"en": "test"}},
        "description": {"default_locale": "en", "translations": {"en": "test"}},
        "type": "llm",
        "criteria_block_ids": ["blk_1234567890abcdef"],
        "extraction_protocol_block_id": "blk_1234567890abcdef",
        "model_strategy": "test_strategy",
    }

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", new_callable=AsyncMock),
        patch("backend_v2.services.orchestrator.two_pass_atomizer.TwoPassAtomizer") as mock_atomizer_class,
        patch("backend_v2.services.orchestrator.dag_executor.get_settings") as mock_settings,
    ):
        mock_hooks.execute = AsyncMock(return_value=HookResult(success=True, state_delta={"inputs": {}}))

        mock_settings.return_value.max_extracted_atoms_per_document = 2
        mock_settings.return_value.schema_max_evaluations = 100
        mock_settings.return_value.max_concurrent_llm_steps = 5
        mock_settings.return_value.rag_preflight_chunk_size = 12000
        mock_settings.return_value.max_development_chunks = 0

        mock_atomizer = mock_atomizer_class.return_value
        mock_atomizer.execute_phase_0 = AsyncMock()

        atoms = [
            DraftExtractedAtom(reasoning="1", resolved_claim="1", draft_id="a1", is_logical_deduction=True),
            DraftExtractedAtom(reasoning="2", resolved_claim="2", draft_id="a2", is_logical_deduction=True),
            DraftExtractedAtom(reasoning="3", resolved_claim="3", draft_id="a3", is_logical_deduction=True),
        ]
        mock_atomizer.execute_phase_1_drafts = AsyncMock(return_value=DraftAtomList(atoms=atoms))

        with pytest.raises(AppException) as exc_info:
            await executor.execute_workflow(
                execution_id="exe_1234567890abcdef",
                workflow=workflow,
                raw_inputs=WorkflowInputs(dynamic_inputs={"doc_1": "test"}),
            )

        assert exc_info.value.status_code == 500  # DAGExecutor wraps inner 400 with 500 workflow execution failed
        assert "Atom ceiling exceeded" in exc_info.value.message
