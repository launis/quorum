from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest

from backend_v2.api.routers.system.health import get_system_hooks
from backend_v2.models.auth import TokenData, UserRole


@pytest.fixture
def mock_current_user() -> TokenData:
    return TokenData(id="usr_123", role=UserRole.ADMIN)


@pytest.mark.asyncio
async def test_get_system_hooks(mock_current_user: TokenData) -> None:
    with patch("backend_v2.api.routers.system.health.hook_registry.get_all_hooks") as mock_get_hooks:
        mock_get_hooks.return_value = ["hook1", "hook2"]
        res = await get_system_hooks()
        assert res.hooks == ["hook1", "hook2"]
