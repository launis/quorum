"""Comprehensive unit tests for Output Profiles SSOT router.

Validates CRUD and clone operations on /output-profiles endpoint with 100%
architectural parity, strict typing, and ISTQB equivalence partitioning.
"""

from collections.abc import Iterator
from unittest.mock import AsyncMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from backend_v2.api.dependencies import (
    get_current_user_from_header,
    get_studio_output_profile_service,
)
from backend_v2.api.routers.output_profiles import (
    delete_output_profile,
    get_output_profile,
    upsert_output_profile,
)
from backend_v2.exceptions import (
    AppException,
    ErrorCodes,
    PermissionDeniedError,
    ResourceNotFoundError,
)
from backend_v2.main import app
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.synthesis import MatrixSynthesisGroup
from backend_v2.models.dtos.output_profile import OutputProfileResponseDTO
from backend_v2.tests.factories.model_factories import OutputProfileFactory


def mock_get_current_user_root() -> TokenData:
    """Fixture providing authenticated ROOT user for route tests.

    Returns:
        Authenticated ROOT user TokenData.
    """
    return TokenData(
        email="root@test.com",
        id="usr_0123456789abcdef",
        role=UserRole.ROOT,
        organization_id="org_0123456789abcdef",
    )


@pytest.fixture
def mock_studio_service() -> AsyncMock:
    """Fixture providing an AsyncMock for StudioOutputProfileService.

    Returns:
        Mocked StudioOutputProfileService instance.
    """
    return AsyncMock()


@pytest.fixture
def client(mock_studio_service: AsyncMock) -> Iterator[TestClient]:
    """TestClient using the main FastAPI application with all exception handlers registered.

    Args:
        mock_studio_service: Injected mock service dependency.

    Yields:
        Configured FastAPI TestClient instance.
    """
    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user_root
    app.dependency_overrides[get_studio_output_profile_service] = lambda: mock_studio_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_output_profile() -> OutputProfile:
    """Fixture providing a valid OutputProfile domain model via OutputProfileFactory.

    Returns:
        Strictly typed OutputProfile instance.
    """
    return OutputProfileFactory.build(
        id="prof_0123456789abcdef",
        workflow_id="wf_0123456789abcdef",
        slug="test-profile",
        name=I18nText(translations={"en": "Test Profile", "fi": "Testiprofiili"}),
        organization_id="org_0123456789abcdef",
        content_blocks=[],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_1234567890123456",
                title=I18nText(translations={"en": "Group", "fi": "Ryhmä"}),
                target_blocks=["*"],
            )
        ],
    )


@pytest.mark.asyncio
async def test_list_output_profiles_returns_200(
    client: TestClient,
    mock_studio_service: AsyncMock,
    sample_output_profile: OutputProfile,
) -> None:
    """Test listing output profiles returns HTTP 200 with validated OutputProfileResponseDTO list."""
    mock_studio_service.list_output_profiles.return_value = [sample_output_profile]
    response = client.get("/api/v2/output-profiles/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    dto = OutputProfileResponseDTO.model_validate(data[0])
    assert dto.id == "prof_0123456789abcdef"
    mock_studio_service.list_output_profiles.assert_awaited_once_with(
        initiator=mock_get_current_user_root()
    )


@pytest.mark.asyncio
async def test_create_output_profile_draft_returns_201(
    client: TestClient,
    mock_studio_service: AsyncMock,
    sample_output_profile: OutputProfile,
) -> None:
    """Test creating an output profile draft returns HTTP 201 and validates against DTO."""
    mock_studio_service.create_output_profile_draft.return_value = sample_output_profile
    response = client.post("/api/v2/output-profiles/")
    assert response.status_code == status.HTTP_201_CREATED
    dto = OutputProfileResponseDTO.model_validate(response.json())
    assert dto.id == "prof_0123456789abcdef"
    mock_studio_service.create_output_profile_draft.assert_awaited_once_with(
        initiator=mock_get_current_user_root()
    )


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
    dto = OutputProfileResponseDTO.model_validate(response.json())
    assert dto.id == "prof_0123456789abcdef"
    mock_studio_service.get_output_profile.assert_awaited_once_with(
        initiator=mock_get_current_user_root(),
        id="prof_0123456789abcdef",
    )


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
    dto = OutputProfileResponseDTO.model_validate(response.json())
    assert dto.id == "prf_0123456789abcdef"


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
    dto = OutputProfileResponseDTO.model_validate(response.json())
    assert dto.id == "prof_0123456789abcdef"
    mock_studio_service.save_output_profile.assert_awaited_once_with(
        initiator=mock_get_current_user_root(),
        id="prof_0123456789abcdef",
        data=sample_output_profile,
    )


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
async def test_upsert_output_profile_direct_raises_app_exception_on_id_mismatch(
    mock_studio_service: AsyncMock,
    sample_output_profile: OutputProfile,
) -> None:
    """Test upsert_output_profile directly raises AppException (ID_MISMATCH) when IDs differ."""
    mismatched_payload = sample_output_profile.model_copy(update={"id": "prof_9999999999999999"})
    with pytest.raises(AppException) as exc_info:
        await upsert_output_profile(
            data=mismatched_payload,
            initiator=mock_get_current_user_root(),
            service=mock_studio_service,
            profile_id="prof_0123456789abcdef",
        )
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.details == {"error_code": ErrorCodes.ID_MISMATCH.value}
    mock_studio_service.save_output_profile.assert_not_called()


@pytest.mark.asyncio
async def test_get_output_profile_direct_raises_app_exception_when_not_found(
    mock_studio_service: AsyncMock,
) -> None:
    """Test get_output_profile propagates ResourceNotFoundError (AppException) on missing ID."""
    mock_studio_service.get_output_profile.side_effect = ResourceNotFoundError(
        resource_type="output_profile",
        resource_id="prof_0000000000000000",
    )
    with pytest.raises(AppException) as exc_info:
        await get_output_profile(
            initiator=mock_get_current_user_root(),
            service=mock_studio_service,
            profile_id="prof_0000000000000000",
        )
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_output_profile_direct_raises_app_exception_on_permission_denied(
    mock_studio_service: AsyncMock,
) -> None:
    """Test delete_output_profile propagates PermissionDeniedError (AppException) on unauthorized tenant."""
    mock_studio_service.delete_output_profile.side_effect = PermissionDeniedError(
        message="Tenant modification rights violated",
    )
    with pytest.raises(AppException) as exc_info:
        await delete_output_profile(
            initiator=mock_get_current_user_root(),
            service=mock_studio_service,
            profile_id="prof_0123456789abcdef",
        )
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


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
    mock_studio_service.delete_output_profile.assert_awaited_once_with(
        initiator=mock_get_current_user_root(),
        id="prof_0123456789abcdef",
    )


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
    dto = OutputProfileResponseDTO.model_validate(response.json())
    assert dto.id == "prof_1111111111111112"
    mock_studio_service.clone_output_profile.assert_awaited_once_with(
        initiator=mock_get_current_user_root(),
        id="prof_0123456789abcdef",
    )


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
