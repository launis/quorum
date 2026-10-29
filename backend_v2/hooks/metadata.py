"""System Metadata Hook for V2 Execution Steps."""

import logging
from datetime import UTC, datetime

from fastapi import status

from backend_v2.core.hook_registry import (
    HookDeltaDTO,
    HookDependencies,
    HookResult,
    HookState,
    hook_registry,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.metadata import MetadataHookResultDTO, StepMetadataDTO

logger = logging.getLogger(__name__)

__all__ = ["inject_step_metadata"]


@hook_registry.register(name="inject_step_metadata")
def inject_step_metadata(state: HookState | None, deps: HookDependencies) -> HookResult:
    """Compute execution metadata including timestamps and initiator information.

    Provides dynamic timestamp and user initiator metadata to the execution state
    delta without requiring LLM generation.

    Args:
        state: The current execution state of the hook.
        deps: Dependencies required for execution.

    Returns:
        A HookResult containing the computed step metadata in the state_delta.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if required state fields or
            global context variables are missing or invalid.
    """
    if not state:
        return HookResult(success=True, state_delta=HookDeltaDTO())

    if not state.execution_id:
        msg = "state.execution_id is strictly required for metadata injection."
        logger.error("[MetadataHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    if not state.step_id:
        msg = "state.step_id is strictly required for metadata injection."
        logger.error("[MetadataHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    if not state.workflow_id:
        msg = "state.workflow_id is strictly required for metadata injection."
        logger.error("[MetadataHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    if state.global_context_vars is None:
        msg = "state.global_context_vars is strictly required but missing."
        logger.error("[MetadataHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    execution_id = state.execution_id
    step_id = state.step_id
    workflow_id = state.workflow_id

    now_utc = datetime.now(UTC)
    unix_time = int(now_utc.timestamp())
    initiator_id = "system"
    if state.global_context_vars.initiator_id:
        initiator_id = state.global_context_vars.initiator_id

    metadata = StepMetadataDTO(
        execution_id=execution_id,
        workflow_id=workflow_id,
        step_id=step_id,
        initiator_id=initiator_id,
        timestamp_isot=now_utc.isoformat(),
        unix_time=unix_time,
        v2_engine=True,
        task_blueprint=state.task_blueprint,
    )

    result_dto = MetadataHookResultDTO(
        step_metadata=metadata,
        audit_signature=f"{step_id}:{execution_id}:{unix_time}",
    )

    logger.debug("[MetadataHook] Injected metadata for step %s", step_id)

    return HookResult(
        success=True,
        state_delta=HookDeltaDTO(delta=result_dto),
    )
