"""MCP Tool Loop Conductor.

Isolates the LLM tool-calling cycle from the DAG executor (SRP).
Implements a 2-phase execution:
  Phase 1 (Probe): LLM chat with tool declarations — decides if external search is needed.
  Phase 2 (Completion): Injects evidence as ToolMessage, then forces structured matrix output.

Adheres to RFC 7807 Dual-Reporting and Graceful Degradation (§6.3) mandates.
"""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import BaseModel, JsonValue

from backend_v2.exceptions import AppException, ErrorCodes, SemanticEvidenceError
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.mcp import (
    CitationCorrectionResult,
    CitationExtractionFailure,
    CitationExtractionResult,
    MCPRetrievalResultDTO,
    MCPSynthesisInstructionsDTO,
    MCPToolLoopResult,
)
from backend_v2.models.domain.system_config import MCPAuditTrace, SystemConfigMCPGateways
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.mcp import MCPArgumentValue, MCPToolParamOverrides, MCPValidationContextDTO
from backend_v2.models.enums import CognitiveTier, SourceSufficiencyThreshold
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.prompts import (
    CITATION_SELF_CORRECTION_SYSTEM_INSTRUCTION,
    MCP_EVIDENCE_INJECTION_DIRECTIVE,
    build_mcp_citation_extraction_directive,
)
from backend_v2.services.mcp.dispatcher import ToolDispatcher
from backend_v2.services.orchestrator.anchor_validation import AnchorValidationService
from backend_v2.settings import get_settings
from backend_v2.utils.alias_engine import AliasEngine

logger = logging.getLogger(__name__)

__all__ = [
    "execute_mcp_retrieval",
    "execute_tool_loop",
    "is_source_sufficient",
    "validate_query_relevance",
]


async def _resolve_dispatcher(
    dispatcher: ToolDispatcher | None,
    repository: Any,
) -> ToolDispatcher:
    """Resolve an active ToolDispatcher from explicit injection or system repository.

    Args:
        dispatcher: Optional pre-instantiated ToolDispatcher.
        repository: Optional system config repository exposing get_all_mcp_gateways().

    Returns:
        Configured ToolDispatcher instance.
    """
    if dispatcher is not None:
        return dispatcher
    if repository is not None:
        gateways_res = await repository.get_all_mcp_gateways()
        if isinstance(gateways_res, list):
            valid_gateways = [g for g in gateways_res if isinstance(g, SystemConfigMCPGateways)]
            return ToolDispatcher(gateways=valid_gateways)
    return ToolDispatcher(gateways=[])


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

    for word in query_words:
        if word in context_lower:
            return True

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


def _build_tool_evidence_message(audit: MCPAuditTrace, tool_call_id: str) -> LLMMessageDTO:
    """Convert an MCPAuditTrace into a ToolMessage for LLM injection.

    Args:
        audit: The audit trace from the tool execution.
        tool_call_id: The ORIGINAL call ID from the LLM's tool_call response.
                      Must match exactly for LiteLLM/Gemini transformation.

    Returns:
        Tool message formatted as an immutable LLMMessageDTO.
    """
    if not audit.response_summary and not audit.source_urls:
        return LLMMessageDTO(
            role="tool",
            tool_call_id=tool_call_id,
            content=(
                "<tool_response><info>Search returned no results. "
                "Proceed with your evaluation using available context only.</info></tool_response>"
            ),
        )

    content = f"<tool_response>\n  <query>{audit.query}</query>\n"
    if audit.response_summary:
        content += f"  <summary>{audit.response_summary}</summary>\n"
    if audit.source_urls:
        content += "  <sources>\n"
        for url in audit.source_urls:
            content += f"    <url>{url}</url>\n"
        content += "  </sources>\n"
    content += "</tool_response>"

    return LLMMessageDTO(
        role="tool",
        tool_call_id=tool_call_id,
        content=content,
    )


