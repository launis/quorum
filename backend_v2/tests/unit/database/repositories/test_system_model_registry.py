"""Unit tests for SystemRepositoryImpl model registry operations."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from backend_v2.database.driver import Filter
from backend_v2.database.repositories.system import SystemRepositoryImpl
from backend_v2.exceptions import ResourceNotFoundError
from backend_v2.models.enums import CognitiveTier, LLMProvider
from backend_v2.models.v2_core import ModelProfile, SystemConfigModelRegistry


def _build_test_registry(registry_id: str, name: str, provider: LLMProvider = LLMProvider.GOOGLE) -> SystemConfigModelRegistry:
    """Helper to build a valid Option A SystemConfigModelRegistry."""
    return SystemConfigModelRegistry(
        id=registry_id,
        name=name,
        type="model_registry",
        default_provider=provider,
        tier_definitions={
            CognitiveTier.FAST: ModelProfile(provider=provider.value, model_name=f"{provider.value}-fast"),
            CognitiveTier.BALANCED: ModelProfile(provider=provider.value, model_name=f"{provider.value}-balanced"),
            CognitiveTier.DEEP: ModelProfile(provider=provider.value, model_name=f"{provider.value}-deep"),
            CognitiveTier.REASONING: ModelProfile(
                provider=provider.value,
                model_name=f"{provider.value}-reasoning",
                thinking_budget_tokens=4096,
            ),
        },
    )


@pytest.fixture
def gemini_stack() -> SystemConfigModelRegistry:
    """Fixture for Gemini stack registry."""
    return _build_test_registry("sys_e26807f3bfa3454d", "Google Gemini Sovereign Stack", LLMProvider.GOOGLE)


@pytest.fixture
def openai_stack() -> SystemConfigModelRegistry:
    """Fixture for OpenAI stack registry."""
    return _build_test_registry("sys_6f8b1c4a2e0d49f1", "OpenAI O-Series Stack", LLMProvider.OPENAI)


@pytest.mark.asyncio
async def test_get_model_registry_by_id_success(gemini_stack: SystemConfigModelRegistry) -> None:
    """Positive: retrieves specific model registry by ID."""
    mock_driver = AsyncMock()
    mock_driver.get.return_value = gemini_stack.model_dump(mode="json")

    repo = SystemRepositoryImpl(driver=mock_driver)
    res = await repo.get_model_registry(registry_id=gemini_stack.id)

    assert res.id == gemini_stack.id
    assert res.name == "Google Gemini Sovereign Stack"
    assert res.default_provider == LLMProvider.GOOGLE
    mock_driver.get.assert_called_once_with("system_config", gemini_stack.id)


@pytest.mark.asyncio
async def test_get_model_registry_by_id_not_found_raises() -> None:
    """Negative: raises ResourceNotFoundError when requested registry ID does not exist."""
    mock_driver = AsyncMock()
    mock_driver.get.return_value = None

    repo = SystemRepositoryImpl(driver=mock_driver)
    missing_id = "sys_9999999999999999"

    with pytest.raises(ResourceNotFoundError) as exc_info:
        await repo.get_model_registry(registry_id=missing_id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["resource_id"] == missing_id
    mock_driver.get.assert_called_once_with("system_config", missing_id)


@pytest.mark.asyncio
async def test_get_model_registry_by_id_wrong_type_raises() -> None:
    """Negative: raises ResourceNotFoundError when document exists but is not a model_registry."""
    mock_driver = AsyncMock()
    mock_driver.get.return_value = {"id": "sys_mcp_12345", "type": "mcp_gateways"}

    repo = SystemRepositoryImpl(driver=mock_driver)
    target_id = "sys_mcp_12345"

    with pytest.raises(ResourceNotFoundError) as exc_info:
        await repo.get_model_registry(registry_id=target_id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["resource_id"] == target_id


@pytest.mark.asyncio
async def test_get_model_registry_default_returns_primary(
    gemini_stack: SystemConfigModelRegistry, openai_stack: SystemConfigModelRegistry
) -> None:
    """Positive: when registry_id is None, deterministically returns primary registry."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = [
        openai_stack.model_dump(mode="json"),
        gemini_stack.model_dump(mode="json"),
    ]

    repo = SystemRepositoryImpl(driver=mock_driver)
    res = await repo.get_model_registry(registry_id=None)

    assert res.id == gemini_stack.id
    mock_driver.query.assert_called_once_with("system_config", [Filter("type", "==", "model_registry")])


@pytest.mark.asyncio
async def test_get_all_model_registries(
    gemini_stack: SystemConfigModelRegistry, openai_stack: SystemConfigModelRegistry
) -> None:
    """Positive: returns all model registries ordered deterministically."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = [
        openai_stack.model_dump(mode="json"),
        gemini_stack.model_dump(mode="json"),
    ]

    repo = SystemRepositoryImpl(driver=mock_driver)
    all_regs = await repo.get_all_model_registries()

    assert len(all_regs) == 2
    # Primary stack first
    assert all_regs[0].id == gemini_stack.id
    assert all_regs[1].id == openai_stack.id


@pytest.mark.asyncio
async def test_update_model_registry_upserts_by_id(openai_stack: SystemConfigModelRegistry) -> None:
    """Positive: upserts registry using its authoritative id."""
    mock_driver = AsyncMock()
    mock_driver.upsert.return_value = openai_stack.id

    repo = SystemRepositoryImpl(driver=mock_driver)
    res = await repo.update_model_registry(openai_stack)

    assert res is True
    mock_driver.upsert.assert_called_once()
    assert mock_driver.upsert.call_args[0][0] == "system_config"
    assert mock_driver.upsert.call_args[0][2] == openai_stack.id


@pytest.mark.asyncio
async def test_delete_system_config() -> None:
    """Positive: deletes system config by id."""
    mock_driver = AsyncMock()
    mock_driver.delete.return_value = True

    repo = SystemRepositoryImpl(driver=mock_driver)
    res = await repo.delete_system_config("sys_6f8b1c4a2e0d49f1")

    assert res is True
    mock_driver.delete.assert_called_once_with("system_config", "sys_6f8b1c4a2e0d49f1")
