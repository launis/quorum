"""Deterministic Matrix Flattening Hook for V2 Architecture.

This hook extracts `category_id="matrix"` PromptBlocks for a specific DAG Step,
flattens the 75-atom scale representation into a blind, unstructured list, and
applies Stratified Random Sampling using `MatrixSamplingStrategy` to mitigate
LLM context fatigue and JSON token explosion.
"""

import hashlib
import logging
import random

from pydantic import BaseModel, ConfigDict, Field

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.enums import EvaluationMandate
from backend_v2.models.v2_core import PromptBlock, Step

logger = logging.getLogger(__name__)


class FlattenedAtom(BaseModel):
    """Strict Pydantic schema for individual shuffled items (No Naked Dicts rule)."""

    atom_id: str = Field(description="Opaque hashed ID for the extracted atom.")
    question: str = Field(description="The text content evaluated blindly.")

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")


class FlatteningHookOutput(BaseModel):
    """Strict Pydantic schema for the entire hook state delta payload."""

    shuffled_atoms: list[FlattenedAtom]

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")


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

    repo = deps.workflow_repo
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

    step = Step.model_validate(step_def)
    prompt_block_ids = step.prompt_blocks

    if not prompt_block_ids:
        return HookResult(success=True, state_delta={})

    # 2. Extract Matrix Sampler Metadata limit
    if "matrix_sampling_strategy" not in state.metadata:
        raise AppException(
            message="AtomFlatteningHook requires 'matrix_sampling_strategy' in execution metadata.",
            status_code=400,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )

    sampling_limit_val = state.metadata["matrix_sampling_strategy"]

    if not isinstance(sampling_limit_val, int) or sampling_limit_val < 0:
        raise AppException(
            message=f"Invalid matrix_sampling_strategy '{sampling_limit_val}'. Exiting via Fail-Fast.",
            status_code=400,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )

    # 3. Retrieve and filter blocks
    all_blocks = await deps.comp_repo.get_all_prompt_blocks()

    unique_atoms: dict[str, str] = {}

    for raw_block in all_blocks:
        try:
            block = PromptBlock.model_validate(raw_block)
        except Exception as e:
            # Skip invalid legacy models safely. Active models must strictly pass Pydantic validation.
            logger.warning("[AtomFlatteningHook] Skipping malformed raw block: %s", e)
            continue

        if block.id in prompt_block_ids:
            if block.category_id == "matrix":
                assert block.scales is not None, "Matrix Block missing scales. Pydantic fail-fast bypassed."

                logger.info(
                    "[AtomFlatteningHook] Flattening Matrix: '%s'. Sampling limit: %s",
                    block.id,
                    sampling_limit_val,
                )

                matrix_collected_atoms: list[str] = []
                mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value

                # Stratification happens strictly per-scale
                for scale in block.scales:
                    scale_atoms: list[str] = []

                    for claim in scale.claims:
                        if claim.micro_atoms and len(claim.micro_atoms) > 0:
                            scale_atoms.extend([f"{ma.strip()}{mandate}" for ma in claim.micro_atoms])
                        else:
                            msg = f"PromptBlock '{block.id}' claim is missing mandatory 'micro_atoms' during runtime."
                            logger.error("[%s] %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                            raise AppException(
                                message=msg,
                                status_code=500,
                                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                            )

                    # Apply constraint securely using deterministic execution ID locking
                    if sampling_limit_val > 0 and len(scale_atoms) > sampling_limit_val:
                        # Append the specific scale score to the random seed to avoid identical slicing across scales!
                        secure_seed = f"{state.execution_id}_{block.id}_scale_{scale.score}"
                        rng = random.Random(secure_seed)
                        selected_atoms = rng.sample(scale_atoms, sampling_limit_val)
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
        model_list = [FlattenedAtom(atom_id=key, question=val) for key, val in unique_atoms.items()]

        # Shuffle the aggregated pool so LLM cannot infer patterns (e.g. all 1s first, then 2s)
        rng_global = random.Random(state.execution_id)
        rng_global.shuffle(model_list)

        logger.info("[AtomFlatteningHook] Flattened %d total atoms. Executing global blind shuffle.", len(model_list))

        # Enforce Rule 'No Naked Dicts': explicitly dump the structured model
        output_payload = FlatteningHookOutput(shuffled_atoms=model_list)
        return HookResult(success=True, state_delta=output_payload.model_dump(mode="json"))

    return HookResult(success=True, state_delta={})
