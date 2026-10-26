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
from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel, JsonValue

from backend_v2.exceptions import AppException, ErrorCodes, SemanticEvidenceError
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.mcp import (
    CitationCorrectionResult,
    CitationExtractionFailure,
    CitationExtractionItemDTO,
    CitationExtractionResult,
    MCPRetrievalResultDTO,
    MCPSynthesisInstructionsDTO,
    MCPToolLoopResult,
)
from backend_v2.models.domain.system_config import MCPAuditTrace, SystemConfigMCPGateways
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.mcp import MCPValidationContextDTO
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

    resolved_dispatcher = await _resolve_dispatcher(dispatcher=dispatcher, repository=repository)
    tool_declarations = resolved_dispatcher.get_declarations(allowed_tools)
    if not tool_declarations:
        return MCPRetrievalResultDTO(
            audit_traces=[],
            usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
            evidence_payload="",
        )

    active_search_tool = resolved_dispatcher.resolve_primary_search_tool(allowed_tools)

    if is_source_sufficient(source_context) and active_search_tool is None:
        logger.info(
            "[MCPToolLoop] Source sufficiency gate: document (%d chars) exceeds threshold (%d). "
            "Suppressing tool declarations for step '%s'.",
            len(source_context),
            SourceSufficiencyThreshold.MIN_CHARS.value,
            step_name,
        )
        return MCPRetrievalResultDTO(
            audit_traces=[],
            usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
            evidence_payload="",
        )

    if active_search_tool is None:
        return MCPRetrievalResultDTO(
            audit_traces=[],
            usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
            evidence_payload="",
        )

    effective_max_calls = get_settings().max_tool_calls_per_step

    if validation_context is not None:
        val_ctx = MCPValidationContextDTO.model_validate(validation_context, strict=False)
    else:
        val_ctx = MCPValidationContextDTO.model_validate({})
    strictness_level = int(val_ctx.strictness_level)

    total_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
    audit_traces: list[MCPAuditTrace] = []

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

    fast_client = llm_client
    if repository is not None:
        try:
            fast_client = await LLMClient.from_tier(
                CognitiveTier.FAST, repository=repository, pipeline_name="mcp_tool_loop"
            )
        except Exception as e:
            logger.error("Could not initialize 'fast' client for extraction: %s", e, exc_info=True)
            raise AppException(
                message=f"Could not initialize 'fast' client for extraction: {e}",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            ) from e

    async def run_single_extraction() -> tuple[CitationExtractionResult | CitationExtractionFailure, TokenUsage | None]:
        try:
            res, usage = await executor.execute_structured_task(
                client=fast_client,
                messages=extraction_messages,
                response_model=CitationExtractionResult,
                mock_identity=mock_identity,
                validation_context=val_ctx.model_dump(mode="json"),
            )
            if not isinstance(res, CitationExtractionResult):
                res = CitationExtractionResult.model_validate(res)
            return res, usage
        except Exception as ex:
            logger.warning("Ensemble citation extraction call failed: %s", ex, exc_info=True)
            return CitationExtractionFailure(error_message=str(ex)), None

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

    successful_runs: list[tuple[CitationExtractionResult, TokenUsage | None]] = []
    for res, usage in [(res1, usage1), (res2, usage2), (res3, usage3)]:
        if isinstance(res, CitationExtractionResult):
            successful_runs.append((res, usage))
            if usage:
                total_usage += usage

    N = len(successful_runs)
    if N == 0:
        err_msg = f"Phase 0 Citation Extraction failed for step '{step_name}'. All ensemble runs failed."
        logger.error("[MCPToolLoop] %s: %s", ErrorCodes.FETCH_FAILED.name, err_msg, exc_info=True)
        raise AppException(message=err_msg, status_code=502, details={"error_code": ErrorCodes.FETCH_FAILED.value})

    run_appearances: defaultdict[str, int] = defaultdict(int)
    normalized_to_original: dict[str, CitationExtractionItemDTO] = {}

    for res, _ in successful_runs:
        seen_in_this_run = set()
        for citation in res.citations:
            norm_claim, _ = AnchorValidationService.normalize_text_with_mapping(citation.claim_text)
            if norm_claim not in seen_in_this_run:
                seen_in_this_run.add(norm_claim)
                run_appearances[norm_claim] += 1
                if norm_claim not in normalized_to_original:
                    normalized_to_original[norm_claim] = citation

    required_count = 1
    if N >= 2:
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

    extraction_result = CitationExtractionResult(citations=consensus_citations)

    tool_call_count = 0
    allowed_set = set(allowed_tools)

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
        if strictness_level >= 100:
            is_match = AnchorValidationService.strict_match(source_context, [claim])
            if not is_match:
                logger.info(
                    "Physical anchoring failed for claim: '%s'. Initiating self-correction.",
                    claim,
                )
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
                        logger.error("[MCPToolLoop] SemanticEvidenceError: %s", err_msg, exc_info=True)
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
            "Executing primary search tool for validated claim",
            extra={
                "step_name": step_name,
                "query": query,
                "tool_id": active_search_tool.namespaced_alias,
            },
        )

        search_args = resolved_dispatcher.build_search_arguments(
            active_search_tool,
            query,
            claim_text=claim,
            reasoning=citation.reasoning,
        )
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

    evidence_payload = ""
    if audit_traces:
        evidence_blocks = []
        source_texts: dict[str, str] = dict(val_ctx.mcp_source_texts)

        if alias_engine is not None:
            local_alias_engine = alias_engine
        else:
            local_alias_engine = AliasEngine()

        for audit in audit_traces:
            if audit.id:
                real_id = audit.id
            else:
                real_id = f"mcp_trace_{audit.query[:20]}"
            local_id = local_alias_engine.register(real_id, prefix="mcp")
            local_alias_engine.source_document_aliases.append(local_id)
            text_payload = f"Query: {audit.query}\n"
            if audit.response_summary:
                text_payload += f"Summary: {audit.response_summary}\n"
            if audit.source_urls:
                text_payload += f"Sources: {', '.join(audit.source_urls)}\n"

            source_texts[local_id] = text_payload

            evidence_blocks.append(f'<source ID="{local_id}">\n{text_payload}\n</source>')

        val_ctx = val_ctx.model_copy(update={"mcp_source_texts": source_texts})

        evidence_str = "\n".join(evidence_blocks)
        evidence_payload = (
            f"<external_evidence>\n{evidence_str}\n</external_evidence>\n\n{MCP_EVIDENCE_INJECTION_DIRECTIVE}"
        )

    return MCPRetrievalResultDTO(
        audit_traces=audit_traces,
        usage=total_usage,
        evidence_payload=evidence_payload,
    )


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

    if not tool_declarations:
        # No valid tools — direct passthrough (zero overhead)
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

    active_search_tool = resolved_dispatcher.resolve_primary_search_tool(allowed_tools)

    if is_source_sufficient(source_context) and active_search_tool is None:
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
    )

    final_messages: list[LLMMessageDTO] = [LLMMessageDTO(role=m.role, content=m.content) for m in typed_messages]

    if retrieval_result.evidence_payload:
        final_messages.append(
            LLMMessageDTO(
                role="user",
                content=retrieval_result.evidence_payload,
            )
        )

    if synthesis_instructions:
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
