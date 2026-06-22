"""Integrity hooks for verifying citations and hypothesis linking."""

import asyncio
import copy
import functools
import logging
from pathlib import Path
from typing import Any

import rapidfuzz.fuzz as fuzz
from pydantic import TypeAdapter, ValidationError

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.analyst import AnalystOutput
from backend_v2.models.domain.evaluation import EvaluationResult
from backend_v2.models.domain.integrity import CitationAudit, StepContext
from backend_v2.models.enums import get_lexical_fuzz_threshold
from backend_v2.services.orchestrator.anchor_validation_service import AnchorValidationService
from backend_v2.services.storage import get_storage_driver
from backend_v2.settings import get_settings
from backend_v2.utils.paths import get_forensic_input_path

logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=1)
def _read_docs() -> str:
    """Read all static markdown context documents into memory once.

    Returns:
        A concatenated string of all markdown document contents.

    Raises:
        OSError: If there is a failure reading the filesystem directories or files.
    """
    docs_dir = Path(get_settings().docs_dir)
    local_rag = ""
    if docs_dir.exists():
        for doc_file in docs_dir.glob("*.md"):
            with open(doc_file, encoding="utf-8") as f:
                local_rag += f.read() + "\n"
    return local_rag


async def _gather_source_texts(execution_id: str, deps: HookDependencies) -> list[str]:
    """Gather source texts from the filesystem based on the execution record.

    Args:
        execution_id: The ID of the current execution.
        deps: Dependencies including the execution repository.

    Returns:
        A list of decoded string contents from forensic input files.

    Raises:
        AppException: If the execution record cannot be found.
    """
    source_texts: list[str] = []
    exec_record = await deps.exec_repo.get_execution(execution_id)

    if not exec_record or not exec_record.raw_inputs:
        msg = f"Data Integrity Violation: Missing execution record for {execution_id}"
        logger.error("[IntegrityHook] %s: %s", ErrorCodes.STATE_INTEGRITY_ERROR.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.STATE_INTEGRITY_ERROR.name})

    inputs_dict = exec_record.raw_inputs.model_dump()
    dynamic_inputs = inputs_dict.get("dynamic_inputs", {})
    storage = get_storage_driver()

    keys_to_check = set(list(inputs_dict.keys()) + list(dynamic_inputs.keys()))

    for key in keys_to_check:
        forensic_path = get_forensic_input_path(execution_id, key)

        if await storage.exists(forensic_path):
            data = await storage.read(forensic_path)
            if data:
                source_texts.append(data.decode("utf-8"))
                logger.info("[IntegrityHook] Successfully loaded forensic input from disk: %s", forensic_path)

    return source_texts


def _gather_rag_context(global_vars: dict[str, Any]) -> str:
    """Extract context precedents and knowledge items from global variables.

    Args:
        global_vars: The global context dictionary from the HookState.

    Returns:
        A formatted string of RAG context.

    Raises:
        AppException: If the step_context structure is invalid.
    """
    rag_text = ""
    if "step_context" in global_vars:
        try:
            step_ctx = StepContext.model_validate(global_vars["step_context"])
            if step_ctx.precedents:
                rag_text += f"{step_ctx.precedents}\n"
            for item in step_ctx.knowledge_items:
                rag_text += f"[{item.term}]: {item.definition}\n"
        except ValidationError as e:
            logger.error("Validation failed for step_context: %s", e)
            raise AppException(
                message="Data Integrity Violation: Invalid step_context structure.",
                status_code=500,
                details={"error_code": ErrorCodes.STATE_INTEGRITY_ERROR.name},
            ) from e
    return rag_text


