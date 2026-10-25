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
from backend_v2.models.domain.tools import BaseSearchTool, StandardSearchInputDTO
from backend_v2.models.dtos.mcp import (
    MCPFunctionDefinitionDTO,
    MCPToolDeclarationDTO,
    MCPToolInputSchemaDTO,
    MCPToolSchemaPropertyDTO,
)
from backend_v2.models.enums import JSONSchemaPropertyType
from backend_v2.services.mcp.tavily_search_client import tavily_search

logger = logging.getLogger(__name__)

__all__ = [
    "TAVILY_TOOL_ID",
    "TavilyTool",
]

TAVILY_TOOL_ID = "mcp_tavily_search"


class TavilyTool(BaseSearchTool):
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
                parameters=MCPToolInputSchemaDTO(
                    type="object",
                    properties={
                        "query": MCPToolSchemaPropertyDTO(
                            type=JSONSchemaPropertyType.STRING,
                            description="The exact search query to execute on the internet.",
                        ),
                        "reasoning": MCPToolSchemaPropertyDTO(
                            type=JSONSchemaPropertyType.STRING,
                            description=(
                                "Why you believe this search is mathematically necessary. Must be 1-2 sentences."
                            ),
                        ),
                    },
                    required=["query", "reasoning"],
                    additional_properties=False,
                ),
                strict=True,
            ),
        )

    async def execute(self, **kwargs: Any) -> MCPAuditTrace:
        """Execute the Tavily search and return the MCPAuditTrace.

        Args:
            **kwargs: Keyword arguments validated strictly via StandardSearchInputDTO.

        Returns:
            MCPAuditTrace: Completed tool execution audit record.

        Raises:
            AppException: If argument validation fails (VALIDATION_FAILED) or external search fails (FETCH_FAILED).
        """
        try:
            input_dto = StandardSearchInputDTO.model_validate(kwargs)
        except Exception as e:
            msg = f"Validation failed for {self.tool_id} arguments: {e}"
            logger.error(
                "[TavilyTool] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "detail": str(e)},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "detail": str(e)},
            ) from e

        start_ms = int(time.monotonic() * 1000)
        try:
            result = await tavily_search(input_dto.query)
            response_summary = result.answer

            if (
                input_dto.target_language
                and input_dto.target_language.lower() != "en"
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

            trace_id = f"tavily_{uuid.uuid4().hex[:8]}"

            return MCPAuditTrace(
                id=trace_id,
                tool_id=self.tool_id,
                step_name=input_dto.step_name,
                claim_text=input_dto.claim_text,
                query=input_dto.query,
                reasoning=input_dto.reasoning,
                response_summary=response_summary,
                source_urls=result.source_urls,
                timestamp=datetime.now(timezone.utc),
                duration_ms=elapsed_ms,
            )
        except Exception as e:
            # Zero-Compromise Fail-Fast: Crash the step if external search fails
            msg = f"Tavily search failed for query: '{input_dto.query}'"
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
