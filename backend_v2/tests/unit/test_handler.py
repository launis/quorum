from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.exceptions import AppException, ServiceUnavailableError
from backend_v2.llm.handler import LLMHandler
from backend_v2.models.enums import CognitiveTier, LLMProvider
from backend_v2.models.v2_core import ModelProfile, SystemConfigModelRegistry


@pytest.fixture
def mock_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def handler(mock_repo: AsyncMock) -> LLMHandler:
    return LLMHandler(mock_repo)


def _make_sample_registry(is_active: bool = True) -> SystemConfigModelRegistry:
    return SystemConfigModelRegistry(
        id="sys_0123456789abcdef0123456789abcdef",
        slug="global_model_registry",
        name="Global Model Registry",
        type="model_registry",
        default_provider=LLMProvider.OPENAI,
        tier_definitions={
            CognitiveTier.FAST: ModelProfile(
                provider="openai",
                model_name="gpt-4o",
                temperature=0.5,
                max_tokens=1000,
                tpm_limit=10000,
                rpm_limit=1000,
                supports_grounding=False,
                is_active=is_active,
                additional_params={},
            ),
            CognitiveTier.BALANCED: ModelProfile(provider="openai", model_name="gpt-4o"),
            CognitiveTier.DEEP: ModelProfile(provider="openai", model_name="gpt-4o"),
            CognitiveTier.REASONING: ModelProfile(provider="openai", model_name="gpt-4o"),
        },
    )


@pytest.mark.asyncio
async def test_get_active_model_registry_success(handler: LLMHandler, mock_repo: AsyncMock) -> None:
    sample_reg = _make_sample_registry()
    mock_repo.get_system_config.return_value = {
        "id": sample_reg.id,
        "slug": sample_reg.slug,
        "type": sample_reg.type,
        "config": sample_reg.model_dump(mode="json"),
    }

    registry = await handler.get_active_model_registry()
    assert "tier_definitions" in registry
    assert "fast" in registry["tier_definitions"]
    assert registry["tier_definitions"]["fast"]["provider"] == "openai"


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

    sample_reg = _make_sample_registry()
    mock_repo.get_system_config.return_value = {
        "id": sample_reg.id,
        "slug": sample_reg.slug,
        "type": sample_reg.type,
        "config": sample_reg.model_dump(mode="json"),
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
    assert "vertex_ai" in models
    assert "ai_studio" in models
    assert "openai" in models


@pytest.mark.asyncio
@patch("backend_v2.llm.handler.get_settings")
async def test_create_provider_disabled_model(
    mock_get_settings: MagicMock, handler: LLMHandler, mock_repo: AsyncMock
) -> None:
    mock_settings = MagicMock()
    mock_settings.vertex_location = "us-central1"
    mock_get_settings.return_value = mock_settings

    sample_reg = _make_sample_registry(is_active=False)
    mock_repo.get_system_config.return_value = {
        "id": sample_reg.id,
        "slug": sample_reg.slug,
        "type": sample_reg.type,
        "config": sample_reg.model_dump(mode="json"),
    }

    with pytest.raises(ServiceUnavailableError):
        await handler.create_provider_for_strategy("fast")
