"""Data Transfer Objects for MCP Tools, recursive JSON Schema AST, and JSON-RPC 2.0 wire envelopes."""

from typing import Annotated, Literal

from pydantic import AliasChoices, ConfigDict, Field

from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX, V2CoreBase
from backend_v2.models.dtos.quote_evidence import SourceDocumentContext
from backend_v2.models.enums import (
    LaxJSONSchemaPropertyType,
    LaxToolCapability,
    ToolCapability,
)

__all__ = [
    "FastMCPMetaDTO",
    "MCPArgumentScalar",
    "MCPArgumentValue",
    "MCPCapabilityConfigDTO",
    "MCPContentBlockDTO",
    "MCPDiscoveredToolWireDTO",
    "MCPFunctionDefinitionDTO",
    "MCPIconDTO",
    "MCPInitializeClientInfoDTO",
    "MCPInitializeParamsDTO",
    "MCPInitializeResultDTO",
    "MCPJsonRpcErrorDTO",
    "MCPJsonRpcRequestDTO",
    "MCPJsonRpcResponseDTO",
    "MCPSearchResultItemDTO",
    "MCPServerInfoDTO",
    "MCPStructuredContentDTO",
    "MCPToolAnnotationsDTO",
    "MCPToolCallParamsDTO",
    "MCPToolCallResultDTO",
    "MCPToolDeclarationDTO",
    "MCPToolDescriptorDTO",
    "MCPToolExecutionDTO",
    "MCPToolInputSchemaDTO",
    "MCPToolInvocationDTO",
    "MCPToolMetaDTO",
    "MCPToolSchemaPropertyDTO",
    "MCPToolsListResultDTO",
    "MCPValidationContextDTO",
    "ParsedMCPToolAliasDTO",
]

type MCPArgumentScalar = str | int | float | bool
type MCPArgumentValue = MCPArgumentScalar | list[str] | list[int] | list[float] | list[bool]


class MCPValidationContextDTO(V2CoreBase):
    """Typed validation context for MCP tool loop execution and quote anchoring.

    Attributes:
        strictness_level: Validation strictness threshold (0-100).
        query_guidance: Optional domain-specific rule injected into extraction prompts.
        mcp_source_texts: Mapping of MCP source aliases to formatted evidence text.
        source_documents: Optional source document contexts for quote verification.
        alias_registry: Optional alias registry mapping short aliases to opaque IDs.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    strictness_level: Annotated[
        int | float,
        Field(default=100, description="Validation strictness threshold (0-100)."),
    ] = 100
    query_guidance: Annotated[
        str | None,
        Field(default=None, description="Optional domain-specific rule injected into extraction prompts."),
    ] = None
    mcp_source_texts: Annotated[
        dict[str, str],
        Field(default_factory=dict, description="Mapping of MCP source aliases to formatted evidence text."),
    ]
    source_documents: Annotated[
        list[SourceDocumentContext],
        Field(default_factory=list, description="Optional source document contexts for quote verification."),
    ]
    alias_registry: Annotated[
        dict[str, str],
        Field(default_factory=dict, description="Optional alias registry mapping short aliases to opaque IDs."),
    ]


class MCPToolSchemaPropertyDTO(V2CoreBase):
    """Recursive JSON Schema property definition for an MCP tool parameter.

    Attributes:
        type: JSON Schema primitive or structural property type.
        title: Optional JSON Schema property title emitted by FastMCP/Pydantic/Zod servers.
        description: Property description for LLM function calling.
        enum_values: Optional list of allowed string enum values.
        items: Recursive item schema when type is array.
        properties: Recursive property mapping when type is object.
        required: Optional list of required nested property keys when type is object.
        additional_properties: Optional flag restricting additional properties on nested objects.
        default: Optional default value for this property.
        minimum: Optional minimum numeric value.
        maximum: Optional maximum numeric value.
        any_of: Optional list of alternative sub-schemas (anyOf).
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, populate_by_name=True)

    type: Annotated[LaxJSONSchemaPropertyType | None, Field(default=None, description="JSON Schema property type.")] = (
        None
    )
    title: Annotated[
        str | None,
        Field(default=None, description="Optional JSON Schema property title emitted by FastMCP/Pydantic/Zod servers."),
    ] = None
    description: Annotated[str, Field(default="", description="Property description.")] = ""
    enum_values: Annotated[
        list[str] | None,
        Field(
            default=None,
            validation_alias=AliasChoices("enum", "enum_values"),
            description="Allowed string enum values.",
        ),
    ] = None
    items: Annotated[
        MCPToolSchemaPropertyDTO | None,
        Field(default=None, description="Recursive item schema for array properties."),
    ] = None
    properties: Annotated[
        dict[str, MCPToolSchemaPropertyDTO] | None,
        Field(default=None, description="Recursive nested properties for object properties."),
    ] = None
    required: Annotated[
        list[str] | None,
        Field(default=None, description="Required nested property names."),
    ] = None
    additional_properties: Annotated[
        bool | None,
        Field(
            default=None,
            validation_alias=AliasChoices("additionalProperties", "additional_properties"),
            description="Whether additional nested object properties are allowed.",
        ),
    ] = None
    default: Annotated[
        MCPArgumentValue | None,
        Field(default=None, description="Optional default value for this property."),
    ] = None
    minimum: Annotated[
        int | float | None,
        Field(default=None, description="Optional minimum numeric value."),
    ] = None
    maximum: Annotated[
        int | float | None,
        Field(default=None, description="Optional maximum numeric value."),
    ] = None
    min_length: Annotated[
        int | None,
        Field(
            default=None,
            ge=0,
            validation_alias=AliasChoices("minLength", "min_length"),
            description="Minimum string length constraint.",
        ),
    ] = None
    max_length: Annotated[
        int | None,
        Field(
            default=None,
            ge=0,
            validation_alias=AliasChoices("maxLength", "max_length"),
            description="Maximum string length constraint.",
        ),
    ] = None
    any_of: Annotated[
        list[MCPToolSchemaPropertyDTO] | None,
        Field(
            default=None,
            validation_alias=AliasChoices("anyOf", "any_of"),
            description="Alternative sub-schemas.",
        ),
    ] = None


