"""Unit tests for Blueprint combined costs, tokens, and ReportDataDTO synchronization."""

from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock

import pytest

from backend_v2.models.auth import User, UserRole
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.trace import StepTraceMetadataDTO
from backend_v2.models.enums import (
    DisplayScale,
    ExecutionStatus,
    HistoricalContextMode,
    ScoringStrategy,
    TargetBlockType,
)
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import TraceEvent
from backend_v2.models.v2_core import (
    ExecutionRecord,
    I18nText,
    MatrixSynthesisGroup,
    OutputProfile,
    ReportDataDTO,
    Workflow,
)
from backend_v2.models.view.sdui import SduiMetadataBlock
from backend_v2.services.blueprint import BlueprintTransformer
from backend_v2.services.localization import LocalizationService

_WORKFLOW_ID = "wf_0123456789abcdef0123456789abcdef"
_PROFILE_ID = "prf_0123456789abcdef0123456789abcdef"
_USER_ID = "usr_0123456789abcdef"


@pytest.fixture
def mock_blueprint_repos() -> AsyncMock:
    """Creates a mock repository suite for BlueprintTransformer testing."""
    repo = AsyncMock()

    profile = OutputProfile(
        id=_PROFILE_ID,
        slug="default",
        workflow_id=_WORKFLOW_ID,
        name=I18nText(translations={"en": "Executive Summary", "fi": "Johdon yhteenveto"}),
        display_scale=DisplayScale.ORIGINAL,
        target_block_order=[TargetBlockType.METADATA_BLOCK],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0000000000000001",
                title=I18nText(translations={"en": "Default", "fi": "Oletus"}),
                target_blocks=["*"],
            )
        ],
        visible_metadata=["user", "organization", "date", "cost", "tokens"],
        strictness_level=85,
        matrix_visible_columns=["label", "score", "distribution", "quotes"],
    )

    workflow = Workflow(
        id=_WORKFLOW_ID,
        slug="test_workflow",
        description=I18nText(translations={"en": "Workflow", "fi": "Työnkulku"}),
        status="published",
        version=1,
        name=I18nText(translations={"en": "Test Workflow", "fi": "Testi työnkulku"}),
        default_profile_id=_PROFILE_ID,
        allowed_exports=["pdf"],
        historical_context_mode=HistoricalContextMode.DISABLED,
        default_strictness_level=85,
        default_scoring_strategy=ScoringStrategy.WATERFALL,
        steps=[],
    )

    user = User(
        id=_USER_ID,
        email="auditor@example.com",
        name="Lead Auditor",
        role=UserRole.ADMIN,
        is_active=True,
        language="fi",
        theme_mode="system",
        created_at=datetime.now(timezone.utc),
    )

    repo.get_workflow.return_value = workflow
    repo.get_all_output_profiles.return_value = [profile.model_dump(mode="python")]
    repo.get_all_prompt_blocks.return_value = []
    repo.get_user.return_value = user
    repo.get_mcp_gateways.return_value = None
    return repo


