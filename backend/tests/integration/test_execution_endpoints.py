from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from backend.dependencies import get_current_user_from_header
from backend.main import app
from backend.models.auth import TokenData, UserRole
from backend.models.domain.execution import ExecutionRecord
from backend.models.domain.judge import DimensionResultItem, JudgeScoreCard
from backend.models.domain.xai import XAIOutput
from backend.models.dtos.report import XAIFlatReportDTO
from backend.models.state import TraceEvent, WorkflowState
from backend.models.view.sdui import ReportView, SectionType


# Create a clean mock repository
def create_mock_repo():
    repo = AsyncMock()
    return repo


# Mock User for Auth
async def mock_get_current_user() -> TokenData:
    return TokenData(id="test_user", role=UserRole.ADMIN, email="test@example.com", organization_id="test_org")


@pytest.mark.asyncio
async def test_get_execution_view_endpoint():
    """Verify GET /executions/{id}/view returns strict ReportView (SDUI)."""
    exec_uuid = uuid4()
    exec_id = str(exec_uuid)
    state = WorkflowState(execution_id=exec_uuid, workflow_id="wf-123")

    # Populate XAI Output with ALL required fields
    xai_out = XAIOutput(
        thought_process="Reasoning...",
        conclusion="Conclusion.",
        confidence_score=0.9,
        executive_summary="Test Summary",
        analysis_strengths="Strength A",
        analysis_weaknesses="Weakness B",
        analysis_opportunities="Opp C",
        analysis_recommendations="Rec D",
        final_verdict="Approved",
        score_cards=[
            JudgeScoreCard(
                agent_name="Test XAI",
                total_score=4.5,
                max_score=5,
                scale_min=0.0,
                scale_max=5.0,
                verdict="Approved",
                dimensions=[
                    DimensionResultItem(dimension_id="dim1", dimension_label="Dim 1", score=4.0, reasoning="Good"),
                    DimensionResultItem(dimension_id="dim2", dimension_label="Dim 2", score=5.0, reasoning="Excellent"),
                ],
            )
        ],
    )
    xai_dict = xai_out.model_dump()
    xai_dict["xai_report_formatted"] = "Test Summary"
    state.execution_trace.append(TraceEvent(event_type="output", step_name="step_xai", content=xai_dict))

    # Store in context variables so ReportTransformer can inflate it
    state.context_variables["step_xai"] = xai_dict

    # ReportTransformer expects step_judge to assemble the score card layout
    step_judge_dict = {
        "thought_process": "Judge logic",
        "conclusion": "Judge conclusion",
        "confidence_score": 0.9,
        "score_card": xai_out.score_cards[0].model_dump(),
        "matrix_id": "test_matrix"
    }
    state.context_variables["step_judge"] = step_judge_dict


    mock_repo = create_mock_repo()
    mock_repo.get_execution.return_value = ExecutionRecord(
        id=exec_id, workflow_id="wf-123", status="completed", completed_at=datetime.now(timezone.utc), results=state
    )
    # Inject Mock into Singleton
    import backend.api.routes.execution.views
    import backend.dependencies

    # Force override on BOTH keys just in case
    app.dependency_overrides[backend.dependencies.get_async_repository] = lambda: mock_repo
    app.dependency_overrides[backend.api.routes.execution.views.get_async_repository] = lambda: mock_repo
    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user

    # Also set Singleton as fallback
    backend.dependencies._repository_instance = mock_repo

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get(f"/executions/{exec_id}/view")

        assert response.status_code == 200, f"Response: {response.text}"
        data = response.json()

        # Verify ReportView structure (SDUI)
        view = ReportView(**data)
        assert view.view_id == exec_id
        assert view.title == "Auditintiraportti"
        assert len(view.sections) >= 2  # Summary + Scorecard

        # Check Summary Section
        summary = next((s for s in view.sections if s.id == "xai-summary"), None)
        assert summary is not None
        assert summary.type == SectionType.MARKDOWN_BLOCK
        # Data is dict when parsed from JSON unless we explicitly cast via strict typing on UiSection.data
        # In Pydantic V2 processing, data might be dict if Any is used.
        # ReportTransformer ensures it is MarkdownBlockDisplay, but JSON dump converts to dict.
        assert "Test Summary" in summary.data["content"]

    finally:
        # Reset Singleton and Overrides
        backend.dependencies._repository_instance = None
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_flat_report_endpoint():
    """Verify GET /executions/{id}/flat returns XAIFlatReportDTO."""
    exec_uuid = uuid4()
    exec_id = str(exec_uuid)
    state = WorkflowState(execution_id=exec_uuid, workflow_id="wf-123")

    flat_report = XAIFlatReportDTO(
        execution_id=exec_uuid,
        timestamp=datetime.now(),
        verdict="Approved",
        score_total=4.5,
        confidence_score=0.9,
        flattened_scores={"dim1": 4.0, "dim2": 5.0},
        top_strength_id="dim2",
        top_weakness_id="dim1",
    )

    state.execution_trace.append(
        TraceEvent(
            event_type="output", step_name="step_xai", content={"flat_report": flat_report.model_dump(mode="json")}
        )
    )
    state.context_variables["step_xai"] = {"flat_report": flat_report.model_dump(mode="json")}

    mock_repo = create_mock_repo()
    mock_repo.get_execution.return_value = ExecutionRecord(
        id=exec_id, workflow_id="wf-123", status="completed", completed_at=datetime.now(timezone.utc), results=state
    )

    import backend.dependencies

    backend.dependencies._repository_instance = mock_repo
    app.dependency_overrides[backend.dependencies.get_async_repository] = lambda: mock_repo
    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get(f"/executions/{exec_id}/flat")

        assert response.status_code == 200, f"Response: {response.text}"
        data = response.json()
        assert data["execution_id"] == exec_id
        assert data["flattened_scores"]["dim1"] == 4.0
    finally:
        backend.dependencies._repository_instance = None


@pytest.mark.asyncio
async def test_get_pdf_endpoint():
    """Verify GET /executions/{id}/pdf returns PDF content."""
    exec_uuid = uuid4()
    exec_id = str(exec_uuid)
    state = WorkflowState(execution_id=exec_uuid, workflow_id="wf-123")

    # We don't need full state if PdfService is mocked, but repo.get_execution must return SOMETHING.
    mock_repo = create_mock_repo()
    mock_repo.get_execution.return_value = ExecutionRecord(
        id=exec_id, workflow_id="wf-123", status="completed", completed_at=datetime.now(timezone.utc), results=state
    )

    import backend.api.routes.execution.views
    import backend.dependencies

    app.dependency_overrides[backend.dependencies.get_async_repository] = lambda: mock_repo
    app.dependency_overrides[backend.api.routes.execution.views.get_async_repository] = lambda: mock_repo
    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user
    backend.dependencies._repository_instance = mock_repo

    try:
        # Patch the PdfReportService inside views.py or where it is imported.
        # It is imported inside the function in views.py: 'from backend.services.pdf_generator import PdfReportService'
        # So we patch 'backend.services.pdf_generator.PdfReportService'
        with patch("backend.services.pdf_generator.PdfReportService") as MockService:
            mock_instance = MockService.return_value
            mock_instance.generate_execution_pdf = AsyncMock(return_value=b"%PDF-1.4...")

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get(f"/executions/{exec_id}/pdf")

            assert response.status_code == 200, f"Response: {response.text}"
            assert response.content == b"%PDF-1.4..."
    finally:
        backend.dependencies._repository_instance = None
        app.dependency_overrides.clear()
