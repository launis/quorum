"""End-to-end integration tests for SDUI output rendering and BlueprintTransformer."""

from __future__ import annotations

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.matrix import MatrixClaim, MatrixScale, TDAAssertion
from backend_v2.models.dtos.atom_result import AtomResultDTO, HydratedAtomDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.dtos.trace import TraceMatrixPayloadDTO, TraceScoringPayloadDTO
from backend_v2.models.enums import (
    ExecutionStatus,
    HistoricalContextMode,
    SDUIComponentType,
    TargetBlockType,
)
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import TraceEvent
from backend_v2.models.view.sdui import ReportView, SduiMatrixTableBlock, SduiNACard
from backend_v2.services.blueprint import BlueprintTransformer
from backend_v2.services.sdui.sdui_mapper_service import SduiMapperService
from backend_v2.tests.factories.model_factories import (
    ExecutionRecordFactory,
    MatrixPromptBlockFactory,
    OutputProfileFactory,
    WorkflowFactory,
)
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


class TraceEventFactory(ModelFactory[TraceEvent]):
    """Polyfactory model factory for TraceEvent instances."""

    __model__ = TraceEvent


class SduiMatrixTableBlockFactory(ModelFactory[SduiMatrixTableBlock]):
    """Polyfactory model factory for SduiMatrixTableBlock SDUI view blocks."""

    __model__ = SduiMatrixTableBlock


class TDAAssertionFactory(ModelFactory[TDAAssertion]):
    """Polyfactory model factory for TDAAssertion definitions."""

    __model__ = TDAAssertion


def _build_test_matrix_scales() -> list[MatrixScale]:
    """Construct deterministic two-anchor BARS scales for integration tests.

    Returns:
        List of two MatrixScale definitions (0 FAIL and 100 PASS).
    """
    return [
        MatrixScale(
            name=I18nText(translations={"en": "FAIL"}),
            score=0,
            ai_label="FAIL",
            claims=[
                MatrixClaim(
                    label=I18nText(translations={"en": "claim"}),
                    tda_assertions=[
                        TDAAssertionFactory.build(
                            tda_id="tda_00000000000000000000000000000000",
                            concept_description="concept description 1",
                            inverse_evidence=False,
                            depends_on=[],
                        )
                    ],
                )
            ],
        ),
        MatrixScale(
            name=I18nText(translations={"en": "PASS"}),
            score=100,
            ai_label="PASS",
            claims=[
                MatrixClaim(
                    label=I18nText(translations={"en": "claim 2"}),
                    tda_assertions=[
                        TDAAssertionFactory.build(
                            tda_id="tda_11111111111111111111111111111111",
                            concept_description="concept description 2",
                            inverse_evidence=False,
                            depends_on=[],
                        )
                    ],
                )
            ],
        ),
    ]


