"""Validation hooks for structural integrity checks."""

import logging

from pydantic import ValidationError

from backend_v2.core.hook_registry import (
    HookDeltaDTO,
    HookDependencies,
    HookResult,
    HookState,
    hook_registry,
)
from backend_v2.models.domain.hydration import HydrationInputSourceDTO

logger = logging.getLogger(__name__)


@hook_registry.register(name="hydrate_global_inputs")
def hydrate_global_inputs_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Workflow Data wrapper for hydrate_global_inputs.

    Extracts the parsed strings from the InputProcessorAgent's output
    and merges them seamlessly into the global `inputs` context variable.

    Args:
        state: Current hook execution state.
        deps: Injected dependencies for the hook.

    Returns:
        Result containing the updated state delta with hydrated inputs.
    """
    logger.debug("[HydrationHook] Running global inputs hydration...")

    if not state:
        return HookResult(success=True, state_delta=HookDeltaDTO())

    hydration_source: HydrationInputSourceDTO | None = None

    gvars = state.global_context_vars.vars

    for _key, result in gvars.items():
        try:
            # Strict validation attempts to parse the result into the DTO sieve directly
            candidate = HydrationInputSourceDTO.model_validate(result)
            if candidate.is_valid_source():
                hydration_source = candidate
                break
        except ValidationError:
            # Ignore unrelated state payloads
            continue

    if not hydration_source:
        logger.warning("[HydrationHook] No InputProcessorOutput found in data. Skipping hydration.")
        return HookResult(success=True, state_delta=HookDeltaDTO())

    raw_inputs = state.inputs.raw_inputs.copy()

    # Extract updates safely via Pydantic model methods
    updates = hydration_source.extract_hydrated_inputs()

    if not updates:
        logger.debug("[HydrationHook] Processor output contained no text fields to hydrate.")
        return HookResult(success=True, state_delta=HookDeltaDTO())

    logger.info("[HydrationHook] Hydrating global inputs with %s", list(updates.keys()))

    raw_inputs.update(updates)

    return HookResult(success=True, state_delta=HookDeltaDTO(delta={"inputs": raw_inputs}))
