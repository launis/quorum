"""Unit tests for WikipediaClient MCP service."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.wikipedia import (
    WikipediaPageSummaryResult,
    WikipediaSearchResponseDTO,
)
from backend_v2.services.mcp.wikipedia_client import (
    resolve_wikipedia_language,
    wikipedia_read_summary,
    wikipedia_search,
)


def test_resolve_wikipedia_language_valid() -> None:
    """Test valid language code resolution including sub-locales."""
    assert resolve_wikipedia_language("fi") == "fi"
    assert resolve_wikipedia_language("en") == "en"
    assert resolve_wikipedia_language("sv") == "sv"
    assert resolve_wikipedia_language("de") == "de"
    assert resolve_wikipedia_language("fi-FI") == "fi"
    assert resolve_wikipedia_language("en_US") == "en"
    assert resolve_wikipedia_language(None) == "en"
    assert resolve_wikipedia_language("") == "en"


def test_resolve_wikipedia_language_unsupported_raises() -> None:
    """Test that unsupported language codes fail-fast with AppException."""
    with pytest.raises(AppException) as exc_info:
        resolve_wikipedia_language("fr")
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    with pytest.raises(AppException) as exc_info2:
        resolve_wikipedia_language("es")
    assert exc_info2.value.status_code == 400

    with pytest.raises(AppException) as exc_info3:
        resolve_wikipedia_language("invalid_locale")
    assert exc_info3.value.status_code == 400


@pytest.mark.asyncio
async def test_wikipedia_search_success() -> None:
    """Test successful Action API search with HTML snippet stripping."""
    mock_payload = {
        "batchcomplete": "",
        "query": {
            "search": [
                {
                    "ns": 0,
                    "title": "Helsinki",
                    "pageid": 12345,
                    "size": 50000,
                    "wordcount": 4500,
                    "snippet": '<span class="searchmatch">Helsinki</span> on Suomen &quot;pääkaupunki&quot;.',
                }
            ]
        },
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_payload

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_resp
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client):
        res = await wikipedia_search("Helsinki", target_language="fi", max_results=5)

    assert isinstance(res, WikipediaSearchResponseDTO)
    assert res.query == "Helsinki"
    assert res.total_hits == 1
    assert len(res.results) == 1

    item = res.results[0]
    assert item.title == "Helsinki"
    assert item.pageid == 12345
    assert item.snippet == 'Helsinki on Suomen "pääkaupunki".'
    assert item.url == "https://fi.wikipedia.org/wiki/Helsinki"


@pytest.mark.asyncio
async def test_wikipedia_search_empty_results() -> None:
    """Test search returning empty search results."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"query": {"search": []}}

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_resp
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client):
        res = await wikipedia_search("nonexistentterm12345xyz")

    assert res.total_hits == 0
    assert res.results == []


@pytest.mark.asyncio
async def test_wikipedia_search_http_non_200_raises() -> None:
    """Test search API returning HTTP 500 raises AppException."""
    mock_resp = MagicMock()
    mock_resp.status_code = 500

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_resp
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(AppException) as exc_info:
            await wikipedia_search("query")

    assert exc_info.value.status_code == 502
    assert exc_info.value.details["error_code"] == ErrorCodes.FETCH_FAILED.value


@pytest.mark.asyncio
async def test_wikipedia_search_timeout_raises() -> None:
    """Test search request timing out raises AppException 504."""
    mock_client = AsyncMock()
    mock_client.get.side_effect = httpx.TimeoutException("Search timeout")
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(AppException) as exc_info:
            await wikipedia_search("query")

    assert exc_info.value.status_code == 504
    assert exc_info.value.details["error_code"] == ErrorCodes.FETCH_FAILED.value


@pytest.mark.asyncio
async def test_wikipedia_search_generic_error_raises() -> None:
    """Test search transport failure raises AppException."""
    mock_client = AsyncMock()
    mock_client.get.side_effect = RuntimeError("Socket dropped")
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(AppException) as exc_info:
            await wikipedia_search("query")

    assert exc_info.value.status_code == 502
    assert exc_info.value.details["error_code"] == ErrorCodes.FETCH_FAILED.value


@pytest.mark.asyncio
async def test_wikipedia_read_summary_success() -> None:
    """Test retrieving article summary from Wikimedia REST API."""
    mock_payload = {
        "title": "Quantum Computing",
        "extract": "Quantum computing is a rapidly-emerging technology.",
        "pageid": 8888,
        "description": "Subfield of computer science",
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_payload

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_resp
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client):
        res = await wikipedia_read_summary("Quantum Computing", target_language="en")

    assert isinstance(res, WikipediaPageSummaryResult)
    assert res.title == "Quantum Computing"
    assert res.extract == "Quantum computing is a rapidly-emerging technology."
    assert res.pageid == 8888
    assert res.url == "https://en.wikipedia.org/wiki/Quantum_Computing"


@pytest.mark.asyncio
async def test_wikipedia_read_summary_404_raises_resource_not_found() -> None:
    """Test that HTTP 404 raises AppException(ErrorCodes.RESOURCE_NOT_FOUND)."""
    mock_resp = MagicMock()
    mock_resp.status_code = 404

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_resp
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(AppException) as exc_info:
            await wikipedia_read_summary("NonExistentArticleTitle12345", target_language="fi")

    assert exc_info.value.status_code == 404
    assert exc_info.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value


@pytest.mark.asyncio
async def test_wikipedia_read_summary_500_raises_fetch_failed() -> None:
    """Test that HTTP 500 raises AppException(ErrorCodes.FETCH_FAILED)."""
    mock_resp = MagicMock()
    mock_resp.status_code = 500

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_resp
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(AppException) as exc_info:
            await wikipedia_read_summary("Quantum", target_language="en")

    assert exc_info.value.status_code == 502
    assert exc_info.value.details["error_code"] == ErrorCodes.FETCH_FAILED.value


@pytest.mark.asyncio
async def test_wikipedia_read_summary_timeout_raises() -> None:
    """Test summary read timeout raises AppException 504."""
    mock_client = AsyncMock()
    mock_client.get.side_effect = httpx.TimeoutException("Read timeout")
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(AppException) as exc_info:
            await wikipedia_read_summary("Quantum")

    assert exc_info.value.status_code == 504
    assert exc_info.value.details["error_code"] == ErrorCodes.FETCH_FAILED.value


@pytest.mark.asyncio
async def test_wikipedia_read_summary_character_truncation() -> None:
    """Test that extract is truncated to max_chars."""
    long_extract = "A" * 1500
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"title": "Long Article", "extract": long_extract, "pageid": 1}

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_resp
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client):
        res = await wikipedia_read_summary("Long Article", max_chars=300)

    assert len(res.extract) == 300


@pytest.mark.asyncio
async def test_wikipedia_read_summary_generic_error_raises() -> None:
    """Test summary read unexpected exception raises AppException 502."""
    mock_client = AsyncMock()
    mock_client.get.side_effect = RuntimeError("Connection aborted")
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(AppException) as exc_info:
            await wikipedia_read_summary("Error Article")

    assert exc_info.value.status_code == 502
    assert exc_info.value.details["error_code"] == ErrorCodes.FETCH_FAILED.value
