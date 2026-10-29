"""Unit tests for StudioSystemConfigService with Stateful Roundtrip Parity."""

from __future__ import annotations

import re
import socket
from unittest.mock import MagicMock

import httpx
import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX, I18nText
from backend_v2.models.domain.system_config import (
    AllowedMCPTool,
    ModelProfile,
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
)
from backend_v2.models.dtos.mcp import (
    MCPDiscoveredToolWireDTO,
    MCPInitializeResultDTO,
    MCPJsonRpcRequestDTO,
    MCPJsonRpcResponseDTO,
    MCPToolInputSchemaDTO,
    MCPToolSchemaPropertyDTO,
    MCPToolsListResultDTO,
)
from backend_v2.models.dtos.studio import GCPLocationDTO
from backend_v2.models.enums import (
    CognitiveTier,
    JSONSchemaPropertyType,
    LLMPlatformType,
    LLMProvider,
    MCPTransportType,
    ToolCapability,
)
from backend_v2.services.cache.typed_cache import MCPGatewayCache
from backend_v2.services.mcp.generic_mcp_client import GenericMCPClient
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


def _make_dummy_registry(
    reg_id: str = "sys_0195f3a0000070008123456789abcdef",
    name: str = "Test Registry",
) -> SystemConfigModelRegistry:
    """Helper to build a valid Option A SystemConfigModelRegistry."""
    return SystemConfigModelRegistry(
        id=reg_id,
        name=name,
        type="model_registry",
        default_provider=LLMProvider.AI_STUDIO,
        tier_definitions={
            CognitiveTier.FAST: ModelProfile(provider="ai_studio", model_name="gemini-2.5-flash"),
            CognitiveTier.BALANCED: ModelProfile(provider="ai_studio", model_name="gemini-2.5-flash"),
            CognitiveTier.DEEP: ModelProfile(provider="ai_studio", model_name="gemini-2.5-pro"),
            CognitiveTier.REASONING: ModelProfile(provider="ai_studio", model_name="gemini-2.5-pro"),
        },
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
    mock_handler = MagicMock()
    mock_handler.fetch_vertex_locations.return_value = [
        GCPLocationDTO(
            id="europe-north1",
            label="Hamina, Finland (europe-north1)",
            description="Google Cloud Vertex AI region: Hamina, Finland",
        )
    ]
    locations = service.get_supported_locations(admin_token, mock_handler)
    assert len(locations) > 0
    assert locations[0].id == "europe-north1"
    assert locations[0].label == "Hamina, Finland (europe-north1)"


def test_get_supported_locations_permission_denied(service: StudioSystemConfigService, member_token: TokenData) -> None:
    """Assert non-root/admin raises PermissionDeniedError."""
    mock_handler = MagicMock()
    with pytest.raises(PermissionDeniedError):
        service.get_supported_locations(member_token, mock_handler)


def test_get_supported_platforms_success(service: StudioSystemConfigService, admin_token: TokenData) -> None:
    """Return list of supported LLM platforms."""
    platforms = service.get_supported_platforms(admin_token)
    assert len(platforms) == 4
    platform_ids = [p.id for p in platforms]
    assert platform_ids == ["vertex_ai", "ai_studio", "openai", "anthropic"]
    assert platforms[0].has_regions is True
    assert platforms[1].has_regions is False


def test_get_supported_platforms_permission_denied(service: StudioSystemConfigService, member_token: TokenData) -> None:
    """Assert non-root/admin raises PermissionDeniedError on platforms."""
    with pytest.raises(PermissionDeniedError):
        service.get_supported_platforms(member_token)


# ============================================================================
# System Config (Model Registry) Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_system_config_success(
    service: StudioSystemConfigService, root_token: TokenData, system_repo: InMemorySystemRepository
) -> None:
    """Return hydrated SystemConfigModelRegistry from repository."""
    current = (await system_repo.get_all_model_registries())[0]
    res = await service.get_system_config(root_token, current.id)
    assert res.id == current.id
    assert res.type == "model_registry"


@pytest.mark.asyncio
async def test_get_system_config_permission_denied(service: StudioSystemConfigService, member_token: TokenData) -> None:
    """Assert member role raises PermissionDeniedError."""
    with pytest.raises(PermissionDeniedError):
        await service.get_system_config(member_token, "sys_0195f3a0000070008123456789abcdef")


@pytest.mark.asyncio
async def test_get_system_config_not_found(
    service: StudioSystemConfigService,
    root_token: TokenData,
    system_repo: InMemorySystemRepository,
) -> None:
    """Assert missing model registry raises ResourceNotFoundError."""
    with pytest.raises(ResourceNotFoundError):
        await service.get_system_config(root_token, "sys_missing")


