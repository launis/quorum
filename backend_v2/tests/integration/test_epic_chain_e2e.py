"""End-to-End Golden Master Test for Epic 93 SDUI Output Rendering Unification."""

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.execution import ExecutionRecord, FrozenContext
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import TraceEvent
from backend_v2.models.view.sdui import ReportView
from backend_v2.services.blueprint import BlueprintTransformer
from backend_v2.services.sdui_mapper_service import SduiMapperService
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


@pytest.mark.asyncio
async def test_epic_93_e2e_golden_master() -> None:
    """Verify the E2E data flow from ExecutionRecord to SduiComponent tree.

    ExecutionRecord -> MatrixReducer -> ReportDataDTO -> SduiMapper -> SduiComponent tree.
    """
    # 1. Fake Repository
    repo = InMemoryUnifiedWorkflowRepository()

    # Create dummy ExecutionRecord
    execution_id = "exe_1234abcd1234abcd"
    wf_id = "wf_1234abcd1234abcd"
    profile_id = "prf_1234abcd1234abcd"
    block_id = "blk_1234abcd1234abcd"

    frozen = FrozenContext(ui_hints_snapshot={})

    record = ExecutionRecord(
        id=execution_id,
        workflow_id=wf_id,
        status=ExecutionStatus.PASSED,
        raw_inputs=WorkflowInputs(dynamic_inputs={"text": "dummy"}),
        frozen_context=frozen,
        target_locale="en",
        metadata=ExecutionMetadata(),
        execution_trace=[
            TraceEvent(
                step_name="step_analyst",
                event_type="output",
                content={
                    block_id: {
                        "raw_score": 85.0,
                        "normalized_score": 85.0,
                        "justification": "Checked with sources.",
                    }
                },
            ),
            TraceEvent(
                step_name="step_scoring",
                event_type="output",
                content={
                    "scoring_result": {
                        "total_score": 85.0,
                        "final_score": 85.0,
                        "penalties_applied": [],
                        "aggregation_status": "V2 Commensurate Average",
                    }
                },
            ),
            TraceEvent(
                step_name="step_synthesis",
                event_type="output",
                content={
                    "_evaluative_matrices": {block_id: 85.0},
                    "synthesized_markdown": "We need to leverage our robust synergy and drive disruption.",
                },
            ),
        ],
        output_profile_id=profile_id,
    )
    await repo.save_execution(record)

    # Workflow Mock
    mock_workflow = {
        "id": wf_id,
        "slug": "wf_1",
        "name": {"translations": {"en": "Mock Workflow"}},
        "description": {"translations": {"en": "desc"}},
        "status": "published",
        "historical_context_mode": "DISABLED",
        "model_registry_id": "cfg_model_registry_01",
        "version": 1,
        "organization_id": "root",
        "default_profile_id": profile_id,
        "default_strictness_level": 85,
        "expected_inputs": [],
        "steps": [],
    }
    await repo.save_workflow(Workflow.model_validate(mock_workflow, strict=False))

    # Profile Mock
    mock_profile = {
        "id": profile_id,
        "slug": "mock-profile-slug",
        "workflow_id": wf_id,
        "organization_id": "root",
        "name": {"translations": {"en": "Mock Profile"}},
        "description": {"translations": {"en": "desc"}},
        "target_block_order": [
            "metadata_block",
            "executive_summary_block",
            "matrix_summary_table_block",
            "global_score_block",
        ],
    }
    repo.set_output_profiles([mock_profile])

    # Prompt Block Mock
    mock_pb = {
        "id": block_id,
        "slug": "block_1",
        "category_id": "matrix",
        "is_evaluative": True,
        "type": "float",
        "label": {"translations": {"en": "Matrix 1"}},
        "description": {"translations": {"en": "desc"}},
        "scales": [
            {
                "name": {"translations": {"en": "FAIL"}},
                "score": 0,
                "ai_label": "FAIL",
                "claims": [
                    {
                        "label": {"translations": {"en": "claim"}},
                        "tda_assertions": [
                            {
                                "tda_id": "tda_00000000000000000000000000000000",
                                "concept_description": "concept description 1",
                                "inverse_evidence": False,
                                "aggregation_mode": "EXISTS",
                            }
                        ],
                    }
                ],
            },
            {
                "name": {"translations": {"en": "PASS"}},
                "score": 100,
                "ai_label": "PASS",
                "claims": [
                    {
                        "label": {"translations": {"en": "claim 2"}},
                        "tda_assertions": [
                            {
                                "tda_id": "tda_11111111111111111111111111111111",
                                "concept_description": "concept description 2",
                                "inverse_evidence": False,
                                "aggregation_mode": "EXISTS",
                            }
                        ],
                    }
                ],
            },
        ],
        "computed_min": 0,
        "computed_max": 100,
    }
    repo.set_prompt_blocks([mock_pb])

    transformer = BlueprintTransformer(
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        system_repo=repo,
    )

    # 2. Map Execution to ReportDataDTO
    dto = await transformer.build_report_dto(execution_id, profile_id)

    # 3. Map ReportDataDTO to SDUI ReportView
    mapper = SduiMapperService()
    view = mapper.map_report(dto, execution_id=execution_id)

    # 4. Deep Assertions
    assert isinstance(dto, ReportDataDTO)
    assert isinstance(view, ReportView)
    assert view.view_id == execution_id
    assert view.metrics is not None
    assert view.metrics.global_score == 85.0

    # Verify that ReportDataDTO.inner_sdui_blocks are populated
    assert len(view.inner_sdui_blocks) > 0

    executive_or_grid_block = next(
        (
            b
            for b in view.inner_sdui_blocks
            if b.block_type in ("executive_summary", "data_grid", "hero_insight", "metadata")
        ),
        None,
    )
    assert executive_or_grid_block is not None


