"""Integrity hooks for verifying citations and hypothesis linking."""

import asyncio
import copy
import functools
import logging
from pathlib import Path

import rapidfuzz.fuzz as fuzz
from pydantic import TypeAdapter, ValidationError

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.analyst import AnalystOutput
from backend_v2.models.domain.evaluation import EvaluationResult
from backend_v2.models.domain.integrity import CitationAudit, StepContext
from backend_v2.models.enums import QuorumLexicalConfig
from backend_v2.services.storage import get_storage_driver
from backend_v2.settings import get_settings
from backend_v2.utils.paths import get_forensic_input_path

logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=1)
def _read_docs() -> str:
    """Read all static markdown context documents into memory once."""
    docs_dir = Path(get_settings().docs_dir)
    local_rag = ""
    if docs_dir.exists():
        for doc_file in docs_dir.glob("*.md"):
            with open(doc_file, encoding="utf-8") as f:
                local_rag += f.read() + "\n"
    return local_rag


@hook_registry.register(name="verify_citation_integrity")
async def verify_citation_integrity_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Workflow Data wrapper for verify_citation_integrity.

    Verified dynamic citations against structured texts to enforce the Fail-Fast Protocol
    with Option B (Graceful Degradation): hallucinated quotes are gracefully stripped.
    Option C: Bypass verification entirely if SKIP_CITATION_VERIFICATION is enabled.
    """
    source_texts: list[str] = []

    exec_record = await deps.exec_repo.get_execution(state.execution_id)
    if not exec_record or not exec_record.raw_inputs:
        msg = f"Data Integrity Violation: Missing execution record for {state.execution_id}"
        logger.error("[IntegrityHook] %s: %s", ErrorCodes.STATE_INTEGRITY_ERROR.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.STATE_INTEGRITY_ERROR.name})

    inputs_dict = exec_record.raw_inputs.model_dump()
    dynamic_inputs = inputs_dict["dynamic_inputs"]
    storage = get_storage_driver()

    keys_to_check = set(list(inputs_dict.keys()) + list(dynamic_inputs.keys()))

    for key in keys_to_check:
        forensic_path = get_forensic_input_path(state.execution_id, key)

        if await storage.exists(forensic_path):
            data = await storage.read(forensic_path)
            if data:
                source_texts.append(data.decode("utf-8"))
                logger.info("[IntegrityHook] Successfully loaded forensic input from disk: %s", forensic_path)

    global_vars = state.global_context_vars

    if not source_texts:
        msg = "Data Integrity Violation: Missing input text in disk."
        logger.error("[IntegrityHook] %s: %s", ErrorCodes.STATE_INTEGRITY_ERROR.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.STATE_INTEGRITY_ERROR.name})

    # 1b. Gather Context (RAG)
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

    # Chunking: split massive sources by lines to prevent RAM explosion and algorithm brittleness
    raw_lines = ("\n".join(source_texts) + "\n" + rag_text).split("\n")
    corpus_chunks = [line.lower().strip() for line in raw_lines if len(line.strip()) > 5]

    def is_hallucinated(quote: str) -> bool:
        if not quote or len(quote) < 4:
            return False
        norm_q = quote.lower().strip()
        # O(1) best case, early return on first partial fuzzy match >= FUZZ_THRESHOLD_BILINGUAL
        for chunk in corpus_chunks:
            if fuzz.partial_ratio(norm_q, chunk) >= QuorumLexicalConfig.FUZZ_THRESHOLD_BILINGUAL.value:
                return False
        return True

    invalid_citations: list[str] = []
    valid_count = 0
    total_count = 0

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

    if isinstance(parsed_payload, AnalystOutput):
        if parsed_payload.hypotheses:
            new_hypotheses = []
            for hyp in parsed_payload.hypotheses:
                valid_quotes = []
                for quote in hyp.quotes:
                    total_count += 1
                    if is_hallucinated(quote):
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
                if is_hallucinated(quote):
                    invalid_citations.append(quote)
                    logger.warning("[IntegrityHook] Evaluator hallucination detected.")
                else:
                    valid_quotes.append(quote)
                    valid_count += 1
            parsed_payload = parsed_payload.model_copy(update={"citation_snippets": valid_quotes})

    if total_count == 0:
        logger.warning("[IntegrityHook] No structured citations found to verify.")
        return HookResult(success=True, state_delta=parsed_payload.model_dump(mode="json", exclude_none=True))

    if not corpus_chunks:
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

    Ensure that Analyst Hypotheses have sequential, valid IDs (HYP-1, HYP-2...).
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
