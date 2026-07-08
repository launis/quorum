import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.tools import BaseTool
from backend_v2.models.v2_core import MCPAuditTrace
from backend_v2.services.mcp.tavily_search_client import tavily_search

logger = logging.getLogger(__name__)

TAVILY_TOOL_ID = "mcp_tavily_search"


class TavilyTool(BaseTool):
    """MCP tool for executing Tavily web searches."""

    @property
    def tool_id(self) -> str:
        return TAVILY_TOOL_ID

    @property
    def declaration(self) -> dict[str, Any]:
        """Return the OpenAI JSON Schema declaration for Tavily."""
        return {
            "type": "function",
            "function": {
                "name": TAVILY_TOOL_ID,
                "description": (
                    "Perform an explicit search on the live internet using Tavily. "
                    "Use this ONLY when the necessary facts are completely missing from the provided "
                    "context and you require up-to-date or external world knowledge."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The exact search query to execute on the internet.",
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "Why you believe this search is mathematically necessary. Must be 1-2 sentences.",
                        },
                    },
                    "required": ["query", "reasoning"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
        }

    async def execute(self, **kwargs: Any) -> MCPAuditTrace:
        """Execute the Tavily search and return the MCPAuditTrace.

        Expected kwargs:
            query (str): The search query.
            step_name (str): Current step name for auditing.
            target_language (str, optional): Target translation language.
            llm_client (Any, optional): Bound LLM client for translation.
            reasoning (str, optional): The reasoning for the search.
            claim_text (str, optional): The physical claim text being verified.
        """
        query = kwargs.get("query", "")
        step_name = kwargs.get("step_name", "unknown_step")
        target_language = kwargs.get("target_language", "")
        llm_client = kwargs.get("llm_client")
        reasoning = kwargs.get("reasoning", "")
        claim_text = kwargs.get("claim_text")

        start_ms = int(time.monotonic() * 1000)
        try:
            result = await tavily_search(query)
            response_summary = result.answer

            if target_language and target_language.lower() != "en" and response_summary and llm_client:
                from backend_v2.services.translation_service import translate_text

                response_summary = await translate_text(
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
                extra={"detail": str(e)},
                exc_info=True,
            )
            if isinstance(e, AppException):
                raise
            raise AppException(
                message=msg,
                status_code=502,
                details={"error_code": ErrorCodes.FETCH_FAILED.value, "detail": str(e)},
            ) from e
