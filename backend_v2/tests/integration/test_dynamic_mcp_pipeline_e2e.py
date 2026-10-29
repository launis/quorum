"""End-to-End Integration Test Suite for Dynamic MCP Architecture & Runtime Schema Introspection.

Verifies the complete dynamic MCP lifecycle:
1. Studio MCP gateway configuration and live JSON-RPC 2.0 tool discovery ('initialize' + 'tools/list').
2. Stateful persistence roundtrip in SystemRepository and MCPGatewayCache.
3. Dynamic Pydantic V2 argument model compilation via SchemaFactory.create_mcp_tool_argument_model.
4. Multi-gateway deterministic '{gateway_slug}__{tool_id}' namespace isolation and routing via ToolDispatcher.
5. CDATA payload encapsulation, sentence-boundary budget enforcement, and MCPAuditTrace provenance.
6. Server-Driven UI (SDUI) rendering via McpAuditAdapter and PrintableSourcesAdapter.
7. ISTQB negative boundary, permission, allowlist, and SSRF firewall enforcement.
"""

from __future__ import annotations

import socket

import httpx
import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.system_config import SystemConfigMCPGateways
from backend_v2.models.dtos.mcp import (
    MCPContentBlockDTO,
    MCPDiscoveredToolWireDTO,
    MCPInitializeResultDTO,
    MCPJsonRpcRequestDTO,
    MCPJsonRpcResponseDTO,
    MCPToolCallParamsDTO,
    MCPToolCallResultDTO,
    MCPToolInputSchemaDTO,
    MCPToolSchemaPropertyDTO,
    MCPToolsListResultDTO,
)
from backend_v2.models.enums import (
    JSONSchemaPropertyType,
    MCPAuthType,
    MCPTransportType,
    TargetBlockType,
)
from backend_v2.models.view.sdui import MarkdownBlock, SduiAuditTrailBlock
from backend_v2.services.cache.typed_cache import MCPGatewayCache
from backend_v2.services.mcp.dispatcher import ToolDispatcher
from backend_v2.services.mcp.generic_mcp_client import GenericMCPClient
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.mcp_audit_adapter import McpAuditAdapter
from backend_v2.services.sdui.adapters.printable_sources_adapter import PrintableSourcesAdapter
from backend_v2.services.studio.system_config_service import StudioSystemConfigService
from backend_v2.tests.fakes.in_memory_repositories import InMemorySystemRepository


