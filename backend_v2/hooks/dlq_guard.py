import logging
from typing import Any

from fastapi import status

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)


@hook_registry.register(name="dlq_strict_mode_guard")
def dlq_strict_mode_guard_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Pre-scoring hook to guard against excessive DLQ failures.

    Checks DLQ ratio against the absolute allowed maximum safety threshold.
    If dlq_count / total_atoms > 0.10, immediately raises AppException to fail-fast.

    Args:
        state: The frozen execution HookState context.
        deps: Injected system service dependencies.

    Returns:
        Successful execution wrapper with immutable state delta.

    Raises:
        AppException: If DLQ threshold is breached.
    """
    logger.info("[DLQGuard] Inspecting DLQ ratios...")

    # Strict type checks to prevent dict mapping bleed
    if not state or not hasattr(state, "inputs") or not isinstance(state.inputs, dict):
        logger.info("[DLQGuard] State inputs missing or not a dictionary. Bypassing guard.")
        return HookResult(success=True, state_delta={})

    content_payload: dict[str, Any] = state.inputs
    if "evaluations" not in content_payload:
        logger.info("[DLQGuard] No evaluations found or empty. Bypassing guard.")
        return HookResult(success=True, state_delta={})

    evaluations = content_payload["evaluations"]
    if not isinstance(evaluations, list):
        logger.info("[DLQGuard] Evaluations not format-compliant. Bypassing guard.")
        return HookResult(success=True, state_delta={})

    dlq_count: int = 0
    total_atoms: int = len(evaluations)

    for ev in evaluations:
        status_val: Any | None = None
        if isinstance(ev, dict):
            status_val = ev.get("status")
        else:
            status_val = getattr(ev, "status", None)
        if status_val == "DLQ":
            dlq_count += 1

    if total_atoms > 0:
        ratio: float = dlq_count / total_atoms
        if ratio > 0.10:
            message: str = "Strict Fail-Fast: DLQ ratio " + f"{ratio:.2%}" + " exceeded the 10.00% absolute limit."
            logger.error("[DLQGuard] %s: %s", ErrorCodes.VALIDATION_FAILED.name, message, exc_info=True)
            raise AppException(
                message=message,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "dlq_ratio": ratio},
            )

    passed_ratio: float = (dlq_count / total_atoms * 100) if total_atoms > 0 else 0.0
    logger.info("[DLQGuard] DLQ validation passed. Ratio: %.2f%% (%d/%d atoms)", passed_ratio, dlq_count, total_atoms)
    return HookResult(success=True, state_delta={})
