"""Unit tests for BlueprintTransformer costs, tokens, negative boundaries, and SDUI synchronization."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import User, UserRole
from backend_v2.models.core_base import I18nText, generate_uuid7
from backend_v2.models.domain.execution import ExecutionStepState
from backend_v2.models.domain.matrix import MatrixClaim, MatrixScale, TDAAssertion
from backend_v2.models.domain.synthesis import MatrixSynthesisGroup
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
from backend_v2.models.dtos.matrix_scorecard import ScorecardAtomDTO
from backend_v2.models.dtos.node_execution import StepOutputContentValue
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.dtos.trace import StepTraceMetadataDTO, TraceEventMetadataDTO, TraceMatrixPayloadDTO
from backend_v2.models.enums import (
    BlockDataType,
    DisplayScale,
    ExecutionStatus,
    HistoricalContextMode,
    PromptBlockCategory,
    TargetBlockType,
    VirtualSystemStepID,
    VisualIntent,
)
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import TraceEvent
from backend_v2.models.view.sdui import SduiMetadataBlock
from backend_v2.services.blueprint import BlueprintTransformer
from backend_v2.services.localization import LocalizationService
from backend_v2.tests.factories.model_factories import (
    CausalGraphPayloadDTOFactory,
    CausalNodeDTOFactory,
    ExecutionRecordFactory,
    MatrixPromptBlockFactory,
    OutputProfileFactory,
    WorkflowFactory,
)
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository

_WORKFLOW_ID = "wf_0195f3a0000070008123456789abcdef"
_PROFILE_ID = "prf_0195f3a0000070008123456789abcdef"
_USER_ID = "usr_0195f3a0000070008123456789abcdef"
_ORG_ID = "org_0195f3a0000070008123456789abcdef"
_BLOCK_ID = "blk_0195f3a0000070008123456789abcdef"
_STEP_ID = "sr_0195f3a0000070008123456789abcdef"


class _UserFactory(ModelFactory[User]):
    """Hermetic Polyfactory builder for User domain models."""

    __model__ = User


class _MCPAuditTraceFactory(ModelFactory[MCPAuditTrace]):
    """Hermetic Polyfactory builder for MCPAuditTrace entries."""

    __model__ = MCPAuditTrace


def _make_trace_event(
    step_name: str,
    event_type: Literal[
        "input", "reasoning", "decision", "error", "output", "tombstone", "evidence_override", "progress"
    ],
    content: dict[str, StepOutputContentValue],
    step_metadata: StepTraceMetadataDTO | None = None,
) -> TraceEvent:
    """Build a strictly typed TraceEvent instance for unit tests.

    Args:
        step_name: Emitting step identifier.
        event_type: Canonical trace event discriminator.
        content: Mapping of step output keys to content values.
        step_metadata: Optional step telemetry metadata attached to event metadata.

    Returns:
        Validated TraceEvent instance.
    """
    return TraceEvent(
        event_id=generate_uuid7(),
        timestamp=datetime.now(UTC),
        step_name=step_name,
        event_type=event_type,
        content=content,
        metadata=TraceEventMetadataDTO(mcp_audit_traces=[], step_metadata=step_metadata),
        mcp_audit_traces=[],
    )


@pytest.fixture
def mock_blueprint_repos() -> InMemoryUnifiedWorkflowRepository:
    """Create a hermetic in-memory repository suite for BlueprintTransformer testing.

    Returns:
        Configured InMemoryUnifiedWorkflowRepository instance.
    """
    repo = InMemoryUnifiedWorkflowRepository()

    profile = OutputProfileFactory.build(
        id=_PROFILE_ID,
        slug="default",
        workflow_id=_WORKFLOW_ID,
        name=I18nText(translations={"en": "Executive Summary", "fi": "Johdon yhteenveto"}),
        display_scale=DisplayScale.ORIGINAL,
        content_blocks=[],
        target_block_order=[TargetBlockType.METADATA_BLOCK],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a0000070008000000000000001",
                title=I18nText(translations={"en": "Default", "fi": "Oletus"}),
                target_blocks=["*"],
            )
        ],
        visible_metadata=["user", "organization", "date", "cost", "tokens"],
        matrix_visible_columns=["label", "raw_score", "distribution", "row_explanation"],
    )

    workflow = WorkflowFactory.build(
        id=_WORKFLOW_ID,
        slug="test_workflow",
        description=I18nText(translations={"en": "Workflow", "fi": "Työnkulku"}),
        status="published",
        version=1,
        name=I18nText(translations={"en": "Test Workflow", "fi": "Testi työnkulku"}),
        default_profile_id=_PROFILE_ID,
        historical_context_mode=HistoricalContextMode.DISABLED,
        model_registry_id="sys_0195f3a00000700e826807f3bfa3454d",
        default_strictness_level=85,
        steps=[],
    )

    user = _UserFactory.build(
        id=_USER_ID,
        email="auditor@example.com",
        name="Lead Auditor",
        role=UserRole.ADMIN,
        is_active=True,
        language="fi",
        theme_mode="system",
        created_at=datetime.now(UTC),
    )

    repo.set_workflow(workflow)
    repo.set_output_profiles([profile])
    repo.set_user(user)
    return repo


def _make_transformer(repo: InMemoryUnifiedWorkflowRepository) -> BlueprintTransformer:
    """Instantiate BlueprintTransformer bound to the in-memory repository fake.

    Args:
        repo: In-memory unified repository instance.

    Returns:
        Configured BlueprintTransformer instance.
    """
    return BlueprintTransformer(
        exec_repo=repo,
        workflow_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        system_repo=repo,
    )


@pytest.mark.asyncio
async def test_blueprint_combined_cost_and_tokens_from_execution_record(
    mock_blueprint_repos: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify combined cost and token aggregation from ExecutionRecord top-level fields."""
    exec_id = "exe_0195f3a0000070008000000000000001"
    record = ExecutionRecordFactory.build(
        id=exec_id,
        workflow_id=_WORKFLOW_ID,
        status=ExecutionStatus.PASSED,
        progress=100,
        status_message="Completed",
        execution_trace=[],
        output_profile_id=_PROFILE_ID,
        metadata=ExecutionMetadata(),
        target_locale="fi",
        created_by=_USER_ID,
        dag_cost_usd=1.88,
        prompt_tokens=1000,
        completion_tokens=500,
        reasoning_tokens=200,
        cumulative_synthesis_cost=0.45,
        cumulative_synthesis_tokens=300,
    )
    await mock_blueprint_repos.save_execution(record)

    transformer = _make_transformer(mock_blueprint_repos)
    dto = await transformer.build_report_dto(exec_id, profile_id=_PROFILE_ID)

    assert isinstance(dto, ReportDataDTO)
    assert dto.cost_estimate is not None
    assert dto.cost_estimate == pytest.approx(2.33)
    assert dto.total_tokens == 2000
    assert dto.prompt_tokens == 1000
    assert dto.completion_tokens == 500
    assert dto.reasoning_tokens == 200

    metadata_blocks = [b for b in dto.inner_sdui_blocks if isinstance(b, SduiMetadataBlock)]
    assert len(metadata_blocks) == 1
    meta_block = metadata_blocks[0]
    assert meta_block.costs == LocalizationService.format_cost(dto.cost_estimate, "fi")
    assert meta_block.tokens == {"total": "2000"}


