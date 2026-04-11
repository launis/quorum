"""Deterministic Matrix Flattening Hook for V2 Architecture.

This hook extracts `category_id="matrix"` PromptBlocks for a specific DAG Step,
flattens the 75-atom scale representation into a blind, unstructured list, and
applies Stratified Random Sampling using `MatrixSamplingStrategy` to mitigate
LLM context fatigue and JSON token explosion.
"""

import hashlib
import logging
import random

from pydantic import TypeAdapter

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.enums import MatrixSamplingStrategy
from backend_v2.models.v2_core import PromptBlock, Step

logger = logging.getLogger(__name__)


@hook_registry.register(name="atom_flattening_hook")
async def process_matrix_flattening(state: HookState, deps: HookDependencies) -> HookResult:
    """HOOK: atom_flattening_hook.

    Executes before the LLM context generation to transform complex `MatrixScale` structures
    into a purely blind list `[{"atom_id": "...", "question": "..."}]` ensuring Zero-Trust
    evaluations. Includes Stratified Random Sampling capabilities.
    """
    logger.info("[AtomFlatteningHook] Triggered for step '%s' (Execution: %s)", state.step_id, state.execution_id)

    if not state.task_blueprint:
        logger.warning("[AtomFlatteningHook] No task_blueprint defined for step %s. Skpping.", state.step_id)
        return HookResult(success=True, state_delta={})

    repo = deps.repository
    if not repo:
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

    step = TypeAdapter(Step).validate_python(step_def)
    prompt_block_ids = step.prompt_blocks

    if not prompt_block_ids:
        return HookResult(success=True, state_delta={})

    # 2. Extract Matrix Sampler Metadata limit
    sampling_limit_val = state.metadata.get("matrix_sampling_strategy", MatrixSamplingStrategy.ALL.value)

    # Cast safely to our Enum to prevent naked integers causing confusion
    try:
        sampling_strategy = MatrixSamplingStrategy(sampling_limit_val)
    except ValueError:
        logger.warning(
            "[AtomFlatteningHook] Invalid matrix_sampling_strategy '%s'. Falling back to ALL (0).", sampling_limit_val
        )
        sampling_strategy = MatrixSamplingStrategy.ALL

    # 3. Retrieve and filter blocks
    all_blocks = await repo.get_all_prompt_blocks()

    unique_atoms: dict[str, str] = {}

    for block_dict in all_blocks:
        if block_dict.get("id") in prompt_block_ids:
            if block_dict.get("category_id") == "matrix":
                # Strict parsing to uphold architectural mandate
                block = TypeAdapter(PromptBlock).validate_python(block_dict)

                if not block.scales:
                    continue

                logger.info(
                    "[AtomFlatteningHook] Flattening Matrix: '%s'. Sampling strategy: %s",
                    block.id,
                    sampling_strategy.name,
                )

                matrix_collected_atoms: list[str] = []

                # Stratification happens strictly per-scale
                for scale in block.scales:
                    scale_atoms: list[str] = []

                    for claim in scale.claims:
                        if claim.micro_atoms:
                            scale_atoms.extend(claim.micro_atoms)

                    # Apply constraint securely using deterministic execution ID locking
                    if sampling_strategy != MatrixSamplingStrategy.ALL and len(scale_atoms) > sampling_strategy.value:
                        # Append the specific scale score to the random seed to avoid identical slicing across scales!
                        secure_seed = f"{state.execution_id}_{block.id}_scale_{scale.score}"
                        rng = random.Random(secure_seed)
                        selected_atoms = rng.sample(scale_atoms, sampling_strategy.value)
                        logger.debug(
                            "[AtomFlatteningHook] Scale %s: Sampled %d out of %d atoms.",
                            scale.score,
                            len(selected_atoms),
                            len(scale_atoms),
                        )
                    else:
                        selected_atoms = scale_atoms

                    matrix_collected_atoms.extend(selected_atoms)

                # Calculate immutable MD5 IDs for safe bridging to subsequent math logic
                for text in matrix_collected_atoms:
                    atom_id = hashlib.md5(text.encode("utf-8")).hexdigest()
                    if atom_id not in unique_atoms:
                        unique_atoms[atom_id] = text

    # 4. Global Randomization (Blindness Requirement)
    if unique_atoms:
        flat_list = [{"atom_id": key, "question": val} for key, val in unique_atoms.items()]

        # Shuffle the aggregated pool so LLM cannot infer patterns (e.g. all 1s first, then 2s)
        rng_global = random.Random(state.execution_id)
        rng_global.shuffle(flat_list)

        logger.info("[AtomFlatteningHook] Flattened %d total atoms. Executing global blind shuffle.", len(flat_list))
        return HookResult(success=True, state_delta={"shuffled_atoms": flat_list})

    return HookResult(success=True, state_delta={})
