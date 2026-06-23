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

from pydantic import BaseModel

from backend_v2.exceptions import AppException, ErrorCodes, SemanticEvidenceError
from backend_v2.models.domain.mcp import (
    CitationExtractionResult,
    MCPSynthesisInstructionsDTO,
    MCPToolLoopResult,
)
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.enums import SourceSufficiencyThreshold
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


def validate_query_relevance(query: str, source_context: str) -> bool:
    """Validate if the search query is semantically relevant to the source context.

    Prevents the LLM from hallucinating irrelevant searches (e.g., EUR/USD
    exchange rates) that waste API calls and inject noise into the evaluation.

    Args:
        query: The search query hallucinated by the LLM.
        source_context: The text of the document being evaluated.

    Returns:
        bool: True if relevant (or if validation cannot be determined), False if clearly hallucinated.
    """
    if not source_context or not source_context.strip():
        return True

    query_words = [w.lower() for w in query.split() if len(w) >= 3]
    if not query_words:
        return True

    context_lower = source_context.lower()

    # If any substantive word from the query exists in the source context, consider it relevant.
    for word in query_words:
        if word in context_lower:
            return True

    # If no words overlap at all, it's a hallucination.
    return False


def is_source_sufficient(source_context: str) -> bool:
    """Determine if the source document is substantial enough to skip tool calling.

    When the full document is already in the LLM prompt, there is no information
    gap that external tools could fill. This is the L3 root cause fix that
    prevents the LLM from even receiving tool declarations.

    Args:
        source_context: The source document text available in the prompt.

    Returns:
        True if the source is sufficient (tools should be suppressed).
        False if there is an information gap (tools may be needed).
    """
    return len(source_context.strip()) >= SourceSufficiencyThreshold.MIN_CHARS.value


def _build_tool_declarations(allowed_tools: list[str]) -> list[dict[str, Any]]:
    """Build OpenAI-format tool declarations from allowed tool IDs.

    Args:
        allowed_tools: List of allowed tool IDs (e.g., ["mcp_tavily_search"]).

    Returns:
        list[dict[str, Any]]: List of valid OpenAI function declarations.
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
        query: The search query string.
        step_name: Current step name for auditing.
        target_language: Target translation language.
        llm_client: Bound LLM client (optional).

    Returns:
        MCPAuditTrace: Audit record containing the search results.

    Raises:
        AppException: If the search fails critically.
    """
    start_ms = int(time.monotonic() * 1000)
    try:
        result = await tavily_search(query)
        response_summary = result.answer

        # NOTE: We previously did an explicit LLM call here to translate `response_summary`
        # to `target_language`. This was removed to save 1 LLM call per search (5 RPM limit).
        # The main LLM (Phase 2) is perfectly capable of reading English evidence and outputting Finnish.

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
        # Zero-Compromise Fail-Fast: Crash the step if external search fails
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
            status_code=502,
            details={"error_code": ErrorCodes.FETCH_FAILED.value, "detail": str(e)},
        ) from e


