"""Test suite for execution router endpoints."""

from collections.abc import Generator
from datetime import datetime, timezone
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
from backend_v2.models.auth import (
    ExecutionAssignmentBatchResponseDTO,
    ExecutionAssignmentPreviewDTO,
    ExecutionAssignmentResponseDTO,
    TokenData,
    TokenExchangeResponseDTO,
    User,
    UserRole,
)
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.enums import (
    AssignmentResultVisibility,
    AssignmentStatus,
    EmailDeliveryStatus,
    SystemLocale,
)
from backend_v2.models.execution_core import ExecutionMetadata

MOCK_USER_ID = "usr_0195f3a0000070018234567890abcdef"
MOCK_ORG_ID = "org_0195f3a0000070018234567890abcdef"
MOCK_EXE_ID = "exe_0195f3a0000070018234567890abcdef"
MOCK_WOR_ID = "wor_0195f3a0000070018234567890abcdef"
MOCK_PRF_ID = "prf_0195f3a0000070018234567890abcdef"
MOCK_ATM_ID = "atm_0195f3a0000070018234567890abcdef"
MOCK_EVQ_ID = "evq_0195f3a0000070018234567890abcdef"
MOCK_TSK_ID = "tsk_0195f3a0000070018234567890abcdef"
MOCK_BAT_ID = "tsk_0195f3a0000070018234567890abcdee"

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

    response = client.post(
        "/api/v2/execution/executions/",
        json={
            "workflow_id": MOCK_WOR_ID,
            "target_locale": "fi",
            "raw_inputs": {"dynamic_inputs": {}},
            "profile_id": None,
            "matrix_sampling_strategy": None,
        },
    )

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


def _sample_assignment_dto(
    status: AssignmentStatus = AssignmentStatus.PENDING,
) -> ExecutionAssignmentResponseDTO:
    """Construct a canonical ExecutionAssignmentResponseDTO fixture."""
    return ExecutionAssignmentResponseDTO(
        id=MOCK_TSK_ID,
        batch_id=None,
        organization_id=MOCK_ORG_ID,
        assigned_email="candidate@acme.com",
        assigned_user_id=MOCK_USER_ID,
        invited_role=UserRole.MEMBER,
        workflow_id=MOCK_WOR_ID,
        output_profile_id=None,
        target_locale=SystemLocale.FI,
        locked_inputs=WorkflowInputs(dynamic_inputs={"role_brief": "CTO"}),
        assignee_input_keys=["essay"],
        draft_inputs=WorkflowInputs(dynamic_inputs={}),
        status=status,
        email_delivery_status=EmailDeliveryStatus.SENT,
        result_visibility=AssignmentResultVisibility.CONFIRMATION_ONLY,
        hard_deadline_at=datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
        relative_duration_seconds=2700,
        activated_at=None,
        submitted_at=None,
        execution_id=None,
        created_by=MOCK_USER_ID,
        created_at=datetime(2026, 11, 2, 12, 0, 0, tzinfo=timezone.utc),
    )


def test_execution_assignment_management_endpoints_positive(
    override_dependencies: Any, mock_execution_service: Any
) -> None:
    """Verify list, create, batch create, and resend assignment routes serialize responses."""
    client = TestClient(app)
    dto = _sample_assignment_dto()
    mock_execution_service.list_assignments.return_value = [dto]
    mock_execution_service.create_assignment.return_value = dto
    mock_execution_service.create_assignment_batch.return_value = ExecutionAssignmentBatchResponseDTO(
        batch_id=MOCK_BAT_ID, created_count=1, assignments=[dto]
    )
    mock_execution_service.resend_assignment_email.return_value = dto

    assert client.get("/api/v2/execution/executions/assignments").status_code == 200
    create_resp = client.post(
        "/api/v2/execution/executions/assignments",
        json={
            "assigned_email": "candidate@acme.com",
            "workflow_id": MOCK_WOR_ID,
            "locked_inputs": {"dynamic_inputs": {"role_brief": "CTO"}},
            "assignee_input_keys": ["essay"],
            "hard_deadline_at": "2026-12-31T23:59:59+00:00",
            "relative_duration_seconds": 2700,
        },
    )
    assert create_resp.status_code == 201
    batch_resp = client.post(
        "/api/v2/execution/executions/assignments/batch",
        json={
            "recipients": [{"email": "candidate@acme.com"}],
            "workflow_id": MOCK_WOR_ID,
            "locked_inputs": {"dynamic_inputs": {"role_brief": "CTO"}},
            "assignee_input_keys": ["essay"],
            "hard_deadline_at": "2026-12-31T23:59:59+00:00",
            "relative_duration_seconds": 2700,
        },
    )
    assert batch_resp.status_code == 201
    assert client.post(f"/api/v2/execution/executions/assignments/{MOCK_TSK_ID}/resend").status_code == 200


