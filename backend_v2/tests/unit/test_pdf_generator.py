from unittest.mock import AsyncMock

import pytest

from backend_v2.models.state import TraceEvent
from backend_v2.models.v2_core import ExecutionRecord, ExecutionStatus, I18nText, ReportDataDTO, ReportLayoutDTO
from backend_v2.services.pdf_generator import PdfReportService


@pytest.mark.asyncio
async def test_pdf_generator_chart_injection_failure_safe() -> None:
    # A dummy repository
    mock_repo = AsyncMock()

    # Mock an execution record with strict V2 validations
    mock_execution = ExecutionRecord(
        id="exe_aaaaaaaabbbbbbbb",
        workflow_id="test_wf",
        status=ExecutionStatus.COMPLETED,
        metadata={"target_locale": "en"},
        execution_trace=[TraceEvent(step_name="test_step", event_type="output", content={"ok": True})],
    )
    mock_repo.get_execution.return_value = mock_execution
    mock_repo.get_workflow_by_id.return_value = None

    svc = PdfReportService(exec_repo=mock_repo, workflow_repo=mock_repo)

    # Empty layout (should not invoke chart rendering)
    dto = ReportDataDTO(
        strictness_level=85,
        workflow_id="test_wf",
        profile_id="prf_test",
        profile_name=I18nText(default_locale="en", translations={"en": "Test Profile"}),
        layouts=[ReportLayoutDTO(preset_view="1d_metrics", axes=[])],
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
        status=ExecutionStatus.COMPLETED,
        metadata={"target_locale": "en"},
        execution_trace=[TraceEvent(step_name="test_step", event_type="output", content={"ok": True})],
    )
    mock_repo.get_execution.return_value = mock_execution
    mock_repo.get_workflow_by_id.return_value = None

    svc = PdfReportService(exec_repo=mock_repo, workflow_repo=mock_repo)

    # Empty layout (should not invoke chart rendering)
    dto = ReportDataDTO(
        strictness_level=85,
        workflow_id="test_wf",
        profile_id="prf_test",
        profile_name=I18nText(default_locale="en", translations={"en": "Test Profile"}),
        layouts=[ReportLayoutDTO(preset_view="1d_metrics", axes=[])],
    )

    html_string = await svc.generate_execution_html(execution_id="exe_aaaaaaaabbbbbbbb", report_dto=dto)
    assert html_string is not None
    assert isinstance(html_string, str)
    assert "Test Profile" in html_string
    assert "exe_aaaaaaaabbbbbbbb" in html_string
