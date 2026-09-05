from unittest.mock import AsyncMock

import pytest

# Create a FastAPI app to mount the router
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend_v2.api.routers.studio.output_profiles import router as api_router
from backend_v2.models.auth import TokenData
from backend_v2.models.domain.output_profile import OutputProfile

app = FastAPI()
app.include_router(api_router)
client = TestClient(app)

from backend_v2.api.dependencies import (
    get_current_user_from_header,
    get_studio_output_profile_service,
    get_studio_prompt_block_service,
    get_studio_simulation_service,
    get_studio_workflow_service,
)


def mock_get_current_user():
    return TokenData(id="test", role="ROOT", organization_id="root_org")


@pytest.fixture(autouse=True)
def setup_overrides():
    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_studio_service():
    mock_service = AsyncMock()
    app.dependency_overrides[get_studio_simulation_service] = lambda: mock_service
    app.dependency_overrides[get_studio_workflow_service] = lambda: mock_service
    app.dependency_overrides[get_studio_prompt_block_service] = lambda: mock_service
    app.dependency_overrides[get_studio_output_profile_service] = lambda: mock_service
    return mock_service


@pytest.mark.asyncio
async def test_list_output_profiles(mock_studio_service):
    mock_studio_service.list_output_profiles.return_value = []
    response = client.get("/profiles")
    assert response.status_code == 200
    assert response.json() == {"items": []}


@pytest.mark.asyncio
async def test_create_output_profile_draft(mock_studio_service):
    mock_profile = OutputProfile(
        id="prof_0123456789abcdef0123456789abcdef",
        workflow_id="*",
        slug="test-draft",
        name={"translations": {"en": "test"}},
        organization_id="root",
        matrix_synthesis_groups=[
            {
                "id": "grp_1234567890123456",
                "title": {"translations": {"en": "test"}},
                "target_blocks": ["*"],
            }
        ],
    )
    mock_studio_service.create_output_profile_draft.return_value = mock_profile
    response = client.post("/profiles/draft")
    assert response.status_code == 201
    assert response.json()["id"] == "prof_0123456789abcdef0123456789abcdef"


@pytest.mark.asyncio
async def test_get_output_profile(mock_studio_service):
    mock_profile = OutputProfile(
        id="prof_0123456789abcdef0123456789abcdef",
        workflow_id="*",
        slug="test-profile",
        name={"translations": {"en": "test"}},
        organization_id="root",
        matrix_synthesis_groups=[
            {
                "id": "grp_1234567890123456",
                "title": {"translations": {"en": "test"}},
                "target_blocks": ["*"],
            }
        ],
    )
    mock_studio_service.get_output_profile.return_value = mock_profile
    response = client.get("/profiles/prof_0123456789abcdef0123456789abcdef")
    assert response.status_code == 200
    assert response.json()["id"] == "prof_0123456789abcdef0123456789abcdef"


@pytest.mark.asyncio
async def test_save_output_profile(mock_studio_service):
    mock_profile = OutputProfile(
        id="prof_0123456789abcdef0123456789abcdef",
        workflow_id="*",
        slug="test-profile",
        name={"translations": {"en": "test"}},
        organization_id="root",
        matrix_synthesis_groups=[
            {
                "id": "grp_1234567890123456",
                "title": {"translations": {"en": "test"}},
                "target_blocks": ["*"],
            }
        ],
    )
    mock_studio_service.save_output_profile.return_value = mock_profile
    response = client.put("/profiles/prof_0123456789abcdef0123456789abcdef", json=mock_profile.model_dump(mode="json"))
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_output_profile(mock_studio_service):
    response = client.delete("/profiles/prof_0123456789abcdef0123456789abcdef")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_clone_output_profile(mock_studio_service):
    mock_profile = OutputProfile(
        id="prof_0123456789abcdef0123456789abcdef",
        workflow_id="*",
        slug="test-copy",
        name={"translations": {"en": "test copy"}},
        organization_id="root",
        matrix_synthesis_groups=[
            {
                "id": "grp_1234567890123456",
                "title": {"translations": {"en": "test"}},
                "target_blocks": ["*"],
            }
        ],
    )
    mock_studio_service.clone_output_profile.return_value = mock_profile
    response = client.post("/profiles/prof_0123456789abcdef0123456789abcdef/clone")
    assert response.status_code == 201
    assert response.json()["id"] == "prof_0123456789abcdef0123456789abcdef"


@pytest.mark.asyncio
async def test_get_output_profile_accepts_prf_prefix(mock_studio_service):
    prf_id = "prf_1234567890abcdef"
    mock_profile = OutputProfile(
        id=prf_id,
        workflow_id="wf_1234567890abcdef",
        slug="test-profile",
        name={"translations": {"en": "test"}},
        organization_id="root",
        matrix_synthesis_groups=[
            {
                "id": "grp_1234567890123456",
                "title": {"translations": {"en": "test"}},
                "target_blocks": ["blk_sample"],
            }
        ],
    )
    mock_studio_service.get_output_profile.return_value = mock_profile
    response = client.get(f"/profiles/{prf_id}")
    assert response.status_code == 200
    assert response.json()["id"] == prf_id


@pytest.mark.asyncio
async def test_get_output_profile_rejects_invalid_id_regex(mock_studio_service):
    response = client.get("/profiles/12345678-1234-1234-1234-123456789abc")
    assert response.status_code == 422
