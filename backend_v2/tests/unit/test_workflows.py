from typing import Any
from unittest.mock import AsyncMock, patch

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
from backend_v2.models.auth import TokenData, UserRole

# Mock setup_logging to avoid litellm crash on Pydantic V2 during tests
patch("backend_v2.main.setup_logging").start()
from backend_v2.main import app


def mock_get_current_user_member() -> Any:
    return TokenData(
        email="member@test.com", id="usr_user45678", role=UserRole.MEMBER, organization_id="org_testorg123"
    )


def mock_get_current_user_root() -> Any:
    return TokenData(email="root@test.com", id="usr_user99900", role=UserRole.ROOT, organization_id="org_testorg123")


@pytest.fixture
def mock_studio_service_manager() -> Any:
    service = AsyncMock()
    # Configure mock responses for failing non-root mutations
    service.save_workflow.side_effect = PermissionDeniedError("Only ADMIN or MANAGER can modify resources.")
    service.delete_workflow.side_effect = PermissionDeniedError("Only ADMIN or MANAGER can modify resources.")
    return service


@pytest.fixture
def client_member(mock_studio_service_manager: Any) -> Any:
    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user_member
    app.dependency_overrides[get_studio_simulation_service] = lambda: mock_studio_service_manager
    app.dependency_overrides[get_studio_workflow_service] = lambda: mock_studio_service_manager
    app.dependency_overrides[get_studio_prompt_block_service] = lambda: mock_studio_service_manager
    app.dependency_overrides[get_studio_output_profile_service] = lambda: mock_studio_service_manager
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_workflow_rbac_save_member_forbidden(client_member: Any) -> None:
    payload = {
        "id": "wf_2222222222222222",
        "name": {"translations": {"en": "new", "fi": "new"}},
        "description": {"translations": {"en": "desc", "fi": "desc"}},
        "status": "draft",
        "version": 1,
        "default_profile_id": "prof_mmmm1111mmmm1111",
        "allowed_exports": ["pdf"],
        "historical_context_mode": "DISABLED",
        "organization_id": "org_testorg123",
        "slug": "new_wf",
    }
    response = client_member.put("/api/v2/studio/workflows/wf_2222222222222222", json=payload)
    if response.status_code == 404:
        response = client_member.put("/studio/workflows/wf_2222222222222222", json=payload)

    assert response.status_code == 403
    assert "Permission" in response.json()["detail"] or "ADMIN" in response.json()["detail"]


def test_workflow_rbac_delete_member_forbidden(client_member: Any) -> None:
    response = client_member.delete("/api/v2/studio/workflows/wf_someid123")
    if response.status_code == 404:
        response = client_member.delete("/studio/workflows/wf_someid123")

    assert response.status_code == 403
