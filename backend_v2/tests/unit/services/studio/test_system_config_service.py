"""Unit tests for StudioSystemConfigService with Stateful Roundtrip Parity."""

from __future__ import annotations

import re
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX, I18nText
from backend_v2.models.enums import GCPVertexLocation, LLMPlatformType
from backend_v2.models.v2_core import (
    AllowedMCPTool,
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
)
from backend_v2.services.studio.system_config_service import StudioSystemConfigService
from backend_v2.tests.fakes.in_memory_repositories import InMemorySystemRepository


@pytest.fixture
def system_repo() -> InMemorySystemRepository:
    """Provide isolated in-memory system repository for stateful roundtrip tests."""
    return InMemorySystemRepository()


@pytest.fixture
def root_token() -> TokenData:
    """Provide root user token."""
    return TokenData(
        id="usr_root000000000000000000000001",
        email="root@example.com",
        role=UserRole.ROOT,
        organization_id="org_root000000000000000000000001",
    )


@pytest.fixture
def admin_token() -> TokenData:
    """Provide admin user token."""
    return TokenData(
        id="usr_admin00000000000000000000001",
        email="admin@example.com",
        role=UserRole.ADMIN,
        organization_id="org_test00000000000000000000001",
    )


@pytest.fixture
def member_token() -> TokenData:
    """Provide regular member user token."""
    return TokenData(
        id="usr_member0000000000000000000001",
        email="member@example.com",
        role=UserRole.MEMBER,
        organization_id="org_test00000000000000000000001",
    )


@pytest.fixture
def service(system_repo: InMemorySystemRepository) -> StudioSystemConfigService:
    """Provide StudioSystemConfigService backed by real in-memory repository."""
    return StudioSystemConfigService(system_repo=system_repo)


# ============================================================================
# Available Models & Supported Locations Tests
# ============================================================================


def test_get_available_models_success(service: StudioSystemConfigService, root_token: TokenData) -> None:
    """Fetch and flatten available models from LLM handler."""
    llm_handler = MagicMock()
    llm_handler.fetch_all_available_models.return_value = {
        "chat": ["gpt-4o", "claude-3-5-sonnet"],
        "fast": "gpt-4o-mini",
    }

    models = service.get_available_models(root_token, llm_handler, LLMPlatformType.ALL)
    assert models == ["claude-3-5-sonnet", "gpt-4o", "gpt-4o-mini"]
    llm_handler.fetch_all_available_models.assert_called_once_with(location=None, platform="all")


def test_get_available_models_permission_denied(service: StudioSystemConfigService, member_token: TokenData) -> None:
    """Assert non-root/admin raises PermissionDeniedError."""
    llm_handler = MagicMock()
    with pytest.raises(PermissionDeniedError):
        service.get_available_models(member_token, llm_handler)


def test_get_supported_locations_success(service: StudioSystemConfigService, admin_token: TokenData) -> None:
    """Return list of supported GCP locations."""
    locations = service.get_supported_locations(admin_token)
    assert len(locations) == len(GCPVertexLocation)
    assert locations[0].id == GCPVertexLocation.EUROPE_NORTH1.value


def test_get_supported_locations_permission_denied(service: StudioSystemConfigService, member_token: TokenData) -> None:
    """Assert non-root/admin raises PermissionDeniedError."""
    with pytest.raises(PermissionDeniedError):
        service.get_supported_locations(member_token)


# ============================================================================
# System Config (Model Registry) Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_system_config_success(
    service: StudioSystemConfigService, root_token: TokenData, system_repo: InMemorySystemRepository
) -> None:
    """Return hydrated SystemConfigModelRegistry from repository."""
    current = await system_repo.get_model_registry()
    res = await service.get_system_config(root_token, current.id)
    assert res.id == current.id
    assert res.type == "model_registry"


@pytest.mark.asyncio
async def test_get_system_config_permission_denied(service: StudioSystemConfigService, member_token: TokenData) -> None:
    """Assert member role raises PermissionDeniedError."""
    with pytest.raises(PermissionDeniedError):
        await service.get_system_config(member_token, "sys_0123456789abcdef")


@pytest.mark.asyncio
async def test_get_system_config_not_found(
    service: StudioSystemConfigService,
    root_token: TokenData,
    monkeypatch: pytest.MonkeyPatch,
    system_repo: InMemorySystemRepository,
) -> None:
    """Assert missing model registry raises ResourceNotFoundError."""
    monkeypatch.setattr(system_repo, "get_model_registry", AsyncMock(return_value=None))
    with pytest.raises(ResourceNotFoundError):
        await service.get_system_config(root_token, "sys_0123456789abcdef")


