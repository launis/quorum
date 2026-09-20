"""Unit tests for MCP DTOs."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.mcp import (
    MCPFunctionDefinitionDTO,
    MCPToolDeclarationDTO,
    TavilySearchRequestDTO,
)


def test_tavily_search_request_dto() -> None:
    """Test TavilySearchRequestDTO default fields and validation."""
    req = TavilySearchRequestDTO(
        api_key="tvly-secret",
        query="python 3.14 features",
    )
    assert req.api_key == "tvly-secret"
    assert req.query == "python 3.14 features"
    assert req.max_results == 5
    assert req.include_answer is True
    assert req.include_raw_content is False
    assert req.search_depth == "basic"

    with pytest.raises(ValidationError):
        req.query = "new query"  # type: ignore[misc]


def test_mcp_tool_declaration_dto() -> None:
    """Test MCPToolDeclarationDTO and nested MCPFunctionDefinitionDTO."""
    func = MCPFunctionDefinitionDTO(
        name="web_search",
        description="Searches the web via Tavily",
        parameters={"type": "object", "properties": {"q": {"type": "string"}}},
        strict=True,
    )
    tool = MCPToolDeclarationDTO(function=func)
    assert tool.type == "function"
    assert tool.function.name == "web_search"
    assert tool.function.description == "Searches the web via Tavily"
    assert tool.function.strict is True


def test_mcp_dto_missing_required() -> None:
    """Test validation errors when required arguments are missing."""
    with pytest.raises(ValidationError):
        _ = TavilySearchRequestDTO()  # type: ignore[call-arg]

    with pytest.raises(ValidationError):
        _ = MCPToolDeclarationDTO()  # type: ignore[call-arg]
