"""Security hooks for PII redaction and keyword banning."""

from __future__ import annotations

import logging

from fastapi import status

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes

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

    from pydantic import ValidationError

    from backend_v2.models.domain.security import SanitizationResultDTO, SecurityPayloadDTO

    try:
        payload = SecurityPayloadDTO.model_validate(state.inputs)
    except ValidationError as e:
        msg = f"Strict Fail-Fast Enforced: Security payload failed validation: {e}"
        logger.error("[SecurityHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        ) from e

    for field, val in payload.root.items():
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

    try:
        dto = SanitizationResultDTO(
            sanitized_inputs=sanitized_inputs,
            security_status="DATA_CHECKED_AND_SECURED",
        )
        result = dto.model_dump(mode="json")
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