async def _resolve_fast_extraction_client(llm_client: Any, repository: Any) -> Any:
    """Resolve the fast cognitive tier LLMClient when a system repository is available.

    Args:
        llm_client: Fallback bound LLMClient instance.
        repository: Optional system repository for resolving the FAST tier client.

    Returns:
        Resolved fast-tier LLMClient or the provided llm_client.

    Raises:
        AppException: If initializing the FAST tier client from repository fails
            (ErrorCodes.CONFIGURATION_ERROR).
    """
    if repository is None:
        return llm_client
    try:
        return await LLMClient.from_tier(CognitiveTier.FAST, repository=repository, pipeline_name="mcp_tool_loop")
    except Exception as e:
        logger.error("Could not initialize 'fast' client for extraction: %s", e, exc_info=True)
        raise AppException(
            message=f"Could not initialize 'fast' client for extraction: {e}",
            status_code=500,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        ) from e


def _build_extraction_messages(
    typed_messages: Sequence[LLMMessageDTO],
    target_language: str,
    val_ctx: MCPValidationContextDTO,
) -> list[LLMMessageDTO]:
    """Construct the system and user message sequence for Phase 0 citation extraction.

    Args:
        typed_messages: Validated sequence of input LLMMessageDTO instances.
        target_language: Target document language code.
        val_ctx: Validated MCPValidationContextDTO containing optional query_guidance.

    Returns:
        Ordered list of LLMMessageDTO instances for the citation extraction prompt.
    """
    query_guidance: str | None = None
    if val_ctx.query_guidance is not None:
        stripped_guidance = val_ctx.query_guidance.strip()
        if stripped_guidance:
            query_guidance = stripped_guidance

    extraction_sys_msg = build_mcp_citation_extraction_directive(
        target_language=target_language, query_guidance=query_guidance
    )
    extraction_messages: list[LLMMessageDTO] = [
        LLMMessageDTO(role="system", content=extraction_sys_msg),
    ]
    for msg in typed_messages:
        if msg.role == "user":
            extraction_messages.append(LLMMessageDTO(role="user", content=msg.content))
    return extraction_messages


def _aggregate_ensemble_consensus(
    successful_runs: Sequence[tuple[CitationExtractionResult, TokenUsage | None]],
) -> CitationExtractionResult:
    """Compute majority consensus across successful Best-of-3 citation extraction runs.

    Args:
        successful_runs: Non-empty sequence of (CitationExtractionResult, TokenUsage) pairs.

    Returns:
        CitationExtractionResult containing deduplicated consensus citations.
    """
    run_appearances: defaultdict[str, int] = defaultdict(int)
    for res, _ in successful_runs:
        seen_in_this_run: set[str] = set()
        for citation in res.citations:
            norm_claim, _ = AnchorValidationService.normalize_text_with_mapping(citation.claim_text)
            if norm_claim not in seen_in_this_run:
                seen_in_this_run.add(norm_claim)
                run_appearances[norm_claim] += 1

    required_count = 1
    if len(successful_runs) >= 2:
        required_count = 2

    consensus_citations = list(
        dict.fromkeys(
            citation
            for res, _ in successful_runs
            for citation in res.citations
            if run_appearances[AnchorValidationService.normalize_text_with_mapping(citation.claim_text)[0]]
            >= required_count
        )
    )
    return CitationExtractionResult(citations=consensus_citations)