@pytest.mark.asyncio
async def test_blueprint_trace_fail_safe_when_dag_cost_zero(
    mock_blueprint_repos: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify that when dag_cost_usd is 0.0, tokens and costs are recovered from trace metadata."""
    exec_id = "exe_0195f3a0000070008000000000000002"
    meta_dto = StepTraceMetadataDTO(
        model_strategy="fast",
        physical_model="gemini-2.5-flash",
        system_fingerprint="fp_test_123",
        token_usage=TokenUsage(
            prompt_tokens=400,
            completion_tokens=100,
            cached_tokens=50,
            reasoning_tokens=50,
            total_tokens=550,
            cost_usd=0.85,
        ),
    )

    event_with_metadata = _make_trace_event(
        step_name="step_extract_evidence",
        event_type="output",
        content={
            "id": _BLOCK_ID,
            "block_type": "text_block",
            "text": "Evidence extraction findings",
            "step_metadata": meta_dto,
        },
    )

    record = ExecutionRecordFactory.build(
        id=exec_id,
        workflow_id=_WORKFLOW_ID,
        status=ExecutionStatus.PASSED,
        progress=100,
        status_message="Completed",
        execution_trace=[event_with_metadata],
        output_profile_id=_PROFILE_ID,
        metadata=ExecutionMetadata(),
        target_locale="fi",
        created_by=_USER_ID,
        dag_cost_usd=0.0,
        prompt_tokens=0,
        completion_tokens=0,
        reasoning_tokens=0,
        cumulative_synthesis_cost=0.12,
        cumulative_synthesis_tokens=150,
    )
    await mock_blueprint_repos.save_execution(record)

    transformer = _make_transformer(mock_blueprint_repos)
    dto = await transformer.build_report_dto(exec_id, profile_id=_PROFILE_ID)

    assert isinstance(dto, ReportDataDTO)
    assert dto.cost_estimate is not None
    assert dto.cost_estimate == pytest.approx(0.97)
    assert dto.total_tokens == 700
    assert dto.prompt_tokens == 400
    assert dto.completion_tokens == 100
    assert dto.reasoning_tokens == 50

    metadata_blocks = [b for b in dto.inner_sdui_blocks if isinstance(b, SduiMetadataBlock)]
    assert len(metadata_blocks) == 1
    meta_block = metadata_blocks[0]
    assert meta_block.costs == LocalizationService.format_cost(dto.cost_estimate, "fi")
    assert meta_block.tokens == {"total": "700"}


@pytest.mark.asyncio
async def test_blueprint_consecutive_synthesis_accumulation(
    mock_blueprint_repos: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify monotonic accumulation of synthesis costs across consecutive runs."""
    exec_id = "exe_0195f3a0000070008000000000000003"
    base_record = ExecutionRecordFactory.build(
        id=exec_id,
        workflow_id=_WORKFLOW_ID,
        status=ExecutionStatus.PASSED,
        progress=100,
        status_message="Completed",
        execution_trace=[],
        output_profile_id=_PROFILE_ID,
        metadata=ExecutionMetadata(),
        target_locale="fi",
        created_by=_USER_ID,
        dag_cost_usd=1.00,
        prompt_tokens=500,
        completion_tokens=100,
        reasoning_tokens=0,
        cumulative_synthesis_cost=0.20,
        cumulative_synthesis_tokens=200,
    )

    transformer = _make_transformer(mock_blueprint_repos)

    await mock_blueprint_repos.save_execution(base_record)
    dto1 = await transformer.build_report_dto(exec_id, profile_id=_PROFILE_ID)
    assert dto1.cost_estimate is not None
    assert dto1.cost_estimate == pytest.approx(1.20)
    assert dto1.total_tokens == 800

    accumulated_record = base_record.model_copy(
        update={
            "cumulative_synthesis_cost": 0.50,
            "cumulative_synthesis_tokens": 500,
        }
    )
    await mock_blueprint_repos.save_execution(accumulated_record)
    dto2 = await transformer.build_report_dto(exec_id, profile_id=_PROFILE_ID)
    assert dto2.cost_estimate is not None
    assert dto2.total_tokens is not None
    assert dto2.cost_estimate == pytest.approx(1.50)
    assert dto2.total_tokens == 1100
    assert dto2.cost_estimate > dto1.cost_estimate
    assert dto2.total_tokens > dto1.total_tokens


@pytest.mark.asyncio
async def test_blueprint_zero_tokens_and_cost_boundary(
    mock_blueprint_repos: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify boundary condition when execution has zero tokens, zero cost, and empty trace."""
    exec_id = "exe_0195f3a0000070008000000000000004"
    record = ExecutionRecordFactory.build(
        id=exec_id,
        workflow_id=_WORKFLOW_ID,
        status=ExecutionStatus.PASSED,
        progress=100,
        status_message="Completed",
        execution_trace=[],
        output_profile_id=_PROFILE_ID,
        metadata=ExecutionMetadata(),
        target_locale="fi",
        created_by=_USER_ID,
        dag_cost_usd=0.0,
        prompt_tokens=0,
        completion_tokens=0,
        reasoning_tokens=0,
        cumulative_synthesis_cost=0.0,
        cumulative_synthesis_tokens=0,
    )
    await mock_blueprint_repos.save_execution(record)

    transformer = _make_transformer(mock_blueprint_repos)
    dto = await transformer.build_report_dto(exec_id, profile_id=_PROFILE_ID)

    assert isinstance(dto, ReportDataDTO)
    assert dto.cost_estimate == 0.0
    assert dto.total_tokens == 0
    assert dto.prompt_tokens == 0
    assert dto.completion_tokens == 0
    assert dto.reasoning_tokens == 0


@pytest.mark.asyncio
async def test_blueprint_negative_malformed_results_hydrated_refs_and_causal_blocks(
    mock_blueprint_repos: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify negative boundaries where folded results, hydrated_references, or causal blocks fail validation."""
    transformer = _make_transformer(mock_blueprint_repos)

    bad_results_exec_id = "exe_0195f3a0000070008000000000000005"
    await mock_blueprint_repos.save_execution(
        ExecutionRecordFactory.build(
            id=bad_results_exec_id,
            workflow_id=_WORKFLOW_ID,
            status=ExecutionStatus.PASSED,
            execution_trace=[
                _make_trace_event(
                    step_name="step_bad_results",
                    event_type="output",
                    content={"results": "invalid_scalar_results_payload"},
                )
            ],
            output_profile_id=_PROFILE_ID,
            metadata=ExecutionMetadata(),
            target_locale="fi",
        )
    )
    with pytest.raises(AppException) as exc_results:
        await transformer.build_report_dto(bad_results_exec_id, profile_id=_PROFILE_ID)
    assert exc_results.value.status_code == 500
    assert exc_results.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    bad_refs_exec_id = "exe_0195f3a0000070008000000000000006"
    await mock_blueprint_repos.save_execution(
        ExecutionRecordFactory.build(
            id=bad_refs_exec_id,
            workflow_id=_WORKFLOW_ID,
            status=ExecutionStatus.PASSED,
            execution_trace=[
                _make_trace_event(
                    step_name="step_bad_refs",
                    event_type="output",
                    content={"hydrated_references": "invalid_scalar_refs_payload"},
                )
            ],
            output_profile_id=_PROFILE_ID,
            metadata=ExecutionMetadata(),
            target_locale="fi",
        )
    )
    with pytest.raises(AppException) as exc_refs:
        await transformer.build_report_dto(bad_refs_exec_id, profile_id=_PROFILE_ID)
    assert exc_refs.value.status_code == 500
    assert exc_refs.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    bad_causal_exec_id = "exe_0195f3a0000070008000000000000007"
    await mock_blueprint_repos.save_execution(
        ExecutionRecordFactory.build(
            id=bad_causal_exec_id,
            workflow_id=_WORKFLOW_ID,
            status=ExecutionStatus.PASSED,
            execution_trace=[
                _make_trace_event(
                    step_name="step_bad_causal",
                    event_type="output",
                    content={"graph": "invalid_scalar_graph_payload"},
                )
            ],
            output_profile_id=_PROFILE_ID,
            metadata=ExecutionMetadata(),
            target_locale="fi",
        )
    )
    with pytest.raises(AppException) as exc_causal:
        await transformer.build_report_dto(bad_causal_exec_id, profile_id=_PROFILE_ID)
    assert exc_causal.value.status_code == 500
    assert exc_causal.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_blueprint_identity_app_exception_passthrough_and_cleanup(
    mock_blueprint_repos: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify typed AppException raised by identity repository is re-raised intact with scoped fault cleanup."""
    exec_id = "exe_0195f3a0000070008000000000000008"
    await mock_blueprint_repos.save_execution(
        ExecutionRecordFactory.build(
            id=exec_id,
            workflow_id=_WORKFLOW_ID,
            organization_id=_ORG_ID,
            created_by=_USER_ID,
            status=ExecutionStatus.PASSED,
            execution_trace=[],
            output_profile_id=_PROFILE_ID,
            metadata=ExecutionMetadata(),
            target_locale="fi",
        )
    )
    transformer = _make_transformer(mock_blueprint_repos)

    storage_err = AppException(
        message="Database connection interrupted",
        status_code=503,
        details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
    )
    try:
        mock_blueprint_repos.inject_fault("get_organization_model", storage_err)
        with pytest.raises(AppException) as exc_org:
            await transformer.build_report_dto(exec_id, profile_id=_PROFILE_ID)
        assert exc_org.value.status_code == 503
        assert exc_org.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value
    finally:
        mock_blueprint_repos.clear_faults("get_organization_model")

    try:
        mock_blueprint_repos.inject_fault("get_user", storage_err)
        with pytest.raises(AppException) as exc_user:
            await transformer.build_report_dto(exec_id, profile_id=_PROFILE_ID)
        assert exc_user.value.status_code == 503
        assert exc_user.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value
    finally:
        mock_blueprint_repos.clear_faults("get_user")


@pytest.mark.asyncio
async def test_blueprint_event_metadata_warning_and_mcp_axis_enrichment(
    mock_blueprint_repos: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify event.metadata.step_metadata usage recovery, HAS_WARNING flag, and MCP reverse axis mapping."""
    atom_id = "tda_0195f3a0000070008000000000000001"
    mcp_ev_id_1 = "mcp_0195f3a0000070008000000000000001"
    mcp_ev_id_2 = "mcp_0195f3a0000070008000000000000002"

    pb = MatrixPromptBlockFactory.build(
        id=_BLOCK_ID,
        slug="matrix_axis",
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        is_evaluative=True,
        label=I18nText(translations={"en": "Evidence Axis", "fi": "Todisteakseli"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        scales=[
            MatrixScale(score=1, name=I18nText(translations={"en": "Low", "fi": "Matala"}), ai_label="LOW", claims=[]),
            MatrixScale(
                score=5,
                name=I18nText(translations={"en": "High", "fi": "Korkea"}),
                ai_label="HIGH",
                claims=[
                    MatrixClaim(
                        label=I18nText(translations={"en": "Verified Claim", "fi": "Varmennettu väite"}),
                        tda_assertions=[
                            TDAAssertion(
                                tda_id=atom_id,
                                concept_description="Verified claim assertion description",
                                inverse_evidence=False,
                                aggregation_mode="EXISTS",
                                facts_to_find=[],
                                acceptance_criteria=[],
                                anti_patterns=[],
                                syntactic_anchors=[],
                                depends_on=(),
                            )
                        ],
                    )
                ],
            ),
        ],
    )
    mock_blueprint_repos.set_prompt_blocks([pb])

    step_state = ExecutionStepState(
        id=_STEP_ID,
        label="Evaluation Step",
        status=ExecutionStatus.PASSED,
        scorecard_atoms={
            atom_id: ScorecardAtomDTO(
                atom_id=atom_id,
                level=5,
                level_name="High",
                claim_label="Verified Claim",
                extracted_facts={},
                exact_quotes=[
                    QuoteEvidenceDTO(
                        source_quotes=("Exact quote from external verification.",),
                        verified_source_ids=[mcp_ev_id_1],
                        unverified_aliases=[],
                        is_verified=True,
                    )
                ],
                internal_logic_en=ReasoningStepDTO(
                    step_1_identify_premise="Premise",
                    step_2_scan_source="Scan",
                    step_3_evaluate_anti_patterns="Check",
                    step_4_final_conclusion="Conclusion",
                ),
                status=ExecutionStatus.PASSED,
                semantic_reasoning="Verified against external gateway.",
                contextual_override=False,
                structural_location=None,
                chart_display_label="Verified Claim",
                visual_intent=VisualIntent.NEUTRAL,
            )
        },
    )

    causal_node = CausalNodeDTOFactory.build(
        node_id="claim_direct_state",
        claim="Direct causal state node",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=[],
    )
    causal_graph = CausalGraphPayloadDTOFactory.build(
        nodes=[causal_node],
        edges=[],
        root_cause_node_ids=["claim_direct_state"],
    )

    exec_id = "exe_0195f3a0000070008000000000000009"
    record = ExecutionRecordFactory.build(
        id=exec_id,
        workflow_id=_WORKFLOW_ID,
        status=ExecutionStatus.PASSED,
        output_profile_id=_PROFILE_ID,
        target_locale="fi",
        dag_cost_usd=0.0,
        prompt_tokens=0,
        completion_tokens=0,
        reasoning_tokens=0,
        cumulative_synthesis_cost=0.0,
        cumulative_synthesis_tokens=0,
        metadata=ExecutionMetadata(),
        frozen_context=ExecutionRecordFactory.frozen_context().model_copy(
            update={
                "mcp_tool_audit": [
                    _MCPAuditTraceFactory.build(
                        id=mcp_ev_id_1,
                        tool_id="mcp_tavily_search",
                        step_name=_STEP_ID,
                        query="verified axis query",
                        response_summary="Verified summary text.",
                        impacted_axis_names=[],
                    ),
                    _MCPAuditTraceFactory.build(
                        id=mcp_ev_id_2,
                        tool_id="mcp_tavily_search",
                        step_name=_STEP_ID,
                        query="unreferenced query",
                        response_summary='{"results": [{"content": "Extracted JSON finding."}]}',
                        impacted_axis_names=[],
                    ),
                ]
            }
        ),
        execution_trace=[
            _make_trace_event(
                step_name=_STEP_ID,
                event_type="output",
                content={
                    _BLOCK_ID: TraceMatrixPayloadDTO(
                        raw_score=4.5,
                        normalized_score=87.5,
                        evaluated_atoms={atom_id: ExecutionStatus.PASSED},
                    ),
                    "used_evidence_ids": [mcp_ev_id_1],
                    VirtualSystemStepID.HAS_WARNING.value: True,
                },
                step_metadata=StepTraceMetadataDTO(
                    token_usage=TokenUsage(
                        prompt_tokens=200,
                        completion_tokens=80,
                        reasoning_tokens=20,
                        total_tokens=300,
                        cost_usd=0.04,
                    )
                ),
            )
        ],
    ).model_copy(
        update={
            "step_states": {
                _STEP_ID: step_state,
                "sr_0195f3a0000070008000000000000099": causal_graph,
            }
        }
    )
    mock_blueprint_repos.set_execution(record)

    transformer = _make_transformer(mock_blueprint_repos)
    dto = await transformer.build_report_dto(exec_id, profile_id=_PROFILE_ID)

    assert dto.has_warning is True
    assert dto.total_tokens == 300
    assert dto.cost_estimate == pytest.approx(0.04)
    assert len(dto.mcp_tool_audit) == 2
    audit_by_id = {item.id: item for item in dto.mcp_tool_audit}
    assert audit_by_id[mcp_ev_id_1].response_summary == "Verified summary text."
    assert audit_by_id[mcp_ev_id_2].response_summary == "Extracted JSON finding."
