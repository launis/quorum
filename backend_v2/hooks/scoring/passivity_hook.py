"""Passivity penalty scoring hook."""

import logging
from typing import Any

from pydantic import ValidationError

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, PromptBlockAdapter
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.v2_core import Step
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

__all__ = ["enforce_passivity_penalty_hook"]


@hook_registry.register(name="enforce_passivity_penalty")
async def enforce_passivity_penalty_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Refined Truth Protocol: Enforces passivity penalty if detected in Judge Output.

    Checks if any dimension in the Judge Output has the minimum possible score.
    If found, applies a strict penalty. Supports Dual Judges (Standard & Cognitive).

    Args:
        state: The execution state of the workflow step.
        deps: Dependency container with repositories.

    Returns:
        The hook execution result with state_delta containing applied penalties.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if fields are missing or invalid.
        AppException: With ErrorCodes.HOOK_EXECUTION_FAILED if repositories are missing.
        AppException: With ErrorCodes.RESOURCE_NOT_FOUND if the step blueprint is not found.
        AppException: With ErrorCodes.CONFIGURATION_ERROR if prompt block has no scales.
    """
    settings = get_settings()
    multiplier = settings.scoring_passivity_multiplier

    if not state:
        msg = "Strict Fail-Fast Enforced: Missing HookState in enforce_passivity_penalty_hook."
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    repository = deps.workflow_repo
    if not repository:
        msg = (
            "Strict Fail-Fast Enforced: No repository provided in HookDependencies for enforce_passivity_penalty_hook."
        )
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.HOOK_EXECUTION_FAILED.value})

    blueprint_id = state.task_blueprint or state.step_id
    if not blueprint_id:
        msg = "Strict Fail-Fast Enforced: No blueprint_id or step_id provided to enforce_passivity_penalty_hook."
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    try:
        step_obj = await repository.get_step_by_id(blueprint_id)
        if not step_obj:
            msg = f"Strict Fail-Fast Enforced: Step blueprint '{blueprint_id}' not found in database."
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value}
            )

        step_model = Step.model_validate(step_obj)
        prompt_block_ids = step_model.criteria_block_ids

        # Resolve which prompt blocks are matrices (Schema-Driven Routing, strictly no duck typing)
        matrix_blocks_meta: dict[str, dict[str, float]] = {}
        for pb_id in prompt_block_ids:
            pb_data = await deps.prompt_block_repo.get_prompt_block_by_id(pb_id)
            if pb_data:
                pb_model = PromptBlockAdapter.validate_python(pb_data, strict=False)
                if isinstance(pb_model, MatrixPromptBlock):
                    scales = pb_model.scales
                    if not scales:
                        msg = f"Strict Fail-Fast Enforced: PromptBlock '{pb_id}' has no scales."
                        logger.error("[ScoringHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                        raise AppException(
                            message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
                        )
                    scale_values = [float(s.score) for s in scales]
                    matrix_blocks_meta[pb_id] = {"math_min": min(scale_values)}

    except ValidationError as e:
        msg = f"Strict Fail-Fast Enforced: Step or PromptBlock validation failed in enforce_passivity_penalty_hook: {e}"
        logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(
            message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
        ) from e

    updates_needed = False
    new_data: dict[str, Any] = {}

    judges_to_check = []
    judges_to_check.append((blueprint_id, state.inputs, True))

    for judge_key, judge_model, is_post_hook in judges_to_check:
        if not judge_model or not isinstance(judge_model, dict):
            continue

        # Zero-Compromise Pledge: Strategy 1 (Legacy score_card) is eradicated.
        if "score_card" in judge_model:
            msg = (
                f"Strict Fail-Fast Enforced: Legacy 'score_card' found in '{judge_key}'. "
                "V1 monolithic judges are explicitly deprecated and banned."
            )
            logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

        penalty_triggered = False

        matrix_keys: list[tuple[str, LightweightMatrixOutput]] = []
        for k in matrix_blocks_meta.keys():
            if k in judge_model:
                try:
                    matrix_dto = LightweightMatrixOutput.model_validate(judge_model[k])
                    matrix_keys.append((k, matrix_dto))
                except ValidationError as e:
                    msg = f"Strict Fail-Fast Enforced: Invalid LightweightMatrixOutput format for '{k}': {e}"
                    logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                    raise AppException(
                        message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                    ) from e

        for k, matrix_dto in matrix_keys:
            math_min = matrix_blocks_meta[k]["math_min"]
            if matrix_dto.raw_score is not None and matrix_dto.raw_score <= math_min:
                penalty_triggered = True
                logger.warning("[ScoringHook] Passive/Low Quality detected in V2 Matrix '%s'", k)
                break

        if penalty_triggered:
            logger.info("[ScoringHook] Applying V2 Passivity Penalty to %s (Factor %s).", judge_key, multiplier)
            new_judge = judge_model.copy()

            for k, matrix_dto in matrix_keys:
                math_min = matrix_blocks_meta[k]["math_min"]

                new_score = matrix_dto.raw_score
                if new_score is not None:
                    new_score = new_score * multiplier
                    if new_score < math_min:
                        new_score = math_min

                new_norm = matrix_dto.normalized_score
                if new_norm is not None:
                    new_norm = new_norm * multiplier
                    if new_norm < 0.0:
                        new_norm = 0.0

                justification = f"[PASSIVITY PENALTY x{multiplier:.2f}] " + matrix_dto.justification

                new_dto = LightweightMatrixOutput(
                    raw_score=new_score,
                    normalized_score=new_norm,
                    level_breakdown=matrix_dto.level_breakdown,
                    justification=justification,
                    evaluated_atoms=matrix_dto.evaluated_atoms,
                    extensions=matrix_dto.extensions,
                    allowed_extensions=matrix_dto.allowed_extensions,
                )
                new_judge[k] = new_dto.model_dump(mode="json")

            # O(1) Map Update if using pre-computed map
            if "_evaluative_matrices" in new_judge and isinstance(new_judge["_evaluative_matrices"], dict):
                eval_map = new_judge["_evaluative_matrices"]
                for k, _ in matrix_keys:
                    if k in eval_map:
                        eval_map[k] = new_judge[k]["normalized_score"]

            if is_post_hook:
                for k, v in new_judge.items():
                    if k in judge_model and judge_model[k] != v:
                        new_data[k] = v
            else:
                new_data[judge_key] = new_judge
            updates_needed = True

    if updates_needed:
        return HookResult(success=True, state_delta=new_data)

    return HookResult(success=True, state_delta={})
