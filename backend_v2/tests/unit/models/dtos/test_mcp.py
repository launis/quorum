"""Unit tests for MCP DTOs."""

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
    MCPStructuredErrorDetailDTO,
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
    raw_prop_json = (
        '{"type":"object","title":"FilterOptions","description":"Nested object filter",'
        '"enum":["a","b"],"additionalProperties":false,'
        '"properties":{"limit":{"type":"integer","description":"Max items"}},'
        '"required":["limit"]}'
    )
    prop = MCPToolSchemaPropertyDTO.model_validate_json(raw_prop_json)
    assert prop.type == JSONSchemaPropertyType.OBJECT
    assert prop.title == "FilterOptions"
    assert prop.enum_values == ["a", "b"]
    assert prop.additional_properties is False
    assert prop.properties is not None
    assert prop.properties["limit"].type == JSONSchemaPropertyType.INTEGER

    dumped_json = prop.model_dump_json()
    rehydrated = MCPToolSchemaPropertyDTO.model_validate_json(dumped_json)
    assert rehydrated == prop


def test_parsed_mcp_tool_alias_and_invocation_dtos() -> None:
    """Test ParsedMCPToolAliasDTO, MCPToolDescriptorDTO, and MCPToolInvocationDTO."""
    alias = ParsedMCPToolAliasDTO(gateway_slug="tavily_gw", tool_id="search")
    assert alias.gateway_slug == "tavily_gw"
    assert alias.tool_id == "search"

    descriptor = MCPToolDescriptorDTO(
        gateway_id="sys_0195f3a00000700080008172bda70c86",
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
        gateway_id="sys_0195f3a00000700080008172bda70c86",
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

    wire_tools_resp_json = (
        '{"jsonrpc":"2.0","id":2,"result":{"tools":[{"name":"mcp_search",'
        '"description":"Search via MCP","inputSchema":{"type":"object",'
        '"properties":{"query":{"type":"string"}},"required":["query"],'
        '"additionalProperties":false}}]}}'
    )
    parsed_tools_resp = MCPJsonRpcResponseDTO.model_validate_json(wire_tools_resp_json)
    assert isinstance(parsed_tools_resp.result, MCPToolsListResultDTO)
    assert len(parsed_tools_resp.result.tools) == 1
    discovered: MCPDiscoveredToolWireDTO = parsed_tools_resp.result.tools[0]
    assert discovered.name == "mcp_search"
    assert discovered.input_schema.additional_properties is False

    wire_call_resp_json = (
        '{"jsonrpc":"2.0","id":3,"result":{"content":['
        '{"type":"text","text":"Result payload","mimeType":"text/plain"}],'
        '"isError":false}}'
    )
    parsed_call_resp = MCPJsonRpcResponseDTO.model_validate_json(wire_call_resp_json)
    assert isinstance(parsed_call_resp.result, MCPToolCallResultDTO)
    assert parsed_call_resp.result.is_error is False
    block: MCPContentBlockDTO = parsed_call_resp.result.content[0]
    assert block.mime_type == "text/plain"

    init_res = MCPInitializeResultDTO(
        protocol_version="2025-03-26",
        server_info=MCPServerInfoDTO(name="exa", icons=[]),
        capabilities={},
    )
    assert init_res.protocol_version == "2025-03-26"

    err_dto = MCPJsonRpcErrorDTO(code=-32601, message="Method not found")
    assert err_dto.code == -32601


def test_mcp_dto_missing_required() -> None:
    """Test validation errors when required arguments are missing."""
    with pytest.raises(ValidationError):
        _ = ParsedMCPToolAliasDTO.model_validate_json("{}")

    with pytest.raises(ValidationError):
        _ = MCPToolDeclarationDTO.model_validate_json("{}")


def test_parsed_mcp_tool_alias_dto_negative_extra_forbid() -> None:
    """Test ParsedMCPToolAliasDTO rejects extra forbidden fields."""
    with pytest.raises(ValidationError):
        ParsedMCPToolAliasDTO.model_validate_json('{"gateway_slug":"gw","tool_id":"t1","extra_field":"bad"}')


def test_mcp_function_definition_dto_negative_extra_forbid() -> None:
    """Test MCPFunctionDefinitionDTO rejects extra forbidden fields."""
    with pytest.raises(ValidationError):
        MCPFunctionDefinitionDTO.model_validate_json(
            '{"name":"fn","description":"desc","parameters":{},"extra_field":"bad"}'
        )


def test_parsed_mcp_tool_alias_dto_negative_strict_type() -> None:
    """Test strict type validation rejects integer for tool_id string."""
    with pytest.raises(ValidationError):
        ParsedMCPToolAliasDTO.model_validate_json('{"gateway_slug":"gw","tool_id":12345}')


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
        opaque_id="doc_0195f3a0000070088172bda70c8641c5",
        text_content="Evidence body text.",
        display_name="Source A",
    )
    ctx = MCPValidationContextDTO(
        strictness_level=85.5,
        query_guidance="Use exact search keywords.",
        mcp_source_texts={"mcp_0": "Fetched web text."},
        source_documents=[doc],
        alias_registry={"src_0": "doc_0195f3a0000070088172bda70c8641c5"},
    )
    assert ctx.strictness_level == 85.5
    assert ctx.query_guidance == "Use exact search keywords."
    assert ctx.mcp_source_texts["mcp_0"] == "Fetched web text."
    assert len(ctx.source_documents) == 1
    assert ctx.alias_registry["src_0"] == "doc_0195f3a0000070088172bda70c8641c5"

    with pytest.raises(ValidationError):
        MCPValidationContextDTO.model_validate_json('{"strictness_level":"not_a_number"}')

    with pytest.raises(ValidationError):
        MCPValidationContextDTO.model_validate_json('{"unexpected_key":true}')


