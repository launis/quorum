"""Scoring Hook for evaluating agent performance and applying penalties."""

import logging
from typing import Any, Literal, cast

from pydantic import ConfigDict, Field, ValidationError

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.falsifier import FalsifierData
from backend_v2.models.domain.scoring import StepFalsifierDTO, StepPanelDTO
from backend_v2.models.domain.security import InputProcessingOutputDTO, SanitizationResultDTO
from backend_v2.models.dtos.lightweight_matrix import (
    AtomEvaluationItemDTO,
    LevelStatsDTO,
    LightweightExtractionAtom,
    LightweightMatrixOutput,
)
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.enums import (
    LaxXaiExtensionType,
    ScoringCalibrationThresholds,
    XaiExtensionType,
)
from backend_v2.models.state import StepOutputDTO
from backend_v2.models.v2_core import ExecutionRecord, OutputProfile, PromptBlock, Step, Workflow
from backend_v2.services.orchestrator.ast_evaluator import ASTEvaluator
from backend_v2.settings import get_settings
from backend_v2.utils.math_utils import (
    normalize_score_to_100,
    scale_to_custom_range,
)
from backend_v2.utils.scoring import get_scoring_engine

logger = logging.getLogger(__name__)


class ScoringPayloadWrapper(V2CoreBase):
    """Wrapper for intermediate payload extraction during scoring logic execution."""

    model_config = ConfigDict(extra="ignore", frozen=True)
    sanitization_result: SanitizationResultDTO | None = None
    step_input_processing: InputProcessingOutputDTO | None = None
    step_falsifier: StepFalsifierDTO | None = None
    step_panel: StepPanelDTO | None = None
    evaluative_matrices: dict[str, float] | None = Field(default=None, alias="_evaluative_matrices")


class StateInputWrapper(V2CoreBase):
    """Wrapper for structured state inputs passed into the scoring context."""

    model_config = ConfigDict(extra="ignore", frozen=True)
    steps: list[StepOutputDTO] | None = None
    inputs: dict[str, Any] | None = None
    raw_inputs: dict[str, Any] | None = None


def _extract_payloads(data: dict[str, Any]) -> list[ScoringPayloadWrapper]:
    """Strict Phase 9 Extractor. No V1 Fallbacks. No Naked Dict guessing.

    Args:
        data: The dictionary representation of the hook inputs or global context.

    Returns:
        A list of strictly parsed ScoringPayloadWrapper objects.
    """
    payloads = []

    try:
        hydrated_state = StateInputWrapper.model_validate(data)
    except ValidationError as e:
        msg = f"Strict Fail-Fast Enforced: Execution snapshot validation failed: {e}"
        logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(
            message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
        ) from e

    if hydrated_state.steps is None:
        msg = "Strict Fail-Fast Enforced: Execution snapshot 'steps' missing."
        logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    for valid_dto in hydrated_state.steps:
        if valid_dto.payload is None:
            continue
        try:
            wrapper = ScoringPayloadWrapper.model_validate(valid_dto.payload)
            payloads.append(wrapper)
        except ValidationError as e:
            # If the payload is a primitive (e.g. bool, str) it's not a ScoringPayloadWrapper, skip it.
            # We only want to crash if it's a dict that failed strict validation.
            if not isinstance(valid_dto.payload, dict):
                logger.debug("[ScoringHook] Primitive payload skipped: %s", valid_dto.payload)
                continue

            msg = f"Strict Fail-Fast Enforced: Invalid StepOutputDTO payload in execution snapshot: {e}"
            logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
            ) from e

    # Add explicitly injected top-level dict inputs
    for extra_dict in [hydrated_state.inputs, hydrated_state.raw_inputs]:
        try:
            wrapper = ScoringPayloadWrapper.model_validate(extra_dict)
            payloads.append(wrapper)
        except ValidationError as e:
            logger.debug("[ScoringHook] Extra dict skipped (not a ScoringPayloadWrapper): %s", e)

    return payloads


def _extract_guard_flag(data: dict[str, Any]) -> bool | None:
    """Extracts the security threat flag from the guard output in the state.

    Iterates over the V2 execution snapshot to find the input processing result.
    Silent Fallback is BANNED. If the data is malformed, we raise an exception.
    """
    for wrapper in _extract_payloads(data):
        if wrapper.step_input_processing and wrapper.step_input_processing.security_check:
            return wrapper.step_input_processing.security_check.threat_detected
        elif wrapper.sanitization_result:
            return wrapper.sanitization_result.threat_detected

    logger.info("[ScoringHook] security_check (Input Processing data) missing from state. Security step bypassed.")
    return None


def _extract_falsifier_data(data: dict[str, Any]) -> FalsifierData | None:
    """Extracts falsifier data from either step_falsifier or step_panel outputs in V2 state.

    Iterates over the V2 execution snapshot. Silent Fallback is BANNED.
    """
    for wrapper in _extract_payloads(data):
        if wrapper.step_falsifier and wrapper.step_falsifier.falsifier_data:
            return wrapper.step_falsifier.falsifier_data
        if wrapper.step_panel and wrapper.step_panel.falsifier_data:
            return wrapper.step_panel.falsifier_data

    logger.info("[ScoringHook] Falsifier data missing from state. Falsifier step bypassed.")
    return None