@pytest.mark.asyncio
async def test_save_system_config_success(
    service: StudioSystemConfigService, root_token: TokenData, system_repo: InMemorySystemRepository
) -> None:
    """Save model registry and verify true stateful roundtrip persistence."""
    reg = SystemConfigModelRegistry(
        id="sys_0123456789abcdef",
        type="model_registry",
        models={},
    )
    res = await service.save_system_config(root_token, "sys_0123456789abcdef", reg)
    assert res.id == "sys_0123456789abcdef"

    # Stateful Roundtrip Verification via repository
    persisted = await system_repo.get_model_registry()
    assert persisted.id == "sys_0123456789abcdef"
    assert persisted.type == "model_registry"


@pytest.mark.asyncio
async def test_save_system_config_permission_denied(
    service: StudioSystemConfigService, member_token: TokenData
) -> None:
    """Assert non-root user cannot save model registry."""
    reg = SystemConfigModelRegistry(
        id="sys_0123456789abcdef",
        type="model_registry",
        models={},
    )
    with pytest.raises(PermissionDeniedError):
        await service.save_system_config(member_token, "sys_0123456789abcdef", reg)


def test_save_system_config_corrupted_id_fails_fast() -> None:
    """Assert creating model registry with non-conforming ID raises ValidationError."""
    with pytest.raises(ValidationError):
        SystemConfigModelRegistry(
            id="not_an_opaque_id",
            type="model_registry",
            models={},
        )


@pytest.mark.asyncio
async def test_create_model_registry_draft(
    service: StudioSystemConfigService, root_token: TokenData, system_repo: InMemorySystemRepository
) -> None:
    """Create draft model registry and verify stateful persistence."""
    res = await service.create_system_config_draft(root_token)
    assert res.id.startswith("sys_")
    assert re.match(OPAQUE_STRIPE_ID_REGEX, res.id) is not None
    assert res.type == "model_registry"

    # Stateful Roundtrip:
    persisted = await system_repo.get_model_registry()
    assert persisted.id == res.id


@pytest.mark.asyncio
async def test_clone_system_config_success(
    service: StudioSystemConfigService, root_token: TokenData, system_repo: InMemorySystemRepository
) -> None:
    """Clone existing model registry and verify stateful roundtrip."""
    original = await system_repo.get_model_registry()
    res = await service.clone_system_config(root_token, original.id)
    assert res.id != original.id
    assert res.id.startswith("sys_")
    assert re.match(OPAQUE_STRIPE_ID_REGEX, res.id) is not None

    # Stateful Roundtrip:
    persisted = await system_repo.get_model_registry()
    assert persisted.id == res.id


@pytest.mark.asyncio
async def test_clone_system_config_not_found(
    service: StudioSystemConfigService,
    root_token: TokenData,
    monkeypatch: pytest.MonkeyPatch,
    system_repo: InMemorySystemRepository,
) -> None:
    """Assert clone non-existent model registry raises ResourceNotFoundError."""
    monkeypatch.setattr(system_repo, "get_model_registry", AsyncMock(return_value=None))
    with pytest.raises(ResourceNotFoundError):
        await service.clone_system_config(root_token, "sys_0123456789abcdef")


@pytest.mark.asyncio
async def test_save_system_config_not_found_after_save(
    service: StudioSystemConfigService,
    root_token: TokenData,
    monkeypatch: pytest.MonkeyPatch,
    system_repo: InMemorySystemRepository,
) -> None:
    """Assert ResourceNotFoundError if registry not found after save."""
    reg = SystemConfigModelRegistry(
        id="sys_0123456789abcdef",
        type="model_registry",
        models={},
    )
    original_update = system_repo.update_model_registry

    async def mock_update_and_clear(data: SystemConfigModelRegistry) -> bool:
        await original_update(data)
        monkeypatch.setattr(system_repo, "get_model_registry", AsyncMock(return_value=None))
        return True

    monkeypatch.setattr(system_repo, "update_model_registry", mock_update_and_clear)
    with pytest.raises(ResourceNotFoundError):
        await service.save_system_config(root_token, "sys_0123456789abcdef", reg)


@pytest.mark.asyncio
async def test_delete_system_config_success(
    service: StudioSystemConfigService, root_token: TokenData, system_repo: InMemorySystemRepository
) -> None:
    """Assert ROOT user deletes system config successfully."""
    reg = await system_repo.get_model_registry()
    await service.delete_system_config(root_token, reg.id)


@pytest.mark.asyncio
async def test_delete_system_config_permission_denied(
    service: StudioSystemConfigService, member_token: TokenData
) -> None:
    """Assert non-ROOT user raises PermissionDeniedError on delete."""
    with pytest.raises(PermissionDeniedError):
        await service.delete_system_config(member_token, "sys_0123456789abcdef")


@pytest.mark.asyncio
async def test_delete_system_config_not_found(
    service: StudioSystemConfigService,
    root_token: TokenData,
    monkeypatch: pytest.MonkeyPatch,
    system_repo: InMemorySystemRepository,
) -> None:
    """Assert delete non-existent system config raises ResourceNotFoundError."""
    monkeypatch.setattr(system_repo, "get_model_registry", AsyncMock(return_value=None))
    with pytest.raises(ResourceNotFoundError):
        await service.delete_system_config(root_token, "sys_0123456789abcdef")


