"""Validation hooks for structural integrity checks."""

import logging
from typing import Any

from backend_v2.core.hook_registry import hook_registry

logger = logging.getLogger(__name__)


@hook_registry.register(name="hydrate_global_inputs")
def hydrate_global_inputs_hook(data: dict[str, Any]) -> dict[str, Any]:
    """Workflow Data wrapper for hydrate_global_inputs.

    Extracts the parsed strings from the InputProcessorAgent's output
    and merges them seamlessly into the global `inputs` context variable.

    Args:
        data (dict): Current data.

    Returns:
        dict: Updated data with hydrated `inputs`.
    """
    logger.debug("[HydrationHook] Running global inputs hydration...")

    if not data:
        return {}

    processor_output: dict[str, Any] | None = None
    for _key, result in data.items():
        if isinstance(result, dict):
            if result.get("agent_type") == "InputProcessorAgent" or "inputs" in result:
                processor_output = result
                break

    if not processor_output:
        logger.warning("[HydrationHook] No InputProcessorOutput found in data. Skipping hydration.")
        return {}

    # Load existing inputs
    inputs = data.get("inputs", {})
    if not isinstance(inputs, dict):
        logger.warning("[HydrationHook] The 'inputs' key is invalid. Creating fresh dictionary.")
        inputs = {}

    # Apply properties dynamically
    updates: dict[str, Any] = {}

    # Allow InputProcessor to specify 'inputs' dict directly
    if "inputs" in processor_output and isinstance(processor_output["inputs"], dict):
        updates.update(processor_output["inputs"])
    else:
        # Otherwise grab top-level strings as inputs
        for k, v in processor_output.items():
            if isinstance(v, str) and k != "agent_type":
                updates[k] = v

    if not updates:
        logger.debug("[HydrationHook] Processor output contained no text fields to hydrate.")
        return {}

    logger.info(f"[HydrationHook] Hydrating global inputs with {list(updates.keys())}")

    new_inputs = inputs.copy()
    new_inputs.update(updates)

    return {"inputs": new_inputs}
