"""Wikipedia MCP Asynchronous Client Service.

Provides asynchronous HTTP retrieval for Wikipedia Action and REST APIs with:
- Strict language validation against SUPPORTED_WIKIPEDIA_LANGUAGES SSOT
- Canonical article redirect following (follow_redirects=True)
- URL-safe title encoding and snippet HTML stripping
- Character truncation shield and Ingress Sanitization Gate
- Typed fail-fast exceptions (404 -> RESOURCE_NOT_FOUND, 500/timeout -> FETCH_FAILED)
"""

from __future__ import annotations

import html
import logging
import re
import urllib.parse

import httpx

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.wikipedia import (
    SUPPORTED_WIKIPEDIA_LANGUAGES,
    WikimediaActionApiResponseDTO,
    WikimediaActionQueryDTO,
    WikimediaActionSearchItemDTO,
    WikimediaRestSummaryResponseDTO,
    WikipediaPageSummaryResult,
    WikipediaSearchResponseDTO,
    WikipediaSearchResultItem,
)
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

__all__ = [
    "resolve_wikipedia_language",
    "wikipedia_read_summary",
    "wikipedia_search",
]


def resolve_wikipedia_language(lang_code: str | None) -> str:
    """Validate and resolve supported Wikipedia language subdomain code.

    Args:
        lang_code: Requested language code (e.g., 'fi', 'en', 'sv', 'de').

    Returns:
        Canonical 2-letter subdomain string.

    Raises:
        AppException: If language is not in SUPPORTED_WIKIPEDIA_LANGUAGES (VALIDATION_FAILED).
    """
    target = "en"
    if lang_code is not None:
        stripped = lang_code.strip().lower()
        if stripped:
            target = stripped

    prefix = target.split("-")[0].split("_")[0]
    if prefix in SUPPORTED_WIKIPEDIA_LANGUAGES:
        return prefix

    msg = f"Unsupported Wikipedia language '{lang_code}'. Supported: {sorted(SUPPORTED_WIKIPEDIA_LANGUAGES)}"
    logger.error("[WikipediaClient] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
    raise AppException(
        message=msg,
        status_code=400,
        details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "language": lang_code},
    )


async def wikipedia_search(
    query: str,
    target_language: str = "en",
    max_results: int | None = None,
) -> WikipediaSearchResponseDTO:
    """Search Wikipedia using the Action API (action=query&list=search).

    Args:
        query: Search term string.
        target_language: Target Wikipedia language code.
        max_results: Maximum items to return (defaults to Settings SSOT).

    Returns:
        Structured search response containing normalized result items.

    Raises:
        AppException: If network request, parsing, or language resolution fails (FETCH_FAILED or VALIDATION_FAILED).
    """
    lang = resolve_wikipedia_language(target_language)
    settings = get_settings()

    limit = settings.mcp_wikipedia_max_search_results
    if max_results is not None:
        limit = max_results

    endpoint = f"https://{lang}.wikipedia.org/w/api.php"
    params: dict[str, str | int] = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": min(limit, 20),
    }
    headers = {"User-Agent": settings.mcp_wikipedia_user_agent}

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=settings.mcp_wikipedia_timeout_seconds) as client:
            resp = await client.get(endpoint, params=params, headers=headers)
        if resp.status_code != 200:
            msg = f"Wikipedia search API returned HTTP {resp.status_code} for query: '{query}'"
            logger.error("[WikipediaClient] %s: %s", ErrorCodes.FETCH_FAILED.name, msg)
            raise AppException(message=msg, status_code=502, details={"error_code": ErrorCodes.FETCH_FAILED.value})

        raw_data = resp.json()
        sanitized_items: list[WikimediaActionSearchItemDTO] = []

        if type(raw_data) is dict and "query" in raw_data:
            raw_query = raw_data["query"]
            if type(raw_query) is dict and "search" in raw_query:
                raw_search = raw_query["search"]
                if type(raw_search) is list:
                    for it in raw_search:
                        if type(it) is dict:
                            ns_val = 0
                            if "ns" in it:
                                ns_val = int(it["ns"])
                            title_val = ""
                            if "title" in it:
                                title_val = str(it["title"])
                            pageid_val = 0
                            if "pageid" in it:
                                pageid_val = int(it["pageid"])
                            size_val = None
                            if "size" in it and it["size"] is not None:
                                size_val = int(it["size"])
                            wordcount_val = None
                            if "wordcount" in it and it["wordcount"] is not None:
                                wordcount_val = int(it["wordcount"])
                            snippet_val = ""
                            if "snippet" in it:
                                snippet_val = str(it["snippet"])

                            sanitized_items.append(
                                WikimediaActionSearchItemDTO(
                                    ns=ns_val,
                                    title=title_val,
                                    pageid=pageid_val,
                                    size=size_val,
                                    wordcount=wordcount_val,
                                    snippet=snippet_val,
                                )
                            )

        api_dto = WikimediaActionApiResponseDTO(query=WikimediaActionQueryDTO(search=sanitized_items))

        results = [
            WikipediaSearchResultItem(
                title=item.title,
                snippet=html.unescape(re.sub(r"<[^>]+>", "", item.snippet)).strip(),
                pageid=item.pageid,
                url=(
                    f"https://{lang}.wikipedia.org/wiki/"
                    f"{urllib.parse.quote(item.title.strip().replace(' ', '_'), safe=':/@')}"
                ),
            )
            for item in api_dto.query.search
        ]
        return WikipediaSearchResponseDTO(query=query, results=results, total_hits=len(results))
    except AppException:
        raise
    except httpx.TimeoutException as te:
        msg = f"Wikipedia search timed out after {settings.mcp_wikipedia_timeout_seconds}s for query: '{query}'"
        logger.error("[WikipediaClient] %s: %s", ErrorCodes.FETCH_FAILED.name, msg, exc_info=True)
        raise AppException(message=msg, status_code=504, details={"error_code": ErrorCodes.FETCH_FAILED.value}) from te
    except Exception as e:
        msg = f"Wikipedia search failed for query '{query}': {e}"
        logger.error("[WikipediaClient] %s: %s", ErrorCodes.FETCH_FAILED.name, msg, exc_info=True)
        raise AppException(message=msg, status_code=502, details={"error_code": ErrorCodes.FETCH_FAILED.value}) from e