@pytest.mark.asyncio
async def test_epic_95_na_cascade_e2e() -> None:
    """Verify that N_A AtomResultDTO correctly cascades to an n_a_card SduiComponent."""
    from backend_v2.models.dtos.atom_result import AtomResultDTO, HydratedAtomDTO
    from backend_v2.models.enums import ExecutionStatus, SDUIComponentType

    # Create dummy ExecutionRecord mapped as ReportDataDTO with an N_A result
    execution_id = "exe_na1234567890"
    tda_id = "tda_short_circuit1234567"

    dto = ReportDataDTO(
        workflow_id="wf_na",
        execution_id=execution_id,
        profile_id="prf_na",
        results=[
            AtomResultDTO(
                tda_id="tda_target123",
                status=ExecutionStatus.N_A,
                short_circuit_reason_tda_ids=[tda_id],
                depends_on_tda_ids=[],
                evaluation_reasoning="Skipped",
                contextual_override=False,
                source_quote=None,
            )
        ],
        hydrated_references={
            tda_id: HydratedAtomDTO(
                sdui_component=SDUIComponentType.BOOLEAN_CARD,
                resolved_claim="This is the NA reason claim",
                source_quote=None,
            ),
            "tda_target123": HydratedAtomDTO(
                sdui_component=SDUIComponentType.BOOLEAN_CARD, resolved_claim="Target claim", source_quote=None
            ),
        },
    )

    mapper = SduiMapperService()
    view = mapper.map_report(dto, execution_id=execution_id)

    # Assertions
    from backend_v2.models.view.sdui import SduiNACard

    na_card = next(
        (b for b in view.inner_sdui_blocks if isinstance(b, SduiNACard)),
        None,
    )
    assert na_card is not None, "N/A outcomes block missing from inner_sdui_blocks"
    assert na_card.block_type == "n_a_card"
    assert tda_id in na_card.short_circuit_reason_tda_ids
    assert "Ohitettu säännön perusteella: This is the NA reason claim" in na_card.message