def _calculate_falsifier_penalty(falsifier_data: FalsifierData | None) -> bool:
    """Determines if a post-hoc rationalization penalty should be applied.

    Args:
        falsifier_data (Any | None): The strictly typed falsifier data.

    Returns:
        bool: True if post-hoc rationalization is detected, False otherwise.
    """
    if falsifier_data:
        # Access strictly typed Pydantic attributes
        if falsifier_data.fidelity_audit and falsifier_data.fidelity_audit.post_hoc_rationalization:
            return True
    return False


@hook_registry.register(name="apply_scoring_logic")
def apply_scoring_logic_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Workflow Data wrapper for apply_scoring_logic.

    Aggregates scores from Judge/Evaluation steps, applies penalties based on
    Security (Guard) and Falsifier findings, and returns the strictly updated dict.

    Args:
        state: The execution state of the workflow step.
        deps: Dependency container with repositories.

    Returns:
        The hook execution result with state_delta containing updated scoring results.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if state data is invalid or missing.
    """
    logger.debug("[ScoringHook] Calculating final scores...")

    if not state:
        msg = "Strict Fail-Fast Enforced: Missing HookState in apply_scoring_logic_hook."
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    # V2 Architecture Isolation: Evaluate the exact output of the current execution node.
    # Legacy context lookups and hardcoded DB IDs are explicitly banned.
    lookup_ctx = state.inputs

    # 1. Security Penalty Check (Guard)
    security_threat = _extract_guard_flag(lookup_ctx)

    # 2. Falsifier Penalty Check
    falsifier_data = _extract_falsifier_data(lookup_ctx)
    is_post_hoc = _calculate_falsifier_penalty(falsifier_data)
    penalties: list[str] = []

    total_score_accum = 0.0
    count = 0
    scores_found = []

    # Candidate list for potential multiple judges (Standard + Cognitive)
    # Note: V2 matrices are extracted directly from the context history tree
    # But for final scoring, the Judge node has its own output. Actually, the Judge node
    # has ALL the outputs from previous nodes if using a `PromptBlock` approach.
    # Let's inspect the entire context for any `_scaled` keys that match the whitelist.
    # The Judge is the final aggregator so by checking context we capture everything.

    # In V2, we strictly iterate over the execution snapshot (state.global_context_vars).
    # Legacy V1 step_id checks (e.g. step_judge) have been eradicated.
    candidates = [lookup_ctx]

    unique_matrices = {}

    def _extract_scores(source: ScoringPayloadWrapper) -> None:
        # Epic 34: O(1) Map Pre-computation. Zero-Compromise Pledge enforces strict map parsing.
        if source.evaluative_matrices:
            for block_id, norm_val in source.evaluative_matrices.items():
                unique_matrices[block_id] = float(norm_val)

    for item in candidates:
        if isinstance(item, dict):
            for wrapper in _extract_payloads(item):
                _extract_scores(wrapper)

            # Epic 43 Phase 2 Fix: Extract from hoisted StepOutputDTO list
            try:
                hydrated_item = StateInputWrapper.model_validate(item)
            except ValidationError as e:
                msg = f"Strict Fail-Fast Enforced: Invalid State Input Wrapper Context: {e}"
                logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                ) from e

            if hydrated_item.steps:
                for valid_dto in hydrated_item.steps:
                    if valid_dto.block_id == "_evaluative_matrices" and isinstance(valid_dto.payload, dict):
                        for block_id, norm_val in valid_dto.payload.items():
                            unique_matrices[block_id] = float(norm_val)

    for v_float in unique_matrices.values():
        total_score_accum += v_float
        count += 1
        scores_found.append(v_float)

    if count == 0:
        # Phase 4, Component: Scoring Hooks - Check if the zero count is due to valid INDETERMINATE matrices
        is_valid_indeterminate = False
        for _, v in lookup_ctx.items():
            if isinstance(v, dict) and "[INDETERMINATE]" in str(v.get("justification", "")):
                is_valid_indeterminate = True
                break

        # Also check within steps payload if present
        if not is_valid_indeterminate and "steps" in lookup_ctx and isinstance(lookup_ctx["steps"], list):
            for step_val in lookup_ctx["steps"]:
                payload = step_val.get("payload") if isinstance(step_val, dict) else getattr(step_val, "payload", None)
                if isinstance(payload, dict):
                    for _, v in payload.items():
                        if isinstance(v, dict) and "[INDETERMINATE]" in str(v.get("justification", "")):
                            is_valid_indeterminate = True
                            break
                    if is_valid_indeterminate:
                        break

        if is_valid_indeterminate:
            logger.warning("[ScoringHook] All matrices are INDETERMINATE. Skipping aggregation.")
            indet_result = {
                "total_score": None,
                "final_score": None,
                "penalties_applied": penalties,
                "aggregation_status": "INDETERMINATE - Cognitive Collapse / Quality Check Failed",
            }
            return HookResult(success=True, state_delta={"scoring_result": indet_result})

        # Enforce Fail-Fast! Silent fallbacks and graceful degradation are BANNED.
        msg = (
            "Strict Fail-Fast Enforced: '_evaluative_matrices' missing from state. "
            "Matrix normalization failed or was bypassed."
        )
        logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
    else:
        # A true unified average (all 0-100 scales) of commensurate dimensions
        average_score = total_score_accum / count

    # 4. Apply Penalties (Log traces and apply to average without corrupting base)
    settings = get_settings()

    final_score = average_score

    total_penalty_factor = 0.0

    if security_threat:
        p_val = settings.scoring_security_penalty
        if p_val > 0:
            total_penalty_factor += p_val
            pct_val = p_val * 100
            # Use structured key format to defer localization to presentation boundaries
            penalties.append(f"PENALTY_SECURITY:{pct_val:.0f}")
        else:
            logger.warning("[ScoringHook] Security Threat Detected (Logged Only - Penalty Disabled in Settings)")

    if is_post_hoc:
        p_val = settings.scoring_post_hoc_penalty
        if p_val > 0:
            total_penalty_factor += p_val
            pct_val = p_val * 100
            # Use structured key format to defer localization to presentation boundaries
            penalties.append(f"PENALTY_POST_HOC:{pct_val:.0f}")
        else:
            logger.warning(
                "[ScoringHook] Post-Hoc Rationalization Detected (Logged Only - Penalty Disabled in Settings)"
            )

    effective_penalty = min(total_penalty_factor, ScoringCalibrationThresholds.PENALTY_CAP.value)

    if effective_penalty > 0:
        final_score *= 1.0 - effective_penalty
        logger.warning(
            "[ScoringHook] Combined penalties applied: -%.0f%% (capped at %.0f%%).",
            effective_penalty * 100,
            ScoringCalibrationThresholds.PENALTY_CAP.value * 100,
        )

    # Safety Clamp (0.0 - 100.0)
    final_score = max(0.0, final_score)

    # 5. Create Result with True Averaging
    result = {
        "total_score": final_score,
        "final_score": final_score,
        "penalties_applied": penalties,
        "aggregation_status": f"V2 Commensurate Average of {count} matrices",
    }

    logger.info(
        "[ScoringHook] Scoring validation complete. Commensurate Base Average: %.1f, Final: %.1f. Penalties: %d",
        average_score,
        final_score,
        len(penalties),
    )
    return HookResult(success=True, state_delta={"scoring_result": result})


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
    # User requested "Set it to max" -> 1.0 (No reduction) for testing.
    # Logic: new_score = current_score * multiplier
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
                pb_model = PromptBlock.model_validate(pb_data)
                if pb_model.category_id == "matrix":
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

    # V2 Architecture Isolation: Evaluate the exact output of the current execution node.
    # Legacy context lookups and hardcoded DB IDs are explicitly banned.
    judges_to_check.append((blueprint_id, state.inputs, True))

    for judge_key, judge_model, is_post_hook in judges_to_check:
        if not judge_model or not isinstance(judge_model, dict):
            continue

        # Zero-Compromise Pledge: Strategy 1 (Legacy score_card) is eradicated.
        # We exclusively process V2 Matrices (LightweightMatrixOutput).
        if "score_card" in judge_model:
            msg = (
                f"Strict Fail-Fast Enforced: Legacy 'score_card' found in '{judge_key}'. "
                "V1 monolithic judges are explicitly deprecated and banned."
            )
            logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

        penalty_triggered = False

        matrix_keys = []
        for k in matrix_blocks_meta.keys():
            if k in judge_model:
                try:
                    mapped = LightweightMatrixOutput.map_llm_extensions_to_domain(judge_model[k])
                    matrix_dto = LightweightMatrixOutput.model_validate(mapped)
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
            if "_evaluative_matrices" in new_judge:
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


@hook_registry.register(name="matrix_scoring_hook")
async def matrix_scoring_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Post-Hook to calculate Matrix scores from blind atom evaluations.

    Calculates final matrix scores based on the mathematical engine mapped to the
    workflow's execution output profile.

    Args:
        state: The execution state of the workflow step.
        deps: Dependency container with repositories.

    Returns:
        The hook execution result with state_delta containing computed matrix scores.

    Raises:
        AppException: With ErrorCodes.HOOK_EXECUTION_FAILED if dependencies fail.
        AppException: With ErrorCodes.VALIDATION_FAILED if inputs are not dictionaries.
        AppException: With ErrorCodes.RESOURCE_NOT_FOUND if step, execution, or workflow is missing.
        AppException: With ErrorCodes.CONFIGURATION_ERROR if prompt blocks lack valid scales.
    """
    logger.info("[ScoringHook] Running matrix_scoring_hook...")

    repository = deps.workflow_repo
    if not repository:
        msg = "Strict Fail-Fast Enforced: No repository provided in HookDependencies for matrix_scoring_hook."
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.HOOK_EXECUTION_FAILED.value})

    if not isinstance(state.inputs, dict):
        msg = "Strict Fail-Fast Enforced: State inputs must be a dictionary in matrix_scoring_hook."
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    blueprint_id = state.task_blueprint or state.step_id
    if not blueprint_id:
        msg = "Strict Fail-Fast Enforced: No blueprint_id or step_id provided to matrix_scoring_hook."
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    try:
        step_obj = await repository.get_step_by_id(blueprint_id)
        if not step_obj:
            msg = f"Strict Fail-Fast Enforced: Step blueprint '{blueprint_id}' not found in database."
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

        # Determine if this step actually contains matrix blocks
        matrix_blocks = []
        for pb_id in prompt_block_ids:
            pb_data = await deps.prompt_block_repo.get_prompt_block_by_id(pb_id)
            if pb_data:
                try:
                    pb_model = PromptBlock.model_validate(pb_data)
                    if pb_model.category_id == "matrix":
                        matrix_blocks.append((pb_id, pb_model))
                except ValidationError as e:
                    msg = f"Strict Fail-Fast Enforced: PromptBlock '{pb_id}' validation failed."
                    logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                    raise AppException(
                        message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                    ) from e

        # If no matrix blocks exist, then waterfall scoring natively skips without demanding evaluations
        if not matrix_blocks:
            logger.debug("[ScoringHook] Step '%s' contains no matrix blocks. Skipping waterfall scoring.", blueprint_id)
            return HookResult(success=True, state_delta={})

        raw_exec_data = await deps.exec_repo.get_execution(state.execution_id)
        if not raw_exec_data:
            msg = f"Strict Fail-Fast Enforced: Execution {state.execution_id} missing from database."
            logger.error("[ScoringHook] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
            raise AppException(
                message=msg, status_code=404, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value}
            )

        execution_data = ExecutionRecord.model_validate(raw_exec_data, strict=False)

        raw_workflow = await repository.get_workflow_by_id(execution_data.workflow_id)
        if not raw_workflow:
            msg = f"Strict Fail-Fast Enforced: Workflow {execution_data.workflow_id} missing from database."
            logger.error("[ScoringHook] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
            raise AppException(
                message=msg, status_code=404, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value}
            )
        workflow = Workflow.model_validate(raw_workflow, strict=False)
        enable_contextual_overrides = workflow.enable_contextual_overrides

        # Epic 47 Phase 2: Dynamic Orchestration & Scoring Resolution
        strictness_level = None
        scoring_strategy = None
        visible_block_extensions = []
        locale = (
            execution_data.metadata.get("target_locale", "fi")
            if execution_data.metadata and isinstance(execution_data.metadata, dict)
            else "fi"
        )

        profile_id = execution_data.output_profile_id
        if profile_id:
            profile_dict = await deps.output_profile_repo.get_output_profile_by_id(profile_id)
            if profile_dict:
                profile_model = OutputProfile.model_validate(profile_dict, strict=False)
                strictness_level = profile_model.strictness_level
                scoring_strategy = profile_model.scoring_strategy
                visible_block_extensions = profile_model.visible_block_extensions

        if strictness_level is None or scoring_strategy is None:
            msg = f"Strict Fail-Fast Enforced: Missing mandatory scoring configuration in profile '{profile_id}'."
            logger.error("[ScoringHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
            )

        content_payload = state.inputs

        is_dag_mode = False
        if "results" in content_payload:
            evaluations = content_payload["results"]
            is_dag_mode = True
        elif "evaluations" in content_payload:
            evaluations = content_payload["evaluations"]
        else:
            msg = (
                f"Strict Fail-Fast Enforced: 'evaluations' array is completely missing from state.inputs "
                f"for step '{blueprint_id}'. Upstream atomization payload failed."
            )
            logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        if not isinstance(evaluations, list):
            msg = f"Strict Fail-Fast Enforced: 'evaluations' array is not a list for step '{blueprint_id}'."
            logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        atom_mapping: dict[str, tuple[str, float, str, str, bool, bool]] = {}
        blocks_meta: dict[str, dict[str, Any]] = {}

        # 1. Reverse extraction of Atom Hashes
        for pb_id, pb_model in matrix_blocks:
            scales = pb_model.scales
            if not scales:
                msg = f"Strict Fail-Fast Enforced: PromptBlock '{pb_id}' has no scales."
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
                )

            blocks_meta[pb_id] = {"scales": []}

            for scale in scales:
                s_val = float(scale.score)
                blocks_meta[pb_id]["scales"].append(s_val)
                claims = scale.claims
                for claim in claims:
                    tda_assertions = claim.tda_assertions
                    if tda_assertions:
                        for tda in tda_assertions:
                            aid = str(tda.tda_id)
                            atom_mapping[aid] = (
                                pb_id,
                                s_val,
                                tda.concept_description,
                                str(tda.aggregation_mode),
                                tda.inverse_evidence,
                                tda.allow_contextual_override,
                            )

            # Fail-fast: Ei fallbackeja. Korjattu normaalin virhehallinnan tyyliin.
            if not blocks_meta[pb_id]["scales"]:
                msg = f"PromptBlock '{pb_id}' scales array failed to provide numeric values for waterfall bounds."
                logger.error("[ScoringHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )

            blocks_meta[pb_id]["math_min"] = min(blocks_meta[pb_id]["scales"])
            blocks_meta[pb_id]["math_max"] = max(blocks_meta[pb_id]["scales"])

        block_scale_stats: dict[str, dict[float, dict[str, int]]] = {}
        missing_atoms_by_block: dict[str, list[str]] = {}
        evaluated_atoms_by_block: dict[str, dict[str, bool | str]] = {}
        atom_quotes_by_block: dict[str, list[Any]] = {}
        contested_atoms_by_block: dict[str, int] = {}
        matrix_extensions_by_block: dict[str, dict[str, list[str]]] = {}

        # 2. Iterate evaluations using whitelisted ASTEvaluator for 3-State Logic

        # Compute missing chunks ratio based on chunk evaluations in content_payload
        dlq_evals = 0
        infra_dlqs = 0
        total_evals = 0
        if isinstance(evaluations, list):
            total_evals = len(evaluations)
            for ev in evaluations:
                is_infra = False
                is_val = False
                if isinstance(ev, dict):
                    if "_dlq_status" in ev and ev["_dlq_status"] == "FAILED/DLQ":
                        is_infra = True
                    elif "status" in ev and ev["status"] == "DLQ":
                        is_val = True
                else:
                    if hasattr(ev, "_dlq_status") and ev._dlq_status == "FAILED/DLQ":
                        is_infra = True
                    elif hasattr(ev, "status") and ev.status == "DLQ":
                        is_val = True

                if is_infra or is_val:
                    dlq_evals += 1
                if is_infra:
                    infra_dlqs += 1

        # Get merged facts dictionary from dynamic MergedFactsDTO context
        merged_facts = content_payload.get("extracted_facts", {})
        if hasattr(merged_facts, "model_dump"):
            merged_facts = merged_facts.model_dump(mode="json")
        if not isinstance(merged_facts, dict):
            msg = "Strict Fail-Fast Enforced: extracted_facts must be a dictionary or model."
            logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

        for pb_id, pb_model in matrix_blocks:
            scales = pb_model.scales or []
            block_scale_stats[pb_id] = {}
            missing_atoms_by_block[pb_id] = []
            evaluated_atoms_by_block[pb_id] = {}
            atom_quotes_by_block[pb_id] = []
            contested_atoms_by_block[pb_id] = 0
            matrix_extensions_by_block[pb_id] = {}

            for scale in scales:
                s_val = float(scale.score)
                s_name = scale.name.resolve(locale) if scale.name else str(scale.score)
                block_scale_stats[pb_id][s_val] = {"hits": 0, "total": 0, "dlqs": 0}

                claims = scale.claims
                for claim in claims:
                    tda_assertions = claim.tda_assertions
                    if tda_assertions:
                        for tda in tda_assertions:
                            aid = tda.tda_id
                            text = tda.concept_description

                            # Determine evaluation track
                            final_state: Literal["TRUE", "FALSE", "DLQ", "CONTESTED"]
                            if tda.evaluation_track == "EXTRACTIVE_SENSOR" and tda.logical_expression:
                                # Deterministic AST boolean evaluation on merged facts with DLQ tolerance
                                ast_res = ASTEvaluator.evaluate(
                                    expression=tda.logical_expression,
                                    facts=merged_facts,
                                    total_chunks=total_evals or 1,
                                    dlq_chunks=dlq_evals,
                                )
                                final_state = cast(Literal["TRUE", "FALSE", "DLQ", "CONTESTED"], ast_res)
                            else:
                                # Fallback or cognitive track: look up chunk evaluations by atom_id
                                final_state = "FALSE"
                                if isinstance(evaluations, list):
                                    for ev in evaluations:
                                        # Skip Infra-DLQ items to prevent ValidationErrors (Rule 19)
                                        # Validation-DLQs (status="DLQ") are evaluated normally
                                        is_ev_infra_dlq = False
                                        if isinstance(ev, dict):
                                            is_ev_infra_dlq = "_dlq_status" in ev and ev["_dlq_status"] == "FAILED/DLQ"
                                        else:
                                            is_ev_infra_dlq = (
                                                hasattr(ev, "_dlq_status") and ev._dlq_status == "FAILED/DLQ"
                                            )

                                        if is_ev_infra_dlq:
                                            continue

                                        ev_dict = (
                                            ev
                                            if isinstance(ev, dict)
                                            else (
                                                ev.model_dump(mode="json") if hasattr(ev, "model_dump") else ev.__dict__
                                            )
                                        )

                                        val_context = state.global_context_vars or {}
                                        ev_dto: Any = None

                                        if is_dag_mode:
                                            from backend_v2.models.v2_core import AtomResultDTO

                                            try:
                                                ev_dto = AtomResultDTO.model_validate(ev_dict)
                                            except ValidationError as e:
                                                logger.error(f"[ScoringHook] Invalid DAG AtomResultDTO: {e}")
                                                raise AppException(
                                                    message=f"Strict Fail-Fast: Invalid AtomResultDTO: {e}",
                                                    status_code=500,
                                                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                                                ) from e
                                        else:
                                            try:
                                                # Try heavy protocol first by stripping dynamic fields (e.g. premise_1_quote injected by chunk_worker)
                                                heavy_payload = {
                                                    k: v
                                                    for k, v in ev_dict.items()
                                                    if k in AtomEvaluationItemDTO.model_fields
                                                }
                                                ev_dto = AtomEvaluationItemDTO.model_validate(
                                                    heavy_payload, context=val_context
                                                )
                                            except ValidationError:
                                                try:
                                                    # Fallback to lightweight protocol by stripping ALL heavy cognitive fields
                                                    light_payload = {
                                                        k: v
                                                        for k, v in ev_dict.items()
                                                        if k in LightweightExtractionAtom.model_fields
                                                    }
                                                    ev_dto = LightweightExtractionAtom.model_validate(
                                                        light_payload, context=val_context
                                                    )
                                                except ValidationError as e:
                                                    logger.error(
                                                        "[ScoringHook] %s: Invalid evaluation item format (both heavy and light failed): %s",
                                                        ErrorCodes.VALIDATION_FAILED.name,
                                                        e,
                                                        exc_info=True,
                                                    )
                                                    raise AppException(
                                                        message=f"Strict Fail-Fast: Invalid evaluation item format: {e}",
                                                        status_code=500,
                                                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                                                    ) from e

                                        ev_atom_id = ev_dto.tda_id if is_dag_mode else ev_dto.atom_id

                                        if ev_atom_id == aid:
                                            allow_override = tda.allow_contextual_override
                                            effective_override = enable_contextual_overrides and allow_override

                                            if is_dag_mode:
                                                # In DAG mode, AtomResultDTO has status Enum
                                                status_str = (
                                                    ev_dto.status.name
                                                    if hasattr(ev_dto.status, "name")
                                                    else str(ev_dto.status)
                                                )

                                                if status_str == "DLQ":
                                                    final_state = "DLQ"
                                                elif status_str == "CONTESTED":
                                                    final_state = "CONTESTED"
                                                else:
                                                    if status_str == "PASSED":
                                                        is_satisfied = not tda.inverse_evidence
                                                    elif status_str == "FAILED":
                                                        is_satisfied = bool(tda.inverse_evidence)
                                                    else:
                                                        is_satisfied = False

                                                    # Apply override logic
                                                    if (
                                                        (not is_satisfied)
                                                        and effective_override
                                                        and ev_dto.contextual_override
                                                    ):
                                                        is_satisfied = True

                                                    final_state = "TRUE" if is_satisfied else "FALSE"

                                                quotes_to_process = []
                                                if ev_dto.source_quote:
                                                    quotes_to_process = [
                                                        {"text": ev_dto.source_quote, "source_id": None}
                                                    ]

                                            else:
                                                is_satisfied = ev_dto.calculate_rule_satisfied(
                                                    inverse_evidence=tda.inverse_evidence,
                                                    allow_contextual_override=effective_override,
                                                )
                                                if is_satisfied == "DLQ":
                                                    final_state = "DLQ"
                                                else:
                                                    if getattr(ev_dto, "status", None) == "CONTESTED":
                                                        final_state = "CONTESTED"
                                                    else:
                                                        final_state = "TRUE" if is_satisfied else "FALSE"

                                                quotes_to_process = ev_dto.exact_quotes if ev_dto.exact_quotes else []

                                            if quotes_to_process:
                                                for qt in quotes_to_process:
                                                    quote_text = ""
                                                    opaque_id = None
                                                    if isinstance(qt, dict):
                                                        quote_text = qt.get("text", "")
                                                        opaque_id = qt.get("source_id")
                                                    else:
                                                        quote_text = getattr(qt, "text", "")
                                                        opaque_id = getattr(qt, "source_id", None)

                                                    eq_dto = QuoteEvidenceDTO.model_validate(
                                                        {
                                                            "quote": quote_text,
                                                            "source_alias": [opaque_id] if opaque_id else [],
                                                        },
                                                        context=val_context,
                                                    ).model_dump(mode="json")

                                                    atom_quotes_by_block[pb_id].append(
                                                        {
                                                            "level": s_val,
                                                            "level_name": s_name,
                                                            "quote": eq_dto,
                                                        }
                                                    )

                                            elif getattr(ev_dto, "contextual_override", False) and effective_override:
                                                l_raw = getattr(ev_dto, "structural_location", None)
                                                loc = l_raw if l_raw and l_raw != "N/A" else "Tuntematon sijainti"
                                                r_raw = (
                                                    getattr(ev_dto, "semantic_reasoning", None)
                                                    if not is_dag_mode
                                                    else getattr(ev_dto, "evaluation_reasoning", None)
                                                )
                                                rsn = r_raw if r_raw else "Ei perustelua"
                                                atom_quotes_by_block[pb_id].append(f"📍 {loc}: {rsn}")

                                            extensions_dict = ev_dict.get("extensions", {})
                                            if extensions_dict:
                                                allowed_exts = {
                                                    e.value if hasattr(e, "value") else str(e)
                                                    for e in visible_block_extensions
                                                }
                                                for ext_k, ext_v in extensions_dict.items():
                                                    ext_key_str = ext_k.value if hasattr(ext_k, "value") else str(ext_k)
                                                    if ext_key_str in allowed_exts and ext_v:
                                                        prefix = (
                                                            "💡"
                                                            if ext_key_str == "coaching"
                                                            else "⚠️"
                                                            if ext_key_str == "falsification"
                                                            else "🛠️"
                                                        )
                                                        atom_quotes_by_block[pb_id].append(
                                                            f"{prefix} {ext_key_str.upper()}: {ext_v}"
                                                        )
                                                        if ext_key_str not in matrix_extensions_by_block[pb_id]:
                                                            matrix_extensions_by_block[pb_id][ext_key_str] = []
                                                        matrix_extensions_by_block[pb_id][ext_key_str].append(ext_v)

                                            break

                            # Record the logic outcomes
                            if final_state == "DLQ":
                                evaluated_atoms_by_block[pb_id][aid] = "DLQ"
                                block_scale_stats[pb_id][s_val]["total"] += 1
                                block_scale_stats[pb_id][s_val]["dlqs"] += 1
                                missing_atoms_by_block[pb_id].append(f"- {text} (DLQ - Unscorable)")
                            elif final_state == "CONTESTED":
                                evaluated_atoms_by_block[pb_id][aid] = "CONTESTED"
                                block_scale_stats[pb_id][s_val]["total"] += 1
                                block_scale_stats[pb_id][s_val]["hits"] += 1
                                contested_atoms_by_block[pb_id] += 1
                            elif final_state == "TRUE":
                                evaluated_atoms_by_block[pb_id][aid] = True
                                block_scale_stats[pb_id][s_val]["total"] += 1
                                block_scale_stats[pb_id][s_val]["hits"] += 1
                            else:
                                evaluated_atoms_by_block[pb_id][aid] = False
                                block_scale_stats[pb_id][s_val]["total"] += 1
                                missing_atoms_by_block[pb_id].append(f"- {text}")

        # 3. Hybrid Calculation
        new_payload = content_payload.copy()

        if "atom_quotes" not in new_payload:
            new_payload["atom_quotes"] = {}
        for pb_id, quotes in atom_quotes_by_block.items():
            if quotes:
                new_payload["atom_quotes"][pb_id] = quotes

        # Inject dummy matrices so recalculate() can discover and compute them
        for pb_id, evaluated_atoms in evaluated_atoms_by_block.items():
            final_exts = {
                XaiExtensionType(k): "\n\n".join(v) for k, v in matrix_extensions_by_block.get(pb_id, {}).items()
            }
            dummy = LightweightMatrixOutput(
                raw_score=0.0,
                normalized_score=None,
                level_breakdown=None,
                justification="[INITIALIZING]",
                evaluated_atoms=evaluated_atoms,
                extensions=final_exts,
            )
            new_payload[pb_id] = dummy.model_dump(mode="json", exclude_none=True)

            if missing_atoms_by_block[pb_id]:
                new_payload[f"{pb_id}_missing_context"] = "\n".join(missing_atoms_by_block[pb_id])

        # 4. Decoupled Hybrid Calculation
        await recalculate(
            payload=new_payload,
            profile_id=profile_id,
            deps=deps,
        )

        return HookResult(success=True, state_delta=new_payload)

    except Exception as e:
        if isinstance(e, AppException):
            raise
        msg = f"Hybrid waterfall scoring failed for step '{blueprint_id}': {e}"
        logger.error("[ScoringHook] %s: %s", ErrorCodes.HOOK_EXECUTION_FAILED.name, msg, exc_info=True)
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.HOOK_EXECUTION_FAILED.value},
        ) from e

    return HookResult(success=True, state_delta={})


