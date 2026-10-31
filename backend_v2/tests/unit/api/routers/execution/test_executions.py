"""Test suite for execution router endpoints."""

from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import (
    get_arq_pool,
    get_current_user_from_header,
    get_execution_service,
)
from backend_v2.exceptions import (
    AppException,
    ErrorCodes,
    PermissionDeniedError,
    ResourceNotFoundError,
)
from backend_v2.main import app
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.execution_core import ExecutionMetadata

MOCK_USER_ID = "usr_0195f3a0000070018234567890abcdef"
MOCK_ORG_ID = "org_0195f3a0000070018234567890abcdef"
MOCK_EXE_ID = "exe_0195f3a0000070018234567890abcdef"
MOCK_WOR_ID = "wor_0195f3a0000070018234567890abcdef"
MOCK_PRF_ID = "prf_0195f3a0000070018234567890abcdef"
MOCK_ATM_ID = "atm_0195f3a0000070018234567890abcdef"
MOCK_EVQ_ID = "evq_0195f3a0000070018234567890abcdef"

# Basic mock for user
mock_user = TokenData(id=MOCK_USER_ID, role=UserRole.ROOT, organization_id=MOCK_ORG_ID)


@pytest.fixture
def override_dependencies() -> Generator[None]:
    """Override FastAPI authentication and Arq pool dependencies."""
    app.dependency_overrides[get_current_user_from_header] = lambda: mock_user
    app.dependency_overrides[get_arq_pool] = lambda: AsyncMock()
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_execution_service() -> Any:
    """Provide a mocked ExecutionService injected into the router."""
    service = AsyncMock()
    app.dependency_overrides[get_execution_service] = lambda: service
    return service


def test_start_execution_null_matrix_sampling_strategy_regression(
    override_dependencies: Any, mock_execution_service: Any
) -> None:
    """Regression test: Flutter client sends null for matrix_sampling_strategy when omitted."""
    client = TestClient(app)

    mock_record = ExecutionRecord(
        id=MOCK_EXE_ID,
        workflow_id=MOCK_WOR_ID,
        output_profile_id=MOCK_PRF_ID,
        target_locale="fi",
        metadata=ExecutionMetadata(matrix_sampling_strategy=10),
    )
    mock_execution_service.start_execution.return_value = mock_record

    payload = {
        "workflow_id": MOCK_WOR_ID,
        "target_locale": "fi",
        "raw_inputs": {"dynamic_inputs": {}},
        "profile_id": None,
        "matrix_sampling_strategy": None,
    }

    response = client.post("/api/v2/execution/executions/", json=payload)

    # When sent with matrix_sampling_strategy: null, FastAPI must accept and apply default
    assert response.status_code == 202


