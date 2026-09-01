"""Unit tests for StudioSystemConfigService."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.exceptions import PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.enums import GCPVertexLocation, LLMPlatformType
from backend_v2.models.v2_core import (
    AllowedMCPTool,
    I18nText,
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
)
from backend_v2.services.studio.system_config_service import StudioSystemConfigService


@pytest.fixture
def mock_system_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def root_token() -> TokenData:
    return TokenData(
        id="usr_root000000000000000000000001",
        email="root@example.com",
        role=UserRole.ROOT,
        organization_id="org_root000000000000000000000001",
    )


@pytest.fixture
def admin_token() -> TokenData:
    return TokenData(
        id="usr_admin00000000000000000000001",
        email="admin@example.com",
        role=UserRole.ADMIN,
        organization_id="org_test00000000000000000000001",
    )


@pytest.fixture
def member_token() -> TokenData:
    return TokenData(
        id="usr_member0000000000000000000001",
        email="member@example.com",
        role=UserRole.MEMBER,
        organization_id="org_test00000000000000000000001",
    )


@pytest.fixture
def service(mock_system_repo: AsyncMock) -> StudioSystemConfigService:
    return StudioSystemConfigService(system_repo=mock_system_repo)


# ============================================================================
# Available Models & Supported Locations Tests
# ============================================================================


def test_get_available_models_success(service: StudioSystemConfigService, root_token: TokenData) -> None:
    """Positive: fetches and flattens available models from LLM handler."""
    llm_handler = MagicMock()
    llm_handler.fetch_all_available_models.return_value = {
        "chat": ["gpt-4o", "claude-3-5-sonnet"],
        "fast": "gpt-4o-mini",
    }

    models = service.get_available_models(root_token, llm_handler, LLMPlatformType.ALL)
    assert models == ["claude-3-5-sonnet", "gpt-4o", "gpt-4o-mini"]
    llm_handler.fetch_all_available_models.assert_called_once_with(location=None, platform="all")


def test_get_available_models_permission_denied(service: StudioSystemConfigService, member_token: TokenData) -> None:
    """Negative: non-root/admin raises PermissionDeniedError."""
    llm_handler = MagicMock()
    with pytest.raises(PermissionDeniedError):
        service.get_available_models(member_token, llm_handler)


def test_get_supported_locations_success(service: StudioSystemConfigService, admin_token: TokenData) -> None:
    """Positive: returns list of supported GCP locations."""
    locations = service.get_supported_locations(admin_token)
    assert len(locations) == len(GCPVertexLocation)
    assert locations[0].id == GCPVertexLocation.EUROPE_NORTH1.value


def test_get_supported_locations_permission_denied(service: StudioSystemConfigService, member_token: TokenData) -> None:
    """Negative: non-root/admin raises PermissionDeniedError."""
    with pytest.raises(PermissionDeniedError):
        service.get_supported_locations(member_token)


# ============================================================================
# System Config (Model Registry) Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_system_config_success(
    service: StudioSystemConfigService, root_token: TokenData, mock_system_repo: AsyncMock
) -> None:
    """Positive: returns hydrated SystemConfigModelRegistry."""
    mock_system_repo.get_model_registry.return_value = SystemConfigModelRegistry(
        id="sys_0123456789abcdef",
        type="model_registry",
        models={},
    )
    res = await service.get_system_config(root_token, "sys_0123456789abcdef")
    assert res.id == "sys_0123456789abcdef"


@pytest.mark.asyncio
async def test_get_system_config_permission_denied(service: StudioSystemConfigService, member_token: TokenData) -> None:
    """Negative: member role raises PermissionDeniedError."""
    with pytest.raises(PermissionDeniedError):
        await service.get_system_config(member_token, "sys_0123456789abcdef")


@pytest.mark.asyncio
async def test_get_system_config_not_found(
    service: StudioSystemConfigService, root_token: TokenData, mock_system_repo: AsyncMock
) -> None:
    """Negative: missing model registry raises ResourceNotFoundError."""
    mock_system_repo.get_model_registry.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await service.get_system_config(root_token, "sys_0123456789abcdef")


@pytest.mark.asyncio
async def test_save_system_config_success(
    service: StudioSystemConfigService, root_token: TokenData, mock_system_repo: AsyncMock
) -> None:
    """Positive: saves model registry and returns hydrated object."""
    reg = SystemConfigModelRegistry(
        id="sys_0123456789abcdef",
        type="model_registry",
        models={},
    )
    mock_system_repo.get_model_registry.return_value = reg

    res = await service.save_system_config(root_token, "sys_0123456789abcdef", reg)
    assert res.id == "sys_0123456789abcdef"
    mock_system_repo.update_model_registry.assert_called_once()


@pytest.mark.asyncio
async def test_save_system_config_permission_denied(
    service: StudioSystemConfigService, member_token: TokenData
) -> None:
    """Negative: non-root user cannot save model registry."""
    reg = SystemConfigModelRegistry(
        id="sys_0123456789abcdef",
        type="model_registry",
        models={},
    )
    with pytest.raises(PermissionDeniedError):
        await service.save_system_config(member_token, "sys_0123456789abcdef", reg)


@pytest.mark.asyncio
async def test_create_model_registry_draft(
    service: StudioSystemConfigService, root_token: TokenData, mock_system_repo: AsyncMock
) -> None:
    """Positive: creates draft model registry."""
    mock_system_repo.get_model_registry.return_value = SystemConfigModelRegistry(
        id="sys_0123456789abcdef",
        type="model_registry",
        models={},
    )
    res = await service.create_system_config_draft(root_token)
    assert res.id == "sys_0123456789abcdef"


@pytest.mark.asyncio
async def test_clone_system_config_success(
    service: StudioSystemConfigService, root_token: TokenData, mock_system_repo: AsyncMock
) -> None:
    """Positive: clones existing model registry."""
    mock_system_repo.get_model_registry.side_effect = [
        SystemConfigModelRegistry(id="sys_0123456789abcdef", type="model_registry", models={}),
        SystemConfigModelRegistry(id="sys_fedcba9876543210", type="model_registry", models={}),
    ]
    res = await service.clone_system_config(root_token, "sys_0123456789abcdef")
    assert res.id == "sys_fedcba9876543210"


@pytest.mark.asyncio
async def test_clone_system_config_not_found(
    service: StudioSystemConfigService, root_token: TokenData, mock_system_repo: AsyncMock
) -> None:
    """Negative: clone non-existent model registry raises ResourceNotFoundError."""
    mock_system_repo.get_model_registry.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await service.clone_system_config(root_token, "sys_0123456789abcdef")


@pytest.mark.asyncio
async def test_save_system_config_not_found_after_save(
    service: StudioSystemConfigService, root_token: TokenData, mock_system_repo: AsyncMock
) -> None:
    """Negative: raises ResourceNotFoundError if registry not found after save."""
    reg = SystemConfigModelRegistry(
        id="sys_0123456789abcdef",
        type="model_registry",
        models={},
    )
    mock_system_repo.get_model_registry.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await service.save_system_config(root_token, "sys_0123456789abcdef", reg)


@pytest.mark.asyncio
async def test_delete_system_config_success(
    service: StudioSystemConfigService, root_token: TokenData, mock_system_repo: AsyncMock
) -> None:
    """Positive: ROOT user deletes system config successfully."""
    mock_system_repo.get_model_registry.return_value = SystemConfigModelRegistry(
        id="sys_0123456789abcdef",
        type="model_registry",
        models={},
    )
    await service.delete_system_config(root_token, "sys_0123456789abcdef")


@pytest.mark.asyncio
async def test_delete_system_config_permission_denied(
    service: StudioSystemConfigService, member_token: TokenData
) -> None:
    """Negative: non-ROOT user raises PermissionDeniedError on delete."""
    with pytest.raises(PermissionDeniedError):
        await service.delete_system_config(member_token, "sys_0123456789abcdef")


@pytest.mark.asyncio
async def test_delete_system_config_not_found(
    service: StudioSystemConfigService, root_token: TokenData, mock_system_repo: AsyncMock
) -> None:
    """Negative: delete non-existent system config raises ResourceNotFoundError."""
    mock_system_repo.get_model_registry.return_value = None
    with pytest.raises(ResourceNotFoundError):
        await service.delete_system_config(root_token, "sys_0123456789abcdef")


@pytest.mark.asyncio
async def test_list_system_configs(
    service: StudioSystemConfigService, root_token: TokenData, member_token: TokenData, mock_system_repo: AsyncMock
) -> None:
    """Positive & Negative: lists configs for ROOT, empty for non-ROOT."""
    mock_system_repo.get_model_registry.return_value = SystemConfigModelRegistry(
        id="sys_0123456789abcdef",
        type="model_registry",
        models={},
    )
    configs = await service.list_system_configs(root_token)
    assert len(configs) == 1

    configs_member = await service.list_system_configs(member_token)
    assert configs_member == []


# ============================================================================
# MCP Gateway Tests
# ============================================================================


@pytest.mark.asyncio
async def test_list_mcp_gateways(
    service: StudioSystemConfigService, root_token: TokenData, member_token: TokenData, mock_system_repo: AsyncMock
) -> None:
    """Positive: returns list of MCP gateways for ROOT, empty for non-ROOT."""
    mock_system_repo.get_mcp_gateways.return_value = SystemConfigMCPGateways(
        id="sys_8172bda70c8641c5",
        type="mcp_gateways",
        tools=[],
    )

    res = await service.list_mcp_gateways(root_token)
    assert len(res) == 1
    assert res[0].id == "sys_8172bda70c8641c5"

    res_member = await service.list_mcp_gateways(member_token)
    assert res_member == []


@pytest.mark.asyncio
async def test_get_mcp_gateways_success(
    service: StudioSystemConfigService, root_token: TokenData, mock_system_repo: AsyncMock
) -> None:
    """Positive: retrieves specific MCP gateway by id."""
    mock_system_repo.get_mcp_gateways.return_value = SystemConfigMCPGateways(
        id="sys_8172bda70c8641c5",
        type="mcp_gateways",
        tools=[
            AllowedMCPTool(
                tool_id="mcp_tavily_search",
                name=I18nText(translations={"en": "Tavily Search"}),
                description="Tavily web search",
                input_schema={},
            )
        ],
    )

    res = await service.get_mcp_gateways(root_token, "sys_8172bda70c8641c5")
    assert res.id == "sys_8172bda70c8641c5"
    assert len(res.tools) == 1
    mock_system_repo.get_mcp_gateways.assert_called_once_with(id="sys_8172bda70c8641c5")


@pytest.mark.asyncio
async def test_get_mcp_gateways_permission_denied(service: StudioSystemConfigService, member_token: TokenData) -> None:
    """Negative: non-ROOT user raises PermissionDeniedError."""
    with pytest.raises(PermissionDeniedError):
        await service.get_mcp_gateways(member_token, "sys_8172bda70c8641c5")


@pytest.mark.asyncio
async def test_save_mcp_gateways_success(
    service: StudioSystemConfigService, root_token: TokenData, mock_system_repo: AsyncMock
) -> None:
    """Positive: saves MCP gateways and returns hydrated object."""
    gw = SystemConfigMCPGateways(
        id="sys_8172bda70c8641c5",
        type="mcp_gateways",
        tools=[
            AllowedMCPTool(
                tool_id="mcp_tavily_search",
                name=I18nText(translations={"en": "Tavily Search"}),
                description="Tavily search",
                input_schema={},
            )
        ],
    )
    mock_system_repo.get_mcp_gateways.return_value = gw

    res = await service.save_mcp_gateways(root_token, "sys_8172bda70c8641c5", gw)
    assert res.id == "sys_8172bda70c8641c5"
    mock_system_repo.update_mcp_gateways.assert_called_once()
    mock_system_repo.get_mcp_gateways.assert_called_once_with(id="sys_8172bda70c8641c5")


@pytest.mark.asyncio
async def test_save_mcp_gateways_permission_denied(service: StudioSystemConfigService, member_token: TokenData) -> None:
    """Negative: non-ROOT user raises PermissionDeniedError on save."""
    gw = SystemConfigMCPGateways(
        id="sys_8172bda70c8641c5",
        type="mcp_gateways",
        tools=[],
    )
    with pytest.raises(PermissionDeniedError):
        await service.save_mcp_gateways(member_token, "sys_8172bda70c8641c5", gw)


@pytest.mark.asyncio
async def test_create_mcp_gateway_draft(
    service: StudioSystemConfigService, root_token: TokenData, mock_system_repo: AsyncMock
) -> None:
    """Positive: creates draft MCP gateway."""
    mock_system_repo.get_mcp_gateways.return_value = SystemConfigMCPGateways(
        id="sys_0123456789abcdef",
        type="mcp_gateways",
        tools=[],
    )

    res = await service.create_mcp_gateway_draft(root_token)
    assert res.id == "sys_0123456789abcdef"


@pytest.mark.asyncio
async def test_clone_mcp_gateways_success(
    service: StudioSystemConfigService, root_token: TokenData, mock_system_repo: AsyncMock
) -> None:
    """Positive: clones existing MCP gateway."""
    mock_system_repo.get_mcp_gateways.side_effect = [
        SystemConfigMCPGateways(id="sys_8172bda70c8641c5", type="mcp_gateways", tools=[]),
        SystemConfigMCPGateways(id="sys_fedcba9876543210", type="mcp_gateways", tools=[]),
    ]

    res = await service.clone_mcp_gateways(root_token, "sys_8172bda70c8641c5")
    assert res.id == "sys_fedcba9876543210"
    assert mock_system_repo.update_mcp_gateways.called


@pytest.mark.asyncio
async def test_clone_mcp_gateways_permission_denied(
    service: StudioSystemConfigService, member_token: TokenData
) -> None:
    """Negative: non-ROOT user raises PermissionDeniedError on clone."""
    with pytest.raises(PermissionDeniedError):
        await service.clone_mcp_gateways(member_token, "sys_8172bda70c8641c5")
