"""Unit tests for TavilyTool MCP implementation."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.dtos.mcp import MCPToolDeclarationDTO
from backend_v2.services.mcp.tavily_search_client import TavilySearchResult
from backend_v2.services.mcp.tools.tavily import TAVILY_TOOL_ID, TavilyTool


def test_tavily_tool_properties() -> None:
    """Test tool_id and declaration properties of TavilyTool."""
    tool = TavilyTool()
    assert tool.tool_id == TAVILY_TOOL_ID

    decl = tool.declaration
    assert isinstance(decl, MCPToolDeclarationDTO)
    assert decl.type == "function"
    assert decl.function.name == TAVILY_TOOL_ID
    assert "internet" in decl.function.description
    assert decl.function.parameters["type"] == "object"
    assert decl.function.strict is True


@pytest.mark.asyncio
async def test_tavily_tool_execute_success() -> None:
    """Test successful execution of Tavily search returning MCPAuditTrace."""
    tool = TavilyTool()
    mock_result = TavilySearchResult(
        query="capital of finland",
        answer="The capital is Helsinki.",
        source_urls=["https://example.com/helsinki"],
    )

    with patch("backend_v2.services.mcp.tools.tavily.tavily_search", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = mock_result
        trace = await tool.execute(
            query="capital of finland",
            step_name="test_step",
            reasoning="verify location",
            claim_text="Helsinki is the capital",
        )

        assert isinstance(trace, MCPAuditTrace)
        assert trace.tool_id == TAVILY_TOOL_ID
        assert trace.query == "capital of finland"
        assert trace.step_name == "test_step"
        assert trace.reasoning == "verify location"
        assert trace.claim_text == "Helsinki is the capital"
        assert trace.response_summary == "The capital is Helsinki."
        assert trace.source_urls == ["https://example.com/helsinki"]
        assert trace.duration_ms >= 0


@pytest.mark.asyncio
async def test_tavily_tool_execute_with_translation() -> None:
    """Test Tavily search execution with localized translation hook."""
    tool = TavilyTool()
    mock_result = TavilySearchResult(
        query="test query",
        answer="English answer",
        source_urls=["https://example.com"],
    )
    mock_llm = AsyncMock()

    with (
        patch("backend_v2.services.mcp.tools.tavily.tavily_search", new_callable=AsyncMock) as mock_search,
        patch("backend_v2.services.translation_service.translate_text", new_callable=AsyncMock) as mock_translate,
    ):
        mock_search.return_value = mock_result
        mock_translate.return_value = "Suomenkielinen vastaus"

        trace = await tool.execute(
            query="test query",
            step_name="step_fi",
            target_language="fi",
            llm_client=mock_llm,
        )

        assert trace.response_summary == "Suomenkielinen vastaus"
        mock_translate.assert_awaited_once_with(
            text="English answer",
            target_lang="fi",
            llm_client=mock_llm,
            source_language="English/Original",
        )


@pytest.mark.asyncio
async def test_tavily_tool_execute_failure_raises_app_exception() -> None:
    """Test search failure triggers structured AppException with 502 status."""
    tool = TavilyTool()

    with patch("backend_v2.services.mcp.tools.tavily.tavily_search", new_callable=AsyncMock) as mock_search:
        mock_search.side_effect = RuntimeError("Network down")

        with pytest.raises(AppException) as exc_info:
            await tool.execute(query="failing query")

        assert exc_info.value.status_code == 502
        assert exc_info.value.details["error_code"] == ErrorCodes.FETCH_FAILED.value


@pytest.mark.asyncio
async def test_tavily_tool_execute_re_raises_app_exception() -> None:
    """Test existing AppException is re-raised directly."""
    tool = TavilyTool()
    app_exc = AppException("Custom app error", status_code=400)

    with patch("backend_v2.services.mcp.tools.tavily.tavily_search", new_callable=AsyncMock) as mock_search:
        mock_search.side_effect = app_exc

        with pytest.raises(AppException) as exc_info:
            await tool.execute(query="app exception query")

        assert exc_info.value is app_exc
