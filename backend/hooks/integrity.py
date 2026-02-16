"""Integrity hooks for verifying citations and hypothesis linking."""

import logging
import re
from typing import Any, List

from pydantic import BaseModel, ConfigDict, Field

from backend.exceptions import AppException, ErrorCodes
from backend.models.state import WorkflowState

logger = logging.getLogger(__name__)


class CitationAudit(BaseModel):
    """Audit result for citation integrity."""

    valid_citations: int = Field(default=0, description="Count of valid, verified citations.")
    invalid_citations: List[str] = Field(default_factory=list, description="List of hallucinations (citations not found in text).")
    integrity_score: float = Field(default=1.0, description="Ratio of valid citations (0.0 - 1.0).")
    model_config = ConfigDict(frozen=True)


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
    history_text = state.context_variables.get("inputs", {}).get("history_text", "") or ""
    product_text = state.context_variables.get("inputs", {}).get("product_text", "") or ""
    source_corpus = (history_text + "\n" + product_text).lower()

    if not source_corpus.strip():
        logger.warning("[IntegrityHook] Source corpus is empty. Skipping citation verification.")
        return state

    # Helper for loose matching (ignore extra whitespace)
    def normalize(text: str) -> str:
        return " ".join(text.split()).lower()

    norm_corpus = normalize(source_corpus)

    def check_quote(quote: str) -> bool:
        if not quote or len(quote) < 3:  # Ignore tiny fragments
            return True  # Pass benefit of doubt

        norm_q = normalize(quote)
        return norm_q in norm_corpus

    invalid_citations: List[str] = []
    valid_count = 0
    total_count = 0

    # 2. Check Analyst Hypotheses
    step_analyst = state.context_variables.get("step_analyst")
    if step_analyst:
        # STRICT: Expected to be Pydantic model (AnalystOutput)
        # We allow dict for legacy/test flexibility but log warnings?
        # Mandate says: "All internal data exchange MUST use Pydantic Models"
        # We will try getattr first.
        hypotheses = getattr(step_analyst, "hypotheses", [])
        if isinstance(step_analyst, dict):
            hypotheses = step_analyst.get("hypotheses", [])

        for hyp in hypotheses:
            quotes = getattr(hyp, "quotes", [])
            if isinstance(hyp, dict):
                quotes = hyp.get("quotes", [])

            for q in quotes:
                total_count += 1
                if check_quote(q):
                    valid_count += 1
                else:
                    invalid_citations.append(f"Analyst: {q[:50]}...")

    # 3. Check Falsifier (Fidelity Audit)
    step_falsifier = state.context_variables.get("step_falsifier")
    if step_falsifier:
        data = getattr(step_falsifier, "falsifier_data", None)
        # Support dict access for data wrapper if needed
        if isinstance(step_falsifier, dict):
             data = step_falsifier.get("falsifier_data")

        if data:
             audit = getattr(data, "fidelity_audit", None)
             if isinstance(data, dict):
                 audit = data.get("fidelity_audit")
             
             if audit:
                q = getattr(audit, "quote", None)
                if isinstance(audit, dict):
                    q = audit.get("quote")

                if q:
                    total_count += 1
                    if check_quote(q):
                        valid_count += 1
                    else:
                        invalid_citations.append(f"Falsifier: {q[:50]}...")

    # 4. Check Logician (Toulmin Data)
    step_logician = state.context_variables.get("step_logician")
    if step_logician:
        data = getattr(step_logician, "logician_data", None)
        if isinstance(step_logician, dict):
            data = step_logician.get("logician_data")

        if data:
            components = getattr(data, "toulmin_analysis", [])
            if isinstance(data, dict):
                components = data.get("toulmin_analysis", [])

            for comp in components:
                q = getattr(comp, "data", None)
                if isinstance(comp, dict):
                    q = comp.get("data")

                if q:
                    total_count += 1
                    if check_quote(q):
                        valid_count += 1
                    else:
                        invalid_citations.append(f"Logician: {q[:50]}...")

    # 5. Check Judges (Standard & Cognitive)
    for judge_key in ["step_judge", "step_judge_cognitive"]:
        judge_out = state.context_variables.get(judge_key)
        if judge_out:
            snippets = getattr(judge_out, "citation_snippets", None)
            if not snippets and isinstance(judge_out, dict):
                snippets = judge_out.get("citation_snippets")

            if snippets and isinstance(snippets, list):
                for q in snippets:
                    total_count += 1
                    if check_quote(q):
                        valid_count += 1
                    else:
                        invalid_citations.append(f"{judge_key}: {q[:50]}...")

    if total_count == 0:
        logger.info("[IntegrityHook] No citations found to verify.")
        return state

    integrity_score = valid_count / total_count

    # Audit Result
    audit = CitationAudit(
        valid_citations=valid_count, invalid_citations=invalid_citations, integrity_score=integrity_score
    )

    logger.info(
        f"[IntegrityHook] Score: {integrity_score:.2f} ({valid_count}/{total_count}). Invalid: {len(invalid_citations)}"
    )

    # FAIL FAST
    if integrity_score < 0.5:
        error_code = "CITATION_INTEGRITY_FAILURE"
        msg = f"CITATION_INTEGRITY_FAILURE: Score {integrity_score:.2f} < 0.5. Too many hallucinations."
        logger.error(f"[IntegrityHook] {error_code}: {msg}")
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
    step_analyst = state.context_variables.get("step_analyst")
    if not step_analyst:
        return state

    hypotheses = getattr(step_analyst, "hypotheses", [])
    if isinstance(step_analyst, dict):
        hypotheses = step_analyst.get("hypotheses", [])

    if not hypotheses:
        return state

    seen_ids = set()
    expected_idx = 1

    for hyp in hypotheses:
        h_id = getattr(hyp, "id", None)
        if isinstance(hyp, dict):
            h_id = hyp.get("id")

        if not h_id:
            error_code = "INVALID_HYPOTHESIS_ID"
            msg = f"Hypothesis missing ID: {hyp}"
            logger.error(f"[IntegrityHook] {error_code}: {msg}")
            raise AppException(message=msg, status_code=500, details={"error_code": error_code})

        # Format Check: HYP-X
        if not re.match(r"^HYP-\d+$", h_id):
            error_code = "INVALID_HYPOTHESIS_ID"
            msg = f"Invalid Hypothesis ID format: '{h_id}'. Expected 'HYP-N'."
            logger.error(f"[IntegrityHook] {error_code}: {msg}")
            raise AppException(message=msg, status_code=500, details={"error_code": error_code})

        # Sequence Check
        num_part = int(h_id.split("-")[1])
        if num_part != expected_idx:
            # FAIL FAST on sequence gap
            error_code = "HYPOTHESIS_SEQUENCE_ERROR"
            msg = f"Hypothesis ID sequence error. Expected HYP-{expected_idx}, got {h_id}."
            logger.error(f"[IntegrityHook] {error_code}: {msg}")
            raise AppException(
                message=msg, status_code=500, details={"error_code": error_code, "expected": f"HYP-{expected_idx}", "got": h_id}
            )

        seen_ids.add(h_id)
        expected_idx += 1

    logger.info(f"[IntegrityHook] Verified {len(hypotheses)} sequential hypotheses.")
    return state
