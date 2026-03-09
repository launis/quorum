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
            if result.get("agent_type") == "InputProcessorAgent" or result.get("history_text") is not None:
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

    # Apply properties
    updates: dict[str, Any] = {}

    h_text = (
        processor_output.get("history_text")
        if isinstance(processor_output, dict)
        else getattr(processor_output, "history_text", None)
    )
    if h_text is not None:
        updates["history_text"] = h_text

    p_text = (
        processor_output.get("product_text")
        if isinstance(processor_output, dict)
        else getattr(processor_output, "product_text", None)
    )
    if p_text is not None:
        updates["product_text"] = p_text

    r_text = (
        processor_output.get("reflection_text")
        if isinstance(processor_output, dict)
        else getattr(processor_output, "reflection_text", None)
    )
    if r_text is not None:
        updates["reflection_text"] = r_text

    if not updates:
        logger.debug("[HydrationHook] Processor output contained no text fields to hydrate.")
        return {}

    logger.info(f"[HydrationHook] Hydrating global inputs with {list(updates.keys())}")

    new_inputs = inputs.copy()
    new_inputs.update(updates)

    return {"inputs": new_inputs}
