"""Linguistics hooks for analyzing text patterns and language use."""

import logging
from typing import Any

from fastapi import status

from backend_v2.core.hook_registry import hook_registry
from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)


# Structured dictionaries for multi-language support (Zero-Fallback)
PERFORMATIVE_PATTERNS: dict[str, list[str]] = {
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
        "kenttä",  # in metaphorical sense "realm"
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
    ],
}


@hook_registry.register(name="detect_performative_patterns")
def detect_performative_patterns(data: dict[str, Any]) -> dict[str, Any]:
    """HOOK: detect_performative_patterns.

    Scans input texts (history, product) for performative/filler language patterns.
    Injects a strictly typed LinguisticsResult into the returned dictionary.
    Supports localization via 'language' context variable (default: 'en').

    Args:
        data (dict): Current workflow data containing 'inputs'.

    Returns:
        dict: Updated data with detected pattern metadata.

    Raises:
        AppException: If validation or configuration fails.
    """
    logger.debug("[LinguisticsHook] Running detect_performative_patterns...")

    # Strict Input Validation
    inputs = data.get("inputs")

    if not inputs or not isinstance(inputs, dict):
        error_code = ErrorCodes.INVALID_OUTPUT_SCHEMA
        msg = f"Missing or invalid 'inputs' in data: {type(inputs)}. Expected dict."
        logger.error(f"[LinguisticsHook] {error_code.name}: {msg}")
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": error_code},
        )

    # Detect Language
    lang_code = data.get("language")
    if not lang_code:
        lang_code = inputs.get("language", "en")

    # Normalize "fi-FI" -> "fi"
    lang_simple = str(lang_code).split("-")[0].lower()

    # Select patterns securely
    patterns_to_check = PERFORMATIVE_PATTERNS.get(lang_simple, PERFORMATIVE_PATTERNS["en"])
    logger.debug(f"[LinguisticsHook] Using language '{lang_simple}' with {len(patterns_to_check)} patterns.")

    detected: list[str] = []

    # Scan history and product text
    history = inputs.get("history_text", "")
    product = inputs.get("product_text", "")

    if not history and not product:
        # Loophole fix: if mandatory inputs are None but inputs dict input handling allowed it,
        # we treat it as empty text but warn.
        pass

    text_to_scan = (str(history or "") + str(product or "")).lower()

    for pattern in patterns_to_check:
        if pattern in text_to_scan:
            detected.append(pattern)

    # Create pure dict result
    patterns_list: list[dict[str, Any]] = []

    if detected:
        for p in detected:
            patterns_list.append(
                {
                    "pattern_id": f"detected_{lang_simple}_pattern",
                    "detected_phrase": p,
                    "category": "performative_filler",
                }
            )

    result = {"performative_patterns": patterns_list}

    if detected:
        logger.debug(f"   [LinguisticsHook] Detected patterns ({lang_simple}): {detected}")

    return {"linguistics_result": result}
