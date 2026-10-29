"""Unit tests for synthesis_worker.py covering error handling, caching, validation, and full execution."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from backend_v2.core.hook_registry import HookDeltaDTO, HookResult
from backend_v2.exceptions import AppException, ResourceNotFoundError
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord, ExecutionStep
from backend_v2.models.domain.output_profile import MatrixSynthesisGroup, OutputProfile
from backend_v2.models.domain.synthesis import RenderedSynthesisCache
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
from backend_v2.models.dtos.global_context import GlobalContextVarsDTO
from backend_v2.models.dtos.step_output import StepOutputDTO
from backend_v2.models.dtos.synthesis import (
    ExecutiveSummarySectionResult,
    MatrixExplanationContextDTO,
    MatrixExplanationsResult,
    MatrixSectionSynthesesResult,
    SynthesisDistillationDTO,
    SynthesisSectionDTO,
    XaiHighlightsResult,
)
from backend_v2.models.enums import (
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


def _make_base_profile(prof_id: str, wf_id: str) -> OutputProfile:
    return OutputProfile(
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
    return Workflow(
        id=wf_id,
        slug="test_wf",
        name=I18nText(translations={"en": "Test Workflow"}),
        description=I18nText(translations={"en": "Desc"}),
        status="draft",
        version=1,
        steps=[],
        default_profile_id=prof_id,
        model_registry_id="sys_0195f3a0000070018111222233334444",
        historical_context_mode=LaxHistoricalContextMode.DISABLED,
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

    with patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=mock_repo):
            await generate_profile_synthesis_and_pdf_task(
                execution_id="exe_missing", accept_language="en", profile_id="pro_1"
            )
            assert (await mock_repo.get_execution("exe_missing")) is None


@pytest.mark.asyncio
async def test_synthesis_worker_already_synthesized_enqueues_pdf() -> None:
    """Test generate_profile_synthesis_and_pdf_task short-circuits to report artifact generation if already synthesized."""
    prof_id = "pro_0195f3a00000700283456789abcdef01"
    cache = RenderedSynthesisCache()
    rec = ExecutionRecord(
        id="exe_0195f3a00000700283456789abcdef01",
        workflow_id="wor_0195f3a00000700283456789abcdef01",
        output_profile_id=prof_id,
        status=ExecutionStatus.PASSED,
        target_locale="en",
        metadata=ExecutionMetadata(),
        profile_syntheses={prof_id: cache},
    )
    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_execution(rec)
    mock_redis = AsyncMock()
    mock_artifact = MagicMock()
    mock_artifact.id = "rep_0195f3a00000700283456789abcdef01"

    with patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=mock_repo):
            with patch("backend_v2.workers.synthesis_worker.ReportService") as mock_report_service_cls:
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
    rec = ExecutionRecord(
        id="exe_0195f3a00000700283456789abcdef01",
        workflow_id="wor_0195f3a00000700283456789abcdef01",
        output_profile_id=prof_id,
        status=ExecutionStatus.PASSED,
        target_locale="en",
        metadata=ExecutionMetadata(),
    )
    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_execution(rec)

    with patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=mock_repo):
            with pytest.raises(ResourceNotFoundError):
                await generate_profile_synthesis_and_pdf_task(
                    execution_id="exe_0195f3a00000700283456789abcdef01",
                    accept_language="en",
                    profile_id=prof_id,
                )


@pytest.mark.asyncio
async def test_synthesis_worker_workflow_not_found_raises() -> None:
    """Test generate_profile_synthesis_and_pdf_task raises AppException if workflow missing."""
    prof_id = "pro_0195f3a00000700283456789abcdef01"
    rec = ExecutionRecord(
        id="exe_0195f3a00000700283456789abcdef01",
        workflow_id="wor_0195f3a00000700283456789abcdef01",
        output_profile_id=prof_id,
        status=ExecutionStatus.PASSED,
        target_locale="en",
        metadata=ExecutionMetadata(),
    )
    prof = OutputProfile(
        id=prof_id,
        slug="prof_test",
        workflow_id="wor_0195f3a00000700283456789abcdef01",
        name=I18nText(translations={"en": "Test Profile"}),
        target_block_order=[TargetBlockType.EXECUTIVE_SUMMARY_BLOCK],
    )
    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_execution(rec)
    await mock_repo.save_output_profile(prof)

    with patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=mock_repo):
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

    rec = ExecutionRecord(
        id=exec_id,
        workflow_id=wf_id,
        output_profile_id=prof_id,
        status=ExecutionStatus.PASSED,
        target_locale="en",
        metadata=ExecutionMetadata(),
        step_states={
            f"sys_render_{prof_id}": ExecutionStep(
                id=f"sys_render_{prof_id}",
                label="Initial",
                status=ExecutionStatus.QUEUED,
                progress=0,
                has_warning=False,
            )
        },
        execution_trace=[
            TraceEvent(
                v=1,
                timestamp=datetime.now(timezone.utc),
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

    import backend_v2.workers.synthesis_worker as synthesis_worker_mod

    with patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock):
        with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
            with patch(
                "backend_v2.workers.synthesis_worker.synthesis_distiller_hook",
                new_callable=AsyncMock,
                return_value=HookResult(
                    success=True, state_delta=HookDeltaDTO(delta=distilled_dto.model_dump(mode="json"))
                ),
            ):
                with patch("backend_v2.workers.synthesis_worker.LLMClient.from_tier", new_callable=AsyncMock):
                    with patch(
                        "backend_v2.workers.synthesis_worker.create_executive_summary_task",
                        new_callable=AsyncMock,
                        return_value=exec_summary_res,
                    ) as mock_exec_task:
                        with patch(
                            "backend_v2.workers.synthesis_worker.create_matrix_sections_tasks",
                            new_callable=AsyncMock,
                            return_value=matrix_sections_res,
                        ):
                            with patch(
                                "backend_v2.workers.synthesis_worker.create_xai_highlights_task",
                                new_callable=AsyncMock,
                                return_value=xai_res,
                            ):
                                with patch(
                                    "backend_v2.workers.synthesis_worker.create_row_explanations_task",
                                    new_callable=AsyncMock,
                                    return_value=row_res,
                                ):
                                    with patch(
                                        "backend_v2.workers.synthesis_worker.build_variance_metrics_and_task",
                                        new_callable=AsyncMock,
                                        return_value=var_res,
                                    ):
                                        with patch(
                                            "backend_v2.workers.synthesis_worker.ReportService"
                                        ) as mock_report_service_cls:
                                            mock_svc = mock_report_service_cls.return_value
                                            mock_svc.get_or_create_default_artifact = AsyncMock(
                                                return_value=mock_artifact
                                            )
                                            mock_svc.compile_and_persist_artifact = AsyncMock()

                                            await generate_profile_synthesis_and_pdf_task(
                                                execution_id=exec_id,
                                                accept_language="en",
                                                profile_id=prof_id,
                                                redis=mock_redis,
                                            )

                                            # Verify causal diagnosis was passed to create_executive_summary_task
                                            mock_exec_task.assert_awaited_once()
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
async def test_synthesis_worker_with_causal_graph_payload_in_step_states() -> None:
    """Test causal diagnosis extraction from execution.step_states containing CausalGraphPayloadDTO."""
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

    rec = ExecutionRecord.model_construct(
        id=exec_id,
        workflow_id=wf_id,
        output_profile_id=prof_id,
        status=ExecutionStatus.PASSED,
        target_locale="en",
        metadata=ExecutionMetadata(),
        step_states={
            "causal_step": StepOutputDTO(
                step_id="stp_0195f3a00000700283456789abcdef01",
                block_id="blk_0195f3a00000700283456789abcdef01",
                data_type="causal",
                payload=graph_payload,
            )
        },
        execution_trace=[],
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

    import backend_v2.workers.synthesis_worker as synthesis_worker_mod

    with patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock):
        with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
            with patch(
                "backend_v2.workers.synthesis_worker.synthesis_distiller_hook",
                new_callable=AsyncMock,
                return_value=HookResult(
                    success=True, state_delta=HookDeltaDTO(delta=distilled_dto.model_dump(mode="json"))
                ),
            ):
                with patch("backend_v2.workers.synthesis_worker.LLMClient.from_tier", new_callable=AsyncMock):
                    with patch(
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
                    ) as mock_exec_task:
                        with patch(
                            "backend_v2.workers.synthesis_worker.create_matrix_sections_tasks",
                            new_callable=AsyncMock,
                            return_value=[],
                        ):
                            with patch(
                                "backend_v2.workers.synthesis_worker.create_xai_highlights_task",
                                new_callable=AsyncMock,
                                return_value=None,
                            ):
                                with patch(
                                    "backend_v2.workers.synthesis_worker.create_row_explanations_task",
                                    new_callable=AsyncMock,
                                    return_value=None,
                                ):
                                    with patch(
                                        "backend_v2.workers.synthesis_worker.build_variance_metrics_and_task",
                                        new_callable=AsyncMock,
                                        return_value=(None, None),
                                    ):
                                        with patch(
                                            "backend_v2.workers.synthesis_worker.ReportService"
                                        ) as mock_report_service_cls:
                                            mock_svc = mock_report_service_cls.return_value
                                            mock_svc.get_or_create_default_artifact = AsyncMock()

                                            await generate_profile_synthesis_and_pdf_task(
                                                execution_id=exec_id,
                                                accept_language="en",
                                                profile_id=prof_id,
                                            )

                                            mock_exec_task.assert_awaited_once()
                                            causal_diag = mock_exec_task.await_args.kwargs["causal_diagnosis"]
                                            assert causal_diag is not None
                                            assert "Total Propositions: 1" in causal_diag
                                            assert "Cycle Detected: False" in causal_diag
                                            assert "Root Cause Node IDs: node_0" in causal_diag


@pytest.mark.asyncio
async def test_synthesis_worker_data_starvation_short_circuits() -> None:
    """Test generate_profile_synthesis_and_pdf_task short-circuits when DataStarvationEvent is detected."""
    prof_id = "pro_0195f3a00000700283456789abcdef01"
    wf_id = "wor_0195f3a00000700283456789abcdef01"
    exec_id = "exe_0195f3a00000700283456789abcdef01"

    rec = ExecutionRecord(
        id=exec_id,
        workflow_id=wf_id,
        output_profile_id=prof_id,
        status=ExecutionStatus.FAILED,
        target_locale="en",
        metadata=ExecutionMetadata(),
        execution_trace=[
            TraceEvent(
                v=1,
                timestamp=datetime.now(timezone.utc),
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

    import backend_v2.workers.synthesis_worker as synthesis_worker_mod

    with patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock):
        with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
            with patch(
                "backend_v2.workers.synthesis_worker.handle_starvation_if_detected",
                new_callable=AsyncMock,
                return_value=True,
            ) as mock_starvation:
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

    rec = ExecutionRecord(
        id=exec_id,
        workflow_id=wf_id,
        output_profile_id=prof_id,
        status=ExecutionStatus.PASSED,
        target_locale="en",
        metadata=ExecutionMetadata(),
    )
    prof = _make_base_profile(prof_id, wf_id)
    wf = _make_base_workflow(wf_id, prof_id)

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_execution(rec)
    await mock_repo.save_output_profile(prof)
    await mock_repo.save_workflow(wf)

    import backend_v2.workers.synthesis_worker as synthesis_worker_mod

    with patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock):
        with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
            with patch(
                "backend_v2.workers.synthesis_worker.synthesis_distiller_hook",
                new_callable=AsyncMock,
                return_value=HookResult(success=True, state_delta=None),
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

    rec = ExecutionRecord(
        id=exec_id,
        workflow_id=wf_id,
        output_profile_id=prof_id,
        status=ExecutionStatus.PASSED,
        target_locale="en",
        metadata=ExecutionMetadata(),
    )
    prof = _make_base_profile(prof_id, wf_id)
    wf = _make_base_workflow(wf_id, prof_id)

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_execution(rec)
    await mock_repo.save_output_profile(prof)
    await mock_repo.save_workflow(wf)

    import backend_v2.workers.synthesis_worker as synthesis_worker_mod

    with patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock):
        with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
            with patch(
                "backend_v2.workers.synthesis_worker.synthesis_distiller_hook",
                new_callable=AsyncMock,
                return_value=HookResult(
                    success=True,
                    state_delta=HookDeltaDTO(delta=GlobalContextVarsDTO()),
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

    rec = ExecutionRecord(
        id=exec_id,
        workflow_id=wf_id,
        output_profile_id=prof_id,
        status=ExecutionStatus.PASSED,
        target_locale="en",
        metadata=ExecutionMetadata(),
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

    import backend_v2.workers.synthesis_worker as synthesis_worker_mod

    with patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock):
        with patch.object(synthesis_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo):
            with patch(
                "backend_v2.workers.synthesis_worker.synthesis_distiller_hook",
                new_callable=AsyncMock,
                return_value=HookResult(
                    success=True, state_delta=HookDeltaDTO(delta=distilled_dto.model_dump(mode="json"))
                ),
            ):
                with patch("backend_v2.workers.synthesis_worker.LLMClient.from_tier", new_callable=AsyncMock):
                    with patch(
                        "backend_v2.workers.synthesis_worker.create_executive_summary_task",
                        side_effect=ValidationError.from_exception_data("title", []),
                    ):
                        with pytest.raises(AppException) as exc_info:
                            await generate_profile_synthesis_and_pdf_task(
                                execution_id=exec_id,
                                accept_language="en",
                                profile_id=prof_id,
                            )
                        assert exc_info.value.status_code == 500