@pytest.mark.asyncio
async def test_save_system_config_success(
    service: StudioSystemConfigService, root_token: TokenData, system_repo: InMemorySystemRepository
) -> None:
    """Save model registry and verify true stateful roundtrip persistence."""
    reg = _make_dummy_registry("sys_0195f3a0000070008123456789abcdef")
    res = await service.save_system_config(root_token, "sys_0195f3a0000070008123456789abcdef", reg)
    assert res.id == "sys_0195f3a0000070008123456789abcdef"

    # Stateful Roundtrip Verification via repository
    persisted = await system_repo.get_model_registry("sys_0195f3a0000070008123456789abcdef")
    assert persisted.id == "sys_0195f3a0000070008123456789abcdef"
    assert persisted.type == "model_registry"


@pytest.mark.asyncio
async def test_save_system_config_permission_denied(
    service: StudioSystemConfigService, member_token: TokenData
) -> None:
    """Assert non-root user cannot save model registry."""
    reg = _make_dummy_registry("sys_0195f3a0000070008123456789abcdef")
    with pytest.raises(PermissionDeniedError):
        await service.save_system_config(member_token, "sys_0195f3a0000070008123456789abcdef", reg)


def test_save_system_config_corrupted_id_fails_fast() -> None:
    """Assert creating model registry with non-conforming ID raises ValidationError."""
    with pytest.raises(ValidationError):
        _make_dummy_registry(reg_id="not_an_opaque_id")


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
    persisted = await system_repo.get_model_registry(res.id)
    assert persisted.id == res.id


@pytest.mark.asyncio
async def test_clone_system_config_success(
    service: StudioSystemConfigService, root_token: TokenData, system_repo: InMemorySystemRepository
) -> None:
    """Clone existing model registry and verify stateful roundtrip."""
    original = (await system_repo.get_all_model_registries())[0]
    res = await service.clone_system_config(root_token, original.id)
    assert res.id != original.id
    assert res.id.startswith("sys_")
    assert res.name == f"{original.name} (Copy)"
    assert re.match(OPAQUE_STRIPE_ID_REGEX, res.id) is not None

    # Stateful Roundtrip:
    persisted = await system_repo.get_model_registry(res.id)
    assert persisted.id == res.id


@pytest.mark.asyncio
async def test_clone_system_config_not_found(
    service: StudioSystemConfigService,
    root_token: TokenData,
    system_repo: InMemorySystemRepository,
) -> None:
    """Assert clone non-existent model registry raises ResourceNotFoundError."""
    with pytest.raises(ResourceNotFoundError):
        await service.clone_system_config(root_token, "sys_missing")


@pytest.mark.asyncio
async def test_save_system_config_not_found_after_save(
    service: StudioSystemConfigService,
    root_token: TokenData,
    system_repo: InMemorySystemRepository,
) -> None:
    """Assert ResourceNotFoundError if registry not found after save."""
    reg = _make_dummy_registry("sys_0195f3a0000070008123456789abcdef")
    system_repo.inject_fault(
        "get_model_registry",
        ResourceNotFoundError(resource_type="system_config", resource_id="sys_0195f3a0000070008123456789abcdef"),
    )
    with pytest.raises(ResourceNotFoundError):
        await service.save_system_config(root_token, "sys_0195f3a0000070008123456789abcdef", reg)


@pytest.mark.asyncio
async def test_delete_system_config_success(
    service: StudioSystemConfigService, root_token: TokenData, system_repo: InMemorySystemRepository
) -> None:
    """Assert ROOT user deletes system config successfully."""
    reg = (await system_repo.get_all_model_registries())[0]
    await service.delete_system_config(root_token, reg.id)


@pytest.mark.asyncio
async def test_delete_system_config_permission_denied(
    service: StudioSystemConfigService, member_token: TokenData
) -> None:
    """Assert non-ROOT user raises PermissionDeniedError on delete."""
    with pytest.raises(PermissionDeniedError):
        await service.delete_system_config(member_token, "sys_0195f3a0000070008123456789abcdef")


@pytest.mark.asyncio
async def test_delete_system_config_not_found(
    service: StudioSystemConfigService,
    root_token: TokenData,
    system_repo: InMemorySystemRepository,
) -> None:
    """Assert delete non-existent system config raises ResourceNotFoundError."""
    with pytest.raises(ResourceNotFoundError):
        await service.delete_system_config(root_token, "sys_missing")


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
    current = (await system_repo.get_all_model_registries())[0]
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
async def test_get_mcp_gateways_success_and_cache_hit(
    service: StudioSystemConfigService, root_token: TokenData, system_repo: InMemorySystemRepository
) -> None:
    """Retrieve specific MCP gateway by id and verify subsequent cache hit."""
    current = await system_repo.get_mcp_gateways()
    res = await service.get_mcp_gateways(root_token, current.id)
    assert res.id == current.id

    # Second call hits MCPGatewayCache
    cached_res = await service.get_mcp_gateways(root_token, current.id)
    assert cached_res.id == current.id


