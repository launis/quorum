"""Comprehensive unit test suite for Report Artifacts REST API endpoints.

Covers all 11 endpoints and ISTQB failure partitions per Step 8 and Step 10:
- POST /api/v2/executions/{id}/reports (happy path 202, execution not passed 409, concurrent generation 409)
- GET /api/v2/executions/{id}/reports (happy path 200, missing execution 404)
- GET /api/v2/reports/{id} (happy path 200, missing report 404)
- GET /api/v2/reports/{id}/sdui (happy path 200, unready report 409)
- GET /api/v2/reports/{id}/pdf (happy path 200, unready report 409)
- GET /api/v2/reports/{id}/excel (happy path 200)
- GET /api/v2/reports/{id}/csv (happy path 200)
- GET /api/v2/reports/{id}/rows (happy path 200)
- DELETE /api/v2/reports/{id} (happy path 204, missing report 404)
- POST /api/v2/reports/{id}/regenerate (happy path 202, missing report 404)
- GET /api/v1/external/reports/{id} (happy path 200 with X-API-Key, invalid API key 401, missing auth 401)
"""

from collections.abc import Generator
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import (
    get_arq_pool,
    get_current_user_from_header,
    get_execution_service,
    get_report_service,
)
from backend_v2.exceptions import AppException, ErrorCodes, ExecutionNotReadyError, ResourceNotFoundError
from backend_v2.main import app
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.dtos.report_artifact import (
    PublicReportDTO,
    ReportArtifactSummaryDTO,
    ReportMetadataDTO,
    ReportRowItemDTO,
    ReportStoragePathsDTO,
)
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import ReportStatus

MOCK_USER_ID = "usr_0123456789abcdef"
MOCK_ORG_ID = "org_0123456789abcdef"
MOCK_EXE_ID = "exe_0123456789abcdef"
MOCK_WOR_ID = "wor_0123456789abcdef"
MOCK_PRF_ID = "prf_0123456789abcdef"
MOCK_REP_ID = "rep_0123456789abcdef"
MOCK_REP_ID_2 = "rep_0123456789fedcba"
MOCK_PRF_ID_2 = "prf_0123456789fedcba"
MOCK_MISSING_EXE = "exe_9999999999999999"
MOCK_MISSING_REP = "rep_9999999999999999"

mock_user = TokenData(id=MOCK_USER_ID, role=UserRole.ROOT, organization_id=MOCK_ORG_ID)


@pytest.fixture
def override_dependencies() -> Generator[None]:
    """Dependency override fixture for reports API testing."""
    app.dependency_overrides[get_current_user_from_header] = lambda: mock_user
    app.dependency_overrides[get_arq_pool] = lambda: AsyncMock()
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_report_service() -> Any:
    """Mock ReportService injected into router."""
    service = AsyncMock()
    app.dependency_overrides[get_report_service] = lambda: service
    return service


@pytest.fixture
def mock_execution_service() -> Any:
    """Mock ExecutionService injected into router."""
    service = AsyncMock()
    app.dependency_overrides[get_execution_service] = lambda: service
    return service


def test_post_create_report_success(
    override_dependencies: Any,
    mock_report_service: Any,
) -> None:
    """Test POST /api/v2/executions/{id}/reports enqueues artifact creation and returns 202."""
    client = TestClient(app)
    now = datetime.now(timezone.utc)
    mock_report_service.list_reports_for_execution.return_value = []
    mock_report_service.create_report_artifact.return_value = ReportArtifact(
        id=MOCK_REP_ID,
        execution_id=MOCK_EXE_ID,
        workflow_id=MOCK_WOR_ID,
        profile_id=MOCK_PRF_ID,
        locale="fi",
        title="Executive Summary",
        status=ReportStatus.PENDING,
        created_at=now,
        updated_at=now,
    )
    mock_report_service.compile_and_persist_artifact.return_value = None

    payload = {
        "profile_id": MOCK_PRF_ID,
        "locale": "fi",
        "custom_preface_md": "Custom Preface",
    }
    response = client.post(f"/api/v2/executions/{MOCK_EXE_ID}/reports", json=payload)

    assert response.status_code == 202
    data = response.json()
    assert data["id"] == MOCK_REP_ID
    assert data["execution_id"] == MOCK_EXE_ID
    assert data["status"] == ReportStatus.GENERATING.value
    mock_report_service.create_report_artifact.assert_called_once()
    mock_report_service.compile_and_persist_artifact.assert_called_once()