def _build_tool_evidence_message(audit: MCPAuditTrace, tool_call_id: str) -> dict[str, str]:
    """Convert an MCPAuditTrace into a ToolMessage for LLM injection.

    Args:
        audit: The audit trace from the tool execution.
        tool_call_id: The ORIGINAL call ID from the LLM's tool_call response.
                      Must match exactly for LiteLLM/Gemini transformation.

    Returns:
        dict[str, str]: Tool message formatted for OpenAI/LiteLLM.
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


async def execute_tool_loop[T: BaseModel](
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
    source_context: str = "",
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
        synthesis_instructions: Epic 13 OutputProfile limits and preamble constraints.

    Returns:
        MCPToolLoopResult with structured data and audit traces.
    """
    audit_traces: list[MCPAuditTrace] = []
    tool_declarations = _build_tool_declarations(allowed_tools)

    if not tool_declarations:
        # No valid tools — direct passthrough (zero overhead)
        result, usage = await executor.execute_structured_task(
            client=llm_client,
            messages=messages,
            response_model=response_model,
            mock_identity=mock_identity,
            validation_context=validation_context,
        )
        return MCPToolLoopResult(
            result_data=result.model_dump(mode="json"),
            audit_traces=[],
            usage=usage if usage else TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
        )

    # L3 Root Cause Fix: Source Sufficiency Gate
    # When the full document is already in the prompt, the LLM has no information
    # gap to fill. Suppress tool declarations entirely to prevent hallucinated
    # tool calls (e.g., EUR/USD, weather) that inject noise and break caching.
    if is_source_sufficient(source_context) and TAVILY_TOOL_ID not in allowed_tools:
        logger.info(
            "[MCPToolLoop] Source sufficiency gate: document (%d chars) exceeds threshold (%d). "
            "Suppressing tool declarations for step '%s'.",
            len(source_context),
            SourceSufficiencyThreshold.MIN_CHARS.value,
            step_name,
        )
        result, usage = await executor.execute_structured_task(
            client=llm_client,
            messages=messages,
            response_model=response_model,
            mock_identity=mock_identity,
            validation_context=validation_context,
        )
        return MCPToolLoopResult(
            result_data=result.model_dump(mode="json"),
            audit_traces=[],
            usage=usage if usage else TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
        )

    # Epic 13 M2: Restored to standard MAX_TOOL_CALLS_PER_STEP
    effective_max_calls = MAX_TOOL_CALLS_PER_STEP

    if TAVILY_TOOL_ID in allowed_tools:
        extraction_sys_msg = (
            "<system_instruction>\n"
            "  <objective>Extract factual claims that require external verification.</objective>\n"
            "  <rule>Return a structured list of citations.</rule>\n"
            "  <rule>The claim_text MUST be an exact physical substring from the source document.</rule>\n"
            "</system_instruction>"
        )

        extraction_messages = [{"role": "system", "content": extraction_sys_msg}]
        for msg in messages:
            if msg.get("role") == "user":
                extraction_messages.append(msg)

        # Internal Utility rule: lazy load LLMClient
        from backend_v2.llm.client import LLMClient

        # We attempt to fetch the fast client. If executor lacks repository, we gracefully fallback to the step's client.
        repo = getattr(executor, "repository", None)
        fast_client = llm_client
        if repo:
            try:
                fast_client = await LLMClient.from_strategy("fast", repository=repo)
            except Exception as e:
                logger.warning("Could not initialize 'fast' client for extraction, falling back to step client: %s", e)

        try:
            extraction_result_raw, _ = await executor.execute_structured_task(
                client=fast_client,
                messages=extraction_messages,
                response_model=CitationExtractionResult,
                mock_identity=mock_identity,
                validation_context=validation_context,
            )
            if isinstance(extraction_result_raw, CitationExtractionResult):
                extraction_result = extraction_result_raw
            else:
                extraction_result = CitationExtractionResult.model_validate(extraction_result_raw)
        except Exception as e:
            err_msg = f"Phase 0 Citation Extraction failed for step '{step_name}'."
            logger.error("[MCPToolLoop] %s: %s", ErrorCodes.FETCH_FAILED.name, err_msg, exc_info=True)
            if isinstance(e, AppException):
                raise
            raise AppException(
                message=err_msg, status_code=502, details={"error_code": ErrorCodes.FETCH_FAILED.value}
            ) from e

        tool_call_count = 0

        for citation in extraction_result.citations:
            if tool_call_count >= effective_max_calls:
                logger.warning(
                    "Max tool calls reached for step. Bypassing remaining citations.",
                    extra={"max_calls": effective_max_calls, "step_name": step_name},
                )
                break

            claim = citation.claim_text.strip()
            query = citation.search_query.strip()

            # Physical Anchoring Mandate: Validate exact string match
            if claim and claim not in source_context:
                err_msg = f"Hallucinated claim detected. '{claim}' not found in source text."
                logger.error("[MCPToolLoop] SemanticEvidenceError: %s", err_msg)
                raise SemanticEvidenceError(
                    message=err_msg,
                    details={"error_code": ErrorCodes.SEMANTIC_EVIDENCE_HALLUCINATION.value, "claim_text": claim},
                )

            if not query:
                continue

            logger.info(
                "Executing Tavily search for validated claim",
                extra={"step_name": step_name, "query": query},
            )

            audit = await _execute_tavily_search(query, step_name, target_language, llm_client)
            audit_traces.append(audit)
            tool_call_count += 1

    # --- PHASE 2: Completion with evidence injected ---
    # Build final messages: original system/user + any evidence injected
    final_messages = list(messages)

    if audit_traces:
        evidence_blocks = []
        for audit in audit_traces:
            content = f"<search_result>\n  <query>{audit.query}</query>\n"
            if audit.response_summary:
                content += f"  <summary>{audit.response_summary}</summary>\n"
            if audit.source_urls:
                content += "  <sources>\n"
                for url in audit.source_urls:
                    content += f"    <url>{url}</url>\n"
                content += "  </sources>\n"
            content += "</search_result>"
            evidence_blocks.append(content)

        evidence_str = "\n".join(evidence_blocks)
        final_messages.append(
            {
                "role": "user",
                "content": (
                    "<external_evidence>\n"
                    f"{evidence_str}\n"
                    "</external_evidence>\n\n"
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

    # EPIC 13: Dynamically inject runtime parameters from OutputProfile via hook extraction
    if synthesis_instructions:
        try:
            instructions = MCPSynthesisInstructionsDTO.model_validate(synthesis_instructions)
        except Exception as e:
            err_msg = "Failed to validate synthesis_instructions."
            logger.error("[MCPToolLoop] %s: %s", ErrorCodes.VALIDATION_FAILED.name, err_msg, exc_info=True)
            raise AppException(
                message=err_msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
            ) from e

        formatting_msg = "<execution_parameters>\n  <output_profile_formatting_constraints>\n"
        if instructions.synthesis_preamble:
            formatting_msg += f"    <synthesis_preamble>{instructions.synthesis_preamble}</synthesis_preamble>\n"
        if instructions.synthesis_length_limit:
            limit = instructions.synthesis_length_limit
            formatting_msg += f"    <synthesis_length_limit>{limit}</synthesis_length_limit>\n"
        formatting_msg += "  </output_profile_formatting_constraints>\n</execution_parameters>\n\n"

        # Prevent "Alternate Roles" strictly by patching the system prompt (index 0)
        if final_messages and "role" in final_messages[0] and final_messages[0]["role"] == "system":
            original = final_messages[0]["content"]
            final_messages[0]["content"] = f"{formatting_msg}{original}"
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
        return MCPToolLoopResult(
            result_data=result.model_dump(mode="json"),
            audit_traces=audit_traces,
            usage=usage if usage else TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
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
            details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED.value},
        ) from e
