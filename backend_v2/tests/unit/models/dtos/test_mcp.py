"""Unit tests for MCP DTOs."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.mcp import (
    MCPCapabilityConfigDTO,
    MCPContentBlockDTO,
    MCPDiscoveredToolWireDTO,
    MCPFunctionDefinitionDTO,
    MCPInitializeClientInfoDTO,
    MCPInitializeParamsDTO,
    MCPInitializeResultDTO,
    MCPJsonRpcErrorDTO,
    MCPJsonRpcRequestDTO,
    MCPJsonRpcResponseDTO,
    MCPToolCallParamsDTO,
    MCPToolCallResultDTO,
    MCPToolDeclarationDTO,
    MCPToolDescriptorDTO,
    MCPToolInputSchemaDTO,
    MCPToolInvocationDTO,
    MCPToolSchemaPropertyDTO,
    MCPToolsListResultDTO,
    MCPValidationContextDTO,
    ParsedMCPToolAliasDTO,
)
from backend_v2.models.dtos.quote_evidence import SourceDocumentContext
from backend_v2.models.enums import JSONSchemaPropertyType, ToolCapability


def test_mcp_tool_declaration_dto() -> None:
    """Test MCPToolDeclarationDTO and nested MCPFunctionDefinitionDTO with recursive schema."""
    input_schema = MCPToolInputSchemaDTO(
        properties={
            "q": MCPToolSchemaPropertyDTO(
                type=JSONSchemaPropertyType.STRING,
                description="Query string",
            ),
            "tags": MCPToolSchemaPropertyDTO(
                type=JSONSchemaPropertyType.ARRAY,
                items=MCPToolSchemaPropertyDTO(type=JSONSchemaPropertyType.STRING),
            ),
        },
        required=["q"],
    )
    func = MCPFunctionDefinitionDTO(
        name="web_search",
        description="Searches the web via Tavily",
        parameters=input_schema,
        strict=True,
    )
    tool = MCPToolDeclarationDTO(function=func)
    assert tool.type == "function"
    assert tool.function.name == "web_search"
    assert tool.function.description == "Searches the web via Tavily"
    assert tool.function.strict is True
    assert tool.function.parameters.properties["q"].type == JSONSchemaPropertyType.STRING
    assert tool.function.parameters.properties["tags"].items is not None
    assert tool.function.parameters.properties["tags"].items.type == JSONSchemaPropertyType.STRING


def test_mcp_tool_schema_property_dto_aliases_and_recursion() -> None:
    """Test MCPToolSchemaPropertyDTO AliasChoices for enum/enum_values and additionalProperties."""
    raw_prop = {
        "type": "object",
        "title": "FilterOptions",
        "description": "Nested object filter",
        "enum": ["a", "b"],
        "additionalProperties": False,
        "properties": {
            "limit": {
                "type": "integer",
                "description": "Max items",
            }
        },
        "required": ["limit"],
    }
    prop = MCPToolSchemaPropertyDTO.model_validate(raw_prop)
    assert prop.type == JSONSchemaPropertyType.OBJECT
    assert prop.title == "FilterOptions"
    assert prop.enum_values == ["a", "b"]
    assert prop.additional_properties is False
    assert prop.properties is not None
    assert prop.properties["limit"].type == JSONSchemaPropertyType.INTEGER

    dumped = prop.model_dump(mode="json")
    rehydrated = MCPToolSchemaPropertyDTO.model_validate(dumped)
    assert rehydrated == prop


def test_parsed_mcp_tool_alias_and_invocation_dtos() -> None:
    """Test ParsedMCPToolAliasDTO, MCPToolDescriptorDTO, and MCPToolInvocationDTO."""
    alias = ParsedMCPToolAliasDTO(gateway_slug="tavily_gw", tool_id="search")
    assert alias.gateway_slug == "tavily_gw"
    assert alias.tool_id == "search"

    descriptor = MCPToolDescriptorDTO(
        gateway_id="sys_8172bda70c8641c5",
        gateway_slug="tavily_gw",
        namespaced_alias="tavily_gw__search",
        tool_id="search",
        description="Web search",
        capability=ToolCapability.SEARCH,
        input_schema=MCPToolInputSchemaDTO(),
        enabled=True,
    )
    assert descriptor.capability == ToolCapability.SEARCH
    assert descriptor.enabled is True

    invocation = MCPToolInvocationDTO(
        gateway_id="sys_8172bda70c8641c5",
        gateway_slug="tavily_gw",
        tool_id="search",
        namespaced_alias="tavily_gw__search",
        arguments={"query": "quorum", "max_results": 3, "tags": ["ai", "mcp"]},
    )
    assert invocation.arguments["query"] == "quorum"


def test_mcp_json_rpc_wire_dtos_roundtrip() -> None:
    """Test JSON-RPC 2.0 request and response wire DTOs with camelCase AliasChoices."""
    init_req = MCPJsonRpcRequestDTO(
        id=1,
        method="initialize",
        params=MCPInitializeParamsDTO(
            client_info=MCPInitializeClientInfoDTO(name="quorum", version="2.0.0"),
            capabilities={"tools": MCPCapabilityConfigDTO(list_changed=False)},
        ),
    )
    assert init_req.jsonrpc == "2.0"

    call_req = MCPJsonRpcRequestDTO(
        id="req-2",
        method="tools/call",
        params=MCPToolCallParamsDTO(name="search", arguments={"query": "test"}),
    )
    assert call_req.id == "req-2"

    wire_tools_resp = {
        "jsonrpc": "2.0",
        "id": 2,
        "result": {
            "tools": [
                {
                    "name": "mcp_search",
                    "description": "Search via MCP",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"query": {"type": "string"}},
                        "required": ["query"],
                        "additionalProperties": False,
                    },
                }
            ]
        },
    }
    parsed_tools_resp = MCPJsonRpcResponseDTO.model_validate(wire_tools_resp)
    assert isinstance(parsed_tools_resp.result, MCPToolsListResultDTO)
    assert len(parsed_tools_resp.result.tools) == 1
    discovered: MCPDiscoveredToolWireDTO = parsed_tools_resp.result.tools[0]
    assert discovered.name == "mcp_search"
    assert discovered.input_schema.additional_properties is False

    wire_call_resp = {
        "jsonrpc": "2.0",
        "id": 3,
        "result": {
            "content": [{"type": "text", "text": "Result payload", "mimeType": "text/plain"}],
            "isError": False,
        },
    }
    parsed_call_resp = MCPJsonRpcResponseDTO.model_validate(wire_call_resp)
    assert isinstance(parsed_call_resp.result, MCPToolCallResultDTO)
    assert parsed_call_resp.result.is_error is False
    block: MCPContentBlockDTO = parsed_call_resp.result.content[0]
    assert block.mime_type == "text/plain"

    init_res = MCPInitializeResultDTO(protocol_version="2025-03-26")
    assert init_res.protocol_version == "2025-03-26"

    err_dto = MCPJsonRpcErrorDTO(code=-32601, message="Method not found")
    assert err_dto.code == -32601


def test_mcp_dto_missing_required() -> None:
    """Test validation errors when required arguments are missing."""
    empty_payload: dict[str, str] = {}
    with pytest.raises(ValidationError):
        _ = ParsedMCPToolAliasDTO.model_validate(empty_payload)

    with pytest.raises(ValidationError):
        _ = MCPToolDeclarationDTO.model_validate(empty_payload)


def test_parsed_mcp_tool_alias_dto_negative_extra_forbid() -> None:
    """Test ParsedMCPToolAliasDTO rejects extra forbidden fields."""
    invalid_req: dict[str, str] = {"gateway_slug": "gw", "tool_id": "t1", "extra_field": "bad"}
    with pytest.raises(ValidationError):
        ParsedMCPToolAliasDTO.model_validate(invalid_req)


def test_mcp_function_definition_dto_negative_extra_forbid() -> None:
    """Test MCPFunctionDefinitionDTO rejects extra forbidden fields."""
    invalid_fn = {
        "name": "fn",
        "description": "desc",
        "parameters": {},
        "extra_field": "bad",
    }
    with pytest.raises(ValidationError):
        MCPFunctionDefinitionDTO.model_validate(invalid_fn)


def test_parsed_mcp_tool_alias_dto_negative_strict_type() -> None:
    """Test strict type validation rejects integer for tool_id string."""
    invalid_type_payload: dict[str, str | int] = {"gateway_slug": "gw", "tool_id": 12345}
    with pytest.raises(ValidationError):
        ParsedMCPToolAliasDTO.model_validate(invalid_type_payload)


def test_mcp_tool_invocation_dto_negative_invalid_gateway_id() -> None:
    """Test MCPToolInvocationDTO rejects non-opaque gateway_id."""
    with pytest.raises(ValidationError):
        MCPToolInvocationDTO(
            gateway_id="invalid_id",
            gateway_slug="gw",
            tool_id="t1",
            namespaced_alias="gw__t1",
            arguments={},
        )


def test_mcp_validation_context_dto_positive_and_negative() -> None:
    """Test MCPValidationContextDTO positive hydration and negative strict/extra boundaries."""
    doc = SourceDocumentContext(
        opaque_id="doc_8172bda70c8641c5",
        text_content="Evidence body text.",
        display_name="Source A",
    )
    ctx = MCPValidationContextDTO(
        strictness_level=85.5,
        query_guidance="Use exact search keywords.",
        mcp_source_texts={"mcp_0": "Fetched web text."},
        source_documents=[doc],
        alias_registry={"src_0": "doc_8172bda70c8641c5"},
    )
    assert ctx.strictness_level == 85.5
    assert ctx.query_guidance == "Use exact search keywords."
    assert ctx.mcp_source_texts["mcp_0"] == "Fetched web text."
    assert len(ctx.source_documents) == 1
    assert ctx.alias_registry["src_0"] == "doc_8172bda70c8641c5"

    with pytest.raises(ValidationError):
        MCPValidationContextDTO.model_validate({"strictness_level": "not_a_number"})

    with pytest.raises(ValidationError):
        MCPValidationContextDTO.model_validate({"unexpected_key": True})