async def _run_citation_extraction_ensemble(
    *,
    fast_client: Any,
    executor: Any,
    extraction_messages: Sequence[LLMMessageDTO],
    step_name: str,
    mock_identity: str | None,
    val_ctx: MCPValidationContextDTO,
) -> tuple[CitationExtractionResult, TokenUsage]:
    """Execute the Best-of-3 parallel citation extraction ensemble and aggregate consensus.

    Args:
        fast_client: Fast-tier LLMClient instance.
        executor: LLMTaskExecutor instance.
        extraction_messages: System and user messages for extraction.
        step_name: Current step name for error reporting.
        mock_identity: Optional mock identity string for testing.
        val_ctx: Validated MCPValidationContextDTO.

    Returns:
        Tuple of consensus CitationExtractionResult and aggregated TokenUsage.

    Raises:
        AppException: If all 3 ensemble extraction tasks fail (ErrorCodes.FETCH_FAILED).
    """
    val_ctx_json = val_ctx.model_dump(mode="json")

    async def run_single_extraction() -> tuple[CitationExtractionResult | CitationExtractionFailure, TokenUsage | None]:
        try:
            res, usage = await executor.execute_structured_task(
                client=fast_client,
                messages=extraction_messages,
                response_model=CitationExtractionResult,
                mock_identity=mock_identity,
                validation_context=val_ctx_json,
            )
            if not isinstance(res, CitationExtractionResult):
                res = CitationExtractionResult.model_validate(res)
            return res, usage
        except Exception as ex:
            logger.warning("Ensemble citation extraction call failed: %s", ex, exc_info=True)
            return CitationExtractionFailure(error_message=str(ex)), None

    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(run_single_extraction())
        task2 = tg.create_task(run_single_extraction())
        task3 = tg.create_task(run_single_extraction())

    total_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
    successful_runs: list[tuple[CitationExtractionResult, TokenUsage | None]] = []
    for res, usage in (task1.result(), task2.result(), task3.result()):
        if isinstance(res, CitationExtractionResult):
            successful_runs.append((res, usage))
            if usage is not None:
                total_usage += usage

    if not successful_runs:
        err_msg = f"Phase 0 Citation Extraction failed for step '{step_name}'. All ensemble runs failed."
        logger.error("[MCPToolLoop] %s: %s", ErrorCodes.FETCH_FAILED.name, err_msg, exc_info=True)
        raise AppException(message=err_msg, status_code=502, details={"error_code": ErrorCodes.FETCH_FAILED.value})

    return _aggregate_ensemble_consensus(successful_runs), total_usage


async def _verify_or_correct_claim_anchor(
    *,
    claim: str,
    source_context: str,
    strictness_level: int,
    fast_client: Any,
    executor: Any,
    mock_identity: str | None,
    val_ctx: MCPValidationContextDTO,
) -> tuple[str, TokenUsage]:
    """Verify physical anchoring of a claim in source_context or execute single-pass self-correction.

    Args:
        claim: Extracted claim string to verify.
        source_context: Full source document text.
        strictness_level: Configured strictness threshold (physical anchoring active at >= 100).
        fast_client: Fast-tier LLMClient instance.
        executor: LLMTaskExecutor instance.
        mock_identity: Optional mock identity for testing.
        val_ctx: Validated MCPValidationContextDTO.

    Returns:
        Tuple of verified (or self-corrected) claim string and TokenUsage incurred.

    Raises:
        SemanticEvidenceError: If physical anchoring and self-correction fail to locate
            an exact substring match in source_context (ErrorCodes.SEMANTIC_EVIDENCE_HALLUCINATION).
    """
    zero_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
    if strictness_level < 100 or AnchorValidationService.strict_match(source_context, [claim]):
        return claim, zero_usage

    logger.info("Physical anchoring failed for claim: '%s'. Initiating self-correction.", claim)
    correction_user_msg = (
        f"<failed_claim>\n{claim}\n</failed_claim>\n\n<source_context>\n{source_context}\n</source_context>"
    )
    correction_messages: list[LLMMessageDTO] = [
        LLMMessageDTO(role="system", content=CITATION_SELF_CORRECTION_SYSTEM_INSTRUCTION),
        LLMMessageDTO(role="user", content=correction_user_msg),
    ]
    try:
        correction_res_raw, correction_usage = await executor.execute_structured_task(
            client=fast_client,
            messages=correction_messages,
            response_model=CitationCorrectionResult,
            mock_identity=mock_identity,
            validation_context=val_ctx.model_dump(mode="json"),
        )
        resolved_usage = zero_usage
        if correction_usage is not None:
            resolved_usage = correction_usage

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
            return corrected_claim, resolved_usage

        err_msg = f"Self-correction failed to locate exact substring match for: '{claim}'."
        logger.error("[MCPToolLoop] SemanticEvidenceError: %s", err_msg, exc_info=True)
        raise SemanticEvidenceError(
            message=err_msg,
            details={
                "error_code": ErrorCodes.SEMANTIC_EVIDENCE_HALLUCINATION.value,
                "claim_text": claim,
            },
        )
    except SemanticEvidenceError:
        raise
    except Exception as e:
        err_msg = f"Self-correction failed due to task error: {e}"
        logger.error("[MCPToolLoop] SemanticEvidenceError: %s", err_msg, exc_info=True)
        raise SemanticEvidenceError(
            message=err_msg,
            details={
                "error_code": ErrorCodes.SEMANTIC_EVIDENCE_HALLUCINATION.value,
                "claim_text": claim,
            },
        ) from e


