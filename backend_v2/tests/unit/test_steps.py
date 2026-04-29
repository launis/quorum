from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import get_current_user_from_header, get_studio_service
from backend_v2.exceptions import PermissionDeniedError
from backend_v2.main import app
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.services.studio import StudioService


def mock_get_current_user_member() -> Any:
    return TokenData(
        email="member@test.com", id="usr_user45678", role=UserRole.MEMBER, organization_id="org_testorg123"
    )


@pytest.fixture
def mock_studio_service_manager() -> Any:
    service = AsyncMock(spec=StudioService)
    # Configure mock responses for failing non-root mutations
    service.save_step.side_effect = PermissionDeniedError("Only ADMIN or MANAGER can modify resources.")
    service.delete_step.side_effect = PermissionDeniedError("Only ADMIN or MANAGER can modify resources.")
    return service


@pytest.fixture
def client_member(mock_studio_service_manager: Any) -> Any:
    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user_member
    app.dependency_overrides[get_studio_service] = lambda: mock_studio_service_manager
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_step_rbac_save_member_forbidden(client_member: Any) -> None:
    payload = {
        "id": "step_2222222222222222",
        "name": {"default_locale": "en", "translations": {"en": "new"}},
        "description": {"default_locale": "en", "translations": {"en": "desc"}},
        "type": "llm",
        "model_strategy": "fast",
        "prompt_blocks": ["blk_1111111111111111"],
        "organization_id": "org_testorg123",
        "slug": "new_step",
    }
    response = client_member.put("/api/v2/studio/steps/step_2222222222222222", json=payload)
    if response.status_code == 404:
        response = client_member.put("/studio/steps/step_2222222222222222", json=payload)

    assert response.status_code == 403
    assert "Permission" in response.json()["detail"] or "ADMIN" in response.json()["detail"]


def test_step_rbac_delete_member_forbidden(client_member: Any) -> None:
    response = client_member.delete("/api/v2/studio/steps/step_someid123")
    if response.status_code == 404:
        response = client_member.delete("/studio/steps/step_someid123")

    assert response.status_code == 403
