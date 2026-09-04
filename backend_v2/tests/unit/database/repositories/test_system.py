"""Unit tests for the SystemRepositoryImpl database repository."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from backend_v2.database.repositories.system import SystemRepositoryImpl
from backend_v2.exceptions import ResourceNotFoundError
from backend_v2.models.dtos.system import SystemConfigCreateDTO, SystemConfigUpdateDTO, SystemSettingsDTO
from backend_v2.models.v2_core import (
    LexiconConfigPayload,
    ModelProfile,
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
    SystemConfigPerformativeLexicons,
)


@pytest.fixture
def sample_model_registry() -> SystemConfigModelRegistry:
    """Provides a sample SystemConfigModelRegistry model."""
    return SystemConfigModelRegistry(
        id="cfg_1234567890abcdef",
        slug="model_registry",
        type="model_registry",
        models={
            "fast": ModelProfile(provider="google", model_name="gemini-2.5-flash"),
        },
    )


@pytest.fixture
def sample_mcp_gateways() -> SystemConfigMCPGateways:
    """Provides a sample SystemConfigMCPGateways model."""
    return SystemConfigMCPGateways(
        id="cfg_8172bda70c8641c5",
        slug="mcp_gateways",
        type="mcp_gateways",
        tools=[],
    )


@pytest.mark.asyncio
async def test_get_model_registry_success(sample_model_registry: SystemConfigModelRegistry) -> None:
    """Positive: retrieves model_registry document."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = [sample_model_registry.model_dump(mode="json")]

    repo = SystemRepositoryImpl(driver=mock_driver)
    res = await repo.get_model_registry()

    assert res.id == "cfg_1234567890abcdef"
    mock_driver.query.assert_called_once()


@pytest.mark.asyncio
async def test_get_model_registry_not_found_raises() -> None:
    """Negative: raises ResourceNotFoundError if model_registry document is missing."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = []

    repo = SystemRepositoryImpl(driver=mock_driver)
    with pytest.raises(ResourceNotFoundError) as exc_info:
        await repo.get_model_registry()

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["resource_id"] == "model_registry"


@pytest.mark.asyncio
async def test_update_model_registry_existing(sample_model_registry: SystemConfigModelRegistry) -> None:
    """Positive: updates existing model_registry document."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = [{"id": "cfg_models11111111", "type": "model_registry"}]
    mock_driver.upsert.return_value = "cfg_models11111111"

    repo = SystemRepositoryImpl(driver=mock_driver)
    res = await repo.update_model_registry(sample_model_registry)

    assert res is True
    mock_driver.upsert.assert_called_once()


@pytest.mark.asyncio
async def test_update_model_registry_new(sample_model_registry: SystemConfigModelRegistry) -> None:
    """Positive: creates new model_registry document when none exists."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = []
    mock_driver.upsert.return_value = "model_registry"

    repo = SystemRepositoryImpl(driver=mock_driver)
    res = await repo.update_model_registry(sample_model_registry)

    assert res is True
    mock_driver.upsert.assert_called_once()


@pytest.mark.asyncio
async def test_get_mcp_gateways_with_id_success(sample_mcp_gateways: SystemConfigMCPGateways) -> None:
    """Positive: retrieves specific mcp_gateways document by id."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = [sample_mcp_gateways.model_dump(mode="json")]

    repo = SystemRepositoryImpl(driver=mock_driver)
    res = await repo.get_mcp_gateways(id="cfg_8172bda70c8641c5")

    assert res.id == "cfg_8172bda70c8641c5"
    mock_driver.query.assert_called_once()
    filters = mock_driver.query.call_args[0][1]
    assert len(filters) == 1
    assert filters[0].field == "id"
    assert filters[0].value == "cfg_8172bda70c8641c5"


@pytest.mark.asyncio
async def test_get_mcp_gateways_default_type_success(sample_mcp_gateways: SystemConfigMCPGateways) -> None:
    """Positive: retrieves mcp_gateways document by type when id is None."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = [sample_mcp_gateways.model_dump(mode="json")]

    repo = SystemRepositoryImpl(driver=mock_driver)
    res = await repo.get_mcp_gateways()

    assert res.id == "cfg_8172bda70c8641c5"
    mock_driver.query.assert_called_once()
    filters = mock_driver.query.call_args[0][1]
    assert len(filters) == 1
    assert filters[0].field == "type"
    assert filters[0].value == "mcp_gateways"


@pytest.mark.asyncio
async def test_get_mcp_gateways_not_found_raises() -> None:
    """Negative: raises ResourceNotFoundError when mcp_gateways document is missing."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = []

    repo = SystemRepositoryImpl(driver=mock_driver)
    with pytest.raises(ResourceNotFoundError) as exc_info:
        await repo.get_mcp_gateways(id="cfg_nonexistent123")

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["resource_id"] == "cfg_nonexistent123"


