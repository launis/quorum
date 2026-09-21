"""Unit tests for ExecutionLegacyRenderService."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.exceptions import AppException, ResourceNotFoundError
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord, ExecutionStep, JobAcceptedDTO
from backend_v2.models.domain.synthesis import RenderedSynthesisCache
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.flat_record import FlatExecutionRecordDTO
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO
from backend_v2.models.dtos.render import RenderExecutionResultDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import ExecutionStatus, HistoricalContextMode
from backend_v2.models.view.sdui import ParagraphBlock, ReportView, SduiMetrics1DBlock
from backend_v2.services.blueprint import BlueprintTransformer
from backend_v2.services.execution.legacy_render_service import ExecutionLegacyRenderService


@pytest.fixture
def mock_initiator() -> TokenData:
    """Fixture providing an admin token data initiator."""
    return TokenData(id="usr_001", role=UserRole.ADMIN, organization_id="org_001")


@pytest.fixture
def mock_execution_record() -> ExecutionRecord:
    """Fixture providing a mock execution record with rendered synthesis cache."""
    return ExecutionRecord(
        id="exe_1234567890abcdef",
        workflow_id="wor_1234567890abcdef",
        status=ExecutionStatus.PASSED,
        target_locale="fi",
        profile_syntheses={"prf_1234567890abcdef": RenderedSynthesisCache()},
    )


@pytest.fixture
def mock_workflow() -> Workflow:
    """Fixture providing a minimal test workflow definition."""
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
    """Fixture providing a valid ReportDataDTO with SDUI blocks."""
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
    """Fixture providing an ExecutionLegacyRenderService with mocked repositories."""
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


@pytest.mark.asyncio
async def test_render_execution_not_passed_raises(
    render_service: ExecutionLegacyRenderService,
    mock_initiator: TokenData,
    mock_execution_record: ExecutionRecord,
) -> None:
    """Verify render_execution raises 400 when execution is not PASSED."""
    running_rec = mock_execution_record.model_copy(update={"status": ExecutionStatus.RUNNING})
    render_service._get_execution = AsyncMock(return_value=running_rec)  # type: ignore[assignment]

    with pytest.raises(AppException) as exc_info:
        await render_service.render_execution(
            initiator=mock_initiator,
            execution_id="exe_1234567890abcdef",
            format_type="json",
            profile_id="prf_1234567890abcdef",
            accept_language="fi",
            arq_pool=AsyncMock(),
        )
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_render_execution_html(
    render_service: ExecutionLegacyRenderService,
    mock_initiator: TokenData,
) -> None:
    """Verify render_execution format_type='html' generates html bytes."""
    mock_pdf_service = MagicMock()
    mock_pdf_service.generate_execution_html = AsyncMock(return_value="<html><body>Report</body></html>")

    with patch(
        "backend_v2.services.execution.legacy_render_service.pdf_generator.PdfReportService",
        return_value=mock_pdf_service,
    ):
        result = await render_service.render_execution(
            initiator=mock_initiator,
            execution_id="exe_1234567890abcdef",
            format_type="html",
            profile_id="prf_1234567890abcdef",
            accept_language="fi",
            arq_pool=AsyncMock(),
        )

    assert isinstance(result, RenderExecutionResultDTO)
    assert result.media_type == "text/html"
    assert result.content == b"<html><body>Report</body></html>"
    assert result.filename == "execution_exe_1234567890abcdef.html"


@pytest.mark.asyncio
async def test_render_execution_pdf_cached(
    render_service: ExecutionLegacyRenderService,
    mock_initiator: TokenData,
    mock_execution_record: ExecutionRecord,
) -> None:
    """Verify render_execution format_type='pdf' reads cached PDF from storage when present."""
    cached_rec = mock_execution_record.model_copy(
        update={"pdf_report_path": "executions/exe_1234567890abcdef/report.pdf"}
    )
    render_service._get_execution = AsyncMock(return_value=cached_rec)  # type: ignore[assignment]
    mock_storage = AsyncMock()
    mock_storage.read = AsyncMock(return_value=b"%PDF-1.4-cached")

    with patch(
        "backend_v2.services.execution.legacy_render_service.storage.get_storage_driver", return_value=mock_storage
    ):
        result = await render_service.render_execution(
            initiator=mock_initiator,
            execution_id="exe_1234567890abcdef",
            format_type="pdf",
            profile_id="prf_1234567890abcdef",
            accept_language="fi",
            arq_pool=AsyncMock(),
        )

    assert isinstance(result, RenderExecutionResultDTO)
    assert result.media_type == "application/pdf"
    assert result.content == b"%PDF-1.4-cached"
    assert result.filename == "execution_exe_1234567890abcdef.pdf"


@pytest.mark.asyncio
async def test_render_execution_pdf_cached_storage_failure(
    render_service: ExecutionLegacyRenderService,
    mock_initiator: TokenData,
    mock_execution_record: ExecutionRecord,
) -> None:
    """Verify render_execution format_type='pdf' raises 500 when reading cached PDF fails."""
    cached_rec = mock_execution_record.model_copy(
        update={"pdf_report_path": "executions/exe_1234567890abcdef/report.pdf"}
    )
    render_service._get_execution = AsyncMock(return_value=cached_rec)  # type: ignore[assignment]
    mock_storage = AsyncMock()
    mock_storage.read = AsyncMock(side_effect=RuntimeError("Disk I/O failure"))

    with patch(
        "backend_v2.services.execution.legacy_render_service.storage.get_storage_driver", return_value=mock_storage
    ):
        with pytest.raises(AppException) as exc_info:
            await render_service.render_execution(
                initiator=mock_initiator,
                execution_id="exe_1234567890abcdef",
                format_type="pdf",
                profile_id="prf_1234567890abcdef",
                accept_language="fi",
                arq_pool=AsyncMock(),
            )
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_render_execution_pdf_generate_and_save(
    render_service: ExecutionLegacyRenderService,
    mock_initiator: TokenData,
) -> None:
    """Verify render_execution format_type='pdf' generates and saves PDF when not cached."""
    mock_storage = AsyncMock()
    mock_storage.save = AsyncMock(return_value="executions/exe_1234567890abcdef/report.pdf")
    mock_pdf_service = MagicMock()
    mock_pdf_service.generate_execution_pdf = AsyncMock(return_value=b"%PDF-1.4-generated")

    with patch(
        "backend_v2.services.execution.legacy_render_service.storage.get_storage_driver", return_value=mock_storage
    ):
        with patch(
            "backend_v2.services.execution.legacy_render_service.pdf_generator.PdfReportService",
            return_value=mock_pdf_service,
        ):
            result = await render_service.render_execution(
                initiator=mock_initiator,
                execution_id="exe_1234567890abcdef",
                format_type="pdf",
                profile_id="prf_1234567890abcdef",
                accept_language="fi",
                arq_pool=AsyncMock(),
            )

    assert isinstance(result, RenderExecutionResultDTO)
    assert result.media_type == "application/pdf"
    assert result.content == b"%PDF-1.4-generated"


@pytest.mark.asyncio
async def test_get_report_dto(
    render_service: ExecutionLegacyRenderService,
    mock_initiator: TokenData,
    mock_report_dto: ReportDataDTO,
) -> None:
    """Verify get_report_dto returns headless ReportDataDTO when PASSED."""
    dto = await render_service.get_report_dto(mock_initiator, "exe_1234567890abcdef")
    assert isinstance(dto, ReportDataDTO)
    assert dto.execution_id == "exe_1234567890abcdef"


@pytest.mark.asyncio
async def test_get_report_dto_not_passed_raises(
    render_service: ExecutionLegacyRenderService,
    mock_initiator: TokenData,
    mock_execution_record: ExecutionRecord,
) -> None:
    """Verify get_report_dto raises 400 when execution is not PASSED."""
    failed_rec = mock_execution_record.model_copy(update={"status": ExecutionStatus.FAILED})
    render_service._get_execution = AsyncMock(return_value=failed_rec)  # type: ignore[assignment]

    with pytest.raises(AppException) as exc_info:
        await render_service.get_report_dto(mock_initiator, "exe_1234567890abcdef")
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_default_get_execution(
    mock_execution_record: ExecutionRecord,
    mock_workflow: Workflow,
) -> None:
    """Verify _default_get_execution fetches and validates execution from exec_repo."""
    exec_repo = AsyncMock()
    exec_repo.get_execution.return_value = mock_execution_record
    workflow_repo = AsyncMock()
    workflow_repo.get_workflow_by_id.return_value = mock_workflow

    service = ExecutionLegacyRenderService(exec_repo=exec_repo, workflow_repo=workflow_repo)
    rec = await service._default_get_execution(TokenData(id="usr_001", role=UserRole.ADMIN), "exe_1234567890abcdef")
    assert rec.id == "exe_1234567890abcdef"


@pytest.mark.asyncio
async def test_default_get_execution_not_found_raises(
    mock_workflow: Workflow,
) -> None:
    """Verify _default_get_execution raises ResourceNotFoundError when record is missing."""
    exec_repo = AsyncMock()
    exec_repo.get_execution.return_value = None
    workflow_repo = AsyncMock()
    workflow_repo.get_workflow_by_id.return_value = mock_workflow

    service = ExecutionLegacyRenderService(exec_repo=exec_repo, workflow_repo=workflow_repo)
    with pytest.raises(ResourceNotFoundError):
        await service._default_get_execution(TokenData(id="usr_001", role=UserRole.ADMIN), "exe_1234567890abcdef")


def test_transformer_missing_repos_raises(
    mock_execution_record: ExecutionRecord,
    mock_workflow: Workflow,
) -> None:
    """Verify _transformer raises 500 when required repositories are None."""
    exec_repo = AsyncMock()
    workflow_repo = AsyncMock()
    service = ExecutionLegacyRenderService(exec_repo=exec_repo, workflow_repo=workflow_repo)

    with pytest.raises(AppException) as exc_info:
        service._transformer()
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_get_execution_export_bytes_success(
    render_service: ExecutionLegacyRenderService,
    mock_initiator: TokenData,
    mock_execution_record: ExecutionRecord,
) -> None:
    """Verify get_execution_export_bytes delegates to export_service."""
    from backend_v2.models.domain.execution import ExecutionStep
    from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
    from backend_v2.models.dtos.matrix_scorecard import ScorecardAtomDTO
    from backend_v2.models.enums import LaxExecutionStatus, VisualIntent

    atom = ScorecardAtomDTO(
        atom_id="atm_001",
        level=1,
        level_name="Level 1",
        claim_label="Claim 1",
        extracted_facts={},
        exact_quotes=[],
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="Premise",
            step_2_scan_source="Source",
            step_3_evaluate_anti_patterns="None",
            step_4_final_conclusion="Conclusion",
        ),
        status=LaxExecutionStatus.PASSED,
        semantic_reasoning="Valid semantic reasoning",
        contextual_override=False,
        chart_display_label="Chart 1",
        visual_intent=VisualIntent.INFO,
    )
    step = ExecutionStep(
        id="stp_001",
        label="Step 1",
        scorecard_atoms={"atm_001": atom},
    )
    rec_with_atoms = mock_execution_record.model_copy(update={"step_states": {"stp_001": step}})
    render_service._get_execution = AsyncMock(return_value=rec_with_atoms)  # type: ignore[assignment]
    render_service.export_service = AsyncMock()
    render_service.export_service.export_excel.return_value = (b"PK_EXCEL_BYTES", "report.xlsx")

    content, filename = await render_service.get_execution_export_bytes(mock_initiator, "exe_1234567890abcdef")
    assert content == b"PK_EXCEL_BYTES"
    assert filename == "report.xlsx"


def test_transformer_success() -> None:
    """Verify _transformer returns BlueprintTransformer when all required repositories are provided."""
    service = ExecutionLegacyRenderService(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )
    transformer = service._transformer()
    assert isinstance(transformer, BlueprintTransformer)


@pytest.mark.asyncio
async def test_get_execution_export_bytes_not_passed(
    render_service: ExecutionLegacyRenderService,
    mock_initiator: TokenData,
    mock_execution_record: ExecutionRecord,
) -> None:
    """Verify get_execution_export_bytes raises 400 when execution is not PASSED."""
    running_rec = mock_execution_record.model_copy(update={"status": ExecutionStatus.RUNNING})
    render_service._get_execution = AsyncMock(return_value=running_rec)  # type: ignore[assignment]

    with pytest.raises(AppException) as exc_info:
        await render_service.get_execution_export_bytes(mock_initiator, "exe_1234567890abcdef")
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_get_execution_export_bytes_no_atoms(
    render_service: ExecutionLegacyRenderService,
    mock_initiator: TokenData,
    mock_execution_record: ExecutionRecord,
) -> None:
    """Verify get_execution_export_bytes raises 400 when execution has no scoreable atoms."""
    empty_atoms_rec = mock_execution_record.model_copy(update={"step_states": {}})
    render_service._get_execution = AsyncMock(return_value=empty_atoms_rec)  # type: ignore[assignment]

    with pytest.raises(AppException) as exc_info:
        await render_service.get_execution_export_bytes(mock_initiator, "exe_1234567890abcdef")
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_get_execution_export_bytes_report_dto_failure(
    render_service: ExecutionLegacyRenderService,
    mock_initiator: TokenData,
    mock_execution_record: ExecutionRecord,
) -> None:
    """Verify get_execution_export_bytes raises 500 when _get_report_dto fails."""
    from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
    from backend_v2.models.dtos.matrix_scorecard import ScorecardAtomDTO
    from backend_v2.models.enums import LaxExecutionStatus, VisualIntent

    atom = ScorecardAtomDTO(
        atom_id="atm_001",
        level=1,
        level_name="Level 1",
        claim_label="Claim 1",
        extracted_facts={},
        exact_quotes=[],
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="Premise",
            step_2_scan_source="Source",
            step_3_evaluate_anti_patterns="None",
            step_4_final_conclusion="Conclusion",
        ),
        status=LaxExecutionStatus.PASSED,
        semantic_reasoning="Valid semantic reasoning",
        contextual_override=False,
        chart_display_label="Chart 1",
        visual_intent=VisualIntent.INFO,
    )
    step = ExecutionStep(
        id="stp_001",
        label="Step 1",
        scorecard_atoms={"atm_001": atom},
    )
    rec_with_atoms = mock_execution_record.model_copy(update={"step_states": {"stp_001": step}})
    render_service._get_execution = AsyncMock(return_value=rec_with_atoms)  # type: ignore[assignment]
    render_service._get_report_dto = AsyncMock(side_effect=RuntimeError("Transformation error"))  # type: ignore[assignment]

    with pytest.raises(AppException) as exc_info:
        await render_service.get_execution_export_bytes(mock_initiator, "exe_1234567890abcdef")
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_enqueue_pdf_generation_success(
    render_service: ExecutionLegacyRenderService,
    mock_initiator: TokenData,
    mock_execution_record: ExecutionRecord,
) -> None:
    """Verify enqueue_pdf_generation updates execution state and enqueues job."""
    exec_repo = AsyncMock()
    exec_repo.get_execution.return_value = mock_execution_record
    render_service.exec_repo = exec_repo
    render_service._get_execution = AsyncMock(return_value=mock_execution_record)  # type: ignore[assignment]

    arq_pool = AsyncMock()
    await render_service.enqueue_pdf_generation(
        initiator=mock_initiator,
        execution_id="exe_1234567890abcdef",
        accept_language="fi",
        profile_id="prf_1234567890abcdef",
        arq_pool=arq_pool,
    )

    exec_repo.update_execution.assert_awaited_once()
    arq_pool.enqueue_job.assert_awaited_once_with(
        "generate_pdf_job",
        execution_id="exe_1234567890abcdef",
        accept_language="fi",
        profile_id="prf_1234567890abcdef",
        custom_preface_md=None,
        local_time_str=None,
    )


@pytest.mark.asyncio
async def test_render_execution_workflow_not_found(
    render_service: ExecutionLegacyRenderService,
    mock_initiator: TokenData,
) -> None:
    """Verify render_execution raises 500 when workflow is not found."""
    workflow_repo = AsyncMock()
    workflow_repo.get_workflow_by_id.return_value = None
    render_service.workflow_repo = workflow_repo

    with pytest.raises(AppException) as exc_info:
        await render_service.render_execution(
            initiator=mock_initiator,
            execution_id="exe_1234567890abcdef",
            format_type="json",
            profile_id="prf_1234567890abcdef",
            accept_language="fi",
            arq_pool=AsyncMock(),
        )
    assert exc_info.value.status_code == 500
    assert "Workflow not found" in exc_info.value.message


@pytest.mark.asyncio
async def test_render_execution_target_locale_missing(
    render_service: ExecutionLegacyRenderService,
    mock_initiator: TokenData,
    mock_execution_record: ExecutionRecord,
) -> None:
    """Verify render_execution raises 500 when target locale is missing."""
    no_locale_rec = mock_execution_record.model_copy(update={"target_locale": None})
    render_service._get_execution = AsyncMock(return_value=no_locale_rec)  # type: ignore[assignment]

    with pytest.raises(AppException) as exc_info:
        await render_service.render_execution(
            initiator=mock_initiator,
            execution_id="exe_1234567890abcdef",
            format_type="html",
            profile_id="prf_1234567890abcdef",
            accept_language=None,
            arq_pool=AsyncMock(),
        )
    assert exc_info.value.status_code == 500
    assert "target_locale missing" in exc_info.value.message


@pytest.mark.asyncio
async def test_render_execution_pdf_storage_save_failure(
    render_service: ExecutionLegacyRenderService,
    mock_initiator: TokenData,
) -> None:
    """Verify render_execution raises 500 when saving generated PDF to storage fails."""
    mock_storage = AsyncMock()
    mock_storage.save = AsyncMock(side_effect=RuntimeError("Storage disk failure"))
    mock_pdf_service = MagicMock()
    mock_pdf_service.generate_execution_pdf = AsyncMock(return_value=b"%PDF-1.4-generated")

    with patch(
        "backend_v2.services.execution.legacy_render_service.storage.get_storage_driver", return_value=mock_storage
    ):
        with patch(
            "backend_v2.services.execution.legacy_render_service.pdf_generator.PdfReportService",
            return_value=mock_pdf_service,
        ):
            with pytest.raises(AppException) as exc_info:
                await render_service.render_execution(
                    initiator=mock_initiator,
                    execution_id="exe_1234567890abcdef",
                    format_type="pdf",
                    profile_id="prf_1234567890abcdef",
                    accept_language="fi",
                    arq_pool=AsyncMock(),
                )
    assert exc_info.value.status_code == 500
    assert "Failed to save PDF to storage" in exc_info.value.message
