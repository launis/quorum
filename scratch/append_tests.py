import sys
from pathlib import Path

file_path = Path(r"c:\src\quorum\backend_v2\tests\unit\test_pdf_generator.py")
content = file_path.read_text(encoding="utf-8")

if "ConfigurationError" not in content:
    content = content.replace(
        "from backend_v2.services.pdf_generator import PdfReportService",
        "from backend_v2.exceptions import ConfigurationError\nfrom backend_v2.services.pdf_generator import PdfReportService"
    )

if "SduiRadarChartBlock" not in content:
    content = content.replace(
        "from backend_v2.models.view.sdui import SduiMetrics1DBlock",
        "from backend_v2.models.view.sdui import SduiMetrics1DBlock, SduiRadarChartBlock, SduiParagraphBlock"
    )

if "patch" not in content:
    content = content.replace(
        "from unittest.mock import AsyncMock",
        "from unittest.mock import AsyncMock, patch"
    )

new_tests = """

@pytest.mark.asyncio
async def test_pdf_generator_empty_chart_crashes() -> None:
    mock_repo = AsyncMock()
    mock_execution = ExecutionRecord(
        id="exe_111",
        workflow_id="test_wf",
        status=ExecutionStatus.PASSED,
        metadata={"target_locale": "en"},
        execution_trace=[],
    )
    mock_repo.get_execution.return_value = mock_execution
    mock_repo.get_workflow_by_id.return_value = None

    svc = PdfReportService(exec_repo=mock_repo, workflow_repo=mock_repo)

    dto = ReportDataDTO(
        execution_id="exe_111",
        strictness_level=85,
        workflow_id="test_wf",
        profile_id="prf_test",
        profile_name=I18nText(default_locale="en", translations={"en": "Test Profile", "fi": "Test Profile"}),
        inner_sdui_blocks=[SduiRadarChartBlock(axes=[], text_delivery_mode="none")],
    )

    with patch("backend_v2.services.pdf_generator.generate_radar_chart", return_value=""):
        with pytest.raises(ConfigurationError) as exc_info:
            await svc.generate_execution_pdf(execution_id="exe_111", report_dto=dto)
        assert "returned empty data for block" in str(exc_info.value)


@pytest.mark.asyncio
async def test_pdf_generator_unknown_block_type_skipped() -> None:
    mock_repo = AsyncMock()
    mock_execution = ExecutionRecord(
        id="exe_222",
        workflow_id="test_wf",
        status=ExecutionStatus.PASSED,
        metadata={"target_locale": "en"},
        execution_trace=[],
    )
    mock_repo.get_execution.return_value = mock_execution
    mock_repo.get_workflow_by_id.return_value = None

    svc = PdfReportService(exec_repo=mock_repo, workflow_repo=mock_repo)

    dto = ReportDataDTO(
        execution_id="exe_222",
        strictness_level=85,
        workflow_id="test_wf",
        profile_id="prf_test",
        profile_name=I18nText(default_locale="en", translations={"en": "Test Profile", "fi": "Test Profile"}),
        inner_sdui_blocks=[SduiParagraphBlock(text="Hello", text_delivery_mode="none")],
    )

    pdf_bytes = await svc.generate_execution_pdf(execution_id="exe_222", report_dto=dto)
    assert pdf_bytes is not None
    assert isinstance(pdf_bytes, bytes)
"""
file_path.write_text(content + new_tests, encoding="utf-8")
