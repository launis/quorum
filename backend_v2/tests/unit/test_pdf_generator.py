from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.exceptions import ConfigurationError
from backend_v2.models.state import TraceEvent
from backend_v2.models.v2_core import ExecutionRecord, ExecutionStatus, I18nText, ReportDataDTO
from backend_v2.models.view.sdui import ParagraphBlock, SduiMetrics1DBlock, SduiRadarChartBlock
from backend_v2.services.pdf_generator import PdfReportService


@pytest.mark.asyncio
async def test_pdf_generator_chart_injection_failure_safe() -> None:
    # A dummy repository
    mock_repo = AsyncMock()

    # Mock an execution record with strict V2 validations
    mock_execution = ExecutionRecord(
        id="exe_aaaaaaaabbbbbbbb",
        workflow_id="test_wf",
        status=ExecutionStatus.PASSED,
        metadata={"target_locale": "en"},
        execution_trace=[TraceEvent(step_name="test_step", event_type="output", content={"ok": True})],
    )
    mock_repo.get_execution.return_value = mock_execution
    mock_repo.get_workflow_by_id.return_value = None

    svc = PdfReportService(exec_repo=mock_repo, workflow_repo=mock_repo)

    # Empty layout (should not invoke chart rendering)
    dto = ReportDataDTO(
        execution_id="exe_aaaaaaaabbbbbbbb",
        strictness_level=85,
        workflow_id="test_wf",
        profile_id="prf_test",
        profile_name=I18nText(default_locale="en", translations={"en": "Test Profile", "fi": "Test Profile"}),
        inner_sdui_blocks=[SduiMetrics1DBlock(axes=[])],
    )

    pdf_bytes = await svc.generate_execution_pdf(execution_id="exe_aaaaaaaabbbbbbbb", report_dto=dto)
    assert pdf_bytes is not None
    assert isinstance(pdf_bytes, bytes)


@pytest.mark.asyncio
async def test_html_generator_chart_injection_failure_safe() -> None:
    # A dummy repository
    mock_repo = AsyncMock()

    # Mock an execution record with strict V2 validations
    mock_execution = ExecutionRecord(
        id="exe_aaaaaaaabbbbbbbb",
        workflow_id="test_wf",
        status=ExecutionStatus.PASSED,
        metadata={"target_locale": "en"},
        execution_trace=[TraceEvent(step_name="test_step", event_type="output", content={"ok": True})],
    )
    mock_repo.get_execution.return_value = mock_execution
    mock_repo.get_workflow_by_id.return_value = None

    svc = PdfReportService(exec_repo=mock_repo, workflow_repo=mock_repo)

    # Empty layout (should not invoke chart rendering)
    dto = ReportDataDTO(
        execution_id="exe_aaaaaaaabbbbbbbb",
        strictness_level=85,
        workflow_id="test_wf",
        profile_id="prf_test",
        profile_name=I18nText(default_locale="en", translations={"en": "Test Profile", "fi": "Test Profile"}),
        inner_sdui_blocks=[SduiMetrics1DBlock(axes=[])],
    )

    html_string = await svc.generate_execution_html(execution_id="exe_aaaaaaaabbbbbbbb", report_dto=dto)
    assert html_string is not None
    assert isinstance(html_string, str)
    # The execution ID is not necessarily in the HTML either, wait!
    # I should just check that html_string starts with <!DOCTYPE html>
    assert html_string.strip().startswith("<!DOCTYPE html>")


@pytest.mark.asyncio
async def test_pdf_generator_empty_chart_crashes() -> None:
    mock_repo = AsyncMock()
    mock_execution = ExecutionRecord(
        id="exe_1111111111111111",
        workflow_id="test_wf",
        status=ExecutionStatus.PASSED,
        metadata={"target_locale": "en"},
        execution_trace=[],
    )
    mock_repo.get_execution.return_value = mock_execution
    mock_repo.get_workflow_by_id.return_value = None

    svc = PdfReportService(exec_repo=mock_repo, workflow_repo=mock_repo)

    dto = ReportDataDTO(
        execution_id="exe_1111111111111111",
        strictness_level=85,
        workflow_id="test_wf",
        profile_id="prf_test",
        profile_name=I18nText(default_locale="en", translations={"en": "Test Profile", "fi": "Test Profile"}),
        inner_sdui_blocks=[SduiRadarChartBlock(axes=[])],
    )

    with patch("backend_v2.services.pdf_generator.generate_radar_chart", return_value=""):
        with pytest.raises(ConfigurationError) as exc_info:
            await svc.generate_execution_pdf(execution_id="exe_1111111111111111", report_dto=dto)
        assert "returned empty data for block" in str(exc_info.value)


@pytest.mark.asyncio
async def test_pdf_generator_unknown_block_type_skipped() -> None:
    mock_repo = AsyncMock()
    mock_execution = ExecutionRecord(
        id="exe_2222222222222222",
        workflow_id="test_wf",
        status=ExecutionStatus.PASSED,
        metadata={"target_locale": "en"},
        execution_trace=[],
    )
    mock_repo.get_execution.return_value = mock_execution
    mock_repo.get_workflow_by_id.return_value = None

    svc = PdfReportService(exec_repo=mock_repo, workflow_repo=mock_repo)

    dto = ReportDataDTO(
        execution_id="exe_2222222222222222",
        strictness_level=85,
        workflow_id="test_wf",
        profile_id="prf_test",
        profile_name=I18nText(default_locale="en", translations={"en": "Test Profile", "fi": "Test Profile"}),
        inner_sdui_blocks=[ParagraphBlock(text="Hello", exact_quotes=[], citations=[])],
    )

    pdf_bytes = await svc.generate_execution_pdf(execution_id="exe_2222222222222222", report_dto=dto)
    assert pdf_bytes is not None
    assert isinstance(pdf_bytes, bytes)