@hook_registry.register(name="normalize_matrix_scores")
async def normalize_matrix_scores_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Post-Hook to normalize any raw matrix scores into a user-defined target scale.

    It scans the current step's output in the state context.
    For any numeric field corresponding to a PromptBlock with `scales` and min/max boundaries,
    it calculates the scaled score.

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

    # V2 Fast-Fail Architecture: State is now a strictly isolated dictionary (DAGExecutor final_dict)
    # We depend on _sys_step_id being injected during the execution context.
    if not isinstance(state.inputs, dict):
        msg = "Strict Fail-Fast Enforced: State inputs must be a dictionary in normalize_matrix_scores_hook."
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    # Look up the PromptBlocks from the task_blueprint (the actual Step model schema)
    # rather than the workflow's StepRule instance ID, which lacks the prompt_blocks array.
    blueprint_id = state.task_blueprint or state.step_id

    content_payload = state.inputs

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

        eval_map = new_payload.setdefault("_evaluative_matrices", {})

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
                pb_model = PromptBlock.model_validate(pb_data)
            except ValidationError as e:
                msg = f"Strict Fail-Fast Enforced: Invalid PromptBlock format for '{pb_id}': {e}"
                logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                ) from e

            # Skip non-matrix blocks! They have different schemas (e.g. they include 'status' from ChunkWorker)
            if pb_model.category_id != "matrix":
                continue

            # The Anti-TDD Trap & Zero-Compromise Pledge: We intercept the payload with a strict Pydantic adapter
            raw_input_val = new_payload[pb_id]

            try:
                mapped = LightweightMatrixOutput.map_llm_extensions_to_domain(raw_input_val)
                parsed_payload = LightweightMatrixOutput.model_validate(mapped)
            except Exception as e:
                # Strictly fail-fast, Graceful Degradation is banned!
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

            # FAIL-FAST: The scales array MUST dictate the internal math boundaries.
            if not scales:
                msg = f"Strict Fail-Fast Enforced: PromptBlock '{pb_id}' missing 'scales' array."
                logger.error("[ScoringHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
                )

            # DISPLAY BOUNDARIES: UI projection targets
            display_min = pb_model.scale_min
            display_max = pb_model.scale_max

            if display_min is None or display_max is None:
                msg = (
                    f"Strict Fail-Fast Enforced: PromptBlock '{pb_id}' missing explicit display "
                    "'scale_min' or 'scale_max' in database. Fallback estimates are forbidden."
                )
                logger.error("[ScoringHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
                )

            scores_in_scales = []
            for s in scales:
                scores_in_scales.append(float(s.score))

            if not scores_in_scales:
                msg = (
                    f"Strict Fail-Fast Enforced: PromptBlock '{pb_id}' has a 'scales' array, "
                    "but no valid numeric scores could be extracted from it."
                )
                logger.error("[ScoringHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
                )

            # 1. The original AI output, calculated on the internal Math bounds
            raw_float = float(raw_val)

            math_min = min(scores_in_scales)
            math_max = max(scores_in_scales)

            # 2. Scale mathematically to custom Output Target Range (DB scale_min/scale_max explicitly for DISPLAY)
            scaled_val = scale_to_custom_range(
                score=raw_float,
                raw_min=math_min,
                raw_max=math_max,
                target_min=float(display_min),
                target_max=float(display_max),
            )

            # 3. The 1-100 normalized value for commensurable aggregation (V2 Logic)
            normalized_val = normalize_score_to_100(
                score=raw_float,
                math_min=math_min,
                math_max=math_max,
            )

            justification = justification.strip()

            # Replace legacy flattening with strict schema mapping!
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
            dumped_matrix["__replace__"] = True
            new_payload[pb_id] = dumped_matrix

            # Epic 10 & 34: Check the DB truth for Evaluative Matrix status and inject to O(1) Map
            if pb_model.is_evaluative:
                eval_map[pb_id] = normalized_val

            new_payload["_evaluative_matrices"] = eval_map

            updates_made = True
            logger.info(
                "[ScoringHook] 3-Tier Score '%s': Raw=%s, Scaled=%s, Normalized=%s",
                pb_id,
                raw_val,
                scaled_val,
                normalized_val,
            )

        # V2 Dict direct mutation avoided, send back state_delta
        if updates_made:
            return HookResult(success=True, state_delta=new_payload)

    except Exception as e:
        if isinstance(e, AppException):
            raise

        # Fail Fast Requirement
        msg = f"Normalization failed for step '{blueprint_id}': {e}"
        logger.error("[ScoringHook] %s: %s", ErrorCodes.HOOK_EXECUTION_FAILED.name, msg, exc_info=True)

        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.HOOK_EXECUTION_FAILED.value},
        ) from e

    return HookResult(success=True, state_delta={})


