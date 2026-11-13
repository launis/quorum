"""Unit tests verifying DAGExecutor resolves prompt blocks from IPromptBlockRepository."""

from __future__ import annotations

from typing import Annotated
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel, Field

from backend_v2.core.hook_registry import HookDeltaDTO, HookResult
from backend_v2.exceptions import AppException
from backend_v2.llm.client import LLMClient
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.prompt_blocks import PromptBlockAdapter
from backend_v2.models.domain.step import StepRule
from backend_v2.models.domain.system_config import ModelProfile, SystemConfigModelRegistry
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.dtos.hook_delta import ProjectedResultsDTO
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO
from backend_v2.models.enums import (
    BlockDataType,
    CognitiveTier,
    ExecutionStatus,
    HistoricalContextMode,
    LLMProvider,
)
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import StateProjector
from backend_v2.services.orchestrator.dag_executor import DAGExecutor
from backend_v2.tests.factories.model_factories import (
    ExecutionRecordFactory,
    WorkflowFactory,
)
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


class ModelProfileFactory(ModelFactory[ModelProfile]):
    """Polyfactory model factory for ModelProfile configurations."""

    __model__ = ModelProfile


class MockSchema(BaseModel):
    """Dynamic schema stub returned by the mocked prompt compiler."""

    blk_0195f3a00000700c8def0123456789ab: Annotated[str | None, Field(description="Test block value.")] = None


@pytest.fixture
def mock_repo() -> InMemoryUnifiedWorkflowRepository:
    """Create an in-memory unified repository seeded with prompt blocks and workflow definitions.

    Returns:
        Seeded InMemoryUnifiedWorkflowRepository instance.
    """
    repo = InMemoryUnifiedWorkflowRepository()

    prompt_blocks = [
        PromptBlockAdapter.validate_python(
            {
                "organization_id": "org_0195f3a0000070008000000000000001",
                "id": "blk_0195f3a00000700c8def0123456789ab",
                "slug": "task_bp",
                "label": {"translations": {"fi": "Testi", "en": "Test"}},
                "description": {"translations": {"fi": "Kuvaus", "en": "Desc"}},
                "category_id": "system_rule",
                "type": BlockDataType.STRING,
                "allow_decimals": False,
                "output_extensions": [],
            }
        ),
        PromptBlockAdapter.validate_python(
            {
                "organization_id": "org_0195f3a0000070008000000000000001",
                "id": "blk_0195f3a000007005873802341db9d68c",
                "slug": "zero_trust_extraction_protocol",
                "category_id": "system_rule",
                "type": BlockDataType.STRING,
                "label": {"translations": {"en": "Zero-Trust", "fi": "Zero-Trust"}},
                "description": {"translations": {"en": "Zero-Trust", "fi": "Zero-Trust"}},
                "instruction_text": "Strict extraction protocol.",
                "allow_decimals": False,
                "output_extensions": [],
            }
        ),
    ]
    repo.set_prompt_blocks(prompt_blocks)
    step_def = {
        "organization_id": "org_0195f3a0000070008000000000000001",
        "id": "stp_0195f3a0000070018111111111111111",
        "slug": "task_bp",
        "name": {"translations": {"fi": "Vaihe", "en": "Step"}},
        "role_block_id": None,
        "extraction_protocol_block_id": "blk_0195f3a000007005873802341db9d68c",
        "criteria_block_ids": ["blk_0195f3a00000700c8def0123456789ab"],
        "cognitive_tier": "reasoning",
        "pre_hooks": [],
    }
    repo.set_step(step_def)
    repo.seed_raw_step("task_bp", step_def)
    repo.set_workflow(
        {
            "organization_id": "org_0195f3a0000070008000000000000001",
            "id": "wf_0195f3a0000070058555555555555555",
            "slug": "wf_test_slug",
            "status": "draft",
            "version": 1,
            "default_profile_id": "prof_0195f3a00000700d8ddd1111dddd1111",
            "historical_context_mode": "DISABLED",
            "model_registry_id": "mrg_0195f3a00000700e826807f3bfa3454d",
            "name": {"translations": {"en": "Test WF", "fi": "Test WF"}},
            "description": {"translations": {"en": "Desc", "fi": "Desc"}},
            "steps": [{"id": "stp_0195f3a0000070018111111111111111", "task_blueprint": "task_bp"}],
        }
    )
    repo.set_output_profiles(
        [
            {
                "organization_id": "org_0195f3a0000070008000000000000001",
                "id": "prof_0195f3a00000700d8ddd1111dddd1111",
                "slug": "test_profile",
                "workflow_id": "wf_0195f3a0000070058555555555555555",
                "name": {"translations": {"en": "Test Profile"}},
                "visible_block_extensions": [],
                "visible_workflow_extensions": [],
                "matrix_synthesis_groups": [
                    {
                        "id": "grp_0195f3a0000070008000000000000001",
                        "title": {"translations": {"en": "Default"}},
                        "target_blocks": ["*"],
                    }
                ],
            }
        ]
    )
    tier_profile = ModelProfileFactory.build(
        provider=LLMProvider.OPENAI,
        model_name="gpt-4o-mini",
        tpm_limit=100000,
        rpm_limit=1000,
        max_tokens=4096,
        temperature=0.0,
        is_active=True,
        allowed_tools=[],
        additional_params={},
    )
    model_reg = SystemConfigModelRegistry(
        id="mrg_0195f3a00000700e826807f3bfa3454d",
        name="Default Stack",
        slug="default",
        default_provider=LLMProvider.OPENAI,
        tier_definitions={
            tier: tier_profile
            for tier in (
                CognitiveTier.FAST,
                CognitiveTier.BALANCED,
                CognitiveTier.DEEP,
                CognitiveTier.REASONING,
            )
        },
    )
    repo.set_model_registry(model_reg)
    return repo


