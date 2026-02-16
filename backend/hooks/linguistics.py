"""Linguistics hooks for analyzing text patterns and language use."""

import logging
from typing import Any, List, Dict

from backend.exceptions import AppException
from backend.models.domain import LinguisticsResult, PerformativePattern
from backend.models.state import WorkflowState

logger = logging.getLogger(__name__)


# Structured dictionaries for multi-language support (Zero-Fallback)
PERFORMATIVE_PATTERNS: Dict[str, List[str]] = {
    "en": [
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
        "game changer",
        "cutting edge",
        "revolutionary",
        "dive deep",
        "in conclusion",
        "it is important to note",
        "vast array",
        "myriad of",
        "unleash the power",
        "embark on a journey",
        "beacon of",
    ],
    "fi": [
        "syventyä",
        "kattava katsaus",
        "rikas historia",
        "osoitus siitä",
        "korostaa merkitystä",
        "keskeinen rooli",
        "merkittävä rooli",
        "maisema",  # in metaphorical sense "landscape"
        "kenttä",   # in metaphorical sense "realm"
        "luoda tunnetta",
        "mullistava",
        "huippuluokan",
        "vallankumouksellinen",
        "sukeltaa syvälle",
        "yhteenvetona",
        "on tärkeää huomata",
        "voidaan todeta",
        "laaja kirjo",
        "lukuisia",
        "vapauttaa voima",
        "lähteä matkalle",
        "majakka",
        "dynaaminen",
        "innovatiivinen",
        "saumaton",
        "synergia",
        "kokonaisvaltainen",
        "merkittävästi",
        "avainasemassa",
        "tulevaisuuden näkymät",
        "digitaalinen aikakausi",
        "virstanpylväs",
        "paradigm",
        "ekosysteemi",  # often overused
        "kärkihanke",
        "strateginen",
        "optimoitu",
        "resonoimaan",
        "navigoida",  # metaphorical
    ]
}

def detect_performative_patterns(state: WorkflowState) -> WorkflowState:
    """HOOK: detect_performative_patterns.

    Scans input texts (history, product) for performative/filler language patterns.
    Injects a strictly typed LinguisticsResult into 'linguistics_result'.
    Supports localization via 'language' context variable (default: 'en').

    Args:
        state (WorkflowState): Current workflow state.

    Returns:
        WorkflowState: Updated state with detected pattern metadata.

    Raises:
        AppException: If validation or configuration fails.
    """
    logger.debug("[LinguisticsHook] Running detect_performative_patterns...")

    inputs = state.context_variables.get("inputs", {})
    if not isinstance(inputs, dict):
        inputs = {}

    # Detect Language (Fail Fast fallback to 'en' is acceptable for safety, but strict on types)
    # We check context_variables first, then inputs (legacy)
    lang_code = state.context_variables.get("language")
    if not lang_code:
        # Fallback to inputs if not in root context
        lang_code = inputs.get("language", "en")
    
    # Normalize "fi-FI" -> "fi"
    lang_simple = str(lang_code).split("-")[0].lower()
    
    # Select patterns securely
    patterns_to_check = PERFORMATIVE_PATTERNS.get(lang_simple, PERFORMATIVE_PATTERNS["en"])
    logger.debug(f"[LinguisticsHook] Using language '{lang_simple}' with {len(patterns_to_check)} patterns.")

    detected: List[str] = []
    
    # Scan history and product text
    text_to_scan = (str(inputs.get("history_text", "") or "")) + (str(inputs.get("product_text", "") or ""))
    text_lower = text_to_scan.lower()

    for pattern in patterns_to_check:
        if pattern in text_lower:
            detected.append(pattern)

    # Create strictly typed result
    try:
        patterns_list: List[PerformativePattern] = []
        if detected:
            for p in detected:
                # We are creating these from known strings, so we can be sure of structure
                patterns_list.append(
                    PerformativePattern(
                        pattern_id=f"detected_{lang_simple}_pattern",
                        detected_phrase=p,
                        category="performative_filler",
                    )
                )

        result = LinguisticsResult(performative_patterns=patterns_list)

    except Exception as e:
        # Generic catch for Pydantic failures
        error_code = "LINGUISTICS_VALIDATION_FAILED"
        logger.error(f"[LinguisticsHook] {error_code}: {e}")
        raise AppException(
            message=f"Validation Error: {e}", status_code=500, details={"error_code": error_code}
        ) from e

    # IMMUTABILITY FIX
    new_context = state.context_variables.copy()
    new_context["linguistics_result"] = result

    if detected:
        logger.debug(f"   [LinguisticsHook] Detected patterns ({lang_simple}): {detected}")

    return state.model_copy(update={"context_variables": new_context})