@pytest.mark.asyncio
async def test_get_mcp_gateways_not_found(service: StudioSystemConfigService, root_token: TokenData) -> None:
    """Assert retrieving non-existent MCP gateway raises ResourceNotFoundError."""
    with pytest.raises(ResourceNotFoundError):
        await service.get_mcp_gateways(root_token, "sys_0195f3a0000070098999999999999999")


@pytest.mark.asyncio
async def test_get_mcp_gateways_permission_denied(service: StudioSystemConfigService, member_token: TokenData) -> None:
    """Assert non-ROOT user raises PermissionDeniedError."""
    with pytest.raises(PermissionDeniedError):
        await service.get_mcp_gateways(member_token, "sys_0195f3a00000700080008172bda70c86")


@pytest.mark.asyncio
async def test_save_mcp_gateways_success(
    service: StudioSystemConfigService, root_token: TokenData, system_repo: InMemorySystemRepository
) -> None:
    """Save MCP gateways and verify true stateful roundtrip."""
    gw = SystemConfigMCPGateways(
        id="sys_0195f3a00000700080008172bda70c86",
        slug="tavily_gateway",
        type="mcp_gateways",
        tools=[
            AllowedMCPTool(
                tool_id="mcp_tavily_search",
                name=I18nText(translations={"en": "Tavily Search"}),
                description="Tavily search",
                input_schema=MCPToolInputSchemaDTO(),
            )
        ],
    )
    res = await service.save_mcp_gateways(root_token, "sys_0195f3a00000700080008172bda70c86", gw)
    assert res.id == "sys_0195f3a00000700080008172bda70c86"
    assert res.slug == "tavily_gateway"
    assert len(res.tools) == 1
    assert res.tools[0].tool_id == "mcp_tavily_search"

    # Stateful Roundtrip Verification via repository
    persisted = await system_repo.get_mcp_gateways(id="sys_0195f3a00000700080008172bda70c86")
    assert persisted.id == "sys_0195f3a00000700080008172bda70c86"
    assert len(persisted.tools) == 1
    assert persisted.tools[0].tool_id == "mcp_tavily_search"


@pytest.mark.asyncio
async def test_save_mcp_gateways_duplicate_slug_raises_validation_error(
    service: StudioSystemConfigService, root_token: TokenData
) -> None:
    """Assert saving a gateway with a slug already in use by another gateway raises AppException."""
    gw = SystemConfigMCPGateways(
        id="sys_0195f3a00000700080008172bda70c86",
        slug="default_mcp_gateway",
        type="mcp_gateways",
        tools=[],
    )
    with pytest.raises(AppException) as exc_info:
        await service.save_mcp_gateways(root_token, "sys_0195f3a00000700080008172bda70c86", gw)
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_save_mcp_gateways_invalid_slug_format_raises_validation_error(
    service: StudioSystemConfigService, root_token: TokenData
) -> None:
    """Assert saving a gateway with malformed double-underscore slug raises AppException."""
    malformed = SystemConfigMCPGateways.model_construct(
        id="sys_0195f3a00000700080008172bda70c86",
        slug="bad__slug",
        type="mcp_gateways",
        tools=[],
    )
    with pytest.raises(AppException) as exc_info:
        await service.save_mcp_gateways(root_token, "sys_0195f3a00000700080008172bda70c86", malformed)
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_save_mcp_gateways_permission_denied(service: StudioSystemConfigService, member_token: TokenData) -> None:
    """Assert non-ROOT user raises PermissionDeniedError on save."""
    gw = SystemConfigMCPGateways(
        id="sys_0195f3a00000700080008172bda70c86",
        slug="tavily_gateway",
        type="mcp_gateways",
        tools=[],
    )
    with pytest.raises(PermissionDeniedError):
        await service.save_mcp_gateways(member_token, "sys_0195f3a00000700080008172bda70c86", gw)