async def wikipedia_read_summary(
    title: str,
    target_language: str = "en",
    max_chars: int | None = None,
) -> WikipediaPageSummaryResult:
    """Retrieve article summary from Wikimedia REST API (/page/summary/{title}).

    Args:
        title: Exact article title string.
        target_language: Target Wikipedia language code.
        max_chars: Character truncation shield limit (defaults to Settings SSOT).

    Returns:
        Structured article summary result.

    Raises:
        AppException: If article not found (RESOURCE_NOT_FOUND), language unsupported (VALIDATION_FAILED),
            or network failure occurs (FETCH_FAILED).
    """
    lang = resolve_wikipedia_language(target_language)
    settings = get_settings()

    char_limit = settings.mcp_wikipedia_max_chars
    if max_chars is not None:
        char_limit = max_chars

    encoded_title = urllib.parse.quote(title.strip().replace(" ", "_"), safe=":/@")
    endpoint = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"
    headers = {"User-Agent": settings.mcp_wikipedia_user_agent}

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=settings.mcp_wikipedia_timeout_seconds) as client:
            resp = await client.get(endpoint, headers=headers)
        if resp.status_code == 404:
            msg = f"Wikipedia article '{title}' not found in '{lang}'."
            logger.error("[WikipediaClient] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
            raise AppException(
                message=msg,
                status_code=404,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "title": title, "language": lang},
            )
        if resp.status_code != 200:
            msg = f"Wikimedia REST API returned HTTP {resp.status_code} for title '{title}'."
            logger.error("[WikipediaClient] %s: %s", ErrorCodes.FETCH_FAILED.name, msg)
            raise AppException(message=msg, status_code=502, details={"error_code": ErrorCodes.FETCH_FAILED.value})

        raw_data = resp.json()
        title_val = title
        extract_val = ""
        pageid_val = None
        desc_val = None

        if type(raw_data) is dict:
            if "title" in raw_data:
                title_val = str(raw_data["title"])
            if "extract" in raw_data:
                extract_val = str(raw_data["extract"])
            if "pageid" in raw_data and raw_data["pageid"] is not None:
                pageid_val = int(raw_data["pageid"])
            if "description" in raw_data and raw_data["description"] is not None:
                desc_val = str(raw_data["description"])

        summary_dto = WikimediaRestSummaryResponseDTO(
            title=title_val,
            extract=extract_val,
            pageid=pageid_val,
            description=desc_val,
        )

        extract = summary_dto.extract
        if len(extract) > char_limit:
            extract = extract[:char_limit]

        return WikipediaPageSummaryResult(
            title=summary_dto.title,
            extract=extract,
            pageid=summary_dto.pageid,
            url=f"https://{lang}.wikipedia.org/wiki/{encoded_title}",
        )
    except AppException:
        raise
    except httpx.TimeoutException as te:
        msg = f"Wikipedia summary read timed out after {settings.mcp_wikipedia_timeout_seconds}s for '{title}'"
        logger.error("[WikipediaClient] %s: %s", ErrorCodes.FETCH_FAILED.name, msg, exc_info=True)
        raise AppException(message=msg, status_code=504, details={"error_code": ErrorCodes.FETCH_FAILED.value}) from te
    except Exception as e:
        msg = f"Wikipedia summary read failed for '{title}': {e}"
        logger.error("[WikipediaClient] %s: %s", ErrorCodes.FETCH_FAILED.name, msg, exc_info=True)
        raise AppException(message=msg, status_code=502, details={"error_code": ErrorCodes.FETCH_FAILED.value}) from e
