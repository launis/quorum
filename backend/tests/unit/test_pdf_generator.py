from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.services.pdf_generator import PdfReportService, ProgressServiceProtocol


@pytest.fixture
def mock_repo():
    return AsyncMock()

@pytest.fixture
def mock_progress():
    progress = AsyncMock(spec=ProgressServiceProtocol)
    return progress

@pytest.fixture
def mock_weasyprint():
    with patch("backend.services.pdf_generator.weasyprint") as mock_wp:
        mock_html = MagicMock()
        mock_wp.HTML.return_value = mock_html
        mock_html.write_pdf.return_value = b"%PDF-1.4 mock content"
        yield mock_wp

@pytest.fixture
def mock_chart_service():
    with patch("backend.services.pdf_generator.ChartService") as mock_cs:
        mock_cs.generate_radar_chart.return_value = "data:image/png;base64,mock"
        yield mock_cs

@pytest.mark.asyncio
async def test_generate_execution_pdf_success(mock_repo, mock_progress, mock_weasyprint, mock_chart_service):
    # Setup
    service = PdfReportService(mock_repo, mock_progress)
    execution_id = "exec-123"

    # Mock Repository Return
    mock_execution = MagicMock()
    # Ensure model_dump works if checked
    mock_execution.model_dump.return_value = {
        "id": execution_id,
        "results": {
            "step_judge": {
                "score_cards": [{
                    "total_score": 3.5,
                    "verdict": "Pass",
                    "dimensions": [{"label": "Logic", "score": 4.0}]
                }]
            }
        }
    }
    mock_repo.get_execution.return_value = mock_execution

    # Execute
    result = await service.generate_execution_pdf(execution_id)

    # Verify
    assert result == b"%PDF-1.4 mock content"

    # Verify Progress Calls (Sequence)
    assert mock_progress.emit_progress.call_count == 5
    args_list = mock_progress.emit_progress.call_args_list

    # Check 10%
    assert args_list[0][0][3] == 0.1
    # Check 100%
    assert args_list[4][0][3] == 1.0

    # Verify Chart generation triggered
    mock_chart_service.generate_radar_chart.assert_called_once()

    # Verify HTML generation (implicit via weasyprint call)
    mock_weasyprint.HTML.assert_called_once()
    # Check that template rendering passed data (hard to inspect template output directly without mocking template env, but weasyprint input implies it)

@pytest.mark.asyncio
async def test_generate_execution_pdf_not_found(mock_repo, mock_progress):
    service = PdfReportService(mock_repo, mock_progress)
    mock_repo.get_execution.return_value = None

    with pytest.raises(ValueError, match="not found"):
        await service.generate_execution_pdf("missing-id")

    # Verify failure progress emitted
    assert mock_progress.emit_progress.called

@pytest.mark.asyncio
async def test_generate_execution_pdf_error_handling(mock_repo, mock_progress):
    service = PdfReportService(mock_repo, mock_progress)
    mock_execution = MagicMock()
    mock_repo.get_execution.return_value = mock_execution

    # Force error during chart generation
    with patch("backend.services.pdf_generator.ChartService.generate_radar_chart", side_effect=ValueError("Chart Error")):
        with pytest.raises(ValueError):
            await service.generate_execution_pdf("exec-123")

    # Check that it tried to emit progress even on failure
    failure_call = mock_progress.emit_progress.call_args_list[-1]
    assert "Error: Chart Error" in failure_call[0][2]
