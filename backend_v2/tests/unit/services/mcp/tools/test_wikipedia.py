"""Unit tests for WikipediaSearchTool and WikipediaReadTool MCP implementations."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.domain.wikipedia import (
    WikipediaPageSummaryResult,
    WikipediaSearchResponseDTO,
    WikipediaSearchResultItem,
)
from backend_v2.models.dtos.mcp import MCPToolDeclarationDTO
from backend_v2.models.enums import ToolCapability
from backend_v2.services.mcp.tools.wikipedia import (
    WIKIPEDIA_READ_TOOL_ID,
    WIKIPEDIA_SEARCH_TOOL_ID,
    WikipediaReadTool,
    WikipediaSearchTool,
)


# --- WikipediaSearchTool Tests ---
def test_wikipedia_search_tool_properties() -> None:
    """Test tool_id, capability, and declaration properties of WikipediaSearchTool."""
    tool = WikipediaSearchTool()
    assert tool.tool_id == WIKIPEDIA_SEARCH_TOOL_ID
    assert tool.capability == ToolCapability.SEARCH

    decl = tool.declaration
    assert isinstance(decl, MCPToolDeclarationDTO)
    assert decl.type == "function"
    assert decl.function.name == WIKIPEDIA_SEARCH_TOOL_ID
    assert "Wikipedia" in decl.function.description
    assert decl.function.parameters.type == "object"
    assert decl.function.parameters.required == ["query", "reasoning"]
    assert decl.function.strict is True


@pytest.mark.asyncio
async def test_wikipedia_search_tool_execute_success() -> None:
    """Test successful execution of Wikipedia search returning MCPAuditTrace."""
    tool = WikipediaSearchTool()
    mock_result = WikipediaSearchResponseDTO(
        query="Finland",
        total_hits=1,
        results=[
            WikipediaSearchResultItem(
                title="Finland",
                snippet="Finland is a Nordic country.",
                pageid=123,
                url="https://en.wikipedia.org/wiki/Finland",
            )
        ],
    )

    with patch("backend_v2.services.mcp.tools.wikipedia.wikipedia_search", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = mock_result
        trace = await tool.execute(
            query="Finland",
            step_name="step_verify",
            reasoning="Verify country data",
            claim_text="Finland is in Northern Europe",
        )

        assert isinstance(trace, MCPAuditTrace)
        assert trace.tool_id == WIKIPEDIA_SEARCH_TOOL_ID
        assert trace.query == "Finland"
        assert trace.step_name == "step_verify"
        assert trace.reasoning == "Verify country data"
        assert trace.claim_text == "Finland is in Northern Europe"
        assert (
            "[Finland](https://en.wikipedia.org/wiki/Finland): Finland is a Nordic country." in trace.response_summary
        )
        assert trace.source_urls == ["https://en.wikipedia.org/wiki/Finland"]
        assert trace.duration_ms >= 0


@pytest.mark.asyncio
async def test_wikipedia_search_tool_execute_empty_results() -> None:
    """Test execution when Wikipedia returns zero search results for English query (no fallback)."""
    tool = WikipediaSearchTool()
    mock_result = WikipediaSearchResponseDTO(
        query="NonExistentTopic12345",
        total_hits=0,
        results=[],
    )

    with patch("backend_v2.services.mcp.tools.wikipedia.wikipedia_search", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = mock_result
        trace = await tool.execute(
            query="NonExistentTopic12345",
            step_name="step_empty",
            reasoning="Testing empty query",
            target_language="en",
        )

        assert "No Wikipedia articles found for query: 'NonExistentTopic12345'." in trace.response_summary
        assert trace.source_urls == []
        mock_search.assert_awaited_once_with(query="NonExistentTopic12345", target_language="en")


@pytest.mark.asyncio
async def test_wikipedia_search_tool_execute_multilingual_fallback_success() -> None:
    """Test that zero hits in non-English search expands to English and translates summary."""
    tool = WikipediaSearchTool()
    fi_empty_result = WikipediaSearchResponseDTO(
        query="Nicholas Bloom",
        total_hits=0,
        results=[],
    )
    en_hit_result = WikipediaSearchResponseDTO(
        query="Nicholas Bloom",
        total_hits=1,
        results=[
            WikipediaSearchResultItem(
                title="Nicholas Bloom",
                snippet="Nicholas Bloom is an economics professor at Stanford University.",
                pageid=789,
                url="https://en.wikipedia.org/wiki/Nicholas_Bloom",
            )
        ],
    )
    mock_llm = AsyncMock()

    with (
        patch("backend_v2.services.mcp.tools.wikipedia.wikipedia_search", new_callable=AsyncMock) as mock_search,
        patch("backend_v2.services.translation_service.translate_text", new_callable=AsyncMock) as mock_translate,
    ):
        mock_search.side_effect = [fi_empty_result, en_hit_result]
        mock_translate.return_value = "Nicholas Bloom on taloustieteen professori Stanfordin yliopistossa."

        trace = await tool.execute(
            query="Nicholas Bloom",
            step_name="step_verify_scholar",
            target_language="fi",
            llm_client=mock_llm,
        )

        assert mock_search.await_count == 2
        assert mock_search.await_args_list[0].kwargs == {"query": "Nicholas Bloom", "target_language": "fi"}
        assert mock_search.await_args_list[1].kwargs == {"query": "Nicholas Bloom", "target_language": "en"}

        mock_translate.assert_awaited_once_with(
            text="[Nicholas Bloom](https://en.wikipedia.org/wiki/Nicholas_Bloom): Nicholas Bloom is an economics professor at Stanford University.",
            target_lang="fi",
            llm_client=mock_llm,
            source_language="English/Original",
        )

        assert trace.response_summary == "Nicholas Bloom on taloustieteen professori Stanfordin yliopistossa."
        assert trace.source_urls == ["https://en.wikipedia.org/wiki/Nicholas_Bloom"]


@pytest.mark.asyncio
async def test_wikipedia_search_tool_execute_multilingual_fallback_both_empty() -> None:
    """Test that zero hits in both local language and English terminates gracefully without translation."""
    tool = WikipediaSearchTool()
    empty_result = WikipediaSearchResponseDTO(
        query="UnknownConceptXYZ",
        total_hits=0,
        results=[],
    )
    mock_llm = AsyncMock()

    with (
        patch("backend_v2.services.mcp.tools.wikipedia.wikipedia_search", new_callable=AsyncMock) as mock_search,
        patch("backend_v2.services.translation_service.translate_text", new_callable=AsyncMock) as mock_translate,
    ):
        mock_search.side_effect = [empty_result, empty_result]

        trace = await tool.execute(
            query="UnknownConceptXYZ",
            step_name="step_verify",
            target_language="fi",
            llm_client=mock_llm,
        )

        assert mock_search.await_count == 2
        mock_translate.assert_not_awaited()
        assert "No Wikipedia articles found for query: 'UnknownConceptXYZ'." in trace.response_summary
        assert trace.source_urls == []


@pytest.mark.asyncio
async def test_wikipedia_search_tool_execute_with_translation() -> None:
    """Test Wikipedia search execution with translation hook when target language differs."""
    tool = WikipediaSearchTool()
    mock_result = WikipediaSearchResponseDTO(
        query="Helsinki",
        total_hits=1,
        results=[
            WikipediaSearchResultItem(
                title="Helsinki",
                snippet="Helsinki is the capital of Finland.",
                pageid=456,
                url="https://en.wikipedia.org/wiki/Helsinki",
            )
        ],
    )
    mock_llm = AsyncMock()

    with (
        patch("backend_v2.services.mcp.tools.wikipedia.wikipedia_search", new_callable=AsyncMock) as mock_search,
        patch("backend_v2.services.mcp.tools.wikipedia.resolve_wikipedia_language", return_value="en"),
        patch("backend_v2.services.translation_service.translate_text", new_callable=AsyncMock) as mock_translate,
    ):
        mock_search.return_value = mock_result
        mock_translate.return_value = "Helsinki on Suomen pääkaupunki."

        trace = await tool.execute(
            query="Helsinki",
            step_name="step_fi",
            target_language="fi",
            llm_client=mock_llm,
        )

        assert trace.response_summary == "Helsinki on Suomen pääkaupunki."
        mock_translate.assert_awaited_once()


@pytest.mark.asyncio
async def test_wikipedia_search_tool_execute_app_exception_propagates() -> None:
    """Test that AppException from wikipedia_search is propagated directly."""
    tool = WikipediaSearchTool()
    exc = AppException(
        message="Validation failed", status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
    )

    with patch("backend_v2.services.mcp.tools.wikipedia.wikipedia_search", new_callable=AsyncMock) as mock_search:
        mock_search.side_effect = exc
        with pytest.raises(AppException) as exc_info:
            await tool.execute(query="test", step_name="step_err")
        assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_wikipedia_search_tool_execute_generic_error_wrapped() -> None:
    """Test that unexpected Exception is wrapped in AppException(502, FETCH_FAILED)."""
    tool = WikipediaSearchTool()

    with patch("backend_v2.services.mcp.tools.wikipedia.wikipedia_search", new_callable=AsyncMock) as mock_search:
        mock_search.side_effect = RuntimeError("Socket timeout")
        with pytest.raises(AppException) as exc_info:
            await tool.execute(query="test", step_name="step_err")
        assert exc_info.value.status_code == 502
        assert "Socket timeout" in str(exc_info.value.details)


def test_wikipedia_search_tool_validation_error() -> None:
    """Test that invalid input kwargs trigger Pydantic ValidationError."""
    tool = WikipediaSearchTool()
    with pytest.raises(ValidationError):
        # query is empty string (min_length=1)
        import asyncio

        asyncio.run(tool.execute(query=""))


# --- WikipediaReadTool Tests ---
def test_wikipedia_read_tool_properties() -> None:
    """Test tool_id, capability, and declaration properties of WikipediaReadTool."""
    tool = WikipediaReadTool()
    assert tool.tool_id == WIKIPEDIA_READ_TOOL_ID
    assert tool.capability == ToolCapability.DOCUMENT_READER

    decl = tool.declaration
    assert isinstance(decl, MCPToolDeclarationDTO)
    assert decl.type == "function"
    assert decl.function.name == WIKIPEDIA_READ_TOOL_ID
    assert "summary" in decl.function.description
    assert decl.function.parameters.type == "object"
    assert decl.function.parameters.required == ["title", "reasoning"]
    assert decl.function.strict is True


@pytest.mark.asyncio
async def test_wikipedia_read_tool_execute_success() -> None:
    """Test successful execution of Wikipedia read returning MCPAuditTrace."""
    tool = WikipediaReadTool()
    mock_result = WikipediaPageSummaryResult(
        title="Alan Turing",
        extract="Alan Turing was an English mathematician and computer scientist.",
        pageid=789,
        url="https://en.wikipedia.org/wiki/Alan_Turing",
    )

    with patch("backend_v2.services.mcp.tools.wikipedia.wikipedia_read_summary", new_callable=AsyncMock) as mock_read:
        mock_read.return_value = mock_result
        trace = await tool.execute(
            title="Alan Turing",
            step_name="step_read",
            reasoning="Retrieve biographical facts",
            claim_text="Alan Turing was a pioneer of computing",
        )

        assert isinstance(trace, MCPAuditTrace)
        assert trace.tool_id == WIKIPEDIA_READ_TOOL_ID
        assert trace.query == "Alan Turing"
        assert trace.step_name == "step_read"
        assert trace.reasoning == "Retrieve biographical facts"
        assert trace.claim_text == "Alan Turing was a pioneer of computing"
        assert trace.response_summary == "Alan Turing was an English mathematician and computer scientist."
        assert trace.source_urls == ["https://en.wikipedia.org/wiki/Alan_Turing"]
        assert trace.duration_ms >= 0


@pytest.mark.asyncio
async def test_wikipedia_read_tool_execute_with_translation() -> None:
    """Test Wikipedia read execution with translation hook when target language differs."""
    tool = WikipediaReadTool()
    mock_result = WikipediaPageSummaryResult(
        title="Oulu",
        extract="Oulu is a city in Finland.",
        pageid=101,
        url="https://en.wikipedia.org/wiki/Oulu",
    )
    mock_llm = AsyncMock()

    with (
        patch("backend_v2.services.mcp.tools.wikipedia.wikipedia_read_summary", new_callable=AsyncMock) as mock_read,
        patch("backend_v2.services.mcp.tools.wikipedia.resolve_wikipedia_language", return_value="en"),
        patch("backend_v2.services.translation_service.translate_text", new_callable=AsyncMock) as mock_translate,
    ):
        mock_read.return_value = mock_result
        mock_translate.return_value = "Oulu on kaupunki Suomessa."

        trace = await tool.execute(
            title="Oulu",
            step_name="step_fi",
            target_language="fi",
            llm_client=mock_llm,
        )

        assert trace.response_summary == "Oulu on kaupunki Suomessa."
        mock_translate.assert_awaited_once()


@pytest.mark.asyncio
async def test_wikipedia_read_tool_execute_not_found_raises() -> None:
    """Test that 404 RESOURCE_NOT_FOUND AppException from client propagates."""
    tool = WikipediaReadTool()
    exc = AppException(
        message="Not found", status_code=404, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value}
    )

    with patch("backend_v2.services.mcp.tools.wikipedia.wikipedia_read_summary", new_callable=AsyncMock) as mock_read:
        mock_read.side_effect = exc
        with pytest.raises(AppException) as exc_info:
            await tool.execute(title="Ghost_Article_404", step_name="step_read")
        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_wikipedia_read_tool_execute_generic_error_wrapped() -> None:
    """Test that unexpected Exception is wrapped in AppException(502, FETCH_FAILED)."""
    tool = WikipediaReadTool()

    with patch("backend_v2.services.mcp.tools.wikipedia.wikipedia_read_summary", new_callable=AsyncMock) as mock_read:
        mock_read.side_effect = ConnectionResetError("Connection lost")
        with pytest.raises(AppException) as exc_info:
            await tool.execute(title="Test", step_name="step_read")
        assert exc_info.value.status_code == 502
        assert "Connection lost" in str(exc_info.value.details)


def test_wikipedia_read_tool_validation_error() -> None:
    """Test that invalid input kwargs trigger Pydantic ValidationError."""
    tool = WikipediaReadTool()
    with pytest.raises(ValidationError):
        # title is empty string (min_length=1)
        import asyncio

        asyncio.run(tool.execute(title=""))
