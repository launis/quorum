"""MCP Tool Loop Conductor.

Isolates the LLM tool-calling cycle from the DAG executor (SRP).
Implements a 2-phase execution:
  Phase 1 (Probe): LLM chat with tool declarations — decides if external search is needed.
  Phase 2 (Completion): Injects evidence as ToolMessage, then forces structured matrix output.

Adheres to RFC 7807 Dual-Reporting and Graceful Degradation (§6.3) mandates.
"""

import asyncio
import logging
from typing import Any

from pydantic import BaseModel

from backend_v2.exceptions import AppException, ErrorCodes, SemanticEvidenceError
from backend_v2.llm.prompt_builder import build_system_directive
from backend_v2.models.domain.mcp import (
    CitationCorrectionResult,
    CitationExtractionResult,
    MCPSynthesisInstructionsDTO,
    MCPToolLoopResult,
)
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.enums import SourceSufficiencyThreshold
from backend_v2.models.v2_core import MCPAuditTrace
from backend_v2.services.mcp.dispatcher import ToolDispatcher
from backend_v2.services.mcp.tools.tavily import TAVILY_TOOL_ID, TavilyTool
from backend_v2.services.orchestrator.anchor_validation_service import AnchorValidationService
from backend_v2.settings import get_settings
from backend_v2.utils.alias_engine import AliasEngine

logger = logging.getLogger(__name__)


# NOTE (Architecture): Hard cap to prevent infinite LLM↔Tool loops.
# EPIC §3 "The Infinite Loop Limit". Controlled by SystemOverrides.

_SELF_CORRECTION_SYSTEM_INSTRUCTION = build_system_directive(
    objective=(
        "Locate and return the exact physical substring from the source context "
        "that is semantically equivalent to the failed claim."
    ),
    rules=[
        "The returned corrected_claim MUST be a 100% exact substring match from the source context (including case, spaces, and diacritics).",
        "Do not paraphrase or summarize.",
    ],
)

# Global Dispatcher Instance
DISPATCHER = ToolDispatcher(tools=[TavilyTool()])