@pytest.mark.asyncio
async def test_create_mcp_gateway_draft(
    service: StudioSystemConfigService, root_token: TokenData, system_repo: InMemorySystemRepository
) -> None:
    """Create draft MCP gateway and verify stateful roundtrip."""
    res = await service.create_mcp_gateway_draft(root_token)
    assert res.id.startswith("sys_")
    assert re.match(OPAQUE_STRIPE_ID_REGEX, res.id) is not None
    assert res.slug == f"gateway_{res.id.removeprefix('sys_')[:8]}"
    assert res.type == "mcp_gateways"

    # Stateful Roundtrip:
    persisted = await system_repo.get_mcp_gateways(id=res.id)
    assert persisted.id == res.id


@pytest.mark.asyncio
async def test_clone_mcp_gateways_success_and_repeated_suffix(
    service: StudioSystemConfigService, root_token: TokenData, system_repo: InMemorySystemRepository
) -> None:
    """Clone existing MCP gateway multiple times and verify unique copy slugs."""
    original = await system_repo.get_mcp_gateways()
    res = await service.clone_mcp_gateways(root_token, original.id)
    assert res.id != original.id
    assert res.id.startswith("sys_")
    assert res.slug == f"{original.slug}_copy"
    assert re.match(OPAQUE_STRIPE_ID_REGEX, res.id) is not None

    # Second clone of same original increments suffix to _copy_2
    res2 = await service.clone_mcp_gateways(root_token, original.id)
    assert res2.slug == f"{original.slug}_copy_2"

    # Stateful Roundtrip:
    persisted = await system_repo.get_mcp_gateways(id=res.id)
    assert persisted.id == res.id


@pytest.mark.asyncio
async def test_clone_mcp_gateways_not_found(service: StudioSystemConfigService, root_token: TokenData) -> None:
    """Assert cloning non-existent MCP gateway raises ResourceNotFoundError."""
    with pytest.raises(ResourceNotFoundError):
        await service.clone_mcp_gateways(root_token, "sys_0195f3a0000070098999999999999999")


@pytest.mark.asyncio
async def test_clone_mcp_gateways_permission_denied(
    service: StudioSystemConfigService, member_token: TokenData
) -> None:
    """Assert non-ROOT user raises PermissionDeniedError on clone."""
    with pytest.raises(PermissionDeniedError):
        await service.clone_mcp_gateways(member_token, "sys_0195f3a00000700080008172bda70c86")


@pytest.mark.asyncio
async def test_delete_mcp_gateways_success_and_cache_invalidation(
    service: StudioSystemConfigService, root_token: TokenData, system_repo: InMemorySystemRepository
) -> None:
    """Delete MCP gateway, verify removal from repository and cache invalidation."""
    draft = await service.create_mcp_gateway_draft(root_token)
    assert await service.gateway_cache.get_gateway(draft.id) is not None

    await service.delete_mcp_gateways(root_token, draft.id)
    assert await service.gateway_cache.get_gateway(draft.id) is None
    with pytest.raises(ResourceNotFoundError):
        await service.get_mcp_gateways(root_token, draft.id)


@pytest.mark.asyncio
async def test_delete_mcp_gateways_not_found(service: StudioSystemConfigService, root_token: TokenData) -> None:
    """Assert deleting non-existent MCP gateway raises ResourceNotFoundError."""
    with pytest.raises(ResourceNotFoundError):
        await service.delete_mcp_gateways(root_token, "sys_0195f3a0000070098999999999999999")


@pytest.mark.asyncio
async def test_delete_mcp_gateways_permission_denied(
    service: StudioSystemConfigService, member_token: TokenData
) -> None:
    """Assert non-ROOT user raises PermissionDeniedError on delete_mcp_gateways."""
    with pytest.raises(PermissionDeniedError):
        await service.delete_mcp_gateways(member_token, "sys_0195f3a00000700080008172bda70c86")


