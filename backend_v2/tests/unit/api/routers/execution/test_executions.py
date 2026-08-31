"""Test suite for execution router endpoints."""

from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import get_arq_pool, get_current_user_from_header, get_execution_service
from backend_v2.main import app
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.enums import VisualIntent
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.v2_core import ExecutionRecord, ReportDataDTO
from backend_v2.models.view.sdui import ReportView

# Basic mock for user
mock_user = TokenData(id="test-user-id", role=UserRole.ROOT, organization_id="root_org")


@pytest.fixture
def override_dependencies() -> Generator[None]:
    app.dependency_overrides[get_current_user_from_header] = lambda: mock_user
    app.dependency_overrides[get_arq_pool] = lambda: AsyncMock()
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_execution_service() -> Any:
    service = AsyncMock()
    app.dependency_overrides[get_execution_service] = lambda: service
    return service


def test_get_execution_report_returns_raw_dto(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Integration test for /report headless endpoint using v2_core.ReportDataDTO."""
    client = TestClient(app)

    mock_dto = ReportDataDTO(
        execution_id="test_execution_123",
        workflow_id="wf_1",
        profile_id="prf_001",
        global_score=72.5,
    )
    mock_execution_service.get_report_dto.return_value = mock_dto

    response = client.get("/api/v2/execution/executions/test_execution_123/report")

    assert response.status_code == 200
    data = response.json()
    assert data["workflow_id"] == "wf_1"
    assert data["profile_id"] == "prf_001"
    assert data["global_score"] == 72.5
    # Ensure it's not wrapped in SDUI
    assert "sections" not in data


def test_get_execution_sdui_returns_view(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Integration test for /sdui SDUI view endpoint."""
    client = TestClient(app)

    mock_sdui_view = ReportView(
        view_id="test_execution_123",
        title="SDUI Raportti",
        status_theme=VisualIntent.SUCCESS,
        sections=[],
        metrics=None,
        system_notification=None,
        references=[],
    )
    mock_execution_service.get_sdui_view.return_value = mock_sdui_view

    response = client.get("/api/v2/execution/executions/test_execution_123/sdui")

    assert response.status_code == 200
    data = response.json()
    assert data["view_id"] == "test_execution_123"
    assert data["title"] == "SDUI Raportti"
    assert "sections" in data


def test_start_execution_null_matrix_sampling_strategy_regression(
    override_dependencies: Any, mock_execution_service: Any
) -> None:
    """Regression test: Flutter client sends null for matrix_sampling_strategy when omitted."""
    client = TestClient(app)

    mock_record = ExecutionRecord(
        id="exe_1234567890abcdef",
        workflow_id="wor_standard_audit",
        target_locale="fi",
        metadata=ExecutionMetadata(
            target_locale="fi",
            profile_id="prf_001",
            matrix_sampling_strategy=10,
        ),
    )
    mock_execution_service.start_execution.return_value = mock_record

    payload = {
        "workflow_id": "wor_standard_audit",
        "target_locale": "fi",
        "raw_inputs": {"dynamic_inputs": {}},
        "profile_id": None,
        "matrix_sampling_strategy": None,
    }

    response = client.post("/api/v2/execution/executions/", json=payload)

    # When sent with matrix_sampling_strategy: null, FastAPI must accept and apply default
    assert response.status_code == 202


def test_list_executions_returns_records(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Test GET /api/v2/execution/executions/ returns execution records."""
    client = TestClient(app)
    mock_record = ExecutionRecord(
        id="exe_1234567890abcdef",
        workflow_id="wor_standard_audit",
        target_locale="fi",
        metadata=ExecutionMetadata(target_locale="fi", profile_id="prf_001", matrix_sampling_strategy=10),
    )
    mock_execution_service.list_executions.return_value = [mock_record]

    response = client.get("/api/v2/execution/executions/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "exe_1234567890abcdef"


def test_get_execution_status(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Test GET /api/v2/execution/executions/{execution_id} returns status."""
    client = TestClient(app)
    mock_record = ExecutionRecord(
        id="exe_1234567890abcdef",
        workflow_id="wor_standard_audit",
        target_locale="fi",
        metadata=ExecutionMetadata(target_locale="fi", profile_id="prf_001", matrix_sampling_strategy=10),
    )
    mock_execution_service.get_execution.return_value = mock_record

    response = client.get("/api/v2/execution/executions/exe_1234567890abcdef")
    assert response.status_code == 200
    assert response.json()["id"] == "exe_1234567890abcdef"


def test_resume_execution(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Test POST /api/v2/execution/executions/{execution_id}/resume resumes workflow."""
    client = TestClient(app)
    mock_record = ExecutionRecord(
        id="exe_1234567890abcdef",
        workflow_id="wor_standard_audit",
        target_locale="fi",
        metadata=ExecutionMetadata(target_locale="fi", profile_id="prf_001", matrix_sampling_strategy=10),
    )
    mock_execution_service.resume_execution.return_value = mock_record

    response = client.post("/api/v2/execution/executions/exe_1234567890abcdef/resume")
    assert response.status_code == 202
    assert response.json()["id"] == "exe_1234567890abcdef"


def test_stream_execution_status(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Test GET /api/v2/execution/executions/{execution_id}/stream returns SSE stream."""
    client = TestClient(app)

    async def fake_stream(*args: Any, **kwargs: Any) -> Any:
        yield "data: {\"status\": \"running\"}\n\n"

    mock_execution_service.stream_status = fake_stream

    response = client.get("/api/v2/execution/executions/exe_1234567890abcdef/stream")
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]


def test_delete_execution(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Test DELETE /api/v2/execution/executions/{execution_id} returns 204."""
    client = TestClient(app)
    mock_execution_service.delete_execution.return_value = None

    response = client.delete("/api/v2/execution/executions/exe_1234567890abcdef")
    assert response.status_code == 204


def test_download_frozen_context(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Test GET /api/v2/execution/executions/{execution_id}/frozen_context."""
    client = TestClient(app)
    mock_execution_service.get_frozen_context_bytes.return_value = (b'{"key": "val"}', "frozen_context.json")

    response = client.get("/api/v2/execution/executions/exe_1234567890abcdef/frozen_context")
    assert response.status_code == 200
    assert response.headers["content-disposition"] == 'attachment; filename="frozen_context.json"'
    assert response.content == b'{"key": "val"}'


def test_download_execution_export(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Test GET /api/v2/execution/executions/{execution_id}/export."""
    client = TestClient(app)
    mock_execution_service.get_execution_export_bytes.return_value = (b"excel-bytes", "export.xlsx")

    response = client.get("/api/v2/execution/executions/exe_1234567890abcdef/export")
    assert response.status_code == 200
    assert response.headers["content-disposition"] == 'attachment; filename="export.xlsx"'
    assert response.content == b"excel-bytes"


def test_render_execution_json(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Test GET /api/v2/execution/executions/{execution_id}/render returning dict."""
    client = TestClient(app)
    mock_execution_service.render_execution.return_value = ({"rendered": "ok"}, "application/json", None)

    response = client.get("/api/v2/execution/executions/exe_1234567890abcdef/render?format=json")
    assert response.status_code == 200
    assert response.json() == {"rendered": "ok"}


def test_render_execution_job_accepted(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Test GET /api/v2/execution/executions/{execution_id}/render returning JobAcceptedDTO."""
    from backend_v2.models.v2_core import JobAcceptedDTO

    client = TestClient(app)
    mock_execution_service.render_execution.return_value = (
        JobAcceptedDTO(status="Accepted", message="Rendering queued", execution_id="exe_1234567890abcdef"),
        "application/json",
        None,
    )

    response = client.get("/api/v2/execution/executions/exe_1234567890abcdef/render?format=pdf")
    assert response.status_code == 202
    assert response.json()["status"] == "Accepted"


def test_render_execution_binary_pdf(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Test GET /api/v2/execution/executions/{execution_id}/render returning binary pdf."""
    client = TestClient(app)
    mock_execution_service.render_execution.return_value = (b"%PDF-1.4", "application/pdf", "report.pdf")

    response = client.get("/api/v2/execution/executions/exe_1234567890abcdef/render?format=pdf")
    assert response.status_code == 200
    assert response.headers["content-disposition"] == 'attachment; filename="report.pdf"'
    assert response.content == b"%PDF-1.4"


def test_generate_pdf_async(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Test POST /api/v2/execution/executions/{execution_id}/render_pdf."""
    client = TestClient(app)
    mock_execution_service.enqueue_pdf_generation.return_value = None

    response = client.post("/api/v2/execution/executions/exe_1234567890abcdef/render_pdf")
    assert response.status_code == 202
    assert response.json()["status"] == "Accepted"


def test_delete_profile_synthesis(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Test DELETE /api/v2/execution/executions/{execution_id}/profiles/{profile_id}."""
    client = TestClient(app)
    mock_execution_service.clear_profile_synthesis.return_value = None

    response = client.delete("/api/v2/execution/executions/exe_1234567890abcdef/profiles/prf_001")
    assert response.status_code == 204


def test_override_atom(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Test PATCH /api/v2/execution/executions/{execution_id}/atoms/{atom_id}/override."""
    client = TestClient(app)
    mock_execution_service.override_atom.return_value = None

    payload = {"reason": "Manual review correction", "new_status": "PASSED"}
    response = client.patch(
        "/api/v2/execution/executions/exe_1234567890abcdef/atoms/atm_001/override",
        json=payload,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_reject_evidence_quote(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Test PUT /api/v2/execution/executions/{execution_id}/evidence/{evq_id}/reject."""
    client = TestClient(app)
    mock_execution_service.reject_evidence_quote.return_value = None

    payload = {"rejection_reason": "Out of context evidence"}
    response = client.put(
        "/api/v2/execution/executions/exe_1234567890abcdef/evidence/evq_001/reject",
        json=payload,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"