MCPToolSchemaPropertyDTO.model_rebuild()


class MCPToolInputSchemaDTO(V2CoreBase):
    """Root JSON Schema object definition for an MCP tool's input parameters.

    Attributes:
        type: Root schema type literal ('object').
        title: Optional root JSON Schema title.
        description: Optional root JSON Schema description.
        properties: Mapping of parameter names to recursive property schemas.
        required: List of required top-level parameter names.
        additional_properties: Optional flag restricting additional top-level properties.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, populate_by_name=True)

    type: Annotated[Literal["object"], Field(default="object", description="Root JSON Schema type.")] = "object"
    title: Annotated[str | None, Field(default=None, description="Optional root JSON Schema title.")] = None
    description: Annotated[
        str,
        Field(default="", description="Optional root JSON Schema description."),
    ] = ""
    properties: Annotated[
        dict[str, MCPToolSchemaPropertyDTO],
        Field(default_factory=dict, description="Mapping of parameter names to property schemas."),
    ]
    required: Annotated[
        list[str],
        Field(default_factory=list, description="List of required top-level parameter names."),
    ]
    additional_properties: Annotated[
        bool | None,
        Field(
            default=None,
            validation_alias=AliasChoices("additionalProperties", "additional_properties"),
            description="Whether additional top-level properties are permitted.",
        ),
    ] = None
    schema_uri: Annotated[
        str | None,
        Field(
            default=None,
            validation_alias=AliasChoices("$schema", "schema_uri", "schema"),
            description="JSON Schema Draft URI specification.",
        ),
    ] = None


class ParsedMCPToolAliasDTO(V2CoreBase):
    """Bijective parsed representation of a namespaced MCP tool alias ('{gateway_slug}__{tool_id}').

    Attributes:
        gateway_slug: Collision-free namespace slug of the MCP gateway.
        tool_id: Canonical technical identifier of the tool on the remote MCP server.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    gateway_slug: Annotated[str, Field(min_length=1, description="Namespace slug of the MCP gateway.")]
    tool_id: Annotated[str, Field(min_length=1, description="Technical identifier of the MCP tool.")]


