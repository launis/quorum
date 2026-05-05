from unittest.mock import AsyncMock

import pytest

from backend_v2.api.routers.studio.mcp_gateways import get_all_mcp_gateways
from backend_v2.models.auth import TokenData, UserRole


@pytest.fixture
def mock_current_user() -> TokenData:
    return TokenData(id="usr_123", role=UserRole.ADMIN)


@pytest.fixture
def mock_studio_service() -> AsyncMock:
    return AsyncMock()


@pytest.mark.asyncio
async def test_get_all_mcp_gateways(mock_current_user: TokenData, mock_studio_service: AsyncMock) -> None:
    mock_studio_service.list_mcp_gateways.return_value = []
    res = await get_all_mcp_gateways(current_user=mock_current_user, studio_service=mock_studio_service)
    assert res == []
