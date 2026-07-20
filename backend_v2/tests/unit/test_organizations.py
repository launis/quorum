from unittest.mock import AsyncMock

import pytest

from backend_v2.api.routers.iam.organizations import get_all_organizations, get_organization
from backend_v2.models.auth import TokenData, UserRole


@pytest.fixture
def mock_current_user() -> TokenData:
    return TokenData(id="usr_123", role=UserRole.ROOT)


@pytest.fixture
def mock_auth_service() -> AsyncMock:
    return AsyncMock()


@pytest.mark.asyncio
async def test_get_all_organizations(mock_current_user: TokenData, mock_auth_service: AsyncMock) -> None:
    mock_auth_service.list_organizations.return_value = []
    res = await get_all_organizations(current_user=mock_current_user, auth_service=mock_auth_service)
    assert res == []


@pytest.mark.asyncio
async def test_get_organization(mock_current_user: TokenData, mock_auth_service: AsyncMock) -> None:
    mock_auth_service.get_organization.return_value = "mock_org"
    res = await get_organization(id="org_456", current_user=mock_current_user, auth_service=mock_auth_service)
    assert res == "mock_org"  # type: ignore
