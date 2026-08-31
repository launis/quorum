"""Falsifier and security scoring hook logic."""

import logging
from typing import Annotated, Any

from pydantic import ConfigDict, Field, TypeAdapter, ValidationError

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    HookDeltaDTO,
    HookDependencies,
    HookResult,
    HookState,
    hook_registry,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.falsifier import FalsifierData
from backend_v2.models.domain.scoring import StepFalsifierDTO, StepPanelDTO
from backend_v2.models.domain.security import InputProcessingOutputDTO, SanitizationResultDTO
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.enums import ScoringCalibrationThresholds
from backend_v2.models.state import StepOutputDTO
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

__all__ = [
    "ScoringPayloadWrapper",
    "StateInputWrapper",
    "_extract_payloads",
    "apply_scoring_logic_hook",
]


class ScoringPayloadWrapper(V2CoreBase):
    """Wrapper for intermediate payload extraction during scoring logic execution."""

    model_config = ConfigDict(strict=True, extra="ignore", frozen=True)

    sanitization_result: SanitizationResultDTO | None = None
    step_input_processing: InputProcessingOutputDTO | None = None
    step_falsifier: StepFalsifierDTO | None = None
    step_panel: StepPanelDTO | None = None
    evaluative_matrices: Annotated[dict[str, float] | None, Field(alias="_evaluative_matrices")] = None

    @property
    def has_scoring_data(self) -> bool:
        """Returns True if at least one scoring payload field is present."""
        return any(
            (
                self.sanitization_result is not None,
                self.step_input_processing is not None,
                self.step_falsifier is not None,
                self.step_panel is not None,
                self.evaluative_matrices is not None,
            )
        )


class StateInputWrapper(V2CoreBase):
    """Wrapper for structured state inputs passed into the scoring context."""

    model_config = ConfigDict(strict=True, extra="ignore", frozen=True)

    steps: list[StepOutputDTO] | None = None
    inputs: ExecutionInputsDTO | dict[str, Any] | None = None
    raw_inputs: ExecutionInputsDTO | dict[str, Any] | None = None


def _extract_payloads(data: ExecutionInputsDTO | dict[str, Any]) -> list[ScoringPayloadWrapper]:
    """Strict Phase 9 Extractor. No V1 Fallbacks. No Naked Dict guessing.

    Args:
        data: The execution inputs DTO or dictionary representation.

    Returns:
        A list of strictly parsed ScoringPayloadWrapper objects.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if data validation fails.
    """
    payloads: list[ScoringPayloadWrapper] = []

    try:
        hydrated_state = (
            data
            if isinstance(data, StateInputWrapper)
            else StateInputWrapper.model_validate(data.raw_inputs if isinstance(data, ExecutionInputsDTO) else data)
        )
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
        if isinstance(valid_dto.payload, (str, int, float, bool, list)):
            continue
        if valid_dto.block_id == "_evaluative_matrices":
            try:
                eval_map = TypeAdapter(dict[str, float]).validate_python(valid_dto.payload)
                payloads.append(ScoringPayloadWrapper.model_validate({"_evaluative_matrices": eval_map}))
                continue
            except ValidationError:
                pass
        try:
            wrapper = ScoringPayloadWrapper.model_validate(valid_dto.payload)
            if wrapper.has_scoring_data:
                payloads.append(wrapper)
        except ValidationError as e:
            msg = f"Strict Fail-Fast Enforced: Invalid StepOutputDTO payload in execution snapshot: {e}"
            logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
            ) from e

    # Add explicitly injected top-level inputs
    for extra_inputs in [hydrated_state.inputs, hydrated_state.raw_inputs]:
        if extra_inputs is not None:
            candidate_dicts = (
                [extra_inputs.raw_inputs, extra_inputs.dynamic_inputs]
                if isinstance(extra_inputs, ExecutionInputsDTO)
                else [extra_inputs]
            )
            for extra_dict in candidate_dicts:
                if extra_dict:
                    if "_evaluative_matrices" in extra_dict:
                        try:
                            eval_map = TypeAdapter(dict[str, float]).validate_python(extra_dict["_evaluative_matrices"])
                            payloads.append(ScoringPayloadWrapper.model_validate({"_evaluative_matrices": eval_map}))
                        except ValidationError:
                            pass
                    try:
                        wrapper = ScoringPayloadWrapper.model_validate(extra_dict)
                        payloads.append(wrapper)
                    except ValidationError as e:
                        logger.debug("[ScoringHook] Extra dict skipped (not a ScoringPayloadWrapper): %s", e)

    return payloads


