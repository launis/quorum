"""Unit tests for backend_v2/api/routers/studio/steps.py router."""

from collections.abc import Generator
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import (
    get_current_user_from_header,
    get_studio_simulation_service,
    get_studio_workflow_service,
)
from backend_v2.api.routers.studio.steps import router
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.main import app_exception_handler
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.step import Step
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO
from backend_v2.models.dtos.studio import StepSimulationResponse, StepSimulationTraceDTO
from backend_v2.models.enums import StepFilterScope, StepType

app = FastAPI()
app.include_router(router)


@app.exception_handler(AppException)
async def _test_app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return await app_exception_handler(request, exc)


client = TestClient(app)


def mock_get_current_user() -> TokenData:
    return TokenData(id="test_usr", role=UserRole.ROOT, organization_id="root_org")


@pytest.fixture(autouse=True)
def setup_overrides() -> Generator[None]:
    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_studio_services() -> tuple[AsyncMock, AsyncMock]:
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
        name=I18nText(translations={"fi": "Testi", "en": "Test"}),
        description=I18nText(translations={"fi": "Kuvaus", "en": "Description"}),
        type=StepType.LOGIC,
        hook="input_processing_hook",
        is_system_core=False,
    )


def test_router_initialization() -> None:
    """Test that the steps router initializes correctly."""
    assert router is not None
    assert router.prefix == "/steps"


