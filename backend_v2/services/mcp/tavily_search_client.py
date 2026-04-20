"""Tavily AI Search MCP Client.

Stateless async HTTP client for the Tavily AI Search API.
Adheres to RFC 7807 Dual-Reporting and Fail-Fast mandates.
"""

import logging
import re
import time
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field

from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

# NOTE (Architecture): Timeout is enforced per §3.4 Reliability Strategy.
# Tavily typically responds in 1-3s; 15s is a generous safety margin for Serverless.
TAVILY_TIMEOUT_SECONDS = 15
TAVILY_API_URL = "https://api.tavily.com/search"
MAX_RESULTS = 5
CONTENT_CHAR_LIMIT = 8000


class TavilySearchResult(BaseModel):
    """Parsed Tavily response for downstream consumption."""

    model_config = ConfigDict(strict=True)

    query: str = Field(description="Echo of the original search query.")
    answer: str = Field(default="", description="AI-generated summary from Tavily.")
    source_urls: list[str] = Field(default_factory=list, description="Deduplicated source URLs.")
    raw_content: str = Field(default="", description="Concatenated source texts (truncated).")
    duration_ms: int = Field(default=0, description="Round-trip latency in milliseconds.")


def _sanitize_text(text: str) -> str:
    """Strip HTML tags and collapse whitespace from raw content."""
    cleaned = re.sub(r"<[^>]+>", " ", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


async def tavily_search(query: str) -> TavilySearchResult:
    """Execute a Tavily AI Search and return structured results.

    Args:
        query: The search query string.

    Returns:
        TavilySearchResult with answer, source URLs, and raw content.

    Raises:
        ConfigurationError: If the Tavily API key is not configured.
        AppException: On network failures or malformed API responses.
    """
    if not query or not str(query).strip():
        msg = "Tavily search query cannot be empty. Zero-Compromise Fail-Fast enforced."
        logger.error("[TavilyClient] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    settings = get_settings()
    api_key = settings.tavily_api_key

    if not api_key:
        msg = "Tavily API key is not configured. Set TAVILY_API_KEY in .env."
        logger.error("[TavilyClient] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
        raise ConfigurationError(message=msg)

    payload: dict[str, Any] = {
        "api_key": api_key,
        "query": query,
        "max_results": MAX_RESULTS,
        "include_answer": True,
        "include_raw_content": False,
        "search_depth": "basic",
    }

    start_ms = int(time.monotonic() * 1000)

    try:
        async with httpx.AsyncClient(timeout=TAVILY_TIMEOUT_SECONDS) as client:
            response = await client.post(TAVILY_API_URL, json=payload)

        elapsed_ms = int(time.monotonic() * 1000) - start_ms

        if response.status_code != 200:
            msg = f"Tavily returned HTTP {response.status_code} for query: {query}"
            logger.error(
                f"[TavilyClient] {ErrorCodes.FETCH_FAILED.name}: {msg}",
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=502,
                details={"error_code": ErrorCodes.FETCH_FAILED, "query": query},
            )

        try:
            data = response.json()
        except Exception as e:
            msg = f"Tavily returned malformed JSON for query: {query}"
            logger.error(
                f"[TavilyClient] {ErrorCodes.VALIDATION_FAILED.name}: {msg}: {e}",
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=502,
                details={"error_code": ErrorCodes.VALIDATION_FAILED, "query": query},
            ) from e

        # Parse response — Zero-Compromise Fail-Fast, no empty result fallbacks
        answer = str(data.get("answer", "") or "")
        results_list: list[dict[str, Any]] = data.get("results", [])

        if not results_list and not answer.strip():
            msg = f"Tavily search returned zero results for query: '{query}'. Zero-Compromise Fail-Fast enforced."
            logger.error("[TavilyClient] %s: %s", ErrorCodes.FETCH_FAILED.name, msg)
            raise AppException(
                message=msg,
                status_code=404,
                details={"error_code": ErrorCodes.FETCH_FAILED.value, "query": query},
            )

        source_urls: list[str] = []
        content_parts: list[str] = []
        seen_urls: set[str] = set()

        for item in results_list:
            url = str(item.get("url", ""))
            if url and url not in seen_urls:
                source_urls.append(url)
                seen_urls.add(url)

            snippet = str(item.get("content", ""))
            if snippet:
                content_parts.append(_sanitize_text(snippet))

        raw_content = "\n\n".join(content_parts)[:CONTENT_CHAR_LIMIT]

        logger.info(
            f"[TavilyClient] Search completed: query='{query}', "
            f"results={len(results_list)}, urls={len(source_urls)}, "
            f"duration={elapsed_ms}ms"
        )

        return TavilySearchResult(
            query=query,
            answer=answer,
            source_urls=source_urls,
            raw_content=raw_content,
            duration_ms=elapsed_ms,
        )

    except AppException:
        raise
    except httpx.TimeoutException as e:
        msg = f"Tavily search timed out for query: {query}"
        logger.error(
            f"[TavilyClient] {ErrorCodes.FETCH_FAILED.name}: {msg}: {e}",
            exc_info=True,
        )
        raise AppException(
            message=msg,
            status_code=502,
            details={"error_code": ErrorCodes.FETCH_FAILED, "query": query},
        ) from e
    except httpx.HTTPError as e:
        msg = f"Tavily network error for query: {query}"
        logger.error(
            f"[TavilyClient] {ErrorCodes.FETCH_FAILED.name}: {msg}: {e}",
            exc_info=True,
        )
        raise AppException(
            message=msg,
            status_code=502,
            details={"error_code": ErrorCodes.FETCH_FAILED, "query": query},
        ) from e
