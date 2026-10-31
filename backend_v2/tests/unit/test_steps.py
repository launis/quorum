"""Unit tests for Step RBAC authorization and router boundaries in Studio endpoints."""

from collections.abc import Generator
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import (
    get_current_user_from_header,
    get_studio_output_profile_service,
    get_studio_prompt_block_service,
    get_studio_simulation_service,
    get_studio_workflow_service,
)
from backend_v2.exceptions import PermissionDeniedError
from backend_v2.main import app
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import I18nText, generate_opaque_id
from backend_v2.models.domain.step import Step
from backend_v2.models.dtos.studio import StepSimulationResponse, StepSimulationTraceDTO
from backend_v2.models.enums import CognitiveTier, EntityPrefix, StepType


def mock_get_current_user_member() -> TokenData:
    """Provides a standard Member user token with restricted mutation permissions."""
    return TokenData(
        email="member@test.com",
        id="usr_user45678",
        role=UserRole.MEMBER,
        organization_id="org_testorg123",
    )


@pytest.fixture
def sample_step() -> Step:
    """Provides a valid Step domain model instance."""
    protocol_block_id = generate_opaque_id(EntityPrefix.PROMPT_BLOCK)
    criteria_block_id = generate_opaque_id(EntityPrefix.PROMPT_BLOCK)
    return Step(
        id=generate_opaque_id(EntityPrefix.STEP),
        slug="sample_step",
        name=I18nText(translations={"en": "Sample Step", "fi": "Esimerkkivaihe"}),
        description=I18nText(translations={"en": "Description", "fi": "Kuvaus"}),
        type=StepType.LLM,
        cognitive_tier=CognitiveTier.FAST,
        role_block_id=None,
        extraction_protocol_block_id=protocol_block_id,
        criteria_block_ids=[criteria_block_id],
        mcp_tool_params={},
    )


@pytest.fixture
def mock_studio_service_manager(sample_step: Step) -> AsyncMock:
    """Provides a mocked Studio service that rejects non-admin step mutations."""
    service = AsyncMock()
    service.list_steps.return_value = [sample_step]
    service.get_step.return_value = sample_step
    service.create_step_draft.side_effect = PermissionDeniedError("Only ADMIN or MANAGER can modify resources.")
    service.save_step.side_effect = PermissionDeniedError("Only ADMIN or MANAGER can modify resources.")
    service.delete_step.side_effect = PermissionDeniedError("Only ADMIN or MANAGER can modify resources.")
    service.clone_step.side_effect = PermissionDeniedError("Only ADMIN or MANAGER can modify resources.")
    service.simulate_step.return_value = StepSimulationResponse(
        valid=True,
        errors=[],
        rendered_prompt="Simulated prompt",
        trace=StepSimulationTraceDTO(execution_time_ms=5.0, estimated_tokens=42),
        prompt_context=None,
    )
    return service


@pytest.fixture
def client_member(mock_studio_service_manager: AsyncMock) -> Generator[TestClient]:
    """Provides a TestClient authenticated as MEMBER."""
    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user_member
    app.dependency_overrides[get_studio_simulation_service] = lambda: mock_studio_service_manager
    app.dependency_overrides[get_studio_workflow_service] = lambda: mock_studio_service_manager
    app.dependency_overrides[get_studio_prompt_block_service] = lambda: mock_studio_service_manager
    app.dependency_overrides[get_studio_output_profile_service] = lambda: mock_studio_service_manager
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_step_rbac_list_and_get_allowed(client_member: TestClient, sample_step: Step) -> None:
    """Verifies that listing and retrieving steps delegates to StudioWorkflowService."""
    list_resp = client_member.get("/api/v2/studio/steps/")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    get_resp = client_member.get(f"/api/v2/studio/steps/{sample_step.id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == sample_step.id


def test_step_rbac_create_and_clone_member_forbidden(client_member: TestClient, sample_step: Step) -> None:
    """Verifies that creating a draft or cloning a step as MEMBER returns 403."""
    create_resp = client_member.post("/api/v2/studio/steps/")
    assert create_resp.status_code == 403

    clone_resp = client_member.post(f"/api/v2/studio/steps/{sample_step.id}/clone")
    assert clone_resp.status_code == 403


def test_step_simulate_endpoint(client_member: TestClient, sample_step: Step) -> None:
    """Verifies that step simulation delegates to StudioSimulationService."""
    payload = {
        "step": sample_step.model_dump(mode="json"),
        "mock_inputs": {"input_text": "Test input"},
        "target_locale": "en",
        "context_text": "Context text",
    }
    sim_resp = client_member.post("/api/v2/studio/steps/simulate", json=payload)
    assert sim_resp.status_code == 200
    assert sim_resp.json()["valid"] is True


def test_step_rbac_save_member_forbidden(client_member: TestClient) -> None:
    """Verifies that MEMBER role is rejected with 403 when attempting to save a step."""
    step_id = generate_opaque_id(EntityPrefix.STEP)
    protocol_block_id = generate_opaque_id(EntityPrefix.PROMPT_BLOCK)
    criteria_block_id = generate_opaque_id(EntityPrefix.PROMPT_BLOCK)
    payload = {
        "id": step_id,
        "name": {"translations": {"en": "new", "fi": "new"}},
        "description": {"translations": {"en": "desc", "fi": "desc"}},
        "type": "llm",
        "cognitive_tier": "fast",
        "role_block_id": None,
        "extraction_protocol_block_id": protocol_block_id,
        "criteria_block_ids": [criteria_block_id],
        "organization_id": "org_testorg123",
        "slug": "new_step",
    }
    response = client_member.put(f"/api/v2/studio/steps/{step_id}", json=payload)
    assert response.status_code == 403
    assert "Permission" in response.json()["detail"] or "ADMIN" in response.json()["detail"]


def test_step_save_id_mismatch_triggers_400(client_member: TestClient, sample_step: Step) -> None:
    """Negative test: Verifies that mismatched path and payload step IDs return 400."""
    other_step_id = generate_opaque_id(EntityPrefix.STEP)
    response = client_member.put(
        f"/api/v2/studio/steps/{other_step_id}",
        json=sample_step.model_dump(mode="json"),
    )
    assert response.status_code == 400


def test_step_rbac_delete_member_forbidden(client_member: TestClient) -> None:
    """Verifies that MEMBER role is rejected with 403 when attempting to delete a step."""
    step_id = generate_opaque_id(EntityPrefix.STEP)
    response = client_member.delete(f"/api/v2/studio/steps/{step_id}")
    assert response.status_code == 403
