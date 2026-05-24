import logging

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)


@hook_registry.register(name="dlq_strict_mode_guard")
def dlq_strict_mode_guard_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Pre-scoring hook to guard against excessive DLQ failures.

    If dlq_count / total_atoms > 0.10, immediately raises AppException to fail-fast.
    """
    logger.info("[DLQGuard] Inspecting DLQ ratios...")

    if not state or not isinstance(state.inputs, dict):
        logger.info("[DLQGuard] State inputs missing or not a dictionary. Bypassing guard.")
        return HookResult(success=True, state_delta={})

    content_payload = state.inputs
    evaluations = content_payload.get("evaluations")

    if not evaluations or not isinstance(evaluations, list):
        logger.info("[DLQGuard] No evaluations found or empty. Bypassing guard.")
        return HookResult(success=True, state_delta={})

    dlq_count = 0
    total_atoms = len(evaluations)

    for ev in evaluations:
        status = ev.get("status") if isinstance(ev, dict) else getattr(ev, "status", None)
        if status == "DLQ":
            dlq_count += 1

    if total_atoms > 0:
        ratio = dlq_count / total_atoms
        if ratio > 0.10:
            msg = f"Strict Fail-Fast: DLQ ratio {ratio:.2%} exceeded the 10.00% absolute limit."
            logger.error("[DLQGuard] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "dlq_ratio": ratio},
            )

    logger.info(
        "[DLQGuard] DLQ validation passed. Ratio: %.2f%% (%d/%d atoms)",
        (dlq_count / total_atoms * 100) if total_atoms > 0 else 0.0,
        dlq_count,
        total_atoms,
    )
    return HookResult(success=True, state_delta={})
