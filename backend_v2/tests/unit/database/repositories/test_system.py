"""Unit tests for the SystemRepositoryImpl database repository."""

from unittest.mock import AsyncMock

import pytest

from backend_v2.database.repositories.system import SystemRepositoryImpl
from backend_v2.exceptions import ResourceNotFoundError


@pytest.mark.asyncio
async def test_get_model_registry_success() -> None:
    """Positive: retrieves model_registry document."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = [{"id": "sys_1234567890abcdef", "type": "model_registry", "models": {}}]

    repo = SystemRepositoryImpl(driver=mock_driver)
    res = await repo.get_model_registry()

    assert res.id == "sys_1234567890abcdef"
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
async def test_update_model_registry_existing() -> None:
    """Positive: updates existing model_registry document."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = [{"id": "sys_models_1", "type": "model_registry"}]
    mock_driver.upsert.return_value = "sys_models_1"

    repo = SystemRepositoryImpl(driver=mock_driver)
    res = await repo.update_model_registry({"models": {}})

    assert res is True
    mock_driver.upsert.assert_called_once_with(
        "system_config", {"models": {}, "type": "model_registry"}, "sys_models_1"
    )


@pytest.mark.asyncio
async def test_update_model_registry_new() -> None:
    """Positive: creates new model_registry document when none exists."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = []
    mock_driver.upsert.return_value = "model_registry"

    repo = SystemRepositoryImpl(driver=mock_driver)
    res = await repo.update_model_registry({"models": {}})

    assert res is True
    mock_driver.upsert.assert_called_once_with("system_config", {"models": {}}, "model_registry")


@pytest.mark.asyncio
async def test_get_mcp_gateways_with_id_success() -> None:
    """Positive: retrieves specific mcp_gateways document by id."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = [{"id": "sys_8172bda70c8641c5", "type": "mcp_gateways", "tools": []}]

    repo = SystemRepositoryImpl(driver=mock_driver)
    res = await repo.get_mcp_gateways(id="sys_8172bda70c8641c5")

    assert res.id == "sys_8172bda70c8641c5"
    mock_driver.query.assert_called_once()
    filters = mock_driver.query.call_args[0][1]
    assert len(filters) == 1
    assert filters[0].field == "id"
    assert filters[0].value == "sys_8172bda70c8641c5"


@pytest.mark.asyncio
async def test_get_mcp_gateways_default_type_success() -> None:
    """Positive: retrieves mcp_gateways document by type when id is None."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = [{"id": "sys_8172bda70c8641c5", "type": "mcp_gateways", "tools": []}]

    repo = SystemRepositoryImpl(driver=mock_driver)
    res = await repo.get_mcp_gateways()

    assert res.id == "sys_8172bda70c8641c5"
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
        await repo.get_mcp_gateways(id="sys_nonexistent")

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["resource_id"] == "sys_nonexistent"


@pytest.mark.asyncio
async def test_update_mcp_gateways_existing() -> None:
    """Positive: updates existing mcp_gateways document."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = [{"id": "sys_gateways_1", "type": "mcp_gateways"}]
    mock_driver.upsert.return_value = "sys_gateways_1"

    repo = SystemRepositoryImpl(driver=mock_driver)
    res = await repo.update_mcp_gateways({"tools": []})

    assert res is True
    mock_driver.upsert.assert_called_once_with("system_config", {"tools": [], "type": "mcp_gateways"}, "sys_gateways_1")


@pytest.mark.asyncio
async def test_update_mcp_gateways_new() -> None:
    """Positive: creates new mcp_gateways document when none exists."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = []
    mock_driver.upsert.return_value = "cfg_mcpGateways01"

    repo = SystemRepositoryImpl(driver=mock_driver)
    res = await repo.update_mcp_gateways({"tools": []})

    assert res is True
    mock_driver.upsert.assert_called_once_with("system_config", {"tools": []}, "cfg_mcpGateways01")


@pytest.mark.asyncio
async def test_get_system_settings_success() -> None:
    """Positive: retrieves global_settings document."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = [{"id": "global_settings", "type": "global_settings"}]

    repo = SystemRepositoryImpl(driver=mock_driver)
    res = await repo.get_system_settings()

    assert res is not None
    assert res["id"] == "global_settings"


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
    mock_driver.query.return_value = [{"id": "sys_settings_1", "type": "global_settings"}]
    mock_driver.upsert.return_value = "sys_settings_1"

    repo = SystemRepositoryImpl(driver=mock_driver)
    res = await repo.update_system_settings({"key": "val"})

    assert res is True
    mock_driver.upsert.assert_called_once_with(
        "system_config", {"key": "val", "type": "global_settings"}, "sys_settings_1"
    )


@pytest.mark.asyncio
async def test_update_system_settings_new() -> None:
    """Positive: creates new global_settings document when none exists."""
    mock_driver = AsyncMock()
    mock_driver.query.return_value = []
    mock_driver.upsert.return_value = "global_settings"

    repo = SystemRepositoryImpl(driver=mock_driver)
    res = await repo.update_system_settings({"key": "val"})

    assert res is True
    mock_driver.upsert.assert_called_once_with("system_config", {"key": "val"}, "global_settings")


@pytest.mark.asyncio
async def test_get_system_config() -> None:
    """Positive: gets document by direct id lookup."""
    mock_driver = AsyncMock()
    mock_driver.get.return_value = {"id": "cfg_1"}

    repo = SystemRepositoryImpl(driver=mock_driver)
    res = await repo.get_system_config("cfg_1")

    assert res == {"id": "cfg_1"}
    mock_driver.get.assert_called_once_with("system_config", "cfg_1")


@pytest.mark.asyncio
async def test_create_system_config() -> None:
    """Positive: creates system config document."""
    mock_driver = AsyncMock()
    mock_driver.upsert.return_value = "cfg_1"

    repo = SystemRepositoryImpl(driver=mock_driver)
    res = await repo.create_system_config({"id": "cfg_1", "data": "val"})

    assert res == "cfg_1"
    mock_driver.upsert.assert_called_once_with("system_config", {"id": "cfg_1", "data": "val"}, "cfg_1")
