"""Dead Letter Queue (DLQ) guard hook for strict validation."""

import logging
from typing import Any

from fastapi import status
from pydantic import BaseModel, ConfigDict

from backend_v2.core.hook_registry import (
    HookDeltaDTO,
    HookDependencies,
    HookResult,
    HookState,
    hook_registry,
)
from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)


class DLQAtomSchema(BaseModel):
    """Strict schema for DLQ validation."""

    model_config = ConfigDict(strict=True, extra="forbid")

    atom_id: str | None = None
    status: str | None = None


@hook_registry.register(name="dlq_strict_mode_guard")
def dlq_strict_mode_guard_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Pre-scoring hook to guard against excessive DLQ failures.

    Checks DLQ ratio against the absolute allowed maximum safety threshold.
    If dlq_count / total_atoms > 0.10, immediately raises AppException to fail-fast.

    Args:
        state: The frozen execution HookState context.
        deps: Injected system service dependencies.

    Returns:
        HookResult: Successful execution wrapper with immutable state delta.

    Raises:
        AppException: If DLQ threshold is breached or data is malformed.
    """
    logger.info("[DLQGuard] Inspecting DLQ ratios...")

    if not state.inputs:
        logger.info("[DLQGuard] State inputs missing. Bypassing guard.")
        return HookResult(success=True, state_delta=HookDeltaDTO())

    content_payload: dict[str, Any] = state.inputs.raw_inputs
    if "evaluations" not in content_payload:
        logger.info("[DLQGuard] No evaluations found or empty. Bypassing guard.")
        return HookResult(success=True, state_delta=HookDeltaDTO())

    evaluations = content_payload["evaluations"]
    if not isinstance(evaluations, list):
        msg = "Strict Fail-Fast: 'evaluations' must be a list."
        logger.error("[DLQGuard] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    dlq_count: int = 0
    total_atoms: int = len(evaluations)

    for ev_raw in evaluations:
        try:
            ev = DLQAtomSchema.model_validate(ev_raw)
            if ev.status == "DLQ":
                dlq_count += 1
        except Exception as e:
            msg = f"Strict Fail-Fast: Evaluation atom malformed: {e}"
            logger.error("[DLQGuard] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e

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
    return HookResult(success=True, state_delta=HookDeltaDTO())