class MCPToolDescriptorDTO(V2CoreBase):
    """Hydrated runtime descriptor for an MCP tool bound to a specific gateway.

    Attributes:
        gateway_id: Opaque ID of the parent MCP gateway.
        gateway_slug: Namespace slug of the parent MCP gateway.
        namespaced_alias: Full namespaced alias ('{gateway_slug}__{tool_id}').
        tool_id: Technical identifier of the tool.
        description: English-only LLM description for function calling schema.
        capability: Operational capability category of the tool.
        input_schema: Strict recursive JSON Schema for tool parameters.
        enabled: Whether this tool is enabled for agent execution.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    gateway_id: Annotated[str, Field(default="", description="Opaque ID of the parent MCP gateway.")] = ""
    gateway_slug: Annotated[str, Field(default="", description="Namespace slug of the parent MCP gateway.")] = ""
    namespaced_alias: Annotated[
        str,
        Field(default="", description="Full namespaced alias ('{gateway_slug}__{tool_id}')."),
    ] = ""
    tool_id: Annotated[str, Field(min_length=1, description="Technical identifier of the tool.")]
    description: Annotated[str, Field(description="English-only LLM description for function calling schema.")]
    capability: Annotated[
        LaxToolCapability,
        Field(default=ToolCapability.GENERAL, description="Operational capability category of the tool."),
    ] = ToolCapability.GENERAL
    input_schema: Annotated[
        MCPToolInputSchemaDTO,
        Field(
            default_factory=MCPToolInputSchemaDTO,
            description="Strict recursive JSON Schema for tool parameters.",
        ),
    ]
    enabled: Annotated[
        bool,
        Field(default=True, description="Whether this tool is enabled for agent execution."),
    ] = True


class MCPToolInvocationDTO(V2CoreBase):
    """Validated runtime invocation request for a specific MCP gateway tool.

    Attributes:
        gateway_id: Opaque ID of the target MCP gateway.
        gateway_slug: Namespace slug of the target MCP gateway.
        tool_id: Technical identifier of the tool on the MCP server.
        namespaced_alias: Full namespaced alias invoked by the LLM.
        arguments: Validated tool arguments dictionary.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    gateway_id: Annotated[
        str,
        Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Opaque ID of the target MCP gateway."),
    ]
    gateway_slug: Annotated[str, Field(min_length=1, description="Namespace slug of the target MCP gateway.")]
    tool_id: Annotated[str, Field(min_length=1, description="Technical identifier of the tool on the MCP server.")]
    namespaced_alias: Annotated[str, Field(min_length=1, description="Full namespaced alias invoked by the LLM.")]
    arguments: Annotated[
        dict[str, MCPArgumentValue],
        Field(default_factory=dict, description="Validated tool arguments dictionary."),
    ]


class MCPFunctionDefinitionDTO(V2CoreBase):
    """Inner function definition schema for MCP tool declaration.

    Attributes:
        name: Tool function identifier name.
        description: Detailed tool description for LLM.
        parameters: Strict recursive JSON schema parameter definitions.
        strict: Whether schema enforces strict adherence.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    name: Annotated[str, Field(description="Tool function identifier name.")]
    description: Annotated[str, Field(description="Detailed tool description for LLM.")]
    parameters: Annotated[
        MCPToolInputSchemaDTO,
        Field(default_factory=MCPToolInputSchemaDTO, description="JSON schema parameter definitions."),
    ]
    strict: Annotated[bool, Field(default=True, description="Whether schema enforces strict adherence.")] = True


class MCPToolDeclarationDTO(V2CoreBase):
    """OpenAI-compatible function tool declaration for MCP.

    Attributes:
        type: Tool declaration type.
        function: Function definition.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    type: Annotated[str, Field(default="function", description="Tool declaration type.")] = "function"
    function: Annotated[MCPFunctionDefinitionDTO, Field(description="Function definition.")]


class MCPCapabilityConfigDTO(V2CoreBase):
    """Feature capability flags declared by an MCP client or server.

    Attributes:
        list_changed: Whether the endpoint emits notifications when the item list changes.
        subscribe: Whether the endpoint supports resource subscription notifications.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, populate_by_name=True)

    list_changed: Annotated[
        bool | None,
        Field(
            default=None,
            validation_alias=AliasChoices("listChanged", "list_changed"),
            serialization_alias="listChanged",
            description="Whether list-changed notifications are supported.",
        ),
    ] = None
    subscribe: Annotated[
        bool | None,
        Field(default=None, description="Whether resource subscription notifications are supported."),
    ] = None


class MCPInitializeClientInfoDTO(V2CoreBase):
    """Client implementation metadata sent during MCP initialize handshake.

    Attributes:
        name: Client application name.
        version: Client application version.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    name: Annotated[str, Field(default="quorum-backend-v2", description="Client application name.")] = (
        "quorum-backend-v2"
    )
    version: Annotated[str, Field(default="2.0.0", description="Client application version.")] = "2.0.0"


