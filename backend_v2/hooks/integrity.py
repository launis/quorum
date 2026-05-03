"""Integrity hooks for verifying citations and hypothesis linking."""

import asyncio
import copy
import logging
import re
from pathlib import Path

from pydantic import ValidationError

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.analyst import AnalystOutput
from backend_v2.models.domain.evaluation import EvaluationResult
from backend_v2.models.domain.integrity import CitationAudit, StepContext
from backend_v2.services.storage import get_storage_driver
from backend_v2.utils.paths import get_forensic_input_path

logger = logging.getLogger(__name__)


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
    storage = get_storage_driver()

    for key in inputs_dict.keys():
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
        docs_dir = Path(__file__).parent.parent.parent / "docs"

        def _read_docs() -> str:
            local_rag = ""
            if docs_dir.exists():
                for doc_file in docs_dir.glob("*.md"):
                    with open(doc_file, encoding="utf-8") as f:
                        local_rag += f.read() + "\n"
            return local_rag

        rag_text += await asyncio.to_thread(_read_docs)
    except OSError as e:
        msg = f"Data Integrity Violation: Failed to load local context documents. Error: {e}"
        logger.error("[IntegrityHook] %s: %s", ErrorCodes.STATE_INTEGRITY_ERROR.name, msg)
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.STATE_INTEGRITY_ERROR.name},
        ) from e

    source_corpus = ("\n".join(source_texts) + "\n" + rag_text).lower()

    def normalize(text: str) -> str:
        return " ".join(text.split()).lower()

    norm_corpus = normalize(source_corpus)

    def is_hallucinated(quote: str) -> bool:
        if not quote or len(quote) < 4:
            return False
        norm_q = normalize(quote)
        return norm_q not in norm_corpus

    invalid_citations: list[str] = []
    valid_count = 0
    total_count = 0

    # 2. V2 Schema Citation Verification (Zero-Compromise Pydantic Definitions)
    if "hypotheses" in state.inputs:
        try:
            analyst_dto = AnalystOutput.model_validate(state.inputs)
            if analyst_dto and analyst_dto.hypotheses:
                new_hypotheses = []
                for hyp in analyst_dto.hypotheses:
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
                analyst_dto = analyst_dto.model_copy(update={"hypotheses": new_hypotheses})
            delta = analyst_dto.model_dump(mode="json", exclude_none=True)
        except ValidationError as e:
            logger.error("Validation failed for AnalystOutput: %s", e)
            raise AppException(
                message="Data Integrity Violation: Invalid AnalystOutput.",
                status_code=500,
                details={"error_code": ErrorCodes.STATE_INTEGRITY_ERROR.name},
            ) from e

    elif "citation_snippets" in state.inputs:
        try:
            eval_dto = EvaluationResult.model_validate(state.inputs)
            if eval_dto and eval_dto.citation_snippets:
                valid_quotes = []
                for quote in eval_dto.citation_snippets:
                    total_count += 1
                    if is_hallucinated(quote):
                        invalid_citations.append(quote)
                        logger.warning("[IntegrityHook] Evaluator hallucination detected.")
                    else:
                        valid_quotes.append(quote)
                        valid_count += 1
                eval_dto = eval_dto.model_copy(update={"citation_snippets": valid_quotes})
            delta = eval_dto.model_dump(mode="json", exclude_none=True)
        except ValidationError as e:
            logger.error("Validation failed for EvaluationResult: %s", e)
            raise AppException(
                message="Data Integrity Violation: Invalid EvaluationResult.",
                status_code=500,
                details={"error_code": ErrorCodes.STATE_INTEGRITY_ERROR.name},
            ) from e
    else:
        delta = copy.deepcopy(state.inputs)

    if total_count == 0:
        logger.warning("[IntegrityHook] No structured citations found to verify.")
        return HookResult(success=True, state_delta=delta)

    if not source_corpus.strip():
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

    if isinstance(delta, dict):
        delta["integrity_audit"] = audit.model_dump(mode="json")

    return HookResult(success=True, state_delta=delta)


@hook_registry.register(name="enforce_hypothesis_linking")
def enforce_hypothesis_linking_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Workflow Data wrapper for enforce_hypothesis_linking.

    Ensure that Analyst Hypotheses have sequential, valid IDs (HYP-1, HYP-2...).
    """
    payload = state.inputs

    # Strict boundary check: Only process if payload is explicitly an AnalystOutput payload
    if not isinstance(payload, dict) or "hypotheses" not in payload:
        return HookResult(success=True, state_delta={})

    try:
        analyst_dto = AnalystOutput.model_validate(payload)
    except ValidationError as e:
        logger.error("Validation failed for AnalystOutput: %s", e)
        raise AppException(
            message="Data Integrity Violation: Invalid AnalystOutput.",
            status_code=500,
            details={"error_code": ErrorCodes.STATE_INTEGRITY_ERROR.name},
        ) from e

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

        if not re.match(r"^hyp_[a-zA-Z0-9]+$", h_id):
            error_code = ErrorCodes.VALIDATION_FAILED
            msg = f"Invalid Hypothesis ID format: '{h_id}'. Expected opaque Stripe ID 'hyp_xxx'."
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