@pytest.mark.asyncio
async def test_sdui_output_rendering_e2e_golden_master() -> None:
    """Verify the end-to-end data flow from ExecutionRecord to ReportDataDTO and SDUI ReportView."""
    repo = InMemoryUnifiedWorkflowRepository()

    execution_id = "exe_0195f3a0000070018234abcd1234abcd"
    wf_id = "wf_0195f3a0000070018234abcd1234abcd"
    profile_id = "prf_0195f3a0000070018234abcd1234abcd"
    block_id = "blk_0195f3a0000070018234abcd1234abcd"

    record = ExecutionRecordFactory.build(
        id=execution_id,
        workflow_id=wf_id,
        status=ExecutionStatus.PASSED,
        raw_inputs=WorkflowInputs(dynamic_inputs={"text": "dummy"}),
        target_locale="en",
        metadata=ExecutionMetadata(),
        execution_trace=[
            TraceEventFactory.build(
                step_name="step_analyst",
                event_type="output",
                content={
                    block_id: TraceMatrixPayloadDTO(
                        raw_score=85.0,
                        normalized_score=85.0,
                        justification="Checked with sources.",
                    )
                },
                mcp_audit_traces=None,
            ),
            TraceEventFactory.build(
                step_name="step_scoring",
                event_type="output",
                content={
                    "scoring_result": TraceScoringPayloadDTO(
                        total_score=85.0,
                        final_score=85.0,
                        penalties_applied=[],
                        aggregation_status="V2 Commensurate Average",
                    )
                },
                mcp_audit_traces=None,
            ),
            TraceEventFactory.build(
                step_name="step_synthesis",
                event_type="output",
                content={
                    "_evaluative_matrices": {block_id: 85.0},
                    "synthesized_markdown": "We need to leverage our robust synergy and drive disruption.",
                },
                mcp_audit_traces=None,
            ),
        ],
        output_profile_id=profile_id,
    )
    await repo.save_execution(record)

    workflow = WorkflowFactory.build(
        id=wf_id,
        slug="wf_1",
        name=I18nText(translations={"en": "Mock Workflow"}),
        description=I18nText(translations={"en": "desc"}),
        status="published",
        historical_context_mode=HistoricalContextMode.DISABLED,
        model_registry_id="mrg_0195f3a00000700e826807f3bfa3454d",
        version=1,
        organization_id="root",
        default_profile_id=profile_id,
        default_strictness_level=85,
        expected_inputs=[],
        steps=[],
    )
    await repo.save_workflow(workflow)

    mock_profile = OutputProfileFactory.build(
        id=profile_id,
        slug="mock-profile-slug",
        workflow_id=wf_id,
        organization_id="root",
        name=I18nText(translations={"en": "Mock Profile"}),
        description=I18nText(translations={"en": "desc"}),
        target_block_order=[
            TargetBlockType.METADATA_BLOCK,
            TargetBlockType.EXECUTIVE_SUMMARY_BLOCK,
            TargetBlockType.MATRIX_SUMMARY_TABLE_BLOCK,
            TargetBlockType.GLOBAL_SCORE_BLOCK,
        ],
    )
    repo.set_output_profiles([mock_profile])

    mock_pb = MatrixPromptBlockFactory.build(
        id=block_id,
        slug="block_1",
        is_evaluative=True,
        label=I18nText(translations={"en": "Matrix 1"}),
        description=I18nText(translations={"en": "desc"}),
        scales=_build_test_matrix_scales(),
        computed_min=0,
        computed_max=100,
    )
    repo.set_prompt_blocks([mock_pb])

    transformer = BlueprintTransformer(
        exec_repo=repo,
        workflow_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        system_repo=repo,
    )

    dto = await transformer.build_report_dto(execution_id, profile_id)

    mapper = SduiMapperService()
    view = mapper.map_report(dto, execution_id=execution_id)

    assert isinstance(dto, ReportDataDTO)
    assert isinstance(view, ReportView)
    assert view.view_id == execution_id
    assert view.metrics is not None
    assert view.metrics.global_score == 85.0
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
async def test_sdui_na_cascade_e2e() -> None:
    """Verify N_A AtomResultDTO cascades to inline short_circuited_by_claims on SduiMatrixTableBlock."""
    execution_id = "exe_na1234567890"
    tda_id = "tda_short_circuit1234567"

    dto = ReportDataDTO(
        workflow_id="wf_na",
        execution_id=execution_id,
        profile_id="prf_na",
        available_profiles={},
        visible_metadata=[],
        mcp_tool_audit=[],
        short_circuited_by_claims=[],
        falsified_warrant_claims=[],
        inner_sdui_blocks=[
            SduiMatrixTableBlockFactory.build(
                axes=[],
                short_circuited_by_claims=[],
                falsified_warrant_claims=[],
            )
        ],
        results=[
            AtomResultDTO(
                tda_id="tda_target123",
                status=ExecutionStatus.N_A,
                extensions={},
                short_circuit_reason_tda_ids=[tda_id],
                depends_on_tda_ids=[],
                evaluation_reasoning="Skipped",
                contextual_override=False,
                source_quotes=None,
            )
        ],
        hydrated_references={
            tda_id: HydratedAtomDTO(
                sdui_component=SDUIComponentType.BOOLEAN_CARD,
                resolved_claim="This is the NA reason claim",
                source_quotes=None,
            ),
            "tda_target123": HydratedAtomDTO(
                sdui_component=SDUIComponentType.BOOLEAN_CARD,
                resolved_claim="Target claim",
                source_quotes=None,
            ),
        },
    )

    mapper = SduiMapperService()
    view = mapper.map_report(dto, execution_id=execution_id)

    assert not any(isinstance(b, SduiNACard) for b in view.inner_sdui_blocks)
    matrix_block = next(
        (b for b in view.inner_sdui_blocks if isinstance(b, SduiMatrixTableBlock)),
        None,
    )
    assert matrix_block is not None
    assert "Ohitettu säännön perusteella: This is the NA reason claim" in matrix_block.short_circuited_by_claims