def _assemble_evidence_payload(
    audit_traces: Sequence[MCPAuditTrace],
    alias_engine: AliasEngine | None,
    val_ctx: MCPValidationContextDTO,
) -> str:
    """Format MCPAuditTrace records into XML <external_evidence> blocks and register aliases.

    Args:
        audit_traces: Sequence of completed MCPAuditTrace records.
        alias_engine: Optional AliasEngine for registering short MCP source aliases.
        val_ctx: Validated MCPValidationContextDTO.

    Returns:
        Formatted XML evidence payload string, or empty string when audit_traces is empty.
    """
    if not audit_traces:
        return ""

    evidence_blocks: list[str] = []
    source_texts: dict[str, str] = dict(val_ctx.mcp_source_texts)
    local_alias_engine = alias_engine if alias_engine is not None else AliasEngine()

    for audit in audit_traces:
        real_id = audit.id if audit.id else f"mcp_trace_{audit.query[:20]}"
        local_id = local_alias_engine.register(real_id, prefix="mcp")
        local_alias_engine.source_document_aliases.append(local_id)
        text_payload = f"Query: {audit.query}\n"
        if audit.response_summary:
            text_payload += f"Summary: {audit.response_summary}\n"
        if audit.source_urls:
            text_payload += f"Sources: {', '.join(audit.source_urls)}\n"

        source_texts[local_id] = text_payload
        evidence_blocks.append(f'<source ID="{local_id}">\n{text_payload}\n</source>')

    evidence_str = "\n".join(evidence_blocks)
    return f"<external_evidence>\n{evidence_str}\n</external_evidence>\n\n{MCP_EVIDENCE_INJECTION_DIRECTIVE}"


