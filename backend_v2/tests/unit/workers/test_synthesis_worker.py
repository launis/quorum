"""Unit tests for synthesis_worker.py covering error handling, caching, validation, and full execution."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

import backend_v2.workers.synthesis_worker as synthesis_worker_mod
from backend_v2.core.hook_registry import HookDeltaDTO, HookResult
from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes, ResourceNotFoundError
from backend_v2.models.auth import SystemOrganizations
from backend_v2.models.core_base import I18nText, generate_opaque_id
from backend_v2.models.domain.execution import ExecutionRecord, FrozenContext
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.proposition_graph import FalsifiedClaimMatch
from backend_v2.models.domain.synthesis import MatrixSynthesisGroup, RenderedSynthesisCache
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.base import DataStarvationEvent
from backend_v2.models.dtos.causal_discovery import (
    AntiFluffAuditDTO,
    CausalEdgeDTO,
    CausalGraphPayloadDTO,
    CausalNodeDTO,
    CausalRootCauseDiagnosisDTO,
    CausalTdaFusionResultDTO,
    FairScoringBreakdownDTO,
    PrescriptiveRemediationDTO,
)
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.dtos.global_context import GlobalContextVarsDTO
from backend_v2.models.dtos.schema_manifest import GeneratedSchemaManifestDTO
from backend_v2.models.dtos.step_output import StepOutputDTO
from backend_v2.models.dtos.synthesis import (
    CausalSynthesisBriefDTO,
    ExecutiveSummarySectionResult,
    MatrixExplanationContextDTO,
    MatrixExplanationsResult,
    MatrixSectionSynthesesResult,
    SynthesisDistillationDTO,
    SynthesisSectionDTO,
    XaiHighlightsResult,
)
from backend_v2.models.dtos.theory_manifest import InjectedTheoryManifestDTO
from backend_v2.models.enums import (
    EntityPrefix,
    ExecutionStatus,
    LaxHistoricalContextMode,
    PresetView,
    RoleClassification,
    TargetBlockType,
    XaiExtensionType,
)
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import TraceEvent
from backend_v2.models.view.sdui import ParagraphBlock
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository
from backend_v2.workers.synthesis_worker import generate_profile_synthesis_and_pdf_task
from backend_v2.workers.variance_synthesis import VarianceExplanationResult
from scripts.audit_warning_baseline import (
    CURRENT_RESIDUAL_CEILINGS,
    ResidualDebtCeilingsDTO,
    compute_census_counts,
    verify_residual_debt_ceilings,
)


def _make_base_profile(prof_id: str, wf_id: str) -> OutputProfile:
    """Create a validated OutputProfile fixture for synthesis worker tests."""
    return OutputProfile(
        organization_id="org_0195f3a0000070008000000000000001",
        id=prof_id,
        slug="prof_test",
        workflow_id=wf_id,
        name=I18nText(translations={"en": "Test Profile"}),
        target_block_order=[
            TargetBlockType.EXECUTIVE_SUMMARY_BLOCK,
            TargetBlockType.MATRIX_GRAPHS_BLOCK,
            TargetBlockType.GROUPED_EXTENSIONS_BLOCK,
            TargetBlockType.PRINTABLE_SOURCES_BLOCK,
        ],
        executive_summary_directive="Synthesize executive summary.",
        synthesis_length_constraint=500,
        tone_instruction="Objective",
        matrix_1d_synthesis_directive="Synthesize 1D.",
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a00000700283456789abcdef01",
                title=I18nText(translations={"en": "Group 1"}),
                view_type=PresetView.METRICS_1D,
                target_blocks=["blk_0195f3a00000700283456789abcdef01"],
            )
        ],
        visible_workflow_extensions=[XaiExtensionType.VARIANCE_VALIDATION],
        variance_target_block="blk_0195f3a00000700283456789abcdef01",
        max_extension_items=5,
        xai_synthesis_directive="Synthesize highlights.",
        row_explanation_directive="Explain rows.",
    )


def _make_base_workflow(wf_id: str, prof_id: str) -> Workflow:
    """Create a validated Workflow fixture for synthesis worker tests."""
    return Workflow(
        organization_id="org_0195f3a0000070008000000000000001",
        id=wf_id,
        slug="test_wf",
        name=I18nText(translations={"en": "Test Workflow"}),
        description=I18nText(translations={"en": "Desc"}),
        status="draft",
        version=1,
        steps=[],
        default_profile_id=prof_id,
        model_registry_id="mrg_0195f3a0000070018111222233334444",
        historical_context_mode=LaxHistoricalContextMode.DISABLED,
    )


def _make_execution_record(
    exec_id: str,
    wf_id: str,
    prof_id: str,
    status: ExecutionStatus = ExecutionStatus.PASSED,
    trace_events: list[TraceEvent] | None = None,
) -> ExecutionRecord:
    """Create a validated ExecutionRecord fixture via direct typed constructor."""
    return ExecutionRecord(
        id=exec_id,
        workflow_id=wf_id,
        output_profile_id=prof_id,
        status=status,
        target_locale="en",
        raw_inputs=WorkflowInputs(),
        frozen_context=FrozenContext(),
        metadata=ExecutionMetadata(),
        execution_trace=trace_events if trace_events is not None else [],
    )


@pytest.mark.asyncio
async def test_synthesis_worker_empty_accept_language_raises() -> None:
    """Test generate_profile_synthesis_and_pdf_task raises AppException when accept_language is empty."""
    with pytest.raises(AppException) as exc_info:
        await generate_profile_synthesis_and_pdf_task(execution_id="exe_1", accept_language="", profile_id="pro_1")
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_synthesis_worker_whitespace_accept_language_raises() -> None:
    """Test generate_profile_synthesis_and_pdf_task raises AppException when accept_language is whitespace only."""
    with pytest.raises(AppException) as exc_info:
        await generate_profile_synthesis_and_pdf_task(execution_id="exe_1", accept_language="   ", profile_id="pro_1")
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_synthesis_worker_missing_execution_returns() -> None:
    """Test generate_profile_synthesis_and_pdf_task returns early if execution does not exist."""
    mock_repo = InMemoryUnifiedWorkflowRepository()

    with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exe_missing", accept_language="en", profile_id="pro_1"
        )
        assert (await mock_repo.get_execution("exe_missing")) is None


@pytest.mark.asyncio
async def test_synthesis_worker_already_synthesized_enqueues_pdf() -> None:
    """Test generate_profile_synthesis_and_pdf_task short-circuits to report artifact generation if already synthesized."""
    prof_id = "pro_0195f3a00000700283456789abcdef01"
    cache = RenderedSynthesisCache()
    rec = _make_execution_record(
        exec_id="exe_0195f3a00000700283456789abcdef01",
        wf_id="wor_0195f3a00000700283456789abcdef01",
        prof_id=prof_id,
    ).model_copy(update={"profile_syntheses": {prof_id: cache}})
    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_execution(rec)
    mock_redis = AsyncMock()
    mock_artifact = MagicMock()
    mock_artifact.id = "rep_0195f3a00000700283456789abcdef01"

    with (
        patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo),
        patch("backend_v2.workers.synthesis_worker.ReportService") as mock_report_service_cls,
    ):
        mock_svc = mock_report_service_cls.return_value
        mock_svc.get_or_create_default_artifact = AsyncMock(return_value=mock_artifact)
        mock_svc.compile_and_persist_artifact = AsyncMock()
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exe_0195f3a00000700283456789abcdef01",
            accept_language="en",
            profile_id=prof_id,
            redis=mock_redis,
        )
        mock_svc.get_or_create_default_artifact.assert_awaited_once_with(
            execution_id="exe_0195f3a00000700283456789abcdef01",
            profile_id=prof_id,
            locale="en",
        )
        mock_svc.compile_and_persist_artifact.assert_awaited_once_with(
            "rep_0195f3a00000700283456789abcdef01",
            mock_redis,
        )


@pytest.mark.asyncio
async def test_synthesis_worker_profile_not_found_raises() -> None:
    """Test generate_profile_synthesis_and_pdf_task raises ResourceNotFoundError if profile missing."""
    prof_id = "pro_0195f3a00000700283456789abcdef01"
    rec = _make_execution_record(
        exec_id="exe_0195f3a00000700283456789abcdef01",
        wf_id="wor_0195f3a00000700283456789abcdef01",
        prof_id=prof_id,
    )
    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_execution(rec)

    with (
        patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo),
        pytest.raises(ResourceNotFoundError),
    ):
        await generate_profile_synthesis_and_pdf_task(
            execution_id="exe_0195f3a00000700283456789abcdef01",
            accept_language="en",
            profile_id=prof_id,
        )


@pytest.mark.asyncio
async def test_synthesis_worker_workflow_not_found_raises() -> None:
    """Test generate_profile_synthesis_and_pdf_task raises AppException if workflow missing."""
    prof_id = "pro_0195f3a00000700283456789abcdef01"
    rec = _make_execution_record(
        exec_id="exe_0195f3a00000700283456789abcdef01",
        wf_id="wor_0195f3a00000700283456789abcdef01",
        prof_id=prof_id,
    )
    prof = OutputProfile(
        organization_id="org_0195f3a0000070008000000000000001",
        id=prof_id,
        slug="prof_test",
        workflow_id="wor_0195f3a00000700283456789abcdef01",
        name=I18nText(translations={"en": "Test Profile"}),
        target_block_order=[TargetBlockType.EXECUTIVE_SUMMARY_BLOCK],
    )
    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_execution(rec)
    await mock_repo.save_output_profile(prof)

    with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
        with pytest.raises(AppException) as exc_info:
            await generate_profile_synthesis_and_pdf_task(
                execution_id="exe_0195f3a00000700283456789abcdef01",
                accept_language="en",
                profile_id=prof_id,
            )
        assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_synthesis_worker_full_pipeline_happy_path_with_causal_fusion() -> None:
    """Test full synthesis pipeline including CausalTdaFusionResultDTO parsing and execution update."""
    prof_id = "pro_0195f3a00000700283456789abcdef01"
    wf_id = "wor_0195f3a00000700283456789abcdef01"
    exec_id = "exe_0195f3a00000700283456789abcdef01"

    fusion_result = CausalTdaFusionResultDTO(
        graph=CausalGraphPayloadDTO(
            nodes=[
                CausalNodeDTO(
                    node_id="node_0",
                    claim="Root proposition",
                    status=ExecutionStatus.PASSED,
                    blame_parent_ids=[],
                    dependent_child_ids=["node_1"],
                ),
                CausalNodeDTO(
                    node_id="node_1",
                    claim="Dependent proposition",
                    status=ExecutionStatus.FAILED,
                    blame_parent_ids=["node_0"],
                    dependent_child_ids=[],
                ),
            ],
            edges=[
                CausalEdgeDTO(
                    source_id="node_0",
                    target_id="node_1",
                    reasoning="Direct causal influence",
                )
            ],
            root_cause_node_ids=["node_0"],
            cycle_detected=False,
        ),
        root_cause_diagnoses=[
            CausalRootCauseDiagnosisDTO(
                root_cause_parent_id="node_0",
                failing_node_id="node_1",
                paragraph_ref="p1",
                explanation="Proposition failure propagated from node 0.",
                penalty_points=1.0,
            )
        ],
        prescriptive_remediations=[
            PrescriptiveRemediationDTO(
                target_node_id="node_1",
                required_action="Review premise in node 0.",
                unlocks_node_ids=[],
                potential_score_impact=1.0,
            )
        ],
        anti_fluff_audit=AntiFluffAuditDTO(
            isolated_concept_count=0,
            cycle_detected=False,
            unsupported_claims_count=0,
            logical_cohesion_score=0.95,
        ),
        fair_scoring=FairScoringBreakdownDTO(
            independent_error_count=0,
            cascading_fault_count=1,
            raw_penalty_points=1.0,
            deduplicated_penalty_points=0.7,
            dampened_savings_points=0.3,
        ),
    )

    rec = _make_execution_record(
        exec_id=exec_id,
        wf_id=wf_id,
        prof_id=prof_id,
        trace_events=[
            TraceEvent(
                v=1,
                timestamp=datetime.now(UTC),
                event_type="progress",
                step_name="causal_discovery",
                content=fusion_result,
            )
        ],
    )
    prof = _make_base_profile(prof_id, wf_id)
    wf = _make_base_workflow(wf_id, prof_id)

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_execution(rec)
    await mock_repo.save_output_profile(prof)
    await mock_repo.save_workflow(wf)

    distilled_dto = SynthesisDistillationDTO(
        distilled_inputs="Distilled inputs text",
        target_locale="en",
        title_map={"blk_1": "Block 1 Title"},
        matrices_to_explain=[
            MatrixExplanationContextDTO(
                real_matrix_id="blk_0195f3a00000700283456789abcdef01",
                matrix_id="mat_1",
                matrix_label="Matrix 1",
                score=1.0,
                justification="Matrix justification",
            )
        ],
    )

    token_usage = TokenUsage(prompt_tokens=50, completion_tokens=50, total_tokens=100, cost_usd=0.005)
    exec_summary_res = (
        ExecutiveSummarySectionResult(
            executive_summary=[ParagraphBlock(text="Executive summary synthesized.", exact_quotes=[], citations=[])],
            user_role=RoleClassification.ARCHITECT,
            user_role_justification="Strategic authority",
            cited_sources=["doc_1"],
        ),
        token_usage,
    )
    matrix_sections_res = [
        (
            "grp_0195f3a00000700283456789abcdef01",
            (
                MatrixSectionSynthesesResult(
                    sections=[
                        SynthesisSectionDTO(
                            layout_id="grp_0195f3a00000700283456789abcdef01",
                            content_blocks=[ParagraphBlock(text="Group 1 Title", exact_quotes=[], citations=[])],
                        )
                    ]
                ),
                token_usage,
            ),
        )
    ]
    xai_res = (XaiHighlightsResult(xai_highlights=[]), token_usage)
    row_res = (MatrixExplanationsResult(explanations=[]), token_usage)
    var_res = (None, (VarianceExplanationResult(explanation="Variance verified"), token_usage))

    mock_redis = AsyncMock()
    mock_artifact = MagicMock()
    mock_artifact.id = "rep_123"

    with (
        patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo),
        patch(
            "backend_v2.workers.synthesis_worker.synthesis_distiller_hook",
            new_callable=AsyncMock,
            return_value=HookResult(success=True, state_delta=HookDeltaDTO(delta=distilled_dto)),
        ),
        patch("backend_v2.workers.synthesis_worker.LLMClient.from_tier", new_callable=AsyncMock),
        patch(
            "backend_v2.workers.synthesis_worker.create_executive_summary_task",
            new_callable=AsyncMock,
            return_value=exec_summary_res,
        ) as mock_exec_task,
        patch(
            "backend_v2.workers.synthesis_worker.create_matrix_sections_tasks",
            new_callable=AsyncMock,
            return_value=matrix_sections_res,
        ),
        patch(
            "backend_v2.workers.synthesis_worker.create_xai_highlights_task",
            new_callable=AsyncMock,
            return_value=xai_res,
        ),
        patch(
            "backend_v2.workers.synthesis_worker.create_row_explanations_task",
            new_callable=AsyncMock,
            return_value=row_res,
        ),
        patch(
            "backend_v2.workers.synthesis_worker.build_variance_metrics_and_task",
            new_callable=AsyncMock,
            return_value=var_res,
        ),
        patch("backend_v2.workers.synthesis_worker.ReportService") as mock_report_service_cls,
    ):
        mock_svc = mock_report_service_cls.return_value
        mock_svc.get_or_create_default_artifact = AsyncMock(return_value=mock_artifact)
        mock_svc.compile_and_persist_artifact = AsyncMock()

        await generate_profile_synthesis_and_pdf_task(
            execution_id=exec_id,
            accept_language="en",
            profile_id=prof_id,
            redis=mock_redis,
        )

        # Verify causal diagnosis was passed to create_executive_summary_task
        mock_exec_task.assert_awaited_once()
        assert mock_exec_task.await_args is not None
        call_kwargs = mock_exec_task.await_args.kwargs
        assert "causal_diagnosis" in call_kwargs
        causal_diag = call_kwargs["causal_diagnosis"]
        assert causal_diag is not None
        assert "Intact Propositions: 1/2" in causal_diag
        assert "Logical Cohesion: 0.95" in causal_diag
        assert "Root Cause Fault Chains:" in causal_diag

    # Verify execution was updated with profile_syntheses
    updated_exec = await mock_repo.get_execution(exec_id)
    assert updated_exec is not None
    assert updated_exec.profile_syntheses is not None
    assert prof_id in updated_exec.profile_syntheses
    cache = updated_exec.profile_syntheses[prof_id]
    assert TargetBlockType.EXECUTIVE_SUMMARY_BLOCK.value in cache.section_syntheses
    assert cache.user_role == RoleClassification.ARCHITECT.value
    assert cache.cited_sources == ["doc_1"]
    assert updated_exec.cumulative_synthesis_tokens > 0


@pytest.mark.asyncio
async def test_synthesis_worker_with_causal_graph_payload_in_execution_trace() -> None:
    """Test causal diagnosis extraction from execution_trace output event containing CausalGraphPayloadDTO."""
    prof_id = "pro_0195f3a00000700283456789abcdef01"
    wf_id = "wor_0195f3a00000700283456789abcdef01"
    exec_id = "exe_0195f3a00000700283456789abcdef01"

    graph_payload = CausalGraphPayloadDTO(
        nodes=[
            CausalNodeDTO(
                node_id="node_0",
                claim="Premise 0",
                status=ExecutionStatus.PASSED,
                blame_parent_ids=[],
                dependent_child_ids=[],
            )
        ],
        edges=[],
        root_cause_node_ids=["node_0"],
        cycle_detected=False,
    )

    step_out = StepOutputDTO(
        step_id="stp_0195f3a00000700283456789abcdef01",
        block_id="graph",
        data_type="causal",
        payload=graph_payload,
    )
    rec = _make_execution_record(
        exec_id=exec_id,
        wf_id=wf_id,
        prof_id=prof_id,
        trace_events=[
            TraceEvent(
                v=1,
                timestamp=datetime.now(UTC),
                event_type="output",
                step_name="stp_0195f3a00000700283456789abcdef01",
                content=step_out,
            )
        ],
    )
    prof = _make_base_profile(prof_id, wf_id)
    wf = _make_base_workflow(wf_id, prof_id)

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_execution(rec)
    await mock_repo.save_output_profile(prof)
    await mock_repo.save_workflow(wf)

    distilled_dto = SynthesisDistillationDTO(
        distilled_inputs="Distilled inputs text",
        target_locale="en",
        title_map={},
        matrices_to_explain=[],
    )
    token_usage = TokenUsage(prompt_tokens=10, completion_tokens=10, total_tokens=20, cost_usd=0.001)

    with (
        patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo),
        patch(
            "backend_v2.workers.synthesis_worker.synthesis_distiller_hook",
            new_callable=AsyncMock,
            return_value=HookResult(success=True, state_delta=HookDeltaDTO(delta=distilled_dto)),
        ),
        patch("backend_v2.workers.synthesis_worker.LLMClient.from_tier", new_callable=AsyncMock),
        patch(
            "backend_v2.workers.synthesis_worker.create_executive_summary_task",
            new_callable=AsyncMock,
            return_value=(
                ExecutiveSummarySectionResult(
                    executive_summary=[ParagraphBlock(text="Exec", exact_quotes=[], citations=[])],
                    user_role=None,
                    user_role_justification=None,
                    cited_sources=[],
                ),
                token_usage,
            ),
        ) as mock_exec_task,
        patch(
            "backend_v2.workers.synthesis_worker.create_matrix_sections_tasks",
            new_callable=AsyncMock,
            return_value=[],
        ),
        patch(
            "backend_v2.workers.synthesis_worker.create_xai_highlights_task",
            new_callable=AsyncMock,
            return_value=None,
        ),
        patch(
            "backend_v2.workers.synthesis_worker.create_row_explanations_task",
            new_callable=AsyncMock,
            return_value=None,
        ),
        patch(
            "backend_v2.workers.synthesis_worker.build_variance_metrics_and_task",
            new_callable=AsyncMock,
            return_value=(None, None),
        ),
        patch("backend_v2.workers.synthesis_worker.ReportService") as mock_report_service_cls,
    ):
        mock_svc = mock_report_service_cls.return_value
        mock_svc.get_or_create_default_artifact = AsyncMock()

        await generate_profile_synthesis_and_pdf_task(
            execution_id=exec_id,
            accept_language="en",
            profile_id=prof_id,
        )

        mock_exec_task.assert_awaited_once()
        assert mock_exec_task.await_args is not None
        causal_diag = mock_exec_task.await_args.kwargs["causal_diagnosis"]
        assert causal_diag is not None
        assert "Total Propositions: 1" in causal_diag
        assert "Cycle Detected: False" in causal_diag
        assert "Root Cause Proposition: Premise 0" in causal_diag


@pytest.mark.asyncio
async def test_synthesis_worker_fans_out_causal_synthesis_brief_to_all_four_tasks() -> None:
    """Test generate_profile_synthesis_and_pdf_task fans out CausalSynthesisBriefDTO and shared BALANCED client to all 4 tasks."""
    prof_id = "pro_0195f3a00000700283456789abcdef01"
    wf_id = "wor_0195f3a00000700283456789abcdef01"
    exec_id = "exe_0195f3a00000700283456789abcdef01"
    claim_id = generate_opaque_id(EntityPrefix.NODE)
    warrant_id = generate_opaque_id(EntityPrefix.NODE)
    rebuttal_id = generate_opaque_id(EntityPrefix.NODE)

    fusion_result = CausalTdaFusionResultDTO(
        graph=CausalGraphPayloadDTO(
            nodes=[
                CausalNodeDTO(
                    node_id=warrant_id,
                    claim="Warrant Premise Claim",
                    status=ExecutionStatus.FAILED,
                    blame_parent_ids=[],
                    dependent_child_ids=[claim_id],
                ),
                CausalNodeDTO(
                    node_id=claim_id,
                    claim="Downstream Target Claim",
                    status=ExecutionStatus.FAILED,
                    blame_parent_ids=[warrant_id],
                    dependent_child_ids=[],
                ),
                CausalNodeDTO(
                    node_id=rebuttal_id,
                    claim="Counter-Evidence Rebuttal Claim",
                    status=ExecutionStatus.PASSED,
                    blame_parent_ids=[],
                    dependent_child_ids=[],
                ),
            ],
            edges=[],
            root_cause_node_ids=[warrant_id],
            cycle_detected=False,
        ),
        root_cause_diagnoses=[
            CausalRootCauseDiagnosisDTO(
                root_cause_parent_id=warrant_id,
                root_cause_claim="Warrant Premise Claim",
                failing_node_id=claim_id,
                failing_node_claim="Downstream Target Claim",
                warrant_relation="warrants",
                paragraph_ref="p1",
                explanation="Warrant failed empirically.",
                penalty_points=1.5,
            )
        ],
        falsified_claims=[
            FalsifiedClaimMatch(
                falsified_claim_id=claim_id,
                claim_statement="Downstream Target Claim",
                invalidated_warrant_id=warrant_id,
                rebuttal_id=rebuttal_id,
                rebuttal_confidence=0.92,
            )
        ],
        prescriptive_remediations=[
            PrescriptiveRemediationDTO(
                target_node_id=claim_id,
                required_action="Establish empirical warrant.",
                unlocks_node_ids=[],
                potential_score_impact=1.5,
            )
        ],
        anti_fluff_audit=AntiFluffAuditDTO(
            isolated_concept_count=0,
            cycle_detected=False,
            unsupported_claims_count=0,
            logical_cohesion_score=0.80,
        ),
        fair_scoring=FairScoringBreakdownDTO(
            independent_error_count=1,
            cascading_fault_count=1,
            raw_penalty_points=2.0,
            deduplicated_penalty_points=1.5,
            dampened_savings_points=0.5,
        ),
    )

    rec = _make_execution_record(
        exec_id=exec_id,
        wf_id=wf_id,
        prof_id=prof_id,
        trace_events=[
            TraceEvent(
                v=1,
                timestamp=datetime.now(UTC),
                event_type="progress",
                step_name="causal_discovery",
                content=fusion_result,
            )
        ],
    )
    prof = _make_base_profile(prof_id, wf_id)
    wf = _make_base_workflow(wf_id, prof_id)

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_execution(rec)
    await mock_repo.save_output_profile(prof)
    await mock_repo.save_workflow(wf)

    distilled_dto = SynthesisDistillationDTO(
        distilled_inputs="Distilled inputs text",
        target_locale="en",
        title_map={"blk_0195f3a00000700283456789abcdef01": "Matrix 1"},
        matrices_to_explain=[
            MatrixExplanationContextDTO(
                real_matrix_id="blk_0195f3a00000700283456789abcdef01",
                matrix_id="m0",
                matrix_label="Matrix 1",
                score=2.0,
                justification="Justification",
            )
        ],
    )
    token_usage = TokenUsage(prompt_tokens=10, completion_tokens=10, total_tokens=20, cost_usd=0.001)
    shared_balanced_client = AsyncMock()

    with (
        patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo),
        patch(
            "backend_v2.workers.synthesis_worker.synthesis_distiller_hook",
            new_callable=AsyncMock,
            return_value=HookResult(success=True, state_delta=HookDeltaDTO(delta=distilled_dto)),
        ),
        patch(
            "backend_v2.workers.synthesis_worker.LLMClient.from_tier",
            new_callable=AsyncMock,
            return_value=shared_balanced_client,
        ),
        patch(
            "backend_v2.workers.synthesis_worker.create_executive_summary_task",
            new_callable=AsyncMock,
            return_value=(
                ExecutiveSummarySectionResult(
                    executive_summary=[ParagraphBlock(text="Exec", exact_quotes=[], citations=[])],
                    user_role=None,
                    user_role_justification=None,
                    cited_sources=[],
                ),
                token_usage,
            ),
        ) as mock_exec_task,
        patch(
            "backend_v2.workers.synthesis_worker.create_matrix_sections_tasks",
            new_callable=AsyncMock,
            return_value=[],
        ) as mock_matrix_task,
        patch(
            "backend_v2.workers.synthesis_worker.create_xai_highlights_task",
            new_callable=AsyncMock,
            return_value=None,
        ) as mock_xai_task,
        patch(
            "backend_v2.workers.synthesis_worker.create_row_explanations_task",
            new_callable=AsyncMock,
            return_value=None,
        ) as mock_row_task,
        patch(
            "backend_v2.workers.synthesis_worker.build_variance_metrics_and_task",
            new_callable=AsyncMock,
            return_value=(None, None),
        ),
        patch("backend_v2.workers.synthesis_worker.ReportService") as mock_report_service_cls,
    ):
        mock_svc = mock_report_service_cls.return_value
        mock_svc.get_or_create_default_artifact = AsyncMock()

        await generate_profile_synthesis_and_pdf_task(
            execution_id=exec_id,
            accept_language="en",
            profile_id=prof_id,
        )

        for task_mock in (
            mock_exec_task,
            mock_matrix_task,
            mock_xai_task,
            mock_row_task,
        ):
            task_mock.assert_awaited_once()
            assert task_mock.await_args is not None
            assert task_mock.await_args.kwargs["client"] is shared_balanced_client
            diag = task_mock.await_args.kwargs["causal_diagnosis"]
            assert diag is not None
            assert "Warrant Premise Claim -> Downstream Target Claim (warrants)" in diag
            assert "Counter-Evidence Rebuttal Claim -> Warrant Premise Claim -> Downstream Target Claim" in diag
            assert "Post-Hoc Fidelity Penalties:" in diag

        assert mock_exec_task.await_args is not None
        base_dynamic_parts = mock_exec_task.await_args.kwargs["base_dynamic_parts"]
        for part in base_dynamic_parts:
            assert "<global_length_constraint_chars>" not in part


@pytest.mark.asyncio
async def test_synthesis_worker_hydrates_quiescent_fusion_from_jsonb_trace_output() -> None:
    """Test generate_profile_synthesis_and_pdf_task hydrates CausalTdaFusionResultDTO from JSONB output TraceEvent via final_inputs."""
    prof_id = "pro_0195f3a00000700283456789abcdef01"
    wf_id = "wor_0195f3a00000700283456789abcdef01"
    exec_id = "exe_0195f3a00000700283456789abcdef01"
    step_id = generate_opaque_id(EntityPrefix.STEP)
    n1 = generate_opaque_id(EntityPrefix.NODE)
    n2 = generate_opaque_id(EntityPrefix.NODE)
    n3 = generate_opaque_id(EntityPrefix.NODE)

    fusion_result = CausalTdaFusionResultDTO(
        graph=CausalGraphPayloadDTO(
            nodes=[
                CausalNodeDTO(node_id=n1, claim="Foundational Premise", status=ExecutionStatus.PASSED),
                CausalNodeDTO(node_id=n2, claim="Warranted Conclusion", status=ExecutionStatus.PASSED),
                CausalNodeDTO(node_id=n3, claim="Unlinked Deliverable Island", status=ExecutionStatus.PASSED),
            ],
            edges=[
                CausalEdgeDTO(
                    source_id=n1,
                    target_id=n2,
                    reasoning="Foundational Premise directly supports Warranted Conclusion.",
                )
            ],
            isolated_node_ids=[n3],
            cycle_detected=False,
        ),
        root_cause_diagnoses=[],
        falsified_claims=[],
        prescriptive_remediations=[],
        anti_fluff_audit=AntiFluffAuditDTO(
            isolated_concept_count=1,
            cycle_detected=False,
            unsupported_claims_count=0,
            logical_cohesion_score=0.33,
            largest_component_ratio=0.67,
            branch_convergence_ratio=0.0,
        ),
        fair_scoring=FairScoringBreakdownDTO(
            independent_error_count=0,
            cascading_fault_count=0,
            raw_penalty_points=0.0,
            deduplicated_penalty_points=0.0,
            dampened_savings_points=0.0,
        ),
    )

    rec = _make_execution_record(
        exec_id=exec_id,
        wf_id=wf_id,
        prof_id=prof_id,
        trace_events=[
            TraceEvent(
                v=1,
                timestamp=datetime.now(UTC),
                event_type="output",
                step_name=step_id,
                content={"fusion": fusion_result.model_dump(mode="json", exclude_none=True)},
            )
        ],
    )
    prof = _make_base_profile(prof_id, wf_id)
    wf = _make_base_workflow(wf_id, prof_id)

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_execution(rec)
    await mock_repo.save_output_profile(prof)
    await mock_repo.save_workflow(wf)

    distilled_dto = SynthesisDistillationDTO(
        distilled_inputs="Distilled inputs text",
        target_locale="en",
        title_map={"blk_0195f3a00000700283456789abcdef01": "Matrix 1"},
        matrices_to_explain=[
            MatrixExplanationContextDTO(
                real_matrix_id="blk_0195f3a00000700283456789abcdef01",
                matrix_id="m0",
                matrix_label="Matrix 1",
                score=2.0,
                justification="Justification",
            )
        ],
    )
    token_usage = TokenUsage(prompt_tokens=10, completion_tokens=10, total_tokens=20, cost_usd=0.001)
    shared_balanced_client = AsyncMock()

    with (
        patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo),
        patch(
            "backend_v2.workers.synthesis_worker.synthesis_distiller_hook",
            new_callable=AsyncMock,
            return_value=HookResult(success=True, state_delta=HookDeltaDTO(delta=distilled_dto)),
        ),
        patch(
            "backend_v2.workers.synthesis_worker.LLMClient.from_tier",
            new_callable=AsyncMock,
            return_value=shared_balanced_client,
        ),
        patch(
            "backend_v2.workers.synthesis_worker.create_executive_summary_task",
            new_callable=AsyncMock,
            return_value=(
                ExecutiveSummarySectionResult(
                    executive_summary=[ParagraphBlock(text="Exec", exact_quotes=[], citations=[])],
                    user_role=None,
                    user_role_justification=None,
                    cited_sources=[],
                ),
                token_usage,
            ),
        ) as mock_exec_task,
        patch(
            "backend_v2.workers.synthesis_worker.create_matrix_sections_tasks",
            new_callable=AsyncMock,
            return_value=[],
        ) as mock_matrix_task,
        patch(
            "backend_v2.workers.synthesis_worker.create_xai_highlights_task",
            new_callable=AsyncMock,
            return_value=None,
        ) as mock_xai_task,
        patch(
            "backend_v2.workers.synthesis_worker.create_row_explanations_task",
            new_callable=AsyncMock,
            return_value=None,
        ) as mock_row_task,
        patch(
            "backend_v2.workers.synthesis_worker.build_variance_metrics_and_task",
            new_callable=AsyncMock,
            return_value=(None, None),
        ),
        patch("backend_v2.workers.synthesis_worker.ReportService") as mock_report_service_cls,
    ):
        mock_svc = mock_report_service_cls.return_value
        mock_svc.get_or_create_default_artifact = AsyncMock()

        await generate_profile_synthesis_and_pdf_task(
            execution_id=exec_id,
            accept_language="en",
            profile_id=prof_id,
        )

        for task_mock in (
            mock_exec_task,
            mock_matrix_task,
            mock_xai_task,
            mock_row_task,
        ):
            task_mock.assert_awaited_once()
            assert task_mock.await_args is not None
            diag = task_mock.await_args.kwargs["causal_diagnosis"]
            assert diag is not None
            assert "Logical Cohesion: 0.33" in diag
            assert "Largest Connected Component Ratio: 0.67" in diag
            assert "Established Causal Chains (Premise -> Conclusion):" in diag
            assert (
                "- Foundational Premise -> Warranted Conclusion: "
                "Foundational Premise directly supports Warranted Conclusion." in diag
            )
            assert "Isolated Unlinked Claims (Degree-Zero Islands):" in diag
            assert "- Unlinked Deliverable Island" in diag


@pytest.mark.asyncio
async def test_synthesis_worker_corrupted_fusion_payload_in_trace_raises_app_exception() -> None:
    """Test generate_profile_synthesis_and_pdf_task raises AppException when fusion payload in final_inputs is corrupted."""
    prof_id = "pro_0195f3a00000700283456789abcdef01"
    wf_id = "wor_0195f3a00000700283456789abcdef01"
    exec_id = "exe_0195f3a00000700283456789abcdef01"
    step_id = generate_opaque_id(EntityPrefix.STEP)

    rec = _make_execution_record(
        exec_id=exec_id,
        wf_id=wf_id,
        prof_id=prof_id,
        trace_events=[
            TraceEvent(
                v=1,
                timestamp=datetime.now(UTC),
                event_type="output",
                step_name=step_id,
                content={"fusion": {"corrupted": "invalid_schema"}},
            )
        ],
    )
    prof = _make_base_profile(prof_id, wf_id)
    wf = _make_base_workflow(wf_id, prof_id)

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_execution(rec)
    await mock_repo.save_output_profile(prof)
    await mock_repo.save_workflow(wf)

    distilled_dto = SynthesisDistillationDTO(
        distilled_inputs="Distilled inputs text",
        target_locale="en",
        title_map={},
        matrices_to_explain=[],
    )

    with (
        patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo),
        patch(
            "backend_v2.workers.synthesis_worker.synthesis_distiller_hook",
            new_callable=AsyncMock,
            return_value=HookResult(success=True, state_delta=HookDeltaDTO(delta=distilled_dto)),
        ),
        patch("backend_v2.workers.synthesis_worker.LLMClient.from_tier", new_callable=AsyncMock),
    ):
        with pytest.raises(AppException) as exc_info:
            await generate_profile_synthesis_and_pdf_task(
                execution_id=exec_id,
                accept_language="en",
                profile_id=prof_id,
            )
        assert exc_info.value.status_code == 500


def test_causal_synthesis_brief_dto_extra_fields_raises_validation_error() -> None:
    """Test CausalSynthesisBriefDTO.model_validate raises ValidationError on unknown extra attribute."""
    with pytest.raises(ValidationError):
        CausalSynthesisBriefDTO.model_validate(
            {
                "intact_propositions": 1,
                "total_propositions": 2,
                "unknown_extra_field": "forbidden",
            }
        )


@pytest.mark.asyncio
async def test_synthesis_worker_data_starvation_short_circuits() -> None:
    """Test generate_profile_synthesis_and_pdf_task short-circuits when DataStarvationEvent is detected."""
    prof_id = "pro_0195f3a00000700283456789abcdef01"
    wf_id = "wor_0195f3a00000700283456789abcdef01"
    exec_id = "exe_0195f3a00000700283456789abcdef01"

    rec = _make_execution_record(
        exec_id=exec_id,
        wf_id=wf_id,
        prof_id=prof_id,
        status=ExecutionStatus.FAILED,
        trace_events=[
            TraceEvent(
                v=1,
                timestamp=datetime.now(UTC),
                event_type="output",
                step_name="stp_starvation",
                content=DataStarvationEvent(total_atoms=0, reason="insufficient atoms"),
            )
        ],
    )
    prof = _make_base_profile(prof_id, wf_id)
    wf = _make_base_workflow(wf_id, prof_id)

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_execution(rec)
    await mock_repo.save_output_profile(prof)
    await mock_repo.save_workflow(wf)

    with (
        patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo),
        patch(
            "backend_v2.workers.synthesis_worker.handle_starvation_if_detected",
            new_callable=AsyncMock,
            return_value=True,
        ) as mock_starvation,
    ):
        await generate_profile_synthesis_and_pdf_task(
            execution_id=exec_id,
            accept_language="en",
            profile_id=prof_id,
        )
        mock_starvation.assert_awaited_once()


@pytest.mark.asyncio
async def test_synthesis_worker_distiller_hook_missing_delta_raises() -> None:
    """Test generate_profile_synthesis_and_pdf_task raises AppException when hook_result.state_delta is None."""
    prof_id = "pro_0195f3a00000700283456789abcdef01"
    wf_id = "wor_0195f3a00000700283456789abcdef01"
    exec_id = "exe_0195f3a00000700283456789abcdef01"

    rec = _make_execution_record(exec_id=exec_id, wf_id=wf_id, prof_id=prof_id)
    prof = _make_base_profile(prof_id, wf_id)
    wf = _make_base_workflow(wf_id, prof_id)

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_execution(rec)
    await mock_repo.save_output_profile(prof)
    await mock_repo.save_workflow(wf)

    with (
        patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo),
        patch(
            "backend_v2.workers.synthesis_worker.synthesis_distiller_hook",
            new_callable=AsyncMock,
            return_value=HookResult(success=True, state_delta=None),
        ),
    ):
        with pytest.raises(AppException) as exc_info:
            await generate_profile_synthesis_and_pdf_task(
                execution_id=exec_id,
                accept_language="en",
                profile_id=prof_id,
            )
        assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_synthesis_worker_distiller_hook_invalid_delta_raises() -> None:
    """Test generate_profile_synthesis_and_pdf_task raises AppException when state_delta is invalid."""
    prof_id = "pro_0195f3a00000700283456789abcdef01"
    wf_id = "wor_0195f3a00000700283456789abcdef01"
    exec_id = "exe_0195f3a00000700283456789abcdef01"

    rec = _make_execution_record(exec_id=exec_id, wf_id=wf_id, prof_id=prof_id)
    prof = _make_base_profile(prof_id, wf_id)
    wf = _make_base_workflow(wf_id, prof_id)

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_execution(rec)
    await mock_repo.save_output_profile(prof)
    await mock_repo.save_workflow(wf)

    with (
        patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo),
        patch(
            "backend_v2.workers.synthesis_worker.synthesis_distiller_hook",
            new_callable=AsyncMock,
            return_value=HookResult(success=True, state_delta=HookDeltaDTO(delta=GlobalContextVarsDTO())),
        ),
    ):
        with pytest.raises(AppException) as exc_info:
            await generate_profile_synthesis_and_pdf_task(
                execution_id=exec_id,
                accept_language="en",
                profile_id=prof_id,
            )
        assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_synthesis_worker_validation_error_in_taskgroup_handled() -> None:
    """Test generate_profile_synthesis_and_pdf_task handles ValidationError converting to AppException."""
    prof_id = "pro_0195f3a00000700283456789abcdef01"
    wf_id = "wor_0195f3a00000700283456789abcdef01"
    exec_id = "exe_0195f3a00000700283456789abcdef01"

    rec = _make_execution_record(exec_id=exec_id, wf_id=wf_id, prof_id=prof_id)
    prof = _make_base_profile(prof_id, wf_id)
    wf = _make_base_workflow(wf_id, prof_id)

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_execution(rec)
    await mock_repo.save_output_profile(prof)
    await mock_repo.save_workflow(wf)

    distilled_dto = SynthesisDistillationDTO(
        distilled_inputs="Distilled inputs text",
        target_locale="en",
        title_map={},
        matrices_to_explain=[],
    )

    with (
        patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo),
        patch(
            "backend_v2.workers.synthesis_worker.synthesis_distiller_hook",
            new_callable=AsyncMock,
            return_value=HookResult(success=True, state_delta=HookDeltaDTO(delta=distilled_dto)),
        ),
        patch("backend_v2.workers.synthesis_worker.LLMClient.from_tier", new_callable=AsyncMock),
        patch(
            "backend_v2.workers.synthesis_worker.create_executive_summary_task",
            side_effect=ValidationError.from_exception_data("title", []),
        ),
    ):
        with pytest.raises(AppException) as exc_info:
            await generate_profile_synthesis_and_pdf_task(
                execution_id=exec_id,
                accept_language="en",
                profile_id=prof_id,
            )
        assert exc_info.value.status_code == 500


def test_audit_warning_baseline_verify_ceilings_all_zero() -> None:
    """Verify all 10 residual categories equal 0 in audit_warning_baseline."""
    assert CURRENT_RESIDUAL_CEILINGS == ResidualDebtCeilingsDTO(
        d=0,
        f=0,
        k=0,
        x=0,
        n=0,
        t=0,
        p=0,
        m=0,
        r=0,
        s=0,
    )
    live_counts = compute_census_counts()
    is_valid, _ = verify_residual_debt_ceilings(live_counts)
    assert is_valid is True
    assert live_counts.f == 0


def _build_strict_typed_synthesis_fixtures(
    prof_id: str,
    wf_id: str,
    exec_id: str,
    organization_id: str | None = None,
    raw_inputs_org_id: str | None = None,
) -> tuple[ExecutionRecord, OutputProfile, Workflow]:
    """Create ExecutionRecord, OutputProfile, and Workflow via direct typed constructors."""
    rec = ExecutionRecord(
        id=exec_id,
        workflow_id=wf_id,
        output_profile_id=prof_id,
        organization_id=organization_id,
        status=ExecutionStatus.PASSED,
        target_locale="en",
        metadata=ExecutionMetadata(),
        execution_trace=[],
        context_variables=ContextVariablesDTO(variables={}),
        raw_inputs=WorkflowInputs(organization_id=raw_inputs_org_id, dynamic_inputs={}),
        frozen_context=FrozenContext(
            compiled_prompts={},
            injected_theory=InjectedTheoryManifestDTO(theories={}),
            generated_schemas=GeneratedSchemaManifestDTO(schemas={}),
            ui_hints_snapshot={},
            mcp_tool_audit=[],
        ),
        steps=[],
        profile_syntheses={},
        source_identity_manifest={},
        models_used={},
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    prof = OutputProfile(
        organization_id="org_0195f3a0000070008000000000000001",
        id=prof_id,
        slug="prof_test_strict",
        workflow_id=wf_id,
        name=I18nText(translations={"en": "Strict Profile"}),
        target_block_order=[TargetBlockType.EXECUTIVE_SUMMARY_BLOCK],
        executive_summary_directive="Synthesize executive summary.",
        synthesis_length_constraint=500,
        tone_instruction="Objective",
        visible_metadata=[],
        matrix_visible_columns=[],
        visible_block_extensions=[],
        visible_workflow_extensions=[],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a00000700283456789abcdef01",
                title=I18nText(translations={"en": "Group 1"}),
                view_type=PresetView.METRICS_1D,
                target_blocks=["blk_0195f3a00000700283456789abcdef01"],
            )
        ],
        content_blocks=[],
    )
    wf = Workflow(
        organization_id="org_0195f3a0000070008000000000000001",
        id=wf_id,
        slug="wf_test_strict",
        name=I18nText(translations={"en": "Strict Workflow"}),
        description=I18nText(translations={"en": "Strict Description"}),
        status="draft",
        version=1,
        expected_inputs=[],
        steps=[],
        default_profile_id=prof_id,
        model_registry_id="mrg_0195f3a0000070018111222233334444",
        historical_context_mode=LaxHistoricalContextMode.DISABLED,
    )
    return rec, prof, wf


@pytest.mark.asyncio
async def test_synthesis_worker_propagates_tenant_organization_id_to_hook_and_llm_client() -> None:
    """Verify execution.organization_id is forwarded to GlobalContextVarsDTO and LLMClient.from_tier."""
    prof_id = "prf_0195f3a00000700283456789abcdef01"
    wf_id = "wf_0195f3a00000700283456789abcdef01"
    exec_id = "exe_0195f3a00000700283456789abcdef01"
    tenant_org_id = "org_0195f3a0000070008000000000000777"

    rec, prof, wf = _build_strict_typed_synthesis_fixtures(
        prof_id=prof_id,
        wf_id=wf_id,
        exec_id=exec_id,
        organization_id=tenant_org_id,
    )
    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_execution(rec)
    await mock_repo.save_output_profile(prof)
    await mock_repo.save_workflow(wf)

    distilled_dto = SynthesisDistillationDTO(
        distilled_inputs="Distilled inputs text",
        target_locale="en",
        title_map={},
        matrices_to_explain=[],
        source_alias_map={},
        alias_registry={},
    )
    token_usage = TokenUsage(prompt_tokens=10, completion_tokens=10, total_tokens=20, cost_usd=0.001)
    exec_summary_res = (
        ExecutiveSummarySectionResult(
            executive_summary=[ParagraphBlock(text="Executive summary synthesized.", exact_quotes=[], citations=[])],
            user_role=RoleClassification.ARCHITECT,
            user_role_justification="Strategic authority",
            cited_sources=[],
        ),
        token_usage,
    )

    with (
        patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo),
        patch(
            "backend_v2.workers.synthesis_worker.synthesis_distiller_hook",
            new_callable=AsyncMock,
            return_value=HookResult(success=True, state_delta=HookDeltaDTO(delta=distilled_dto)),
        ) as mock_distiller,
        patch(
            "backend_v2.workers.synthesis_worker.LLMClient.from_tier",
            new_callable=AsyncMock,
        ) as mock_from_tier,
        patch(
            "backend_v2.workers.synthesis_worker.create_executive_summary_task",
            new_callable=AsyncMock,
            return_value=exec_summary_res,
        ),
        patch(
            "backend_v2.workers.synthesis_worker.create_matrix_sections_tasks",
            new_callable=AsyncMock,
            return_value=[],
        ),
        patch(
            "backend_v2.workers.synthesis_worker.create_xai_highlights_task",
            new_callable=AsyncMock,
            return_value=None,
        ),
        patch(
            "backend_v2.workers.synthesis_worker.create_row_explanations_task",
            new_callable=AsyncMock,
            return_value=None,
        ),
        patch(
            "backend_v2.workers.synthesis_worker.build_variance_metrics_and_task",
            new_callable=AsyncMock,
            return_value=(None, None),
        ),
        patch("backend_v2.workers.synthesis_worker.ReportService") as mock_report_service_cls,
    ):
        mock_svc = mock_report_service_cls.return_value
        mock_svc.get_or_create_default_artifact = AsyncMock(
            return_value=MagicMock(id="rep_0195f3a00000700283456789abcdef01")
        )
        mock_svc.compile_and_persist_artifact = AsyncMock()

        await generate_profile_synthesis_and_pdf_task(
            execution_id=exec_id,
            accept_language="en",
            profile_id=prof_id,
        )

        mock_distiller.assert_awaited_once()
        assert mock_distiller.await_args is not None
        hook_state_arg = mock_distiller.await_args.args[0]
        assert hook_state_arg.global_context_vars.organization_id == tenant_org_id

        mock_from_tier.assert_awaited_once()
        assert mock_from_tier.await_args is not None
        assert mock_from_tier.await_args.kwargs["organization_id"] == tenant_org_id


@pytest.mark.asyncio
async def test_synthesis_worker_resolves_organization_id_from_raw_inputs_and_defaults_to_root_system() -> None:
    """Verify fallback to raw_inputs.organization_id and SystemOrganizations.ROOT_SYSTEM."""
    prof_id = "prf_0195f3a00000700283456789abcdef01"
    wf_id = "wf_0195f3a00000700283456789abcdef01"
    exec_id_raw = "exe_0195f3a00000700283456789abcdef02"
    exec_id_root = "exe_0195f3a00000700283456789abcdef03"
    raw_org_id = "org_0195f3a0000070008000000000000888"

    rec_raw, prof, wf = _build_strict_typed_synthesis_fixtures(
        prof_id=prof_id,
        wf_id=wf_id,
        exec_id=exec_id_raw,
        organization_id=None,
        raw_inputs_org_id=raw_org_id,
    )
    rec_root, _, _ = _build_strict_typed_synthesis_fixtures(
        prof_id=prof_id,
        wf_id=wf_id,
        exec_id=exec_id_root,
        organization_id=None,
        raw_inputs_org_id=None,
    )
    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_execution(rec_raw)
    await mock_repo.save_execution(rec_root)
    await mock_repo.save_output_profile(prof)
    await mock_repo.save_workflow(wf)

    distilled_dto = SynthesisDistillationDTO(
        distilled_inputs="Distilled inputs text",
        target_locale="en",
        title_map={},
        matrices_to_explain=[],
        source_alias_map={},
        alias_registry={},
    )
    token_usage = TokenUsage(prompt_tokens=10, completion_tokens=10, total_tokens=20, cost_usd=0.001)
    exec_summary_res = (
        ExecutiveSummarySectionResult(
            executive_summary=[ParagraphBlock(text="Executive summary synthesized.", exact_quotes=[], citations=[])],
            user_role=RoleClassification.ARCHITECT,
            user_role_justification="Strategic authority",
            cited_sources=[],
        ),
        token_usage,
    )

    with (
        patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo),
        patch(
            "backend_v2.workers.synthesis_worker.synthesis_distiller_hook",
            new_callable=AsyncMock,
            return_value=HookResult(success=True, state_delta=HookDeltaDTO(delta=distilled_dto)),
        ),
        patch(
            "backend_v2.workers.synthesis_worker.LLMClient.from_tier",
            new_callable=AsyncMock,
        ) as mock_from_tier,
        patch(
            "backend_v2.workers.synthesis_worker.create_executive_summary_task",
            new_callable=AsyncMock,
            return_value=exec_summary_res,
        ),
        patch(
            "backend_v2.workers.synthesis_worker.create_matrix_sections_tasks",
            new_callable=AsyncMock,
            return_value=[],
        ),
        patch(
            "backend_v2.workers.synthesis_worker.create_xai_highlights_task",
            new_callable=AsyncMock,
            return_value=None,
        ),
        patch(
            "backend_v2.workers.synthesis_worker.create_row_explanations_task",
            new_callable=AsyncMock,
            return_value=None,
        ),
        patch(
            "backend_v2.workers.synthesis_worker.build_variance_metrics_and_task",
            new_callable=AsyncMock,
            return_value=(None, None),
        ),
        patch("backend_v2.workers.synthesis_worker.ReportService") as mock_report_service_cls,
    ):
        mock_svc = mock_report_service_cls.return_value
        mock_svc.get_or_create_default_artifact = AsyncMock(
            return_value=MagicMock(id="rep_0195f3a00000700283456789abcdef01")
        )
        mock_svc.compile_and_persist_artifact = AsyncMock()

        await generate_profile_synthesis_and_pdf_task(
            execution_id=exec_id_raw,
            accept_language="en",
            profile_id=prof_id,
        )
        assert mock_from_tier.await_args is not None
        assert mock_from_tier.await_args.kwargs["organization_id"] == raw_org_id

        mock_from_tier.reset_mock()
        await generate_profile_synthesis_and_pdf_task(
            execution_id=exec_id_root,
            accept_language="en",
            profile_id=prof_id,
        )
        assert mock_from_tier.await_args is not None
        assert mock_from_tier.await_args.kwargs["organization_id"] == SystemOrganizations.ROOT_SYSTEM.value


@pytest.mark.asyncio
async def test_synthesis_worker_byok_secret_resolution_failure_fails_fast() -> None:
    """Verify ConfigurationError from LLMClient.from_tier marks render status failed and re-raises."""
    prof_id = "prf_0195f3a00000700283456789abcdef01"
    wf_id = "wf_0195f3a00000700283456789abcdef01"
    exec_id = "exe_0195f3a00000700283456789abcdef04"

    rec, prof, wf = _build_strict_typed_synthesis_fixtures(
        prof_id=prof_id,
        wf_id=wf_id,
        exec_id=exec_id,
        organization_id="org_0195f3a0000070008000000000000777",
    )
    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_execution(rec)
    await mock_repo.save_output_profile(prof)
    await mock_repo.save_workflow(wf)

    distilled_dto = SynthesisDistillationDTO(
        distilled_inputs="Distilled inputs text",
        target_locale="en",
        title_map={},
        matrices_to_explain=[],
        source_alias_map={},
        alias_registry={},
    )

    with (
        patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo),
        patch(
            "backend_v2.workers.synthesis_worker.synthesis_distiller_hook",
            new_callable=AsyncMock,
            return_value=HookResult(success=True, state_delta=HookDeltaDTO(delta=distilled_dto)),
        ),
        patch(
            "backend_v2.workers.synthesis_worker.LLMClient.from_tier",
            new_callable=AsyncMock,
            side_effect=ConfigurationError(
                message="BYOK decryption failed for tenant org_0195f3a0000070008000000000000777",
                details={"error_code": ErrorCodes.SECRET_RESOLUTION_FAILED.value},
            ),
        ),
        pytest.raises(ConfigurationError) as exc_info,
    ):
        await generate_profile_synthesis_and_pdf_task(
            execution_id=exec_id,
            accept_language="en",
            profile_id=prof_id,
        )

    assert exc_info.value.details["error_code"] == ErrorCodes.SECRET_RESOLUTION_FAILED.value
    updated_exec = await mock_repo.get_execution(exec_id)
    assert updated_exec is not None
    assert updated_exec.status == ExecutionStatus.PASSED
    assert updated_exec.status_message is not None
    assert f"Synthesis failed for profile {prof_id}:" in updated_exec.status_message
