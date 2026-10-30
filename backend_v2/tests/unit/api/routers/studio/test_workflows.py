"""Unit tests for backend_v2/api/routers/studio/workflows.py router."""

from collections.abc import Generator
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import (
    get_current_user_from_header,
    get_execution_service,
    get_studio_simulation_service,
    get_studio_workflow_service,
)
from backend_v2.api.routers.studio.workflows import (
    delete_workflow,
    get_workflow,
    router,
)
from backend_v2.exceptions import AppException, ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.main import app_exception_handler
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.step import ExpectedInput
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.studio import (
    StepSimulationTraceDTO,
    WorkflowResponseDTO,
    WorkflowSimulationResponse,
)
from backend_v2.models.dtos.workflow_schema import WorkflowSchemaResponseDTO
from backend_v2.models.enums import HistoricalContextMode

app = FastAPI()
app.include_router(router)


@app.exception_handler(AppException)
async def _test_app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return await app_exception_handler(request, exc)


client = TestClient(app)


def mock_get_current_user() -> TokenData:
    """Provide a root TokenData fixture for router tests."""
    return TokenData(id="test_usr", role=UserRole.ROOT, organization_id="root_org")


@pytest.fixture(autouse=True)
def setup_overrides() -> Generator[None]:
    """Configure FastAPI dependency overrides for authentication."""
    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_studio_services() -> tuple[AsyncMock, AsyncMock]:
    """Provide mocked workflow and simulation service dependencies."""
    mock_workflow = AsyncMock()
    mock_simulation = AsyncMock()
    app.dependency_overrides[get_studio_workflow_service] = lambda: mock_workflow
    app.dependency_overrides[get_studio_simulation_service] = lambda: mock_simulation
    return mock_workflow, mock_simulation


@pytest.fixture
def mock_execution_service() -> AsyncMock:
    """Provide mocked execution service dependency."""
    mock_execution = AsyncMock()
    app.dependency_overrides[get_execution_service] = lambda: mock_execution
    return mock_execution


@pytest.fixture
def sample_workflow() -> Workflow:
    """Create a valid sample Workflow domain model."""
    return Workflow(
        id="wor_0195f3a0000070018234567890abcdef",
        slug="test_wf",
        name=I18nText(translations={"fi": "Testi", "en": "Test"}),
        description=I18nText(translations={"fi": "Kuvaus", "en": "Description"}),
        status="active",
        version=1,
        default_profile_id="prf_0195f3a0000070018234567890abcdef",
        historical_context_mode=HistoricalContextMode.DISABLED,
        model_registry_id="sys_0195f3a00000700e826807f3bfa3454d",
        expected_inputs=[],
        steps=[],
    )


@pytest.fixture
def sample_workflow_response_dto(sample_workflow: Workflow) -> WorkflowResponseDTO:
    """Create a valid sample WorkflowResponseDTO."""
    return WorkflowResponseDTO.model_validate(sample_workflow.model_dump(mode="json"))


def test_router_initialization() -> None:
    """Test that the workflows router initializes correctly."""
    assert router is not None
    assert router.prefix == "/workflows"


