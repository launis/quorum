"""Validation hooks for structural integrity checks."""

import logging
from typing import Any

from fastapi import status

from backend_v2.core.hook_registry import hook_registry
from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)


@hook_registry.register(name="verify_structure")
def verify_structure(data: dict[str, Any]) -> dict[str, Any]:
    """HOOK: verify_structure.

    Pre-execution validation check to ensure inputs ('history_text', 'product_text', 'reflection_text')
    have sufficient content length for meaningful analysis.
    Adds warnings to 'structural_warnings' if checks fail.

    Min Length: 100 chars.

    Args:
        data (dict): Current workflow data containing 'inputs'.

    Returns:
        dict: Updated data with warnings if applicable.

    Raises:
        AppException: If structure check fails (Fail Fast).
    """
    logger.debug("[ValidationHook] Running structural inputs check...")

    # Minimum char limits
    MIN_CHARS = 100

    warnings = []

    if not data:
        msg = "Context variables missing in validation hook."
        logger.error(f"[ValidationHook] {ErrorCodes.EMPTY_INPUT.name}: {msg}")
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.EMPTY_INPUT},
        )

    inputs = data.get("inputs")

    if not inputs or not isinstance(inputs, dict):
        error_code = ErrorCodes.EMPTY_INPUT if inputs is None else ErrorCodes.INVALID_OUTPUT_SCHEMA
        msg = "Missing or invalid 'inputs' in data. Expected dict."
        status_code = status.HTTP_400_BAD_REQUEST if inputs is None else status.HTTP_500_INTERNAL_SERVER_ERROR
        logger.error(f"[ValidationHook] {error_code.name}: {msg}")
        raise AppException(
            message=msg,
            status_code=status_code,
            details={"error_code": error_code},
        )

    # Generic check for all provided string inputs
    for key, val in inputs.items():
        if not val or not str(val).strip():
            # If the value is present but empty, we still warn or continue
            continue
            
        text = str(val).strip()
        if len(text) < MIN_CHARS:
            warnings.append(f"Input '{key}' is too short ({len(text)} chars). Min required: {MIN_CHARS}.")

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

    return {"validation_result": result}