@pytest.mark.asyncio
async def test_sdui_chain_e2e_invalid_profile_raises_app_exception() -> None:
    """Verify requesting a non-existent output profile raises AppException with HTTP 404."""
    repo = InMemoryUnifiedWorkflowRepository()

    execution_id = "exe_11111111111111111111111111111111"
    wf_id = "wf_11111111111111111111111111111111"
    non_existent_profile_id = "prf_99999999999999999999999999999999"

    record = ExecutionRecordFactory.build(
        id=execution_id,
        workflow_id=wf_id,
        output_profile_id="prf_11111111111111111111111111111111",
        status=ExecutionStatus.PASSED,
        raw_inputs=WorkflowInputs(dynamic_inputs={"text": "dummy"}),
        target_locale="en",
        metadata=ExecutionMetadata(),
        execution_trace=[],
    )
    await repo.save_execution(record)

    workflow = WorkflowFactory.build(
        id=wf_id,
        slug="wf_invalid_profile",
        name=I18nText(translations={"en": "Mock Workflow"}),
        description=I18nText(translations={"en": "desc"}),
        status="published",
        historical_context_mode=HistoricalContextMode.DISABLED,
        model_registry_id="mrg_0195f3a00000700e826807f3bfa3454d",
        version=1,
        organization_id="root",
        default_profile_id="prf_11111111111111111111111111111111",
        default_strictness_level=85,
        expected_inputs=[],
        steps=[],
    )
    await repo.save_workflow(workflow)
    repo.set_output_profiles([])
    repo.set_prompt_blocks([])

    transformer = BlueprintTransformer(
        exec_repo=repo,
        workflow_repo=repo,
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
async def test_sdui_chain_e2e_missing_locale_error() -> None:
    """Verify missing locale raises AppException with HTTP 400."""
    repo = InMemoryUnifiedWorkflowRepository()

    execution_id = "exe_22222222222222222222222222222222"
    wf_id = "wf_22222222222222222222222222222222"

    record = ExecutionRecordFactory.build(
        id=execution_id,
        workflow_id=wf_id,
        output_profile_id="prf_22222222222222222222222222222222",
        status=ExecutionStatus.PASSED,
        raw_inputs=WorkflowInputs(dynamic_inputs={"text": "dummy"}),
        target_locale="",
        metadata=ExecutionMetadata(),
        execution_trace=[],
    )
    await repo.save_execution(record)

    workflow = WorkflowFactory.build(
        id=wf_id,
        slug="wf_missing_locale",
        name=I18nText(translations={"en": "Mock Workflow"}),
        description=I18nText(translations={"en": "desc"}),
        status="published",
        historical_context_mode=HistoricalContextMode.DISABLED,
        model_registry_id="mrg_0195f3a00000700e826807f3bfa3454d",
        version=1,
        organization_id="root",
        default_profile_id="prf_22222222222222222222222222222222",
        default_strictness_level=85,
        expected_inputs=[],
        steps=[],
    )
    await repo.save_workflow(workflow)

    transformer = BlueprintTransformer(
        exec_repo=repo,
        workflow_repo=repo,
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
async def test_sdui_chain_e2e_malformed_matrix_payload_failure() -> None:
    """Verify malformed matrix step payload raises AppException with HTTP 500."""
    repo = InMemoryUnifiedWorkflowRepository()

    execution_id = "exe_33333333333333333333333333333333"
    wf_id = "wf_33333333333333333333333333333333"
    profile_id = "prf_33333333333333333333333333333333"
    block_id = "blk_33333333333333333333333333333333"

    record = ExecutionRecordFactory.build(
        id=execution_id,
        workflow_id=wf_id,
        output_profile_id=profile_id,
        status=ExecutionStatus.PASSED,
        raw_inputs=WorkflowInputs(dynamic_inputs={"text": "dummy"}),
        target_locale="en",
        metadata=ExecutionMetadata(),
        execution_trace=[
            TraceEventFactory.build(
                step_name="step_analyst",
                event_type="output",
                content={
                    block_id: "corrupted_non_dict_payload_string",
                },
                mcp_audit_traces=None,
            )
        ],
    )
    await repo.save_execution(record)

    workflow = WorkflowFactory.build(
        id=wf_id,
        slug="wf_malformed_matrix",
        name=I18nText(translations={"en": "Mock Workflow"}),
        description=I18nText(translations={"en": "desc"}),
        status="published",
        historical_context_mode=HistoricalContextMode.DISABLED,
        model_registry_id="mrg_0195f3a00000700e826807f3bfa3454d",
        version=1,
        organization_id="root",
        default_profile_id=profile_id,
        default_strictness_level=85,
        expected_inputs=[],
        steps=[],
    )
    await repo.save_workflow(workflow)

    mock_profile = OutputProfileFactory.build(
        id=profile_id,
        slug="mock-profile",
        workflow_id=wf_id,
        name=I18nText(translations={"en": "Mock Profile"}),
        target_block_order=[
            TargetBlockType.METADATA_BLOCK,
            TargetBlockType.EXECUTIVE_SUMMARY_BLOCK,
            TargetBlockType.MATRIX_SUMMARY_TABLE_BLOCK,
            TargetBlockType.GLOBAL_SCORE_BLOCK,
        ],
    )
    repo.set_output_profiles([mock_profile])

    mock_pb = MatrixPromptBlockFactory.build(
        id=block_id,
        slug="block_1",
        is_evaluative=True,
        label=I18nText(translations={"en": "Matrix 1"}),
        description=I18nText(translations={"en": "desc"}),
        scales=_build_test_matrix_scales(),
        computed_min=0,
        computed_max=100,
    )
    repo.set_prompt_blocks([mock_pb])

    transformer = BlueprintTransformer(
        exec_repo=repo,
        workflow_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        system_repo=repo,
    )

    with pytest.raises(AppException) as exc_info:
        await transformer.build_report_dto(execution_id, profile_id)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
