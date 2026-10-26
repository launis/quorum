"""Unit tests for MCP DTOs."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.mcp import (
    FastMCPMetaDTO,
    MCPCapabilityConfigDTO,
    MCPContentBlockDTO,
    MCPDiscoveredToolWireDTO,
    MCPExecutionMetaDTO,
    MCPFunctionDefinitionDTO,
    MCPIconDTO,
    MCPInitializeClientInfoDTO,
    MCPInitializeParamsDTO,
    MCPInitializeResultDTO,
    MCPJsonRpcErrorDTO,
    MCPJsonRpcRequestDTO,
    MCPJsonRpcResponseDTO,
    MCPSearchResultItemDTO,
    MCPServerInfoDTO,
    MCPStructuredContentDTO,
    MCPToolAnnotationsDTO,
    MCPToolCallParamsDTO,
    MCPToolCallResultDTO,
    MCPToolDeclarationDTO,
    MCPToolDescriptorDTO,
    MCPToolExecutionDTO,
    MCPToolInputSchemaDTO,
    MCPToolInvocationDTO,
    MCPToolMetaDTO,
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
        input_schema=MCPToolInputSchemaDTO(properties={}, required=[]),
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

    init_res = MCPInitializeResultDTO(
        protocol_version="2025-03-26",
        server_info=MCPServerInfoDTO(icons=[]),
        capabilities={},
    )
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


def test_mcp_initialize_result_dto_with_complex_server_info_metadata() -> None:
    """Regression test for serverInfo metadata with icons.

    Verify MCPInitializeResultDTO and MCPJsonRpcResponseDTO validate serverInfo
    with icons and metadata. Exa AI and other MCP servers return serverInfo with
    lists of icons and strings, which must not fail validation with string_type errors.
    """
    raw_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {"listChanged": True},
                "prompts": {"listChanged": True},
                "resources": {"listChanged": True},
            },
            "serverInfo": {
                "name": "exa-search-server",
                "title": "Exa",
                "version": "3.5.0",
                "description": "Exa web search, page fetching and research-agent tools for AI agents over MCP.",
                "websiteUrl": "https://exa.ai",
                "icons": [
                    {
                        "src": "https://exa.ai/images/logo/exa-logomark-blue.svg",
                        "mimeType": "image/svg+xml",
                        "sizes": ["any"],
                    },
                    {
                        "src": "https://exa.ai/images/favicon-32x32.png",
                        "mimeType": "image/png",
                        "sizes": ["32x32"],
                    },
                ],
            },
            "instructions": "Only use tools returned by tools/list.",
        },
    }
    parsed = MCPJsonRpcResponseDTO.model_validate(raw_response)
    assert isinstance(parsed.result, MCPInitializeResultDTO)
    assert parsed.result.server_info.name == "exa-search-server"
    assert parsed.result.server_info.title == "Exa"
    assert parsed.result.server_info.version == "3.5.0"
    assert parsed.result.server_info.website_url == "https://exa.ai"
    assert len(parsed.result.server_info.icons) == 2
    assert parsed.result.server_info.icons[0].src == "https://exa.ai/images/logo/exa-logomark-blue.svg"
    assert parsed.result.server_info.icons[0].mime_type == "image/svg+xml"
    assert parsed.result.server_info.icons[0].sizes == ["any"]

    with pytest.raises(ValidationError):
        MCPServerInfoDTO.model_validate({"name": "exa", "unexpected_field": "forbidden"})

    with pytest.raises(ValidationError):
        MCPIconDTO.model_validate({"src": "https://exa.ai/icon.png", "unexpected_icon_field": True})

    with pytest.raises(ValidationError):
        MCPIconDTO.model_validate({"mimeType": "image/png"})

    with pytest.raises(ValidationError):
        MCPIconDTO.model_validate({"src": 12345})


def test_mcp_tools_list_result_dto_with_exa_metadata() -> None:
    """Regression test for Exa AI tools/list response frame validation.

    Verify MCPToolsListResultDTO and MCPJsonRpcResponseDTO validate tool entries
    containing $schema, minLength, maxLength, and execution metadata without failing
    with extra_forbidden validation errors.
    """
    raw_response = {
        "jsonrpc": "2.0",
        "id": 2,
        "result": {
            "tools": [
                {
                    "name": "web_search_exa",
                    "title": "Web Search",
                    "description": "Search the web for any topic.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "minLength": 1,
                                "description": "Natural language search query.",
                            },
                            "numResults": {
                                "type": "number",
                                "description": "Number of search results.",
                            },
                            "objective": {
                                "type": "string",
                                "minLength": 1,
                                "maxLength": 4096,
                                "description": "Goal for this search turn.",
                            },
                        },
                        "required": ["query", "objective"],
                        "additionalProperties": False,
                        "$schema": "http://json-schema.org/draft-07/schema#",
                    },
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "openWorldHint": True,
                        "idempotentHint": True,
                    },
                    "execution": {"taskSupport": "forbidden"},
                },
                {
                    "name": "web_fetch_exa",
                    "title": "Fetch Web Pages",
                    "description": "Read a webpage's full content as clean markdown.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "urls": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "URLs to read.",
                            },
                            "maxCharacters": {
                                "type": "number",
                                "minimum": 1,
                                "description": "Maximum characters to extract.",
                            },
                        },
                        "required": ["urls"],
                        "additionalProperties": False,
                        "$schema": "http://json-schema.org/draft-07/schema#",
                    },
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "openWorldHint": True,
                        "idempotentHint": True,
                    },
                    "execution": {"taskSupport": "forbidden"},
                },
            ]
        },
    }
    parsed = MCPJsonRpcResponseDTO.model_validate(raw_response)
    assert isinstance(parsed.result, MCPToolsListResultDTO)
    assert len(parsed.result.tools) == 2

    tool_0 = parsed.result.tools[0]
    assert tool_0.name == "web_search_exa"
    assert tool_0.input_schema.schema_uri == "http://json-schema.org/draft-07/schema#"
    assert tool_0.input_schema.properties["query"].min_length == 1
    assert tool_0.input_schema.properties["objective"].max_length == 4096
    assert tool_0.execution is not None
    assert tool_0.execution.task_support == "forbidden"

    tool_1 = parsed.result.tools[1]
    assert tool_1.name == "web_fetch_exa"
    assert tool_1.input_schema.schema_uri == "http://json-schema.org/draft-07/schema#"
    assert tool_1.execution is not None
    assert tool_1.execution.task_support == "forbidden"

    with pytest.raises(ValidationError):
        MCPToolExecutionDTO.model_validate({"taskSupport": "forbidden", "unknownField": "invalid"})

    with pytest.raises(ValidationError):
        MCPToolInputSchemaDTO.model_validate({"type": "object", "unexpectedSchemaField": True})

    with pytest.raises(ValidationError):
        MCPToolSchemaPropertyDTO.model_validate({"type": "string", "minLength": -1})

    with pytest.raises(ValidationError):
        MCPToolSchemaPropertyDTO.model_validate({"type": "string", "maxLength": -5})


def test_mcp_tool_call_result_with_content_execution_meta() -> None:
    """Verify MCPToolCallResultDTO and MCPJsonRpcResponseDTO accept content _meta from search tools."""
    wire_call_resp = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "content": [
                {
                    "type": "text",
                    "text": "Search results from Exa",
                    "_meta": {"searchTime": 906.5},
                }
            ],
            "isError": False,
            "_meta": {"searchTime": 906.5},
        },
    }
    parsed = MCPJsonRpcResponseDTO.model_validate(wire_call_resp)
    assert isinstance(parsed.result, MCPToolCallResultDTO)
    assert parsed.result.content[0].meta is not None
    assert parsed.result.content[0].meta.search_time == 906.5


def test_mcp_structured_content_and_meta_dtos_positive_and_negative() -> None:
    """Test FastMCPMetaDTO, MCPToolMetaDTO, MCPExecutionMetaDTO, MCPSearchResultItemDTO, and MCPStructuredContentDTO."""
    tool_meta = MCPToolMetaDTO(fastmcp=FastMCPMetaDTO(tags=["search", "web"]))
    assert tool_meta.fastmcp is not None
    assert tool_meta.fastmcp.tags == ["search", "web"]

    annotations = MCPToolAnnotationsDTO.model_validate(
        {
            "destructiveHint": False,
            "readOnlyHint": True,
            "openInNewTab": True,
            "idempotentHint": True,
            "openWorldHint": True,
        }
    )
    assert annotations.open_in_new_tab is True

    exec_meta = MCPExecutionMetaDTO.model_validate(
        {
            "searchTime": 120.5,
            "responseTime": 0.42,
            "requestId": "req_123",
            "totalCost": 0.005,
            "progress": 100,
            "total": 10,
            "ai.exa/rateLimited": False,
        }
    )
    assert exec_meta.cost == 0.005
    assert exec_meta.rate_limited is False

    structured = MCPStructuredContentDTO.model_validate(
        {
            "query": "quorum architecture",
            "followUpQuestions": ["What is Quorum V2?"],
            "answer": "Synthesized answer.",
            "summary": "Summary text.",
            "description": "Description text.",
            "text": "Body text.",
            "message": "OK",
            "finding": "Key finding.",
            "images": ["https://example.com/img.png"],
            "results": [
                {
                    "id": "res_1",
                    "url": "https://example.com/doc",
                    "title": "Quorum Doc",
                    "content": "Extracted content.",
                    "snippet": "Short snippet.",
                    "text": "Plain text.",
                    "summary": "Item summary.",
                    "rawContent": "<html></html>",
                    "score": 0.98,
                }
            ],
            "authMode": "bearer",
            "responseTime": 0.35,
            "requestId": "req_abc",
        }
    )
    assert structured.query == "quorum architecture"
    assert structured.follow_up_questions == ["What is Quorum V2?"]
    assert len(structured.results) == 1
    assert structured.results[0].raw_content == "<html></html>"
    assert structured.results[0].score == 0.98

    with pytest.raises(ValidationError):
        FastMCPMetaDTO.model_validate({"tags": "not_a_list"})

    with pytest.raises(ValidationError):
        MCPToolMetaDTO.model_validate({"unexpected": True})

    with pytest.raises(ValidationError):
        MCPExecutionMetaDTO.model_validate({"cost": "not_a_float"})

    with pytest.raises(ValidationError):
        MCPSearchResultItemDTO.model_validate({"score": "not_a_number"})

    with pytest.raises(ValidationError):
        MCPStructuredContentDTO.model_validate({"unknown_key": "forbidden"})

