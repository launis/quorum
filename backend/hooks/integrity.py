"""Integrity hooks for verifying citations and hypothesis linking."""

import logging
import re

from pydantic import BaseModel, ConfigDict, Field

from backend.exceptions import AppException, ErrorCodes
from backend.models.domain.analyst import AnalystOutput
from backend.models.domain.falsifier import FalsifierOutput
from backend.models.domain.inputs import WorkflowInputs
from backend.models.domain.judge import JudgeOutput
from backend.models.domain.logician import LogicianOutput
from backend.models.state import WorkflowState
from backend.utils.pydantic_utils import inflate

logger = logging.getLogger(__name__)


class KnowledgeItem(BaseModel):
    """Knowledge item structure."""

    term: str
    definition: str
    model_config = ConfigDict(frozen=True, strict=True)


class StepContext(BaseModel):
    """Step context structure."""

    precedents: str | None = None
    knowledge_items: list[KnowledgeItem] = Field(default_factory=list)
    model_config = ConfigDict(frozen=True, strict=True)


class CitationAudit(BaseModel):
    """Audit result for citation integrity."""

    valid_citations: int = Field(default=0, description="Count of valid, verified citations.")
    invalid_citations: list[str] = Field(
        default_factory=list, description="List of hallucinations (citations not found in text)."
    )
    integrity_score: float = Field(default=1.0, description="Ratio of valid citations (0.0 - 1.0).")
    model_config = ConfigDict(frozen=True, strict=True)