@pytest.mark.asyncio
async def test_discover_mcp_gateway_tools_preserves_existing_settings(
    monkeypatch: pytest.MonkeyPatch,
    system_repo: InMemorySystemRepository,
    root_token: TokenData,
) -> None:
    """Introspect remote MCP gateway tools while preserving enabled, capability, and name on known tools."""
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda host, port, type=0: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))],
    )

    def handler(request: httpx.Request) -> httpx.Response:
        rpc_req = MCPJsonRpcRequestDTO.model_validate_json(request.content)
        if rpc_req.method == "initialize":
            init_resp = MCPJsonRpcResponseDTO(
                id=rpc_req.id,
                result=MCPInitializeResultDTO(
                    protocolVersion="2025-03-26",
                    serverInfo={"name": "tavily-mcp", "version": "1.0.0"},
                ),
            )
            return httpx.Response(200, json=init_resp.model_dump(mode="json", by_alias=True))
        if rpc_req.method == "notifications/initialized":
            return httpx.Response(202)

        list_resp = MCPJsonRpcResponseDTO(
            id=rpc_req.id,
            result=MCPToolsListResultDTO(
                tools=[
                    MCPDiscoveredToolWireDTO(
                        name="tavily_search",
                        description="Updated remote description",
                        inputSchema=MCPToolInputSchemaDTO(
                            properties={
                                "query": MCPToolSchemaPropertyDTO(
                                    type=JSONSchemaPropertyType.STRING,
                                    description="Query string",
                                )
                            },
                            required=["query"],
                        ),
                    ),
                    MCPDiscoveredToolWireDTO(
                        name="tavily_extract",
                        description="Extract URL content",
                        inputSchema=MCPToolInputSchemaDTO(),
                    ),
                ]
            ),
        )
        return httpx.Response(200, json=list_resp.model_dump(mode="json", by_alias=True))

    mcp_client = GenericMCPClient(transport=httpx.MockTransport(handler))
    gw_cache = MCPGatewayCache()
    svc = StudioSystemConfigService(system_repo=system_repo, mcp_client=mcp_client, gateway_cache=gw_cache)

    gw = SystemConfigMCPGateways(
        id="sys_0195f3a00000700080008172bda70c86",
        slug="tavily_gateway",
        type="mcp_gateways",
        endpoint_url="https://mcp.tavily.example.com/mcp",
        transport_type=MCPTransportType.STREAMABLE_HTTP,
        tools=[
            AllowedMCPTool(
                tool_id="tavily_search",
                name=I18nText(translations={"en": "Custom Search Title", "fi": "Mukautettu haku"}),
                description="Old description",
                enabled=False,
                capability=ToolCapability.DOCUMENT_READER,
                input_schema=MCPToolInputSchemaDTO(),
            )
        ],
    )
    await svc.save_mcp_gateways(root_token, gw.id, gw)

    updated = await svc.discover_mcp_gateway_tools(root_token, gw.id)
    assert len(updated.tools) == 2

    search_tool = next(t for t in updated.tools if t.tool_id == "tavily_search")
    assert search_tool.enabled is False
    assert search_tool.capability == ToolCapability.DOCUMENT_READER
    assert search_tool.name.translations["fi"] == "Mukautettu haku"
    assert search_tool.description == "Updated remote description"
    assert "query" in search_tool.input_schema.properties

    extract_tool = next(t for t in updated.tools if t.tool_id == "tavily_extract")
    assert extract_tool.enabled is True
    assert extract_tool.capability == ToolCapability.SEARCH


@pytest.mark.asyncio
async def test_discover_mcp_gateway_tools_negative_permissions_and_not_found(
    service: StudioSystemConfigService,
    root_token: TokenData,
    member_token: TokenData,
) -> None:
    """Assert discover_mcp_gateway_tools enforces RBAC and ResourceNotFoundError."""
    with pytest.raises(PermissionDeniedError):
        await service.discover_mcp_gateway_tools(member_token, "sys_0195f3a00000700080008172bda70c86")

    with pytest.raises(ResourceNotFoundError):
        await service.discover_mcp_gateway_tools(root_token, "sys_0195f3a0000070098999999999999999")


@pytest.mark.asyncio
async def test_clone_system_config_permission_denied(
    service: StudioSystemConfigService, member_token: TokenData
) -> None:
    """Assert non-ROOT user raises PermissionDeniedError on cloning system config."""
    with pytest.raises(PermissionDeniedError):
        await service.clone_system_config(member_token, "sys_0195f3a0000070008123456789abcdef")


@pytest.mark.asyncio
async def test_save_system_config_id_mismatch_updates_id(
    service: StudioSystemConfigService, root_token: TokenData, system_repo: InMemorySystemRepository
) -> None:
    """Assert saving with mismatched ID updates ID to target ID parameter."""
    reg = _make_dummy_registry("sys_0195f3a0000070008123456789abcdef")
    target_id = "sys_0195f3a00000700f8edcba9876543210"
    res = await service.save_system_config(root_token, target_id, reg)
    assert res.id == target_id


@pytest.mark.asyncio
async def test_save_mcp_gateways_id_mismatch_updates_id(
    service: StudioSystemConfigService, root_token: TokenData, system_repo: InMemorySystemRepository
) -> None:
    """Assert saving MCP gateways with mismatched ID updates to target ID parameter."""
    gw = SystemConfigMCPGateways(
        id="sys_0195f3a00000700080008172bda70c86",
        slug="tavily_gateway",
        type="mcp_gateways",
        tools=[],
    )
    target_id = "sys_0195f3a0000070018122334455667788"
    res = await service.save_mcp_gateways(root_token, target_id, gw)
    assert res.id == target_id
