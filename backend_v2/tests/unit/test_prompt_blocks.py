from unittest.mock import AsyncMock

import pytest

from backend_v2.api.routers.studio.prompt_blocks import get_prompt_blocks
from backend_v2.models.auth import TokenData, UserRole


@pytest.fixture
def mock_current_user() -> TokenData:
    return TokenData(id="usr_123", role=UserRole.ADMIN)


@pytest.fixture
def mock_studio_service() -> AsyncMock:
    return AsyncMock()


@pytest.mark.asyncio
async def test_get_prompt_blocks(mock_current_user: TokenData, mock_studio_service: AsyncMock) -> None:
    mock_studio_service.list_prompt_blocks.return_value = []
    res = await get_prompt_blocks(current_user=mock_current_user, studio_service=mock_studio_service)
    assert res == []