async def execute_mcp_retrieval(
    llm_client: Any,
    executor: Any,
    messages: Sequence[LLMMessageDTO],
    allowed_tools: list[str],
    step_name: str,
    mock_identity: str | None = None,
    target_language: str = "en",
    validation_context: dict[str, JsonValue] | None = None,
    source_context: str = "",
    alias_engine: AliasEngine | None = None,
    repository: Any = None,
    dispatcher: ToolDispatcher | None = None,
    mcp_tool_params: Mapping[str, MCPToolParamOverrides] | None = None,
) -> MCPRetrievalResultDTO:
    """Execute the MCP retrieval phase — citation extraction, anchoring, and tool dispatch.

    Phase 1 (Probe): Uses an ensemble of extraction prompts to identify claims needing verification,
    enforces physical anchoring against the source document, and executes resolved tools via ToolDispatcher.

    Args:
        llm_client: Bound LLMClient instance.
        executor: Bound LLMTaskExecutor instance.
        messages: Compiled chat messages (system + user).
        allowed_tools: List of namespaced tool aliases allowed for this step.
        step_name: Current DAG step name (for audit logging).
        mock_identity: Mock identity for testing.
        target_language: Optional user requested language.
        validation_context: Context dictionary passed to executor.
        source_context: Source document text available in prompt.
        alias_engine: Optional alias engine for registering evidence aliases.
        repository: Optional system config repository for resolving cognitive tier and gateways.
        dispatcher: Optional pre-configured ToolDispatcher instance.
        mcp_tool_params: Optional per-tool static parameter overrides keyed by namespaced alias.

    Returns:
        Structured retrieval result containing audit traces, usage, and assembled evidence payload.

    Raises:
        AppException: If Phase 0 ensemble extraction, client initialization, or parameter
            validation fails (ErrorCodes.FETCH_FAILED or ErrorCodes.CONFIGURATION_ERROR).
        SemanticEvidenceError: If physical anchoring verification or self-correction fails
            to locate an exact quote in source context (ErrorCodes.SEMANTIC_EVIDENCE_HALLUCINATION).
    """
    typed_messages: list[LLMMessageDTO] = [
        m if isinstance(m, LLMMessageDTO) else LLMMessageDTO.model_validate(m) for m in messages
    ]
    empty_result = MCPRetrievalResultDTO(
        audit_traces=[],
        usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
        evidence_payload="",
    )

    resolved_dispatcher = await _resolve_dispatcher(dispatcher=dispatcher, repository=repository)
    if not resolved_dispatcher.get_declarations(allowed_tools):
        return empty_result

    active_search_tool = resolved_dispatcher.resolve_primary_search_tool(allowed_tools)
    if active_search_tool is None:
        if is_source_sufficient(source_context):
            logger.info(
                "[MCPToolLoop] Source sufficiency gate: document (%d chars) exceeds threshold (%d). "
                "Suppressing tool declarations for step '%s'.",
                len(source_context),
                SourceSufficiencyThreshold.MIN_CHARS.value,
                step_name,
            )
        return empty_result

    val_ctx = (
        MCPValidationContextDTO.model_validate(validation_context, strict=False)
        if validation_context is not None
        else MCPValidationContextDTO.model_validate({})
    )
    strictness_level = int(val_ctx.strictness_level)
    fast_client = await _resolve_fast_extraction_client(llm_client=llm_client, repository=repository)
    extraction_messages = _build_extraction_messages(typed_messages, target_language, val_ctx)

    extraction_result, total_usage = await _run_citation_extraction_ensemble(
        fast_client=fast_client,
        executor=executor,
        extraction_messages=extraction_messages,
        step_name=step_name,
        mock_identity=mock_identity,
        val_ctx=val_ctx,
    )

    effective_max_calls = get_settings().max_tool_calls_per_step
    tool_call_count = 0
    allowed_set = set(allowed_tools)
    audit_traces: list[MCPAuditTrace] = []

    for citation in extraction_result.citations:
        if tool_call_count >= effective_max_calls:
            logger.warning(
                "Max tool calls reached for step. Bypassing remaining citations.",
                extra={"max_calls": effective_max_calls, "step_name": step_name},
            )
            break

        claim, correction_usage = await _verify_or_correct_claim_anchor(
            claim=citation.claim_text.strip(),
            source_context=source_context,
            strictness_level=strictness_level,
            fast_client=fast_client,
            executor=executor,
            mock_identity=mock_identity,
            val_ctx=val_ctx,
        )
        total_usage += correction_usage

        query = citation.search_query.strip()
        if not query:
            logger.debug("Skipping citation with empty search query for step '%s'.", step_name)
            continue

        logger.info(
            "Executing primary search tool for validated claim",
            extra={
                "step_name": step_name,
                "query": query,
                "tool_id": active_search_tool.namespaced_alias,
            },
        )

        tool_configured_params: Mapping[str, MCPArgumentValue] | None = None
        if mcp_tool_params is not None and active_search_tool.namespaced_alias in mcp_tool_params:
            tool_configured_params = mcp_tool_params[active_search_tool.namespaced_alias]

        search_args, synth_usage = await resolved_dispatcher.synthesize_search_arguments(
            active_search_tool,
            query,
            claim_text=claim,
            reasoning=citation.reasoning,
            configured_params=tool_configured_params,
            llm_client=fast_client,
            executor=executor,
            mock_identity=mock_identity,
            validation_context=val_ctx.model_dump(mode="json"),
        )
        total_usage += synth_usage
        audit = await resolved_dispatcher.execute_tool(
            tool_id=active_search_tool.namespaced_alias,
            raw_arguments=search_args,
            allowed_step_tools=allowed_set,
            step_name=step_name,
            claim_text=claim,
            reasoning=citation.reasoning,
        )
        audit_traces.append(audit)
        tool_call_count += 1

    evidence_payload = _assemble_evidence_payload(
        audit_traces=audit_traces,
        alias_engine=alias_engine,
        val_ctx=val_ctx,
    )
    return MCPRetrievalResultDTO(
        audit_traces=audit_traces,
        usage=total_usage,
        evidence_payload=evidence_payload,
    )