@pytest.mark.asyncio
async def test_blueprint_combined_cost_and_tokens_from_execution_record(mock_blueprint_repos: Any) -> None:
    """Verifies combined cost and token aggregation from ExecutionRecord top-level fields."""
    record = ExecutionRecord(
        id="exe_00000000000000010000000000000001",
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
    mock_blueprint_repos.get_execution.return_value = record

    transformer = BlueprintTransformer(
        exec_repo=mock_blueprint_repos,
        workflow_repo=mock_blueprint_repos,
        comp_repo=mock_blueprint_repos,
        prompt_block_repo=mock_blueprint_repos,
        output_profile_repo=mock_blueprint_repos,
        identity_repo=mock_blueprint_repos,
        system_repo=mock_blueprint_repos,
    )

    dto = await transformer.build_report_dto("exe_00000000000000010000000000000001", profile_id=_PROFILE_ID)

    assert isinstance(dto, ReportDataDTO)
    # Expected: DAG (1.88) + Synthesis (0.45) = 2.33
    assert dto.cost_estimate is not None
    assert dto.cost_estimate == pytest.approx(2.33)
    # Expected: prompt (1000) + comp (500) + reas (200) + synth (300) = 2000
    assert dto.total_tokens == 2000
    assert dto.prompt_tokens == 1000
    assert dto.completion_tokens == 500
    assert dto.reasoning_tokens == 200

    # Verify SduiMetadataBlock semantic parity
    metadata_blocks = [b for b in dto.inner_sdui_blocks if isinstance(b, SduiMetadataBlock)]
    assert len(metadata_blocks) == 1
    meta_block = metadata_blocks[0]
    assert meta_block.costs == LocalizationService.format_cost(dto.cost_estimate, "fi")
    assert meta_block.tokens == {"total": "2000"}


@pytest.mark.asyncio
async def test_blueprint_trace_fail_safe_when_dag_cost_zero(mock_blueprint_repos: Any) -> None:
    """Verifies that when dag_cost_usd is 0.0, tokens and costs are recovered from trace metadata."""
    meta_dto = StepTraceMetadataDTO(
        model_strategy="analytical_fast",
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

    event_with_metadata = TraceEvent(
        step_name="step_extract_evidence",
        event_type="output",
        content={
            "id": "blk_0123456789abcdef0123456789abcdef",
            "block_type": "text_block",
            "text": "Evidence extraction findings",
            "_step_metadata": meta_dto.model_dump(mode="python"),
        },
    )

    record = ExecutionRecord(
        id="exe_00000000000000020000000000000002",
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
    mock_blueprint_repos.get_execution.return_value = record

    transformer = BlueprintTransformer(
        exec_repo=mock_blueprint_repos,
        workflow_repo=mock_blueprint_repos,
        comp_repo=mock_blueprint_repos,
        prompt_block_repo=mock_blueprint_repos,
        output_profile_repo=mock_blueprint_repos,
        identity_repo=mock_blueprint_repos,
        system_repo=mock_blueprint_repos,
    )

    dto = await transformer.build_report_dto("exe_00000000000000020000000000000002", profile_id=_PROFILE_ID)

    assert isinstance(dto, ReportDataDTO)
    # Recovered DAG cost (0.85) + Synthesis cost (0.12) = 0.97
    assert dto.cost_estimate is not None
    assert dto.cost_estimate == pytest.approx(0.97)
    # Recovered DAG tokens (550) + Synthesis tokens (150) = 700
    assert dto.total_tokens == 700
    assert dto.prompt_tokens == 400
    assert dto.completion_tokens == 100
    assert dto.reasoning_tokens == 50

    # Verify SduiMetadataBlock reflects identical combined figures
    metadata_blocks = [b for b in dto.inner_sdui_blocks if isinstance(b, SduiMetadataBlock)]
    assert len(metadata_blocks) == 1
    meta_block = metadata_blocks[0]
    assert meta_block.costs == LocalizationService.format_cost(dto.cost_estimate, "fi")
    assert meta_block.tokens == {"total": "700"}


@pytest.mark.asyncio
async def test_blueprint_consecutive_synthesis_accumulation(mock_blueprint_repos: Any) -> None:
    """Verifies monotonic accumulation of synthesis costs across consecutive runs."""
    base_record = ExecutionRecord(
        id="exe_00000000000000030000000000000003",
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

    transformer = BlueprintTransformer(
        exec_repo=mock_blueprint_repos,
        workflow_repo=mock_blueprint_repos,
        comp_repo=mock_blueprint_repos,
        prompt_block_repo=mock_blueprint_repos,
        output_profile_repo=mock_blueprint_repos,
        identity_repo=mock_blueprint_repos,
        system_repo=mock_blueprint_repos,
    )

    # Run 1: initial synthesis
    mock_blueprint_repos.get_execution.return_value = base_record
    dto1 = await transformer.build_report_dto("exe_00000000000000030000000000000003", profile_id=_PROFILE_ID)
    assert dto1.cost_estimate is not None
    assert dto1.cost_estimate == pytest.approx(1.20)
    assert dto1.total_tokens == 800

    # Run 2: accumulated second profile synthesis
    accumulated_record = base_record.model_copy(
        update={
            "cumulative_synthesis_cost": 0.50,
            "cumulative_synthesis_tokens": 500,
        }
    )
    mock_blueprint_repos.get_execution.return_value = accumulated_record
    dto2 = await transformer.build_report_dto("exe_00000000000000030000000000000003", profile_id=_PROFILE_ID)
    assert dto2.cost_estimate is not None
    assert dto2.total_tokens is not None
    assert dto2.cost_estimate == pytest.approx(1.50)
    assert dto2.total_tokens == 1100
    assert dto2.cost_estimate > dto1.cost_estimate
    assert dto2.total_tokens > dto1.total_tokens


@pytest.mark.asyncio
async def test_blueprint_zero_tokens_and_cost_boundary(mock_blueprint_repos: Any) -> None:
    """Verifies boundary condition when execution has zero tokens, zero cost, and empty trace."""
    record = ExecutionRecord(
        id="exe_00000000000000040000000000000004",
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
    mock_blueprint_repos.get_execution.return_value = record

    transformer = BlueprintTransformer(
        exec_repo=mock_blueprint_repos,
        workflow_repo=mock_blueprint_repos,
        comp_repo=mock_blueprint_repos,
        prompt_block_repo=mock_blueprint_repos,
        output_profile_repo=mock_blueprint_repos,
        identity_repo=mock_blueprint_repos,
        system_repo=mock_blueprint_repos,
    )

    dto = await transformer.build_report_dto("exe_00000000000000040000000000000004", profile_id=_PROFILE_ID)

    assert isinstance(dto, ReportDataDTO)
    assert dto.cost_estimate == 0.0
    assert dto.total_tokens == 0
    assert dto.prompt_tokens == 0
    assert dto.completion_tokens == 0
    assert dto.reasoning_tokens == 0