def test_mcp_initialize_result_dto_with_complex_server_info_metadata() -> None:
    """Regression test for serverInfo metadata with icons.

    Verify MCPInitializeResultDTO and MCPJsonRpcResponseDTO validate serverInfo
    with icons and metadata. Exa AI and other MCP servers return serverInfo with
    lists of icons and strings, which must not fail validation with string_type errors.
    """
    raw_response_json = (
        '{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05",'
        '"capabilities":{"tools":{"listChanged":true},"prompts":{"listChanged":true},'
        '"resources":{"listChanged":true}},'
        '"serverInfo":{"name":"exa-search-server","title":"Exa","version":"3.5.0",'
        '"description":"Exa web search, page fetching and research-agent tools for AI agents over MCP.",'
        '"websiteUrl":"https://exa.ai",'
        '"icons":[{"src":"https://exa.ai/images/logo/exa-logomark-blue.svg","mimeType":"image/svg+xml","sizes":["any"]},'
        '{"src":"https://exa.ai/images/favicon-32x32.png","mimeType":"image/png","sizes":["32x32"]}]},'
        '"instructions":"Only use tools returned by tools/list."}}'
    )
    parsed = MCPJsonRpcResponseDTO.model_validate_json(raw_response_json)
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
        MCPServerInfoDTO.model_validate_json('{"name":"exa","unexpected_field":"forbidden"}')

    with pytest.raises(ValidationError):
        MCPIconDTO.model_validate_json('{"src":"https://exa.ai/icon.png","unexpected_icon_field":true}')

    with pytest.raises(ValidationError):
        MCPIconDTO.model_validate_json('{"mimeType":"image/png"}')

    with pytest.raises(ValidationError):
        MCPIconDTO.model_validate_json('{"src":12345}')


