"""Integrity hooks for verifying citations and hypothesis linking."""

import copy
import logging
import re

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.integrity import CitationAudit, IntegrityGlobalInputsDTO, StepContext

logger = logging.getLogger(__name__)


@hook_registry.register(name="verify_citation_integrity")
async def verify_citation_integrity_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Workflow Data wrapper for verify_citation_integrity.

    Verified dynamic citations against structured texts to enforce the Fail-Fast Protocol
    with Option B (Graceful Degradation): hallucinated quotes are gracefully stripped.
    Option C: Bypass verification entirely if SKIP_CITATION_VERIFICATION is enabled.
    """
    if not state:
        return HookResult(success=True, state_delta={})

    import os

    if os.getenv("SKIP_CITATION_VERIFICATION", "false").lower() == "true":
        logger.info("[IntegrityHook] Citation verification bypassed (SKIP_CITATION_VERIFICATION=true).")
        return HookResult(success=True, state_delta={})

    # 1. Gather Source Text safely without dict.get or isinstance
    global_vars = state.global_context_vars
    actual_inputs = global_vars["inputs"] if "inputs" in global_vars else {}

    if not actual_inputs and "$inputs" in global_vars:
        try:
            inputs_dto = IntegrityGlobalInputsDTO.model_validate(global_vars["$inputs"])
            actual_inputs = inputs_dto.extract_source_texts()
        except Exception:
            actual_inputs = []

    source_texts: list[str] = []

    # Safe extraction without duck typing
    try:
        raw_val = actual_inputs if isinstance(actual_inputs, dict) else {"raw_inputs": actual_inputs}
        payload = IntegrityGlobalInputsDTO.model_validate(raw_val)
        source_texts = payload.extract_source_texts()
    except Exception:
        pass

    if not source_texts:
        logger.warning("[IntegrityHook] Verification bypassed: Missing input text in global_context.")
        return HookResult(success=True, state_delta={})

    # 1b. Gather Context (RAG)
    rag_text = ""
    step_ctx_raw = global_vars["step_context"] if "step_context" in global_vars else {}

    try:
        step_ctx = StepContext.model_validate(step_ctx_raw)
        if step_ctx.precedents:
            rag_text += f"{step_ctx.precedents}\n"
        for item in step_ctx.knowledge_items:
            rag_text += f"[{item.term}]: {item.definition}\n"
    except Exception:
        pass

    import json

    try:
        import asyncio
        from pathlib import Path

        seed_path = Path(__file__).parent.parent / "seed" / "seed_data.json"
        docs_dir = Path(__file__).parent.parent.parent / "docs"

        def _read_seed_and_docs() -> str:
            local_rag = ""
            if seed_path.exists():
                with open(seed_path, encoding="utf-8") as f:
                    seed_json = json.load(f)
                    if "prompt_blocks" in seed_json:
                        for pb in seed_json["prompt_blocks"]:
                            if "theory_grounding" in pb:
                                pass

            if docs_dir.exists():
                for doc_file in docs_dir.glob("*.md"):
                    with open(doc_file, encoding="utf-8") as f:
                        local_rag += f.read() + "\n"
            return local_rag

        rag_text += await asyncio.to_thread(_read_seed_and_docs)
    except Exception as e:
        logger.warning("[IntegrityHook] Failed to load documents for citation checking: %s", e)

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
    # Mutates a deep copy of the LLM's output
    delta = copy.deepcopy(state.inputs)

    from pydantic import ValidationError

    from backend_v2.models.domain.analyst import AnalystOutput
    from backend_v2.models.domain.evaluation import EvaluationResult

    # Strategy 1: V2 Analyst Output
    try:
        analyst_dto = AnalystOutput.model_validate(delta)
        if analyst_dto and analyst_dto.hypotheses:
            for h_idx, hyp in enumerate(analyst_dto.hypotheses):
                valid_quotes = []
                for quote in hyp.quotes:
                    total_count += 1
                    if is_hallucinated(quote):
                        invalid_citations.append(quote)
                        logger.warning("[IntegrityHook] Analyst hallucination detected.")
                    else:
                        valid_quotes.append(quote)
                        valid_count += 1

                # Mutate delta strictly
                if "hypotheses" in delta and len(delta["hypotheses"]) > h_idx:
                    delta["hypotheses"][h_idx]["quotes"] = valid_quotes
    except ValidationError:
        # Not an AnalystOutput, or malformed. Speculative parse fails cleanly.
        pass

    # Strategy 2: V2 Evaluation Result
    try:
        eval_dto = EvaluationResult.model_validate(delta)
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

            delta["citation_snippets"] = valid_quotes
    except ValidationError:
        # Not an EvaluationResult, or malformed. Speculative parse fails cleanly.
        pass

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
        delta["integrity_audit"] = audit.model_dump()

    return HookResult(success=True, state_delta=delta)


@hook_registry.register(name="enforce_hypothesis_linking")
def enforce_hypothesis_linking_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Workflow Data wrapper for enforce_hypothesis_linking.

    Ensure that Analyst Hypotheses have sequential, valid IDs (HYP-1, HYP-2...).
    """
    if not state:
        return HookResult(success=True, state_delta={})

    # V2 Architecture Isolation: Eradicated dict.get and isinstance
    from pydantic import ValidationError

    from backend_v2.models.domain.analyst import AnalystOutput

    payload = state.global_context_vars["step_analyst"] if "step_analyst" in state.global_context_vars else state.inputs

    try:
        analyst_dto = AnalystOutput.model_validate(payload)
    except ValidationError:
        return HookResult(success=True, state_delta={})

    hypotheses = analyst_dto.hypotheses if analyst_dto else []

    if not hypotheses:
        return HookResult(success=True, state_delta={})

    seen_ids = set()
    expected_idx = 1

    for hyp in hypotheses:
        h_id = hyp.id

        if not h_id:
            error_code = ErrorCodes.VALIDATION_FAILED
            msg = f"Hypothesis missing ID: {hyp}"
            logger.error("[IntegrityHook] %s: %s", error_code.name, msg)
            raise AppException(message=msg, status_code=500, details={"error_code": error_code.value})

        if not re.match(r"^HYP-\d+$", h_id):
            error_code = ErrorCodes.VALIDATION_FAILED
            msg = f"Invalid Hypothesis ID format: '{h_id}'. Expected 'HYP-N'."
            logger.error("[IntegrityHook] %s: %s", error_code.name, msg)
            raise AppException(message=msg, status_code=500, details={"error_code": error_code.value})

        num_part = int(h_id.split("-")[1])
        if num_part != expected_idx:
            error_code = ErrorCodes.STATE_INTEGRITY_ERROR
            msg = f"Hypothesis ID sequence error. Expected HYP-{expected_idx}, got {h_id}."
            logger.error("[IntegrityHook] %s: %s", error_code.name, msg)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": error_code.value, "expected": f"HYP-{expected_idx}", "got": h_id},
            )

        seen_ids.add(h_id)
        expected_idx += 1

    logger.info("[IntegrityHook] Verified %s sequential hypotheses.", len(hypotheses))
    return HookResult(success=True, state_delta={})
