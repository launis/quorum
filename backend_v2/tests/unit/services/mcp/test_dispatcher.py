"""Unit tests for dynamic gateway-backed ToolDispatcher in MCP services."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.system_config import AllowedMCPTool, SystemConfigMCPGateways
from backend_v2.models.dtos.mcp import (
    MCPToolInputSchemaDTO,
    MCPToolInvocationDTO,
    MCPToolSchemaPropertyDTO,
)
from backend_v2.models.enums import JSONSchemaPropertyType, MCPAuthType, MCPTransportType, ToolCapability
from backend_v2.services.mcp.dispatcher import ToolDispatcher
from backend_v2.services.mcp.generic_mcp_client import GenericMCPClient


def _build_gateway(
    *,
    gateway_id: str = "sys_1111222233334444",
    slug: str = "default_mcp_gateway",
    tools: list[AllowedMCPTool] | None = None,
) -> SystemConfigMCPGateways:
    """Helper to construct a valid SystemConfigMCPGateways fixture."""
    default_tools: list[AllowedMCPTool] = [
        AllowedMCPTool(
            tool_id="mcp_tavily_search",
            capability=ToolCapability.SEARCH,
            name=I18nText(translations={"en": "Tavily Search", "fi": "Tavily-haku"}),
            description="Search the web for factual verification.",
            input_schema=MCPToolInputSchemaDTO(
                properties={
                    "query": MCPToolSchemaPropertyDTO(
                        type=JSONSchemaPropertyType.STRING,
                        description="Search query string.",
                    ),
                    "max_results": MCPToolSchemaPropertyDTO(
                        type=JSONSchemaPropertyType.INTEGER,
                        description="Maximum results.",
                    ),
                },
                required=["query"],
            ),
            enabled=True,
        )
    ]
    resolved_tools = default_tools
    if tools is not None:
        resolved_tools = tools

    return SystemConfigMCPGateways(
        id=gateway_id,
        slug=slug,
        endpoint_url="https://mcp.example.com/v1",
        transport_type=MCPTransportType.STREAMABLE_HTTP,
        auth_type=MCPAuthType.NONE,
        timeout_seconds=15,
        tools=resolved_tools,
    )


def test_tool_dispatcher_init_and_get_declarations() -> None:
    """Verify ToolDispatcher indexes active gateways and builds namespaced declarations."""
    gw_active = _build_gateway()
    disabled_tool = AllowedMCPTool(
        tool_id="mcp_tavily_search",
        capability=ToolCapability.SEARCH,
        name=I18nText(translations={"en": "Disabled"}),
        description="Disabled tool",
        input_schema=MCPToolInputSchemaDTO(
            properties={"query": MCPToolSchemaPropertyDTO(type=JSONSchemaPropertyType.STRING)},
            required=["query"],
        ),
        enabled=False,
    )
    gw_disabled = _build_gateway(
        gateway_id="sys_2222333344445555",
        slug="disabled_gw",
        tools=[disabled_tool],
    )
    dispatcher = ToolDispatcher([gw_active, gw_disabled])

    decls = dispatcher.get_declarations(
        [
            "default_mcp_gateway__mcp_tavily_search",
            "disabled_gw__mcp_tavily_search",
            "unknown_gw__missing",
        ]
    )
    assert len(decls) == 1
    assert decls[0].function.name == "default_mcp_gateway__mcp_tavily_search"
    assert "query" in decls[0].function.parameters.properties

    all_aliases = dispatcher.get_all_enabled_tool_aliases()
    assert all_aliases == ["default_mcp_gateway__mcp_tavily_search"]
    assert dispatcher.get_all_enabled_tool_aliases(ToolCapability.SEARCH) == ["default_mcp_gateway__mcp_tavily_search"]
    assert dispatcher.get_all_enabled_tool_aliases(ToolCapability.DOCUMENT_READER) == []


def test_tool_dispatcher_capabilities_and_search_precedence() -> None:
    """Verify capability filtering and primary search tool precedence order."""
    search_a = AllowedMCPTool(
        tool_id="search_a",
        capability=ToolCapability.SEARCH,
        name=I18nText(translations={"en": "Search A"}),
        description="Search A",
        input_schema=MCPToolInputSchemaDTO(
            properties={"query": MCPToolSchemaPropertyDTO(type=JSONSchemaPropertyType.STRING)},
            required=["query"],
        ),
        enabled=True,
    )
    search_b = AllowedMCPTool(
        tool_id="search_b",
        capability=ToolCapability.SEARCH,
        name=I18nText(translations={"en": "Search B"}),
        description="Search B",
        input_schema=MCPToolInputSchemaDTO(
            properties={"q": MCPToolSchemaPropertyDTO(type=JSONSchemaPropertyType.STRING)},
            required=["q"],
        ),
        enabled=True,
    )
    reader_1 = AllowedMCPTool(
        tool_id="reader_1",
        capability=ToolCapability.DOCUMENT_READER,
        name=I18nText(translations={"en": "Reader 1"}),
        description="Reader 1",
        input_schema=MCPToolInputSchemaDTO(
            properties={"doc_id": MCPToolSchemaPropertyDTO(type=JSONSchemaPropertyType.STRING)},
            required=["doc_id"],
        ),
        enabled=True,
    )
    gw = _build_gateway(slug="gw", tools=[search_a, search_b, reader_1])
    dispatcher = ToolDispatcher([gw])

    allowed = ["gw__reader_1", "gw__search_b", "gw__search_a"]
    search_tools = dispatcher.get_tools_by_capability(allowed, ToolCapability.SEARCH)
    assert [t.namespaced_alias for t in search_tools] == ["gw__search_b", "gw__search_a"]

    assert dispatcher.get_tools_by_capability(allowed, ToolCapability.ACTION) == []

    primary = dispatcher.resolve_primary_search_tool(allowed)
    assert primary is not None
    assert primary.namespaced_alias == "gw__search_b"

    assert dispatcher.resolve_primary_search_tool(["gw__reader_1", "gw__missing"]) is None
    assert dispatcher.has_capability(allowed, ToolCapability.DOCUMENT_READER) is True
    assert dispatcher.has_capability(["gw__reader_1"], ToolCapability.SEARCH) is False


def test_tool_dispatcher_build_search_arguments_positive_and_negative() -> None:
    """Verify build_search_arguments maps query to 'query', single required string, or fails-fast."""
    gw = _build_gateway()
    dispatcher = ToolDispatcher([gw])
    primary = dispatcher.resolve_primary_search_tool(["default_mcp_gateway__mcp_tavily_search"])
    assert primary is not None
    assert dispatcher.build_search_arguments(primary, "climate report") == {"query": "climate report"}

    # Single required string property with custom name 'search_term'
    custom_tool = AllowedMCPTool(
        tool_id="custom_search",
        capability=ToolCapability.SEARCH,
        name=I18nText(translations={"en": "Custom"}),
        description="Custom search",
        input_schema=MCPToolInputSchemaDTO(
            properties={"search_term": MCPToolSchemaPropertyDTO(type=JSONSchemaPropertyType.STRING)},
            required=["search_term"],
        ),
    )
    assert dispatcher.build_search_arguments(custom_tool, "custom query") == {"search_term": "custom query"}

    # Optional single string property when required is empty
    optional_single_str_tool = AllowedMCPTool(
        tool_id="opt_search",
        capability=ToolCapability.SEARCH,
        name=I18nText(translations={"en": "Opt"}),
        description="Optional search",
        input_schema=MCPToolInputSchemaDTO(
            properties={"keyword": MCPToolSchemaPropertyDTO(type=JSONSchemaPropertyType.STRING)},
            required=[],
        ),
    )
    assert dispatcher.build_search_arguments(optional_single_str_tool, "opt query") == {"keyword": "opt query"}

    # Negative: Multiple required parameters cannot be auto-bound from a single query string
    ambiguous_tool = AllowedMCPTool(
        tool_id="bad_search",
        capability=ToolCapability.SEARCH,
        name=I18nText(translations={"en": "Bad"}),
        description="Ambiguous search",
        input_schema=MCPToolInputSchemaDTO(
            properties={
                "query": MCPToolSchemaPropertyDTO(type=JSONSchemaPropertyType.STRING),
                "index_id": MCPToolSchemaPropertyDTO(type=JSONSchemaPropertyType.STRING),
            },
            required=["query", "index_id"],
        ),
    )
    with pytest.raises(AppException) as exc_info:
        dispatcher.build_search_arguments(ambiguous_tool, "test")
    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value


@pytest.mark.asyncio
async def test_tool_dispatcher_execute_tool_success() -> None:
    """Verify execute_tool validates arguments, invokes GenericMCPClient, and returns populated MCPAuditTrace."""
    mock_client = AsyncMock(spec=GenericMCPClient)
    mock_client.call_tool.return_value = (
        "<![CDATA[Verified evidence from https://example.com/report and https://finland.fi/stats]]>"
    )

    gw = _build_gateway()
    dispatcher = ToolDispatcher([gw], mcp_client=mock_client)

    alias = "default_mcp_gateway__mcp_tavily_search"
    trace = await dispatcher.execute_tool(
        tool_id=alias,
        raw_arguments={"query": "Finland GDP 2025", "max_results": 3},
        allowed_step_tools={alias},
        step_name="stp_verify",
        claim_text="Finland GDP grew in 2025.",
        reasoning="Check official statistics.",
    )

    assert trace.gateway_id == gw.id
    assert trace.gateway_slug == "default_mcp_gateway"
    assert trace.namespaced_alias == alias
    assert trace.tool_id == "mcp_tavily_search"
    assert trace.step_name == "stp_verify"
    assert trace.query == "Finland GDP 2025"
    assert trace.claim_text == "Finland GDP grew in 2025."
    assert trace.reasoning == "Check official statistics."
    assert "https://example.com/report" in trace.source_urls
    assert "https://finland.fi/stats" in trace.source_urls

    mock_client.call_tool.assert_awaited_once()
    call_args = mock_client.call_tool.call_args
    passed_inv: MCPToolInvocationDTO = call_args.args[1]
    assert passed_inv.tool_id == "mcp_tavily_search"
    assert passed_inv.namespaced_alias == alias
    assert passed_inv.arguments == {"query": "Finland GDP 2025", "max_results": 3}


@pytest.mark.asyncio
async def test_tool_dispatcher_execute_tool_fallback_first_string_arg_as_query() -> None:
    """Verify execute_tool extracts first string argument as trace.query when 'query' key is absent."""
    mock_client = AsyncMock(spec=GenericMCPClient)
    mock_client.call_tool.return_value = "<![CDATA[Result without URLs]]>"

    custom_tool = AllowedMCPTool(
        tool_id="lookup_entity",
        capability=ToolCapability.SEARCH,
        name=I18nText(translations={"en": "Lookup"}),
        description="Lookup entity",
        input_schema=MCPToolInputSchemaDTO(
            properties={"entity_name": MCPToolSchemaPropertyDTO(type=JSONSchemaPropertyType.STRING)},
            required=["entity_name"],
        ),
        enabled=True,
    )
    gw = _build_gateway(slug="ent_gw", tools=[custom_tool])
    dispatcher = ToolDispatcher([gw], mcp_client=mock_client)

    trace = await dispatcher.execute_tool(
        tool_id="ent_gw__lookup_entity",
        raw_arguments={"entity_name": "Nokia Corporation"},
        allowed_step_tools={"ent_gw__lookup_entity"},
        step_name="stp_lookup",
    )
    assert trace.query == "Nokia Corporation"
    assert trace.source_urls == []


@pytest.mark.asyncio
async def test_tool_dispatcher_execute_tool_unauthorized_raises_403() -> None:
    """Verify execute_tool fails-fast with PERMISSION_DENIED when tool_id is not in allowed_step_tools."""
    gw = _build_gateway()
    dispatcher = ToolDispatcher([gw], mcp_client=AsyncMock(spec=GenericMCPClient))

    with pytest.raises(AppException) as exc_info:
        await dispatcher.execute_tool(
            tool_id="default_mcp_gateway__mcp_tavily_search",
            raw_arguments={"query": "test"},
            allowed_step_tools=set(),
            step_name="stp_unauth",
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.details["error_code"] == ErrorCodes.PERMISSION_DENIED.value


@pytest.mark.asyncio
async def test_tool_dispatcher_execute_tool_disabled_raises_400() -> None:
    """Verify execute_tool fails-fast with VALIDATION_FAILED when tool is disabled on gateway."""
    disabled_tool = AllowedMCPTool(
        tool_id="disabled_search",
        capability=ToolCapability.SEARCH,
        name=I18nText(translations={"en": "Disabled"}),
        description="Disabled tool",
        input_schema=MCPToolInputSchemaDTO(
            properties={"query": MCPToolSchemaPropertyDTO(type=JSONSchemaPropertyType.STRING)},
            required=["query"],
        ),
        enabled=False,
    )
    gw = _build_gateway(tools=[disabled_tool])
    dispatcher = ToolDispatcher([gw], mcp_client=AsyncMock(spec=GenericMCPClient))

    alias = "default_mcp_gateway__disabled_search"
    with pytest.raises(AppException) as exc_info:
        await dispatcher.execute_tool(
            tool_id=alias,
            raw_arguments={"query": "test"},
            allowed_step_tools={alias},
            step_name="stp_disabled",
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_tool_dispatcher_execute_tool_not_found_raises_404() -> None:
    """Verify execute_tool fails-fast with RESOURCE_NOT_FOUND when whitelisted tool does not exist."""
    dispatcher = ToolDispatcher([], mcp_client=AsyncMock(spec=GenericMCPClient))

    alias = "default_mcp_gateway__missing_tool"
    with pytest.raises(AppException) as exc_info:
        await dispatcher.execute_tool(
            tool_id=alias,
            raw_arguments={"query": "test"},
            allowed_step_tools={alias},
            step_name="stp_missing",
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


@pytest.mark.asyncio
async def test_tool_dispatcher_execute_tool_invalid_arguments_raises_400() -> None:
    """Verify execute_tool fails-fast with VALIDATION_FAILED when raw_arguments violate compiled Pydantic schema."""
    gw = _build_gateway()
    dispatcher = ToolDispatcher([gw], mcp_client=AsyncMock(spec=GenericMCPClient))

    alias = "default_mcp_gateway__mcp_tavily_search"
    with pytest.raises(AppException) as exc_info:
        await dispatcher.execute_tool(
            tool_id=alias,
            raw_arguments={"unexpected_arg": "bad"},
            allowed_step_tools={alias},
            step_name="stp_invalid_args",
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_tool_dispatcher_execute_tool_timeout_raises_504() -> None:
    """Verify execute_tool translates TimeoutError into 504 SERVICE_UNAVAILABLE AppException."""
    mock_client = AsyncMock(spec=GenericMCPClient)
    mock_client.call_tool.side_effect = TimeoutError("Simulated timeout")

    gw = _build_gateway()
    dispatcher = ToolDispatcher([gw], mcp_client=mock_client)

    alias = "default_mcp_gateway__mcp_tavily_search"
    with pytest.raises(AppException) as exc_info:
        await dispatcher.execute_tool(
            tool_id=alias,
            raw_arguments={"query": "timeout query"},
            allowed_step_tools={alias},
            step_name="stp_timeout",
        )

    assert exc_info.value.status_code == 504
    assert exc_info.value.details["error_code"] == ErrorCodes.SERVICE_UNAVAILABLE.value


@pytest.mark.asyncio
async def test_tool_dispatcher_execute_tool_propagates_non_timeout_exception() -> None:
    """Verify execute_tool records exception on span and re-raises non-timeout errors."""
    mock_client = AsyncMock(spec=GenericMCPClient)
    mock_client.call_tool.side_effect = RuntimeError("Unexpected transport failure")

    gw = _build_gateway()
    dispatcher = ToolDispatcher([gw], mcp_client=mock_client)

    alias = "default_mcp_gateway__mcp_tavily_search"
    with pytest.raises(RuntimeError, match="Unexpected transport failure"):
        await dispatcher.execute_tool(
            tool_id=alias,
            raw_arguments={"query": "crash query"},
            allowed_step_tools={alias},
            step_name="stp_crash",
        )


def test_tool_dispatcher_build_search_arguments_exa_web_search() -> None:
    """Verify build_search_arguments binds search query and objective for Exa web_search_exa schema."""
    exa_tool = AllowedMCPTool(
        tool_id="web_search_exa",
        capability=ToolCapability.SEARCH,
        name=I18nText(translations={"en": "Web Search"}),
        description="Search the web for any topic and get clean, ready-to-use content.",
        input_schema=MCPToolInputSchemaDTO(
            properties={
                "query": MCPToolSchemaPropertyDTO(
                    type=JSONSchemaPropertyType.STRING,
                    description="Natural language search query.",
                    min_length=1,
                ),
                "numResults": MCPToolSchemaPropertyDTO(
                    type=JSONSchemaPropertyType.NUMBER,
                    description="Number of search results to return.",
                ),
                "objective": MCPToolSchemaPropertyDTO(
                    type=JSONSchemaPropertyType.STRING,
                    description="Goal for this search turn.",
                    min_length=1,
                    max_length=4096,
                ),
            },
            required=["query", "objective"],
        ),
    )
    gw = SystemConfigMCPGateways(
        id="sys_9c2093907e2d4d24",
        slug="exa_gateway",
        endpoint_url="https://mcp.exa.ai/mcp",
        transport_type=MCPTransportType.STREAMABLE_HTTP,
        auth_type=MCPAuthType.NONE,
        tools=[exa_tool],
    )
    dispatcher = ToolDispatcher([gw])
    resolved = dispatcher.resolve_primary_search_tool(["exa_gateway__web_search_exa"])
    assert resolved is not None

    # 1. Fallback objective from query
    args = dispatcher.build_search_arguments(resolved, "climate report")
    assert args["query"] == "climate report"
    assert args["objective"] == "Find external evidence regarding: climate report"

    # 2. Objective derived from claim_text
    args_claim = dispatcher.build_search_arguments(
        resolved,
        "climate report",
        claim_text="Global temperatures rose by 1.2C",
    )
    assert args_claim["query"] == "climate report"
    assert args_claim["objective"] == "Verify factual accuracy for claim: Global temperatures rose by 1.2C"

    # 3. Objective derived from reasoning when claim_text is absent
    args_reasoning = dispatcher.build_search_arguments(
        resolved,
        "climate report",
        reasoning="Evaluate recent IPCC baseline metrics",
    )
    assert args_reasoning["objective"] == "Evaluate recent IPCC baseline metrics"

    # 4. Explicit objective override takes precedence
    args_explicit = dispatcher.build_search_arguments(
        resolved,
        "climate report",
        claim_text="Some claim",
        reasoning="Some reasoning",
        objective="Custom authoritative search goal",
    )
    assert args_explicit["objective"] == "Custom authoritative search goal"


