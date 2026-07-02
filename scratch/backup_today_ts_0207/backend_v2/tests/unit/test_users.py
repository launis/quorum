from unittest.mock import AsyncMock

import pytest

from backend_v2.api.routers.iam.users import get_all_users, get_user
from backend_v2.models.auth import TokenData, UserRole


@pytest.fixture
def mock_current_user() -> TokenData:
    return TokenData(id="usr_123", role=UserRole.ADMIN)


@pytest.fixture
def mock_auth_service() -> AsyncMock:
    return AsyncMock()


@pytest.mark.asyncio
async def test_get_all_users(mock_current_user: TokenData, mock_auth_service: AsyncMock) -> None:
    mock_auth_service.list_users.return_value = []
    res = await get_all_users(current_user=mock_current_user, auth_service=mock_auth_service)
    assert res == []


@pytest.mark.asyncio
async def test_get_user(mock_current_user: TokenData, mock_auth_service: AsyncMock) -> None:
    mock_auth_service.get_user.return_value = "mock_user"
    res = await get_user(id="usr_456", current_user=mock_current_user, auth_service=mock_auth_service)
    assert res == "mock_user"  # type: ignore
