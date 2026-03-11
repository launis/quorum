"""Validation hooks for structural integrity checks."""

import logging
from typing import Any

from backend_v2.core.hook_registry import hook_registry
from backend_v2.exceptions import AppException, ErrorCodes

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

    # Original logic for processor_output
    processor_output: dict[str, Any] | Any | None = None
    for _key, result in data.items():
        if result and type(result).__name__ == "InputProcessorOutput":
            processor_output = result
            break
        elif isinstance(result, dict):
            if result.get("agent_type") == "InputProcessorAgent" or "inputs" in result:
                try:
                    processor_output = result
                    break
                except Exception as e:
                    raise AppException(
                        message=f"Failed to inflate InputProcessorOutput during hydration: {str(e)}",
                        status_code=500,
                        details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
                    ) from e

    if not processor_output:
        logger.warning("[HydrationHook] No InputProcessorOutput found in data. Skipping hydration.")
        return {}

    # Load existing inputs
    inputs_raw = data.get("inputs", {})
    if isinstance(inputs_raw, dict):
        inputs = inputs_raw
    else:
        inputs = inputs_raw.model_dump() if hasattr(inputs_raw, "model_dump") else {}

    if not inputs:
        logger.warning("[HydrationHook] Missing 'inputs' block in context. Creating fresh.")
        inputs = {}

    # Apply properties dynamically
    updates: dict[str, Any] = {}

    if isinstance(processor_output, dict):
        # Allow InputProcessor to specify 'inputs' dict directly
        if "inputs" in processor_output and isinstance(processor_output["inputs"], dict):
            updates.update(processor_output["inputs"])
        else:
            # Otherwise grab top-level strings as inputs
            for k, v in processor_output.items():
                if isinstance(v, str) and k != "agent_type":
                    updates[k] = v
    else:
        for k, v in vars(processor_output).items():
            if isinstance(v, str) and k != "agent_type":
                updates[k] = v

    if not updates:
        logger.debug("[HydrationHook] Processor output contained no text fields to hydrate.")
        return {}

    logger.info(f"[HydrationHook] Hydrating global inputs with {list(updates.keys())}")

    new_inputs = inputs.copy()
    new_inputs.update(updates)

    return {"inputs": new_inputs}