def test_start_execution_invalid_payload_422(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Negative test: POST /api/v2/execution/executions/ rejects invalid schema payload with 422."""
    client = TestClient(app)
    response = client.post("/api/v2/execution/executions/", json={"unexpected_field": "invalid"})
    assert response.status_code == 422


def test_list_executions_returns_records(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Test GET /api/v2/execution/executions/ returns execution records."""
    client = TestClient(app)
    mock_record = ExecutionRecord(
        id=MOCK_EXE_ID,
        workflow_id=MOCK_WOR_ID,
        output_profile_id=MOCK_PRF_ID,
        target_locale="fi",
        metadata=ExecutionMetadata(matrix_sampling_strategy=10),
    )
    mock_execution_service.list_executions.return_value = [mock_record]

    response = client.get("/api/v2/execution/executions/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == MOCK_EXE_ID


def test_get_execution_status(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Test GET /api/v2/execution/executions/{execution_id} returns status."""
    client = TestClient(app)
    mock_record = ExecutionRecord(
        id=MOCK_EXE_ID,
        workflow_id=MOCK_WOR_ID,
        output_profile_id=MOCK_PRF_ID,
        target_locale="fi",
        metadata=ExecutionMetadata(matrix_sampling_strategy=10),
    )
    mock_execution_service.get_execution.return_value = mock_record

    response = client.get(f"/api/v2/execution/executions/{MOCK_EXE_ID}")
    assert response.status_code == 200
    assert response.json()["id"] == MOCK_EXE_ID


def test_get_execution_status_not_found_404(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Negative test: GET /api/v2/execution/executions/{execution_id} returns 404 when missing."""
    client = TestClient(app)
    mock_execution_service.get_execution.side_effect = ResourceNotFoundError(
        resource_type="Execution", resource_id=MOCK_EXE_ID
    )

    response = client.get(f"/api/v2/execution/executions/{MOCK_EXE_ID}")
    assert response.status_code == 404
    assert response.json()["extensions"]["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


def test_get_execution_status_permission_denied_403(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Negative test: GET /api/v2/execution/executions/{execution_id} returns 403 when forbidden."""
    client = TestClient(app)
    mock_execution_service.get_execution.side_effect = PermissionDeniedError("Access denied")

    response = client.get(f"/api/v2/execution/executions/{MOCK_EXE_ID}")
    assert response.status_code == 403
    assert response.json()["extensions"]["error_code"] == ErrorCodes.PERMISSION_DENIED.value


def test_resume_execution(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Test POST /api/v2/execution/executions/{execution_id}/resume resumes workflow."""
    client = TestClient(app)
    mock_record = ExecutionRecord(
        id=MOCK_EXE_ID,
        workflow_id=MOCK_WOR_ID,
        output_profile_id=MOCK_PRF_ID,
        target_locale="fi",
        metadata=ExecutionMetadata(matrix_sampling_strategy=10),
    )
    mock_execution_service.resume_execution.return_value = mock_record

    response = client.post(f"/api/v2/execution/executions/{MOCK_EXE_ID}/resume")
    assert response.status_code == 202
    assert response.json()["id"] == MOCK_EXE_ID


def test_resume_execution_unresumable_state_409(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Negative test: POST /api/v2/execution/executions/{execution_id}/resume returns 409 when unresumable."""
    client = TestClient(app)
    mock_execution_service.resume_execution.side_effect = AppException(
        message="Execution is not in a resumable state",
        status_code=409,
        details={"error_code": ErrorCodes.UNRESUMABLE_STATE_ERROR.value},
    )

    response = client.post(f"/api/v2/execution/executions/{MOCK_EXE_ID}/resume")
    assert response.status_code == 409
    assert response.json()["extensions"]["error_code"] == ErrorCodes.UNRESUMABLE_STATE_ERROR.value


def test_stream_execution_status(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Test GET /api/v2/execution/executions/{execution_id}/stream returns SSE stream."""
    client = TestClient(app)

    async def fake_stream(*args: Any, **kwargs: Any) -> Any:
        yield 'data: {"status": "running"}\n\n'

    mock_execution_service.stream_status = fake_stream

    response = client.get(f"/api/v2/execution/executions/{MOCK_EXE_ID}/stream")
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]


def test_delete_execution(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Test DELETE /api/v2/execution/executions/{execution_id} returns 204."""
    client = TestClient(app)
    mock_execution_service.delete_execution.return_value = None

    response = client.delete(f"/api/v2/execution/executions/{MOCK_EXE_ID}")
    assert response.status_code == 204


def test_download_frozen_context(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Test GET /api/v2/execution/executions/{execution_id}/frozen_context."""
    client = TestClient(app)
    mock_execution_service.get_frozen_context_bytes.return_value = (b'{"key": "val"}', "frozen_context.json")

    response = client.get(f"/api/v2/execution/executions/{MOCK_EXE_ID}/frozen_context")
    assert response.status_code == 200
    assert response.headers["content-disposition"] == 'attachment; filename="frozen_context.json"'
    assert response.content == b'{"key": "val"}'


def test_delete_profile_synthesis(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Test DELETE /api/v2/execution/executions/{execution_id}/profiles/{profile_id}."""
    client = TestClient(app)
    mock_execution_service.clear_profile_synthesis.return_value = None

    response = client.delete(f"/api/v2/execution/executions/{MOCK_EXE_ID}/profiles/{MOCK_PRF_ID}")
    assert response.status_code == 204


def test_override_atom(override_dependencies: Any, mock_execution_service: Any) -> None:
    """Test PATCH /api/v2/execution/executions/{execution_id}/atoms/{atom_id}/override."""
    client = TestClient(app)
    mock_execution_service.override_atom.return_value = None

    payload = {"reason": "Manual review correction", "new_status": "PASSED"}
    response = client.patch(
        f"/api/v2/execution/executions/{MOCK_EXE_ID}/atoms/{MOCK_ATM_ID}/override",
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
        f"/api/v2/execution/executions/{MOCK_EXE_ID}/evidence/{MOCK_EVQ_ID}/reject",
        json=payload,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.parametrize(
    "method,path",
    [
        ("GET", "/api/v2/execution/executions/exe_0195f3a0000070018234567890abcdef/render"),
        ("POST", "/api/v2/execution/executions/exe_0195f3a0000070018234567890abcdef/render_pdf"),
        ("GET", "/api/v2/execution/executions/exe_0195f3a0000070018234567890abcdef/export"),
        ("GET", "/api/v2/execution/executions/exe_0195f3a0000070018234567890abcdef/report"),
        ("GET", "/api/v2/execution/executions/exe_0195f3a0000070018234567890abcdef/sdui"),
    ],
)
def test_eradicated_render_routes_return_404(
    override_dependencies: Any, mock_execution_service: Any, method: str, path: str
) -> None:
    """Proof Anchor: Eradicated presentation routes must return HTTP 404, not 405 or 200."""
    client = TestClient(app)
    response = client.request(method, path)
    assert response.status_code == 404, f"Residual route detected for {method} {path}: {response.status_code}"


def test_eradicated_render_routes_absent_from_route_table() -> None:
    """Proof Anchor: Eradicated presentation route templates must be absent from app route table."""
    route_paths = {route.path for route in app.routes if isinstance(route, APIRoute)}
    eradicated_paths = {
        "/api/v2/execution/executions/{execution_id}/render",
        "/api/v2/execution/executions/{execution_id}/render_pdf",
        "/api/v2/execution/executions/{execution_id}/export",
        "/api/v2/execution/executions/{execution_id}/report",
        "/api/v2/execution/executions/{execution_id}/sdui",
    }
    present_eradicated = route_paths.intersection(eradicated_paths)
    assert not present_eradicated, f"Residual route templates found in app.routes: {present_eradicated}"
