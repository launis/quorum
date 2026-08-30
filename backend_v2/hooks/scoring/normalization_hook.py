"""Normalization and recalculation scoring hook module."""

import logging
from typing import Any

from pydantic import ValidationError

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    HookDeltaDTO,
    HookDependencies,
    HookResult,
    HookState,
    hook_registry,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, PromptBlockAdapter
from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO, LightweightMatrixOutput
from backend_v2.models.enums import ExecutionStatus, LaxXaiExtensionType
from backend_v2.models.v2_core import OutputProfile, Step
from backend_v2.utils.math_utils import normalize_score_to_100
from backend_v2.utils.scoring import get_scoring_engine

logger = logging.getLogger(__name__)

__all__ = [
    "normalize_matrix_scores_hook",
    "recalculate",
]


@hook_registry.register(name="normalize_matrix_scores")
async def normalize_matrix_scores_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Post-Hook to normalize any raw matrix scores into a user-defined target scale.

    Scans the current step's output in the state context.
    For any numeric field corresponding to a PromptBlock with scales and min/max boundaries,
    calculates the scaled score.

    Args:
        state: The execution state of the workflow step.
        deps: Dependency container with repositories.

    Returns:
        The hook execution result with state_delta containing normalized scores.

    Raises:
        AppException: With ErrorCodes.HOOK_EXECUTION_FAILED if repositories are missing or failure occurs.
        AppException: With ErrorCodes.VALIDATION_FAILED if state data is invalid.
        AppException: With ErrorCodes.RESOURCE_NOT_FOUND if the blueprint or blocks are missing.
        AppException: With ErrorCodes.CONFIGURATION_ERROR if prompt blocks lack scales or boundaries.
    """
    logger.info("[ScoringHook] Running normalize_matrix_scores_hook...")

    repository = deps.workflow_repo
    if not repository:
        msg = "Strict Fail-Fast Enforced: No repository provided in HookDependencies for normalize_matrix_scores_hook."
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.HOOK_EXECUTION_FAILED.value})

    raw_inputs = (
        state.inputs.dynamic_inputs
        if isinstance(state.inputs, ExecutionInputsDTO) and state.inputs.dynamic_inputs
        else (
            state.inputs.raw_inputs
            if isinstance(state.inputs, ExecutionInputsDTO) and state.inputs.raw_inputs
            else (state.inputs if isinstance(state.inputs, dict) else {})  # noqa: QGR012 [REASON: Polymorphic DAG payload validation]
        )
    )
    if not isinstance(raw_inputs, dict):  # noqa: QGR012 [REASON: Polymorphic DAG payload validation]
        msg = "Strict Fail-Fast Enforced: State inputs must be a dictionary in normalize_matrix_scores_hook."
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    blueprint_id = state.task_blueprint or state.step_id

    content_payload = raw_inputs

    if not blueprint_id:
        msg = "Strict Fail-Fast Enforced: No blueprint_id or step_id found in execution context for normalization."
        logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    try:
        step_obj = await repository.get_step_by_id(blueprint_id)
        if not step_obj:
            msg = f"Strict Fail-Fast Enforced: Step blueprint '{blueprint_id}' not found in registry."
            logger.error("[ScoringHook] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value}
            )

        try:
            step_model = Step.model_validate(step_obj)
            prompt_block_ids = step_model.criteria_block_ids
        except ValidationError as e:
            msg = f"Strict Fail-Fast Enforced: Step blueprint '{blueprint_id}' validation failed."
            logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
            ) from e

        updates_made = False
        new_payload = content_payload.copy()

        eval_map: dict[str, float] = (
            new_payload["_evaluative_matrices"]
            if "_evaluative_matrices" in new_payload and isinstance(new_payload["_evaluative_matrices"], dict)  # noqa: QGR012 [REASON: Polymorphic DAG payload validation]
            else {}
        )
        new_payload["_evaluative_matrices"] = eval_map

        for pb_id in prompt_block_ids:
            if pb_id not in new_payload:
                continue

            pb_data = await deps.prompt_block_repo.get_prompt_block_by_id(pb_id)
            if not pb_data:
                msg = f"Strict Fail-Fast Enforced: Missing PromptBlock '{pb_id}' during score normalization."
                logger.error("[ScoringHook] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value}
                )

            try:
                pb_model = PromptBlockAdapter.validate_python(pb_data, strict=False)
            except ValidationError as e:
                msg = f"Strict Fail-Fast Enforced: Invalid PromptBlock format for '{pb_id}': {e}"
                logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                ) from e

            # Skip non-matrix blocks
            if not isinstance(pb_model, MatrixPromptBlock):
                continue

            raw_input_val = new_payload[pb_id]

            try:
                parsed_payload = LightweightMatrixOutput.model_validate(raw_input_val)
            except Exception as e:
                msg = f"Strict Fail-Fast Enforced: Invalid input for normalization at PromptBlock '{pb_id}': {e}"
                logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e

            extensions = parsed_payload.extensions
            justification = parsed_payload.justification
            level_breakdown = parsed_payload.level_breakdown
            evaluated_atoms = parsed_payload.evaluated_atoms

            raw_val = parsed_payload.raw_score

            if not isinstance(raw_val, (int, float)):
                continue

            logger.debug(
                "[ScoringHook] Found PromptBlock '%s' with allowed decimals: %s",
                pb_id,
                pb_model.allow_decimals,
            )

            scales = pb_model.scales

            if not scales:
                msg = f"Strict Fail-Fast Enforced: PromptBlock '{pb_id}' missing 'scales' array."
                logger.error("[ScoringHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
                )

            scores_in_scales = [float(s.score) for s in scales]

            if not scores_in_scales:
                msg = (
                    f"Strict Fail-Fast Enforced: PromptBlock '{pb_id}' has a 'scales' array, "
                    "but no valid numeric scores could be extracted from it."
                )
                logger.error("[ScoringHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
                )

            raw_float = float(raw_val)

            math_min = float(pb_model.computed_min) if pb_model.computed_min is not None else min(scores_in_scales)
            math_max = float(pb_model.computed_max) if pb_model.computed_max is not None else max(scores_in_scales)

            normalized_val = normalize_score_to_100(
                score=raw_float,
                math_min=math_min,
                math_max=math_max,
            )

            justification = justification.strip()

            matrix_dto = LightweightMatrixOutput(
                raw_score=raw_float,
                normalized_score=normalized_val,
                level_breakdown=level_breakdown if level_breakdown else None,
                justification=justification,
                evaluated_atoms=evaluated_atoms,
                extensions=extensions,
                allowed_extensions=parsed_payload.allowed_extensions,
            )

            dumped_matrix = matrix_dto.model_dump(mode="json")
            new_payload[pb_id] = dumped_matrix

            if pb_model.is_evaluative:
                eval_map[pb_id] = normalized_val

            new_payload["_evaluative_matrices"] = eval_map

            updates_made = True
            logger.info(
                "[ScoringHook] Matrix Score '%s': Raw=%s, Normalized=%s",
                pb_id,
                raw_val,
                normalized_val,
            )

        if updates_made:
            return HookResult(success=True, state_delta=HookDeltaDTO(delta=new_payload))

    except Exception as e:
        if isinstance(e, AppException):
            raise

        msg = f"Normalization failed for step '{blueprint_id}': {e}"
        logger.error("[ScoringHook] %s: %s", ErrorCodes.HOOK_EXECUTION_FAILED.name, msg, exc_info=True)

        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.HOOK_EXECUTION_FAILED.value},
        ) from e

    return HookResult(success=True, state_delta=HookDeltaDTO())


async def recalculate(payload: dict[str, Any], profile_id: str | None, deps: HookDependencies) -> None:
    """Decoupled Hybrid Calculation for matrix scores.

    Recalculates matrix scores by analyzing the atoms present in the payload.
    Prioritizes 'human_override' values if present. Mutates payload in-place.

    Args:
        payload: The state_delta dictionary to mutate.
        profile_id: Output Profile ID defining strictness and strategy.
        deps: Hook dependencies for fetching config.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if matrix format or extensions are invalid.
    """
    if not isinstance(payload, dict):  # noqa: QGR012 [REASON: Polymorphic DAG payload validation]
        return

    strictness_level = None
    scoring_strategy = None
    if profile_id:
        profile_dict = await deps.output_profile_repo.get_output_profile_by_id(profile_id)
        if profile_dict:
            profile_model = OutputProfile.model_validate(profile_dict, strict=False)
            strictness_level = profile_model.strictness_level
            scoring_strategy = profile_model.scoring_strategy

    if strictness_level is None or scoring_strategy is None:
        logger.error("[ScoringHook] Missing mandatory scoring configuration in profile '%s'.", profile_id)
        return

    total_true_atoms = 0
    total_false_atoms = 0

    matrix_keys: list[str] = []
    for k, v in payload.items():
        if isinstance(v, dict) and "evaluated_atoms" in v and "justification" in v:  # noqa: QGR012 [REASON: Polymorphic DAG payload validation]
            pb_data = await deps.prompt_block_repo.get_prompt_block_by_id(k)
            if pb_data:
                pb_model = PromptBlockAdapter.validate_python(pb_data, strict=False)
                if isinstance(pb_model, MatrixPromptBlock):
                    try:
                        _ = LightweightMatrixOutput.model_validate(v)
                        matrix_keys.append(k)
                    except Exception as e:
                        msg = f"Strict Fail-Fast Enforced: Invalid LightweightMatrixOutput for matrix '{k}': {e}"
                        logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                        raise AppException(
                            message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                        ) from e

    for pb_id in matrix_keys:
        raw_data = payload[pb_id]
        existing_matrix = LightweightMatrixOutput.model_validate(raw_data)

        pb_data = await deps.prompt_block_repo.get_prompt_block_by_id(pb_id)
        if not pb_data:
            continue
        pb_model = PromptBlockAdapter.validate_python(pb_data, strict=False)
        if not isinstance(pb_model, MatrixPromptBlock):
            continue

        scales = pb_model.scales
        if not scales:
            continue

        scale_values = [float(s.score) for s in scales]
        math_min = min(scale_values)
        math_max = max(scale_values)

        atom_to_scale: dict[str, float] = {}
        for scale in scales:
            s_val = float(scale.score)
            for claim in scale.claims:
                for tda in claim.tda_assertions or []:
                    atom_to_scale[tda.tda_id] = s_val

        raw_stats = {s_val: {"hits": 0, "total": 0, "dlqs": 0} for s_val in scale_values}
        infra_dlqs = 0

        evaluated_atoms = existing_matrix.evaluated_atoms
        for atom_id, status in evaluated_atoms.items():
            if atom_id not in atom_to_scale:
                continue
            s_val = atom_to_scale[atom_id]
            raw_stats[s_val]["total"] += 1

            effective_status = status

            if effective_status == ExecutionStatus.N_A:
                continue

            if effective_status == ExecutionStatus.SYSTEM_ERROR:
                raw_stats[s_val]["dlqs"] += 1
            elif effective_status == ExecutionStatus.PASSED:
                raw_stats[s_val]["hits"] += 1

        global_total = sum(level_data["total"] for level_data in raw_stats.values())
        global_hits = sum(level_data["hits"] for level_data in raw_stats.values())
        global_dlqs = sum(level_data["dlqs"] for level_data in raw_stats.values())

        is_indeterminate = global_total > 0 and (infra_dlqs / global_total) > 0.10

        total_true_atoms += global_hits
        total_false_atoms += global_total - global_hits - global_dlqs

        justification = existing_matrix.justification or ""

        if is_indeterminate:
            raw_score = math_min
            formatted_breakdown = None
            xai_log = None
            justification = (
                f"[INDETERMINATE] Matrix score invalidated because the DLQ ratio "
                f"({global_dlqs / global_total:.2%}) exceeded the 10.00% threshold."
            )
        else:
            engine = get_scoring_engine(scoring_strategy)
            stats = {
                float(k): LevelStatsDTO(hits=v["hits"], total=v["total"], dlqs=v["dlqs"]) for k, v in raw_stats.items()
            }
            raw_score, xai_log, formatted_breakdown = engine.calculate(
                stats=stats,
                math_min=math_min,
                math_max=math_max,
                strictness_level=strictness_level,
            )

        allowed_exts = None
        if pb_model.output_extensions:
            allowed_exts = []
            for ext_str in pb_model.output_extensions:
                try:
                    allowed_exts.append(LaxXaiExtensionType(ext_str))
                except ValueError as e:
                    msg = f"Strict Fail-Fast Enforced: Unsupported LaxXaiExtensionType '{ext_str}' in '{pb_id}'"
                    logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                    raise AppException(
                        message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                    ) from e

        parsed_payload = LightweightMatrixOutput(
            raw_score=raw_score,
            normalized_score=None,
            level_breakdown=formatted_breakdown,
            justification=justification,
            xai_log=xai_log,
            evaluated_atoms=evaluated_atoms,
            extensions=existing_matrix.extensions,
            allowed_extensions=allowed_exts,
        )

        payload[pb_id] = parsed_payload.model_dump(mode="json", exclude_none=True)

    payload["true_atoms_count"] = total_true_atoms
    payload["false_atoms_count"] = total_false_atoms