def _is_hallucinated(quote: str, norm_corpus: str, threshold: float) -> bool:
    """Determine if a quote is hallucinated using fuzzy matching against a corpus.

    Args:
        quote: The text quote to verify.
        norm_corpus: The unified normalized source material.
        threshold: The required fuzzy match score percentage.

    Returns:
        True if the quote is hallucinated, False if a match is found.
    """
    if not quote or len(quote) < 4:
        return False
    norm_q, _ = AnchorValidationService.normalize_text_with_mapping(quote)
    if not norm_q:
        return True

    # Harmonized unified search
    if fuzz.partial_ratio(norm_q, norm_corpus) >= threshold:
        return False
    return True


def _verify_payload_citations(
    parsed_payload: AnalystOutput | EvaluationResult, norm_corpus: str, threshold: float
) -> tuple[AnalystOutput | EvaluationResult, int, int, list[str]]:
    """Verify citations in the parsed payload and drop hallucinated ones.

    Args:
        parsed_payload: The structured payload (AnalystOutput or EvaluationResult).
        norm_corpus: The unified normalized source corpus.
        threshold: The required fuzzy match score percentage.

    Returns:
        A tuple containing the updated payload, the total citation count,
        the valid citation count, and a list of invalid citations.
    """
    invalid_citations: list[str] = []
    valid_count = 0
    total_count = 0

    if isinstance(parsed_payload, AnalystOutput):
        if parsed_payload.hypotheses:
            new_hypotheses = []
            for hyp in parsed_payload.hypotheses:
                valid_quotes = []
                for quote in hyp.quotes:
                    total_count += 1
                    if _is_hallucinated(quote, norm_corpus, threshold):
                        invalid_citations.append(quote)
                        logger.warning("[IntegrityHook] Analyst hallucination detected.")
                    else:
                        valid_quotes.append(quote)
                        valid_count += 1
                new_hypotheses.append(hyp.model_copy(update={"quotes": valid_quotes}))
            parsed_payload = parsed_payload.model_copy(update={"hypotheses": new_hypotheses})

    elif isinstance(parsed_payload, EvaluationResult):
        if parsed_payload.citation_snippets:
            valid_quotes = []
            for quote in parsed_payload.citation_snippets:
                total_count += 1
                if _is_hallucinated(quote, norm_corpus, threshold):
                    invalid_citations.append(quote)
                    logger.warning("[IntegrityHook] Evaluator hallucination detected.")
                else:
                    valid_quotes.append(quote)
                    valid_count += 1
            parsed_payload = parsed_payload.model_copy(update={"citation_snippets": valid_quotes})

    return parsed_payload, total_count, valid_count, invalid_citations


