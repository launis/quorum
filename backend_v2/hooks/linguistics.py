"""Linguistics hooks for analyzing text patterns and language use."""

import logging
import uuid

from fastapi import status

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.linguistics import (
    LinguisticsPayloadDTO,
    LinguisticsResultDTO,
    PerformativePatternDTO,
)

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
def detect_performative_patterns(state: HookState, deps: HookDependencies) -> HookResult:
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

    if not state:
        return HookResult(success=True, state_delta={})

    # Strict Validation via DTO inflation
    try:
        payload_data = {"dynamic_inputs": state.inputs}
        if "language" in state.inputs:
            payload_data["language"] = state.inputs["language"]
        payload = LinguisticsPayloadDTO.model_validate(payload_data)
    except Exception as e:
        error_code = ErrorCodes.INVALID_OUTPUT_SCHEMA
        msg = f"Failed to strictly validate inputs for linguistics: {e}"
        logger.error("[LinguisticsHook] %s: %s", error_code.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": error_code.value},
        ) from e

    # Extract Language safely without dict.get()
    lang_simple = payload.extract_language(state.global_context_vars)

    # Select patterns securely without .get()
    patterns_to_check = PERFORMATIVE_PATTERNS["en"]
    if lang_simple in PERFORMATIVE_PATTERNS:
        patterns_to_check = PERFORMATIVE_PATTERNS[lang_simple]

    logger.debug("[LinguisticsHook] Using language '%s' with %s patterns.", lang_simple, len(patterns_to_check))

    detected: list[str] = []

    # Scan all string inputs dynamically using DTO method
    text_to_scan = payload.get_text_to_scan()

    for pattern in patterns_to_check:
        if pattern in text_to_scan:
            detected.append(pattern)

    # Create strictly typed result
    patterns_list: list[PerformativePatternDTO] = []

    if detected:
        for p in detected:
            patterns_list.append(
                PerformativePatternDTO(
                    pattern_id=f"ptrn_{uuid.uuid4().hex[:8]}",
                    detected_phrase=p,
                    category="performative_filler",
                )
            )

    result_dto = LinguisticsResultDTO(performative_patterns=patterns_list)

    if detected:
        logger.debug("   [LinguisticsHook] Detected patterns (%s): %s", lang_simple, detected)

    return HookResult(success=True, state_delta={"linguistics_result": result_dto.model_dump()})