def test_mcp_tools_list_result_dto_with_exa_metadata() -> None:
    """Regression test for Exa AI tools/list response frame validation.

    Verify MCPToolsListResultDTO and MCPJsonRpcResponseDTO validate tool entries
    containing $schema, minLength, maxLength, and execution metadata without failing
    with extra_forbidden validation errors.
    """
    raw_response_json = (
        '{"jsonrpc":"2.0","id":2,"result":{"tools":['
        '{"name":"web_search_exa","title":"Web Search","description":"Search the web for any topic.",'
        '"inputSchema":{"type":"object","properties":{'
        '"query":{"type":"string","minLength":1,"description":"Natural language search query."},'
        '"numResults":{"type":"number","description":"Number of search results."},'
        '"objective":{"type":"string","minLength":1,"maxLength":4096,"description":"Goal for this search turn."}'
        '},"required":["query","objective"],"additionalProperties":false,"$schema":"http://json-schema.org/draft-07/schema#"},'
        '"annotations":{"readOnlyHint":true,"destructiveHint":false,"openWorldHint":true,"idempotentHint":true},'
        '"execution":{"taskSupport":"forbidden"}},'
        '{"name":"web_fetch_exa","title":"Fetch Web Pages","description":"Read a webpage\'s full content as clean markdown.",'
        '"inputSchema":{"type":"object","properties":{'
        '"urls":{"type":"array","items":{"type":"string"},"description":"URLs to read."},'
        '"maxCharacters":{"type":"number","minimum":1,"description":"Maximum characters to extract."}'
        '},"required":["urls"],"additionalProperties":false,"$schema":"http://json-schema.org/draft-07/schema#"},'
        '"annotations":{"readOnlyHint":true,"destructiveHint":false,"openWorldHint":true,"idempotentHint":true},'
        '"execution":{"taskSupport":"forbidden"}}'
        "]}}"
    )
    parsed = MCPJsonRpcResponseDTO.model_validate_json(raw_response_json)
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
        MCPToolExecutionDTO.model_validate_json('{"taskSupport":"forbidden","unknownField":"invalid"}')

    with pytest.raises(ValidationError):
        MCPToolInputSchemaDTO.model_validate_json('{"type":"object","unexpectedSchemaField":true}')

    with pytest.raises(ValidationError):
        MCPToolSchemaPropertyDTO.model_validate_json('{"type":"string","minLength":-1}')

    with pytest.raises(ValidationError):
        MCPToolSchemaPropertyDTO.model_validate_json('{"type":"string","maxLength":-5}')


def test_mcp_tool_call_result_with_content_execution_meta() -> None:
    """Verify MCPToolCallResultDTO and MCPJsonRpcResponseDTO accept content _meta from search tools."""
    wire_call_resp_json = (
        '{"jsonrpc":"2.0","id":1,"result":{"content":['
        '{"type":"text","text":"Search results from Exa","_meta":{"searchTime":906.5}}],'
        '"isError":false,"_meta":{"searchTime":906.5}}}'
    )
    parsed = MCPJsonRpcResponseDTO.model_validate_json(wire_call_resp_json)
    assert isinstance(parsed.result, MCPToolCallResultDTO)
    assert parsed.result.content[0].meta is not None
    assert parsed.result.content[0].meta.search_time == 906.5


