"""Validation hooks for structural integrity checks."""

import logging
import re

from fastapi import status

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes

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
        logger.error(f"[ValidationHook] {ErrorCodes.EMPTY_INPUT.name}: {msg}")
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.EMPTY_INPUT},
        )

    inputs = state.inputs

    if not inputs or not isinstance(inputs, dict):
        error_code = ErrorCodes.EMPTY_INPUT if inputs is None else ErrorCodes.INVALID_OUTPUT_SCHEMA
        msg = "Missing or invalid 'inputs' in state. Expected dict."
        status_code = status.HTTP_400_BAD_REQUEST if inputs is None else status.HTTP_500_INTERNAL_SERVER_ERROR
        logger.error(f"[ValidationHook] {error_code.name}: {msg}")
        raise AppException(
            message=msg,
            status_code=status_code,
            details={"error_code": error_code},
        )

    # Validate length for all payload texts, ignoring pure metadata and core identifiers
    valid_content_keys = 0
    for key, val in inputs.items():
        key_lower = key.lower()
        if (
            key_lower in ignored_keys
            or key_lower.endswith('_id')
            or key_lower.endswith('_mode')
            or key_lower.startswith('_')
        ):
            continue

        if not val or not str(val).strip():
            warnings.append({
                "type": f"{AppException.PROBLEM_BASE_URI}/empty-input",
                "title": "Empty Analysis Input",
                "error_code": ErrorCodes.EMPTY_INPUT.name,
                "detail": f"Field '{key}' requires content.",
                "meta": {"key": key}
            })
            continue

        text = str(val).strip()
        if len(text) < MIN_CHARS:
            warnings.append({
                "type": f"{AppException.PROBLEM_BASE_URI}/input-too-short",
                "title": "Analysis Input Too Short",
                "error_code": ErrorCodes.VALIDATION_FAILED.name,
                "detail": f"Field '{key}' has length {len(text)}, required {MIN_CHARS}.",
                "meta": {"key": key, "length": len(text), "min_chars": MIN_CHARS}
            })
            continue

        valid_content_keys += 1

    if valid_content_keys == 0 and len(warnings) == 0:
        warnings.append({
            "type": f"{AppException.PROBLEM_BASE_URI}/no-content",
            "title": "No Content Detected",
            "error_code": ErrorCodes.EMPTY_INPUT.name,
            "detail": "No valid analysis content was provided in the payload.",
            "meta": {}
        })

    try:
        # Create pure dict result
        result = {"is_valid": len(warnings) == 0, "errors": warnings}
    except Exception as e:
        # Pydantic validation failure -> System Error
        error_code = ErrorCodes.INTERNAL_SERVER_ERROR
        logger.error(f"[ValidationHook] Failed to create ValidationResult: {e}")
        raise AppException(message=f"System Error: {e}", status_code=500, details={"error_code": error_code}) from e

    if not result["is_valid"]:
        msg = f"Structural Validation Failed: {warnings}"
        logger.error(f"[ValidationHook] {msg}")

        # FAIL FAST: Pre-validation failure is a client error (Bad Request)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.VALIDATION_FAILED, "warnings": warnings},
        )
    else:
        logger.debug("[ValidationHook] Checks passed.")

    return HookResult(success=True, state_delta={"validation_result": result})


@hook_registry.register(name="verify_output_language")
def verify_output_language(state: HookState, deps: HookDependencies) -> HookResult:
    """HOOK: verify_output_language.

    Post-execution soft-validation check. Scans generated text for English leakage
    when the target locale is restricted. Uses a Fail-Soft heuristic to not break
    execution flow but records RFC 7807 style warnings in _system_warnings.
    """
    logger.debug("[ValidationHook] Running output language check...")

    if not state or not isinstance(state.inputs, dict):
        return HookResult(success=True, state_delta={})  # Can only validate dicts

    target_locale = state.metadata.get("target_locale", "en").lower()

    if target_locale == "en":
        return HookResult(success=True, state_delta={})  # English is allowed

    # Heuristics: Extremely common, unambiguous English stop words.
    # We use word boundary \b to prevent matching inside Finnish words.
    english_stops = {"the", "and", "is", "are", "was", "were", "this", "that", "these", "those", "from", "with"}

    # We specifically target Generative text fields, not strict citations.
    target_keys = ["evaluation_notes"]
    leakage_detected = False

    for key, value in state.inputs.items():
        if not isinstance(value, str):
            continue

        if key in target_keys or key.endswith("_justification"):
            words = set(re.findall(r'\b[a-z]{2,}\b', value.lower()))
            overlap = words.intersection(english_stops)

            # If 3 or more distinct core English stop words are found in the field,
            # it is highly probable the LLM generated English instead of the target locale.
            if len(overlap) >= 3:
                leakage_detected = True
                logger.warning(
                    f"[ValidationHook] Language mismatch detected in field '{key}'. "
                    f"Target locale was '{target_locale}' but detected English stop words: {overlap}. "
                    f"Text excerpt: {value[:100]}..."
                )

    delta = {}
    if leakage_detected:
        delta["_system_warnings"] = state.inputs.get("_system_warnings", [])
        delta["_system_warnings"].append({
            "type": f"{AppException.PROBLEM_BASE_URI}/language-mismatch",
            "title": "Output Language Mismatch",
            "detail": f"Model neglected the '{target_locale}' localization mandate and leaked English.",
            "error_code": ErrorCodes.VALIDATION_FAILED.name
        })

    return HookResult(success=True, state_delta=delta)
