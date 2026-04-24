"""Validation hooks for structural integrity checks."""

import logging

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry

logger = logging.getLogger(__name__)


@hook_registry.register(name="hydrate_global_inputs")
def hydrate_global_inputs_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Workflow Data wrapper for hydrate_global_inputs.

    Extracts the parsed strings from the InputProcessorAgent's output
    and merges them seamlessly into the global `inputs` context variable.

    Args:
        data (dict): Current data.

    Returns:
        dict: Updated data with hydrated `inputs`.
    """
    logger.debug("[HydrationHook] Running global inputs hydration...")

    if not state:
        return HookResult(success=True, state_delta={})

    from backend_v2.models.domain.hydration import HydrationInputSourceDTO
    from backend_v2.utils.pydantic_utils import inflate

    hydration_source: HydrationInputSourceDTO | None = None

    for _key, result in state.global_context_vars.items():
        try:
            # Strict inflation attempts to parse the result into the DTO sieve
            candidate = inflate(result, HydrationInputSourceDTO)
            if candidate and candidate.is_valid_source():
                hydration_source = candidate
                break
        except Exception:
            # Ignore unrelated state payloads
            continue

    if not hydration_source:
        logger.warning("[HydrationHook] No InputProcessorOutput found in data. Skipping hydration.")
        return HookResult(success=True, state_delta={})

    # HookState strictly enforces inputs as dict[str, Any], eliminating legacy fallback checks
    inputs = state.inputs.copy()

    # Extract updates safely via Pydantic model methods
    updates = hydration_source.extract_hydrated_inputs()

    if not updates:
        logger.debug("[HydrationHook] Processor output contained no text fields to hydrate.")
        return HookResult(success=True, state_delta={})

    logger.info(f"[HydrationHook] Hydrating global inputs with {list(updates.keys())}")

    inputs.update(updates)

    return HookResult(success=True, state_delta={"inputs": inputs})
