from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.api.routers.studio.model_registry import get_all_model_registries, get_available_models
from backend_v2.models.auth import TokenData, UserRole


@pytest.fixture
def mock_current_user() -> TokenData:
    return TokenData(id="usr_123", role=UserRole.ADMIN)


@pytest.fixture
def mock_studio_service() -> AsyncMock:
    return AsyncMock()


def test_get_available_models(mock_current_user: TokenData, mock_studio_service: AsyncMock) -> None:
    mock_llm_handler = MagicMock()
    mock_studio_service.get_available_models = MagicMock(return_value=["model1"])
    res = get_available_models(
        current_user=mock_current_user, llm_handler=mock_llm_handler, studio_service=mock_studio_service
    )
    assert "model1" in res


@pytest.mark.asyncio
async def test_get_all_model_registries(mock_current_user: TokenData, mock_studio_service: AsyncMock) -> None:
    mock_studio_service.get_all_system_configs.return_value = []
    res = await get_all_model_registries(current_user=mock_current_user, studio_service=mock_studio_service)
    assert res == []
