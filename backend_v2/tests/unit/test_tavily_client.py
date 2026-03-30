"""Unit tests for Tavily MCP Client.

All tests use mocked HTTP — no live API calls (EPIC §3 'Tavily No-Spam').
"""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from backend_v2.exceptions import AppException, ConfigurationError
from backend_v2.services.mcp.tavily_search_client import TavilySearchResult, tavily_search

MOCK_TAVILY_RESPONSE = {
    "answer": "Finland has 5.5 million people.",
    "results": [
        {
            "url": "https://example.com/finland",
            "content": "Finland is a Nordic country with approximately 5.5 million inhabitants.",
        },
        {
            "url": "https://example.com/nordic",
            "content": "The Nordic countries include Finland, Sweden, Norway, Denmark, and Iceland.",
        },
    ],
}


@pytest.mark.asyncio
async def test_tavily_search_happy_path() -> None:
    """Mock httpx.post, verify TavilySearchResult shape and content."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_TAVILY_RESPONSE

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("backend_v2.services.mcp.tavily_search_client.httpx.AsyncClient", return_value=mock_client),
        patch("backend_v2.services.mcp.tavily_search_client.get_settings") as mock_settings,
    ):
        mock_settings.return_value.tavily_api_key = "tvly-test-key"
        result = await tavily_search("Finland population")

    assert isinstance(result, TavilySearchResult)
    assert result.query == "Finland population"
    assert result.answer == "Finland has 5.5 million people."
    assert len(result.source_urls) == 2
    assert "https://example.com/finland" in result.source_urls
    assert len(result.raw_content) > 0


@pytest.mark.asyncio
async def test_tavily_search_missing_api_key() -> None:
    """Ensure ConfigurationError when key is None."""
    with patch("backend_v2.services.mcp.tavily_search_client.get_settings") as mock_settings:
        mock_settings.return_value.tavily_api_key = None

        with pytest.raises(ConfigurationError) as exc_info:
            await tavily_search("test query")

        assert "TAVILY_API_KEY" in str(exc_info.value)


@pytest.mark.asyncio
async def test_tavily_search_network_failure() -> None:
    """Ensure AppException(502) on httpx timeout."""
    mock_client = AsyncMock()
    mock_client.post.side_effect = httpx.TimeoutException("Connection timed out")
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("backend_v2.services.mcp.tavily_search_client.httpx.AsyncClient", return_value=mock_client),
        patch("backend_v2.services.mcp.tavily_search_client.get_settings") as mock_settings,
    ):
        mock_settings.return_value.tavily_api_key = "tvly-test-key"

        with pytest.raises(AppException) as exc_info:
            await tavily_search("test query")

        assert exc_info.value.status_code == 502
