"""Linguistics hooks for analyzing text patterns and language use."""

import logging
import uuid

from fastapi import status
from rapidfuzz import fuzz

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDeltaDTO,
    HookDependencies,
    HookResult,
    HookState,
    hook_registry,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.linguistics import (
    LinguisticsPayloadDTO,
    LinguisticsResultDTO,
    PerformativePatternDTO,
)
from backend_v2.models.enums import SystemConfigID
from backend_v2.models.v2_core import SystemConfigPerformativeLexicons

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
        return HookResult(success=True, state_delta=HookDeltaDTO())

    raw_inputs = (
        state.inputs.raw_inputs
        if isinstance(state.inputs, ExecutionInputsDTO)
        else (state.inputs if isinstance(state.inputs, dict) else {})
    )
    gvars = (
        state.global_context_vars.vars
        if isinstance(state.global_context_vars, GlobalContextVarsDTO)
        else (state.global_context_vars if isinstance(state.global_context_vars, dict) else {})
    )

    # Check for early exit signal (Workflow override)
    should_scan = True
    if "scan_for_performative_patterns" in raw_inputs:
        should_scan = raw_inputs["scan_for_performative_patterns"]
    elif "scan_for_performative_patterns" in gvars:
        should_scan = gvars["scan_for_performative_patterns"]

    if str(should_scan).lower() in ["false", "0"]:
        logger.debug("[LinguisticsHook] Skipping scan due to scan_for_performative_patterns=False.")
        return HookResult(
            success=True,
            state_delta=HookDeltaDTO(
                delta={"step_linguistics": LinguisticsResultDTO(performative_patterns=[]).model_dump(mode="json")}
            ),
        )

    # Strict Validation via DTO inflation
    try:
        payload_data = {"dynamic_inputs": raw_inputs}
        if "language" in raw_inputs:
            payload_data["language"] = raw_inputs["language"]
        payload = LinguisticsPayloadDTO.model_validate(payload_data)
    except Exception as e:
        msg = f"Failed to strictly validate inputs for linguistics: {e}"
        logger.error("[LinguisticsHook] %s: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        ) from e

    # Extract Language safely without dict.get()
    lang_simple = payload.extract_language(gvars)

    # Fetch from DB (Strict Fail-Fast)
    try:
        config_data = await deps.system_repo.get_system_config(SystemConfigID.PERFORMATIVE_LEXICONS.value)
        if not config_data:
            raise AppException(
                message=f"Fail-Fast: Lexicon config '{SystemConfigID.PERFORMATIVE_LEXICONS.value}' missing.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        config = SystemConfigPerformativeLexicons.model_validate(config_data)
        target_lexicon = config.lexicon_configs[lang_simple] if lang_simple in config.lexicon_configs else None
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

    user_only_text = raw_inputs["chat_log_user_only"] if "chat_log_user_only" in raw_inputs else None
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
        success=True,
        state_delta=HookDeltaDTO(delta={"step_linguistics": result_dto.model_dump(mode="json")}),
    )
