"""Data Transfer Objects for MCP Tools and Tavily search integration."""

from __future__ import annotations

from typing import Annotated

from pydantic import ConfigDict, Field, JsonValue

from backend_v2.models.core_base import V2CoreBase

__all__ = [
    "MCPFunctionDefinitionDTO",
    "MCPToolDeclarationDTO",
    "MCPValidationContextDTO",
    "TavilySearchRequestDTO",
]


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
        list[JsonValue],
        Field(default_factory=list, description="Optional source document contexts for quote verification."),
    ]
    alias_registry: Annotated[
        dict[str, str],
        Field(default_factory=dict, description="Optional alias registry mapping short aliases to opaque IDs."),
    ]


class TavilySearchRequestDTO(V2CoreBase):
    """Payload sent to the Tavily search API endpoint.

    Attributes:
        api_key: Tavily API key.
        query: Search query string.
        max_results: Maximum number of search results.
        include_answer: Include concise AI answer.
        include_raw_content: Include full raw content.
        search_depth: Search depth (basic or advanced).
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    api_key: Annotated[str, Field(description="Tavily API key")]
    query: Annotated[str, Field(description="Search query string")]
    max_results: Annotated[int, Field(default=5, description="Maximum number of search results")] = 5
    include_answer: Annotated[bool, Field(default=True, description="Include concise AI answer")] = True
    include_raw_content: Annotated[bool, Field(default=False, description="Include full raw content")] = False
    search_depth: Annotated[str, Field(default="basic", description="Search depth (basic or advanced)")] = "basic"


class MCPFunctionDefinitionDTO(V2CoreBase):
    """Inner function definition schema for MCP tool declaration.

    Attributes:
        name: Tool function identifier name.
        description: Detailed tool description for LLM.
        parameters: JSON schema parameter definitions.
        strict: Whether schema enforces strict adherence.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    name: Annotated[str, Field(description="Tool function identifier name")]
    description: Annotated[str, Field(description="Detailed tool description for LLM")]
    parameters: Annotated[dict[str, JsonValue], Field(description="JSON schema parameter definitions")]
    strict: Annotated[bool, Field(default=True, description="Whether schema enforces strict adherence")] = True


class MCPToolDeclarationDTO(V2CoreBase):
    """OpenAI-compatible function tool declaration for MCP.

    Attributes:
        type: Tool declaration type.
        function: Function definition.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    type: Annotated[str, Field(default="function", description="Tool declaration type")] = "function"
    function: Annotated[MCPFunctionDefinitionDTO, Field(description="Function definition")]
