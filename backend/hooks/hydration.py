"""Validation hooks for structural integrity checks."""

import logging
from typing import Any

from backend.exceptions import AppException, ErrorCodes
from backend.models.domain.input_processor import InputProcessorOutput
from backend.models.domain.inputs import WorkflowInputs
from backend.models.state import WorkflowState
from backend.utils.pydantic_utils import inflate

logger = logging.getLogger(__name__)


def hydrate_global_inputs(state: WorkflowState) -> WorkflowState:
    """HOOK: hydrate_global_inputs.

    Extracts the parsed strings from the InputProcessorAgent's output
    and merges them seamlessly into the global `inputs` context variable.
    This preserves the standard `$inputs.history_text` Blueprint Pointer Protocol
    for downstream agents without requiring complex string IDs in seed_data.json.

    Args:
        state (WorkflowState): Current state.

    Returns:
        WorkflowState: Updated state with hydrated `inputs`.
    """
    logger.debug("[HydrationHook] Running global inputs hydration...")

    # Strict Enforce: State must be WorkflowState object
    if isinstance(state, dict):
        raise AppException(
            message="Hydration Hook received dict state. Strict Pydantic Enforcement Violation.",
            status_code=500,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA},
        )

    # Resolve latest results from InputProcessorAgent (Step 0)
    # We must scan results to find the InputProcessorObject
    processor_output: InputProcessorOutput | None = None

    for _, result in state.context_variables.items():
        if isinstance(result, InputProcessorOutput):
            processor_output = result
            break
        elif isinstance(result, dict):
            if result.get("agent_type") == "InputProcessorAgent" or result.get("history_text") is not None:
                try:
                    processor_output = inflate(result, InputProcessorOutput)
                    break
                except Exception as e:
                    raise AppException(
                        message=f"Failed to inflate InputProcessorOutput during hydration: {str(e)}",
                        status_code=500,
                        details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA},
                    ) from e

    if not processor_output:
        logger.warning("[HydrationHook] No InputProcessorOutput found in state results. Skipping hydration.")
        return state

    # Load existing inputs
    inputs = state.get_context("inputs", WorkflowInputs)

    if not inputs:
        logger.warning("[HydrationHook] Missing 'inputs' block in context. Creating fresh.")
        # Fallback creation if somehow missing
        inputs = WorkflowInputs()

    # Apply properties (Immutable copy)
    updates: dict[str, Any] = {}

    if processor_output.history_text is not None:
        updates["history_text"] = processor_output.history_text
    if processor_output.product_text is not None:
        updates["product_text"] = processor_output.product_text
    if processor_output.reflection_text is not None:
        updates["reflection_text"] = processor_output.reflection_text

    if not updates:
        logger.debug("[HydrationHook] Processor output contained no text fields to hydrate.")
        return state

    logger.info(f"[HydrationHook] Hydrating global inputs with {list(updates.keys())}")

    new_inputs = inputs.model_copy(update=updates)

    new_context = state.context_variables.copy()
    new_context["inputs"] = new_inputs

    return state.model_copy(update={"context_variables": new_context})
