"""Validation hooks for structural integrity checks."""

import logging
import re

from fastapi import status

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.validation import (
    SystemWarningsStateDTO,
    ValidationHookPayloadDTO,
    ValidationResultDTO,
    ValidationWarningDTO,
)
from backend_v2.models.dtos.state import HookStateMetadata, I18nStatePayload

logger = logging.getLogger(__name__)


@hook_registry.register(name="verify_structure")
def verify_structure(state: HookState, deps: HookDependencies) -> HookResult:
    """HOOK: verify_structure.

    Pre-execution validation check to ensure inputs ('history_text', 'product_text', 'reflection_text')
    have sufficient content length for meaningful analysis.
    Adds warnings to 'structural_warnings' if checks fail.

    Min Length: 100 chars.

    Args:
        data (dict): Current workflow data containing 'inputs'.
        context (HookExecutionContext): The strongly typed execution context.

    Returns:
        dict: Updated data with warnings if applicable.

    Raises:
        AppException: If structure check fails (Fail Fast).
    """
    logger.debug("[ValidationHook] Running structural inputs check...")

    # Minimum char limits
    MIN_CHARS = 10
    # System metadata keys that should bypass length constraints
    ignored_keys = {"language", "locale", "target_locale"}

    warnings = []

    if not state:
        msg = "State missing in validation hook."
        logger.error("[ValidationHook] %s: %s", ErrorCodes.EMPTY_INPUT.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.EMPTY_INPUT},
        )

    try:
        # Zero-Compromise: Enforce strict dictionary structure via DTO
        payload = ValidationHookPayloadDTO.model_validate(state.inputs)
    except Exception as e:
        msg = "Missing or invalid 'inputs' in state. Expected dict."
        logger.error("[ValidationHook] %s: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA},
        ) from e

    inputs_dict = payload.root

    # Validate length for all payload texts, ignoring pure metadata and core identifiers
    valid_content_keys = 0
    for key, val in inputs_dict.items():
        key_lower = key.lower()
        if (
            key_lower in ignored_keys
            or key_lower.endswith("_id")
            or key_lower.endswith("_mode")
            or key_lower.startswith("_")
        ):
            continue

        if not val or not str(val).strip():
            warnings.append(
                ValidationWarningDTO(
                    type=f"{AppException.PROBLEM_BASE_URI}/empty-input",
                    title="Empty Analysis Input",
                    error_code=ErrorCodes.EMPTY_INPUT.name,
                    detail=f"Field '{key}' requires content.",
                    meta={"key": key},
                )
            )
            continue

        text = str(val).strip()
        if len(text) < MIN_CHARS:
            warnings.append(
                ValidationWarningDTO(
                    type=f"{AppException.PROBLEM_BASE_URI}/input-too-short",
                    title="Analysis Input Too Short",
                    error_code=ErrorCodes.VALIDATION_FAILED.name,
                    detail=f"Field '{key}' has length {len(text)}, required {MIN_CHARS}.",
                    meta={"key": key, "length": len(text), "min_chars": MIN_CHARS},
                )
            )
            continue

        valid_content_keys += 1

    if valid_content_keys == 0 and len(warnings) == 0:
        warnings.append(
            ValidationWarningDTO(
                type=f"{AppException.PROBLEM_BASE_URI}/no-content",
                title="No Content Detected",
                error_code=ErrorCodes.EMPTY_INPUT.name,
                detail="No valid analysis content was provided in the payload.",
                meta={},
            )
        )

    try:
        # Create strict DTO result
        result_dto = ValidationResultDTO(is_valid=len(warnings) == 0, errors=warnings)
    except Exception as e:
        # Pydantic validation failure -> System Error
        error_code = ErrorCodes.INTERNAL_SERVER_ERROR
        logger.error("[ValidationHook] Failed to create ValidationResult: %s", e)
        raise AppException(message=f"System Error: {e}", status_code=500, details={"error_code": error_code}) from e

    if not result_dto.is_valid:
        msg = f"Structural Validation Failed: {[w.model_dump() for w in warnings]}"
        logger.error("[ValidationHook] %s", msg)

        # FAIL FAST: Pre-validation failure is a client error (Bad Request)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.VALIDATION_FAILED, "warnings": [w.model_dump() for w in warnings]},
        )
    else:
        logger.debug("[ValidationHook] Checks passed.")

    return HookResult(success=True, state_delta={"validation_result": result_dto.model_dump()})


@hook_registry.register(name="verify_output_language")
def verify_output_language(state: HookState, deps: HookDependencies) -> HookResult:
    """HOOK: verify_output_language.

    Post-execution soft-validation check. Scans generated text for English leakage
    when the target locale is restricted. Uses a Fail-Soft heuristic to not break
    execution flow but records RFC 7807 style warnings in _system_warnings.
    """
    logger.debug("[ValidationHook] Running output language check...")

    if not state:
        return HookResult(success=True, state_delta={})

    try:
        payload = ValidationHookPayloadDTO.model_validate(state.inputs)
        meta = HookStateMetadata.model_validate(state.metadata)
        _ = I18nStatePayload.model_validate(state.inputs)
    except Exception as e:
        msg = "Execution state is missing mandatory 'target_locale' metadata or 'language' inputs."
        logger.error("[ValidationHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(
            message=msg,
            status_code=400,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        ) from e

    target_locale = meta.target_locale.lower()
    inputs_dict = payload.root

    if target_locale == "en":
        return HookResult(success=True, state_delta={})  # English is allowed

    # Heuristics: Extremely common, unambiguous English stop words.
    # We use word boundary \b to prevent matching inside Finnish words.
    english_stops = {"the", "and", "is", "are", "was", "were", "this", "that", "these", "those", "from", "with"}

    # We specifically target Generative text fields, not strict citations.
    target_keys = ["evaluation_notes"]
    leakage_detected = False

    for key, value in inputs_dict.items():
        if not isinstance(value, str):
            continue

        if key in target_keys or key.endswith("_justification"):
            words = set(re.findall(r"\b[a-z]{2,}\b", value.lower()))
            overlap = words.intersection(english_stops)

            # If 3 or more distinct core English stop words are found in the field,
            # it is highly probable the LLM generated English instead of the target locale.
            if len(overlap) >= 3:
                leakage_detected = True
                logger.warning(
                    "[ValidationHook] Language mismatch detected in field '%s'. "
                    "Target locale was '%s' but detected English stop words: %s. "
                    "Text excerpt: %s...",
                    key,
                    target_locale,
                    overlap,
                    value[:100],
                )

    delta = {}
    if leakage_detected:
        try:
            warnings_payload = SystemWarningsStateDTO.model_validate(state.inputs)
            existing_warnings = warnings_payload.system_warnings.copy()
        except Exception:
            existing_warnings = []

        new_warning = ValidationWarningDTO(
            type=f"{AppException.PROBLEM_BASE_URI}/language-mismatch",
            title="Output Language Mismatch",
            error_code=ErrorCodes.VALIDATION_FAILED.name,
            detail=f"Model neglected the '{target_locale}' localization mandate and leaked English.",
            meta={},
        )
        existing_warnings.append(new_warning)
        delta["_system_warnings"] = [w.model_dump() for w in existing_warnings]

    return HookResult(success=True, state_delta=delta)
