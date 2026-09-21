"""Unit tests for ExecutionLegacyRenderService."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord, JobAcceptedDTO
from backend_v2.models.domain.synthesis import RenderedSynthesisCache
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.flat_record import FlatExecutionRecordDTO
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO
from backend_v2.models.dtos.render import RenderExecutionResultDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import ExecutionStatus, HistoricalContextMode
from backend_v2.models.view.sdui import ParagraphBlock, ReportView, SduiMetrics1DBlock
from backend_v2.services.execution.legacy_render_service import ExecutionLegacyRenderService


@pytest.fixture
def mock_initiator() -> TokenData:
    return TokenData(id="usr_001", role=UserRole.ADMIN, organization_id="org_001")


@pytest.fixture
def mock_execution_record() -> ExecutionRecord:
    return ExecutionRecord(
        id="exe_1234567890abcdef",
        workflow_id="wor_1234567890abcdef",
        status=ExecutionStatus.PASSED,
        target_locale="fi",
        profile_syntheses={"prf_1234567890abcdef": RenderedSynthesisCache()},
    )


@pytest.fixture
def mock_workflow() -> Workflow:
    return Workflow(
        id="wor_1234567890abcdef",
        slug="test-workflow",
        name="Test Workflow",
        description="Test Workflow Description",
        status="active",
        version=1,
        model_registry_id="cfg_model_registry_01",
        historical_context_mode=HistoricalContextMode.DISABLED,
        default_profile_id="prf_1234567890abcdef",
        steps=[],
    )


@pytest.fixture
def mock_report_dto() -> ReportDataDTO:
    axis = MatrixScorecardRowDTO(
        block_id="blk_001",
        name="Coaching Clarity",
        label_i18n=I18nText(translations={"fi": "Valmennuksen selkeys", "en": "Coaching Clarity"}),
        row_explanation="Detailed and clear reasoning provided.",
        score=4.5,
        is_evaluative=True,
        semantic_reasoning="Detailed and clear reasoning provided.",
    )
    metric_block = SduiMetrics1DBlock(id="metrics_1", axes=[axis])
    para_block = ParagraphBlock(id="p1", text="Executive Summary Lead Text")
    return ReportDataDTO(
        execution_id="exe_1234567890abcdef",
        workflow_id="wor_1234567890abcdef",
        profile_id="prf_1234567890abcdef",
        global_score=85.0,
        inner_sdui_blocks=[para_block, metric_block],
    )


@pytest.fixture
def render_service(
    mock_execution_record: ExecutionRecord,
    mock_workflow: Workflow,
    mock_report_dto: ReportDataDTO,
) -> ExecutionLegacyRenderService:
    exec_repo = AsyncMock()
    exec_repo.get_execution.return_value = mock_execution_record

    workflow_repo = AsyncMock()
    workflow_repo.get_workflow_by_id.return_value = mock_workflow

    service = ExecutionLegacyRenderService(
        exec_repo=exec_repo,
        workflow_repo=workflow_repo,
        get_execution_fn=AsyncMock(return_value=mock_execution_record),
        get_report_dto_fn=AsyncMock(return_value=mock_report_dto),
    )
    transformer_mock = AsyncMock()
    transformer_mock.build_report_dto.return_value = mock_report_dto
    service._transformer = lambda: transformer_mock  # type: ignore[assignment]
    return service


@pytest.mark.asyncio
async def test_get_sdui_view_returns_report_view_directly(
    render_service: ExecutionLegacyRenderService,
    mock_initiator: TokenData,
) -> None:
    """Verify get_sdui_view returns a strongly typed ReportView directly without dict conversion."""
    view = await render_service.get_sdui_view(mock_initiator, "exe_1234567890abcdef")

    assert isinstance(view, ReportView)
    assert view.view_id == "exe_1234567890abcdef"
    assert "Executive Summary Lead Text" in view.title
    assert isinstance(view.inner_sdui_blocks, list)
    assert len(view.inner_sdui_blocks) == 2


@pytest.mark.asyncio
async def test_render_execution_returns_flat_record_dto(
    render_service: ExecutionLegacyRenderService,
    mock_initiator: TokenData,
    mock_report_dto: ReportDataDTO,
) -> None:
    """Verify format_type='flat' returns RenderExecutionResultDTO containing FlatExecutionRecordDTO."""
    result = await render_service.render_execution(
        initiator=mock_initiator,
        execution_id="exe_1234567890abcdef",
        format_type="flat",
        profile_id="prf_1234567890abcdef",
        accept_language="fi",
        arq_pool=AsyncMock(),
    )

    assert isinstance(result, RenderExecutionResultDTO)
    assert isinstance(result.content, FlatExecutionRecordDTO)
    assert result.content.execution_id == "exe_1234567890abcdef"
    assert result.content.global_score == 85.0
    assert result.media_type == "application/json"
    assert result.filename is None


@pytest.mark.asyncio
async def test_render_execution_returns_json_report_dto(
    render_service: ExecutionLegacyRenderService,
    mock_initiator: TokenData,
) -> None:
    """Verify format_type='json' returns RenderExecutionResultDTO containing ReportDataDTO."""
    result = await render_service.render_execution(
        initiator=mock_initiator,
        execution_id="exe_1234567890abcdef",
        format_type="json",
        profile_id="prf_1234567890abcdef",
        accept_language="fi",
        arq_pool=AsyncMock(),
    )

    assert isinstance(result, RenderExecutionResultDTO)
    assert isinstance(result.content, ReportDataDTO)
    assert result.content.execution_id == "exe_1234567890abcdef"
    assert result.content.global_score == 85.0
    assert result.media_type == "application/json"


@pytest.mark.asyncio
async def test_render_execution_returns_job_accepted_when_synthesis_missing(
    render_service: ExecutionLegacyRenderService,
    mock_initiator: TokenData,
    mock_execution_record: ExecutionRecord,
) -> None:
    """Verify missing profile synthesis triggers async job and returns JobAcceptedDTO."""
    empty_synth_record = mock_execution_record.model_copy(update={"profile_syntheses": {}})
    render_service._get_execution = AsyncMock(return_value=empty_synth_record)  # type: ignore[assignment]

    result = await render_service.render_execution(
        initiator=mock_initiator,
        execution_id="exe_1234567890abcdef",
        format_type="pdf",
        profile_id="prf_1234567890abcdef",
        accept_language="fi",
        arq_pool=AsyncMock(),
    )

    assert isinstance(result, RenderExecutionResultDTO)
    assert isinstance(result.content, JobAcceptedDTO)
    assert result.content.status == ExecutionStatus.PENDING
    assert result.content.execution_id == "exe_1234567890abcdef"
    assert result.media_type == "application/json"


@pytest.mark.asyncio
async def test_render_execution_unsupported_format_raises(
    render_service: ExecutionLegacyRenderService,
    mock_initiator: TokenData,
) -> None:
    """Verify unsupported format raises AppException fail-fast."""
    with pytest.raises(AppException) as exc_info:
        await render_service.render_execution(
            initiator=mock_initiator,
            execution_id="exe_1234567890abcdef",
            format_type="unsupported_format_xyz",
            profile_id="prf_1234567890abcdef",
            accept_language="fi",
            arq_pool=AsyncMock(),
        )
    assert exc_info.value.status_code == 400