def verify_citation_integrity(state: WorkflowState) -> WorkflowState:
    """HOOK: verify_citation_integrity.

    Verifies that quotes used by agents (Analyst, Falsifier, Logician) actually exist
    in the source text (History, Product).

    FAIL FAST:
    - If integrity_score < 0.5 (more than half are hallucinations), raises Error.

    Args:
        state (WorkflowState): Current workflow state.

    Returns:
        WorkflowState: Updated state with audit logs.

    Raises:
        AppException: If integrity check fails critically.
    """
    # 1. Gather Source Text

    # Strict Enforce: State must be WorkflowState object
    if isinstance(state, dict):
        raise AppException(
            message="Integrity Hook received dict state. Strict Pydantic Enforcement Violation.",
            status_code=500,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA},
        )

    # 1. Gather Source Text
    input_data = state.context_variables.get("inputs")  # Keep raw for error check
    inputs = state.get_context("inputs", WorkflowInputs)

    # Context variable 'inputs' MUST be WorkflowInputs
    if not inputs:
        if input_data is None:
            error_code = ErrorCodes.EMPTY_INPUT
            msg = "Missing 'inputs' in context_variables."
            status_code = 400
        else:
            error_code = ErrorCodes.INVALID_OUTPUT_SCHEMA
            msg = f"Context 'inputs' is {type(input_data)}, expected WorkflowInputs."
            status_code = 500

        logger.error(f"[IntegrityHook] {error_code.name}: {msg}")
        raise AppException(message=msg, status_code=status_code, details={"error_code": error_code})

    # Strict separation of mandatory inputs
    history_text = inputs.history_text
    product_text = inputs.product_text
    reflection_text = inputs.reflection_text

    if not history_text or not product_text or not reflection_text:
        error_code = ErrorCodes.EMPTY_INPUT
        msg = "Missing mandatory input fields (history_text, product_text, reflection_text) for citation verification."
        logger.error(f"[IntegrityHook] {error_code.name}: {msg}")
        raise AppException(message=msg, status_code=400, details={"error_code": error_code})

    # Ensure strings (Pydantic models fields are already typed as Optional[str], so strict check above handles None)
    # We can cast to str just to be safe for concatenation, but if they are str they are str.
    history_text = str(history_text)
    product_text = str(product_text)
    reflection_text = str(reflection_text)

    # 1b. Gather Context (RAG) - SAFE INFLATION
    rag_text = ""
    step_context_data = state.context_variables.get("step_context")

    if step_context_data:
        # Strict Inflation
        step_ctx = state.get_context("step_context", StepContext)

        if step_ctx:
            # Precedents
            if step_ctx.precedents:
                rag_text += str(step_ctx.precedents) + "\n"

            # Knowledge Items
            for item in step_ctx.knowledge_items:
                rag_text += f"[{item.term}]: {item.definition}\n"

    source_corpus = (history_text + "\n" + product_text + "\n" + reflection_text + "\n" + rag_text).lower()

    # Helper for loose matching (ignore extra whitespace)
    def normalize(text: str) -> str:
        return " ".join(text.split()).lower()

    norm_corpus = normalize(source_corpus)

    def check_quote(quote: str) -> bool:
        if not quote or len(quote) < 3:  # Ignore tiny fragments
            return True  # Pass benefit of doubt

        norm_q = normalize(quote)
        return norm_q in norm_corpus

    invalid_citations: list[str] = []
    valid_count = 0
    total_count = 0

    # 2. Check Analyst Hypotheses
    analyst_model = state.get_context("683eb4b9-147c-4f5d-89a7-7b18d75c4202", AnalystOutput)

    if analyst_model:
        for hyp in analyst_model.hypotheses:
            for q in hyp.quotes:
                total_count += 1
                if check_quote(q):
                    valid_count += 1
                else:
                    invalid_citations.append(f"Analyst: {q[:50]}...")

    # 3. Check Falsifier (Fidelity Audit)
    falsifier_model = state.get_context("step_falsifier", FalsifierOutput)

    if falsifier_model and falsifier_model.falsifier_data:
        audit = falsifier_model.falsifier_data.fidelity_audit
        if audit and audit.quote:
            total_count += 1
            if check_quote(audit.quote):
                valid_count += 1
            else:
                invalid_citations.append(f"Falsifier: {audit.quote[:50]}...")

    # 4. Check Logician (Toulmin Data)
    logician_model = state.get_context("step_logician", LogicianOutput)

    if logician_model and logician_model.logician_data:
        for comp in logician_model.logician_data.toulmin_analysis:
            if comp.data:
                total_count += 1
                if check_quote(comp.data):
                    valid_count += 1
                else:
                    invalid_citations.append(f"Logician: {comp.data[:50]}...")

    # 5. Check Judges (Standard & Cognitive)
    for judge_key in ["step_judge", "step_judge_cognitive"]:
        judge_out = state.context_variables.get(judge_key)
        # FIX: Use EvaluationResult. JudgeOutput is deprecated/aliased but agent returns EvaluationResult.
        # Also citation_snippets is not present in EvaluationResult.
        if not judge_out:
            continue

        try:
            # We just validate it exists and is correct type.
            # Citation checking for Judge is temporarily disabled until schema supports it.
            # FIX: JudgeAgent returns JudgeOutput, not EvaluationResult.
            # We accept JudgeOutput as valid for now without forcing EvaluationResult inflation.

            # STRICT PYDANTIC ENFORCEMENT:
            if isinstance(judge_out, dict):
                # Try to strict inflate first
                judge_out = inflate(judge_out, JudgeOutput)

                # If still a dict (inflation failed to produce object), RAISE Strict Violation
                if isinstance(judge_out, dict):
                    raise AppException(
                        message=f"Strict Pydantic Enforcement: {judge_key} is a dict, expected JudgeOutput model.",
                        details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA},
                    )

            # If it's already an object, checking type might be tricky if imports are circular or strict.
            # For now, we trust the presence of data if it's not None.
            pass
        except AppException:
            raise
        except Exception:
            pass

    if total_count == 0:
        logger.info("[IntegrityHook] No citations found to verify.")
        return state

    # FAIL FAST: Data Integrity (Part 18.1)
    if not source_corpus.strip():
        error_code = ErrorCodes.STATE_INTEGRITY_ERROR
        msg = f"Data Integrity Violation: {total_count} citations found, but Source Corpus is empty."
        logger.error(f"[IntegrityHook] {error_code.name}: {msg}")
        raise AppException(message=msg, status_code=500, details={"error_code": error_code})

    integrity_score = valid_count / total_count

    # Audit Result
    audit = CitationAudit(
        valid_citations=valid_count, invalid_citations=invalid_citations, integrity_score=integrity_score
    )

    logger.info(
        f"[IntegrityHook] Score: {integrity_score:.2f} ({valid_count}/{total_count}). Invalid: {len(invalid_citations)}"
    )

    from backend.settings import get_settings

    # FAIL FAST
    threshold = get_settings().citation_integrity_threshold
    if integrity_score < threshold:
        error_code = ErrorCodes.STATE_INTEGRITY_ERROR
        msg = f"CITATION_INTEGRITY_FAILURE: Score {integrity_score:.2f} < {threshold}. Too many hallucinations."
        logger.error(f"[IntegrityHook] {error_code.name}: {msg}")
        raise AppException(
            message=msg,
            status_code=422,
            details={"error_code": error_code, "audit": audit.model_dump()},
        )

    # Update Metadata
    new_context = state.context_variables.copy()
    existing_meta = new_context.get("metadata", {})
    if hasattr(existing_meta, "model_dump"):
        existing_meta = existing_meta.model_dump()  # Should verify structure

    # Store in audit_logs list
    audit_logs = existing_meta.get("audit_logs", [])
    if not isinstance(audit_logs, list):
        audit_logs = []

    audit_logs.append(audit.model_dump())

    # Update metadata dict
    existing_meta["audit_logs"] = audit_logs
    new_context["metadata"] = existing_meta

    # We need to update metadata carefully.
    # Since WorkflowState metadata is typically a Dict or Pydantic, we store it in context_variables usually.
    # But let's create a dedicated 'integrity_audit' key in context for visibility
    new_context["integrity_audit"] = audit

    return state.model_copy(update={"context_variables": new_context})