class MCPInitializeParamsDTO(V2CoreBase):
    """Parameters for the MCP 'initialize' JSON-RPC 2.0 request.

    Attributes:
        protocol_version: MCP protocol specification version.
        capabilities: Client capability map.
        client_info: Client implementation metadata.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, populate_by_name=True)

    protocol_version: Annotated[
        str,
        Field(
            default="2025-03-26",
            validation_alias=AliasChoices("protocolVersion", "protocol_version"),
            serialization_alias="protocolVersion",
            description="MCP protocol specification version.",
        ),
    ] = "2025-03-26"
    capabilities: Annotated[
        dict[str, MCPCapabilityConfigDTO],
        Field(default_factory=dict, description="Client capability map."),
    ]
    client_info: Annotated[
        MCPInitializeClientInfoDTO,
        Field(
            default_factory=MCPInitializeClientInfoDTO,
            validation_alias=AliasChoices("clientInfo", "client_info"),
            serialization_alias="clientInfo",
            description="Client implementation metadata.",
        ),
    ]


class MCPToolCallParamsDTO(V2CoreBase):
    """Parameters for the MCP 'tools/call' JSON-RPC 2.0 request.

    Attributes:
        name: Remote tool name to execute.
        arguments: Tool invocation arguments.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    name: Annotated[str, Field(min_length=1, description="Remote tool name to execute.")]
    arguments: Annotated[
        dict[str, MCPArgumentValue],
        Field(default_factory=dict, description="Tool invocation arguments."),
    ]


class MCPJsonRpcRequestDTO(V2CoreBase):
    """Outbound JSON-RPC 2.0 request envelope for MCP servers.

    Attributes:
        jsonrpc: JSON-RPC protocol version literal ('2.0').
        id: Request correlation identifier.
        method: JSON-RPC method name ('initialize', 'notifications/initialized', 'tools/list', 'tools/call').
        params: Optional method parameters payload.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    jsonrpc: Annotated[Literal["2.0"], Field(default="2.0", description="JSON-RPC version.")] = "2.0"
    id: Annotated[int | str | None, Field(default=None, description="Request correlation identifier.")] = None
    method: Annotated[str, Field(min_length=1, description="JSON-RPC method name.")]
    params: Annotated[
        MCPInitializeParamsDTO | MCPToolCallParamsDTO | None,
        Field(default=None, description="Optional method parameters payload."),
    ] = None


class MCPJsonRpcErrorDTO(V2CoreBase):
    """JSON-RPC 2.0 error object returned by an MCP server.

    Attributes:
        code: Integer JSON-RPC error code.
        message: Error description message.
        data: Optional error detail string.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    code: Annotated[int, Field(description="Integer JSON-RPC error code.")]
    message: Annotated[str, Field(description="Error description message.")]
    data: Annotated[str | None, Field(default=None, description="Optional error detail string.")] = None


class MCPIconDTO(V2CoreBase):
    """Icon descriptor returned in MCP server implementation metadata.

    Attributes:
        src: Icon source URI or data URL.
        mime_type: Optional MIME type of the icon asset.
        sizes: List of supported icon dimensions or 'any'.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, populate_by_name=True)

    src: Annotated[str, Field(description="Icon source URI or data URL.")]
    mime_type: Annotated[
        str | None,
        Field(
            default=None,
            validation_alias=AliasChoices("mimeType", "mime_type"),
            description="Optional MIME type of the icon asset.",
        ),
    ] = None
    sizes: Annotated[
        list[str],
        Field(default_factory=list, description="List of supported icon dimensions or 'any'."),
    ]


class MCPServerInfoDTO(V2CoreBase):
    """Server implementation metadata returned in MCP 'initialize' response.

    Attributes:
        name: Server implementation identifier name.
        version: Server implementation version string.
        title: Optional human-readable server title.
        description: Optional human-readable server description.
        website_url: Optional URL to the server documentation or homepage.
        icons: List of server icon descriptors.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, populate_by_name=True)

    name: Annotated[str, Field(default="", description="Server implementation identifier name.")] = ""
    version: Annotated[str, Field(default="", description="Server implementation version string.")] = ""
    title: Annotated[str | None, Field(default=None, description="Optional human-readable server title.")] = None
    description: Annotated[
        str | None, Field(default=None, description="Optional human-readable server description.")
    ] = None
    website_url: Annotated[
        str | None,
        Field(
            default=None,
            validation_alias=AliasChoices("websiteUrl", "website_url"),
            description="Optional URL to the server documentation or homepage.",
        ),
    ] = None
    icons: Annotated[
        list[MCPIconDTO],
        Field(default_factory=list, description="List of server icon descriptors."),
    ]


