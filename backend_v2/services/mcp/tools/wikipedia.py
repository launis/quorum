"""MCP tool implementations for Wikipedia search and article reading."""

from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any

import backend_v2.services.translation_service as translation_service
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.domain.tools import BaseSearchTool, BaseTool, StandardSearchInputDTO
from backend_v2.models.domain.wikipedia import WikipediaReadInputDTO
from backend_v2.models.dtos.mcp import MCPFunctionDefinitionDTO, MCPToolDeclarationDTO
from backend_v2.models.enums import ToolCapability
from backend_v2.services.mcp.wikipedia_client import (
    resolve_wikipedia_language,
    wikipedia_read_summary,
    wikipedia_search,
)

logger = logging.getLogger(__name__)

__all__ = [
    "WIKIPEDIA_READ_TOOL_ID",
    "WIKIPEDIA_SEARCH_TOOL_ID",
    "WikipediaReadTool",
    "WikipediaSearchTool",
]

WIKIPEDIA_SEARCH_TOOL_ID = "mcp_wikipedia_search"
WIKIPEDIA_READ_TOOL_ID = "mcp_wikipedia_read"


class WikipediaSearchTool(BaseSearchTool):
    """MCP tool for executing Wikipedia article searches."""

    @property
    def tool_id(self) -> str:
        """Return the canonical tool identifier."""
        return WIKIPEDIA_SEARCH_TOOL_ID

    @property
    def declaration(self) -> MCPToolDeclarationDTO:
        """Return the OpenAI JSON Schema declaration for Wikipedia search."""
        return MCPToolDeclarationDTO(
            type="function",
            function=MCPFunctionDefinitionDTO(
                name=WIKIPEDIA_SEARCH_TOOL_ID,
                description=(
                    "Search Wikipedia articles and return top matching titles and snippets. "
                    "Use this when you need factual encyclopedic background or to find relevant article titles."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The exact search query to execute on Wikipedia.",
                        },
                        "reasoning": {
                            "type": "string",
                            "description": (
                                "Why you believe this search is mathematically necessary. Must be 1-2 sentences."
                            ),
                        },
                    },
                    "required": ["query", "reasoning"],
                    "additionalProperties": False,
                },
                strict=True,
            ),
        )

    async def execute(self, **kwargs: Any) -> MCPAuditTrace:
        """Execute the Wikipedia search and return the MCPAuditTrace.

        Args:
            **kwargs: Keyword arguments validated strictly via StandardSearchInputDTO.

        Returns:
            MCPAuditTrace: Completed tool execution audit record.

        Raises:
            AppException: Raised with FETCH_FAILED if search fails.
        """
        input_dto = StandardSearchInputDTO.model_validate(kwargs)
        start_ms = int(time.monotonic() * 1000)
        try:
            lang = resolve_wikipedia_language(input_dto.target_language)
            result = await wikipedia_search(query=input_dto.query, target_language=lang)

            if len(result.results) == 0 and lang != "en":
                logger.info(
                    "[WikipediaSearchTool] 0 results in '%s' for '%s'. Expanding search to 'en'.",
                    lang,
                    input_dto.query,
                )
                en_result = await wikipedia_search(query=input_dto.query, target_language="en")
                if len(en_result.results) > 0:
                    result = en_result
                    lang = "en"

            if len(result.results) == 0:
                response_summary = f"No Wikipedia articles found for query: '{input_dto.query}'."
            else:
                summary_lines = [f"[{item.title}]({item.url}): {item.snippet}" for item in result.results]
                response_summary = "\n\n".join(summary_lines)

            if (
                input_dto.target_language
                and input_dto.target_language.lower() != "en"
                and lang == "en"
                and len(result.results) > 0
                and input_dto.llm_client
            ):
                response_summary = await translation_service.translate_text(
                    text=response_summary,
                    target_lang=input_dto.target_language,
                    llm_client=input_dto.llm_client,
                    source_language="English/Original",
                )

            elapsed_ms = int(time.monotonic() * 1000) - start_ms
            trace_id = f"wiki_search_{uuid.uuid4().hex[:8]}"

            return MCPAuditTrace(
                id=trace_id,
                tool_id=self.tool_id,
                step_name=input_dto.step_name,
                claim_text=input_dto.claim_text,
                query=input_dto.query,
                reasoning=input_dto.reasoning,
                response_summary=response_summary,
                source_urls=[item.url for item in result.results],
                timestamp=datetime.now(timezone.utc),
                duration_ms=elapsed_ms,
            )
        except Exception as e:
            msg = f"Wikipedia search failed for query: '{input_dto.query}'"
            logger.error(
                "[WikipediaSearchTool] %s: %s",
                ErrorCodes.FETCH_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.FETCH_FAILED.value, "detail": str(e)},
                exc_info=True,
            )
            if isinstance(e, AppException):
                raise
            raise AppException(
                message=msg,
                status_code=502,
                details={"error_code": ErrorCodes.FETCH_FAILED.value, "detail": str(e)},
            ) from e


