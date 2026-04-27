"""Unit tests for the Tavily Search Client."""

from typing import Any
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from backend_v2.exceptions import AppException, ConfigurationError
from backend_v2.services.mcp.tavily_search_client import tavily_search


@pytest.fixture
def mock_settings() -> Any:
    """Mock the settings to provide a fake API key."""
    with patch("backend_v2.services.mcp.tavily_search_client.get_settings") as mock_get:
        mock_get.return_value.tavily_api_key = "test_tavily_key"
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
