"""Comprehensive unit tests for Output Profiles SSOT router.

Validates CRUD and clone operations on /output-profiles endpoint with 100%
architectural parity, strict typing, and ISTQB equivalence partitioning.
"""

from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import (
    get_current_user_from_header,
    get_studio_output_profile_service,
)
from backend_v2.exceptions import ResourceNotFoundError
from backend_v2.main import app
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.domain.output_profile import OutputProfile


def mock_get_current_user_root() -> TokenData:
    """Fixture providing authenticated ROOT user for route tests."""
    return TokenData(
        email="root@test.com",
        id="usr_root999",
        role=UserRole.ROOT,
        organization_id="org_testorg123",
    )


@pytest.fixture
def mock_studio_service() -> AsyncMock:
    """Fixture providing an AsyncMock for StudioOutputProfileService."""
    return AsyncMock()


@pytest.fixture
def client(mock_studio_service: AsyncMock) -> Any:
    """TestClient using the main FastAPI application with all exception handlers registered."""
    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user_root
    app.dependency_overrides[get_studio_output_profile_service] = lambda: mock_studio_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_output_profile() -> OutputProfile:
    """Fixture providing a valid OutputProfile domain model."""
    return OutputProfile(
        id="prof_0123456789abcdef",
        workflow_id="wf_0123456789abcdef",
        slug="test-profile",
        name={"translations": {"en": "Test Profile", "fi": "Testiprofiili"}},
        organization_id="org_testorg123",
        matrix_synthesis_groups=[
            {
                "id": "grp_1234567890123456",
                "title": {"translations": {"en": "Group", "fi": "Ryhmä"}},
                "target_blocks": ["*"],
            }
        ],
    )