class WikipediaReadTool(BaseTool):
    """MCP tool for retrieving the full encyclopedic summary of a specific Wikipedia article."""

    @property
    def tool_id(self) -> str:
        """Return the canonical tool identifier."""
        return WIKIPEDIA_READ_TOOL_ID

    @property
    def capability(self) -> ToolCapability:
        """Return DOCUMENT_READER capability."""
        return ToolCapability.DOCUMENT_READER

    @property
    def declaration(self) -> MCPToolDeclarationDTO:
        """Return the OpenAI JSON Schema declaration for Wikipedia article reading."""
        return MCPToolDeclarationDTO(
            type="function",
            function=MCPFunctionDefinitionDTO(
                name=WIKIPEDIA_READ_TOOL_ID,
                description=(
                    "Retrieve the full encyclopedic summary of a specific Wikipedia article by title. "
                    "Use this when you know the exact article title and need detailed factual content."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The exact title of the Wikipedia article to read.",
                        },
                        "reasoning": {
                            "type": "string",
                            "description": (
                                "Why you believe reading this specific article is mathematically necessary. "
                                "Must be 1-2 sentences."
                            ),
                        },
                    },
                    "required": ["title", "reasoning"],
                    "additionalProperties": False,
                },
                strict=True,
            ),
        )

    async def execute(self, **kwargs: Any) -> MCPAuditTrace:
        """Execute the Wikipedia article summary retrieval and return the MCPAuditTrace.

        Args:
            **kwargs: Keyword arguments validated strictly via WikipediaReadInputDTO.

        Returns:
            MCPAuditTrace: Completed tool execution audit record.

        Raises:
            AppException: Raised with RESOURCE_NOT_FOUND if missing or FETCH_FAILED if read fails.
        """
        input_dto = WikipediaReadInputDTO.model_validate(kwargs)
        start_ms = int(time.monotonic() * 1000)
        try:
            lang = resolve_wikipedia_language(input_dto.target_language)
            result = await wikipedia_read_summary(title=input_dto.title, target_language=lang)
            response_summary = result.extract

            if (
                input_dto.target_language
                and input_dto.target_language.lower() != "en"
                and lang != input_dto.target_language
                and response_summary
                and input_dto.llm_client
            ):
                response_summary = await translation_service.translate_text(
                    text=response_summary,
                    target_lang=input_dto.target_language,
                    llm_client=input_dto.llm_client,
                    source_language="English/Original",
                )

            elapsed_ms = int(time.monotonic() * 1000) - start_ms
            trace_id = f"wiki_read_{uuid.uuid4().hex[:8]}"

            return MCPAuditTrace(
                id=trace_id,
                tool_id=self.tool_id,
                step_name=input_dto.step_name,
                claim_text=input_dto.claim_text,
                query=input_dto.title,
                reasoning=input_dto.reasoning,
                response_summary=response_summary,
                source_urls=[result.url],
                timestamp=datetime.now(timezone.utc),
                duration_ms=elapsed_ms,
            )
        except Exception as e:
            msg = f"Wikipedia read summary failed for title: '{input_dto.title}'"
            logger.error(
                "[WikipediaReadTool] %s: %s",
                ErrorCodes.FETCH_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.FETCH_FAILED.value, "detail": str(e)},
                exc_info=True,
            )
            if isinstance(e, AppException):
                raise
            raise AppException(
                message=msg,
                status_code=502,
                details={"error_code": ErrorCodes.FETCH_FAILED.value, "detail": str(e)},
            ) from e
