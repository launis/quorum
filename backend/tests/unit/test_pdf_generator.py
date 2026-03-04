import sys
from unittest.mock import AsyncMock, MagicMock, patch

# Mock weasyprint and numpy BEFORE importing the service to avoid dependency issues
mock_wp_module = MagicMock()
sys.modules["weasyprint"] = mock_wp_module
sys.modules["numpy"] = MagicMock()
sys.modules["matplotlib"] = MagicMock()
sys.modules["matplotlib.pyplot"] = MagicMock()
sys.modules["matplotlib.figure"] = MagicMock()

from datetime import datetime, timezone

import pytest

from backend.exceptions import AppException
from backend.models.domain.execution import ExecutionRecord
from backend.models.state import TraceEvent, WorkflowState
from backend.models.view.semantic_models import BlockType, SemanticBlock, SemanticIntent, SemanticReport
from backend.services.pdf_generator import PdfReportService, ProgressServiceProtocol


@pytest.fixture
def mock_repo():
    repo = AsyncMock()
    repo.get_workflow.return_value = None
    return repo


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

    # Mock Repository Return (needed for initial fetch check)
    mock_execution = ExecutionRecord(
        id=execution_id,
        workflow_id="test",
        status="completed",
        completed_at=datetime.now(timezone.utc),
        results=WorkflowState(workflow_id="test"),
    )
    mock_repo.get_execution.return_value = mock_execution

    # MOCK TRANSFORMER to bypass complex validation logic
    service.transformer = MagicMock()
    # Create a mock SemanticBlock with a Score Card section
    mock_section = SemanticBlock(
        id="score-card-1",
        type=BlockType.CARD,
        label="Test Score Card",
        value={
            "dimensions": [{"dimension_label": "Logic", "score": 4.0, "dimension_id": "logic"}],
            "max_score": 4,
        },  # chart_image will be injected by service
    )
    service.transformer.transform.return_value = SemanticReport(
        report_id=execution_id, title="Test", intent=SemanticIntent.SUCCESS, blocks=[mock_section]
    )

    # Execute
    result = await service.generate_execution_pdf(execution_id)

    # Verify
    assert result == b"%PDF-1.4 mock content"

    # Verify Progress Calls
    assert mock_progress.emit_progress.call_count == 6

    # Verify Chart generation triggered
    # The service iterates sections, finds SCORE_CARD, generates chart.
    mock_chart_service.generate_radar_chart.assert_called_once()

    # Verify HTML generation
    mock_weasyprint.HTML.assert_called_once()


@pytest.mark.asyncio
async def test_generate_execution_pdf_not_found(mock_repo, mock_progress):
    service = PdfReportService(mock_repo, mock_progress)
    mock_repo.get_execution.return_value = None

    # Service wraps ValueError in AppException
    with pytest.raises(AppException) as excinfo:
        await service.generate_execution_pdf("missing-id")

    assert "not found" in str(excinfo.value) or "not found" in str(excinfo.value.details)
    assert mock_progress.emit_progress.called


@pytest.mark.asyncio
async def test_generate_execution_pdf_error_handling(mock_repo, mock_progress):
    service = PdfReportService(mock_repo, mock_progress)
    mock_execution = ExecutionRecord(
        id="exec-123",
        workflow_id="test",
        status="completed",
        completed_at=datetime.now(timezone.utc),
        results=WorkflowState(workflow_id="test"),
    )
    mock_repo.get_execution.return_value = mock_execution

    # MOCK TRANSFORMER
    service.transformer = MagicMock()
    mock_section = SemanticBlock(
        id="score-card-1",
        type=BlockType.CARD,
        label="Test Score Card",
        value={"max_score": 5, "dimensions": [{"dimension_label": "Logic", "score": 4.0, "dimension_id": "logic"}]},
    )
    service.transformer.transform.return_value = SemanticReport(
        report_id="exec-123", title="Test", intent=SemanticIntent.SUCCESS, blocks=[mock_section]
    )

    # Force error during chart generation
    with patch(
        "backend.services.pdf_generator.ChartService.generate_radar_chart", side_effect=ValueError("Chart Error")
    ):
        with pytest.raises(AppException) as excinfo:
            await service.generate_execution_pdf("exec-123")

        assert "Chart Error" in str(excinfo.value) or "Chart Error" in str(excinfo.value.details)

    # Check that it tried to emit progress even on failure
    failure_call = mock_progress.emit_progress.call_args_list[-1]
    assert "Error: Chart Error" in failure_call[0][2]


@pytest.mark.asyncio
async def test_generate_pdf_with_logic_and_ethics(mock_repo, mock_progress, mock_weasyprint):
    # Setup
    service = PdfReportService(mock_repo, mock_progress)
    execution_id = "exec-logic"

    # Mock Execution with Logic and Ethics Data
    # Create WorkflowState with Context Variables instead of trace_data dicts
    mock_execution = ExecutionRecord(
        id=execution_id,
        workflow_id="test",
        status="completed",
        completed_at=datetime.now(timezone.utc),
        results=WorkflowState(
            workflow_id="test",
            execution_trace=[
                TraceEvent(
                    event_type="output",
                    step_name="step_logician",
                    content={
                        "cognitive_level": {
                            "bloom_level": "Analyzing",
                            "bloom_score": 4.0,
                            "strategic_depth": "High",
                            "strategic_score": 3.0,
                        },
                        "toulmin_analysis": [
                            {
                                "id": "t1",
                                "claim": "C",
                                "data": "D",
                                "warrant": "W",
                                "component_type": "Data",
                                "content": "Facts",
                                "evaluation": "Good",
                            }
                        ],
                        "toulmin_score": 4.0,
                        "walton_scheme": {"identified_scheme": "Expert", "critical_questions": []},
                        "arguments": [],
                    },
                ),
                TraceEvent(
                    event_type="output",
                    step_name="step_judge_cognitive",
                    content={
                        "score_card": {
                            "agent_name": "Cognitive Analyst",
                            "max_score": 5,
                            "total_score": 4.0,
                            "scale_min": 1,
                            "scale_max": 5,
                            "verdict": "v",
                        },
                        "pisteet": {"Bloom's Taxonomy": {"arvosana": 4.0, "perustelu": "Remembering based."}},
                        "kriittiset_havainnot_yhteenveto": [],
                    },
                ),
                TraceEvent(
                    event_type="output",
                    step_name="step_overseer",
                    content={
                        "fact_checks": [
                            {
                                "claim": "Test Claim",
                                "verification_result": "Verified",
                                "source_or_reasoning": "Source A",
                            }
                        ],
                        "ethical_issues": [
                            {"issue_type": "Bias", "severity": "Warning", "description": "Minor bias detected"}
                        ],
                    },
                ),
            ],
        ),
    )
    mock_repo.get_execution.return_value = mock_execution

    # Mock Chart Service to return a bubble chart
    with patch("backend.services.pdf_generator.ChartService") as mock_cs:
        mock_cs.generate_bubble_chart.return_value = "data:image/png;base64,bubble_mock"

        # Execute
        await service.generate_execution_pdf(execution_id)

        # Verify WeasyPrint called (implies successful template rendering of new data)
        mock_weasyprint.HTML.assert_called_once()
