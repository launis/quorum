"""Validation hooks for structural integrity, output language, and Guttman anomaly checks."""

from __future__ import annotations

import logging
import re
from collections.abc import Sequence

from fastapi import status
from pydantic import ValidationError

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
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
from backend_v2.models.dtos.hook_delta import AnomalyRetryResultDTO

logger = logging.getLogger(__name__)

__all__ = [
    "verify_anomaly",
    "verify_output_language",
    "verify_structure",
]

_MIN_STRUCTURAL_CHARS: int = 10
_IGNORED_STRUCTURAL_KEYS: frozenset[str] = frozenset({"language", "locale", "target_locale"})
_ENGLISH_STOP_WORDS: frozenset[str] = frozenset(
    {"the", "and", "is", "are", "was", "were", "this", "that", "these", "those", "from", "with"}
)
_ENGLISH_STOP_WORD_THRESHOLD: int = 3
_GUTTMAN_INVERSION_MARGIN: float = 0.4


def _extract_inputs_source(state: HookState) -> object:
    """Extract raw inputs dictionary or model dump from hook execution state.

    Args:
        state: Current frozen workflow execution state.

    Returns:
        Raw inputs mapping or dumped model dictionary for validation.
    """
    return state.inputs.raw_inputs if state.inputs.raw_inputs is not None else state.inputs.model_dump()


