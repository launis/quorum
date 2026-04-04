"""Security hooks for PII redaction and keyword banning."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import status

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes, SecurityViolationError

logger = logging.getLogger(__name__)

from backend_v2.core.security import sanitize_text

# --- WORKFLOW STATE WRAPPERS (for HOOK_MAPPING compatibility) ---


@hook_registry.register(name="sanitize_text")
def sanitize_text_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Workflow Data wrapper for sanitize_text.

    Sanitizes all text inputs and stores results in context_variables as SanitizationResult.
    """
    logger.debug("[SecurityHook] Running sanitize_text_hook...")

    if not state:
        logger.warning("[SecurityHook] Empty initial state. Skipping.")
        return HookResult(success=True, state_delta={})

    sanitized_inputs: dict[str, str] = {}
    threats_summary: list[str] = []

    inputs = state.inputs

    if not inputs or not isinstance(inputs, dict):
        error_code = ErrorCodes.EMPTY_INPUT if inputs is None else ErrorCodes.INVALID_OUTPUT_SCHEMA
        msg = f"Missing or invalid 'inputs' in data. Expected dict. Got type: {type(inputs)}, Value: {inputs}"
        status_code = status.HTTP_400_BAD_REQUEST if inputs is None else status.HTTP_500_INTERNAL_SERVER_ERROR
        logger.error("[SecurityHook] %s: %s", error_code.name, msg)
        raise AppException(
            message=msg,
            status_code=status_code,
            details={"error_code": error_code},
        )

    for field, val in inputs.items():
        if not val:
            continue

        original = str(val)
        if original.strip():
            try:
                sanitized, threats = sanitize_text(original)
                sanitized_inputs[field] = sanitized
                if threats:
                    threats_summary.extend(threats)
            except Exception as e:
                # Fail Fast: If sanitization logic breaks, we cannot proceed safely
                error_code = ErrorCodes.SECURITY_SCAN_FAILED
                logger.warning(
                    "[SecurityHook] Sanitization failed for field '%s': %s",
                    field,
                    e,
                    exc_info=True,
                )
                raise AppException(
                    message=f"Sanitization failed for field '{field}': {e}",
                    status_code=500,
                    details={"error_code": error_code},
                ) from e
        else:
            sanitized_inputs[field] = original

    # Create pure dict result
    try:
        result: dict[str, Any] = {
            "sanitized_inputs": sanitized_inputs,
            "security_status": "DATA_CHECKED_AND_SECURED",
        }
    except Exception as e:
        # Configuration/System Error
        error_code = ErrorCodes.SECURITY_CONFIG_ERROR
        logger.error("[SecurityHook] %s: %s", error_code.name, e)
        raise AppException(
            message=f"Failed to create SanitizationResult: {e}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code},
        ) from e

    if threats_summary:
        logger.warning("[SecurityHook] PII detected and redacted: %s", threats_summary)
    else:
        logger.debug("[SecurityHook] No PII detected.")

    return HookResult(success=True, state_delta={"sanitization_result": result})


