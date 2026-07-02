"""System Metadata Hook for V2 Execution Steps."""

import logging
from datetime import datetime, timezone

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.metadata import MetadataHookPayloadDTO, MetadataHookResultDTO, StepMetadataDTO

logger = logging.getLogger(__name__)


@hook_registry.register(name="inject_step_metadata")
def inject_step_metadata(state: HookState, deps: HookDependencies) -> HookResult:
    """Computes execution metadata including timestamps and initiator information.

    This fulfills the V2 requirement for providing 'kello' (timestamp) and 'user'
    information dynamically to the output dictionary without requiring LLM generation.

    Args:
        state: The current execution state of the hook.
        deps: Dependencies required for execution.

    Returns:
        A HookResult containing the computed step metadata in the state_delta.

    Raises:
        AppException: If required state fields or global context variables are missing or invalid.
    """
    if not state:
        return HookResult(success=True, state_delta={})

    if not state.execution_id:
        error_code = ErrorCodes.VALIDATION_FAILED
        msg = "state.execution_id is strictly required for metadata injection."
        logger.error("[MetadataHook] %s: %s", error_code.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": error_code.value})

    if not state.step_id:
        error_code = ErrorCodes.VALIDATION_FAILED
        msg = "state.step_id is strictly required for metadata injection."
        logger.error("[MetadataHook] %s: %s", error_code.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": error_code.value})

    if not state.workflow_id:
        error_code = ErrorCodes.VALIDATION_FAILED
        msg = "state.workflow_id is strictly required for metadata injection."
        logger.error("[MetadataHook] %s: %s", error_code.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": error_code.value})

    if state.global_context_vars is None:
        error_code = ErrorCodes.VALIDATION_FAILED
        msg = "state.global_context_vars is strictly required but missing."
        logger.error("[MetadataHook] %s: %s", error_code.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": error_code.value})

    execution_id = state.execution_id
    step_id = state.step_id
    workflow_id = state.workflow_id

    # Strict Validation via DTO inflation
    try:
        payload = MetadataHookPayloadDTO.model_validate(state.global_context_vars)
    except Exception as e:
        error_code = ErrorCodes.INVALID_OUTPUT_SCHEMA
        msg = f"Failed to strictly validate global context for metadata: {e}"
        logger.error("[MetadataHook] %s: %s", error_code.name, msg)
        raise AppException(
            message=msg,
            status_code=400,
            details={"error_code": error_code.value},
        ) from e

    unix_time = int(datetime.now(timezone.utc).timestamp())

    metadata = StepMetadataDTO(
        execution_id=execution_id,
        workflow_id=workflow_id,
        step_id=step_id,
        initiator_id=payload.sys_initiator_id,
        timestamp_isot=datetime.now(timezone.utc).isoformat(),
        unix_time=unix_time,
        v2_engine=True,
    )

    result_dto = MetadataHookResultDTO(step_metadata=metadata)

    logger.debug("[MetadataHook] Injected metadata for step %s", step_id)

    return HookResult(
        success=True,
        state_delta={
            "step_metadata": result_dto.step_metadata.model_dump(mode="json"),
            # Ensure we always provide a deterministic audit signature
            "_audit_signature": f"{step_id}:{execution_id}:{unix_time}",
        },
    )
