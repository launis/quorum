"""MCP Tool Loop Conductor.

Isolates the LLM tool-calling cycle from the DAG executor (SRP).
Implements a 2-phase execution:
  Phase 1 (Probe): LLM chat with tool declarations — decides if external search is needed.
  Phase 2 (Completion): Injects evidence as ToolMessage, then forces structured matrix output.

Adheres to RFC 7807 Dual-Reporting and Graceful Degradation (§6.3) mandates.
"""

import logging
import time
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.v2_core import MCPAuditTrace

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


class MCPToolLoopResult(BaseModel):
    """Result from the Tool Loop — structured output + audit trail."""

    model_config = ConfigDict(strict=True)

    result_data: dict[str, Any] = Field(description="Final structured output dict.")
    audit_traces: list[MCPAuditTrace] = Field(default_factory=list, description="Audit log of all tool invocations.")
    usage: dict[str, Any] = Field(default_factory=dict, description="Cumulative token usage.")


def _build_tool_declarations(allowed_tools: list[str]) -> list[dict[str, Any]]:
    """Build OpenAI-format tool declarations from allowed tool IDs."""
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
    """
    from backend_v2.services.mcp.tavily_search_client import tavily_search

    start_ms = int(time.monotonic() * 1000)
    try:
        result = await tavily_search(query)
        response_summary = result.answer

        if target_language and target_language != "en" and llm_client:
            logger.info("[MCPToolLoop] Translating search evidence to '%s'...", target_language)
            try:
                trans_prompt = (
                    f"Translate the following search summary into {target_language} accurately. "
                    f"Return only the translated text.\n\nSummary:\n{response_summary}"
                )
                trans_resp = await llm_client.run_chat(messages=[{"role": "user", "content": trans_prompt}])
                if trans_resp and isinstance(trans_resp, str):
                    response_summary = trans_resp.strip()
            except Exception as tr_err:
                logger.error(
                    "Evidence translation failed",
                    extra={
                        "error_code": ErrorCodes.INTERNAL_SERVER_ERROR.name,
                        "target_language": target_language,
                        "detail": str(tr_err),
                    },
                    exc_info=True,
                )

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
        # Graceful Degradation: log but don't crash the step
        elapsed_ms = int(time.monotonic() * 1000) - start_ms
        logger.error(
            "Tavily search failed",
            extra={
                "error_code": ErrorCodes.FETCH_FAILED.name,
                "query": query,
                "detail": str(e),
            },
            exc_info=True,
        )
        return MCPAuditTrace(
            tool_id=TAVILY_TOOL_ID,
            step_name=step_name,
            query=query,
            response_summary="",
            source_urls=[],
            timestamp=datetime.now(timezone.utc),
            duration_ms=elapsed_ms,
        )


def _build_tool_evidence_message(audit: MCPAuditTrace, tool_call_id: str) -> dict[str, str]:
    """Convert an MCPAuditTrace into a ToolMessage for LLM injection.

    Args:
        audit: The audit trace from the tool execution.
        tool_call_id: The ORIGINAL call ID from the LLM's tool_call response.
                      Must match exactly for LiteLLM/Gemini transformation.
    """
    if not audit.response_summary and not audit.source_urls:
        return {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": "[Search returned no results. Proceed with your evaluation using available context only.]",
        }

    sources = "\n".join(f"- {url}" for url in audit.source_urls)
    content = f"Search Results for: '{audit.query}'\n\n"
    if audit.response_summary:
        content += f"Summary: {audit.response_summary}\n\n"
    if sources:
        content += f"Sources:\n{sources}"

    return {
        "role": "tool",
        "tool_call_id": tool_call_id,
        "content": content,
    }


async def execute_tool_loop[T: BaseModel](
    llm_client: Any,
    messages: list[dict[str, Any]],
    response_model: type[T],
    allowed_tools: list[str],
    step_name: str,
    mock_identity: str | None = None,
    target_language: str = "en",
) -> MCPToolLoopResult:
    """Execute the MCP Tool Loop — 2-phase LLM execution with optional tool calling.

    Phase 1 (Probe): Ask LLM with tool declarations if it wants to search.
    Phase 2 (Completion): Inject evidence, force structured output.

    Args:
        llm_client: Bound LLMClient instance.
        messages: The compiled chat messages (system + user).
        response_model: Pydantic schema for structured output.
        allowed_tools: List of tool IDs allowed for this step.
        step_name: Current DAG step name (for audit logging).
        mock_identity: Mock identity for testing.

    Returns:
        MCPToolLoopResult with structured data and audit traces.
    """
    audit_traces: list[MCPAuditTrace] = []
    tool_declarations = _build_tool_declarations(allowed_tools)

    if not tool_declarations:
        # No valid tools — direct passthrough (zero overhead)
        result, usage = await llm_client.run_structured_task(
            messages=messages,
            response_model=response_model,
            mock_identity=mock_identity,
        )
        return MCPToolLoopResult(
            result_data=result.model_dump(mode="json"),
            audit_traces=[],
            usage=usage,
        )

    # --- PHASE 1: Probe with tool_choice="auto" ---
    probe_messages = list(messages)  # defensive copy
    tool_call_count = 0

    while tool_call_count < MAX_TOOL_CALLS_PER_STEP:
        # The Root Cause Fix: Empower the LLM to decide autonomously (Zero-Forcing).
        # Forcing 'required' when the LLM has nothing to search causes empty query hallucinations.
        current_tool_choice = "auto"
        try:
            probe_response = await llm_client.run_chat(
                messages=probe_messages,
                tools=tool_declarations,
                tool_choice=current_tool_choice,
            )
        except Exception as e:
            # If Phase 1 probe fails, fall through to Phase 2 with no evidence
            logger.error(
                "Phase 1 probe failed for step",
                extra={
                    "error_code": ErrorCodes.FETCH_FAILED.name,
                    "step_name": step_name,
                    "detail": str(e),
                },
                exc_info=True,
            )
            break

        # Check if LLM returned tool calls
        if not isinstance(probe_response, dict) or "tool_calls" not in probe_response:
            # LLM decided no search needed — proceed directly to Phase 2
            break

        response_tool_calls = probe_response.get("tool_calls", [])
        if not response_tool_calls:
            break

        # Process each tool call
        invalid_tools_detected = False
        for tc in response_tool_calls:
            if tool_call_count >= MAX_TOOL_CALLS_PER_STEP:
                logger.warning(
                    "Max tool calls reached for step. Forcing completion.",
                    extra={
                        "max_calls": MAX_TOOL_CALLS_PER_STEP,
                        "step_name": step_name,
                    },
                )
                break

            func = tc.get("function", {})
            tool_name = func.get("name", "")
            tool_args = func.get("arguments", {})

            if isinstance(tool_args, str):
                import json

                try:
                    tool_args = json.loads(tool_args)
                except Exception:
                    tool_args = {"query": tool_args}

            if tool_name != TAVILY_TOOL_ID:
                logger.warning(
                    "LLM hallucinated unknown tool — skipping.",
                    extra={
                        "error_code": ErrorCodes.VALIDATION_FAILED.name,
                        "tool_name": tool_name,
                    },
                )
                invalid_tools_detected = True
                continue

            query = tool_args.get("query", "")
            if not query:
                logger.warning(
                    "LLM returned empty query for Tavily, skipping.",
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
                )
                invalid_tools_detected = True
                continue

            logger.info(
                "Executing Tavily search",
                extra={
                    "step_name": step_name,
                    "query": query,
                },
            )

            audit = await _execute_tavily_search(query, step_name, target_language, llm_client)
            audit_traces.append(audit)
            tool_call_count += 1

            # Inject evidence as tool message — MUST use the LLM's original call ID
            original_call_id = tc.get("id", f"{TAVILY_TOOL_ID}_{step_name}")
            evidence_msg = _build_tool_evidence_message(audit, tool_call_id=original_call_id)

            # Add the assistant's tool_call message and the tool response
            probe_messages.append(
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tc],
                }
            )
            probe_messages.append(evidence_msg)

        # If LLM tried to hallucinate or bypass the tool and we skipped, break the loop to avoid infinite forcing
        if invalid_tools_detected and tool_call_count == 0:
            logger.warning(
                "Forced tool call yielded invalid output. Breaking to Phase 2.", extra={"step_name": step_name}
            )
            break

        # If we processed tool calls, loop back to let LLM decide again
        if tool_call_count >= MAX_TOOL_CALLS_PER_STEP:
            break

    # --- PHASE 2: Completion with evidence injected ---
    # Build final messages: original system/user + any evidence injected
    final_messages = list(probe_messages)

    # If evidence was injected, add a forcing instruction
    if audit_traces:
        final_messages.append(
            {
                "role": "user",
                "content": (
                    "[SYSTEM: EVIDENCE INJECTION COMPLETE] "
                    "You now have external search evidence above. "
                    "Complete the evaluation matrix using both the original context "
                    "AND the search evidence. Output your response strictly in the "
                    "required JSON schema format."
                ),
            }
        )

    try:
        result, usage = await llm_client.run_structured_task(
            messages=final_messages,
            response_model=response_model,
            mock_identity=mock_identity,
        )
        return MCPToolLoopResult(
            result_data=result.model_dump(mode="json"),
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
            status_code=500,
            details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED},
        ) from e