class MCPInitializeResultDTO(V2CoreBase):
    """Result payload returned by an MCP server for 'initialize'.

    Attributes:
        protocol_version: Negotiated MCP protocol version.
        server_info: Server implementation metadata (name/version).
        capabilities: Server capability declarations.
        instructions: Optional server usage instructions.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, populate_by_name=True)

    protocol_version: Annotated[
        str,
        Field(
            default="2025-03-26",
            validation_alias=AliasChoices("protocolVersion", "protocol_version"),
            description="Negotiated MCP protocol version.",
        ),
    ] = "2025-03-26"
    server_info: Annotated[
        MCPServerInfoDTO,
        Field(
            default_factory=MCPServerInfoDTO,
            validation_alias=AliasChoices("serverInfo", "server_info"),
            description="Server implementation metadata.",
        ),
    ]
    capabilities: Annotated[
        dict[str, MCPCapabilityConfigDTO],
        Field(default_factory=dict, description="Server capability declarations."),
    ]
    instructions: Annotated[
        str | None,
        Field(default=None, description="Optional server usage instructions."),
    ] = None


class FastMCPMetaDTO(V2CoreBase):
    """Metadata block specific to FastMCP server frameworks.

    Attributes:
        tags: List of categorization tags.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    tags: Annotated[list[str], Field(default_factory=list, description="FastMCP tags.")]


class MCPToolMetaDTO(V2CoreBase):
    """Server and framework metadata container on discovered MCP tools.

    Attributes:
        fastmcp: Optional FastMCP metadata block.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    fastmcp: Annotated[FastMCPMetaDTO | None, Field(default=None, description="FastMCP metadata block.")] = None


class MCPToolAnnotationsDTO(V2CoreBase):
    """Behavioral hints and annotations for an MCP tool per specification.

    Attributes:
        destructive_hint: Whether the tool call may cause destructive changes.
        read_only_hint: Whether the tool only reads data without mutations.
        open_in_new_tab: Whether the UI should open tool results in a new tab.
        idempotent_hint: Whether the tool can be safely called multiple times.
        open_world_hint: Whether the tool interacts with external open-world state.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, populate_by_name=True)

    destructive_hint: Annotated[
        bool | None,
        Field(
            default=None,
            validation_alias=AliasChoices("destructiveHint", "destructive_hint"),
            description="Whether tool execution is destructive.",
        ),
    ] = None
    read_only_hint: Annotated[
        bool | None,
        Field(
            default=None,
            validation_alias=AliasChoices("readOnlyHint", "read_only_hint"),
            description="Whether tool execution is read-only.",
        ),
    ] = None
    open_in_new_tab: Annotated[
        bool | None,
        Field(
            default=None,
            validation_alias=AliasChoices("openInNewTab", "open_in_new_tab"),
            description="Whether UI should open result in a new tab.",
        ),
    ] = None
    idempotent_hint: Annotated[
        bool | None,
        Field(
            default=None,
            validation_alias=AliasChoices("idempotentHint", "idempotent_hint"),
            description="Whether tool execution is idempotent.",
        ),
    ] = None
    open_world_hint: Annotated[
        bool | None,
        Field(
            default=None,
            validation_alias=AliasChoices("openWorldHint", "open_world_hint"),
            description="Whether tool accesses open-world resources.",
        ),
    ] = None


