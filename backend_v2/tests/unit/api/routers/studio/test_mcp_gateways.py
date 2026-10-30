"""Unit tests for Studio MCP Gateways API Router with stateful repository roundtrips."""

from __future__ import annotations

import socket

import httpx
import pytest

from backend_v2.api.routers.studio.mcp_gateways import (
    clone_mcp_gateway,
    create_mcp_gateways,
    delete_mcp_gateway,
    discover_mcp_gateway_tools,
    get_all_mcp_gateways,
    get_mcp_gateway,
    save_mcp_gateway,
)
from backend_v2.exceptions import AppException, ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.domain.system_config import SystemConfigMCPGateways
from backend_v2.models.dtos.mcp import (
    MCPDiscoveredToolWireDTO,
    MCPInitializeResultDTO,
    MCPJsonRpcRequestDTO,
    MCPJsonRpcResponseDTO,
    MCPToolInputSchemaDTO,
    MCPToolsListResultDTO,
)
from backend_v2.services.cache.typed_cache import MCPGatewayCache
from backend_v2.services.mcp.generic_mcp_client import GenericMCPClient
from backend_v2.services.studio.system_config_service import StudioSystemConfigService
from backend_v2.tests.fakes.in_memory_repositories import InMemorySystemRepository


@pytest.fixture
def root_user() -> TokenData:
    """Return a ROOT user TokenData fixture."""
    return TokenData(
        id="usr_root000000000000000000000001",
        email="root@example.com",
        role=UserRole.ROOT,
        organization_id="org_root000000000000000000000001",
    )


@pytest.fixture
def member_user() -> TokenData:
    """Return a non-ROOT MEMBER user TokenData fixture."""
    return TokenData(
        id="usr_member0000000000000000000001",
        email="member@example.com",
        role=UserRole.MEMBER,
        organization_id="org_test00000000000000000000001",
    )


@pytest.fixture
def studio_service(monkeypatch: pytest.MonkeyPatch) -> StudioSystemConfigService:
    """Return a real StudioSystemConfigService backed by InMemorySystemRepository and MockTransport."""
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
                    serverInfo={"name": "router-mcp", "version": "1.0.0"},
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
                        description="Search tool",
                        inputSchema=MCPToolInputSchemaDTO(),
                    )
                ]
            ),
        )
        return httpx.Response(200, json=list_resp.model_dump(mode="json", by_alias=True))

    return StudioSystemConfigService(
        system_repo=InMemorySystemRepository(),
        mcp_client=GenericMCPClient(transport=httpx.MockTransport(handler)),
        gateway_cache=MCPGatewayCache(),
    )


@pytest.mark.asyncio
async def test_mcp_gateways_router_full_lifecycle(
    root_user: TokenData,
    studio_service: StudioSystemConfigService,
) -> None:
    """Verify create, get, save, clone, discover, list, and delete endpoints on MCP Gateways router."""
    initial_list = await get_all_mcp_gateways(current_user=root_user, studio_service=studio_service)
    assert len(initial_list) == 1

    draft = await create_mcp_gateways(current_user=root_user, studio_service=studio_service)
    assert draft.id.startswith("sys_")

    fetched = await get_mcp_gateway(
        gateway_id=draft.id,
        current_user=root_user,
        studio_service=studio_service,
    )
    assert fetched.id == draft.id

    updated_payload = draft.model_copy(
        update={
            "slug": "custom_gateway_slug",
            "endpoint_url": "https://mcp.tavily.example.com/mcp",
        }
    )
    saved = await save_mcp_gateway(
        gateway_id=draft.id,
        data=updated_payload,
        current_user=root_user,
        studio_service=studio_service,
    )
    assert saved.slug == "custom_gateway_slug"

    discovered = await discover_mcp_gateway_tools(
        gateway_id=draft.id,
        current_user=root_user,
        studio_service=studio_service,
    )
    assert len(discovered.tools) == 1
    assert discovered.tools[0].tool_id == "tavily_search"

    cloned = await clone_mcp_gateway(
        gateway_id=draft.id,
        current_user=root_user,
        studio_service=studio_service,
    )
    assert cloned.slug == "custom_gateway_slug_copy"

    del_resp = await delete_mcp_gateway(
        gateway_id=cloned.id,
        current_user=root_user,
        studio_service=studio_service,
    )
    assert del_resp.status == "success"
    assert del_resp.deleted_id == cloned.id


@pytest.mark.asyncio
async def test_mcp_gateways_router_negative_cases(
    root_user: TokenData,
    member_user: TokenData,
    studio_service: StudioSystemConfigService,
) -> None:
    """Verify negative RBAC, ResourceNotFoundError, and duplicate slug AppException across router endpoints."""
    assert await get_all_mcp_gateways(current_user=member_user, studio_service=studio_service) == []

    with pytest.raises(PermissionDeniedError):
        await get_mcp_gateway(
            gateway_id="sys_abcdef1234567890abcdef1234567890",
            current_user=member_user,
            studio_service=studio_service,
        )

    with pytest.raises(ResourceNotFoundError):
        await get_mcp_gateway(
            gateway_id="sys_0195f3a0000070098999999999999999",
            current_user=root_user,
            studio_service=studio_service,
        )

    with pytest.raises(ResourceNotFoundError):
        await delete_mcp_gateway(
            gateway_id="sys_0195f3a0000070098999999999999999",
            current_user=root_user,
            studio_service=studio_service,
        )

    with pytest.raises(ResourceNotFoundError):
        await discover_mcp_gateway_tools(
            gateway_id="sys_0195f3a0000070098999999999999999",
            current_user=root_user,
            studio_service=studio_service,
        )

    duplicate_gw = SystemConfigMCPGateways(
        id="sys_0195f3a00000700080008172bda70c86",
        slug="default_mcp_gateway",
        type="mcp_gateways",
        tools=[],
    )
    with pytest.raises(AppException) as exc_info:
        await save_mcp_gateway(
            gateway_id="sys_0195f3a00000700080008172bda70c86",
            data=duplicate_gw,
            current_user=root_user,
            studio_service=studio_service,
        )
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
