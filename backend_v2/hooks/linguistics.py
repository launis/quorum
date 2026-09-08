"""Linguistics hooks for analyzing text patterns and language use."""

import logging
import uuid

from fastapi import status
from pydantic import ValidationError
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
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.prompts.execution.dynamic_linguistics import (
    DYNAMIC_PERFORMATIVE_SYSTEM_PROMPT,
    DYNAMIC_PERFORMATIVE_USER_PROMPT_TEMPLATE,
)
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

    # Strict Validation via DTO inflation
    try:
        payload_data = {"dynamic_inputs": raw_inputs}
        if "language" in raw_inputs:
            payload_data["language"] = raw_inputs["language"]
        payload = LinguisticsPayloadDTO.model_validate(payload_data)
    except (ValidationError, TypeError, ValueError) as e:
        msg = f"Failed to strictly validate inputs for linguistics: {e}"
        logger.error("[LinguisticsHook] %s: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        ) from e

    # Extract Language safely without dict.get()
    lang_simple = payload.extract_language(gvars)

    # Clean text extraction via DTO method encapsulating chat_log_user_only prioritization
    text_to_scan = payload.get_text_to_scan()
    text_to_scan_lower = text_to_scan.lower()
    total_word_count = len(text_to_scan.split())

    # Check for early exit signal (Workflow override)
    should_scan = True
    if "scan_for_performative_patterns" in raw_inputs:
        should_scan = raw_inputs["scan_for_performative_patterns"]
    elif "scan_for_performative_patterns" in gvars:
        should_scan = gvars["scan_for_performative_patterns"]

    if str(should_scan).lower() in ["false", "0"]:
        logger.debug("[LinguisticsHook] Skipping scan due to scan_for_performative_patterns=False.")
        empty_dto = LinguisticsResultDTO(performative_patterns=[], total_word_count=total_word_count)
        return HookResult(
            success=True,
            state_delta=HookDeltaDTO(
                delta={
                    "step_linguistics": empty_dto.model_dump(mode="json"),
                    "global_context_vars": {"step_linguistics": empty_dto.model_dump(mode="json")},
                }
            ),
        )

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
            user_content = DYNAMIC_PERFORMATIVE_USER_PROMPT_TEMPLATE.format(
                language=lang_simple, text_to_scan=text_to_scan
            )
            messages = [
                LLMMessageDTO(role="system", content=DYNAMIC_PERFORMATIVE_SYSTEM_PROMPT),
                LLMMessageDTO(role="user", content=user_content),
            ]
            extraction_dto, _ = await executor.execute_structured_task(
                client=llm_client,
                messages=messages,
                response_model=DynamicLinguisticsExtractorDTO,
            )
            fuzz_threshold = get_lexical_fuzz_threshold(lang_simple)
            for phrase in extraction_dto.detected_phrases:
                cleaned = phrase.strip().lower()
                if not cleaned:
                    continue
                # Strict physical lexical anchoring verification (exact substring or morphological fallback)
                if text_to_scan_lower.find(cleaned) != -1:
                    dynamic_phrases.append(cleaned)
                else:
                    ratio = fuzz.partial_ratio(cleaned, text_to_scan_lower)
                    if ratio >= fuzz_threshold:
                        dynamic_phrases.append(cleaned)
                    else:
                        logger.warning(
                            "[LinguisticsHook] Unanchored performative phrase discarded: '%s'",
                            phrase,
                            extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                        )
        except (AppException, RuntimeError, ValueError, TimeoutError, OSError) as e:
            logger.warning(
                "[LinguisticsHook] Dynamic performative extraction failed: %s",
                e,
            )

    # Deduplicate detected phrases while preserving order
    unique_detected = list(dict.fromkeys(dynamic_phrases))

    # Create strictly typed result
    patterns_list: list[PerformativePatternDTO] = [
        PerformativePatternDTO(
            pattern_id=f"ptrn_{uuid.uuid4().hex[:8]}",
            detected_phrase=p,
            category="performative_filler",
        )
        for p in unique_detected
    ]

    result_dto = LinguisticsResultDTO(
        performative_patterns=patterns_list,
        total_word_count=total_word_count,
    )

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