@pytest.fixture(autouse=True)
def mock_public_dns(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stub socket.getaddrinfo to resolve test domains to a public IPv4 address while preserving SSRF IP checks.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """

    def _fake_getaddrinfo(
        host: str,
        port: int | str | None,
        family: int = 0,
        type: int = 0,
        proto: int = 0,
        flags: int = 0,
    ) -> list[tuple[socket.AddressFamily, socket.SocketKind, int, str, tuple[str, int]]]:
        resolved_port = int(port) if isinstance(port, (int, str)) and str(port).isdigit() else 443
        if host in {"169.254.169.254", "127.0.0.1"}:
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (host, resolved_port))]
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", resolved_port))]

    monkeypatch.setattr(socket, "getaddrinfo", _fake_getaddrinfo)


@pytest.fixture
def root_token() -> TokenData:
    """Provide root user token for Studio MCP gateway operations.

    Returns:
        TokenData with ROOT role.
    """
    return TokenData(
        id="usr_root000000000000000000000001",
        email="root@example.com",
        role=UserRole.ROOT,
        organization_id="org_root000000000000000000000001",
    )


def _build_mock_mcp_server_transport() -> httpx.MockTransport:
    """Build an in-process JSON-RPC 2.0 MCP server transport supporting initialize, tools/list, and tools/call.

    Returns:
        Configured httpx.MockTransport instance.
    """

    def _handler(request: httpx.Request) -> httpx.Response:
        rpc_req = MCPJsonRpcRequestDTO.model_validate_json(request.content)
        if rpc_req.method == "initialize":
            init_resp = MCPJsonRpcResponseDTO(
                id=rpc_req.id,
                result=MCPInitializeResultDTO(
                    protocol_version="2025-03-26",
                    server_info={"name": "quorum-mock-mcp-server", "version": "1.0.0"},
                ),
            )
            return httpx.Response(
                200,
                headers={"Content-Type": "application/json", "Mcp-Session-Id": "sess_e2e_01"},
                json=init_resp.model_dump(mode="json", by_alias=True, exclude_none=True),
            )

        if rpc_req.method == "notifications/initialized":
            return httpx.Response(202)

        if rpc_req.method == "tools/list":
            list_resp = MCPJsonRpcResponseDTO(
                id=rpc_req.id,
                result=MCPToolsListResultDTO(
                    tools=[
                        MCPDiscoveredToolWireDTO(
                            name="mcp_tavily_search",
                            description="Execute web search for factual claim verification.",
                            input_schema=MCPToolInputSchemaDTO(
                                properties={
                                    "query": MCPToolSchemaPropertyDTO(
                                        type=JSONSchemaPropertyType.STRING,
                                        description="Search query string",
                                    ),
                                    "max_results": MCPToolSchemaPropertyDTO(
                                        type=JSONSchemaPropertyType.INTEGER,
                                        description="Maximum number of search results",
                                    ),
                                    "search_depth": MCPToolSchemaPropertyDTO(
                                        type=JSONSchemaPropertyType.STRING,
                                        description="Search depth level",
                                        enum_values=["basic", "advanced"],
                                    ),
                                },
                                required=["query"],
                                additional_properties=False,
                            ),
                        ),
                        MCPDiscoveredToolWireDTO(
                            name="wikipedia_lookup",
                            description="Lookup encyclopedic article summary.",
                            input_schema=MCPToolInputSchemaDTO(
                                properties={
                                    "query": MCPToolSchemaPropertyDTO(
                                        type=JSONSchemaPropertyType.STRING,
                                        description="Article title or topic",
                                    ),
                                },
                                required=["query"],
                                additional_properties=False,
                            ),
                        ),
                    ]
                ),
            )
            return httpx.Response(
                200,
                headers={"Content-Type": "application/json"},
                json=list_resp.model_dump(mode="json", by_alias=True, exclude_none=True),
            )

        if rpc_req.method == "tools/call" and isinstance(rpc_req.params, MCPToolCallParamsDTO):
            query_val = rpc_req.params.arguments.get("query", "")
            call_resp = MCPJsonRpcResponseDTO(
                id=rpc_req.id,
                result=MCPToolCallResultDTO(
                    content=[
                        MCPContentBlockDTO(
                            type="text",
                            text=(
                                f"Verified evidence for '{query_val}' <xml_guard>: "
                                "World Health Organization recommends at least 150 minutes of "
                                "moderate-intensity aerobic physical activity throughout the week. "
                                "Source: https://www.who.int/news-room/fact-sheets/detail/physical-activity."
                            ),
                        )
                    ],
                    is_error=False,
                ),
            )
            return httpx.Response(
                200,
                headers={"Content-Type": "application/json"},
                json=call_resp.model_dump(mode="json", by_alias=True, exclude_none=True),
            )

        return httpx.Response(400, json={"error": "Unsupported JSON-RPC method"})

    return httpx.MockTransport(_handler)


@pytest.mark.asyncio
async def test_dynamic_mcp_pipeline_full_lifecycle_e2e(root_token: TokenData) -> None:
    """Verify full E2E pipeline: Studio discovery -> persistence -> SchemaFactory -> ToolDispatcher -> SDUI."""
    system_repo = InMemorySystemRepository()
    gateway_cache = MCPGatewayCache()
    mcp_client = GenericMCPClient(transport=_build_mock_mcp_server_transport())
    studio_service = StudioSystemConfigService(
        system_repo=system_repo,
        mcp_client=mcp_client,
        gateway_cache=gateway_cache,
    )

    # 1. Configure and save default MCP gateway in Studio
    existing_gw = await system_repo.get_mcp_gateways()
    initial_gateway = existing_gw.model_copy(
        update={
            "slug": "default_mcp_gateway",
            "endpoint_url": "https://mcp.tavily.example.com/v1/mcp",
            "transport_type": MCPTransportType.STREAMABLE_HTTP,
            "auth_type": MCPAuthType.NONE,
            "timeout_seconds": 15,
            "tools": [],
        }
    )
    await studio_service.save_mcp_gateways(root_token, initial_gateway.id, initial_gateway)

    # 2. Trigger live Studio tool discovery ('initialize' + 'tools/list')
    discovered_gateway = await studio_service.discover_mcp_gateway_tools(root_token, initial_gateway.id)
    assert len(discovered_gateway.tools) == 2

    # Verify stateful persistence roundtrip in repository and cache
    persisted_gateway = await system_repo.get_mcp_gateways(id=initial_gateway.id)
    assert len(persisted_gateway.tools) == 2
    cached_gateway = await gateway_cache.get_gateway(initial_gateway.id)
    assert cached_gateway is not None
    assert len(cached_gateway.tools) == 2

    # 3. Initialize ToolDispatcher and verify dynamic SchemaFactory declarations
    dispatcher = ToolDispatcher(gateways=[persisted_gateway], mcp_client=mcp_client)
    enabled_aliases = dispatcher.get_all_enabled_tool_aliases()
    assert enabled_aliases == [
        "default_mcp_gateway__mcp_tavily_search",
        "default_mcp_gateway__wikipedia_lookup",
    ]

    declarations = dispatcher.get_declarations(["default_mcp_gateway__mcp_tavily_search"])
    assert len(declarations) == 1
    assert declarations[0].function.name == "default_mcp_gateway__mcp_tavily_search"
    assert "query" in declarations[0].function.parameters.properties
    assert declarations[0].function.parameters.properties["search_depth"].enum_values == [
        "basic",
        "advanced",
    ]

    # 4. Execute tool dynamically and verify MCPAuditTrace provenance & CDATA shielding
    audit_trace = await dispatcher.execute_tool(
        "default_mcp_gateway__mcp_tavily_search",
        {"query": "WHO physical activity guidelines", "max_results": 3, "search_depth": "basic"},
        allowed_step_tools={"default_mcp_gateway__mcp_tavily_search"},
        step_name="sp_0195f3a00000700786eedbc020274f66",
        claim_text="Adults should do at least 150 minutes of physical activity per week.",
        reasoning="Verify official WHO physical activity recommendation.",
    )

    assert audit_trace.id is not None
    assert audit_trace.gateway_id == initial_gateway.id
    assert audit_trace.gateway_slug == "default_mcp_gateway"
    assert audit_trace.namespaced_alias == "default_mcp_gateway__mcp_tavily_search"
    assert audit_trace.tool_id == "mcp_tavily_search"
    assert audit_trace.step_name == "sp_0195f3a00000700786eedbc020274f66"
    assert audit_trace.query == "WHO physical activity guidelines"
    assert audit_trace.response_summary.startswith("<![CDATA[")
    assert audit_trace.response_summary.endswith("]]>")
    assert "<xml_guard>" in audit_trace.response_summary
    assert "https://www.who.int/news-room/fact-sheets/detail/physical-activity." in audit_trace.source_urls

    # 5. Verify SDUI rendering via McpAuditAdapter and PrintableSourcesAdapter
    mock_profile = OutputProfile(
        id="prf_0195f3a0000070018111222233334444",
        slug="default_profile",
        workflow_id="wor_0195f3a0000070018111222233334444",
        name=I18nText(translations={"fi": "Oletusprofiili", "en": "Default Profile"}),
        target_block_order=[
            TargetBlockType.PRINTABLE_SOURCES_BLOCK,
        ],
    )
    adapter_context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map={audit_trace.id: audit_trace},
        global_score=None,
        profile=mock_profile,
        profile_cache=None,
        user_name="Test Auditor",
        org_name="Test Organization",
        parsed_matrices={},
        mcp_tools_map={t.tool_id: t for t in persisted_gateway.tools},
    )

    audit_blocks = McpAuditAdapter.build(adapter_context)
    assert len(audit_blocks) == 1
    assert isinstance(audit_blocks[0], SduiAuditTrailBlock)

    bibliography_blocks = PrintableSourcesAdapter.build(adapter_context)
    assert len(bibliography_blocks) == 1
    assert isinstance(bibliography_blocks[0], MarkdownBlock)
    assert "### Sources and Bibliography" in bibliography_blocks[0].text
    assert "https://www.who.int/news-room/fact-sheets/detail/physical-activity." in bibliography_blocks[0].text


@pytest.mark.asyncio
async def test_dynamic_mcp_multi_gateway_namespace_isolation_e2e(root_token: TokenData) -> None:
    """Verify collision-free namespace routing when two gateways expose tools with identical local names."""
    system_repo = InMemorySystemRepository()

    def _multi_gw_handler(request: httpx.Request) -> httpx.Response:
        host = request.url.host
        rpc_req = MCPJsonRpcRequestDTO.model_validate_json(request.content)
        if rpc_req.method == "initialize":
            return httpx.Response(
                200,
                json=MCPJsonRpcResponseDTO(
                    id=rpc_req.id,
                    result=MCPInitializeResultDTO(protocol_version="2025-03-26"),
                ).model_dump(mode="json", by_alias=True, exclude_none=True),
            )
        if rpc_req.method == "notifications/initialized":
            return httpx.Response(202)
        if rpc_req.method == "tools/list":
            return httpx.Response(
                200,
                json=MCPJsonRpcResponseDTO(
                    id=rpc_req.id,
                    result=MCPToolsListResultDTO(
                        tools=[
                            MCPDiscoveredToolWireDTO(
                                name="search",
                                description=f"Search tool hosted on {host}",
                                input_schema=MCPToolInputSchemaDTO(
                                    properties={
                                        "query": MCPToolSchemaPropertyDTO(
                                            type=JSONSchemaPropertyType.STRING,
                                            description="Query string",
                                        )
                                    },
                                    required=["query"],
                                ),
                            )
                        ]
                    ),
                ).model_dump(mode="json", by_alias=True, exclude_none=True),
            )
        if rpc_req.method == "tools/call":
            return httpx.Response(
                200,
                json=MCPJsonRpcResponseDTO(
                    id=rpc_req.id,
                    result=MCPToolCallResultDTO(
                        content=[MCPContentBlockDTO(type="text", text=f"Response from {host}.")],
                        is_error=False,
                    ),
                ).model_dump(mode="json", by_alias=True, exclude_none=True),
            )
        return httpx.Response(400)

    mcp_client = GenericMCPClient(transport=httpx.MockTransport(_multi_gw_handler))
    studio_service = StudioSystemConfigService(system_repo=system_repo, mcp_client=mcp_client)

    gw_alpha = SystemConfigMCPGateways(
        id="sys_0195f3a00000700a8aaa111122223333",
        slug="alpha_gw",
        type="mcp_gateways",
        endpoint_url="https://alpha.mcp.example.com/rpc",
        tools=[],
    )
    gw_beta = SystemConfigMCPGateways(
        id="sys_0195f3a00000700b8bbb444455556666",
        slug="beta_gw",
        type="mcp_gateways",
        endpoint_url="https://beta.mcp.example.com/rpc",
        tools=[],
    )
    await studio_service.save_mcp_gateways(root_token, gw_alpha.id, gw_alpha)
    await studio_service.save_mcp_gateways(root_token, gw_beta.id, gw_beta)

    disc_alpha = await studio_service.discover_mcp_gateway_tools(root_token, gw_alpha.id)
    disc_beta = await studio_service.discover_mcp_gateway_tools(root_token, gw_beta.id)

    dispatcher = ToolDispatcher(gateways=[disc_alpha, disc_beta], mcp_client=mcp_client)
    allowed = {"alpha_gw__search", "beta_gw__search"}

    trace_alpha = await dispatcher.execute_tool(
        "alpha_gw__search",
        {"query": "test alpha"},
        allowed_step_tools=allowed,
        step_name="sp_0195f3a00000700786eedbc020274f66",
    )
    trace_beta = await dispatcher.execute_tool(
        "beta_gw__search",
        {"query": "test beta"},
        allowed_step_tools=allowed,
        step_name="sp_0195f3a00000700786eedbc020274f66",
    )

    assert trace_alpha.gateway_id == "sys_0195f3a00000700a8aaa111122223333"
    assert trace_alpha.gateway_slug == "alpha_gw"
    assert trace_alpha.namespaced_alias == "alpha_gw__search"
    assert "Response from alpha.mcp.example.com." in trace_alpha.response_summary

    assert trace_beta.gateway_id == "sys_0195f3a00000700b8bbb444455556666"
    assert trace_beta.gateway_slug == "beta_gw"
    assert trace_beta.namespaced_alias == "beta_gw__search"
    assert "Response from beta.mcp.example.com." in trace_beta.response_summary


@pytest.mark.asyncio
async def test_dynamic_mcp_pipeline_negative_unallowed_step_tool_rejected(root_token: TokenData) -> None:
    """Negative ISTQB test: Reject tool execution when namespaced alias is not in step's allowed_step_tools."""
    system_repo = InMemorySystemRepository()
    mcp_client = GenericMCPClient(transport=_build_mock_mcp_server_transport())
    studio_service = StudioSystemConfigService(system_repo=system_repo, mcp_client=mcp_client)

    existing_gw = await system_repo.get_mcp_gateways()
    await studio_service.save_mcp_gateways(
        root_token,
        existing_gw.id,
        existing_gw.model_copy(update={"endpoint_url": "https://mcp.tavily.example.com/v1/mcp", "tools": []}),
    )
    gw = await studio_service.discover_mcp_gateway_tools(root_token, existing_gw.id)
    dispatcher = ToolDispatcher(gateways=[gw], mcp_client=mcp_client)

    with pytest.raises(AppException) as exc_info:
        await dispatcher.execute_tool(
            "default_mcp_gateway__wikipedia_lookup",
            {"query": "Quantum computing"},
            allowed_step_tools={"default_mcp_gateway__mcp_tavily_search"},
            step_name="sp_0195f3a00000700786eedbc020274f66",
        )
    assert exc_info.value.status_code == 403
    assert exc_info.value.details["error_code"] == ErrorCodes.PERMISSION_DENIED.value


@pytest.mark.asyncio
async def test_dynamic_mcp_pipeline_negative_invalid_runtime_schema_arguments_rejected(
    root_token: TokenData,
) -> None:
    """Negative ISTQB boundary test: Reject arguments violating runtime Pydantic model enum constraints."""
    system_repo = InMemorySystemRepository()
    mcp_client = GenericMCPClient(transport=_build_mock_mcp_server_transport())
    studio_service = StudioSystemConfigService(system_repo=system_repo, mcp_client=mcp_client)

    existing_gw = await system_repo.get_mcp_gateways()
    await studio_service.save_mcp_gateways(
        root_token,
        existing_gw.id,
        existing_gw.model_copy(update={"endpoint_url": "https://mcp.tavily.example.com/v1/mcp", "tools": []}),
    )
    gw = await studio_service.discover_mcp_gateway_tools(root_token, existing_gw.id)
    dispatcher = ToolDispatcher(gateways=[gw], mcp_client=mcp_client)

    with pytest.raises(AppException) as exc_info:
        await dispatcher.execute_tool(
            "default_mcp_gateway__mcp_tavily_search",
            {"query": "WHO guidelines", "search_depth": "invalid_depth_value"},
            allowed_step_tools={"default_mcp_gateway__mcp_tavily_search"},
            step_name="sp_0195f3a00000700786eedbc020274f66",
        )
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_dynamic_mcp_pipeline_negative_disabled_tool_rejected(root_token: TokenData) -> None:
    """Negative ISTQB test: Reject execution when a discovered tool is toggled disabled in Studio allowlist."""
    system_repo = InMemorySystemRepository()
    mcp_client = GenericMCPClient(transport=_build_mock_mcp_server_transport())
    studio_service = StudioSystemConfigService(system_repo=system_repo, mcp_client=mcp_client)

    existing_gw = await system_repo.get_mcp_gateways()
    await studio_service.save_mcp_gateways(
        root_token,
        existing_gw.id,
        existing_gw.model_copy(update={"endpoint_url": "https://mcp.tavily.example.com/v1/mcp", "tools": []}),
    )
    gw = await studio_service.discover_mcp_gateway_tools(root_token, existing_gw.id)
    disabled_tools = [
        t.model_copy(update={"enabled": False}) if t.tool_id == "mcp_tavily_search" else t for t in gw.tools
    ]
    updated_gw = await studio_service.save_mcp_gateways(
        root_token,
        gw.id,
        gw.model_copy(update={"tools": disabled_tools}),
    )

    dispatcher = ToolDispatcher(gateways=[updated_gw], mcp_client=mcp_client)
    assert "default_mcp_gateway__mcp_tavily_search" not in dispatcher.get_all_enabled_tool_aliases()

    with pytest.raises(AppException) as exc_info:
        await dispatcher.execute_tool(
            "default_mcp_gateway__mcp_tavily_search",
            {"query": "WHO guidelines"},
            allowed_step_tools={"default_mcp_gateway__mcp_tavily_search"},
            step_name="sp_0195f3a00000700786eedbc020274f66",
        )
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_dynamic_mcp_pipeline_negative_ssrf_cloud_metadata_endpoint_blocked(
    root_token: TokenData,
) -> None:
    """Negative ISTQB security test: Block Studio tool discovery targeting cloud metadata SSRF IP (169.254.169.254)."""
    system_repo = InMemorySystemRepository()
    mcp_client = GenericMCPClient(transport=_build_mock_mcp_server_transport())
    studio_service = StudioSystemConfigService(system_repo=system_repo, mcp_client=mcp_client)

    existing_gw = await system_repo.get_mcp_gateways()
    ssrf_gateway = existing_gw.model_copy(
        update={
            "endpoint_url": "http://169.254.169.254/latest/meta-data/",
            "tools": [],
        }
    )
    await studio_service.save_mcp_gateways(root_token, ssrf_gateway.id, ssrf_gateway)

    with pytest.raises(AppException) as exc_info:
        await studio_service.discover_mcp_gateway_tools(root_token, ssrf_gateway.id)
    assert exc_info.value.details["error_code"] == ErrorCodes.SECURITY_VIOLATION.value