def test_mcp_structured_content_and_meta_dtos_positive_and_negative() -> None:
    """Test FastMCPMetaDTO, MCPToolMetaDTO, MCPExecutionMetaDTO, MCPSearchResultItemDTO, and MCPStructuredContentDTO."""
    tool_meta = MCPToolMetaDTO(fastmcp=FastMCPMetaDTO(tags=["search", "web"]))
    assert tool_meta.fastmcp is not None
    assert tool_meta.fastmcp.tags == ["search", "web"]

    annotations = MCPToolAnnotationsDTO.model_validate_json(
        '{"destructiveHint":false,"readOnlyHint":true,"openInNewTab":true,"idempotentHint":true,"openWorldHint":true}'
    )
    assert annotations.open_in_new_tab is True

    exec_meta = MCPExecutionMetaDTO.model_validate_json(
        '{"searchTime":120.5,"responseTime":0.42,"requestId":"req_123","totalCost":0.005,'
        '"progress":100,"total":10,"ai.exa/rateLimited":false}'
    )
    assert exec_meta.cost == 0.005
    assert exec_meta.rate_limited is False

    structured = MCPStructuredContentDTO.model_validate_json(
        '{"query":"quorum architecture","followUpQuestions":["What is Quorum V2?"],'
        '"answer":"Synthesized answer.","summary":"Summary text.","description":"Description text.",'
        '"text":"Body text.","message":"OK","finding":"Key finding.","images":["https://example.com/img.png"],'
        '"results":[{"id":"res_1","url":"https://example.com/doc","title":"Quorum Doc",'
        '"content":"Extracted content.","snippet":"Short snippet.","text":"Plain text.",'
        '"summary":"Item summary.","rawContent":"<html></html>","score":0.98}],'
        '"authMode":"bearer","responseTime":0.35,"requestId":"req_abc"}'
    )
    assert structured.query == "quorum architecture"
    assert structured.follow_up_questions == ["What is Quorum V2?"]
    assert len(structured.results) == 1
    assert structured.results[0].raw_content == "<html></html>"
    assert structured.results[0].score == 0.98

    with pytest.raises(ValidationError):
        FastMCPMetaDTO.model_validate_json('{"tags":"not_a_list"}')

    with pytest.raises(ValidationError):
        MCPToolMetaDTO.model_validate_json('{"unexpected":true}')

    with pytest.raises(ValidationError):
        MCPExecutionMetaDTO.model_validate_json('{"cost":"not_a_float"}')

    with pytest.raises(ValidationError):
        MCPSearchResultItemDTO.model_validate_json('{"score":"not_a_number"}')

    with pytest.raises(ValidationError):
        MCPStructuredContentDTO.model_validate_json('{"unknown_key":"forbidden"}')

    err_structured = MCPStructuredContentDTO.model_validate_json(
        '{"error":"Upstream quota exceeded","statusCode":429,'
        '"detail":{"error":"Rate limit reached","message":"Retry after 60s"},'
        '"documentationUrl":"https://docs.example.com/errors/429"}'
    )
    assert err_structured.error == "Upstream quota exceeded"
    assert err_structured.status == 429
    assert isinstance(err_structured.detail, MCPStructuredErrorDetailDTO)
    assert err_structured.detail.error == "Rate limit reached"
    assert err_structured.detail.message == "Retry after 60s"
    assert err_structured.documentation == "https://docs.example.com/errors/429"

    with pytest.raises(ValidationError):
        MCPStructuredErrorDetailDTO.model_validate_json('{"error":"bad","extra_key":"forbidden"}')

    with pytest.raises(ValidationError):
        MCPStructuredErrorDetailDTO.model_validate_json('{"error":12345}')


def test_mcp_tools_list_result_dto_with_tavily_research_max_items_and_const_positive_and_negative() -> None:
    """Verify MCPJsonRpcResponseDTO parses tools/list schemas with minItems, maxItems, and const in anyOf."""
    raw_sse_jsonrpc_frame = (
        '{"jsonrpc":"2.0","id":2,"result":{"tools":[{"name":"tavily_research",'
        '"description":"Perform comprehensive research on a given topic.",'
        '"inputSchema":{"type":"object","properties":{"input":{"type":"string",'
        '"description":"A comprehensive description of the research task"},'
        '"files":{"anyOf":[{"items":{"properties":{"name":{"type":"string"},'
        '"data":{"type":"string"},"type":{"const":"base64","default":"base64",'
        '"type":"string"}},"required":["name","data"],"type":"object"},'
        '"minItems":1,"maxItems":5,"type":"array"},{"type":"null"}],'
        '"default":null,"description":"Base64 .txt/.md/.json attachments"}},'
        '"required":["input"]}}]}}'
    )
    parsed = MCPJsonRpcResponseDTO.model_validate_json(raw_sse_jsonrpc_frame)
    assert isinstance(parsed.result, MCPToolsListResultDTO)
    assert len(parsed.result.tools) == 1
    files_prop = parsed.result.tools[0].input_schema.properties["files"]
    assert files_prop.any_of is not None
    array_branch = files_prop.any_of[0]
    assert array_branch.min_items == 1
    assert array_branch.max_items == 5
    assert array_branch.items is not None
    assert array_branch.items.properties is not None
    type_prop = array_branch.items.properties["type"]
    assert type_prop.const == "base64"

    # Negative 1 (BVA min-1): minItems < 0 and maxItems < 0 must raise ValidationError
    with pytest.raises(ValidationError):
        MCPToolSchemaPropertyDTO.model_validate_json('{"type":"array","minItems":-1}')

    with pytest.raises(ValidationError):
        MCPToolSchemaPropertyDTO.model_validate_json('{"type":"array","maxItems":-1}')

    # Negative 2 (Type Violation): non-scalar const value (dict) must raise ValidationError
    with pytest.raises(ValidationError):
        MCPToolSchemaPropertyDTO.model_validate_json('{"type":"string","const":{"nested":"invalid"}}')


