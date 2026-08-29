"""Unit tests for the Tavily Search Client."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from backend_v2.exceptions import AppException, ConfigurationError
from backend_v2.models.dtos.retrieval import BatchSearchQueryDTO
from backend_v2.models.enums import SearchStatus
from backend_v2.services.mcp.tavily_search_client import (
    _is_transient_error,
    batch_tavily_search,
    tavily_search,
)


@pytest.fixture
def mock_settings() -> Any:
    """Mock the settings to provide a fake API key and limits."""
    with patch("backend_v2.services.mcp.tavily_search_client.get_settings") as mock_get:
        mock_get.return_value.tavily_api_key = "test_tavily_key"
        mock_get.return_value.tavily_api_url = "https://api.tavily.com/search"
        mock_get.return_value.tavily_timeout_seconds = 15
        mock_get.return_value.tavily_max_results = 5
        mock_get.return_value.tavily_content_char_limit = 8000
        mock_get.return_value.tavily_max_concurrent_requests = 3
        yield mock_get


@pytest.mark.asyncio
async def test_tavily_search_success(mock_settings: Any) -> None:
    """Test a successful Tavily search with valid results."""
    mock_response = httpx.Response(
        status_code=200,
        json={
            "answer": "Finland has a population of 5.6 million.",
            "results": [{"url": "https://example.com/finland", "content": "Detailed article about Finland."}],
        },
        request=httpx.Request("POST", "https://api.tavily.com/search"),
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await tavily_search("Finland population")

        assert result.query == "Finland population"
        assert result.answer == "Finland has a population of 5.6 million."
        assert len(result.source_urls) == 1
        assert result.source_urls[0] == "https://example.com/finland"
        assert "Detailed article about Finland" in result.raw_content


@pytest.mark.asyncio
async def test_tavily_search_missing_api_key() -> None:
    """Test that missing API key raises ConfigurationError."""
    with patch("backend_v2.services.mcp.tavily_search_client.get_settings") as mock_get:
        mock_get.return_value.tavily_api_key = None

        with pytest.raises(ConfigurationError) as exc_info:
            await tavily_search("Test query")

        assert "Tavily API key is not configured" in str(exc_info.value)


@pytest.mark.asyncio
async def test_tavily_search_empty_query() -> None:
    """Test that empty query raises AppException early."""
    with pytest.raises(AppException) as exc_info:
        await tavily_search("   ")

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"


@pytest.mark.asyncio
async def test_tavily_search_http_error(mock_settings: Any) -> None:
    """Test that HTTP errors are wrapped in AppException."""
    mock_response = httpx.Response(
        status_code=500,
        text="Internal Server Error",
        request=httpx.Request("POST", "https://api.tavily.com/search"),
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        with pytest.raises(AppException) as exc_info:
            await tavily_search("Test query")

        assert exc_info.value.status_code == 502
        assert exc_info.value.details["error_code"] == "FETCH_FAILED"


@pytest.mark.asyncio
async def test_tavily_search_timeout_error(mock_settings: Any) -> None:
    """Test that TimeoutException raises AppException with status 502."""
    with patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("Timed out")):
        with pytest.raises(AppException) as exc_info:
            await tavily_search("Test query")

        assert exc_info.value.status_code == 502
        assert exc_info.value.details["error_code"] == "FETCH_FAILED"


@pytest.mark.asyncio
async def test_tavily_search_httpx_generic_error(mock_settings: Any) -> None:
    """Test that httpx.HTTPError raises AppException with status 502."""
    with patch("httpx.AsyncClient.post", side_effect=httpx.ConnectError("Connection refused")):
        with pytest.raises(AppException) as exc_info:
            await tavily_search("Test query")

        assert exc_info.value.status_code == 502
        assert exc_info.value.details["error_code"] == "FETCH_FAILED"


@pytest.mark.asyncio
async def test_tavily_search_malformed_json(mock_settings: Any) -> None:
    """Test that malformed JSON payload raises Validation AppException."""
    mock_response = httpx.Response(
        status_code=200,
        json={"wrong_key": "not a list of results"},
        request=httpx.Request("POST", "https://api.tavily.com/search"),
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        with pytest.raises(AppException) as exc_info:
            await tavily_search("Test query")

        assert exc_info.value.status_code == 502
        assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"


@pytest.mark.asyncio
async def test_tavily_search_empty_results_success(mock_settings: Any) -> None:
    """Test that a successful HTTP 200 with empty results and answer returns an empty TavilySearchResult without exception."""
    mock_response = httpx.Response(
        status_code=200,
        json={
            "answer": "",
            "results": [],
        },
        request=httpx.Request("POST", "https://api.tavily.com/search"),
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await tavily_search("Finland population")

        assert result.query == "Finland population"
        assert result.answer == ""
        assert len(result.source_urls) == 0
        assert result.raw_content == ""


def test_is_transient_error_helper() -> None:
    """Test _is_transient_error logic."""
    err_val = AppException(message="Validation", status_code=400, details={"error_code": "VALIDATION_FAILED"})
    assert _is_transient_error(err_val) is False

    err_fetch = AppException(message="Fetch", status_code=502, details={"error_code": "FETCH_FAILED"})
    assert _is_transient_error(err_fetch) is True

    assert _is_transient_error(ValueError("Other")) is False


@pytest.mark.asyncio
async def test_batch_tavily_search_empty_input() -> None:
    """Test batch search with empty text returns empty list."""
    task_executor = AsyncMock()
    llm_client = AsyncMock()
    res = await batch_tavily_search("", task_executor, llm_client)
    assert res == []


@pytest.mark.asyncio
async def test_batch_tavily_search_extraction_failure() -> None:
    """Test batch search when extraction task crashes."""
    task_executor = MagicMock()
    task_executor.execute_structured_task = AsyncMock(side_effect=RuntimeError("Extraction failed"))
    llm_client = AsyncMock()

    with pytest.raises(AppException) as exc_info:
        await batch_tavily_search("Some document text", task_executor, llm_client)
    assert exc_info.value.status_code == 502


@pytest.mark.asyncio
async def test_batch_tavily_search_no_queries_extracted() -> None:
    """Test batch search when no queries are returned from extraction."""
    task_executor = MagicMock()
    dto = BatchSearchQueryDTO(queries=[])
    task_executor.execute_structured_task = AsyncMock(return_value=(dto, {}))
    llm_client = AsyncMock()

    res = await batch_tavily_search("Some text", task_executor, llm_client)
    assert res == []


@pytest.mark.asyncio
async def test_batch_tavily_search_success(mock_settings: Any) -> None:
    """Test batch search executing queries concurrently and mapping results."""
    task_executor = MagicMock()
    dto = BatchSearchQueryDTO(queries=["query 1", "query 2", "query 1"])
    task_executor.execute_structured_task = AsyncMock(return_value=(dto, {}))
    llm_client = AsyncMock()

    mock_search_result = MagicMock()
    mock_search_result.answer = "Answer text"
    mock_search_result.source_urls = ["https://example.com/1"]
    mock_search_result.raw_content = "Raw content"
    mock_search_result.duration_ms = 120

    with patch(
        "backend_v2.services.mcp.tavily_search_client.tavily_search",
        new_callable=AsyncMock,
        return_value=mock_search_result,
    ):
        results = await batch_tavily_search("Valid document text", task_executor, llm_client)

        assert len(results) == 3
        assert results[0].query == "query 1"
        assert results[0].status == SearchStatus.COMPLETED
        assert results[0].source_urls == ["https://example.com/1"]


@pytest.mark.asyncio
async def test_batch_tavily_search_dlq_on_errors(mock_settings: Any) -> None:
    """Test batch search handling validation and network failures into DLQ status."""
    task_executor = MagicMock()
    dto = BatchSearchQueryDTO(queries=["q_validation_error", "q_fetch_error", "q_unexpected_error"])
    task_executor.execute_structured_task = AsyncMock(return_value=(dto, {}))
    llm_client = AsyncMock()

    async def _mock_search(q: str) -> Any:
        if q == "q_validation_error":
            raise AppException(message="Validation", status_code=400, details={"error_code": "VALIDATION_FAILED"})
        if q == "q_fetch_error":
            raise AppException(message="Fetch", status_code=502, details={"error_code": "FETCH_FAILED"})
        raise RuntimeError("Unexpected")

    with patch("backend_v2.services.mcp.tavily_search_client.tavily_search", side_effect=_mock_search):
        results = await batch_tavily_search("Document text", task_executor, llm_client)

        assert len(results) == 3
        res_map = {r.query: r for r in results}
        assert res_map["q_validation_error"].status == SearchStatus.DLQ_ERROR
        assert res_map["q_fetch_error"].status == SearchStatus.DLQ_TIMEOUT
        assert res_map["q_unexpected_error"].status == SearchStatus.DLQ_ERROR
