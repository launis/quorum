"""Integrity hooks for verifying citations and hypothesis linking."""

import logging
import re
from typing import Any

from fastapi import status
from pydantic import BaseModel, ConfigDict, Field

from backend_v2.core.hook_registry import hook_registry
from backend_v2.exceptions import AppException, ErrorCodes

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


@hook_registry.register(name="verify_citation_integrity")
def verify_citation_integrity_hook(data: dict[str, Any]) -> dict[str, Any]:
    """Workflow Data wrapper for verify_citation_integrity.

    Verify that quotes used by agents (Analyst, Falsifier, Logician) actually exist
    in the source text (History, Product).

    FAIL FAST:
    - If integrity_score < 0.5 (more than half are hallucinations), raises Error.

    Args:
        data (dict): Current workflow data.

    Returns:
        dict: Updated data with audit logs.

    Raises:
        AppException: If integrity check fails critically.
    """
    if not data:
        return {}

    # 1. Gather Source Text
    inputs = data.get("inputs")

    # Context variable 'inputs' MUST be a dictionary/object we can read from
    if not inputs:
        error_code = ErrorCodes.EMPTY_INPUT if inputs is None else ErrorCodes.INVALID_OUTPUT_SCHEMA
        msg = "Missing 'inputs' in data."
        status_code = status.HTTP_400_BAD_REQUEST

        logger.error(f"[IntegrityHook] {error_code.name}: {msg}")
        raise AppException(message=msg, status_code=status_code, details={"error_code": error_code})

    # Gather all text inputs dynamically
    source_texts = []
    
    if isinstance(inputs, dict):
        for val in inputs.values():
            if val:
                source_texts.append(str(val))
    else:
        # Fallback if Pydantic model (though should be dict in V2)
        for key, val in vars(inputs).items():
            if val and isinstance(val, str):
                source_texts.append(val)
                
    if not source_texts:
        error_code = ErrorCodes.EMPTY_INPUT
        msg = "Missing any input text for citation verification."
        logger.error(f"[IntegrityHook] {error_code.name}: {msg}")
        raise AppException(message=msg, status_code=400, details={"error_code": error_code})

    # 1b. Gather Context (RAG) - SAFE INFLATION
    rag_text = ""
    step_ctx = data.get("step_context")

    if step_ctx:
        if isinstance(step_ctx, dict):
            # Precedents
            if step_ctx.get("precedents"):
                rag_text += str(step_ctx.get("precedents")) + "\n"

            # Knowledge Items
            for item in step_ctx.get("knowledge_items", []):
                term = item.get("term", "") if isinstance(item, dict) else getattr(item, "term", "")
                defn = item.get("definition", "") if isinstance(item, dict) else getattr(item, "definition", "")
                rag_text += f"[{term}]: {defn}\n"
        else:
            # Precedents
            if step_ctx.precedents:
                rag_text += str(step_ctx.precedents) + "\n"

            # Knowledge Items
            for item in step_ctx.knowledge_items:
                rag_text += f"[{item.term}]: {item.definition}\n"

    source_corpus = ("\n".join(source_texts) + "\n" + rag_text).lower()

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
    analyst_model = data.get("step_analyst")

    if analyst_model:
        hypotheses = (
            analyst_model.get("hypotheses", [])
            if isinstance(analyst_model, dict)
            else getattr(analyst_model, "hypotheses", [])
        )
        for hyp in hypotheses:
            quotes = hyp.get("quotes", []) if isinstance(hyp, dict) else getattr(hyp, "quotes", [])
            for q in quotes:
                total_count += 1
                if check_quote(q):
                    valid_count += 1
                else:
                    invalid_citations.append(f"Analyst: {q[:50]}...")

    # 3. Check Falsifier (Fidelity Audit)
    falsifier_model = data.get("step_falsifier")
    panel_model = data.get("step_panel")

    falsifier_data = None
    if isinstance(falsifier_model, dict) and falsifier_model.get("falsifier_data"):
        falsifier_data = falsifier_model.get("falsifier_data")
    elif hasattr(falsifier_model, "falsifier_data") and getattr(falsifier_model, "falsifier_data", None):
        falsifier_data = falsifier_model.falsifier_data  # type: ignore
    elif isinstance(panel_model, dict) and panel_model.get("falsifier_data"):
        falsifier_data = panel_model.get("falsifier_data")
    elif hasattr(panel_model, "falsifier_data") and getattr(panel_model, "falsifier_data", None):
        falsifier_data = panel_model.falsifier_data  # type: ignore

    if falsifier_data:
        if isinstance(falsifier_data, dict):
            audit = falsifier_data.get("fidelity_audit", {})
        else:
            audit = getattr(falsifier_data, "fidelity_audit", None)

        quote = audit.get("quote", "") if isinstance(audit, dict) else getattr(audit, "quote", "")
        if audit and quote:
            total_count += 1
            if check_quote(audit.quote):
                valid_count += 1
            else:
                invalid_citations.append(f"Falsifier: {audit.quote[:50]}...")

    # 4. Check Logician (Toulmin Data)
    logician_model = data.get("step_logician")
    panel_model = data.get("step_panel")

    logician_data = None
    if isinstance(logician_model, dict) and logician_model.get("logician_data"):
        logician_data = logician_model.get("logician_data")
    elif hasattr(logician_model, "logician_data") and getattr(logician_model, "logician_data", None):
        logician_data = logician_model.logician_data  # type: ignore
    elif isinstance(panel_model, dict) and panel_model.get("logician_data"):
        logician_data = panel_model.get("logician_data")
    elif hasattr(panel_model, "logician_data") and getattr(panel_model, "logician_data", None):
        logician_data = panel_model.logician_data  # type: ignore

    if logician_data:
        if isinstance(logician_data, dict):
            toulmin_analysis = logician_data.get("toulmin_analysis", [])
        else:
            toulmin_analysis = getattr(logician_data, "toulmin_analysis", [])

        for comp in toulmin_analysis:
            comp_data = comp.get("data", "") if isinstance(comp, dict) else getattr(comp, "data", "")
            if comp_data:
                total_count += 1
                if check_quote(comp.data):
                    valid_count += 1
                else:
                    invalid_citations.append(f"Logician: {comp_data[:50]}...")

    if total_count == 0:
        logger.warning("[IntegrityHook] No citations found to verify.")
        return {}

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

    from backend_v2.settings import get_settings

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

    # Update Metadata (Strict Pydantic Enforcement - handled safely for dictionaries)
    new_data = {}
    existing_meta_raw = data.get("metadata", {})

    try:
        if isinstance(existing_meta_raw, dict):
            if existing_meta_raw:
                audit_logs = existing_meta_raw.get("audit_logs", [])
                audit_logs.append(audit.model_dump())
                new_meta = existing_meta_raw.copy()
                new_meta["audit_logs"] = audit_logs
                new_data["metadata"] = new_meta
        elif hasattr(existing_meta_raw, "model_copy"):
            # Update existing Metadata instance directly
            audit_logs = existing_meta_raw.audit_logs or []
            audit_logs.append(audit.model_dump())
            new_data["metadata"] = existing_meta_raw.model_copy(update={"audit_logs": audit_logs})
    except Exception as e:
        logger.warning(f"[IntegrityHook] Failed to append CitationAudit to metadata: {e}")

    # Create a dedicated 'integrity_audit' key in context for visibility regardless of metadata presence
    new_data["integrity_audit"] = audit.model_dump()

    return new_data


@hook_registry.register(name="enforce_hypothesis_linking")
def enforce_hypothesis_linking_hook(data: dict[str, Any]) -> dict[str, Any]:
    """Workflow Data wrapper for enforce_hypothesis_linking.

    Ensure that Analyst Hypotheses have sequential, valid IDs (HYP-1, HYP-2...).

    Args:
        data (dict): Current data.

    Returns:
        dict: Verified data (empty delta).

    Raises:
        AppException: If hypothesis IDs are malformed or non-sequential.
    """
    if not data:
        return {}

    step_analyst = data.get("step_analyst")
    if not step_analyst:
        return {}

    if isinstance(step_analyst, dict):
        hypotheses = step_analyst.get("hypotheses", [])
    else:
        hypotheses = getattr(step_analyst, "hypotheses", [])
    if not hypotheses:
        return {}

    seen_ids = set()
    expected_idx = 1

    for hyp in hypotheses:
        h_id = hyp.get("id", "") if isinstance(hyp, dict) else getattr(hyp, "id", "")

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
    return {}
