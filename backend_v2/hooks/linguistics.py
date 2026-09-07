"""Linguistics hooks for analyzing text patterns and language use."""

import logging
import uuid

from fastapi import status
from rapidfuzz import fuzz

from backend_v2.core.hook_registry import (
    HookDeltaDTO,
    HookDependencies,
    HookResult,
    HookState,
    hook_registry,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.linguistics import (
    DynamicLinguisticsExtractorDTO,
    LinguisticsPayloadDTO,
    LinguisticsResultDTO,
    PerformativePatternDTO,
)
from backend_v2.models.enums import SystemConfigID
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.prompts.execution.dynamic_linguistics import (
    DYNAMIC_PERFORMATIVE_SYSTEM_PROMPT,
    DYNAMIC_PERFORMATIVE_USER_PROMPT_TEMPLATE,
)
from backend_v2.models.v2_core import SystemConfigPerformativeLexicons
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
from backend_v2.settings import get_lexical_fuzz_threshold, get_settings

__all__ = ["detect_performative_patterns"]

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

    raw_inputs = state.inputs.raw_inputs
    gvars = state.global_context_vars.vars

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
                delta={
                    "step_linguistics": LinguisticsResultDTO(performative_patterns=[]).model_dump(mode="json"),
                    "global_context_vars": {
                        "step_linguistics": LinguisticsResultDTO(performative_patterns=[]).model_dump(mode="json")
                    },
                }
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
        if lang_simple not in config.lexicon_configs or not config.lexicon_configs[lang_simple].words:
            raise AppException(
                message=f"Fail-Fast: Missing performative lexicon words for language '{lang_simple}'.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        target_lexicon = config.lexicon_configs[lang_simple]
        baseline_words = list(target_lexicon.words)
        fuzz_threshold = get_lexical_fuzz_threshold(lang_simple)
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

    logger.debug("[LinguisticsHook] Using language '%s' with %s baseline words.", lang_simple, len(baseline_words))

    # Clean text extraction via DTO method encapsulating chat_log_user_only prioritization
    text_to_scan = payload.get_text_to_scan()

    # Dynamic LLM Extraction (feature-flagged)
    settings = get_settings()
    dynamic_phrases: list[str] = []

    if settings.enable_dynamic_performative_extraction and text_to_scan.strip():
        try:
            llm_client = await LLMClient.from_strategy(
                "fast",
                repository=deps.system_repo,
                pipeline_name="linguistics_hook",
            )
            executor = LLMTaskExecutor(prompt_compiler=PromptCompiler())
            user_content = DYNAMIC_PERFORMATIVE_USER_PROMPT_TEMPLATE.format(text_to_scan=text_to_scan)
            messages = [
                LLMMessageDTO(role="system", content=DYNAMIC_PERFORMATIVE_SYSTEM_PROMPT),
                LLMMessageDTO(role="user", content=user_content),
            ]
            extraction_dto, _ = await executor.execute_structured_task(
                client=llm_client,
                messages=messages,
                response_model=DynamicLinguisticsExtractorDTO,
            )
            for phrase in extraction_dto.detected_phrases:
                cleaned = phrase.strip().lower()
                if not cleaned:
                    continue
                # Strict physical lexical anchoring verification
                if text_to_scan.find(cleaned) != -1:
                    dynamic_phrases.append(cleaned)
                else:
                    logger.warning(
                        "[LinguisticsHook] Unanchored performative phrase discarded: '%s'",
                        phrase,
                        extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    )
        except (AppException, RuntimeError, ValueError, TimeoutError, OSError) as e:
            logger.warning(
                "[LinguisticsHook] Dynamic performative extraction failed, falling back to baseline: %s",
                e,
            )

    # Merge baseline and anchored dynamic phrases, preserving order and uniqueness
    patterns_to_check = list(dict.fromkeys(baseline_words + dynamic_phrases))

    detected: list[str] = []
    for pattern in patterns_to_check:
        pattern_lower = pattern.lower()
        if pattern_lower in text_to_scan:
            detected.append(pattern_lower)
        else:
            ratio = fuzz.partial_ratio(pattern_lower, text_to_scan)
            if ratio >= fuzz_threshold:
                detected.append(pattern_lower)

    # Deduplicate detected phrases while preserving order
    unique_detected = list(dict.fromkeys(detected))

    # Create strictly typed result
    patterns_list: list[PerformativePatternDTO] = [
        PerformativePatternDTO(
            pattern_id=f"ptrn_{uuid.uuid4().hex[:8]}",
            detected_phrase=p,
            category="performative_filler",
        )
        for p in unique_detected
    ]

    result_dto = LinguisticsResultDTO(performative_patterns=patterns_list)

    if unique_detected:
        logger.debug("   [LinguisticsHook] Detected patterns (%s): %s", lang_simple, unique_detected)

    return HookResult(
        success=True,
        state_delta=HookDeltaDTO(
            delta={
                "step_linguistics": result_dto.model_dump(mode="json"),
                "global_context_vars": {"step_linguistics": result_dto.model_dump(mode="json")},
            }
        ),
    )
