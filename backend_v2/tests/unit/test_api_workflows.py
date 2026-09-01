"""Unit and RBAC integration tests for Admin Studio Workflows API endpoints."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import (
    get_current_user_from_header,
    get_studio_output_profile_service,
    get_studio_prompt_block_service,
    get_studio_simulation_service,
    get_studio_workflow_service,
)
from backend_v2.main import app
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.services.studio.prompt_block_service import StudioPromptBlockService
from backend_v2.services.studio.workflow_service import StudioWorkflowService
from backend_v2.tests.factories import WorkflowFactory
from backend_v2.tests.fakes.in_memory_repositories import InMemoryWorkflowRepository


def get_member_user() -> TokenData:
    """Provides a standard Member user token with restricted mutation permissions."""
    return TokenData(
        email="member@test.com",
        id="usr_user45678",
        role=UserRole.MEMBER,
        organization_id="org_testorg123",
    )


def get_root_user() -> TokenData:
    """Provides a Root superuser token with full administrative permissions."""
    return TokenData(
        email="root@test.com",
        id="usr_user99900",
        role=UserRole.ROOT,
        organization_id="org_testorg123",
    )


@pytest.fixture
def client_member(
    studio_workflow_service: StudioWorkflowService,
    studio_prompt_block_service: StudioPromptBlockService,
) -> Generator[TestClient]:
    """TestClient authenticated as a MEMBER user with real services backed by in-memory fakes."""
    app.dependency_overrides[get_current_user_from_header] = get_member_user
    app.dependency_overrides[get_studio_workflow_service] = lambda: studio_workflow_service
    app.dependency_overrides[get_studio_simulation_service] = lambda: studio_workflow_service
    app.dependency_overrides[get_studio_prompt_block_service] = lambda: studio_prompt_block_service
    app.dependency_overrides[get_studio_output_profile_service] = lambda: studio_workflow_service
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def client_root(
    studio_workflow_service: StudioWorkflowService,
    studio_prompt_block_service: StudioPromptBlockService,
) -> Generator[TestClient]:
    """TestClient authenticated as a ROOT user with real services backed by in-memory fakes."""
    app.dependency_overrides[get_current_user_from_header] = get_root_user
    app.dependency_overrides[get_studio_workflow_service] = lambda: studio_workflow_service
    app.dependency_overrides[get_studio_simulation_service] = lambda: studio_workflow_service
    app.dependency_overrides[get_studio_prompt_block_service] = lambda: studio_prompt_block_service
    app.dependency_overrides[get_studio_output_profile_service] = lambda: studio_workflow_service
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_workflow_rbac_save_member_forbidden(client_member: TestClient) -> None:
    """Verifies that MEMBER role is rejected with 403 when attempting to save a workflow."""
    workflow = WorkflowFactory.build(organization_id="org_testorg123")
    payload = workflow.model_dump(mode="json")
    response = client_member.put(f"/api/v2/studio/workflows/{workflow.id}", json=payload)

    assert response.status_code == 403
    detail = response.json()["detail"]
    assert "Only ADMIN or MANAGER" in detail or "Permission" in detail or "Forbidden" in detail


def test_workflow_rbac_delete_member_forbidden(
    client_member: TestClient, fake_workflow_repo: InMemoryWorkflowRepository
) -> None:
    """Verifies that MEMBER role is rejected with 403 when attempting to delete an existing workflow."""
    workflow = WorkflowFactory.build(organization_id="org_testorg123")
    fake_workflow_repo._save_isolated(workflow.id, workflow)

    response = client_member.delete(f"/api/v2/studio/workflows/{workflow.id}")

    assert response.status_code == 403
    detail = response.json()["detail"]
    assert "Only ADMIN or MANAGER" in detail or "Permission" in detail or "Forbidden" in detail


def test_workflow_save_malformed_json_triggers_422(client_member: TestClient) -> None:
    """Negative test: Verifies that invalid/malformed JSON body fails with 422 Unprocessable Entity."""
    response = client_member.put("/api/v2/studio/workflows/wf_1234567890abcdef", json={"invalid": "payload"})
    assert response.status_code == 422


def test_workflow_get_nonexistent_triggers_404(client_root: TestClient) -> None:
    """Negative test: Verifies that requesting a non-existent workflow returns 404 Not Found."""
    response = client_root.get("/api/v2/studio/workflows/wf_nonexistent000000")
    assert response.status_code == 404


def test_workflow_delete_nonexistent_triggers_404(client_root: TestClient) -> None:
    """Negative test: Verifies that deleting a non-existent workflow returns 404 Not Found."""
    response = client_root.delete("/api/v2/studio/workflows/wf_nonexistent000000")
    assert response.status_code == 404