def _apply_synthesis_instructions(
    final_messages: list[LLMMessageDTO],
    synthesis_instructions: MCPSynthesisInstructionsDTO | None,
) -> None:
    """Validate and prepend OutputProfile synthesis formatting constraints to final_messages.

    Args:
        final_messages: Mutable list of LLMMessageDTO instances for Phase 2 completion.
        synthesis_instructions: Optional MCPSynthesisInstructionsDTO or raw payload.

    Raises:
        AppException: If synthesis_instructions fails schema validation (ErrorCodes.VALIDATION_FAILED).
    """
    if not synthesis_instructions:
        return

    try:
        if isinstance(synthesis_instructions, MCPSynthesisInstructionsDTO):
            instructions = synthesis_instructions
        else:
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

    if final_messages and final_messages[0].role == "system":
        original = final_messages[0].content
        final_messages[0] = final_messages[0].model_copy(update={"content": f"{formatting_msg}{original}"})
    else:
        final_messages.insert(0, LLMMessageDTO(role="system", content=formatting_msg))


async def _execute_phase2_completion[T: BaseModel](
    *,
    llm_client: Any,
    executor: Any,
    final_messages: Sequence[LLMMessageDTO],
    response_model: type[T],
    step_name: str,
    mock_identity: str | None,
    validation_context: dict[str, JsonValue] | None,
    retrieval_result: MCPRetrievalResultDTO,
) -> MCPToolLoopResult:
    """Execute Phase 2 structured task completion and wrap unexpected errors in AppException.

    Args:
        llm_client: Bound LLMClient instance.
        executor: Bound LLMTaskExecutor instance.
        final_messages: Assembled messages including injected external evidence.
        response_model: Target Pydantic schema for structured output.
        step_name: Current DAG step name.
        mock_identity: Optional mock identity for testing.
        validation_context: Optional validation context dictionary.
        retrieval_result: Result from Phase 1 MCP retrieval.

    Returns:
        MCPToolLoopResult combining structured output, audit traces, and total token usage.

    Raises:
        AppException: Re-raises existing AppException or wraps unexpected errors
            (ErrorCodes.WORKFLOW_EXECUTION_FAILED).
    """
    try:
        result, usage = await executor.execute_structured_task(
            client=llm_client,
            messages=final_messages,
            response_model=response_model,
            mock_identity=mock_identity,
            validation_context=validation_context,
        )
        completion_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
        if usage is not None:
            completion_usage = usage
        return MCPToolLoopResult(
            result_data=result.model_dump(mode="json"),
            audit_traces=retrieval_result.audit_traces,
            usage=retrieval_result.usage + completion_usage,
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


async def execute_tool_loop[T: BaseModel](
    llm_client: Any,
    executor: Any,
    messages: Sequence[LLMMessageDTO],
    response_model: type[T],
    allowed_tools: list[str],
    step_name: str,
    mock_identity: str | None = None,
    target_language: str = "en",
    synthesis_instructions: MCPSynthesisInstructionsDTO | None = None,
    validation_context: dict[str, JsonValue] | None = None,
    source_context: str = "",
    alias_engine: AliasEngine | None = None,
    repository: Any = None,
    dispatcher: ToolDispatcher | None = None,
    mcp_tool_params: Mapping[str, MCPToolParamOverrides] | None = None,
) -> MCPToolLoopResult:
    """Execute the MCP Tool Loop — 2-phase LLM execution with optional tool calling.

    Phase 1 (Probe): Ask LLM with tool declarations if it wants to search.
    Phase 2 (Completion): Inject evidence, force structured output.

    Args:
        llm_client: Bound LLMClient instance.
        executor: Bound LLMTaskExecutor instance.
        messages: The compiled chat messages (system + user).
        response_model: Pydantic schema for structured output.
        allowed_tools: List of namespaced tool aliases allowed for this step.
        step_name: Current DAG step name (for audit logging).
        mock_identity: Mock identity for testing.
        target_language: Optional user requested language.
        synthesis_instructions: OutputProfile synthesis formatting limits and preamble constraints.
        validation_context: Optional validation context.
        source_context: The text of the document being evaluated.
        alias_engine: Optional alias engine.
        repository: Optional system config repository.
        dispatcher: Optional pre-configured ToolDispatcher instance.
        mcp_tool_params: Optional per-tool static parameter overrides keyed by namespaced alias.

    Returns:
        Structured tool loop results and audit traces.

    Raises:
        AppException: If Phase 0 ensemble extraction, client initialization, parameter
            validation, or Phase 2 completion fails (ErrorCodes.FETCH_FAILED,
            ErrorCodes.VALIDATION_FAILED, ErrorCodes.CONFIGURATION_ERROR, or
            ErrorCodes.WORKFLOW_EXECUTION_FAILED).
        SemanticEvidenceError: If physical anchoring verification or self-correction fails
            to locate an exact quote in source context (ErrorCodes.SEMANTIC_EVIDENCE_HALLUCINATION).
    """
    typed_messages: list[LLMMessageDTO] = [
        m if isinstance(m, LLMMessageDTO) else LLMMessageDTO.model_validate(m) for m in messages
    ]

    resolved_dispatcher = await _resolve_dispatcher(dispatcher=dispatcher, repository=repository)
    tool_declarations = resolved_dispatcher.get_declarations(allowed_tools)
    active_search_tool = resolved_dispatcher.resolve_primary_search_tool(allowed_tools)

    if not tool_declarations or (is_source_sufficient(source_context) and active_search_tool is None):
        if tool_declarations and is_source_sufficient(source_context) and active_search_tool is None:
            logger.info(
                "[MCPToolLoop] Source sufficiency gate: document (%d chars) exceeds threshold (%d). "
                "Suppressing tool declarations for step '%s'.",
                len(source_context),
                SourceSufficiencyThreshold.MIN_CHARS.value,
                step_name,
            )
        result, usage = await executor.execute_structured_task(
            client=llm_client,
            messages=typed_messages,
            response_model=response_model,
            mock_identity=mock_identity,
            validation_context=validation_context,
        )
        resolved_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
        if usage is not None:
            resolved_usage = usage
        return MCPToolLoopResult(
            result_data=result.model_dump(mode="json"),
            audit_traces=[],
            usage=resolved_usage,
        )

    retrieval_result = await execute_mcp_retrieval(
        llm_client=llm_client,
        executor=executor,
        messages=typed_messages,
        allowed_tools=allowed_tools,
        step_name=step_name,
        mock_identity=mock_identity,
        target_language=target_language,
        validation_context=validation_context,
        source_context=source_context,
        alias_engine=alias_engine,
        repository=repository,
        dispatcher=resolved_dispatcher,
        mcp_tool_params=mcp_tool_params,
    )

    final_messages: list[LLMMessageDTO] = [LLMMessageDTO(role=m.role, content=m.content) for m in typed_messages]
    if retrieval_result.evidence_payload:
        final_messages.append(
            LLMMessageDTO(
                role="user",
                content=retrieval_result.evidence_payload,
            )
        )

    _apply_synthesis_instructions(final_messages, synthesis_instructions)

    return await _execute_phase2_completion(
        llm_client=llm_client,
        executor=executor,
        final_messages=final_messages,
        response_model=response_model,
        step_name=step_name,
        mock_identity=mock_identity,
        validation_context=validation_context,
        retrieval_result=retrieval_result,
    )