class MCPToolExecutionDTO(V2CoreBase):
    """Execution control metadata for an MCP tool.

    Attributes:
        task_support: Task execution support policy (e.g., 'forbidden', 'optional', 'required').
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, populate_by_name=True)

    task_support: Annotated[
        str | None,
        Field(
            default=None,
            validation_alias=AliasChoices("taskSupport", "task_support"),
            description="Task execution support policy for MCP background tasks.",
        ),
    ] = None


class MCPDiscoveredToolWireDTO(V2CoreBase):
    """Single tool entry returned inside 'tools/list' response from an MCP server.

    Attributes:
        name: Technical tool identifier on the MCP server.
        title: Optional human-readable display title.
        description: Human/LLM description of the tool.
        input_schema: Recursive JSON Schema for the tool's input parameters.
        output_schema: Optional recursive JSON Schema for the tool's output.
        annotations: Optional behavioral annotations and hints.
        meta: Optional server framework metadata container.
        execution: Optional tool execution configuration and task support policy.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, populate_by_name=True)

    name: Annotated[str, Field(min_length=1, description="Technical tool identifier on the MCP server.")]
    title: Annotated[str | None, Field(default=None, description="Optional human-readable display title.")] = None
    description: Annotated[str, Field(default="", description="Tool description.")] = ""
    input_schema: Annotated[
        MCPToolInputSchemaDTO,
        Field(
            default_factory=MCPToolInputSchemaDTO,
            validation_alias=AliasChoices("inputSchema", "input_schema"),
            description="Recursive JSON Schema for the tool's input parameters.",
        ),
    ]
    output_schema: Annotated[
        MCPToolInputSchemaDTO | None,
        Field(
            default=None,
            validation_alias=AliasChoices("outputSchema", "output_schema"),
            description="Optional recursive JSON Schema for tool output.",
        ),
    ] = None
    annotations: Annotated[
        MCPToolAnnotationsDTO | None,
        Field(default=None, description="Optional behavioral annotations and hints."),
    ] = None
    meta: Annotated[
        MCPToolMetaDTO | None,
        Field(
            default=None,
            validation_alias=AliasChoices("_meta", "meta"),
            description="Optional server framework metadata.",
        ),
    ] = None
    execution: Annotated[
        MCPToolExecutionDTO | None,
        Field(default=None, description="Optional tool execution configuration and task support policy."),
    ] = None


class MCPToolsListResultDTO(V2CoreBase):
    """Result payload returned by an MCP server for 'tools/list'.

    Attributes:
        tools: List of discovered tool wire descriptors.
        next_cursor: Optional pagination cursor.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, populate_by_name=True)

    tools: Annotated[
        list[MCPDiscoveredToolWireDTO],
        Field(default_factory=list, description="List of discovered tool wire descriptors."),
    ]
    next_cursor: Annotated[
        str | None,
        Field(
            default=None,
            validation_alias=AliasChoices("nextCursor", "next_cursor"),
            description="Optional pagination cursor.",
        ),
    ] = None


class MCPContentBlockDTO(V2CoreBase):
    """Content item returned inside an MCP 'tools/call' result.

    Attributes:
        type: Content block type (e.g., 'text', 'image', 'resource').
        text: Text content when type is 'text'.
        mime_type: Optional MIME type of the content block.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, populate_by_name=True)

    type: Annotated[str, Field(default="text", description="Content block type.")] = "text"
    text: Annotated[str, Field(default="", description="Text content payload.")] = ""
    mime_type: Annotated[
        str | None,
        Field(
            default=None,
            validation_alias=AliasChoices("mimeType", "mime_type"),
            description="Optional MIME type of the content block.",
        ),
    ] = None