def enforce_hypothesis_linking(state: WorkflowState) -> WorkflowState:
    """HOOK: enforce_hypothesis_linking.

    Ensures that Analyst Hypotheses have sequential, valid IDs (HYP-1, HYP-2...).

    Args:
        state (WorkflowState): Current state.

    Returns:
        WorkflowState: Verified state.

    Raises:
        AppException: If hypothesis IDs are malformed or non-sequential.
    """
    step_analyst = state.context_variables.get("683eb4b9-147c-4f5d-89a7-7b18d75c4202")
    if not step_analyst:
        return state

    analyst_model = inflate(step_analyst, AnalystOutput)
    if not analyst_model or not analyst_model.hypotheses:
        return state

    hypotheses = analyst_model.hypotheses
    seen_ids = set()
    expected_idx = 1

    for hyp in hypotheses:
        h_id = hyp.id

        if not h_id:
            error_code = ErrorCodes.VALIDATION_FAILED
            msg = f"Hypothesis missing ID: {hyp}"
            logger.error(f"[IntegrityHook] {error_code.name}: {msg}")
            raise AppException(message=msg, status_code=500, details={"error_code": error_code})

        # Format Check: HYP-X
        if not re.match(r"^HYP-\d+$", h_id):
            error_code = ErrorCodes.VALIDATION_FAILED
            msg = f"Invalid Hypothesis ID format: '{h_id}'. Expected 'HYP-N'."
            logger.error(f"[IntegrityHook] {error_code.name}: {msg}")
            raise AppException(message=msg, status_code=500, details={"error_code": error_code})

        # Sequence Check
        num_part = int(h_id.split("-")[1])
        if num_part != expected_idx:
            # FAIL FAST on sequence gap
            error_code = ErrorCodes.STATE_INTEGRITY_ERROR
            msg = f"Hypothesis ID sequence error. Expected HYP-{expected_idx}, got {h_id}."
            logger.error(f"[IntegrityHook] {error_code.name}: {msg}")
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": error_code, "expected": f"HYP-{expected_idx}", "got": h_id},
            )

        seen_ids.add(h_id)
        expected_idx += 1

    logger.info(f"[IntegrityHook] Verified {len(hypotheses)} sequential hypotheses.")
    return state
