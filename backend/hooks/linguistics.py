"""Linguistics hooks for analyzing text patterns and language use."""

import json
import logging

from backend.models.state import WorkflowState

logger = logging.getLogger(__name__)


def detect_performative_patterns(state: WorkflowState) -> WorkflowState:
    """HOOK: detect_performative_patterns.

    Scans input texts (history, product) for performative/filler language patterns.
    Injects a JSON list of matches into 'aux_data.performative_patterns_detected'.
    Used to flag potentially generic or low-quality input text.

    Args:
        state (WorkflowState): Current workflow state.

    Returns:
        WorkflowState: Updated state with detected pattern metadata.

    """
    logger.debug("[LinguisticsHook] Running detect_performative_patterns...")

    # TODO (Zero-Fallback compliance): Move patterns to database configuration
    # For now, these are static linguistic markers for AI-generated text detection
    suspect_patterns = [
        "delve into",
        "tapestry",
        "comprehensive overview",
        "rich history",
        "testament to",
        "underscore the importance",
        "pivotal role",
        "landscape of",
        "realm of",
        "foster a sense of",
    ]

    detected = []
    # Scan history and product text
    inputs = state.context_variables.get("inputs", {})
    if not isinstance(inputs, dict):
        inputs = {}

    text_to_scan = (inputs.get("history_text", "") or "") + (inputs.get("product_text", "") or "")
    text_lower = text_to_scan.lower()

    for pattern in suspect_patterns:
        if pattern in text_lower:
            detected.append(pattern)

    # Create strictly typed result
    try:
        from backend.models.domain import LinguisticsResult, PerformativePattern
        
        patterns_list = []
        if detected:
            for p in detected:
                # Assuming 'p' is a dict from linguistics.py logic or needs parsing
                # If 'detected' is already a list of dicts:
                if isinstance(p, dict):
                    patterns_list.append(PerformativePattern(
                        pattern_id=str(p.get("id", "unknown")),
                        detected_phrase=str(p.get("phrase", "")),
                        category=str(p.get("category", "general"))
                    ))
                # If 'detected' is list of strings (simplified logic in some versions)
                elif isinstance(p, str):
                     patterns_list.append(PerformativePattern(
                        pattern_id="detected_pattern",
                        detected_phrase=p,
                        category="general"
                    ))

        result = LinguisticsResult(performative_patterns=patterns_list)
    except ImportError:
        logger.error("[LinguisticsHook] Could not import LinguisticsResult")
        return state

    # IMMUTABILITY FIX
    new_context = state.context_variables.copy()
    new_context["linguistics_result"] = result
    
    # Legacy support
    new_context["performative_patterns_detected"] = json.dumps(detected) if detected else "[]"
    
    if detected:
        logger.debug(f"   [LinguisticsHook] Detected patterns: {detected}")

    return state.model_copy(update={"context_variables": new_context})