@pytest.fixture
def mock_compiler() -> MagicMock:
    """Create a mocked prompt compiler returning MockSchema.

    Returns:
        Configured MagicMock prompt compiler.
    """
    MockSchema.model_rebuild()

    compiler = MagicMock()
    compiler.build_xml_context.return_value = "<test>context</test>"
    compiler.build_dynamic_schema.return_value = MockSchema
    compiler.compile_static_instructions.return_value = "static instructions"

    return compiler


@pytest.mark.asyncio
async def test_dag_executor_uses_prompt_blocks_instead_of_matrices(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    mock_compiler: MagicMock,
) -> None:
    """Verify DAGExecutor fetches prompt blocks via get_prompt_blocks_by_ids and projects output.

    Args:
        mock_repo: Seeded in-memory repository fixture.
        mock_compiler: Mocked prompt compiler fixture.
    """
    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        prompt_block_repo=mock_repo,
        output_profile_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )

    workflow = WorkflowFactory.build(
        historical_context_mode=HistoricalContextMode.DISABLED,
        model_registry_id="mrg_0195f3a00000700e826807f3bfa3454d",
        id="wf_0195f3a0000070058555555555555555",
        slug="wf_test_slug",
        status="draft",
        version=1,
        default_profile_id="prof_0195f3a00000700d8ddd1111dddd1111",
        name=I18nText(translations={"en": "Test WF", "fi": "Test WF"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
        expected_inputs=[],
        steps=[
            StepRule(
                id="stp_0195f3a0000070018111111111111111",
                task_blueprint="task_bp",
                depends_on=[],
                input_mappings={},
            )
        ],
    )

    input_str = "this_is_a_very_long_test_string_to_bypass_fail_fast"

    with patch("backend_v2.llm.client.LLMClient.from_tier", new_callable=AsyncMock) as mock_tier:
        mock_bound_client = AsyncMock(spec=LLMClient)
        mock_bound_client._config = MagicMock()
        mock_bound_client._config.provider = "mock_llm_99"

        mock_schema_cls = mock_compiler.build_dynamic_schema.return_value
        mock_bound_client.run_structured_task.return_value = (
            mock_schema_cls(blk_0195f3a00000700c8def0123456789ab="test"),
            TokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
        )

        mock_tier.return_value = mock_bound_client

        with (
            patch(
                "backend_v2.services.orchestrator.two_pass_atomizer.TwoPassAtomizer.execute_phase_0",
                new_callable=AsyncMock,
            ) as mock_phase_0,
            patch(
                "backend_v2.services.orchestrator.two_pass_atomizer.TwoPassAtomizer.execute_phase_1",
                new_callable=AsyncMock,
            ) as mock_phase_1,
            patch(
                "backend_v2.services.orchestrator.sliding_window_linker.SlidingWindowLinker.link_graph",
                new_callable=AsyncMock,
            ) as mock_link,
            patch(
                "backend_v2.services.orchestrator.enriched_dag_executor.EnrichedDagExecutor.execute_graph",
                new_callable=AsyncMock,
            ) as mock_execute_graph,
            patch("backend_v2.services.orchestrator.result_projector.ResultProjector.project") as mock_project,
        ):
            mock_phase_0.return_value = MagicMock()
            mock_phase_1.return_value = MagicMock()
            mock_link.return_value = MagicMock()
            mock_execute_graph.return_value = MagicMock()

            mock_project.return_value = ProjectedResultsDTO(
                results=[
                    AtomResultDTO(
                        tda_id="blk_0195f3a00000700c8def0123456789ab",
                        status=ExecutionStatus.PASSED,
                        contextual_override=True,
                        source_quotes=None,
                        evaluation_reasoning="Because",
                        extensions={},
                        depends_on_tda_ids=[],
                        short_circuit_reason_tda_ids=[],
                    )
                ],
                hydrated_references={},
            )

            mock_repo.set_execution(
                ExecutionRecordFactory.build(
                    id="exe_0195f3a0000070018231231231231231",
                    workflow_id="wf_0195f3a0000070058555555555555555",
                    status=ExecutionStatus.PENDING,
                    target_locale="fi",
                    output_profile_id="prof_0195f3a00000700d8ddd1111dddd1111",
                    raw_inputs=WorkflowInputs(dynamic_inputs={"chat_log": input_str}),
                    metadata=ExecutionMetadata(),
                )
            )

            with patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks:
                mock_hooks.execute = AsyncMock(
                    return_value=HookResult(
                        success=True,
                        state_delta=HookDeltaDTO(
                            delta=ExecutionInputsDTO(
                                raw_inputs={},
                                dynamic_inputs={"chat_log": input_str},
                            )
                        ),
                    )
                )

                record = await executor.execute_workflow(
                    execution_id="exe_0195f3a0000070018231231231231231",
                    workflow=workflow,
                    raw_inputs=WorkflowInputs(dynamic_inputs={"chat_log": input_str}),
                )

    assert mock_repo.get_call_count("get_prompt_blocks_by_ids") >= 1
    assert record.status == ExecutionStatus.RUNNING

    projector = StateProjector()
    results = projector.fold_trace(record.execution_trace)

    found = False
    for dto in results:
        if (
            dto.step_id == "stp_0195f3a0000070018111111111111111"
            and dto.block_id == "blk_0195f3a00000700c8def0123456789ab"
            and dto.payload == "test"
        ):
            found = True
            break
    assert found


@pytest.mark.asyncio
async def test_dag_executor_prompt_blocks_missing_execution_error(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    mock_compiler: MagicMock,
) -> None:
    """Verify DAGExecutor raises AppException when execution_id does not exist in repository.

    Args:
        mock_repo: Seeded in-memory repository fixture.
        mock_compiler: Mocked prompt compiler fixture.
    """
    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        prompt_block_repo=mock_repo,
        output_profile_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )
    workflow = WorkflowFactory.build(
        historical_context_mode=HistoricalContextMode.DISABLED,
        model_registry_id="mrg_0195f3a00000700e826807f3bfa3454d",
        id="wf_0195f3a0000070058555555555555555",
        slug="wf_test_slug",
        status="draft",
        version=1,
        default_profile_id="prof_0195f3a00000700d8ddd1111dddd1111",
        expected_inputs=[],
        steps=[
            StepRule(
                id="stp_0195f3a0000070018111111111111112",
                task_blueprint="stp_0195f3a0000070019999999999999999",
            )
        ],
    )

    with pytest.raises(AppException):
        await executor.execute_workflow(
            execution_id="exe_0195f3a0000070019999999999999999",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={}),
        )