@pytest.mark.asyncio
async def test_list_output_profiles_returns_200(
    client: TestClient,
    mock_studio_service: AsyncMock,
    sample_output_profile: OutputProfile,
) -> None:
    """Test listing output profiles returns HTTP 200 with list of profiles."""
    mock_studio_service.list_output_profiles.return_value = [sample_output_profile]
    response = client.get("/api/v2/output-profiles/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == "prof_0123456789abcdef"


@pytest.mark.asyncio
async def test_create_output_profile_draft_returns_201(
    client: TestClient,
    mock_studio_service: AsyncMock,
    sample_output_profile: OutputProfile,
) -> None:
    """Test creating an output profile draft returns HTTP 201."""
    mock_studio_service.create_output_profile_draft.return_value = sample_output_profile
    response = client.post("/api/v2/output-profiles/")
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["id"] == "prof_0123456789abcdef"


@pytest.mark.asyncio
async def test_get_output_profile_returns_200(
    client: TestClient,
    mock_studio_service: AsyncMock,
    sample_output_profile: OutputProfile,
) -> None:
    """Test retrieving an output profile by valid ID returns HTTP 200."""
    mock_studio_service.get_output_profile.return_value = sample_output_profile
    response = client.get("/api/v2/output-profiles/prof_0123456789abcdef")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == "prof_0123456789abcdef"
    mock_studio_service.get_output_profile.assert_called_once()


@pytest.mark.asyncio
async def test_get_output_profile_with_prf_prefix_returns_200(
    client: TestClient,
    mock_studio_service: AsyncMock,
    sample_output_profile: OutputProfile,
) -> None:
    """Test retrieving an output profile with 'prf_' prefix passes regex and returns HTTP 200."""
    prf_profile = sample_output_profile.model_copy(update={"id": "prf_0123456789abcdef"})
    mock_studio_service.get_output_profile.return_value = prf_profile
    response = client.get("/api/v2/output-profiles/prf_0123456789abcdef")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == "prf_0123456789abcdef"


@pytest.mark.asyncio
async def test_get_output_profile_invalid_id_returns_422(
    client: TestClient,
    mock_studio_service: AsyncMock,
) -> None:
    """Test retrieving an output profile with invalid UUID format returns HTTP 422."""
    response = client.get("/api/v2/output-profiles/invalid-uuid-format")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    mock_studio_service.get_output_profile.assert_not_called()


@pytest.mark.asyncio
async def test_upsert_output_profile_returns_200(
    client: TestClient,
    mock_studio_service: AsyncMock,
    sample_output_profile: OutputProfile,
) -> None:
    """Test updating an output profile with matching ID returns HTTP 200."""
    mock_studio_service.save_output_profile.return_value = sample_output_profile
    response = client.put(
        "/api/v2/output-profiles/prof_0123456789abcdef",
        json=sample_output_profile.model_dump(mode="json"),
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == "prof_0123456789abcdef"
    mock_studio_service.save_output_profile.assert_called_once()


@pytest.mark.asyncio
async def test_upsert_output_profile_id_mismatch_returns_400(
    client: TestClient,
    mock_studio_service: AsyncMock,
    sample_output_profile: OutputProfile,
) -> None:
    """Test updating an output profile with mismatched path ID and payload ID returns HTTP 400."""
    mismatched_payload = sample_output_profile.model_copy(update={"id": "prof_9999999999999999"})
    response = client.put(
        "/api/v2/output-profiles/prof_0123456789abcdef",
        json=mismatched_payload.model_dump(mode="json"),
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    mock_studio_service.save_output_profile.assert_not_called()


@pytest.mark.asyncio
async def test_upsert_output_profile_invalid_path_id_returns_422(
    client: TestClient,
    mock_studio_service: AsyncMock,
    sample_output_profile: OutputProfile,
) -> None:
    """Test updating with invalid path ID format returns HTTP 422."""
    response = client.put(
        "/api/v2/output-profiles/not-an-opaque-id",
        json=sample_output_profile.model_dump(mode="json"),
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_delete_output_profile_returns_204(
    client: TestClient,
    mock_studio_service: AsyncMock,
) -> None:
    """Test deleting an output profile returns HTTP 204."""
    response = client.delete("/api/v2/output-profiles/prof_0123456789abcdef")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_studio_service.delete_output_profile.assert_called_once()


@pytest.mark.asyncio
async def test_delete_output_profile_invalid_id_returns_422(
    client: TestClient,
    mock_studio_service: AsyncMock,
) -> None:
    """Test deleting an output profile with invalid ID regex returns HTTP 422."""
    response = client.delete("/api/v2/output-profiles/invalid-id")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    mock_studio_service.delete_output_profile.assert_not_called()


@pytest.mark.asyncio
async def test_clone_output_profile_returns_201(
    client: TestClient,
    mock_studio_service: AsyncMock,
    sample_output_profile: OutputProfile,
) -> None:
    """Test deep cloning an output profile returns HTTP 201 with cloned model."""
    cloned_profile = sample_output_profile.model_copy(update={"id": "prof_1111111111111112"})
    mock_studio_service.clone_output_profile.return_value = cloned_profile
    response = client.post("/api/v2/output-profiles/prof_0123456789abcdef/clone")
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["id"] == "prof_1111111111111112"
    mock_studio_service.clone_output_profile.assert_called_once()


@pytest.mark.asyncio
async def test_clone_output_profile_not_found_returns_404(
    client: TestClient,
    mock_studio_service: AsyncMock,
) -> None:
    """Test cloning a non-existent output profile returns HTTP 404."""
    mock_studio_service.clone_output_profile.side_effect = ResourceNotFoundError(
        resource_type="output_profile", resource_id="prof_0000000000000000"
    )
    response = client.post("/api/v2/output-profiles/prof_0000000000000000/clone")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_clone_output_profile_invalid_id_returns_422(
    client: TestClient,
    mock_studio_service: AsyncMock,
) -> None:
    """Test cloning with invalid ID regex returns HTTP 422."""
    response = client.post("/api/v2/output-profiles/invalid-id/clone")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    mock_studio_service.clone_output_profile.assert_not_called()
