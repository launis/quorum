"""Unit tests for backend_v2/api/routers/studio/workflows.py router."""

from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import (
    get_current_user_from_header,
    get_studio_simulation_service,
    get_studio_workflow_service,
)
from backend_v2.api.routers.studio.workflows import router
from backend_v2.models.auth import TokenData
from backend_v2.models.dtos.studio import (
    WorkflowResponseDTO,
    WorkflowSimulationResponse,
)
from backend_v2.models.enums import HistoricalContextMode
from backend_v2.models.v2_core import I18nText, Workflow

app = FastAPI()
app.include_router(router)
client = TestClient(app)


def mock_get_current_user() -> TokenData:
    return TokenData(id="test_usr", role="ROOT", organization_id="root_org")


@pytest.fixture(autouse=True)
def setup_overrides():
    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_studio_services():
    mock_workflow = AsyncMock()
    mock_simulation = AsyncMock()
    app.dependency_overrides[get_studio_workflow_service] = lambda: mock_workflow
    app.dependency_overrides[get_studio_simulation_service] = lambda: mock_simulation
    return mock_workflow, mock_simulation


@pytest.fixture
def sample_workflow() -> Workflow:
    return Workflow(
        id="wor_1234567890abcdef",
        slug="test_wf",
        name=I18nText(translations={"fi": "Testi", "en": "Test"}),
        description=I18nText(translations={"fi": "Kuvaus", "en": "Description"}),
        status="active",
        version=1,
        default_profile_id="prf_1234567890abcdef",
        allowed_exports=[],
        historical_context_mode=HistoricalContextMode.DISABLED,
        expected_inputs=[],
        steps=[],
    )


@pytest.fixture
def sample_workflow_response_dto(sample_workflow: Workflow) -> WorkflowResponseDTO:
    return WorkflowResponseDTO.model_validate(sample_workflow.model_dump(mode="json"))


def test_router_initialization() -> None:
    """Test that the workflows router initializes correctly."""
    assert router is not None
    assert router.prefix == "/workflows"


@pytest.mark.asyncio
async def test_get_workflows(mock_studio_services, sample_workflow_response_dto: WorkflowResponseDTO) -> None:
    mock_workflow, _ = mock_studio_services
    mock_workflow.list_workflows.return_value = [sample_workflow_response_dto]

    response = client.get("/workflows/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == "wor_1234567890abcdef"


@pytest.mark.asyncio
async def test_create_workflow(mock_studio_services, sample_workflow_response_dto: WorkflowResponseDTO) -> None:
    mock_workflow, _ = mock_studio_services
    mock_workflow.create_workflow_draft.return_value = sample_workflow_response_dto

    response = client.post("/workflows/")
    assert response.status_code == 200
    assert response.json()["id"] == "wor_1234567890abcdef"


@pytest.mark.asyncio
async def test_get_workflow(mock_studio_services, sample_workflow_response_dto: WorkflowResponseDTO) -> None:
    mock_workflow, _ = mock_studio_services
    mock_workflow.get_workflow.return_value = sample_workflow_response_dto

    response = client.get("/workflows/wor_1234567890abcdef")
    assert response.status_code == 200
    assert response.json()["id"] == "wor_1234567890abcdef"


@pytest.mark.asyncio
async def test_simulate_workflow(mock_studio_services, sample_workflow: Workflow) -> None:
    _, mock_simulation = mock_studio_services
    sim_response = WorkflowSimulationResponse(
        valid=True,
        errors=[],
        step_status={},
        execution_order=[],
        trace={},
    )
    mock_simulation.simulate_workflow.return_value = sim_response

    response = client.post("/workflows/simulate", json=sample_workflow.model_dump(mode="json"))
    assert response.status_code == 200
    assert response.json()["valid"] is True


@pytest.mark.asyncio
async def test_get_workflow_available_extensions(mock_studio_services) -> None:
    mock_workflow, _ = mock_studio_services
    mock_workflow.get_workflow_available_extensions.return_value = ["ext_1", "ext_2"]

    response = client.get("/workflows/wor_1234567890abcdef/available-extensions")
    assert response.status_code == 200
    assert response.json()["available_extensions"] == ["ext_1", "ext_2"]


@pytest.mark.asyncio
async def test_clone_workflow(mock_studio_services, sample_workflow_response_dto: WorkflowResponseDTO) -> None:
    mock_workflow, _ = mock_studio_services
    mock_workflow.clone_workflow.return_value = sample_workflow_response_dto

    response = client.post("/workflows/wor_1234567890abcdef/clone")
    assert response.status_code == 200
    assert response.json()["id"] == "wor_1234567890abcdef"


@pytest.mark.asyncio
async def test_save_workflow(
    mock_studio_services, sample_workflow: Workflow, sample_workflow_response_dto: WorkflowResponseDTO
) -> None:
    mock_workflow, _ = mock_studio_services
    mock_workflow.save_workflow.return_value = sample_workflow_response_dto

    response = client.put("/workflows/wor_1234567890abcdef", json=sample_workflow.model_dump(mode="json"))
    assert response.status_code == 200
    assert response.json()["id"] == "wor_1234567890abcdef"


@pytest.mark.asyncio
async def test_delete_workflow(mock_studio_services) -> None:
    mock_workflow, _ = mock_studio_services
    mock_workflow.delete_workflow.return_value = None

    response = client.delete("/workflows/wor_1234567890abcdef")
    assert response.status_code == 200
    assert response.json() == {"status": "success", "deleted_id": "wor_1234567890abcdef"}
