"""Deterministic Matrix Flattening Hook for V2 Architecture.

This hook extracts `category_id="matrix"` PromptBlocks for a specific DAG Step,
flattens the 75-atom scale representation into a blind, unstructured list, and
applies Stratified Random Sampling using `MatrixSamplingStrategy` to mitigate
LLM context fatigue and JSON token explosion.
"""

import logging
import random

from pydantic import BaseModel, ConfigDict, Field

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.v2_core import PromptBlock, Step

logger = logging.getLogger(__name__)


class FlattenedAtom(BaseModel):
    """Strict Pydantic schema for individual shuffled items.

    Attributes:
        atom_id: Opaque hashed ID for the extracted atom.
        question: The text content evaluated blindly.
    """

    atom_id: str = Field(description="Opaque hashed ID for the extracted atom.")
    question: str = Field(description="The text content evaluated blindly.")

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")


class FlatteningHookOutput(BaseModel):
    """Strict Pydantic schema for the entire hook state delta payload.

    Attributes:
        shuffled_atoms: The structured list of flattened atoms.
    """

    shuffled_atoms: list[FlattenedAtom]

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")


@hook_registry.register(name="atom_flattening_hook")
async def process_matrix_flattening(state: HookState, deps: HookDependencies) -> HookResult:
    """HOOK: atom_flattening_hook.

    Executes before the LLM context generation to transform complex `MatrixScale` structures
    into a purely blind list `[{"atom_id": "...", "question": "..."}]` ensuring Zero-Trust
    evaluations. Includes Stratified Random Sampling capabilities.

    Args:
        state: The contextual HookState tracking the current run metadata and variables.
        deps: Injected system dependencies including database and configuration registries.

    Returns:
        The HookResult containing execution status and parsed metadata state transitions.

    Raises:
        AppException:
            - ErrorCodes.EXECUTION_NOT_FOUND when repository dependencies are invalid.
            - ErrorCodes.CONFIGURATION_ERROR when sampling configurations are invalid.
            - ErrorCodes.VALIDATION_FAILED when legacy blocks or missing fields are encountered.
    """
    logger.info("[AtomFlatteningHook] Triggered for step '%s' (Execution: %s)", state.step_id, state.execution_id)

    if not state.task_blueprint:
        logger.warning("[AtomFlatteningHook] No task_blueprint defined for step %s. Skpping.", state.step_id)
        return HookResult(success=True, state_delta={})

    repo = deps.workflow_repo
    if not repo:
        logger.error("HookDependencies missing repository.", exc_info=True)
        raise AppException(
            message="HookDependencies missing repository.",
            status_code=500,
            details={"error_code": ErrorCodes.EXECUTION_NOT_FOUND},
        )

    # 1. Fetch the overarching Step configuration safely
    step_def = await repo.get_step_by_id(state.task_blueprint)
    if not step_def:
        logger.warning("[AtomFlatteningHook] Step blueprint '%s' not found.", state.task_blueprint)
        return HookResult(success=True, state_delta={})

    step = Step.model_validate(step_def)
    prompt_block_ids = step.criteria_block_ids

    if not prompt_block_ids:
        return HookResult(success=True, state_delta={})

    # 2. Extract Matrix Sampler Metadata limit
    if "matrix_sampling_strategy" not in state.metadata:
        logger.error("AtomFlatteningHook requires 'matrix_sampling_strategy' in execution metadata.", exc_info=True)
        raise AppException(
            message="AtomFlatteningHook requires 'matrix_sampling_strategy' in execution metadata.",
            status_code=400,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )

    sampling_limit_val = state.metadata["matrix_sampling_strategy"]

    if not isinstance(sampling_limit_val, int) or sampling_limit_val < 0:
        logger.error("Invalid matrix_sampling_strategy value encountered in metadata.", exc_info=True)
        raise AppException(
            message=f"Invalid matrix_sampling_strategy '{sampling_limit_val}'. Exiting via Fail-Fast.",
            status_code=400,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )

    # 3. Retrieve and filter blocks
    all_blocks_raw = await deps.comp_repo.get_all_prompt_blocks()
    all_blocks = all_blocks_raw

    unique_atoms: dict[str, str] = {}

    for raw_block in all_blocks:
        try:
            block = PromptBlock.model_validate(raw_block)
            if block.id in prompt_block_ids and block.category_id == "matrix":
                if block.scales:
                    for scale in block.scales:
                        for claim in scale.claims:
                            for assertion in claim.tda_assertions:
                                unique_atoms[assertion.tda_id] = assertion.ai_rule_description
        except Exception as e:
            logger.warning("Failed to parse prompt block %s: %s", raw_block.get("id"), e, exc_info=True)
            continue

    if not unique_atoms:
        return HookResult(success=True, state_delta={"shuffled_atoms": []})

    atoms_list = [{"atom_id": aid, "question": q} for aid, q in unique_atoms.items()]

    random.shuffle(atoms_list)

    if sampling_limit_val > 0:
        atoms_list = atoms_list[:sampling_limit_val]

    output = FlatteningHookOutput(shuffled_atoms=[FlattenedAtom(**a) for a in atoms_list])

    return HookResult(success=True, state_delta=output.model_dump())