def _extract_guard_flag(data: ExecutionInputsDTO | dict[str, Any]) -> bool | None:
    """Extracts the security threat flag from the guard output in the state.

    Iterates over the V2 execution snapshot to find the input processing result.
    Silent Fallback is BANNED. If the data is malformed, we raise an exception.

    Args:
        data: The execution inputs DTO or dictionary representation.

    Returns:
        Boolean indicating if a threat was detected, or None if guard data is missing.
    """
    for wrapper in _extract_payloads(data):
        if wrapper.step_input_processing and wrapper.step_input_processing.security_check:
            return wrapper.step_input_processing.security_check.threat_detected
        elif wrapper.sanitization_result:
            return wrapper.sanitization_result.threat_detected

    logger.info("[ScoringHook] security_check (Input Processing data) missing from state. Security step bypassed.")
    return None


def _extract_falsifier_data(data: ExecutionInputsDTO | dict[str, Any]) -> FalsifierData | None:
    """Extracts falsifier data from either step_falsifier or step_panel outputs in V2 state.

    Iterates over the V2 execution snapshot. Silent Fallback is BANNED.

    Args:
        data: The execution inputs DTO or dictionary representation.

    Returns:
        FalsifierData if present, or None if falsifier data is missing.
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
        falsifier_data: The strictly typed falsifier data.

    Returns:
        bool: True if post-hoc rationalization is detected, False otherwise.
    """
    if falsifier_data:
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

    lookup_ctx = state.inputs.dynamic_inputs if state.inputs.dynamic_inputs else state.inputs.raw_inputs

    # 1. Security Penalty Check (Guard)
    security_threat = _extract_guard_flag(lookup_ctx)

    # 2. Falsifier Penalty Check
    falsifier_data = _extract_falsifier_data(lookup_ctx)
    is_post_hoc = _calculate_falsifier_penalty(falsifier_data)
    penalties: list[str] = []

    total_score_accum = 0.0
    count = 0
    scores_found = []

    unique_matrices: dict[str, float] = {}

    def _extract_scores(source: ScoringPayloadWrapper) -> None:
        if source.evaluative_matrices:
            for block_id, norm_val in source.evaluative_matrices.items():
                unique_matrices[block_id] = float(norm_val)

    for wrapper in _extract_payloads(lookup_ctx):
        _extract_scores(wrapper)

    for v_float in unique_matrices.values():
        total_score_accum += v_float
        count += 1
        scores_found.append(v_float)

    if count == 0:
        is_valid_indeterminate = False
        for _, v in lookup_ctx.items():
            try:
                matrix_out = LightweightMatrixOutput.model_validate(v)
                if matrix_out.justification and "[INDETERMINATE]" in matrix_out.justification:
                    is_valid_indeterminate = True
                    break
            except ValidationError:
                continue

        if is_valid_indeterminate:
            logger.warning("[ScoringHook] All matrices are INDETERMINATE. Skipping aggregation.")
            indet_result = {
                "total_score": None,
                "final_score": None,
                "penalties_applied": penalties,
                "aggregation_status": "INDETERMINATE - Cognitive Collapse / Quality Check Failed",
            }
            return HookResult(success=True, state_delta=HookDeltaDTO(delta={"scoring_result": indet_result}))

        msg = (
            "Strict Fail-Fast Enforced: '_evaluative_matrices' missing from state. "
            "Matrix normalization failed or was bypassed."
        )
        logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
    else:
        average_score = total_score_accum / count

    # 4. Apply Penalties
    settings = get_settings()

    final_score = average_score
    total_penalty_factor = 0.0

    if security_threat:
        p_val = settings.scoring_security_penalty
        if p_val > 0:
            total_penalty_factor += p_val
            pct_val = p_val * 100
            penalties.append(f"PENALTY_SECURITY:{pct_val:.0f}")
        else:
            logger.warning("[ScoringHook] Security Threat Detected (Logged Only - Penalty Disabled in Settings)")

    if is_post_hoc:
        p_val = settings.scoring_post_hoc_penalty
        if p_val > 0:
            total_penalty_factor += p_val
            pct_val = p_val * 100
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
    return HookResult(success=True, state_delta=HookDeltaDTO(delta={"scoring_result": result}))
