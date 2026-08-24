"""Deterministic Matrix Flattening Hook for V2 Architecture.

This hook extracts `category_id="matrix"` PromptBlocks for a specific DAG Step,
flattens the 75-atom scale representation into a blind, unstructured list, and
applies Stratified Random Sampling using `MatrixSamplingStrategy` to mitigate
LLM context fatigue and JSON token explosion.
"""

import logging
import random

from pydantic import BaseModel, ConfigDict, ValidationError

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, PromptBlockAdapter
from backend_v2.models.dtos.dag_models import CausalEdge
from backend_v2.models.dtos.engine import FlattenedAtom
from backend_v2.models.v2_core import Step

logger = logging.getLogger(__name__)

__all__ = ["FlatteningHookOutput", "process_matrix_flattening"]


class FlatteningHookOutput(BaseModel):
    """Strict Pydantic schema for the entire hook state delta payload.

    Attributes:
        shuffled_atoms: List of selected and randomized extraction items.
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
        state: The frozen execution HookState context.
        deps: Injected system service dependencies.

    Returns:
        HookResult: Successful execution wrapper with shuffled atoms in state_delta.

    Raises:
        AppException: If configuration is invalid (CONFIGURATION_ERROR), dependencies
            are missing (EXECUTION_NOT_FOUND), or prompt block validation fails (VALIDATION_FAILED).
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
    prompt_block_ids = step.criteria_block_ids

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
    all_blocks = await deps.prompt_block_repo.get_all_prompt_blocks()

    unique_atoms: dict[str, tuple[str, str, str, bool, tuple[CausalEdge, ...]]] = {}

    for raw_block in all_blocks:
        try:
            block = PromptBlockAdapter.validate_python(raw_block, strict=False)
        except (ValidationError, ValueError) as e:
            msg = f"Strict Fail-Fast Enforced: Invalid legacy block format: {e}"
            logger.error("[AtomFlatteningHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
            ) from e

        if block.id in prompt_block_ids:
            if isinstance(block, MatrixPromptBlock):
                assert block.scales is not None, "Matrix Block missing scales. Pydantic fail-fast bypassed."

                logger.info(
                    "[AtomFlatteningHook] Flattening Matrix: '%s'. Sampling limit: %s",
                    block.id,
                    sampling_limit_val,
                )

                all_matrix_atoms: dict[str, tuple[str, str, str, str, bool, tuple[CausalEdge, ...]]] = {}
                matrix_collected_atoms: list[tuple[str, str, str, str, bool, tuple[CausalEdge, ...]]] = []

                for scale in block.scales:
                    scale_atoms: list[tuple[str, str, str, str, bool, tuple[CausalEdge, ...]]] = []

                    for claim in scale.claims:
                        for tda in claim.tda_assertions:
                            aid = str(tda.tda_id)
                            atom_entry = (
                                aid,
                                tda.concept_description.strip(),
                                tda.extraction_rule.strip() if tda.extraction_rule else "",
                                tda.anchor_target.strip() if tda.anchor_target else "",
                                bool(tda.inverse_evidence),
                                tda.depends_on,
                            )
                            scale_atoms.append(atom_entry)
                            all_matrix_atoms[aid] = atom_entry

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

                # Transitive Causal Closure: retain ancestor atoms required by causal preconditions
                if sampling_limit_val > 0:
                    closure_queue = list(matrix_collected_atoms)
                    included_ids = {atom[0] for atom in matrix_collected_atoms}

                    while closure_queue:
                        current_atom = closure_queue.pop(0)
                        causal_edges = current_atom[5]
                        for edge in causal_edges:
                            parent_id = edge.tda_id
                            if parent_id in all_matrix_atoms and parent_id not in included_ids:
                                parent_atom = all_matrix_atoms[parent_id]
                                matrix_collected_atoms.append(parent_atom)
                                included_ids.add(parent_id)
                                closure_queue.append(parent_atom)
                                logger.debug(
                                    "[AtomFlatteningHook] Transitive Causal Closure: Retained ancestor atom '%s' for '%s'",
                                    parent_id,
                                    current_atom[0],
                                )

                for atom_id, text, rule, anchor, is_inv, deps_tuple in matrix_collected_atoms:
                    if atom_id not in unique_atoms:
                        unique_atoms[atom_id] = (text, rule, anchor, is_inv, deps_tuple)

    # 4. Global Deterministic Sort (Semantic Micro-Batching Requirement)
    if unique_atoms:
        model_list = [
            FlattenedAtom(
                atom_id=key,
                question=val[0],
                extraction_rule=val[1],
                anchor_target=val[2],
                is_inverse=val[3],
                depends_on=val[4],
            )
            for key, val in unique_atoms.items()
        ]

        # Deterministic sort based on atom_id hash to prevent LLM Context Fatigue and ensure reproducibility
        model_list.sort(key=lambda x: x.atom_id)

        logger.info("[AtomFlatteningHook] Flattened %d total atoms. Executing deterministic sort.", len(model_list))

        # Enforce Rule 'No Naked Dicts': explicitly dump the structured model
        output_payload = FlatteningHookOutput(shuffled_atoms=model_list)
        return HookResult(success=True, state_delta=output_payload.model_dump(mode="json"))

    return HookResult(success=True, state_delta={})