async def recalculate(payload: dict[str, Any], profile_id: str | None, deps: HookDependencies) -> None:
    """Decoupled Hybrid Calculation for matrix scores.

    Recalculates matrix scores by analyzing the atoms present in the payload.
    Prioritizes 'human_override' values if present. Mutates payload in-place.

    Args:
        payload: The state_delta dictionary to mutate.
        profile_id: Output Profile ID defining strictness and strategy.
        deps: Hook dependencies for fetching config.
    """
    if not isinstance(payload, dict):
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

    # Discover matrix blocks inside state_delta
    matrix_keys = []
    for k, v in payload.items():
        if isinstance(v, dict) and "evaluated_atoms" in v and "justification" in v:
            # Check if this is a matrix block
            pb_data = await deps.prompt_block_repo.get_prompt_block_by_id(k)
            if pb_data:
                pb_model = PromptBlock.model_validate(pb_data)
                if pb_model.category_id == "matrix":
                    try:
                        mapped_data = LightweightMatrixOutput.map_llm_extensions_to_domain(v)
                        _ = LightweightMatrixOutput.model_validate(mapped_data)
                        matrix_keys.append(k)
                    except Exception as e:
                        msg = f"Strict Fail-Fast Enforced: Invalid LightweightMatrixOutput for matrix '{k}': {e}"
                        logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                        raise AppException(
                            message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                        ) from e

    for pb_id in matrix_keys:
        raw_data = payload[pb_id]
        mapped_data = LightweightMatrixOutput.map_llm_extensions_to_domain(raw_data)
        existing_matrix = LightweightMatrixOutput.model_validate(mapped_data)

        pb_data = await deps.prompt_block_repo.get_prompt_block_by_id(pb_id)
        if not pb_data:
            continue
        pb_model = PromptBlock.model_validate(pb_data)

        scales = pb_model.scales
        if not scales:
            continue

        scale_values = [float(s.score) for s in scales]
        math_min = min(scale_values)
        math_max = max(scale_values)

        # Build scale mapping for atoms
        atom_to_scale = {}
        for scale in scales:
            s_val = float(scale.score)
            for claim in scale.claims:
                for tda in claim.tda_assertions or []:
                    atom_to_scale[tda.tda_id] = s_val

        # Re-aggregate stats from existing evaluated_atoms
        raw_stats = {s_val: {"hits": 0, "total": 0, "dlqs": 0} for s_val in scale_values}
        n_contested = 0
        infra_dlqs = 0  # Re-deriving infra_dlqs is impossible purely from atoms dict if they didn't even make it to evaluated_atoms, but we will count what we have.

        evaluated_atoms = existing_matrix.evaluated_atoms
        for atom_id, status in evaluated_atoms.items():
            if atom_id not in atom_to_scale:
                continue
            s_val = atom_to_scale[atom_id]
            raw_stats[s_val]["total"] += 1

            # Phase 2 requirement: Prioritize human_override if present in the raw atom dict
            effective_status = status

            # Epic 91.5: N/A items are mathematically excluded from the evaluation completely.
            if effective_status == "N_A":
                continue

            if effective_status == "DLQ":
                raw_stats[s_val]["dlqs"] += 1
            elif effective_status == "CONTESTED":
                raw_stats[s_val]["hits"] += 1
                n_contested += 1
            elif effective_status is True:
                raw_stats[s_val]["hits"] += 1

        global_total = sum(level_data["total"] for level_data in raw_stats.values())
        global_hits = sum(level_data["hits"] for level_data in raw_stats.values())
        global_dlqs = sum(level_data["dlqs"] for level_data in raw_stats.values())

        cognitive_collapse = n_contested > 3 or (global_total > 0 and (n_contested / global_total) > 0.5)
        is_indeterminate = global_total > 0 and (infra_dlqs / global_total) > 0.10
        if cognitive_collapse:
            is_indeterminate = True

        total_true_atoms += global_hits
        total_false_atoms += global_total - global_hits - global_dlqs

        justification = existing_matrix.justification or ""

        if is_indeterminate:
            raw_score = math_min
            formatted_breakdown = None
            xai_log = None
            if cognitive_collapse:
                justification = (
                    f"[INDETERMINATE] Matrix score invalidated because the cognitive collapse safety lock was triggered "
                    f"({n_contested} CONTESTED atoms exceeded thresholds)."
                )
            else:
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

            # Apply dynamic penalty here
            if raw_score is not None and n_contested > 0 and global_total > 0:
                penalty_factor = (n_contested / global_total) * 0.15
                raw_score = raw_score * (1.0 - penalty_factor)
                raw_score = max(raw_score, math_min)

                penalty_pct = penalty_factor * 100
                justification = f"[DYNAMIC PENALTY APPLIED: -{penalty_pct:.1f}% for CONTESTED atoms]\n{justification}"

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