@pytest.mark.asyncio
async def test_update_mcp_gateways_existing(sample_mcp_gateways: SystemConfigMCPGateways) -> None:
    """Positive: updates existing mcp_gateways document."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = [{"id": "cfg_gateways111111", "type": "mcp_gateways"}]
    mock_driver.upsert.return_value = "cfg_gateways111111"

    repo = SystemRepositoryImpl(driver=mock_driver)
    res = await repo.update_mcp_gateways(sample_mcp_gateways)

    assert res is True
    mock_driver.upsert.assert_called_once()


@pytest.mark.asyncio
async def test_update_mcp_gateways_new(sample_mcp_gateways: SystemConfigMCPGateways) -> None:
    """Positive: creates new mcp_gateways document when none exists."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = []
    mock_driver.upsert.return_value = "cfg_mcpGateways01"

    repo = SystemRepositoryImpl(driver=mock_driver)
    res = await repo.update_mcp_gateways(sample_mcp_gateways)

    assert res is True
    mock_driver.upsert.assert_called_once()


@pytest.mark.asyncio
async def test_get_system_settings_success() -> None:
    """Positive: retrieves global_settings document."""
    mock_driver = AsyncMock()
    settings_dto = SystemSettingsDTO(environment="development", maintenance_mode=False)
    mock_driver.query.return_value = [settings_dto.model_dump(mode="json")]

    repo = SystemRepositoryImpl(driver=mock_driver)
    res = await repo.get_system_settings()

    assert res is not None
    assert res.environment == "development"


@pytest.mark.asyncio
async def test_get_system_settings_not_found_raises() -> None:
    """Negative: raises ResourceNotFoundError when global_settings is missing."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = []

    repo = SystemRepositoryImpl(driver=mock_driver)
    with pytest.raises(ResourceNotFoundError) as exc_info:
        await repo.get_system_settings()

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["resource_id"] == "global_settings"


@pytest.mark.asyncio
async def test_update_system_settings_existing() -> None:
    """Positive: updates existing global_settings document."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = [{"id": "cfg_settings111111", "type": "global_settings"}]
    mock_driver.upsert.return_value = "cfg_settings111111"

    repo = SystemRepositoryImpl(driver=mock_driver)
    res = await repo.update_system_settings(
        SystemConfigUpdateDTO(system_settings=SystemSettingsDTO(maintenance_mode=True))
    )

    assert res is True
    mock_driver.upsert.assert_called_once()


@pytest.mark.asyncio
async def test_update_system_settings_new() -> None:
    """Positive: creates new global_settings document when none exists."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = []
    mock_driver.upsert.return_value = "global_settings"

    repo = SystemRepositoryImpl(driver=mock_driver)
    res = await repo.update_system_settings(
        SystemConfigUpdateDTO(system_settings=SystemSettingsDTO(maintenance_mode=True))
    )

    assert res is True
    mock_driver.upsert.assert_called_once()


@pytest.mark.asyncio
async def test_get_system_config(sample_model_registry: SystemConfigModelRegistry) -> None:
    """Positive: gets document by direct id lookup."""
    mock_driver = AsyncMock()
    mock_driver.get.return_value = sample_model_registry.model_dump(mode="json")

    repo = SystemRepositoryImpl(driver=mock_driver)
    res = await repo.get_system_config("cfg_1234567890abcdef")

    assert res is not None
    assert isinstance(res, SystemConfigModelRegistry)
    mock_driver.get.assert_called_once_with("system_config", "cfg_1234567890abcdef")


@pytest.mark.asyncio
async def test_create_system_config(sample_model_registry: SystemConfigModelRegistry) -> None:
    """Positive: creates system config document."""
    mock_driver = AsyncMock()
    mock_driver.upsert.return_value = "cfg_1234567890abcdef"

    repo = SystemRepositoryImpl(driver=mock_driver)
    res = await repo.create_system_config(SystemConfigCreateDTO(type="model_registry", content=sample_model_registry))

    assert res == "cfg_1234567890abcdef"
    mock_driver.upsert.assert_called_once()


@pytest.mark.asyncio
async def test_update_performative_lexicons() -> None:
    """Positive: updates performative lexicons configuration in-place."""
    mock_driver = AsyncMock()
    mock_driver.upsert.return_value = "sys_e0b2a3c4d5e6f7a8"

    repo = SystemRepositoryImpl(driver=mock_driver)
    lex_data = SystemConfigPerformativeLexicons(
        id="sys_e0b2a3c4d5e6f7a8",
        slug="performative_lexicons",
        type="performative_lexicons",
        lexicon_configs={
            "en": LexiconConfigPayload(
                language_code="en",
                language_name="English",
                words=["test_word"],
            )
        },
    )
    res = await repo.update_performative_lexicons(lex_data)

    assert res is True
    mock_driver.upsert.assert_called_once_with(
        "system_config", lex_data.model_dump(mode="json"), "sys_e0b2a3c4d5e6f7a8"
    )