@pytest.mark.asyncio
async def test_list_system_configs(
    service: StudioSystemConfigService,
    root_token: TokenData,
    member_token: TokenData,
    system_repo: InMemorySystemRepository,
) -> None:
    """List configs for ROOT and assert empty list for non-ROOT."""
    configs = await service.list_system_configs(root_token)
    assert len(configs) == 1
    current = await system_repo.get_model_registry()
    assert configs[0].id == current.id

    configs_member = await service.list_system_configs(member_token)
    assert configs_member == []


# ============================================================================
# MCP Gateway Tests
# ============================================================================


@pytest.mark.asyncio
async def test_list_mcp_gateways(
    service: StudioSystemConfigService,
    root_token: TokenData,
    member_token: TokenData,
    system_repo: InMemorySystemRepository,
) -> None:
    """Return list of MCP gateways for ROOT, empty for non-ROOT."""
    res = await service.list_mcp_gateways(root_token)
    assert len(res) == 1
    current = await system_repo.get_mcp_gateways()
    assert res[0].id == current.id

    res_member = await service.list_mcp_gateways(member_token)
    assert res_member == []


@pytest.mark.asyncio
async def test_get_mcp_gateways_success(
    service: StudioSystemConfigService, root_token: TokenData, system_repo: InMemorySystemRepository
) -> None:
    """Retrieve specific MCP gateway by id."""
    current = await system_repo.get_mcp_gateways()
    res = await service.get_mcp_gateways(root_token, current.id)
    assert res.id == current.id


@pytest.mark.asyncio
async def test_get_mcp_gateways_permission_denied(service: StudioSystemConfigService, member_token: TokenData) -> None:
    """Assert non-ROOT user raises PermissionDeniedError."""
    with pytest.raises(PermissionDeniedError):
        await service.get_mcp_gateways(member_token, "sys_8172bda70c8641c5")


@pytest.mark.asyncio
async def test_save_mcp_gateways_success(
    service: StudioSystemConfigService, root_token: TokenData, system_repo: InMemorySystemRepository
) -> None:
    """Save MCP gateways and verify true stateful roundtrip."""
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
    res = await service.save_mcp_gateways(root_token, "sys_8172bda70c8641c5", gw)
    assert res.id == "sys_8172bda70c8641c5"
    assert len(res.tools) == 1
    assert res.tools[0].tool_id == "mcp_tavily_search"

    # Stateful Roundtrip Verification via repository
    persisted = await system_repo.get_mcp_gateways(id="sys_8172bda70c8641c5")
    assert persisted.id == "sys_8172bda70c8641c5"
    assert len(persisted.tools) == 1
    assert persisted.tools[0].tool_id == "mcp_tavily_search"


@pytest.mark.asyncio
async def test_save_mcp_gateways_permission_denied(service: StudioSystemConfigService, member_token: TokenData) -> None:
    """Assert non-ROOT user raises PermissionDeniedError on save."""
    gw = SystemConfigMCPGateways(
        id="sys_8172bda70c8641c5",
        type="mcp_gateways",
        tools=[],
    )
    with pytest.raises(PermissionDeniedError):
        await service.save_mcp_gateways(member_token, "sys_8172bda70c8641c5", gw)


@pytest.mark.asyncio
async def test_create_mcp_gateway_draft(
    service: StudioSystemConfigService, root_token: TokenData, system_repo: InMemorySystemRepository
) -> None:
    """Create draft MCP gateway and verify stateful roundtrip."""
    res = await service.create_mcp_gateway_draft(root_token)
    assert res.id.startswith("sys_")
    assert re.match(OPAQUE_STRIPE_ID_REGEX, res.id) is not None
    assert res.type == "mcp_gateways"

    # Stateful Roundtrip:
    persisted = await system_repo.get_mcp_gateways(id=res.id)
    assert persisted.id == res.id


@pytest.mark.asyncio
async def test_clone_mcp_gateways_success(
    service: StudioSystemConfigService, root_token: TokenData, system_repo: InMemorySystemRepository
) -> None:
    """Clone existing MCP gateway and verify stateful roundtrip."""
    original = await system_repo.get_mcp_gateways()
    res = await service.clone_mcp_gateways(root_token, original.id)
    assert res.id != original.id
    assert res.id.startswith("sys_")
    assert re.match(OPAQUE_STRIPE_ID_REGEX, res.id) is not None

    # Stateful Roundtrip:
    persisted = await system_repo.get_mcp_gateways(id=res.id)
    assert persisted.id == res.id


@pytest.mark.asyncio
async def test_clone_mcp_gateways_permission_denied(
    service: StudioSystemConfigService, member_token: TokenData
) -> None:
    """Assert non-ROOT user raises PermissionDeniedError on clone."""
    with pytest.raises(PermissionDeniedError):
        await service.clone_mcp_gateways(member_token, "sys_8172bda70c8641c5")