def _collect_structural_warnings(payload: ValidationHookPayloadDTO) -> list[ValidationWarningDTO]:
    """Flatten nested payload containers and validate minimum character length across fields.

    Args:
        payload: Validated hook payload DTO.

    Returns:
        List of structural validation warnings discovered across fields.
    """
    inputs_dict = payload.root
    fields_to_validate = {}

    if "raw_inputs" in inputs_dict:
        raw_sub = inputs_dict["raw_inputs"]
        if raw_sub is not None:
            fields_to_validate.update(ValidationHookPayloadDTO.model_validate(raw_sub).root)

    if "inputs" in inputs_dict:
        inputs_sub = inputs_dict["inputs"]
        if inputs_sub is not None:
            fields_to_validate.update(ValidationHookPayloadDTO.model_validate(inputs_sub).root)

    if not fields_to_validate and not (
        "steps" in inputs_dict or "raw_inputs" in inputs_dict or "inputs" in inputs_dict
    ):
        fields_to_validate = inputs_dict

    warnings: list[ValidationWarningDTO] = []
    valid_content_keys = 0

    for key, val in fields_to_validate.items():
        key_lower = key.lower()
        if (
            key_lower in _IGNORED_STRUCTURAL_KEYS
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
        if len(text) < _MIN_STRUCTURAL_CHARS:
            warnings.append(
                ValidationWarningDTO(
                    type=f"{AppException.PROBLEM_BASE_URI}/input-too-short",
                    title="Analysis Input Too Short",
                    error_code=ErrorCodes.VALIDATION_FAILED.name,
                    detail=f"Field '{key}' has length {len(text)}, required {_MIN_STRUCTURAL_CHARS}.",
                    meta={"key": key, "length": len(text), "min_chars": _MIN_STRUCTURAL_CHARS},
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

    return warnings


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
        AppException: INTERNAL_SERVER_ERROR if validation result construction fails.
    """
    logger.debug("[ValidationHook] Running structural inputs check...")

    if not state:
        msg = "State missing in validation hook."
        logger.error("[ValidationHook] %s: %s", ErrorCodes.EMPTY_INPUT.name, msg, exc_info=True)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.EMPTY_INPUT.value},
        )

    try:
        payload_source = _extract_inputs_source(state)
        payload = ValidationHookPayloadDTO.model_validate(payload_source)
    except ValidationError as e:
        msg = "Missing or invalid 'inputs' in state. Expected dict."
        logger.error("[ValidationHook] %s: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, msg, exc_info=True)
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        ) from e

    warnings = _collect_structural_warnings(payload)

    try:
        result_dto = ValidationResultDTO(is_valid=len(warnings) == 0, errors=warnings)
    except ValidationError as e:
        logger.error("[ValidationHook] Failed to create ValidationResult: %s", e, exc_info=True)
        raise AppException(
            message=f"System Error: {e}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        ) from e

    if not result_dto.is_valid:
        msg = f"Structural Validation Failed: {[w.model_dump(mode='json') for w in warnings]}"
        logger.error("[ValidationHook] %s", msg, exc_info=True)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={
                "error_code": ErrorCodes.VALIDATION_FAILED.value,
                "warnings": [w.model_dump(mode="json") for w in warnings],
            },
        )

    logger.debug("[ValidationHook] Checks passed.")
    return HookResult(
        success=True,
        state_delta=HookDeltaDTO(delta=result_dto),
    )


def _resolve_target_locale(state: HookState, payload: ValidationHookPayloadDTO) -> str | None:
    """Resolve target locale from state inputs, payload, or global context variables.

    Args:
        state: Current frozen workflow execution state.
        payload: Validated validation hook payload DTO.

    Returns:
        Target locale string if resolved, otherwise None.
    """
    if isinstance(state.inputs, ExecutionInputsDTO) and state.inputs.target_locale:
        return state.inputs.target_locale
    if "target_locale" in payload.root and payload.root["target_locale"]:
        return str(payload.root["target_locale"])
    if "language" in payload.root and payload.root["language"]:
        return str(payload.root["language"])
    if state.global_context_vars and state.global_context_vars.target_locale:
        return state.global_context_vars.target_locale
    if state.global_context_vars and state.global_context_vars.language:
        return state.global_context_vars.language
    return None


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
        inputs_source = _extract_inputs_source(state)
        payload = ValidationHookPayloadDTO.model_validate(inputs_source)
        target_locale = _resolve_target_locale(state, payload)
        if not target_locale:
            msg = "Execution state is missing mandatory 'target_locale'."
            logger.error("[ValidationHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        target_locale = target_locale.lower()
    except ValidationError as e:
        msg = "Execution state inputs failed validation."
        logger.error("[ValidationHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        ) from e

    if target_locale == "en":
        return HookResult(success=True, state_delta=HookDeltaDTO())

    target_keys = {"evaluation_notes"}
    leakage_detected = False

    for key, value in payload.root.items():
        if not isinstance(value, str):
            continue

        if key in target_keys or key.endswith("_justification"):
            words = set(re.findall(r"\b[a-z]{2,}\b", value.lower()))
            overlap = words.intersection(_ENGLISH_STOP_WORDS)

            if len(overlap) >= _ENGLISH_STOP_WORD_THRESHOLD:
                leakage_detected = True
                logger.warning(
                    "[ValidationHook] Language mismatch detected in field '%s'. "
                    "Target locale was '%s' but detected %d English stop words.",
                    key,
                    target_locale,
                    len(overlap),
                )

    if leakage_detected:
        existing_warnings: list[ValidationWarningDTO] = []
        if "_system_warnings" in payload.root:
            val = payload.root["_system_warnings"]
            if val is not None:
                try:
                    warnings_payload = SystemWarningsStateDTO.model_validate({"_system_warnings": val})
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
        return HookResult(
            success=True, state_delta=HookDeltaDTO(delta=ValidationResultDTO(is_valid=True, errors=existing_warnings))
        )

    return HookResult(success=True, state_delta=HookDeltaDTO())


def _evaluate_block_guttman_anomaly(block_id: str, atoms: Sequence[object]) -> bool:
    """Evaluate a single block's atom list for Guttman hit-rate inversion.

    Args:
        block_id: Identifier of the evaluated block.
        atoms: Non-empty sequence of raw or hydrated atom items.

    Returns:
        True if a Guttman logic inversion is detected, otherwise False.

    Raises:
        AppException: VALIDATION_FAILED if an atom item fails schema validation.
    """
    hits_by_level: dict[float, float] = {}
    total_by_level: dict[float, float] = {}

    for atom in atoms:
        try:
            atom_dto = GuttmanAtomItemDTO.model_validate(atom)
        except ValidationError as e:
            msg = f"Malformed atom payload in block '{block_id}': {e}"
            logger.error("[ValidationHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e

        level = atom_dto.score_level
        if level not in hits_by_level:
            hits_by_level[level] = 0.0
            total_by_level[level] = 0.0
        if atom_dto.hit:
            hits_by_level[level] += 1.0
        total_by_level[level] += 1.0

    if len(total_by_level) <= 1:
        return False

    sorted_levels = sorted(total_by_level.keys())
    for i in range(len(sorted_levels)):
        for j in range(i + 1, len(sorted_levels)):
            level_low = sorted_levels[i]
            level_high = sorted_levels[j]
            hr_low = hits_by_level[level_low] / total_by_level[level_low]
            hr_high = hits_by_level[level_high] / total_by_level[level_high]

            if hr_low < hr_high - _GUTTMAN_INVERSION_MARGIN or (hr_low == 0.0 and hr_high == 1.0):
                logger.warning(
                    "[ValidationHook] Guttman logic anomaly detected in block %s: "
                    "L%s rate (%.2f) vs L%s rate (%.2f). Requesting LLM Self-Correction.",
                    block_id,
                    level_low,
                    hr_low,
                    level_high,
                    hr_high,
                )
                return True

    return False


@hook_registry.register(name="verify_anomaly")
def verify_anomaly(state: HookState | None, deps: HookDependencies) -> HookResult:
    """HOOK: verify_anomaly.

    Pre-scoring anomaly detection to catch Guttman logic failures.

    Args:
        state: Current frozen workflow state.
        deps: Injected hook runtime dependencies.

    Returns:
        Structured state delta container.

    Raises:
        AppException: VALIDATION_FAILED if atom payload is malformed.
    """
    logger.debug("[ValidationHook] Running LLM Anomaly detection...")

    if not state:
        return HookResult(success=True, state_delta=HookDeltaDTO())

    inputs_source = state.inputs.raw_inputs if state.inputs.raw_inputs is not None else state.inputs.model_dump()
    if not inputs_source:
        return HookResult(success=True, state_delta=HookDeltaDTO())

    for block_id, result in inputs_source.items():
        if isinstance(result, list) and len(result) > 0:
            if _evaluate_block_guttman_anomaly(block_id, result):
                return HookResult(
                    success=True,
                    state_delta=HookDeltaDTO(delta=AnomalyRetryResultDTO(llm_anomaly_retry_requested=True)),
                )

    return HookResult(success=True, state_delta=HookDeltaDTO())
