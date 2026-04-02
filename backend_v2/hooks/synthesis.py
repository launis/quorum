"""Synthesis hooks for Output Management.

Implements text consolidation and LLM logic generation rules based on
SynthesisConfigDTO properties (such as length constraints and preamble texts).
"""

import logging
from typing import Any

from fastapi import status

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)


@hook_registry.register(name="text_consolidation_hook")
async def text_consolidation_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """HOOK: text_consolidation_hook.

    Consolidates text structures and enforces SynthesisConfigDTO properties.
    Ensures that empty structures are omitted if configured, and injects
    instructions (preambles) into the text payload.

    Args:
        state: Immutable cognitive state including inputs.
        deps: HookDependencies providing data access.

    Returns:
        HookResult: Delta injected with text synthesis instructions.
    """
    logger.debug("[SynthesisHook] Running text_consolidation_hook...")

    if not state:
        return HookResult(success=True, state_delta={})

    inputs = state.inputs
    if not isinstance(inputs, dict):
        msg = "Missing or invalid 'inputs'. Expected dict."
        logger.error("[SynthesisHook] %s: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        )

    # Resolve active workflow to determine the output profile bounds
    workflow_data = await deps.repository.get_workflow_by_id(state.workflow_id)
    if not workflow_data:
        msg = f"Workflow '{state.workflow_id}' not found."
        raise AppException(
            message=msg,
            status_code=status.HTTP_404_NOT_FOUND,
            details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
        )

    # Optional synthesis config
    # By default, we attempt to read the workflow default profile
    default_pid = workflow_data.get("default_profile_id", "default")
    output_profiles = workflow_data.get("output_profiles", {})

    active_profile = output_profiles.get(default_pid, {})
    synthesis_cfg = active_profile.get("synthesis", {}) or {}

    length_constraint = synthesis_cfg.get("length_constraint")
    preamble_dict = synthesis_cfg.get("preamble_text")
    omit_empty = synthesis_cfg.get("omit_empty_sections", True)

    # Start preparing the delta
    delta_result: dict[str, Any] = {}

    # 1. Provide preamble instructions via metadata injection if present
    language = str(state.global_context_vars.get("language") or inputs.get("language") or "en")
    language = language.split("-")[0].lower()

    if preamble_dict and isinstance(preamble_dict, dict):
        _preamble = preamble_dict.get(language) or preamble_dict.get("en")
        if _preamble:
            delta_result["synthesis_preamble"] = _preamble

    # 2. Length Constraints
    if length_constraint:
        delta_result["synthesis_length_limit"] = length_constraint

    # 3. Clean up inputs (Omit Empty Sections)
    consolidated_inputs = {}
    for k, v in inputs.items():
        if omit_empty and (v is None or v == "" or v == []):
            logger.debug("[SynthesisHook] Omitting empty section: %s", k)
            continue
        consolidated_inputs[k] = v

    # Expose the cleaned payload and constraints as a state delta for the DAG to process
    return HookResult(
        success=True,
        state_delta={
            "synthesis_instructions": delta_result,
            "consolidated_inputs": consolidated_inputs
        }
    )
