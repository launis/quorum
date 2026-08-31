"""Validation hooks for structural integrity checks in Phase 9 system."""

import logging
import re
from typing import Any

from fastapi import status
from pydantic import ValidationError

from backend_v2.core.hook_registry import (
    HookDeltaDTO,
    HookDependencies,
    HookResult,
    HookState,
    hook_registry,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.validation import (
    GuttmanAtomItemDTO,
    SystemWarningsStateDTO,
    ValidationHookPayloadDTO,
    ValidationResultDTO,
    ValidationWarningDTO,
)

logger = logging.getLogger(__name__)


@hook_registry.register(name="verify_structure")
def verify_structure(state: HookState | None, deps: HookDependencies) -> HookResult:
    """HOOK: verify_structure.

    Pre-execution validation check to ensure inputs have sufficient content length for meaningful analysis.
    Adds warnings to 'structural_warnings' if checks fail.

    Args:
        state: Current frozen workflow state.
        deps: Injected hook runtime dependencies.

    Returns:
        Structured state delta container.

    Raises:
        AppException: EMPTY_INPUT if state is missing or fields are empty.
        AppException: INVALID_OUTPUT_SCHEMA if inputs validation fails.
        AppException: VALIDATION_FAILED if structural rules are violated.
    """
    logger.debug("[ValidationHook] Running structural inputs check...")

    # Minimum char limits
    MIN_CHARS = 10
    # System metadata keys that should bypass length constraints
    ignored_keys = {"language", "locale", "target_locale"}

    warnings: list[ValidationWarningDTO] = []

    if not state:
        msg = "State missing in validation hook."
        logger.error("[ValidationHook] %s: %s", ErrorCodes.EMPTY_INPUT.name, msg, exc_info=True)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.EMPTY_INPUT.value},
        )

    try:
        # Zero-Compromise: Enforce strict dictionary structure via DTO validation
        payload_source = state.inputs.raw_inputs if state.inputs.raw_inputs else state.inputs.model_dump()
        payload = ValidationHookPayloadDTO.model_validate(payload_source)
    except ValidationError as e:
        msg = "Missing or invalid 'inputs' in state. Expected dict."
        logger.error("[ValidationHook] %s: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, msg, exc_info=True)
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        ) from e

    inputs_dict = payload.root

    # V2 Architecture: Flatten nested structures to validate actual text content
    fields_to_validate: dict[str, Any] = {}

    # 1. Unpack raw_inputs dynamically
    raw_sub = inputs_dict.get("raw_inputs")
    if raw_sub is not None:
        try:
            fields_to_validate.update(ValidationHookPayloadDTO.model_validate(raw_sub).root)
        except ValidationError:
            pass

    # 2. Unpack inputs dynamically
    inputs_sub = inputs_dict.get("inputs")
    if inputs_sub is not None:
        try:
            fields_to_validate.update(ValidationHookPayloadDTO.model_validate(inputs_sub).root)
        except ValidationError:
            pass

    # Fallback to the root if it's a flat payload, excluding known container keys
    if not fields_to_validate and not ("steps" in inputs_dict or "raw_inputs" in inputs_dict):
        fields_to_validate = inputs_dict

    # Validate length for all payload texts, ignoring pure metadata and core identifiers
    valid_content_keys = 0
    for key, val in fields_to_validate.items():
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
    except ValidationError as e:
        logger.error("[ValidationHook] Failed to create ValidationResult: %s", e, exc_info=True)
        raise AppException(
            message=f"System Error: {e}",
            status_code=500,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        ) from e

    if not result_dto.is_valid:
        # Preserve the structural dumps cleanly utilizing model_dump to prevent bypass errors
        serialized_warnings = [w.model_dump() for w in warnings]
        msg = f"Structural Validation Failed: {serialized_warnings}"
        logger.error("[ValidationHook] %s", msg)

        # FAIL FAST: Pre-validation failure is a client error (Bad Request)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "warnings": serialized_warnings},
        )
    else:
        logger.debug("[ValidationHook] Checks passed.")

    return HookResult(
        success=True,
        state_delta=HookDeltaDTO(delta={"validation_result": result_dto.model_dump(mode="json")}),
    )