@pytest.mark.asyncio
async def test_epic_chain_e2e_invalid_profile_raises_app_exception() -> None:
    """NEG-01: Verify requesting a non-existent output profile raises AppException with 404."""
    repo = InMemoryUnifiedWorkflowRepository()

    execution_id = "exe_11111111111111111111111111111111"
    wf_id = "wf_11111111111111111111111111111111"
    non_existent_profile_id = "prf_99999999999999999999999999999999"

    record = ExecutionRecord(
        id=execution_id,
        workflow_id=wf_id,
        output_profile_id="prf_11111111111111111111111111111111",
        status=ExecutionStatus.PASSED,
        raw_inputs=WorkflowInputs(dynamic_inputs={"text": "dummy"}),
        frozen_context=FrozenContext(ui_hints_snapshot={}),
        target_locale="en",
        metadata=ExecutionMetadata(),
        execution_trace=[],
    )
    await repo.save_execution(record)

    mock_workflow = {
        "id": wf_id,
        "slug": "wf_neg01",
        "name": {"translations": {"en": "Mock Workflow"}},
        "description": {"translations": {"en": "desc"}},
        "status": "published",
        "historical_context_mode": "DISABLED",
        "model_registry_id": "cfg_model_registry_01",
        "version": 1,
        "organization_id": "root",
        "default_profile_id": "prf_11111111111111111111111111111111",
        "default_strictness_level": 85,
        "expected_inputs": [],
        "steps": [],
    }
    await repo.save_workflow(Workflow.model_validate(mock_workflow, strict=False))
    repo.set_output_profiles([])
    repo.set_prompt_blocks([])

    transformer = BlueprintTransformer(
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        system_repo=repo,
    )

    with pytest.raises(AppException) as exc_info:
        await transformer.build_report_dto(execution_id, non_existent_profile_id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


@pytest.mark.asyncio
async def test_epic_chain_e2e_missing_locale_raises_app_exception() -> None:
    """NEG-02: Verify missing locale raises AppException with 400."""
    repo = InMemoryUnifiedWorkflowRepository()

    execution_id = "exe_22222222222222222222222222222222"
    wf_id = "wf_22222222222222222222222222222222"

    record = ExecutionRecord(
        id=execution_id,
        workflow_id=wf_id,
        output_profile_id="prf_22222222222222222222222222222222",
        status=ExecutionStatus.PASSED,
        raw_inputs=WorkflowInputs(dynamic_inputs={"text": "dummy"}),
        frozen_context=FrozenContext(ui_hints_snapshot={}),
        target_locale="",
        metadata=ExecutionMetadata(),
        execution_trace=[],
    )
    await repo.save_execution(record)

    mock_workflow = {
        "id": wf_id,
        "slug": "wf_neg02",
        "name": {"translations": {"en": "Mock Workflow"}},
        "description": {"translations": {"en": "desc"}},
        "status": "published",
        "historical_context_mode": "DISABLED",
        "model_registry_id": "cfg_model_registry_01",
        "version": 1,
        "organization_id": "root",
        "default_profile_id": "prf_22222222222222222222222222222222",
        "default_strictness_level": 85,
        "expected_inputs": [],
        "steps": [],
    }
    await repo.save_workflow(Workflow.model_validate(mock_workflow, strict=False))

    transformer = BlueprintTransformer(
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        system_repo=repo,
    )

    with pytest.raises(AppException) as exc_info:
        await transformer.build_report_dto(execution_id, "prf_22222222222222222222222222222222", accept_language=None)

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_epic_chain_e2e_malformed_matrix_payload_raises_app_exception() -> None:
    """NEG-03: Verify malformed matrix step payload raises AppException with 500."""
    repo = InMemoryUnifiedWorkflowRepository()

    execution_id = "exe_33333333333333333333333333333333"
    wf_id = "wf_33333333333333333333333333333333"
    profile_id = "prf_33333333333333333333333333333333"
    block_id = "blk_33333333333333333333333333333333"

    record = ExecutionRecord(
        id=execution_id,
        workflow_id=wf_id,
        output_profile_id=profile_id,
        status=ExecutionStatus.PASSED,
        raw_inputs=WorkflowInputs(dynamic_inputs={"text": "dummy"}),
        frozen_context=FrozenContext(ui_hints_snapshot={}),
        target_locale="en",
        metadata=ExecutionMetadata(),
        execution_trace=[
            TraceEvent(
                step_name="step_analyst",
                event_type="output",
                content={
                    block_id: "corrupted_non_dict_payload_string"  # Non-dict matrix payload!
                },
            )
        ],
    )
    await repo.save_execution(record)

    mock_workflow = {
        "id": wf_id,
        "slug": "wf_neg03",
        "name": {"translations": {"en": "Mock Workflow"}},
        "description": {"translations": {"en": "desc"}},
        "status": "published",
        "historical_context_mode": "DISABLED",
        "model_registry_id": "cfg_model_registry_01",
        "version": 1,
        "organization_id": "root",
        "default_profile_id": profile_id,
        "default_strictness_level": 85,
        "expected_inputs": [],
        "steps": [],
    }
    await repo.save_workflow(Workflow.model_validate(mock_workflow, strict=False))

    mock_profile = {
        "id": profile_id,
        "slug": "mock-profile",
        "workflow_id": wf_id,
        "name": {"translations": {"en": "Mock Profile"}},
        "target_block_order": [
            "metadata_block",
            "executive_summary_block",
            "matrix_summary_table_block",
            "global_score_block",
        ],
    }
    repo.set_output_profiles([mock_profile])

    mock_pb = {
        "id": block_id,
        "slug": "block_1",
        "category_id": "matrix",
        "is_evaluative": True,
        "type": "float",
        "label": {"translations": {"en": "Matrix 1"}},
        "description": {"translations": {"en": "desc"}},
        "scales": [
            {
                "name": {"translations": {"en": "FAIL"}},
                "score": 0,
                "ai_label": "FAIL",
                "claims": [
                    {
                        "label": {"translations": {"en": "claim"}},
                        "tda_assertions": [
                            {
                                "tda_id": "tda_00000000000000000000000000000000",
                                "concept_description": "concept description 1",
                                "inverse_evidence": False,
                                "aggregation_mode": "EXISTS",
                            }
                        ],
                    }
                ],
            },
            {
                "name": {"translations": {"en": "PASS"}},
                "score": 100,
                "ai_label": "PASS",
                "claims": [
                    {
                        "label": {"translations": {"en": "claim 2"}},
                        "tda_assertions": [
                            {
                                "tda_id": "tda_11111111111111111111111111111111",
                                "concept_description": "concept description 2",
                                "inverse_evidence": False,
                                "aggregation_mode": "EXISTS",
                            }
                        ],
                    }
                ],
            },
        ],
        "computed_min": 0,
        "computed_max": 100,
    }
    repo.set_prompt_blocks([mock_pb])

    transformer = BlueprintTransformer(
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        system_repo=repo,
    )

    with pytest.raises(AppException) as exc_info:
        await transformer.build_report_dto(execution_id, profile_id)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
