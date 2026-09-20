"""Data Transfer Objects for MCP Tools and Tavily search integration."""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase

__all__ = [
    "MCPFunctionDefinitionDTO",
    "MCPToolDeclarationDTO",
    "TavilySearchRequestDTO",
]


class TavilySearchRequestDTO(V2CoreBase):
    """Payload sent to the Tavily search API endpoint."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    api_key: Annotated[str, Field(description="Tavily API key")]
    query: Annotated[str, Field(description="Search query string")]
    max_results: Annotated[int, Field(default=5, description="Maximum number of search results")] = 5
    include_answer: Annotated[bool, Field(default=True, description="Include concise AI answer")] = True
    include_raw_content: Annotated[bool, Field(default=False, description="Include full raw content")] = False
    search_depth: Annotated[str, Field(default="basic", description="Search depth (basic or advanced)")] = "basic"


class MCPFunctionDefinitionDTO(V2CoreBase):
    """Inner function definition schema for MCP tool declaration."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    name: Annotated[str, Field(description="Tool function identifier name")]
    description: Annotated[str, Field(description="Detailed tool description for LLM")]
    parameters: Annotated[dict[str, Any], Field(description="JSON schema parameter definitions")]
    strict: Annotated[bool, Field(default=True, description="Whether schema enforces strict adherence")] = True


class MCPToolDeclarationDTO(V2CoreBase):
    """OpenAI-compatible function tool declaration for MCP."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    type: Annotated[str, Field(default="function", description="Tool declaration type")] = "function"
    function: Annotated[MCPFunctionDefinitionDTO, Field(description="Function definition")]
