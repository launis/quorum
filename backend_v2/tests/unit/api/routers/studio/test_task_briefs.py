"""Unit tests for backend_v2/api/routers/studio/task_briefs.py router."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import (
    get_current_user_from_header,
    get_studio_task_brief_service,
)
from backend_v2.api.routers.studio.task_briefs import router
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.main import app_exception_handler
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import I18nText, generate_opaque_id
from backend_v2.models.domain.task_brief import TaskBrief
from backend_v2.models.enums import EntityPrefix
from backend_v2.services.studio.task_brief_service import StudioTaskBriefService
from backend_v2.tests.factories.model_factories import TaskBriefFactory
from backend_v2.tests.fakes.in_memory_repositories import InMemoryTaskBriefRepository

app = FastAPI()
app.include_router(router)


@app.exception_handler(AppException)
async def _test_app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle AppException instances using the production RFC 7807 handler."""
    return await app_exception_handler(request, exc)


client = TestClient(app)

ORG_ALPHA_ID = "org_0195f3a0000070018234567890abcdef"


def mock_get_current_user() -> TokenData:
    """Return an admin TokenData fixture for router authentication."""
    return TokenData(
        id="usr_0195f3a0000070018234567890abcdef",
        role=UserRole.ADMIN,
        organization_id=ORG_ALPHA_ID,
    )


@pytest.fixture
def task_brief_repo() -> InMemoryTaskBriefRepository:
    """Provide an in-memory task brief repository for router tests."""
    return InMemoryTaskBriefRepository()


@pytest.fixture(autouse=True)
def setup_overrides(task_brief_repo: InMemoryTaskBriefRepository) -> Generator[None]:
    """Configure and clean up FastAPI dependency overrides for each test."""
    service = StudioTaskBriefService(
        task_brief_repo=task_brief_repo,
    )
    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user
    app.dependency_overrides[get_studio_task_brief_service] = lambda: service
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def sample_brief() -> TaskBrief:
    """Provide a valid TaskBrief instance."""
    return TaskBriefFactory.build(
        id="tbr_0195f3a00000700d8a1b2c3d4e5f6001",
        slug="alpha_task_brief",
        organization_id=ORG_ALPHA_ID,
        label=I18nText(translations={"en": "Alpha Task Brief", "fi": "Alpha-tehtävänanto"}),
        description=I18nText(translations={"en": "Brief description", "fi": "Kuvaus"}),
        instruction_text="Evaluate the strategic dilemma and provide a structured recommendation.",
        source_url="https://docs.qrum.ai/cases/alpha",
    )


def test_router_initialization() -> None:
    """Verify that the task briefs router initializes with expected prefix."""
    assert router.prefix == "/task-briefs"


def test_crud_and_clone_task_brief_routes(sample_brief: TaskBrief) -> None:
    """Test POST /, GET /, GET /{id}, PUT /{id}, POST /{id}/clone, and DELETE /{id}."""
    # 1. Create draft (POST /task-briefs/)
    create_resp = client.post("/task-briefs/")
    assert create_resp.status_code == 201
    draft_data = create_resp.json()
    draft_id = draft_data["id"]
    assert draft_id.startswith("tbr_")
    assert draft_data["organization_id"] == ORG_ALPHA_ID

    # 2. Save updated brief (PUT /task-briefs/{id})
    updated_payload = sample_brief.model_copy(update={"id": draft_id}).model_dump(mode="json")
    save_resp = client.put(f"/task-briefs/{draft_id}", json=updated_payload)
    assert save_resp.status_code == 200
    assert save_resp.json()["label"]["translations"]["en"] == "Alpha Task Brief"
    assert save_resp.json()["source_url"] == "https://docs.qrum.ai/cases/alpha"

    # 3. Get single brief (GET /task-briefs/{id})
    get_resp = client.get(f"/task-briefs/{draft_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == draft_id

    # 4. Clone brief (POST /task-briefs/{id}/clone)
    clone_resp = client.post(f"/task-briefs/{draft_id}/clone")
    assert clone_resp.status_code == 201
    cloned_id = clone_resp.json()["id"]
    assert cloned_id != draft_id
    assert clone_resp.json()["label"]["translations"]["en"] == "Alpha Task Brief (Copy)"

    # 5. List briefs (GET /task-briefs/)
    list_resp = client.get("/task-briefs/")
    assert list_resp.status_code == 200
    assert {item["id"] for item in list_resp.json()} == {draft_id, cloned_id}

    # 6. Delete brief (DELETE /task-briefs/{id})
    del_resp = client.delete(f"/task-briefs/{cloned_id}")
    assert del_resp.status_code == 200
    assert del_resp.json() == {"status": "deleted", "deleted_id": cloned_id}


def test_put_task_brief_id_mismatch_error(sample_brief: TaskBrief) -> None:
    """Verify PUT /task-briefs/{id} rejects payload with mismatched ID (ErrorCodes.ID_MISMATCH)."""
    other_id = generate_opaque_id(EntityPrefix.TASK_BRIEF)
    resp = client.put(
        f"/task-briefs/{other_id}",
        json=sample_brief.model_dump(mode="json"),
    )
    assert resp.status_code == 400
    assert resp.json()["extensions"]["error_code"] == ErrorCodes.ID_MISMATCH.value


def test_get_task_brief_not_found_and_invalid_path_pattern_error() -> None:
    """Verify GET /task-briefs/{id} returns 404 on missing ID and 422 on malformed path ID."""
    missing_id = generate_opaque_id(EntityPrefix.TASK_BRIEF)
    not_found_resp = client.get(f"/task-briefs/{missing_id}")
    assert not_found_resp.status_code == 404
    assert not_found_resp.json()["extensions"]["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value

    malformed_resp = client.get("/task-briefs/not-an-opaque-id")
    assert malformed_resp.status_code == 422
