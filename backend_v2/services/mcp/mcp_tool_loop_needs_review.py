"""MCP Tool Loop Conductor.

Isolates the LLM tool-calling cycle from the DAG executor (SRP).
Implements a 2-phase execution:
  Phase 1 (Probe): LLM chat with tool declarations — decides if external search is needed.
  Phase 2 (Completion): Injects evidence as ToolMessage, then forces structured matrix output.

Adheres to RFC 7807 Dual-Reporting and Graceful Degradation (§6.3) mandates.
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, TypeVar

from fastapi import status
from pydantic import BaseModel

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.mcp import (
    MCPSynthesisInstructionsDTO,
    MCPToolLoopResult,
    OpenAIProbeResponseDTO,
    TavilyToolArgsDTO,
)
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.v2_core import MCPAuditTrace
from backend_v2.services.mcp.tavily_search_client import tavily_search

logger = logging.getLogger(__name__)

# NOTE (Architecture): Hard cap to prevent infinite LLM↔Tool loops.
# EPIC §3 "The Infinite Loop Limit".
MAX_TOOL_CALLS_PER_STEP = 3

# The only tool currently registered in the system.
TAVILY_TOOL_ID = "mcp_tavily_search"

# OpenAI function-calling schema for Tavily search.
TAVILY_TOOL_DECLARATION: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": TAVILY_TOOL_ID,
        "description": (
            "Search the web for current, factual information using Tavily AI Search. "
            "Use this tool when the user's input references real-world events, statistics, "
            "organizations, or claims that require external verification."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to look up.",
                }
            },
            "required": ["query"],
        },
    },
}


def _build_tool_declarations(allowed_tools: list[str]) -> list[dict[str, Any]]:
    """Build OpenAI-format tool declarations from allowed tool IDs.

    Args:
        allowed_tools: List of unique tool string IDs.

    Returns:
        List of raw dictionaries defining OpenAI-compatible tool specifications.
    """
    declarations: list[dict[str, Any]] = []
    for tool_id in allowed_tools:
        if tool_id == TAVILY_TOOL_ID:
            declarations.append(TAVILY_TOOL_DECLARATION)
        else:
            logger.warning("Unknown tool_id in allowed_tools — skipping.", extra={"tool_id": tool_id})
    return declarations


async def _execute_tavily_search(
    query: str, step_name: str, target_language: str = "en", llm_client: Any = None
) -> MCPAuditTrace:
    """Execute a Tavily search and return an audit trace.

    Graceful Degradation (§6.3): Tavily failures return an audit trace with empty results,
    allowing the LLM to proceed without external evidence. Translates evidence on-the-fly.

    Args:
        query: Raw search criteria text.
        step_name: The matching step segment identifier context.
        target_language: Target output locale configuration.
        llm_client: Optional client wrapper for localized refinement.

    Returns:
        Audit trace record wrapping downstream web results.

    Raises:
        AppException: Propagated or converted network execution fault.
    """
    start_ms = int(time.monotonic() * 1000)
    try:
        result = await tavily_search(query)
        response_summary = result.answer
        elapsed_ms = int(time.monotonic() * 1000) - start_ms

        return MCPAuditTrace(
            tool_id=TAVILY_TOOL_ID,
            step_name=step_name,
            query=query,
            response_summary=response_summary,
            source_urls=result.source_urls,
            timestamp=datetime.now(timezone.utc),
            duration_ms=elapsed_ms,
        )
    except Exception as e:
        msg = f"Tavily search failed for query: '{query}'"
        logger.error(
            "[MCPToolLoop] %s: %s",
            ErrorCodes.FETCH_FAILED.name,
            msg,
            extra={"detail": str(e)},
            exc_info=True,
        )
        if isinstance(e, AppException):
            raise
        raise AppException(
            message=msg,
            status_code=status.HTTP_502_BAD_GATEWAY,
            details={"error_code": ErrorCodes.FETCH_FAILED.value, "detail": str(e)},
        ) from e


def _build_tool_evidence_message(audit: MCPAuditTrace, tool_call_id: str) -> dict[str, str]:
    """Convert an MCPAuditTrace into a ToolMessage for LLM injection.

    Args:
        audit: The audit trace from the tool execution.
        tool_call_id: The ORIGINAL call ID from the LLM's tool_call response.

    Returns:
        Strict JSON-like dictionary containing role, tool call identifier, and XML formatted content.
    """
    if not audit.response_summary and not audit.source_urls:
        return {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": (
                "<tool_response><info>Search returned no results. "
                "Proceed with your evaluation using available context only.</info></tool_response>"
            ),
        }

    content = f"<tool_response>\n  <query>{audit.query}</query>\n"
    if audit.response_summary:
        content += f"  <summary>{audit.response_summary}</summary>\n"
    if audit.source_urls:
        content += "  <sources>\n"
        for url in audit.source_urls:
            content += f"    <url>{url}</url>\n"
        content += "  </sources>\n"
    content += "</tool_response>"

    return {
        "role": "tool",
        "tool_call_id": tool_call_id,
        "content": content,
    }


T = TypeVar("T", bound=BaseModel)


async def execute_tool_loop(
    llm_client: Any,
    executor: Any,
    messages: list[dict[str, Any]],
    response_model: type[T],
    allowed_tools: list[str],
    step_name: str,
    mock_identity: str | None = None,
    target_language: str = "en",
    synthesis_instructions: dict[str, Any] | None = None,
    validation_context: dict[str, Any] | None = None,
) -> MCPToolLoopResult:
    """Execute the MCP Tool Loop — 2-phase LLM execution with optional tool calling.

    Phase 1 (Probe): Ask LLM with tool declarations if it wants to search.
    Phase 2 (Completion): Inject evidence, force structured output.

    Args:
        llm_client: Bound LLMClient instance.
        executor: Bound LLMTaskExecutor instance.
        messages: The compiled chat messages (system + user).
        response_model: Pydantic schema for structured output.
        allowed_tools: List of tool IDs allowed for this step.
        step_name: Current DAG step name (for audit logging).
        mock_identity: Mock identity for testing.
        target_language: Optional user requested language.
        synthesis_instructions: OutputProfile limits and preamble constraints.
        validation_context: Additional validation schemas.

    Returns:
        MCPToolLoopResult structure with parsed model data and execution telemetry traces.

    Raises:
        AppException: Structured enterprise compliance error.
    """
    audit_traces: list[MCPAuditTrace] = []
    tool_declarations = _build_tool_declarations(allowed_tools)

    if not tool_declarations:
        result, usage = await executor.execute_structured_task(
            client=llm_client,
            messages=messages,
            response_model=response_model,
            mock_identity=mock_identity,
            validation_context=validation_context,
        )
        result_data = result.model_dump(mode="json")
        usage = usage if usage else TokenUsage()
        return MCPToolLoopResult(
            result_data=result_data,
            audit_traces=[],
            usage=usage,
        )

    probe_messages = list(messages)
    tool_call_count = 0
    effective_max_calls = MAX_TOOL_CALLS_PER_STEP

    while tool_call_count < effective_max_calls:
        current_tool_choice = "auto"
        probe_response = None
        try:
            probe_response_raw = await executor.execute_chat_task(
                client=llm_client,
                messages=probe_messages,
                tools=tool_declarations,
                tool_choice=current_tool_choice,
            )

            if isinstance(probe_response_raw, str):
                break

            probe_response = OpenAIProbeResponseDTO.model_validate(probe_response_raw)
        except Exception as e:
            msg = f"Phase 1 LLM probing failed or returned invalid structure for step '{step_name}'."
            logger.error("[MCPToolLoop] %s: %s", ErrorCodes.FETCH_FAILED.name, msg, exc_info=True)
            if isinstance(e, AppException):
                raise
            raise AppException(
                message=msg,
                status_code=status.HTTP_502_BAD_GATEWAY,
                details={"error_code": ErrorCodes.FETCH_FAILED.value},
            ) from e

        if not probe_response or not probe_response.tool_calls:
            break

        invalid_tools_detected = False
        for tc_dto in probe_response.tool_calls:
            if tool_call_count >= effective_max_calls:
                logger.warning(
                    "Max tool calls reached for step. Forcing completion.",
                    extra={
                        "max_calls": effective_max_calls,
                        "step_name": step_name,
                    },
                )
                break

            tool_name = tc_dto.function.name
            tool_args_raw = tc_dto.function.arguments

            if isinstance(tool_args_raw, str):
                try:
                    tool_args = json.loads(tool_args_raw)
                except Exception as e:
                    msg = "LLM returned malformed JSON for tool arguments."
                    logger.error("[MCPToolLoop] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                    raise AppException(
                        message=msg,
                        status_code=status.HTTP_400_BAD_REQUEST,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    ) from e
            else:
                tool_args = tool_args_raw

            if tool_name != TAVILY_TOOL_ID:
                logger.warning(
                    "LLM hallucinated unknown tool — skipping.",
                    extra={
                        "error_code": ErrorCodes.VALIDATION_FAILED.name,
                    },
                )
                invalid_tools_detected = True
                continue

            try:
                tavily_args = TavilyToolArgsDTO.model_validate(tool_args)
                query = tavily_args.query
            except Exception as e:
                msg = "LLM returned invalid arguments for Tavily."
                logger.error("[MCPToolLoop] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e

            if not query or not str(query).strip():
                msg = "LLM returned empty query for Tavily."
                logger.error("[MCPToolLoop] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

            logger.info(
                "Executing Tavily search",
                extra={
                    "step_name": step_name,
                },
            )

            audit = await _execute_tavily_search(str(query), step_name, target_language, llm_client)
            audit_traces.append(audit)
            tool_call_count += 1

            original_call_id = tc_dto.id
            evidence_msg = _build_tool_evidence_message(audit, tool_call_id=original_call_id)

            probe_messages.append(
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tc_dto.model_dump(mode="json", exclude_none=True)],
                }
            )
            probe_messages.append(evidence_msg)

        if invalid_tools_detected and tool_call_count == 0:
            logger.warning(
                "Forced tool call yielded invalid output. Breaking to Phase 2.", extra={"step_name": step_name}
            )
            break

        if tool_call_count >= effective_max_calls:
            break

    final_messages = list(probe_messages)

    if audit_traces:
        final_messages.append(
            {
                "role": "user",
                "content": (
                    "<system_instruction>\n"
                    "  <objective>EVIDENCE INJECTION COMPLETE</objective>\n"
                    "  <rule>You now have external search evidence above.</rule>\n"
                    "  <rule>Complete the evaluation matrix using both the original context AND "
                    "the search evidence.</rule>\n"
                    "  <rule>Output your response strictly in the required JSON schema format.</rule>\n"
                    "</system_instruction>"
                ),
            }
        )

    if synthesis_instructions:
        try:
            instructions = MCPSynthesisInstructionsDTO.model_validate(synthesis_instructions)
        except Exception as e:
            msg = "Failed to validate synthesis_instructions."
            logger.error("[MCPToolLoop] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e

        formatting_msg = "<execution_parameters>\n  <output_profile_formatting_constraints>\n"
        if instructions.synthesis_preamble:
            formatting_msg += f"    <synthesis_preamble>{instructions.synthesis_preamble}</synthesis_preamble>\n"
        if instructions.synthesis_length_limit:
            limit = instructions.synthesis_length_limit
            formatting_msg += f"    <synthesis_length_limit>{limit}</synthesis_length_limit>\n"
        formatting_msg += "  </output_profile_formatting_constraints>\n</execution_parameters>\n\n"

        if final_messages and "role" in final_messages[0] and final_messages[0]["role"] == "system":
            original = final_messages[0]["content"]
            final_messages[0]["content"] = f" {formatting_msg}{original}"
        else:
            final_messages.insert(0, {"role": "system", "content": formatting_msg})

    try:
        result, usage = await executor.execute_structured_task(
            client=llm_client,
            messages=final_messages,
            response_model=response_model,
            mock_identity=mock_identity,
            validation_context=validation_context,
        )
        result_data = result.model_dump(mode="json")
        usage = usage if usage else TokenUsage()
        return MCPToolLoopResult(
            result_data=result_data,
            audit_traces=audit_traces,
            usage=usage,
        )
    except AppException:
        raise
    except Exception as e:
        logger.error(
            "Phase 2 completion failed for step",
            extra={
                "error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED.name,
                "step_name": step_name,
                "detail": str(e),
            },
            exc_info=True,
        )
        raise AppException(
            message=f"Tool Loop Phase 2 failed for step '{step_name}': {e}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED.value},
        ) from e