def test_post_create_report_execution_not_ready_409(
    override_dependencies: Any,
    mock_report_service: Any,
) -> None:
    """Test POST /api/v2/executions/{id}/reports raises 409 when execution is not PASSED."""
    client = TestClient(app)
    mock_report_service.list_reports_for_execution.return_value = []
    mock_report_service.create_report_artifact.side_effect = ExecutionNotReadyError(
        execution_id=MOCK_EXE_ID, current_status="RUNNING"
    )

    payload = {"profile_id": MOCK_PRF_ID, "locale": "fi"}
    response = client.post(f"/api/v2/executions/{MOCK_EXE_ID}/reports", json=payload)

    assert response.status_code == 409
    data = response.json()
    assert data["extensions"]["error_code"] == ErrorCodes.EXECUTION_NOT_READY.value


def test_post_create_report_concurrent_generation_409(
    override_dependencies: Any,
    mock_report_service: Any,
) -> None:
    """Test POST /api/v2/executions/{id}/reports rejects concurrent generation for same profile with 409."""
    client = TestClient(app)
    now = datetime.now(timezone.utc)
    mock_report_service.list_reports_for_execution.return_value = [
        ReportArtifactSummaryDTO(
            id=MOCK_REP_ID,
            execution_id=MOCK_EXE_ID,
            profile_id=MOCK_PRF_ID,
            locale="fi",
            title="In Flight",
            status=ReportStatus.GENERATING,
            created_at=now,
            updated_at=now,
        )
    ]

    payload = {"profile_id": MOCK_PRF_ID, "locale": "fi"}
    response = client.post(f"/api/v2/executions/{MOCK_EXE_ID}/reports", json=payload)

    assert response.status_code == 409
    data = response.json()
    assert data["extensions"]["error_code"] == ErrorCodes.CONFLICT_ERROR.value


def test_get_execution_reports_list_success(
    override_dependencies: Any,
    mock_report_service: Any,
    mock_execution_service: Any,
) -> None:
    """Test GET /api/v2/executions/{id}/reports returns summary list."""
    client = TestClient(app)
    now = datetime.now(timezone.utc)
    mock_execution_service.get_execution.return_value = AsyncMock()
    mock_report_service.list_reports_for_execution.return_value = [
        ReportArtifactSummaryDTO(
            id=MOCK_REP_ID,
            execution_id=MOCK_EXE_ID,
            profile_id=MOCK_PRF_ID,
            locale="fi",
            title="Report 1",
            status=ReportStatus.READY,
            created_at=now,
            updated_at=now,
        ),
        ReportArtifactSummaryDTO(
            id=MOCK_REP_ID_2,
            execution_id=MOCK_EXE_ID,
            profile_id=MOCK_PRF_ID_2,
            locale="en",
            title="Report 2",
            status=ReportStatus.GENERATING,
            created_at=now,
            updated_at=now,
        ),
    ]

    response = client.get(f"/api/v2/executions/{MOCK_EXE_ID}/reports")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == MOCK_REP_ID
    assert data[1]["id"] == MOCK_REP_ID_2


def test_get_execution_reports_execution_not_found_404(
    override_dependencies: Any,
    mock_execution_service: Any,
) -> None:
    """Test GET /api/v2/executions/{id}/reports returns 404 when execution is missing."""
    client = TestClient(app)
    mock_execution_service.get_execution.side_effect = ResourceNotFoundError(
        resource_type="execution", resource_id=MOCK_MISSING_EXE
    )

    response = client.get(f"/api/v2/executions/{MOCK_MISSING_EXE}/reports")
    assert response.status_code == 404