@hook_registry.register(name="verify_output_language")
def verify_output_language(state: HookState | None, deps: HookDependencies) -> HookResult:
    """HOOK: verify_output_language.

    Post-execution soft-validation check scanning generated text for English leakage.

    Args:
        state: Current frozen workflow state.
        deps: Injected hook runtime dependencies.

    Returns:
        Structured state delta container.

    Raises:
        AppException: VALIDATION_FAILED if language checking crashes due to schema mismatch.
        AppException: INVALID_OUTPUT_SCHEMA if _system_warnings validation fails.
    """
    logger.debug("[ValidationHook] Running output language check...")

    if not state:
        return HookResult(success=True, state_delta=HookDeltaDTO())

    try:
        inputs_source = state.inputs.raw_inputs if state.inputs.raw_inputs else state.inputs.model_dump()
        payload = ValidationHookPayloadDTO.model_validate(inputs_source)
        if not state.metadata or not state.metadata.target_locale:
            msg = "Execution state is missing mandatory 'target_locale' metadata."
            logger.error("[ValidationHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        target_locale = state.metadata.target_locale.lower()
    except ValidationError as e:
        msg = "Execution state inputs failed validation."
        logger.error("[ValidationHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
        raise AppException(
            message=msg,
            status_code=400,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        ) from e

    inputs_dict = payload.root

    if target_locale == "en":
        return HookResult(success=True, state_delta=HookDeltaDTO())

    # Heuristics: Extremely common, unambiguous English stop words.
    english_stops = {"the", "and", "is", "are", "was", "were", "this", "that", "these", "those", "from", "with"}

    # Target Generative text fields
    target_keys = ["evaluation_notes"]
    leakage_detected = False

    for key, value in inputs_dict.items():
        if not isinstance(value, str):
            continue

        if key in target_keys or key.endswith("_justification"):
            words = set(re.findall(r"\b[a-z]{2,}\b", value.lower()))
            overlap = words.intersection(english_stops)

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

    delta: dict[str, Any] = {}
    if leakage_detected:
        try:
            warnings_payload = SystemWarningsStateDTO.model_validate(inputs_source)
            existing_warnings = list(warnings_payload.system_warnings)
        except ValidationError as e:
            msg = "Invalid '_system_warnings' schema in state inputs."
            logger.error("[ValidationHook] %s: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
            ) from e

        new_warning = ValidationWarningDTO(
            type=f"{AppException.PROBLEM_BASE_URI}/language-mismatch",
            title="Output Language Mismatch",
            error_code=ErrorCodes.VALIDATION_FAILED.name,
            detail=f"Model neglected the '{target_locale}' localization mandate and leaked English.",
            meta={},
        )
        existing_warnings.append(new_warning)
        delta["_system_warnings"] = [w.model_dump(mode="json") for w in existing_warnings]

    return HookResult(success=True, state_delta=HookDeltaDTO(delta=delta))


@hook_registry.register(name="verify_anomaly")
def verify_anomaly(state: HookState | None, deps: HookDependencies) -> HookResult:
    """HOOK: verify_anomaly.

    Pre-scoring anomaly detection to catch Guttman logic failures.

    Args:
        state: Current frozen workflow state.
        deps: Injected hook runtime dependencies.

    Returns:
        Structured state delta container.
    """
    logger.debug("[ValidationHook] Running LLM Anomaly detection...")

    if not state:
        return HookResult(success=True, state_delta=HookDeltaDTO())

    inputs_source = state.inputs.raw_inputs if state.inputs.raw_inputs else state.inputs.model_dump()
    if not inputs_source:
        return HookResult(success=True, state_delta=HookDeltaDTO())

    anomaly_detected = False

    for block_id, result in inputs_source.items():
        if isinstance(result, list) and len(result) > 0:
            hits_by_level: dict[float, float] = {}
            total_by_level: dict[float, float] = {}

            for atom in result:
                try:
                    atom_dto = GuttmanAtomItemDTO.model_validate(atom)
                    level = atom_dto.score_level
                    current_hits = hits_by_level[level] if level in hits_by_level else 0.0
                    hits_by_level[level] = current_hits + (1.0 if atom_dto.hit else 0.0)
                    current_total = total_by_level[level] if level in total_by_level else 0.0
                    total_by_level[level] = current_total + 1.0
                except ValidationError:
                    continue

            if len(total_by_level) > 1:
                sorted_levels = sorted(total_by_level.keys())
                for i in range(len(sorted_levels)):
                    for j in range(i + 1, len(sorted_levels)):
                        L_low = sorted_levels[i]
                        L_high = sorted_levels[j]
                        hr_low = hits_by_level[L_low] / total_by_level[L_low] if total_by_level[L_low] > 0 else 0.0
                        hr_high = hits_by_level[L_high] / total_by_level[L_high] if total_by_level[L_high] > 0 else 0.0

                        if hr_low < hr_high - 0.4 or (hr_low == 0.0 and hr_high == 1.0):
                            logger.warning(
                                "[ValidationHook] Guttman logic anomaly detected in block %s: "
                                "L%s rate (%.2f) vs L%s rate (%.2f). Requesting LLM Self-Correction.",
                                block_id,
                                L_low,
                                hr_low,
                                L_high,
                                hr_high,
                            )
                            anomaly_detected = True
                            break
                    if anomaly_detected:
                        break

        if anomaly_detected:
            break

    if anomaly_detected:
        return HookResult(success=True, state_delta=HookDeltaDTO(delta={"llm_anomaly_retry_requested": True}))

    return HookResult(success=True, state_delta=HookDeltaDTO())
