"""Unit tests for Admin Studio Model Registry router."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.api.routers.studio.model_registry import (
    clone_model_registry,
    create_model_registry,
    delete_model_registry,
    get_all_model_registries,
    get_available_models,
    get_model_registry,
    get_supported_locations,
    get_supported_platforms,
    save_model_registry,
)
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.dtos.studio import GCPLocationDTO, LLMPlatformDTO
from backend_v2.models.v2_core import SystemConfigModelRegistry


@pytest.fixture
def mock_current_user() -> TokenData:
    """Provide admin token for tests."""
    return TokenData(id="usr_1234567890abcdef", role=UserRole.ADMIN)


@pytest.fixture
def mock_studio_service() -> AsyncMock:
    """Provide async mock for StudioSystemConfigService."""
    return AsyncMock()


def test_get_available_models(mock_current_user: TokenData, mock_studio_service: AsyncMock) -> None:
    """Verify available models endpoint calls service."""
    mock_llm_handler = MagicMock()
    mock_studio_service.get_available_models = MagicMock(return_value=["model1"])
    res = get_available_models(
        current_user=mock_current_user, llm_handler=mock_llm_handler, studio_service=mock_studio_service
    )
    assert "model1" in res


def test_get_supported_locations(mock_current_user: TokenData, mock_studio_service: AsyncMock) -> None:
    """Verify supported locations endpoint returns locations list."""
    mock_loc = GCPLocationDTO(
        id="europe-north1",
        label="Hamina, Finland",
        description="Finland datacenter",
    )
    mock_studio_service.get_supported_locations = MagicMock(return_value=[mock_loc])
    res = get_supported_locations(current_user=mock_current_user, studio_service=mock_studio_service)
    assert len(res) == 1
    assert res[0].id == "europe-north1"


def test_get_supported_platforms(mock_current_user: TokenData, mock_studio_service: AsyncMock) -> None:
    """Verify supported platforms endpoint returns platforms list."""
    mock_platform = LLMPlatformDTO(
        id="vertex_ai",
        label="Google Cloud Vertex AI",
        has_regions=True,
    )
    mock_studio_service.get_supported_platforms = MagicMock(return_value=[mock_platform])
    res = get_supported_platforms(current_user=mock_current_user, studio_service=mock_studio_service)
    assert len(res) == 1
    assert res[0].id == "vertex_ai"
    assert res[0].has_regions is True


@pytest.mark.asyncio
async def test_get_all_model_registries(mock_current_user: TokenData, mock_studio_service: AsyncMock) -> None:
    """Verify get all model registries endpoint."""
    mock_studio_service.get_all_system_configs.return_value = []
    res = await get_all_model_registries(current_user=mock_current_user, studio_service=mock_studio_service)
    assert res == []


@pytest.mark.asyncio
async def test_create_model_registry(mock_current_user: TokenData, mock_studio_service: AsyncMock) -> None:
    """Verify create model registry draft endpoint."""
    dummy_registry = SystemConfigModelRegistry(id="sys_1234567890abcdef", models={})
    mock_studio_service.create_system_config_draft.return_value = dummy_registry
    res = await create_model_registry(current_user=mock_current_user, studio_service=mock_studio_service)
    assert res.id == "sys_1234567890abcdef"


@pytest.mark.asyncio
async def test_get_model_registry(mock_current_user: TokenData, mock_studio_service: AsyncMock) -> None:
    """Verify get single model registry endpoint."""
    dummy_registry = SystemConfigModelRegistry(id="sys_1234567890abcdef", models={})
    mock_studio_service.get_system_config.return_value = dummy_registry
    res = await get_model_registry(
        registry_id="sys_1234567890abcdef", current_user=mock_current_user, studio_service=mock_studio_service
    )
    assert res.id == "sys_1234567890abcdef"


@pytest.mark.asyncio
async def test_save_model_registry(mock_current_user: TokenData, mock_studio_service: AsyncMock) -> None:
    """Verify update model registry endpoint."""
    dummy_registry = SystemConfigModelRegistry(id="sys_1234567890abcdef", models={})
    mock_studio_service.save_system_config.return_value = dummy_registry
    res = await save_model_registry(
        registry_id="sys_1234567890abcdef",
        data=dummy_registry,
        current_user=mock_current_user,
        studio_service=mock_studio_service,
    )
    assert res.id == "sys_1234567890abcdef"


@pytest.mark.asyncio
async def test_delete_model_registry(mock_current_user: TokenData, mock_studio_service: AsyncMock) -> None:
    """Verify delete model registry endpoint."""
    mock_studio_service.delete_system_config.return_value = None
    res = await delete_model_registry(
        registry_id="sys_1234567890abcdef", current_user=mock_current_user, studio_service=mock_studio_service
    )
    assert res.status == "success"
    assert res.deleted_id == "sys_1234567890abcdef"


@pytest.mark.asyncio
async def test_clone_model_registry(mock_current_user: TokenData, mock_studio_service: AsyncMock) -> None:
    """Verify clone model registry endpoint."""
    dummy_registry = SystemConfigModelRegistry(id="sys_a1b2c3d4e5f60718", models={})
    mock_studio_service.clone_system_config.return_value = dummy_registry
    res = await clone_model_registry(
        registry_id="sys_1234567890abcdef", current_user=mock_current_user, studio_service=mock_studio_service
    )
    assert res.id == "sys_a1b2c3d4e5f60718"