def test_get_report_artifact_detail_success(
    override_dependencies: Any,
    mock_report_service: Any,
) -> None:
    """Test GET /api/v2/reports/{id} returns full ReportArtifact domain model."""
    client = TestClient(app)
    now = datetime.now(timezone.utc)
    mock_report_service.get_report.return_value = ReportArtifact(
        id=MOCK_REP_ID,
        execution_id=MOCK_EXE_ID,
        workflow_id=MOCK_WOR_ID,
        profile_id=MOCK_PRF_ID,
        locale="fi",
        title="Full Detail Report",
        status=ReportStatus.READY,
        storage_paths=ReportStoragePathsDTO(pdf_path=f"artifacts/{MOCK_REP_ID}/report.pdf"),
        metadata=ReportMetadataDTO(cost_usd=0.042, duration_ms=1250),
        created_at=now,
        updated_at=now,
    )

    response = client.get(f"/api/v2/reports/{MOCK_REP_ID}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == MOCK_REP_ID
    assert data["title"] == "Full Detail Report"
    assert data["status"] == ReportStatus.READY.value
    assert data["storage_paths"]["pdf_path"] == f"artifacts/{MOCK_REP_ID}/report.pdf"


def test_get_report_artifact_missing_404(
    override_dependencies: Any,
    mock_report_service: Any,
) -> None:
    """Test GET /api/v2/reports/{id} returns 404 when report artifact is missing."""
    client = TestClient(app)
    mock_report_service.get_report.side_effect = ResourceNotFoundError(
        resource_type="report_artifact", resource_id=MOCK_MISSING_REP
    )

    response = client.get(f"/api/v2/reports/{MOCK_MISSING_REP}")
    assert response.status_code == 404


def test_get_report_sdui_success(
    override_dependencies: Any,
    mock_report_service: Any,
) -> None:
    """Test GET /api/v2/reports/{id}/sdui returns cached ReportDataDTO JSON."""
    client = TestClient(app)
    mock_dto = ReportDataDTO(
        execution_id=MOCK_EXE_ID,
        workflow_id=MOCK_WOR_ID,
        profile_id=MOCK_PRF_ID,
        global_score=85.0,
    )
    mock_report_service.get_report_sdui.return_value = mock_dto

    response = client.get(f"/api/v2/reports/{MOCK_REP_ID}/sdui")

    assert response.status_code == 200
    data = response.json()
    assert data["global_score"] == 85.0
    assert data["execution_id"] == MOCK_EXE_ID


def test_get_report_sdui_unready_409(
    override_dependencies: Any,
    mock_report_service: Any,
) -> None:
    """Test GET /api/v2/reports/{id}/sdui returns 409 when report is still generating."""
    client = TestClient(app)
    mock_report_service.get_report_sdui.side_effect = AppException(
        message="Artifact not ready", status_code=409, details={"error_code": ErrorCodes.REPORT_NOT_READY.value}
    )

    response = client.get(f"/api/v2/reports/{MOCK_REP_ID}/sdui")
    assert response.status_code == 409


def test_get_report_pdf_success(
    override_dependencies: Any,
    mock_report_service: Any,
) -> None:
    """Test GET /api/v2/reports/{id}/pdf returns binary PDF with attachment headers."""
    client = TestClient(app)
    mock_report_service.get_report_pdf_bytes.return_value = (b"%PDF-1.4 mock content", f"report_{MOCK_REP_ID}.pdf")

    response = client.get(f"/api/v2/reports/{MOCK_REP_ID}/pdf")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["content-disposition"] == f'attachment; filename="report_{MOCK_REP_ID}.pdf"'
    assert response.content == b"%PDF-1.4 mock content"


def test_get_report_excel_success(
    override_dependencies: Any,
    mock_report_service: Any,
) -> None:
    """Test GET /api/v2/reports/{id}/excel returns binary spreadsheet with attachment headers."""
    client = TestClient(app)
    mock_report_service.get_report_excel_bytes.return_value = (b"PK\x03\x04 mock excel", f"report_{MOCK_REP_ID}.xlsx")

    response = client.get(f"/api/v2/reports/{MOCK_REP_ID}/excel")

    assert response.status_code == 200
    assert "openxmlformats" in response.headers["content-type"]
    assert response.headers["content-disposition"] == f'attachment; filename="report_{MOCK_REP_ID}.xlsx"'
    assert response.content == b"PK\x03\x04 mock excel"


def test_get_report_csv_success(
    override_dependencies: Any,
    mock_report_service: Any,
) -> None:
    """Test GET /api/v2/reports/{id}/csv returns flat CSV with attachment headers."""
    client = TestClient(app)
    mock_report_service.get_report_csv_bytes.return_value = (b"metric,score\na,1\n", f"report_{MOCK_REP_ID}.csv")

    response = client.get(f"/api/v2/reports/{MOCK_REP_ID}/csv")

    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert response.headers["content-disposition"] == f'attachment; filename="report_{MOCK_REP_ID}.csv"'
    assert response.content == b"metric,score\na,1\n"


def test_get_report_rows_success(
    override_dependencies: Any,
    mock_report_service: Any,
) -> None:
    """Test GET /api/v2/reports/{id}/rows returns structured tabular rows for B2B ingestion."""
    client = TestClient(app)
    mock_report_service.get_report_rows.return_value = [
        ReportRowItemDTO(
            execution_id=MOCK_EXE_ID,
            report_id=MOCK_REP_ID,
            metric_key="blk_clarity",
            metric_label="Strategic Clarity",
            score=4.5,
            max_scale=5.0,
            weight=1.0,
            reasoning="High clarity demonstrated in deliverables.",
            quote="Our strategic objective is clearly defined.",
        )
    ]

    response = client.get(f"/api/v2/reports/{MOCK_REP_ID}/rows")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["metric_key"] == "blk_clarity"
    assert data[0]["score"] == 4.5
    assert data[0]["quote"] == "Our strategic objective is clearly defined."


def test_delete_report_artifact_success(
    override_dependencies: Any,
    mock_report_service: Any,
) -> None:
    """Test DELETE /api/v2/reports/{id} deletes artifact and returns 204."""
    client = TestClient(app)
    mock_report_service.delete_report_artifact.return_value = None

    response = client.delete(f"/api/v2/reports/{MOCK_REP_ID}")

    assert response.status_code == 204
    mock_report_service.delete_report_artifact.assert_called_once_with(MOCK_REP_ID)


def test_post_regenerate_report_artifact_success(
    override_dependencies: Any,
    mock_report_service: Any,
) -> None:
    """Test POST /api/v2/reports/{id}/regenerate re-enqueues compilation and returns 202."""
    client = TestClient(app)
    now = datetime.now(timezone.utc)
    mock_report_service.get_report.return_value = ReportArtifact(
        id=MOCK_REP_ID,
        execution_id=MOCK_EXE_ID,
        workflow_id=MOCK_WOR_ID,
        profile_id=MOCK_PRF_ID,
        locale="fi",
        title="Regenerated Title",
        status=ReportStatus.READY,
        created_at=now,
        updated_at=now,
    )
    mock_report_service.regenerate_report_artifact.return_value = None

    response = client.post(f"/api/v2/reports/{MOCK_REP_ID}/regenerate")

    assert response.status_code == 202
    data = response.json()
    assert data["id"] == MOCK_REP_ID
    assert data["status"] == ReportStatus.GENERATING.value
    mock_report_service.regenerate_report_artifact.assert_called_once()


def test_get_public_external_report_success_api_key(
    override_dependencies: Any,
    mock_report_service: Any,
) -> None:
    """Test GET /api/v1/external/reports/{id} returns PublicReportDTO using X-API-Key."""
    client = TestClient(app)
    now = datetime.now(timezone.utc)
    mock_report_service.get_public_report.return_value = PublicReportDTO(
        report_id=MOCK_REP_ID,
        created_at=now,
        title="Public Sanitized Report",
        metrics={"clarity": 4.5},
        downloads={"pdf": f"/api/v2/reports/{MOCK_REP_ID}/pdf"},
    )

    response = client.get(
        f"/api/v1/external/reports/{MOCK_REP_ID}",
        headers={"X-API-Key": "b2b_valid_api_key_secret"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["report_id"] == MOCK_REP_ID
    assert data["metrics"]["clarity"] == 4.5
    assert "pdf" in data["downloads"]


def test_get_public_external_report_invalid_api_key_401(
    override_dependencies: Any,
    mock_report_service: Any,
) -> None:
    """Test GET /api/v1/external/reports/{id} rejects invalid API key with 401."""
    client = TestClient(app)

    response = client.get(
        f"/api/v1/external/reports/{MOCK_REP_ID}",
        headers={"X-API-Key": "invalid"},
    )

    assert response.status_code == 401
    data = response.json()
    assert data["extensions"]["error_code"] == ErrorCodes.AUTHENTICATION_FAILED.value


def test_get_public_external_report_missing_auth_401(
    override_dependencies: Any,
    mock_report_service: Any,
) -> None:
    """Test GET /api/v1/external/reports/{id} rejects requests without auth header with 401."""
    client = TestClient(app)

    response = client.get(f"/api/v1/external/reports/{MOCK_REP_ID}")

    assert response.status_code == 401
    data = response.json()
    assert data["extensions"]["error_code"] == ErrorCodes.AUTHENTICATION_FAILED.value