def validate_query_relevance(query: str, source_context: str) -> bool:
    """Validate if the search query is semantically relevant to the source context.

    Prevents the LLM from hallucinating irrelevant searches (e.g., EUR/USD
    exchange rates) that waste API calls and inject noise into the evaluation.

    Args:
        query: The search query hallucinated by the LLM.
        source_context: The text of the document being evaluated.

    Returns:
        True if relevant (or if validation cannot be determined), False if clearly hallucinated.
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


def _build_tool_evidence_message(audit: MCPAuditTrace, tool_call_id: str) -> dict[str, str]:
    """Convert an MCPAuditTrace into a ToolMessage for LLM injection.

    Args:
        audit: The audit trace from the tool execution.
        tool_call_id: The ORIGINAL call ID from the LLM's tool_call response.
                      Must match exactly for LiteLLM/Gemini transformation.

    Returns:
        Tool message formatted for OpenAI/LiteLLM.
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
    alias_engine: AliasEngine | None = None,
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
        Structured tool loop results and audit traces.

    Raises:
        AppException: If Phase 0 ensemble extraction, parameter validation, or Phase 2
            completion fails critically (ErrorCodes.FETCH_FAILED,
            ErrorCodes.VALIDATION_FAILED, or ErrorCodes.WORKFLOW_EXECUTION_FAILED).
    """
    audit_traces: list[MCPAuditTrace] = []
    tool_declarations = DISPATCHER.get_declarations(allowed_tools)

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
    # Controlled by settings to support Dev-Mode limits
    effective_max_calls = get_settings().max_tool_calls_per_step

    strictness_level = 100
    if validation_context:
        strictness_level = validation_context.get("strictness_level", 100)

    total_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)

    if TAVILY_TOOL_ID in allowed_tools:
        extraction_sys_msg = build_system_directive(
            objective="Extract factual claims that require external verification.",
            rules=[
                "Return a structured list of citations.",
                f"Provide a short max 100 character reasoning sentence for each extraction in the language code '{target_language}'.",
            ],
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
                fast_client = await LLMClient.from_strategy("fast", repository=repo, pipeline_name="mcp_tool_loop")
            except Exception as e:
                logger.warning("Could not initialize 'fast' client for extraction, falling back to step client: %s", e)

        async def run_single_extraction() -> tuple[CitationExtractionResult | None, TokenUsage | None]:
            try:
                res, usage = await executor.execute_structured_task(
                    client=fast_client,
                    messages=extraction_messages,
                    response_model=CitationExtractionResult,
                    mock_identity=mock_identity,
                    validation_context=validation_context,
                )
                if not isinstance(res, CitationExtractionResult):
                    res = CitationExtractionResult.model_validate(res)
                return res, usage
            except Exception as ex:
                logger.warning("Ensemble citation extraction call failed: %s", ex, exc_info=True)
                return None, None

        try:
            async with asyncio.TaskGroup() as tg:
                task1 = tg.create_task(run_single_extraction())
                task2 = tg.create_task(run_single_extraction())
                task3 = tg.create_task(run_single_extraction())

            res1, usage1 = task1.result()
            res2, usage2 = task2.result()
            res3, usage3 = task3.result()
        except Exception as e:
            err_msg = f"Phase 0 Citation Extraction TaskGroup failed for step '{step_name}'."
            logger.error("[MCPToolLoop] %s: %s", ErrorCodes.FETCH_FAILED.name, err_msg, exc_info=True)
            raise AppException(
                message=err_msg, status_code=502, details={"error_code": ErrorCodes.FETCH_FAILED.value}
            ) from e

        successful_runs = []
        for res, usage in [(res1, usage1), (res2, usage2), (res3, usage3)]:
            if res is not None:
                successful_runs.append((res, usage))
                if usage:
                    total_usage += usage

        N = len(successful_runs)
        if N == 0:
            err_msg = f"Phase 0 Citation Extraction failed for step '{step_name}'. All ensemble runs failed."
            logger.error("[MCPToolLoop] %s: %s", ErrorCodes.FETCH_FAILED.name, err_msg)
            raise AppException(message=err_msg, status_code=502, details={"error_code": ErrorCodes.FETCH_FAILED.value})

        from collections import defaultdict

        run_appearances: defaultdict[str, int] = defaultdict(int)
        normalized_to_original = {}

        for res, _ in successful_runs:
            seen_in_this_run = set()
            for citation in res.citations:
                norm_claim, _ = AnchorValidationService.normalize_text_with_mapping(citation.claim_text)
                if norm_claim not in seen_in_this_run:
                    seen_in_this_run.add(norm_claim)
                    run_appearances[norm_claim] += 1
                    if norm_claim not in normalized_to_original:
                        normalized_to_original[norm_claim] = citation

        required_count = 2 if N >= 2 else 1
        consensus_citations = []
        for res, _ in successful_runs:
            for citation in res.citations:
                norm_claim, _ = AnchorValidationService.normalize_text_with_mapping(citation.claim_text)
                if run_appearances[norm_claim] >= required_count:
                    if citation not in consensus_citations:
                        consensus_citations.append(citation)

        extraction_result = CitationExtractionResult(citations=consensus_citations)

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
            # If strictness_level < 100, bypass strict substring verification entirely.
            if strictness_level >= 100:
                is_match = AnchorValidationService.strict_match(source_context, [claim])
                if not is_match:
                    logger.info(
                        "Physical anchoring failed for claim: '%s'. Initiating self-correction.",
                        claim,
                    )
                    correction_user_msg = (
                        "<failed_claim>\n"
                        f"{claim}\n"
                        "</failed_claim>\n\n"
                        "<source_context>\n"
                        f"{source_context}\n"
                        "</source_context>"
                    )
                    correction_messages = [
                        {"role": "system", "content": _SELF_CORRECTION_SYSTEM_INSTRUCTION},
                        {"role": "user", "content": correction_user_msg},
                    ]
                    try:
                        correction_res_raw, correction_usage = await executor.execute_structured_task(
                            client=fast_client,
                            messages=correction_messages,
                            response_model=CitationCorrectionResult,
                            mock_identity=mock_identity,
                            validation_context=validation_context,
                        )
                        if correction_usage:
                            total_usage += correction_usage

                        if isinstance(correction_res_raw, CitationCorrectionResult):
                            correction_res = correction_res_raw
                        else:
                            correction_res = CitationCorrectionResult.model_validate(correction_res_raw)

                        corrected_claim = correction_res.corrected_claim.strip()

                        if corrected_claim and AnchorValidationService.strict_match(source_context, [corrected_claim]):
                            logger.info(
                                "Self-correction succeeded. Corrected claim: '%s' (originally: '%s')",
                                corrected_claim,
                                claim,
                            )
                            claim = corrected_claim
                        else:
                            err_msg = f"Self-correction failed to locate exact substring match for: '{claim}'."
                            logger.error("[MCPToolLoop] SemanticEvidenceError: %s", err_msg)
                            raise SemanticEvidenceError(
                                message=err_msg,
                                details={
                                    "error_code": ErrorCodes.SEMANTIC_EVIDENCE_HALLUCINATION.value,
                                    "claim_text": claim,
                                },
                            )
                    except Exception as e:
                        if isinstance(e, SemanticEvidenceError):
                            raise
                        err_msg = f"Self-correction failed due to task error: {e}"
                        logger.error("[MCPToolLoop] SemanticEvidenceError: %s", err_msg, exc_info=True)
                        raise SemanticEvidenceError(
                            message=err_msg,
                            details={
                                "error_code": ErrorCodes.SEMANTIC_EVIDENCE_HALLUCINATION.value,
                                "claim_text": claim,
                            },
                        ) from e

            if not query:
                continue

            logger.info(
                "Executing Tavily search for validated claim",
                extra={"step_name": step_name, "query": query},
            )

            audit = await DISPATCHER.execute_tool(
                tool_id=TAVILY_TOOL_ID,
                query=query,
                step_name=step_name,
                target_language=target_language,
                llm_client=llm_client,
                reasoning=citation.reasoning,
                claim_text=claim,
            )
            audit_traces.append(audit)
            tool_call_count += 1

    # --- PHASE 2: Completion with evidence injected ---
    # Build final messages: original system/user + any evidence injected
    final_messages = list(messages)

    if audit_traces:
        evidence_blocks = []
        if validation_context is None:
            validation_context = {}
        if "mcp_source_texts" not in validation_context:
            validation_context["mcp_source_texts"] = {}

        # Tier 4 Fix: Use AliasEngine as the single source of truth for alias generation.
        # Removed ad-hoc doc{N} counter and alias_map mutation that bypassed AliasEngine.
        local_alias_engine = alias_engine if alias_engine else AliasEngine()

        for audit in audit_traces:
            real_id = audit.id if audit.id else f"mcp_trace_{audit.query[:20]}"
            local_id = local_alias_engine.register(real_id, prefix="mcp")
            local_alias_engine.source_document_aliases.append(local_id)
            text_payload = f"Query: {audit.query}\n"
            if audit.response_summary:
                text_payload += f"Summary: {audit.response_summary}\n"
            if audit.source_urls:
                text_payload += f"Sources: {', '.join(audit.source_urls)}\n"

            validation_context["mcp_source_texts"][local_id] = text_payload

            evidence_blocks.append(f'<source ID="{local_id}">\n{text_payload}\n</source>')

        evidence_str = "\n".join(evidence_blocks)
        final_messages.append(
            {
                "role": "user",
                "content": (
                    "<external_evidence>\n"
                    f"{evidence_str}\n"
                    "</external_evidence>\n\n"
                    f"{build_system_directive(objective='EVIDENCE INJECTION COMPLETE', rules=['You now have external search evidence above.', 'Complete the evaluation matrix using both the original context AND the search evidence.', 'Output your response strictly in the required JSON schema format.'])}"
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
        completion_usage = usage if usage else TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
        return MCPToolLoopResult(
            result_data=result.model_dump(mode="json"),
            audit_traces=audit_traces,
            usage=total_usage + completion_usage,
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
