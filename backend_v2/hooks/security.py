"""Security hooks for PII redaction and keyword banning.

Provides security hooks for sanitizing incoming inputs by removing personally identifiable
information (PII) and preventing keyword injections before passing data to models or external systems.
"""

from __future__ import annotations

import logging

from pydantic import ValidationError

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.core.security import sanitize_text
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.security import SanitizationResultDTO, SecurityPayloadDTO

logger = logging.getLogger(__name__)


@hook_registry.register(name="sanitize_text")
def sanitize_text_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Workflow Data wrapper for sanitize_text.

    Sanitizes all text inputs and stores results in context_variables as SanitizationResult.

    Args:
        state: The current HookState representing the execution state.
        deps: Hook dependencies injected at runtime.

    Returns:
        The HookResult containing success status and the updated state delta.

    Raises:
        AppException: Raised with VALIDATION_FAILED when state is missing or the incoming security
            payload fails validation. Raised with SECURITY_SCAN_FAILED if text sanitization fails.
            Raised with SECURITY_CONFIG_ERROR if building the final SanitizationResultDTO fails.
    """
    logger.debug("[SecurityHook] Running sanitize_text_hook...")

    if not state:
        msg = "Strict Fail-Fast Enforced: Missing HookState in sanitize_text_hook."
        logger.error("[SecurityHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    sanitized_inputs: dict[str, str] = {}
    threats_summary: list[str] = []

    try:
        payload = SecurityPayloadDTO.model_validate(state.inputs)
    except ValidationError as e:
        msg = f"Strict Fail-Fast Enforced: Security payload failed validation: {e}"
        logger.error("[SecurityHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
        raise AppException(
            message=msg,
            status_code=400,
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
                msg = f"Sanitization failed for field '{field}': {e}"
                logger.error("[SecurityHook] %s: %s", ErrorCodes.SECURITY_SCAN_FAILED.name, msg, exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.SECURITY_SCAN_FAILED.value},
                ) from e
        else:
            sanitized_inputs[field] = original

    threat_detected = bool(threats_summary)
    try:
        dto = SanitizationResultDTO(
            sanitized_inputs=sanitized_inputs,
            security_status="DATA_CHECKED_AND_SECURED",
            threat_detected=threat_detected,
        )
        result = dto.model_dump(mode="json")
    except Exception as e:
        msg = f"Failed to create SanitizationResult: {e}"
        logger.error("[SecurityHook] %s: %s", ErrorCodes.SECURITY_CONFIG_ERROR.name, msg, exc_info=True)
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.SECURITY_CONFIG_ERROR.value},
        ) from e

    if threats_summary:
        logger.warning("[SecurityHook] PII detected and redacted. Threat count: %d", len(threats_summary))
    else:
        logger.debug("[SecurityHook] No PII detected.")

    return HookResult(success=True, state_delta={"sanitization_result": result})
