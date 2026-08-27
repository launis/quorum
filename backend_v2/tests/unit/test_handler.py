from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.exceptions import AppException, ServiceUnavailableError
from backend_v2.llm.handler import LLMHandler


@pytest.fixture
def mock_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def handler(mock_repo: AsyncMock) -> LLMHandler:
    return LLMHandler(mock_repo)


@pytest.mark.asyncio
async def test_get_active_model_registry_success(handler: LLMHandler, mock_repo: AsyncMock) -> None:
    mock_repo.get_system_config.return_value = {
        "id": "sc_0123456789abcdef0123456789abcdef",
        "slug": "global_model_registry",
        "type": "model_registry",
        "config": {
            "id": "sc_0123456789abcdef0123456789abcdef",
            "slug": "global_model_registry",
            "type": "model_registry",
            "models": {
                "fast": {
                    "provider": "openai",
                    "model_name": "gpt-4o",
                    "temperature": 0.5,
                    "max_tokens": 1000,
                    "tpm_limit": 10000,
                    "rpm_limit": 1000,
                    "supports_grounding": False,
                    "is_active": True,
                    "additional_params": {},
                }
            },
        },
    }

    registry = await handler.get_active_model_registry()
    assert "models" in registry
    assert "fast" in registry["models"]
    assert registry["models"]["fast"]["provider"] == "openai"


@pytest.mark.asyncio
async def test_get_active_model_registry_corrupt(handler: LLMHandler, mock_repo: AsyncMock) -> None:
    mock_repo.get_system_config.return_value = {"config": {"invalid": "data"}}
    with pytest.raises(AppException):
        await handler.get_active_model_registry()


@pytest.mark.asyncio
@patch("backend_v2.llm.handler.get_settings")
@patch("backend_v2.llm.handler.LLMFactory.create_provider")
async def test_create_provider_for_strategy_success(
    mock_create_provider: MagicMock, mock_get_settings: MagicMock, handler: LLMHandler, mock_repo: AsyncMock
) -> None:
    mock_settings = MagicMock()
    mock_settings.vertex_location = "us-central1"
    mock_get_settings.return_value = mock_settings

    mock_repo.get_system_config.return_value = {
        "id": "sc_0123456789abcdef0123456789abcdef",
        "slug": "global_model_registry",
        "type": "model_registry",
        "config": {
            "id": "sc_0123456789abcdef0123456789abcdef",
            "slug": "global_model_registry",
            "type": "model_registry",
            "models": {
                "fast": {
                    "provider": "openai",
                    "model_name": "gpt-4o",
                    "temperature": 0.5,
                    "max_tokens": 1000,
                    "tpm_limit": 10000,
                    "rpm_limit": 1000,
                    "supports_grounding": False,
                    "is_active": True,
                    "additional_params": {},
                }
            },
        },
    }

    mock_provider_instance = MagicMock()
    mock_create_provider.return_value = mock_provider_instance

    result = await handler.create_provider_for_strategy("fast")
    assert result == mock_provider_instance
    mock_create_provider.assert_called_once()


@patch("backend_v2.llm.handler.get_settings")
def test_fetch_all_available_models_mock(mock_get_settings: MagicMock, handler: LLMHandler) -> None:
    mock_settings = MagicMock()
    mock_settings.vertex_location = "us-central1"
    mock_settings.use_mock_llm = True
    mock_settings.enabled_providers = ["mock"]
    mock_get_settings.return_value = mock_settings

    models = handler.fetch_all_available_models(["mock"])
    assert "google" in models
    assert "openai" in models


@pytest.mark.asyncio
@patch("backend_v2.llm.handler.get_settings")
async def test_create_provider_disabled_model(
    mock_get_settings: MagicMock, handler: LLMHandler, mock_repo: AsyncMock
) -> None:
    mock_settings = MagicMock()
    mock_settings.vertex_location = "us-central1"
    mock_get_settings.return_value = mock_settings

    mock_repo.get_system_config.return_value = {
        "id": "sc_0123456789abcdef0123456789abcdef",
        "slug": "global_model_registry",
        "type": "model_registry",
        "config": {
            "id": "sc_0123456789abcdef0123456789abcdef",
            "slug": "global_model_registry",
            "type": "model_registry",
            "models": {
                "fast": {
                    "provider": "openai",
                    "model_name": "gpt-4o",
                    "temperature": 0.5,
                    "max_tokens": 1000,
                    "tpm_limit": 10000,
                    "rpm_limit": 1000,
                    "supports_grounding": False,
                    "is_active": False,  # disabled
                    "additional_params": {},
                }
            },
        },
    }

    with pytest.raises(ServiceUnavailableError):
        await handler.create_provider_for_strategy("fast")