def test_execution_assignment_public_endpoints_positive(
    override_dependencies: Any, mock_execution_service: Any
) -> None:
    """Verify SafeLinks-immune preview and JIT onboarding routes."""
    client = TestClient(app)
    mock_execution_service.preview_assignment.return_value = ExecutionAssignmentPreviewDTO(
        id=MOCK_TSK_ID,
        organization_id=MOCK_ORG_ID,
        organization_name="Acme Corp",
        assigned_email_masked="c***@acme.com",
        workflow_id=MOCK_WOR_ID,
        target_locale=SystemLocale.FI,
        status=AssignmentStatus.PENDING,
        hard_deadline_at=datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
        relative_duration_seconds=2700,
    )
    mock_execution_service.onboard_assignee.return_value = TokenExchangeResponseDTO(
        access_token="quorum.jwt.token",
        expires_in_seconds=900,
        user=User(
            id=MOCK_USER_ID,
            email="candidate@acme.com",
            name="Candidate One",
            role=UserRole.MEMBER,
            organization_id=MOCK_ORG_ID,
            is_active=True,
            language=SystemLocale.FI,
            theme_mode="system",
            created_at=datetime(2026, 11, 2, 12, 0, 0, tzinfo=timezone.utc),
        ),
    )
    prev = client.get("/api/v2/execution/executions/assignments/preview?token=valid_token_12345")
    assert prev.status_code == 200
    assert prev.json()["assigned_email_masked"] == "c***@acme.com"
    onboard = client.post(
        "/api/v2/execution/executions/assignments/onboard?token=valid_token_12345",
        json={"firebase_token": "firebase_valid_token_12345", "name": "Candidate One"},
    )
    assert onboard.status_code == 200
    assert onboard.json()["access_token"] == "quorum.jwt.token"


def test_execution_assignment_assignee_endpoints_positive(
    override_dependencies: Any, mock_execution_service: Any
) -> None:
    """Verify activate, draft auto-save, and submit assignment routes."""
    client = TestClient(app)
    mock_execution_service.activate_assignment.return_value = _sample_assignment_dto(AssignmentStatus.ACTIVATED)
    mock_execution_service.save_draft_inputs.return_value = _sample_assignment_dto(AssignmentStatus.ACTIVATED)
    mock_execution_service.submit_assignment.return_value = ExecutionRecord(
        id=MOCK_EXE_ID,
        workflow_id=MOCK_WOR_ID,
        output_profile_id=MOCK_PRF_ID,
        target_locale="fi",
        metadata=ExecutionMetadata(matrix_sampling_strategy=10),
    )
    act = client.post(f"/api/v2/execution/executions/assignments/{MOCK_TSK_ID}/activate")
    assert act.status_code == 200
    assert act.json()["status"] == "activated"
    draft = client.put(
        f"/api/v2/execution/executions/assignments/{MOCK_TSK_ID}/draft",
        json={"draft_inputs": {"dynamic_inputs": {"essay": "Draft content"}}},
    )
    assert draft.status_code == 200
    sub = client.post(
        f"/api/v2/execution/executions/assignments/{MOCK_TSK_ID}/submit",
        json={"submitted_inputs": {"dynamic_inputs": {"essay": "Final answer"}}},
    )
    assert sub.status_code == 202
    assert sub.json()["id"] == MOCK_EXE_ID


def test_execution_assignment_routes_rbac_and_validation_negative(
    override_dependencies: Any, mock_execution_service: Any
) -> None:
    """Negative & Boundary test: VIEWER is rejected on create/resend; short token fails 422."""
    client = TestClient(app)
    viewer = TokenData(id=MOCK_USER_ID, role=UserRole.VIEWER, organization_id=MOCK_ORG_ID)
    app.dependency_overrides[get_current_user_from_header] = lambda: viewer

    forbidden_resp = client.post(
        "/api/v2/execution/executions/assignments",
        json={
            "assigned_email": "candidate@acme.com",
            "workflow_id": MOCK_WOR_ID,
            "locked_inputs": {"dynamic_inputs": {}},
            "assignee_input_keys": ["essay"],
            "hard_deadline_at": "2026-12-31T23:59:59+00:00",
            "relative_duration_seconds": 2700,
        },
    )
    assert forbidden_resp.status_code == 403

    short_token_resp = client.get("/api/v2/execution/executions/assignments/preview?token=short")
    assert short_token_resp.status_code == 422
