"""Global inputs hydration hook for workflow execution."""

from __future__ import annotations

import logging

from fastapi import status

from backend_v2.core.hook_registry import (
    HookDeltaDTO,
    HookDependencies,
    HookResult,
    HookState,
    hook_registry,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.hydration import HydrationInputSourceDTO
from backend_v2.models.dtos.hook_delta import ExecutionInputsDTO

logger = logging.getLogger(__name__)

__all__ = ["hydrate_global_inputs_hook"]


@hook_registry.register(name="hydrate_global_inputs")
def hydrate_global_inputs_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Workflow data wrapper for hydrate_global_inputs.

    Extracts the parsed strings from the InputProcessorAgent's output
    and merges them seamlessly into the global `inputs` context variable.

    Args:
        state: Current hook execution state.
        deps: Injected dependencies for the hook.

    Returns:
        Result containing the updated state delta with hydrated inputs.

    Raises:
        AppException: If execution_id, workflow_id, or any hydrated input key is empty
            or whitespace (ErrorCodes.VALIDATION_FAILED).
    """
    logger.debug("[HydrationHook] Running global inputs hydration...")

    if not state.execution_id.strip() or not state.workflow_id.strip():
        msg = "Missing mandatory execution_id or workflow_id in HookState for global inputs hydration."
        logger.error(
            "[HydrationHook] %s: %s",
            ErrorCodes.VALIDATION_FAILED.name,
            msg,
            exc_info=True,
        )
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    hydration_source: HydrationInputSourceDTO | None = state.global_context_vars.hydration_results

    if not hydration_source or not hydration_source.is_valid_source():
        logger.warning("[HydrationHook] No InputProcessorOutput found in data. Skipping hydration.")
        return HookResult(success=True, state_delta=HookDeltaDTO())

    # Extract updates safely via Pydantic model methods
    updates = hydration_source.extract_hydrated_inputs()

    if not updates:
        logger.debug("[HydrationHook] Processor output contained no text fields to hydrate.")
        return HookResult(success=True, state_delta=HookDeltaDTO())

    for key in updates:
        if not key.strip():
            msg = "Hydrated input key cannot be empty or whitespace."
            logger.error(
                "[HydrationHook] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

    logger.info("[HydrationHook] Hydrating global inputs with %s", list(updates.keys()))

    raw_inputs = dict(state.inputs.raw_inputs)
    raw_inputs.update(updates)

    updated_inputs = ExecutionInputsDTO(
        raw_inputs=raw_inputs,
        dynamic_inputs=state.inputs.dynamic_inputs,
        user_role=state.inputs.user_role,
        target_locale=state.inputs.target_locale,
    )

    return HookResult(success=True, state_delta=HookDeltaDTO(delta=updated_inputs))
