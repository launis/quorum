import logging
from typing import Annotated, Any

from pydantic import ConfigDict, Field, ValidationError

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

    model_config = ConfigDict(extra="ignore", frozen=True)

    sanitization_result: SanitizationResultDTO | None = None
    step_input_processing: InputProcessingOutputDTO | None = None
    step_falsifier: StepFalsifierDTO | None = None
    step_panel: StepPanelDTO | None = None
    evaluative_matrices: Annotated[dict[str, float] | None, Field(alias="_evaluative_matrices")] = None


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

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if data validation fails.
    """
    payloads: list[ScoringPayloadWrapper] = []

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
        if extra_dict is not None:
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

    Args:
        data: The dictionary representation of the hook inputs or global context.

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


def _extract_falsifier_data(data: dict[str, Any]) -> FalsifierData | None:
    """Extracts falsifier data from either step_falsifier or step_panel outputs in V2 state.

    Iterates over the V2 execution snapshot. Silent Fallback is BANNED.

    Args:
        data: The dictionary representation of the hook inputs or global context.

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

    lookup_ctx = (
        state.inputs.raw_inputs
        if isinstance(state.inputs, ExecutionInputsDTO)
        else (state.inputs if isinstance(state.inputs, dict) else {})
    )

    # 1. Security Penalty Check (Guard)
    security_threat = _extract_guard_flag(lookup_ctx)

    # 2. Falsifier Penalty Check
    falsifier_data = _extract_falsifier_data(lookup_ctx)
    is_post_hoc = _calculate_falsifier_penalty(falsifier_data)
    penalties: list[str] = []

    total_score_accum = 0.0
    count = 0
    scores_found = []

    candidates = [lookup_ctx]
    unique_matrices: dict[str, float] = {}

    def _extract_scores(source: ScoringPayloadWrapper) -> None:
        if source.evaluative_matrices:
            for block_id, norm_val in source.evaluative_matrices.items():
                unique_matrices[block_id] = float(norm_val)

    for item in candidates:
        if isinstance(item, dict):
            for wrapper in _extract_payloads(item):
                _extract_scores(wrapper)

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
        is_valid_indeterminate = False
        for _, v in lookup_ctx.items():
            if isinstance(v, dict) and "justification" in v and "[INDETERMINATE]" in str(v["justification"]):
                is_valid_indeterminate = True
                break

        if not is_valid_indeterminate and "steps" in lookup_ctx and isinstance(lookup_ctx["steps"], list):
            for step_val in lookup_ctx["steps"]:
                if isinstance(step_val, StepOutputDTO):
                    payload = step_val.payload
                elif isinstance(step_val, dict) and "payload" in step_val:
                    payload = step_val["payload"]
                else:
                    payload = None

                if isinstance(payload, dict):
                    for _, v in payload.items():
                        if (
                            isinstance(v, dict)
                            and "justification" in v
                            and "[INDETERMINATE]" in str(v["justification"])
                        ):
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