def test_mcp_tool_schema_draft_2020_12_vocabulary_and_jina_format_positive_and_negative() -> None:
    """Verify MCPToolSchemaPropertyDTO and MCPToolInputSchemaDTO parse JSON Schema Draft 2020-12 keywords."""
    jina_frame = (
        '{"jsonrpc":"2.0","id":2,"result":{"tools":[{"name":"read_url",'
        '"description":"Extract clean content from a web URL.",'
        '"inputSchema":{"type":"object",'
        '"$defs":{"UrlRef":{"type":"string","format":"uri"}},'
        '"properties":{'
        '"url":{"anyOf":['
        '{"type":"string","format":"uri","pattern":"^https?://",'
        '"examples":["https://jina.ai"],"deprecated":false,"readOnly":false,"writeOnly":false},'
        '{"type":"array","items":{"$ref":"#/$defs/UrlRef"},"uniqueItems":true,'
        '"minItems":1,"maxItems":10}'
        ']},"score_step":{"type":"number","exclusiveMinimum":0.0,'
        '"exclusiveMaximum":100.0,"multipleOf":0.5,'
        '"oneOf":[{"type":"number"},{"type":"integer"}],'
        '"allOf":[{"type":"number"}]}},'
        '"required":["url"],"additionalProperties":false,'
        '"$schema":"http://json-schema.org/draft-07/schema#"}}]}}'
    )
    parsed = MCPJsonRpcResponseDTO.model_validate_json(jina_frame)
    assert isinstance(parsed.result, MCPToolsListResultDTO)
    tool = parsed.result.tools[0]
    assert tool.input_schema.defs is not None
    assert tool.input_schema.defs["UrlRef"].format == "uri"

    url_prop = tool.input_schema.properties["url"]
    assert url_prop.any_of is not None
    assert url_prop.any_of[0].format == "uri"
    assert url_prop.any_of[0].pattern == "^https?://"
    assert url_prop.any_of[0].examples == ["https://jina.ai"]
    assert url_prop.any_of[0].deprecated is False
    assert url_prop.any_of[0].read_only is False
    assert url_prop.any_of[0].write_only is False
    assert url_prop.any_of[1].unique_items is True
    assert url_prop.any_of[1].items is not None
    assert url_prop.any_of[1].items.ref == "#/$defs/UrlRef"

    score_prop = tool.input_schema.properties["score_step"]
    assert score_prop.exclusive_minimum == 0.0
    assert score_prop.exclusive_maximum == 100.0
    assert score_prop.multiple_of == 0.5
    assert score_prop.one_of is not None
    assert len(score_prop.one_of) == 2
    assert score_prop.all_of is not None
    assert len(score_prop.all_of) == 1

    # Negative 1 (BVA): multipleOf <= 0 must raise ValidationError
    with pytest.raises(ValidationError):
        MCPToolSchemaPropertyDTO.model_validate_json('{"type":"number","multipleOf":0}')

    with pytest.raises(ValidationError):
        MCPToolSchemaPropertyDTO.model_validate_json('{"type":"number","multipleOf":-2}')

    # Negative 2 (Extra Forbid): unknown vendor keyword must still raise ValidationError
    with pytest.raises(ValidationError):
        MCPToolSchemaPropertyDTO.model_validate_json('{"type":"string","nonStandardVendorKey":true}')