@pytest.mark.asyncio
async def test_get_workflows(
    mock_studio_services: tuple[AsyncMock, AsyncMock], sample_workflow_response_dto: WorkflowResponseDTO
) -> None:
    """Test GET /workflows/ retrieves all accessible workflow definitions."""
    mock_workflow, _ = mock_studio_services
    mock_workflow.list_workflows.return_value = [sample_workflow_response_dto]

    response = client.get("/workflows/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == "wor_0195f3a0000070018234567890abcdef"


@pytest.mark.asyncio
async def test_create_workflow(
    mock_studio_services: tuple[AsyncMock, AsyncMock], sample_workflow_response_dto: WorkflowResponseDTO
) -> None:
    """Test POST /workflows/ creates a new workflow draft."""
    mock_workflow, _ = mock_studio_services
    mock_workflow.create_workflow_draft.return_value = sample_workflow_response_dto

    response = client.post("/workflows/")
    assert response.status_code == 200
    assert response.json()["id"] == "wor_0195f3a0000070018234567890abcdef"


@pytest.mark.asyncio
async def test_get_workflow(
    mock_studio_services: tuple[AsyncMock, AsyncMock], sample_workflow_response_dto: WorkflowResponseDTO
) -> None:
    """Test GET /workflows/{id} retrieves a specific workflow by ID."""
    mock_workflow, _ = mock_studio_services
    mock_workflow.get_workflow.return_value = sample_workflow_response_dto

    response = client.get("/workflows/wor_0195f3a0000070018234567890abcdef")
    assert response.status_code == 200
    assert response.json()["id"] == "wor_0195f3a0000070018234567890abcdef"


@pytest.mark.asyncio
async def test_simulate_workflow(mock_studio_services: tuple[AsyncMock, AsyncMock], sample_workflow: Workflow) -> None:
    """Test POST /workflows/simulate validates workflow DAG topology."""
    _, mock_simulation = mock_studio_services
    sim_response = WorkflowSimulationResponse(
        valid=True,
        errors=[],
        step_status={},
        execution_order=[],
        trace=StepSimulationTraceDTO(),
    )
    mock_simulation.simulate_workflow.return_value = sim_response

    response = client.post("/workflows/simulate", json=sample_workflow.model_dump(mode="json"))
    assert response.status_code == 200
    assert response.json()["valid"] is True


@pytest.mark.asyncio
async def test_get_workflow_available_extensions(mock_studio_services: tuple[AsyncMock, AsyncMock]) -> None:
    """Test GET /workflows/{id}/available-extensions returns matrix extensions."""
    mock_workflow, _ = mock_studio_services
    mock_workflow.get_workflow_available_extensions.return_value = ["ext_1", "ext_2"]

    response = client.get("/workflows/wor_0195f3a0000070018234567890abcdef/available-extensions")
    assert response.status_code == 200
    assert response.json()["available_extensions"] == ["ext_1", "ext_2"]


@pytest.mark.asyncio
async def test_clone_workflow(
    mock_studio_services: tuple[AsyncMock, AsyncMock], sample_workflow_response_dto: WorkflowResponseDTO
) -> None:
    """Test POST /workflows/{id}/clone clones an existing workflow."""
    mock_workflow, _ = mock_studio_services
    mock_workflow.clone_workflow.return_value = sample_workflow_response_dto

    response = client.post("/workflows/wor_0195f3a0000070018234567890abcdef/clone")
    assert response.status_code == 200
    assert response.json()["id"] == "wor_0195f3a0000070018234567890abcdef"


@pytest.mark.asyncio
async def test_save_workflow(
    mock_studio_services: tuple[AsyncMock, AsyncMock],
    sample_workflow: Workflow,
    sample_workflow_response_dto: WorkflowResponseDTO,
) -> None:
    """Test PUT /workflows/{id} saves a workflow configuration."""
    mock_workflow, _ = mock_studio_services
    mock_workflow.save_workflow.return_value = sample_workflow_response_dto

    response = client.put(
        "/workflows/wor_0195f3a0000070018234567890abcdef", json=sample_workflow.model_dump(mode="json")
    )
    assert response.status_code == 200
    assert response.json()["id"] == "wor_0195f3a0000070018234567890abcdef"


@pytest.mark.asyncio
async def test_delete_workflow(mock_studio_services: tuple[AsyncMock, AsyncMock]) -> None:
    """Test DELETE /workflows/{id} deletes a workflow."""
    mock_workflow, _ = mock_studio_services
    mock_workflow.delete_workflow.return_value = None

    response = client.delete("/workflows/wor_0195f3a0000070018234567890abcdef")
    assert response.status_code == 200
    assert response.json() == {"status": "success", "deleted_id": "wor_0195f3a0000070018234567890abcdef"}


@pytest.mark.asyncio
async def test_get_workflow_not_found_raises_app_exception(
    mock_studio_services: tuple[AsyncMock, AsyncMock],
) -> None:
    """Negative test: get_workflow propagates ResourceNotFoundError (AppException) on missing ID."""
    mock_workflow, _ = mock_studio_services
    missing_id = "wor_0195f3a0000070018000000000000000"
    mock_workflow.get_workflow.side_effect = ResourceNotFoundError(
        resource_type="workflow", resource_id=missing_id
    )

    with pytest.raises(AppException) as exc_info:
        await get_workflow(
            id=missing_id,
            current_user=mock_get_current_user(),
            studio_workflow_service=mock_workflow,
        )
    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value

    response = client.get(f"/workflows/{missing_id}")
    assert response.status_code == 404
    assert response.json()["extensions"]["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


@pytest.mark.asyncio
async def test_delete_workflow_permission_denied_raises_app_exception(
    mock_studio_services: tuple[AsyncMock, AsyncMock],
) -> None:
    """Negative test: delete_workflow propagates PermissionDeniedError (AppException) on unauthorized access."""
    mock_workflow, _ = mock_studio_services
    mock_workflow.delete_workflow.side_effect = PermissionDeniedError(
        message="Permission denied to delete workflow wor_0195f3a0000070018234567890abcdef"
    )

    with pytest.raises(AppException) as exc_info:
        await delete_workflow(
            id="wor_0195f3a0000070018234567890abcdef",
            current_user=mock_get_current_user(),
            studio_workflow_service=mock_workflow,
        )
    assert exc_info.value.status_code == 403
    assert exc_info.value.details["error_code"] == ErrorCodes.PERMISSION_DENIED.value

    response = client.delete("/workflows/wor_0195f3a0000070018234567890abcdef")
    assert response.status_code == 403
    assert response.json()["extensions"]["error_code"] == ErrorCodes.PERMISSION_DENIED.value


@pytest.mark.asyncio
async def test_simulate_workflow_invalid_payload_boundary(
    mock_studio_services: tuple[AsyncMock, AsyncMock],
) -> None:
    """Negative boundary test: POST /workflows/simulate rejects empty or malformed workflow payload with 422."""
    response = client.post("/workflows/simulate", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_workflow_ui_schema(
    mock_execution_service: AsyncMock,
) -> None:
    """Test GET /workflows/{id}/ui_schema returns WorkflowSchemaResponseDTO."""
    schema_dto = WorkflowSchemaResponseDTO(
        expected_inputs=[
            ExpectedInput(
                input_key="chat_log",
                label=I18nText(translations={"en": "Chat Log", "fi": "Keskusteluloki"}),
                description=I18nText(translations={"en": "Chat Log description", "fi": "Keskusteluloki kuvaus"}),
                input_modes=["text"],
                required=True,
            )
        ],
    )
    mock_execution_service.get_workflow_ui_schema.return_value = schema_dto

    response = client.get("/workflows/wor_0195f3a0000070018234567890abcdef/ui_schema")
    assert response.status_code == 200
    assert len(response.json()["expected_inputs"]) == 1
    assert response.json()["expected_inputs"][0]["input_key"] == "chat_log"


def test_get_workflow_invalid_id_returns_422() -> None:
    """Negative test: GET /workflows/{id} with non-opaque ID returns 422."""
    response = client.get("/workflows/invalid-id")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_save_workflow_id_mismatch_returns_400(
    mock_studio_services: tuple[AsyncMock, AsyncMock],
    sample_workflow: Workflow,
) -> None:
    """Negative test: PUT /workflows/{id} with mismatched payload ID returns 400 ID_MISMATCH."""
    response = client.put(
        "/workflows/wor_0195f3a0000070018000000000000099",
        json=sample_workflow.model_dump(mode="json"),
    )
    assert response.status_code == 400
    assert response.json()["extensions"]["error_code"] == ErrorCodes.ID_MISMATCH.value
