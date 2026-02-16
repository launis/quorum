"""Validation hooks for structural integrity checks."""

import logging

from backend.exceptions import AppException, ErrorCodes
from backend.models.domain import ValidationResult
from backend.models.state import WorkflowState


logger = logging.getLogger(__name__)


def verify_structure(state: WorkflowState) -> WorkflowState:
    """HOOK: verify_structure.

    Pre-execution validation check to ensure inputs ('history_text', 'product_text', 'reflection_text')
    have sufficient content length for meaningful analysis.
    Adds warnings to 'aux_data.structural_warnings' if checks fail.

    Min Length: 100 chars.

    Args:
        state (WorkflowState): Current state.

    Returns:
        WorkflowState: Updated state with warnings if applicable.

    Raises:
        AppException: If structure check fails (Fail Fast).
    """
    logger.debug("[ValidationHook] Running structural inputs check...")

    # Minimum char limits
    MIN_CHARS = 100

    warnings = []

    if not state.context_variables:
        # Should be caught by earlier checks, but fail fast here if empty
        msg = "Context variables missing in validation hook."
        logger.error(f"[ValidationHook] {ErrorCodes.EMPTY_INPUT}: {msg}")
        raise AppException(
            message=msg,
            status_code=400,
            details={"error_code": ErrorCodes.EMPTY_INPUT}
        )

    inputs = state.context_variables.get("inputs", {})
    if not isinstance(inputs, dict):
        logger.warning(f"[ValidationHook] Inputs not a dict: {type(inputs)}. Defaulting to empty.")
        inputs = {}

    for key in ["history_text", "product_text", "reflection_text"]:
        text = str(inputs.get(key, "") or "")
        # Check actual content length (strip whitespace)
        if not text or len(text.strip()) < MIN_CHARS:
            warnings.append(
                f"Input '{key}' is too short ({len(text)} chars). Min required: {MIN_CHARS}."
            )

    try:
        # Create strict result object
        result = ValidationResult(
            is_valid=len(warnings) == 0,
            errors=warnings
        )
    except Exception as e:
        # Pydantic validation failure -> System Error
        error_code = ErrorCodes.INTERNAL_SERVER_ERROR
        logger.error(f"[ValidationHook] Failed to create ValidationResult: {e}")
        raise AppException(
            message=f"System Error: {e}",
            status_code=500,
            details={"error_code": error_code}
        ) from e

    # IMMUTABILITY FIX
    new_context = state.context_variables.copy()
    new_context["validation_result"] = result
    
    # REMOVED LEGACY "warnings" key in aux_data/context. Use validation_result.errors instead.

    if not result.is_valid:
        msg = f"Structural Validation Failed: {warnings}"
        logger.error(f"[ValidationHook] {msg}")
        
        # FAIL FAST: Pre-validation failure is a client error (Bad Request)
        raise AppException(
            message=msg,
            status_code=400,
            details={
                "error_code": ErrorCodes.VALIDATION_FAILED,
                "warnings": warnings
            }
        )
    else:
        logger.debug("[ValidationHook] Checks passed.")

    return state.model_copy(update={"context_variables": new_context})

