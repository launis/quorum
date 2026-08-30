"""Tavily AI Search MCP Client.

Stateless async HTTP client for the Tavily AI Search API.
Adheres to RFC 7807 Dual-Reporting and Fail-Fast mandates.
"""

import asyncio
import logging
import re
import time
from typing import Any

import httpx
from tenacity import AsyncRetrying, retry_if_exception, stop_after_attempt, wait_exponential

from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.models.domain.mcp import (
    TavilyApiResponseDTO,
    TavilySearchResult,
)
from backend_v2.models.dtos.retrieval import BatchSearchQueryDTO, TavilySearchResultDTO
from backend_v2.models.enums import SearchStatus
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

# Limits are dynamically loaded via get_settings() to obey Global Config Sovereignty
# TAVILY_TIMEOUT_SECONDS = get_settings().tavily_timeout_seconds
# MAX_RESULTS = get_settings().tavily_max_results
# CONTENT_CHAR_LIMIT = get_settings().tavily_content_char_limit


def _sanitize_text(text: str) -> str:
    """Strip HTML tags and collapse whitespace from raw content.

    Args:
        text: The raw HTML text to sanitize.

    Returns:
        str: The sanitized plain text.
    """
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
        "max_results": settings.tavily_max_results,
        "include_answer": True,
        "include_raw_content": False,
        "search_depth": "basic",
    }

    start_ms = int(time.monotonic() * 1000)

    try:
        async with httpx.AsyncClient(timeout=settings.tavily_timeout_seconds) as client:
            response = await client.post(settings.tavily_api_url, json=payload)

        elapsed_ms = int(time.monotonic() * 1000) - start_ms

        if response.status_code != 200:
            msg = f"Tavily returned HTTP {response.status_code}."
            logger.error(
                f"[TavilyClient] {ErrorCodes.FETCH_FAILED.name}: {msg}",
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=502,
                details={"error_code": ErrorCodes.FETCH_FAILED.value},
            )

        try:
            data = response.json()
            # Pydantic Zero-Compromise Check
            parsed_data = TavilyApiResponseDTO.model_validate(data)
        except Exception as e:
            msg = "Tavily returned malformed JSON or failed validation."
            logger.error(
                f"[TavilyClient] {ErrorCodes.VALIDATION_FAILED.name}: {msg}",
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=502,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e

        # Parse response — Zero-Compromise Fail-Fast, no empty result fallbacks
        answer = str(parsed_data.answer or "")
        results_list = parsed_data.results

        # Allow empty results gracefully without raising exception.
        # Downstream scoring will naturally handle the lack of evidence, avoiding pipeline crashes.
        if not results_list and not answer.strip():
            logger.info("[TavilyClient] Search returned zero results; returning empty search result structure.")

        source_urls: list[str] = []

        content_parts: list[str] = []
        seen_urls: set[str] = set()

        for item in results_list:
            url = str(item.url)
            if url and url not in seen_urls:
                source_urls.append(url)
                seen_urls.add(url)

            snippet = str(item.content)
            if snippet:
                content_parts.append(_sanitize_text(snippet))

        raw_content = "\n\n".join(content_parts)[: settings.tavily_content_char_limit]

        logger.info(
            "[TavilyClient] Search completed.",
            extra={
                "results": len(results_list),
                "urls": len(source_urls),
                "duration_ms": elapsed_ms,
            },
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
        msg = "Tavily search timed out."
        logger.error(
            f"[TavilyClient] {ErrorCodes.FETCH_FAILED.name}: {msg}",
            exc_info=True,
        )
        raise AppException(
            message=msg,
            status_code=502,
            details={"error_code": ErrorCodes.FETCH_FAILED.value},
        ) from e
    except httpx.HTTPError as e:
        msg = "Tavily network error."
        logger.error(
            f"[TavilyClient] {ErrorCodes.FETCH_FAILED.name}: {msg}",
            exc_info=True,
        )
        raise AppException(
            message=msg,
            status_code=502,
            details={"error_code": ErrorCodes.FETCH_FAILED.value},
        ) from e


def _is_transient_error(e: BaseException) -> bool:
    if isinstance(e, AppException):
        err_code = e.details.get("error_code") if e.details else None
        if err_code == ErrorCodes.VALIDATION_FAILED.value:
            return False  # Structural error, do not retry
        if err_code == ErrorCodes.FETCH_FAILED.value:
            return True  # Network error, retry
    return False


async def batch_tavily_search(document_text: str, task_executor: Any, llm_client: Any) -> list[TavilySearchResultDTO]:
    """Execute a batch concurrent Tavily search from an extracted document text.

    Args:
        document_text: Raw input text to extract queries from.
        task_executor: Injected LLMTaskExecutor.
        llm_client: Injected LLMClient.

    Returns:
        List of TavilySearchResultDTO containing results or DLQ status.

    Raises:
        AppException: If initial extraction fails.
    """
    if not document_text.strip():
        return []

    system_prompt = (
        "Extract required fact-checking queries from the provided document. "
        "Return a list of precise, verifiable search queries."
    )
    user_msg = f"<source_data>\n{document_text}\n</source_data>"

    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_msg}]

    try:
        dto, _usage = await task_executor.execute_structured_task(
            client=llm_client, messages=messages, response_model=BatchSearchQueryDTO
        )
    except Exception as e:
        msg = "Failed to extract search queries for batch Tavily."
        logger.error(f"[BatchTavily] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
        raise AppException(
            message=msg, status_code=502, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
        ) from e

    extracted_queries = dto.queries
    if not extracted_queries:
        return []

    # Step 3.1b: Deduplication Hash Mapping
    normalized_map: dict[str, list[str]] = {}
    for q in extracted_queries:
        norm_q = q.strip().casefold()
        if not norm_q:
            continue
        if norm_q not in normalized_map:
            normalized_map[norm_q] = []
        normalized_map[norm_q].append(q)

    results: list[TavilySearchResultDTO] = []
    settings = get_settings()
    sem = asyncio.Semaphore(settings.tavily_max_concurrent_requests)

    async def _worker(norm_query: str) -> None:
        async with sem:
            try:
                async for attempt in AsyncRetrying(
                    stop=stop_after_attempt(3),
                    wait=wait_exponential(multiplier=1, min=2, max=10),
                    retry=retry_if_exception(_is_transient_error),
                    reraise=True,
                ):
                    with attempt:
                        res = await tavily_search(norm_query)

                # Thread-safe append (lists are thread-safe in python asyncio)
                results.append(
                    TavilySearchResultDTO(
                        query=norm_query,
                        answer=res.answer,
                        source_urls=res.source_urls,
                        raw_content=res.raw_content,
                        duration_ms=res.duration_ms,
                        status=SearchStatus.COMPLETED,
                    )
                )
            except AppException as e:
                err_code = e.details.get("error_code") if e.details else None
                if err_code == ErrorCodes.VALIDATION_FAILED.value:
                    status = SearchStatus.DLQ_ERROR
                    logger.error(
                        f"[BatchTavily] {ErrorCodes.VALIDATION_FAILED.name}: Structural validation failed for query '{norm_query}'",
                        extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "query": norm_query},
                    )
                else:
                    status = SearchStatus.DLQ_TIMEOUT
                    logger.error(
                        f"[BatchTavily] {ErrorCodes.FETCH_FAILED.name}: Transient network errors exhausted for query '{norm_query}'",
                        extra={"error_code": ErrorCodes.FETCH_FAILED.value, "query": norm_query},
                    )

                results.append(
                    TavilySearchResultDTO(
                        query=norm_query, answer="", source_urls=[], raw_content="", duration_ms=0, status=status
                    )
                )
            except (OSError, ValueError, KeyError, RuntimeError, TypeError) as e:
                logger.error(
                    f"[BatchTavily] {ErrorCodes.INTERNAL_SERVER_ERROR.name}: Unexpected error for query '{norm_query}': {e}",
                    extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value, "query": norm_query},
                    exc_info=True,
                )
                results.append(
                    TavilySearchResultDTO(
                        query=norm_query,
                        answer="",
                        source_urls=[],
                        raw_content="",
                        duration_ms=0,
                        status=SearchStatus.DLQ_ERROR,
                    )
                )

    # Step 3.2: TaskGroup bounded concurrency
    async with asyncio.TaskGroup() as tg:
        for norm_q in normalized_map.keys():
            tg.create_task(_worker(norm_q))

    # Fan-out mapping
    final_results: list[TavilySearchResultDTO] = []
    for res in results:
        original_queries = (
            normalized_map[res.query.casefold()] if res.query.casefold() in normalized_map else [res.query]
        )
        for orig_q in original_queries:
            final_results.append(
                TavilySearchResultDTO(
                    query=orig_q,
                    answer=res.answer,
                    source_urls=res.source_urls,
                    raw_content=res.raw_content,
                    duration_ms=res.duration_ms,
                    status=res.status,
                )
            )

    return final_results
