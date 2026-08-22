"""Unit tests for backend_v2/api/routers/studio/steps.py router."""

from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import (
    get_current_user_from_header,
    get_studio_simulation_service,
    get_studio_workflow_service,
)
from backend_v2.api.routers.studio.steps import router
from backend_v2.models.auth import TokenData
from backend_v2.models.dtos.studio import StepSimulationResponse
from backend_v2.models.v2_core import I18nText, Step

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
def sample_step() -> Step:
    return Step(
        id="sp_1234567890abcdef",
        slug="test_step",
        name=I18nText(default_locale="fi", translations={"fi": "Testi", "en": "Test"}),
        description=I18nText(default_locale="fi", translations={"fi": "Kuvaus", "en": "Description"}),
        type="logic",
        hook="input_processing_hook",
        is_system_core=False,
    )


def test_router_initialization() -> None:
    """Test that the steps router initializes correctly."""
    assert router is not None
    assert router.prefix == "/steps"


@pytest.mark.asyncio
async def test_get_steps(mock_studio_services, sample_step: Step) -> None:
    """Test GET /steps/ retrieves step list."""
    mock_workflow, _ = mock_studio_services
    mock_workflow.list_steps.return_value = [sample_step]

    response = client.get("/steps/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == "sp_1234567890abcdef"


@pytest.mark.asyncio
async def test_create_step(mock_studio_services, sample_step: Step) -> None:
    """Test POST /steps/ creates step draft."""
    mock_workflow, _ = mock_studio_services
    mock_workflow.create_step_draft.return_value = sample_step

    response = client.post("/steps/")
    assert response.status_code == 200
    assert response.json()["id"] == "sp_1234567890abcdef"


@pytest.mark.asyncio
async def test_get_step(mock_studio_services, sample_step: Step) -> None:
    """Test GET /steps/{id} retrieves specific step."""
    mock_workflow, _ = mock_studio_services
    mock_workflow.get_step.return_value = sample_step

    response = client.get("/steps/sp_1234567890abcdef")
    assert response.status_code == 200
    assert response.json()["id"] == "sp_1234567890abcdef"


@pytest.mark.asyncio
async def test_save_step(mock_studio_services, sample_step: Step) -> None:
    """Test PUT /steps/{id} saves step configuration."""
    mock_workflow, _ = mock_studio_services
    mock_workflow.save_step.return_value = sample_step

    response = client.put("/steps/sp_1234567890abcdef", json=sample_step.model_dump(mode="json"))
    assert response.status_code == 200
    assert response.json()["id"] == "sp_1234567890abcdef"


@pytest.mark.asyncio
async def test_delete_step(mock_studio_services) -> None:
    """Test DELETE /steps/{id} deletes step."""
    mock_workflow, _ = mock_studio_services
    mock_workflow.delete_step.return_value = None

    response = client.delete("/steps/sp_1234567890abcdef")
    assert response.status_code == 200
    assert response.json() == {"status": "success", "deleted_id": "sp_1234567890abcdef"}


@pytest.mark.asyncio
async def test_clone_step(mock_studio_services, sample_step: Step) -> None:
    """Test POST /steps/{id}/clone clones step."""
    mock_workflow, _ = mock_studio_services
    mock_workflow.clone_step.return_value = sample_step

    response = client.post("/steps/sp_1234567890abcdef/clone")
    assert response.status_code == 200
    assert response.json()["id"] == "sp_1234567890abcdef"


@pytest.mark.asyncio
async def test_simulate_step(mock_studio_services, sample_step: Step) -> None:
    """Test POST /steps/simulate executes step simulation."""
    _, mock_simulation = mock_studio_services
    sim_response = StepSimulationResponse(
        valid=True,
        errors=[],
        rendered_prompt="Simulated prompt text",
        trace={"tokens": 150},
        prompt_context=None,
    )
    mock_simulation.simulate_step.return_value = sim_response

    payload = {
        "step": sample_step.model_dump(mode="json"),
        "mock_inputs": {"raw_text": "Sample text"},
    }
    response = client.post("/steps/simulate", json=payload)
    assert response.status_code == 200
    assert response.json()["valid"] is True
    assert response.json()["rendered_prompt"] == "Simulated prompt text"