class MCPSearchResultItemDTO(V2CoreBase):
    """Structured search result item returned inside an MCP tool call response.

    Attributes:
        id: Optional result item identifier.
        url: URL of the search result document.
        title: Title of the search result document.
        content: Extracted textual content or snippet.
        snippet: Search hit snippet or abstract extract.
        text: Plain text content extract.
        summary: Encyclopedic or article summary.
        raw_content: Optional raw HTML or unparsed content.
        score: Relevance ranking score.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, populate_by_name=True)

    id: Annotated[str | None, Field(default=None, description="Result item identifier.")] = None
    url: Annotated[str | None, Field(default=None, description="URL of the search result.")] = None
    title: Annotated[str | None, Field(default=None, description="Title of the page.")] = None
    content: Annotated[str | None, Field(default=None, description="Extracted content text.")] = None
    snippet: Annotated[str | None, Field(default=None, description="Search hit snippet or abstract extract.")] = None
    text: Annotated[str | None, Field(default=None, description="Plain text content extract.")] = None
    summary: Annotated[str | None, Field(default=None, description="Encyclopedic or article summary.")] = None
    raw_content: Annotated[
        str | None,
        Field(
            default=None,
            validation_alias=AliasChoices("rawContent", "raw_content"),
            description="Raw page content.",
        ),
    ] = None
    score: Annotated[float | int | None, Field(default=None, description="Relevance score.")] = None


class MCPStructuredContentDTO(V2CoreBase):
    """Structured domain payload returned inside 'structuredContent' by an MCP server.

    Attributes:
        query: Search query executed.
        follow_up_questions: Suggested follow-up queries.
        answer: Synthesized direct answer text.
        summary: Executive summary of structured tool output.
        description: Descriptive narrative of tool output.
        text: Direct text response body.
        message: Status or informational message.
        finding: Key factual or analytical finding.
        images: List of image URLs discovered.
        results: List of structured search result items.
        auth_mode: Authentication mode used by remote service.
        response_time: Remote server response time in seconds.
        request_id: Remote request correlation identifier.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, populate_by_name=True)

    query: Annotated[str | None, Field(default=None, description="Search query executed.")] = None
    follow_up_questions: Annotated[
        list[str] | None,
        Field(
            default=None,
            validation_alias=AliasChoices("followUpQuestions", "follow_up_questions"),
            description="Follow-up questions.",
        ),
    ] = None
    answer: Annotated[str | None, Field(default=None, description="Direct synthesized answer.")] = None
    summary: Annotated[str | None, Field(default=None, description="Executive summary of structured tool output.")] = (
        None
    )
    description: Annotated[str | None, Field(default=None, description="Descriptive narrative of tool output.")] = None
    text: Annotated[str | None, Field(default=None, description="Direct text response body.")] = None
    message: Annotated[str | None, Field(default=None, description="Status or informational message.")] = None
    finding: Annotated[str | None, Field(default=None, description="Key factual or analytical finding.")] = None
    images: Annotated[list[str], Field(default_factory=list, description="Image URLs.")]
    results: Annotated[list[MCPSearchResultItemDTO], Field(default_factory=list, description="Search results.")]
    auth_mode: Annotated[
        str | None,
        Field(
            default=None,
            validation_alias=AliasChoices("authMode", "auth_mode"),
            description="Authentication mode.",
        ),
    ] = None
    response_time: Annotated[
        float | int | None,
        Field(
            default=None,
            validation_alias=AliasChoices("responseTime", "response_time"),
            description="Remote response time in seconds.",
        ),
    ] = None
    request_id: Annotated[
        str | None,
        Field(
            default=None,
            validation_alias=AliasChoices("requestId", "request_id"),
            description="Remote request ID.",
        ),
    ] = None


class MCPToolCallResultDTO(V2CoreBase):
    """Result payload returned by an MCP server for 'tools/call'.

    Attributes:
        content: List of content blocks produced by the tool call.
        is_error: Whether the tool execution resulted in an application-level error.
        structured_content: Optional structured domain payload returned by the tool.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, populate_by_name=True)

    content: Annotated[
        list[MCPContentBlockDTO],
        Field(default_factory=list, description="List of content blocks produced by the tool call."),
    ]
    is_error: Annotated[
        bool,
        Field(
            default=False,
            validation_alias=AliasChoices("isError", "is_error"),
            description="Whether the tool execution resulted in an error.",
        ),
    ] = False
    structured_content: Annotated[
        MCPStructuredContentDTO | None,
        Field(
            default=None,
            validation_alias=AliasChoices("structuredContent", "structured_content"),
            description="Optional structured domain payload returned by the tool.",
        ),
    ] = None


class MCPJsonRpcResponseDTO(V2CoreBase):
    """Inbound JSON-RPC 2.0 response envelope from an MCP server.

    Attributes:
        jsonrpc: JSON-RPC protocol version literal ('2.0').
        id: Request correlation identifier.
        result: Typed result payload when call succeeded.
        error: Typed error payload when call failed.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    jsonrpc: Annotated[Literal["2.0"], Field(default="2.0", description="JSON-RPC protocol version.")] = "2.0"
    id: Annotated[int | str | None, Field(default=None, description="Request correlation identifier.")] = None
    result: Annotated[
        MCPInitializeResultDTO | MCPToolsListResultDTO | MCPToolCallResultDTO | None,
        Field(default=None, description="Typed result payload when call succeeded."),
    ] = None
    error: Annotated[
        MCPJsonRpcErrorDTO | None,
        Field(default=None, description="Typed error payload when call failed."),
    ] = None
