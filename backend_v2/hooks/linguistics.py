"""Linguistics hooks for analyzing text patterns and language use."""

import logging
import uuid

from fastapi import status
from rapidfuzz import fuzz

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.linguistics import (
    LinguisticsPayloadDTO,
    LinguisticsResultDTO,
    PerformativePatternDTO,
)
from backend_v2.models.enums import SystemConfigID
from backend_v2.models.v2_core import ReportDataDTO, SystemConfigPerformativeLexicons

logger = logging.getLogger(__name__)


@hook_registry.register(name="detect_performative_patterns")
async def detect_performative_patterns(state: HookState, deps: HookDependencies) -> HookResult:
    """HOOK: detect_performative_patterns.

    Scans input texts (history, product) for performative/filler language patterns.
    Injects a strictly typed LinguisticsResult into the returned dictionary.
    Supports localization via 'language' context variable (default: 'en').

    Args:
        state: The current execution state of the hook.
        deps: Dependencies required for execution (e.g., repositories).

    Returns:
        A HookResult containing the detected pattern metadata in the state_delta.

    Raises:
        AppException: Raised with ErrorCodes.INVALID_OUTPUT_SCHEMA if payload validation fails.
    """
    logger.debug("[LinguisticsHook] Running detect_performative_patterns...")

    if not state:
        return HookResult(success=True, state_delta={})

    # Check for early exit signal (Workflow override)
    should_scan = state.inputs.get(
        "scan_for_performative_patterns", state.global_context_vars.get("scan_for_performative_patterns", True)
    )
    if str(should_scan).lower() in ["false", "0"]:
        logger.debug("[LinguisticsHook] Skipping scan due to scan_for_performative_patterns=False.")
        return HookResult(
            success=True,
            state_delta={
                "global_context_vars": {
                    "step_linguistics": LinguisticsResultDTO(performative_patterns=[]).model_dump(mode="json")
                }
            },
        )

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

    # Fetch from DB (Strict Fail-Fast)
    try:
        config_data = await deps.system_repo.get_system_config(SystemConfigID.PERFORMATIVE_LEXICONS.value)
        if not config_data:
            raise AppException(
                message=f"Fail-Fast: Performative Lexicon config '{SystemConfigID.PERFORMATIVE_LEXICONS.value}' missing from database.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        config = SystemConfigPerformativeLexicons.model_validate(config_data)
        target_lexicon = config.lexicon_configs.get(lang_simple)
        if not target_lexicon or not target_lexicon.words:
            raise AppException(
                message=f"Fail-Fast: Missing performative lexicon words for language '{lang_simple}'.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        patterns_to_check = target_lexicon.words
        fuzz_threshold = target_lexicon.fuzz_threshold
    except AppException:
        raise
    except Exception as e:
        msg = f"Failed to fetch or parse lexicon config from DB: {e}"
        logger.error("[LinguisticsHook] %s", msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        ) from e

    logger.debug("[LinguisticsHook] Using language '%s' with %s patterns.", lang_simple, len(patterns_to_check))

    detected: list[str] = []

    user_only_text = state.inputs.get("chat_log_user_only")
    if user_only_text and isinstance(user_only_text, str) and user_only_text.strip():
        text_to_scan = user_only_text.lower()
    else:
        # Scan all string inputs dynamically using DTO method
        text_to_scan = payload.get_text_to_scan()

    for pattern in patterns_to_check:
        if pattern in text_to_scan:
            detected.append(pattern)
        else:
            ratio = fuzz.partial_ratio(pattern, text_to_scan)
            if ratio >= fuzz_threshold:
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

    return HookResult(
        success=True, state_delta={"global_context_vars": {"step_linguistics": result_dto.model_dump(mode="json")}}
    )


def scan_report_for_slop(
    report_dto: ReportDataDTO, lexicon_words: list[str], fuzz_threshold: float = 90.0
) -> list[str]:
    """Pure function to scan the final rendered report text fields for performative AI jargon.

    Args:
        report_dto: The fully built report data object.
        lexicon_words: The list of performative patterns to check against.
        fuzz_threshold: The threshold for fuzzy matching.

    Returns:
        List of detected performative phrases.
    """
    detected_phrases: set[str] = set()

    # Collect texts
    texts_to_scan: list[str] = []

    if report_dto.layouts:
        for layout in report_dto.layouts:
            if layout.synthesis_blocks:
                for block in layout.synthesis_blocks:
                    if isinstance(block, dict) and "text" in block and isinstance(block["text"], str):
                        texts_to_scan.append(block["text"])

    all_matrices = []
    if report_dto.layouts:
        for layout in report_dto.layouts:
            if layout.axes:
                all_matrices.extend(layout.axes)
    for row in all_matrices:
        texts_to_scan.append(row.row_explanation)
        if row.coaching:
            texts_to_scan.append(row.coaching)
        if row.remediation_steps:
            texts_to_scan.append(row.remediation_steps)
        if row.semantic_reasoning:
            texts_to_scan.append(row.semantic_reasoning)
        if row.falsification:
            texts_to_scan.append(row.falsification)

    for raw_text in texts_to_scan:
        text_lower = raw_text.lower()
        for pattern in lexicon_words:
            if pattern in text_lower:
                detected_phrases.add(pattern)
            else:
                ratio = fuzz.partial_ratio(pattern, text_lower)
                if ratio >= fuzz_threshold:
                    detected_phrases.add(pattern)

    return list(detected_phrases)
