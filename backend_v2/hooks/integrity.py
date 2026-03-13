"""Integrity hooks for verifying citations and hypothesis linking."""

import logging
import re
from typing import Any

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

    Verified dynamic citations against structured texts to enforce the Fail-Fast Protocol
    with Option B (Graceful Degradation): hallucinated quotes are gracefully stripped.
    Option C: Bypass verification entirely if SKIP_CITATION_VERIFICATION is enabled.

    Args:
        data (dict): Current workflow data containing results.

    Returns:
        dict: Updated data with stripped citations if they fail validation.
    """
    if not data:
        return {}

    # Option C: Global Bypass
    import os

    if os.getenv("SKIP_CITATION_VERIFICATION", "false").lower() == "true":
        logger.info("[IntegrityHook] Citation verification bypassed (SKIP_CITATION_VERIFICATION=true).")
        return data

    # 1. Gather Source Text
    # V2 Isolation Support: Since hooks receive local state, "inputs" might be missing if not injected.
    # We gracefully degrade citation verification if inputs are inaccessible locally, rather than hard crashing.
    inputs = data.get("inputs")
    if not inputs and "_sys_repository" in data.keys() and "$inputs" in data.keys():
          # It might be in global lookup if this is evaluated on global end
          pass

    source_texts = []

    if not inputs:
         logger.warning("[IntegrityHook] Local citation verification requires 'inputs' dictionary. Bypassing safely.")
         return data

    # Gather all text inputs dynamically
    source_texts = []

    if isinstance(inputs, dict):
        for val in inputs.values():
            if val:
                source_texts.append(str(val))

    if not source_texts:
        error_code = ErrorCodes.EMPTY_INPUT
        msg = "Missing any input text for citation verification."
        logger.error(f"[IntegrityHook] {error_code.name}: {msg}")
        raise AppException(message=msg, status_code=400, details={"error_code": error_code})

    # 1b. Gather Context (RAG)
    rag_text = ""
    step_ctx = data.get("step_context", {})

    if step_ctx.get("precedents"):
        rag_text += str(step_ctx.get("precedents")) + "\n"
    for item in step_ctx.get("knowledge_items", []):
        if isinstance(item, dict):
            term = item.get("term", "")
            defn = item.get("definition", "")
            rag_text += f"[{term}]: {defn}\n"

    # Inject theoretical texts into the RAG text from seed databases
    import json

    try:
        from pathlib import Path

        seed_path = Path("c:/src/quorum/backend_v2/seed/seed_data.json")
        if seed_path.exists():
            with open(seed_path, encoding="utf-8") as f:
                seed_json = json.load(f)
                if "prompt_blocks" in seed_json:
                    for pb in seed_json["prompt_blocks"]:
                        if "theory_grounding" in pb:
                            _url = pb["theory_grounding"].get("source_url")
                            # In production, this would fetch from the web. We rely on exact texts in the inputs mostly.
                            pass

        # We also read the documentation to verify any theories explicitly named in the documents
        docs_dir = Path("c:/src/quorum/docs")
        if docs_dir.exists():
            for doc_file in docs_dir.glob("*.md"):
                with open(doc_file, encoding="utf-8") as f:
                    rag_text += f.read() + "\n"
    except Exception as e:
        logger.warning(f"[IntegrityHook] Failed to load documents for citation checking: {e}")

    source_corpus = ("\n".join(source_texts) + "\n" + rag_text).lower()

    # Helper for loose matching (ignore extra whitespace)
    def normalize(text: str) -> str:
        return " ".join(text.split()).lower()

    norm_corpus = normalize(source_corpus)

    def is_hallucinated(quote: str) -> bool:
        if not quote or len(quote) < 4:  # Ignore tiny fragments
            return False  # Pass benefit of doubt
        norm_q = normalize(quote)
        return norm_q not in norm_corpus

    invalid_citations: list[str] = []
    valid_count = 0
    total_count = 0

    # 2. Option B (Graceful Nullification): Search data structure dynamically
    def scan_and_nullify(obj: Any) -> None:
        nonlocal valid_count, total_count
        if isinstance(obj, dict):
            items_to_check = list(obj.keys())
            for k in items_to_check:
                if isinstance(k, str) and k.endswith("_cited_text_quote"):
                    base_crit = k.replace("_cited_text_quote", "")
                    quote_val = obj[k]
                    source_key = f"{base_crit}_cited_source_id"

                    if quote_val:
                        total_count += 1
                        if is_hallucinated(str(quote_val)):
                            logger.warning(
                                f"[IntegrityHook] Citation hallucination detected and stripped for {base_crit}.",
                                extra={"invalid_quote": str(quote_val)},
                            )
                            invalid_citations.append(str(quote_val))
                            # Graceful Nullification
                            obj[k] = None
                            if source_key in obj:
                                obj[source_key] = None
                        else:
                            valid_count += 1
                else:
                    if isinstance(obj[k], (dict, list)):
                        scan_and_nullify(obj[k])
        elif isinstance(obj, list):
            for item in obj:
                scan_and_nullify(item)

    # We mutate `data` recursively in-place
    scan_and_nullify(data)

    if total_count == 0:
        logger.warning("[IntegrityHook] No structured citations found to verify.")
        return data

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

    # Option B: We already nullified hallucinations, so we don't strictly Fail Fast the whole system
    # unless the absolute user-defined threshold demands it. We usually let it pass without the quotes.
    _threshold = get_settings().citation_integrity_threshold
    # In Graceful Degradation, we skip raising an AppException here unless desired. We rely on the nullification.

    # Create a dedicated 'integrity_audit' key in context for visibility regardless of metadata presence
    data["integrity_audit"] = audit.model_dump()

    return data


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

    # V2 Architecture Isolation: Post hooks receive the local dictionary.
    step_analyst = data.get("step_analyst", data)

    hypotheses = step_analyst.get("hypotheses", [])
    if not hypotheses:
        return {}

    seen_ids = set()
    expected_idx = 1

    for hyp in hypotheses:
        h_id = hyp.get("id", "")

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
