"""MCP tool implementation for Tavily web search."""

from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any

import backend_v2.services.translation_service as translation_service
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.domain.tools import BaseTool
from backend_v2.models.dtos.mcp import MCPFunctionDefinitionDTO, MCPToolDeclarationDTO
from backend_v2.services.mcp.tavily_search_client import tavily_search

logger = logging.getLogger(__name__)

__all__ = [
    "TAVILY_TOOL_ID",
    "TavilyTool",
]

TAVILY_TOOL_ID = "mcp_tavily_search"


class TavilyTool(BaseTool):
    """MCP tool for executing Tavily web searches."""

    @property
    def tool_id(self) -> str:
        """Return the canonical tool identifier."""
        return TAVILY_TOOL_ID

    @property
    def declaration(self) -> MCPToolDeclarationDTO:
        """Return the OpenAI JSON Schema declaration for Tavily."""
        return MCPToolDeclarationDTO(
            type="function",
            function=MCPFunctionDefinitionDTO(
                name=TAVILY_TOOL_ID,
                description=(
                    "Perform an explicit search on the live internet using Tavily. "
                    "Use this ONLY when the necessary facts are completely missing from the provided "
                    "context and you require up-to-date or external world knowledge."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The exact search query to execute on the internet.",
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
        """Execute the Tavily search and return the MCPAuditTrace.

        Args:
            **kwargs: Arbitrary keyword arguments including query, step_name,
                target_language, llm_client, reasoning, and claim_text.

        Returns:
            MCPAuditTrace: Completed tool execution audit record.

        Raises:
            AppException: Raised with FETCH_FAILED error code if external search fails.
        """
        query = ""
        if "query" in kwargs and kwargs["query"] is not None:
            query = str(kwargs["query"])

        step_name = "unknown_step"
        if "step_name" in kwargs and kwargs["step_name"] is not None:
            step_name = str(kwargs["step_name"])

        target_language = ""
        if "target_language" in kwargs and kwargs["target_language"] is not None:
            target_language = str(kwargs["target_language"])

        llm_client = None
        if "llm_client" in kwargs:
            llm_client = kwargs["llm_client"]

        reasoning = ""
        if "reasoning" in kwargs and kwargs["reasoning"] is not None:
            reasoning = str(kwargs["reasoning"])

        claim_text = None
        if "claim_text" in kwargs and kwargs["claim_text"] is not None:
            claim_text = str(kwargs["claim_text"])

        start_ms = int(time.monotonic() * 1000)
        try:
            result = await tavily_search(query)
            response_summary = result.answer

            if target_language and target_language.lower() != "en" and response_summary and llm_client:
                response_summary = await translation_service.translate_text(
                    text=response_summary,
                    target_lang=target_language,
                    llm_client=llm_client,
                    source_language="English/Original",
                )

            elapsed_ms = int(time.monotonic() * 1000) - start_ms

            trace_id = f"tavily_{uuid.uuid4().hex[:8]}"

            return MCPAuditTrace(
                id=trace_id,
                tool_id=self.tool_id,
                step_name=step_name,
                claim_text=claim_text,
                query=query,
                reasoning=reasoning,
                response_summary=response_summary,
                source_urls=result.source_urls,
                timestamp=datetime.now(timezone.utc),
                duration_ms=elapsed_ms,
            )
        except Exception as e:
            # Zero-Compromise Fail-Fast: Crash the step if external search fails
            msg = f"Tavily search failed for query: '{query}'"
            logger.error(
                "[TavilyTool] %s: %s",
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