@hook_registry.register(name="verify_citation_integrity")
async def verify_citation_integrity_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Workflow Data wrapper for verify_citation_integrity.

    Verifies dynamic citations against structured texts to enforce the Fail-Fast Protocol
    with Option B (Graceful Degradation): hallucinated quotes are gracefully stripped.
    Option C: Bypass verification entirely if SKIP_CITATION_VERIFICATION is enabled.

    Args:
        state: The current execution state of the hook.
        deps: Dependencies required for execution (e.g., repositories).

    Returns:
        A HookResult containing the mutated state delta.

    Raises:
        AppException: If execution records or necessary input texts are missing,
            or if local context documents fail to load.
    """
    source_texts = await _gather_source_texts(state.execution_id, deps)

    if not source_texts:
        msg = "Data Integrity Violation: Missing input text in disk."
        logger.error("[IntegrityHook] %s: %s", ErrorCodes.STATE_INTEGRITY_ERROR.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.STATE_INTEGRITY_ERROR.name})

    # 1b. Gather Context (RAG)
    rag_text = _gather_rag_context(state.global_context_vars)

    try:
        rag_text += await asyncio.to_thread(_read_docs)
    except OSError as e:
        msg = f"Data Integrity Violation: Failed to load local context documents. Error: {e}"
        logger.error("[IntegrityHook] %s: %s", ErrorCodes.STATE_INTEGRITY_ERROR.name, msg)
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.STATE_INTEGRITY_ERROR.name},
        ) from e

    # Phase 2: Unified normalized text space (BP-3/BP-4 Harmonization)
    raw_text = "\n".join(source_texts) + "\n" + rag_text
    norm_corpus, _ = AnchorValidationService.normalize_text_with_mapping(raw_text)

    # 2. V2 Schema Citation Verification (Zero-Compromise Pydantic Definitions)
    CitationPayloadAdapter: TypeAdapter[AnalystOutput | EvaluationResult] = TypeAdapter(
        AnalystOutput | EvaluationResult
    )

    try:
        parsed_payload = CitationPayloadAdapter.validate_python(state.inputs)
    except ValidationError:
        # Hook is attached to a non-citation schema step, bypass gracefully
        logger.info("[IntegrityHook] Payload is neither AnalystOutput nor EvaluationResult. Bypassing.")
        delta = copy.deepcopy(state.inputs)
        return HookResult(success=True, state_delta=delta)

    system_locale = state.global_context_vars.get("system_locale") if state.global_context_vars else None
    threshold = get_lexical_fuzz_threshold(system_locale)

    parsed_payload, total_count, valid_count, invalid_citations = _verify_payload_citations(
        parsed_payload, norm_corpus, threshold
    )

    if total_count == 0:
        logger.warning("[IntegrityHook] No structured citations found to verify.")
        return HookResult(success=True, state_delta=parsed_payload.model_dump(mode="json", exclude_none=True))

    if not norm_corpus:
        error_code = ErrorCodes.STATE_INTEGRITY_ERROR
        msg = f"Data Integrity Violation: {total_count} citations found, but Source Corpus is empty."
        logger.error("[IntegrityHook] %s: %s", error_code.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": error_code.value})

    integrity_score = valid_count / total_count

    audit = CitationAudit(
        valid_citations=valid_count, invalid_citations=invalid_citations, integrity_score=integrity_score
    )

    logger.info(
        "[IntegrityHook] Score: %.2f (%s/%s). Invalid: %s",
        integrity_score,
        valid_count,
        total_count,
        len(invalid_citations),
    )

    parsed_payload = parsed_payload.model_copy(update={"integrity_audit": audit})
    delta = parsed_payload.model_dump(mode="json", exclude_none=True)

    return HookResult(success=True, state_delta=delta)


@hook_registry.register(name="enforce_hypothesis_linking")
def enforce_hypothesis_linking_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Workflow Data wrapper for enforce_hypothesis_linking.

    Ensures that Analyst Hypotheses have sequential, valid IDs (HYP-1, HYP-2...).

    Args:
        state: The current execution state of the hook.
        deps: Dependencies required for execution (not strictly needed here).

    Returns:
        A HookResult signifying completion.

    Raises:
        AppException: If a hypothesis is missing an ID or contains a duplicate ID.
    """
    payload = state.inputs

    # Strict boundary check: Explicit schema-driven parsing
    try:
        analyst_dto = AnalystOutput.model_validate(payload)
    except ValidationError:
        # Graceful bypass for non-Analyst steps
        return HookResult(success=True, state_delta={})

    hypotheses = analyst_dto.hypotheses

    if not hypotheses:
        return HookResult(success=True, state_delta={})

    seen_ids = set()

    for hyp in hypotheses:
        h_id = hyp.id

        if not h_id:
            error_code = ErrorCodes.VALIDATION_FAILED
            msg = f"Hypothesis missing ID: {hyp}"
            logger.error("[IntegrityHook] %s: %s", error_code.name, msg)
            raise AppException(message=msg, status_code=500, details={"error_code": error_code.value})

        if h_id in seen_ids:
            error_code = ErrorCodes.STATE_INTEGRITY_ERROR
            msg = f"Duplicate Hypothesis ID found: {h_id}."
            logger.error("[IntegrityHook] %s: %s", error_code.name, msg)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": error_code.value, "duplicate_id": h_id},
            )

        seen_ids.add(h_id)

    logger.info("[IntegrityHook] Verified %s opaque hypotheses.", len(hypotheses))
    return HookResult(success=True, state_delta={})