@pytest.mark.asyncio
async def test_get_steps(mock_studio_services: tuple[AsyncMock, AsyncMock], sample_step: Step) -> None:
    """Test GET /steps/ retrieves step list with default specialists scope."""
    mock_workflow, _ = mock_studio_services
    mock_workflow.list_steps.return_value = [sample_step]

    response = client.get("/steps/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == "sp_1234567890abcdef"
    mock_workflow.list_steps.assert_called_once()
    assert mock_workflow.list_steps.call_args.kwargs.get("scope") == StepFilterScope.SPECIALISTS


@pytest.mark.asyncio
async def test_get_steps_scope_specialists(
    mock_studio_services: tuple[AsyncMock, AsyncMock], sample_step: Step
) -> None:
    """Test GET /steps/?scope=specialists passes specialists scope to service."""
    mock_workflow, _ = mock_studio_services
    mock_workflow.list_steps.return_value = [sample_step]

    response = client.get("/steps/?scope=specialists")
    assert response.status_code == 200
    assert len(response.json()) == 1
    mock_workflow.list_steps.assert_called_once()
    assert mock_workflow.list_steps.call_args.kwargs.get("scope") == StepFilterScope.SPECIALISTS


@pytest.mark.asyncio
async def test_get_steps_scope_system_core(
    mock_studio_services: tuple[AsyncMock, AsyncMock], sample_step: Step
) -> None:
    """Test GET /steps/?scope=system_core passes system_core scope to service."""
    mock_workflow, _ = mock_studio_services
    mock_workflow.list_steps.return_value = [sample_step]

    response = client.get("/steps/?scope=system_core")
    assert response.status_code == 200
    assert len(response.json()) == 1
    mock_workflow.list_steps.assert_called_once()
    assert mock_workflow.list_steps.call_args.kwargs.get("scope") == StepFilterScope.SYSTEM_CORE


@pytest.mark.asyncio
async def test_get_steps_scope_all(
    mock_studio_services: tuple[AsyncMock, AsyncMock], sample_step: Step
) -> None:
    """Test GET /steps/?scope=all passes all scope to service."""
    mock_workflow, _ = mock_studio_services
    mock_workflow.list_steps.return_value = [sample_step]

    response = client.get("/steps/?scope=all")
    assert response.status_code == 200
    assert len(response.json()) == 1
    mock_workflow.list_steps.assert_called_once()
    assert mock_workflow.list_steps.call_args.kwargs.get("scope") == StepFilterScope.ALL


@pytest.mark.asyncio
async def test_get_steps_invalid_scope_error(
    mock_studio_services: tuple[AsyncMock, AsyncMock],
) -> None:
    """Test GET /steps/?scope=invalid returns 422 Unprocessable Entity."""
    response = client.get("/steps/?scope=invalid_scope")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_step(mock_studio_services: tuple[AsyncMock, AsyncMock], sample_step: Step) -> None:
    """Test POST /steps/ creates step draft."""
    mock_workflow, _ = mock_studio_services
    mock_workflow.create_step_draft.return_value = sample_step

    response = client.post("/steps/")
    assert response.status_code == 200
    assert response.json()["id"] == "sp_1234567890abcdef"


@pytest.mark.asyncio
async def test_get_step(mock_studio_services: tuple[AsyncMock, AsyncMock], sample_step: Step) -> None:
    """Test GET /steps/{id} retrieves specific step."""
    mock_workflow, _ = mock_studio_services
    mock_workflow.get_step.return_value = sample_step

    response = client.get("/steps/sp_1234567890abcdef")
    assert response.status_code == 200
    assert response.json()["id"] == "sp_1234567890abcdef"


@pytest.mark.asyncio
async def test_save_step(mock_studio_services: tuple[AsyncMock, AsyncMock], sample_step: Step) -> None:
    """Test PUT /steps/{id} saves step configuration."""
    mock_workflow, _ = mock_studio_services
    mock_workflow.save_step.return_value = sample_step

    response = client.put("/steps/sp_1234567890abcdef", json=sample_step.model_dump(mode="json"))
    assert response.status_code == 200
    assert response.json()["id"] == "sp_1234567890abcdef"


@pytest.mark.asyncio
async def test_delete_step(mock_studio_services: tuple[AsyncMock, AsyncMock]) -> None:
    """Test DELETE /steps/{id} deletes step."""
    mock_workflow, _ = mock_studio_services
    mock_workflow.delete_step.return_value = None

    response = client.delete("/steps/sp_1234567890abcdef")
    assert response.status_code == 200
    assert response.json() == {"status": "success", "deleted_id": "sp_1234567890abcdef"}


@pytest.mark.asyncio
async def test_clone_step(mock_studio_services: tuple[AsyncMock, AsyncMock], sample_step: Step) -> None:
    """Test POST /steps/{id}/clone clones step."""
    mock_workflow, _ = mock_studio_services
    mock_workflow.clone_step.return_value = sample_step

    response = client.post("/steps/sp_1234567890abcdef/clone")
    assert response.status_code == 200
    assert response.json()["id"] == "sp_1234567890abcdef"


@pytest.mark.asyncio
async def test_simulate_step(mock_studio_services: tuple[AsyncMock, AsyncMock], sample_step: Step) -> None:
    """Test POST /steps/simulate executes step simulation."""
    _, mock_simulation = mock_studio_services
    sim_response = StepSimulationResponse(
        valid=True,
        errors=[],
        rendered_prompt="Simulated prompt text",
        trace=StepSimulationTraceDTO(execution_time_ms=10.0, estimated_tokens=150),
        prompt_context=None,
    )
    mock_simulation.simulate_step.return_value = sim_response

    payload = {
        "step": sample_step.model_dump(mode="json"),
        "mock_inputs": {"raw_text": "Sample text"},
        "target_locale": "fi",
        "context_text": "Test context document",
    }
    response = client.post("/steps/simulate", json=payload)
    assert response.status_code == 200
    assert response.json()["valid"] is True
    assert response.json()["rendered_prompt"] == "Simulated prompt text"
    assert response.json()["trace"]["estimated_tokens"] == 150
    mock_simulation.simulate_step.assert_awaited_once_with(
        mock_get_current_user(),
        sample_step,
        ExecutionInputsDTO(raw_inputs={"raw_text": "Sample text"}),
        target_locale="fi",
        context_text="Test context document",
    )


@pytest.mark.asyncio
async def test_simulate_step_with_null_context_text_and_locale(
    mock_studio_services: tuple[AsyncMock, AsyncMock], sample_step: Step
) -> None:
    """Regression test: simulate_step should gracefully accept null target_locale and context_text from clients."""
    _, mock_simulation = mock_studio_services
    sim_response = StepSimulationResponse(
        valid=True,
        errors=[],
        rendered_prompt="Simulated prompt text",
        trace=StepSimulationTraceDTO(execution_time_ms=10.0, estimated_tokens=150),
        prompt_context=None,
    )
    mock_simulation.simulate_step.return_value = sim_response

    payload = {
        "step": sample_step.model_dump(mode="json"),
        "mock_inputs": {},
        "target_locale": None,
        "context_text": None,
    }
    response = client.post("/steps/simulate", json=payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    assert response.json()["valid"] is True


@pytest.mark.asyncio
async def test_get_step_not_found_error(mock_studio_services: tuple[AsyncMock, AsyncMock]) -> None:
    """Test GET /steps/{id} returns 404 when step is not found."""
    mock_workflow, _ = mock_studio_services
    mock_workflow.get_step.side_effect = ResourceNotFoundError(resource_type="step", resource_id="sp_missing00000000")

    response = client.get("/steps/sp_missing00000000")
    assert response.status_code == 404
    assert response.json()["extensions"]["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


@pytest.mark.asyncio
async def test_delete_system_core_step_failure(mock_studio_services: tuple[AsyncMock, AsyncMock]) -> None:
    """Test DELETE /steps/{id} returns 403 when attempting to delete system core step."""
    mock_workflow, _ = mock_studio_services
    mock_workflow.delete_step.side_effect = AppException(
        message="Cannot delete protected system core step sp_c4a5a1d15c00438a",
        status_code=403,
        details={"error_code": ErrorCodes.SYSTEM_PROTECTED_RESOURCE.value},
    )

    response = client.delete("/steps/sp_c4a5a1d15c00438a")
    assert response.status_code == 403
    assert response.json()["extensions"]["error_code"] == ErrorCodes.SYSTEM_PROTECTED_RESOURCE.value


@pytest.mark.asyncio
async def test_simulate_step_invalid_input_error(mock_studio_services: tuple[AsyncMock, AsyncMock]) -> None:
    """Test POST /steps/simulate returns 422 for malformed simulation payload."""
    response = client.post("/steps/simulate", json={})
    assert response.status_code == 422
