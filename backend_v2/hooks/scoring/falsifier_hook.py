"""Falsifier and security scoring hook logic."""

import logging
from collections.abc import Mapping
from typing import Annotated

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
from backend_v2.models.domain.inputs import DomainInputValue
from backend_v2.models.domain.scoring import StepFalsifierDTO, StepPanelDTO
from backend_v2.models.domain.security import InputProcessingOutputDTO, SanitizationResultDTO
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.trace import TraceScoringPayloadDTO
from backend_v2.models.state import StepOutputDTO

logger = logging.getLogger(__name__)

__all__ = [
    "MAX_TOTAL_PENALTY_RATIO",
    "ScoringPayloadWrapper",
    "StateInputWrapper",
    "_extract_payloads",
    "apply_scoring_logic_hook",
]

MAX_TOTAL_PENALTY_RATIO: float = 0.40

SCORING_PAYLOAD_KEYS: frozenset[str] = frozenset(
    {
        "sanitization_result",
        "step_input_processing",
        "step_falsifier",
        "step_panel",
        "_evaluative_matrices",
        "evaluative_matrices",
        "passivity_detected",
        "justification",
    }
)

STATE_INPUT_KEYS: frozenset[str] = frozenset(
    {
        "steps",
        "inputs",
        "raw_inputs",
        "passivity_detected",
        "_evaluative_matrices",
        "evaluative_matrices",
    }
)


class ScoringPayloadWrapper(V2CoreBase):
    """Wrapper for intermediate payload extraction during scoring logic execution."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, from_attributes=True)

    sanitization_result: SanitizationResultDTO | None = None
    step_input_processing: InputProcessingOutputDTO | None = None
    step_falsifier: StepFalsifierDTO | None = None
    step_panel: StepPanelDTO | None = None
    evaluative_matrices: Annotated[dict[str, float] | None, Field(default=None, alias="_evaluative_matrices")] = None
    passivity_detected: bool | None = None
    justification: str | None = None

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
                self.passivity_detected is not None,
                self.justification is not None,
            )
        )


class StateInputWrapper(V2CoreBase):
    """Wrapper for structured state inputs passed into the scoring context."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, from_attributes=True)

    steps: list[StepOutputDTO] | None = None
    inputs: ExecutionInputsDTO | None = None
    raw_inputs: ExecutionInputsDTO | None = None
    passivity_detected: bool | None = None
    evaluative_matrices: Annotated[dict[str, float] | None, Field(default=None, alias="_evaluative_matrices")] = None


def _extract_payloads(data: ExecutionInputsDTO | StateInputWrapper) -> list[ScoringPayloadWrapper]:
    """Strict Phase 9 Extractor. No V1 Fallbacks. No Naked Dict guessing.

    Args:
        data: The execution inputs DTO or StateInputWrapper representation.

    Returns:
        A list of strictly parsed ScoringPayloadWrapper objects.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if data validation fails.
    """
    payloads: list[ScoringPayloadWrapper] = []
    raw_source: Mapping[str, DomainInputValue] | None = None

    try:
        if isinstance(data, StateInputWrapper):
            hydrated_state = data
        else:
            raw_source = data.dynamic_inputs if data.dynamic_inputs else data.raw_inputs
            filtered_source: dict[str, DomainInputValue] = {}
            if isinstance(raw_source, Mapping):
                filtered_source = {k: v for k, v in raw_source.items() if k in STATE_INPUT_KEYS}
            hydrated_state = StateInputWrapper.model_validate(filtered_source)
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
                wrapper = ScoringPayloadWrapper.model_validate({"_evaluative_matrices": valid_dto.payload})
                payloads.append(wrapper)
                continue
            except ValidationError as e:
                msg = f"Strict Fail-Fast Enforced: Invalid StepOutputDTO '_evaluative_matrices' payload: {e}"
                logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                ) from e
        if isinstance(valid_dto.payload, Mapping) and SCORING_PAYLOAD_KEYS.isdisjoint(valid_dto.payload.keys()):
            continue
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

    if hydrated_state.evaluative_matrices:
        payloads.append(
            ScoringPayloadWrapper.model_validate({"_evaluative_matrices": hydrated_state.evaluative_matrices})
        )

    # Add explicitly injected top-level inputs
    for extra_inputs in [raw_source, hydrated_state.inputs, hydrated_state.raw_inputs]:
        if extra_inputs is not None:
            if isinstance(extra_inputs, ExecutionInputsDTO):
                candidate_dicts = [extra_inputs.raw_inputs, extra_inputs.dynamic_inputs]
            else:
                candidate_dicts = [extra_inputs]
            for extra_dict in candidate_dicts:
                if extra_dict:
                    if "_evaluative_matrices" in extra_dict:
                        try:
                            wrapper = ScoringPayloadWrapper.model_validate(
                                {"_evaluative_matrices": extra_dict["_evaluative_matrices"]}
                            )
                            payloads.append(wrapper)
                        except ValidationError as e:
                            msg = f"Strict Fail-Fast Enforced: Invalid top-level '_evaluative_matrices': {e}"
                            logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                            raise AppException(
                                message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                            ) from e
                    for k, val in extra_dict.items():
                        if k == "_evaluative_matrices":
                            continue
                        if isinstance(val, (str, int, float, bool, list)) or val is None:
                            continue
                        if (
                            k not in SCORING_PAYLOAD_KEYS
                            and isinstance(val, Mapping)
                            and SCORING_PAYLOAD_KEYS.isdisjoint(val.keys())
                        ):
                            continue
                        try:
                            wrapper = ScoringPayloadWrapper.model_validate(val)
                            if wrapper.has_scoring_data:
                                payloads.append(wrapper)
                        except ValidationError as e:
                            msg = f"Strict Fail-Fast Enforced: Invalid scoring payload for key '{k}': {e}"
                            logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                            raise AppException(
                                message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                            ) from e

    return payloads


def _extract_guard_flag(data: ExecutionInputsDTO | StateInputWrapper) -> bool | None:
    """Extracts the security threat flag from the guard output in the state.

    Iterates over the V2 execution snapshot to find the input processing result.
    Silent Fallback is BANNED. If the data is malformed, we raise an exception.

    Args:
        data: The execution inputs DTO or StateInputWrapper representation.

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


def _extract_falsifier_data(data: ExecutionInputsDTO | StateInputWrapper) -> FalsifierData | None:
    """Extracts falsifier data from either step_falsifier or step_panel outputs in V2 state.

    Iterates over the V2 execution snapshot. Silent Fallback is BANNED.

    Args:
        data: The execution inputs DTO or StateInputWrapper representation.

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


def _extract_passivity_flag(data: ExecutionInputsDTO | StateInputWrapper) -> bool:
    """Extracts passivity penalty detection flag from state snapshot or step payloads.

    Args:
        data: The execution inputs DTO or StateInputWrapper representation.

    Returns:
        bool: True if passivity penalty was detected, False otherwise.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if data validation fails.
    """
    for wrapper in _extract_payloads(data):
        if wrapper.passivity_detected is True:
            return True

    try:
        if isinstance(data, StateInputWrapper):
            hydrated_state = data
        else:
            raw_source = data.dynamic_inputs if data.dynamic_inputs else data.raw_inputs
            filtered_source: dict[str, DomainInputValue] = {}
            if isinstance(raw_source, Mapping):
                filtered_source = {k: v for k, v in raw_source.items() if k in STATE_INPUT_KEYS}
            hydrated_state = StateInputWrapper.model_validate(filtered_source)
        if hydrated_state.passivity_detected is True:
            return True
    except ValidationError as e:
        msg = f"Strict Fail-Fast Enforced: Invalid passivity detection state: {e}"
        logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(
            message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
        ) from e

    return False


@hook_registry.register(name="apply_scoring_logic")
async def apply_scoring_logic_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Workflow Data wrapper for apply_scoring_logic.

    Aggregates scores from Judge/Evaluation steps, applies penalties based on
    Workflow configuration, Security (Guard), Falsifier findings, and Passivity detection,
    and returns the strictly updated dict.

    Args:
        state: The execution state of the workflow step.
        deps: Dependency container with repositories.

    Returns:
        The hook execution result with state_delta containing updated scoring results.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if state data is invalid or missing,
            HOOK_EXECUTION_FAILED if dependencies are missing, or RESOURCE_NOT_FOUND if workflow is not found.
    """
    logger.debug("[ScoringHook] Calculating final scores...")

    if not state:
        msg = "Strict Fail-Fast Enforced: Missing HookState in apply_scoring_logic_hook."
        logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    if not deps or deps.workflow_repo is None:
        msg = "Strict Fail-Fast Enforced: Missing workflow_repo dependency in apply_scoring_logic_hook."
        logger.error("[ScoringHook] %s: %s", ErrorCodes.HOOK_EXECUTION_FAILED.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.HOOK_EXECUTION_FAILED.value})

    workflow_raw = await deps.workflow_repo.get_workflow_by_id(state.workflow_id)
    if workflow_raw is None:
        msg = f"Strict Fail-Fast Enforced: Workflow not found for ID '{state.workflow_id}'."
        logger.error("[ScoringHook] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value})

    if isinstance(workflow_raw, Workflow):
        workflow = workflow_raw
    else:
        workflow = Workflow.model_validate(workflow_raw, strict=False)

    # 1. Security Penalty Check (Guard)
    security_threat = _extract_guard_flag(state.inputs)

    # 2. Falsifier Penalty Check
    falsifier_data = _extract_falsifier_data(state.inputs)
    is_post_hoc = _calculate_falsifier_penalty(falsifier_data)

    # 3. Passivity Penalty Check
    passivity_detected = _extract_passivity_flag(state.inputs)

    penalties: list[str] = []
    total_penalty = 0.0

    if security_threat:
        total_penalty += workflow.security_penalty
        if workflow.security_penalty > 0:
            pct = int(round(workflow.security_penalty * 100))
            token = f"PENALTY_SECURITY:{pct}"
        else:
            token = "PENALTY_SECURITY"
        penalties.append(token)
        logger.warning("[ScoringHook] Security threat detected; recorded %s observation token.", token)

    if is_post_hoc:
        total_penalty += workflow.post_hoc_penalty
        if workflow.post_hoc_penalty > 0:
            pct = int(round(workflow.post_hoc_penalty * 100))
            token = f"PENALTY_POST_HOC:{pct}"
        else:
            token = "PENALTY_POST_HOC"
        penalties.append(token)
        logger.warning("[ScoringHook] Post-hoc rationalization detected; recorded %s observation token.", token)

    if passivity_detected:
        total_penalty += workflow.passivity_penalty
        if workflow.passivity_penalty > 0:
            pct = int(round(workflow.passivity_penalty * 100))
            token = f"PENALTY_PASSIVITY:{pct}"
        else:
            token = "PENALTY_PASSIVITY"
        penalties.append(token)
        logger.warning("[ScoringHook] Passivity detected; recorded %s observation token.", token)

    total_score_accum = 0.0
    count = 0
    scores_found = []

    unique_matrices: dict[str, float] = {}

    def _extract_scores(source: ScoringPayloadWrapper) -> None:
        if source.evaluative_matrices:
            for block_id, norm_val in source.evaluative_matrices.items():
                unique_matrices[block_id] = float(norm_val)

    extracted_payloads = _extract_payloads(state.inputs)
    for wrapper in extracted_payloads:
        _extract_scores(wrapper)

    for v_float in unique_matrices.values():
        total_score_accum += v_float
        count += 1
        scores_found.append(v_float)

    if count == 0:
        is_valid_indeterminate = any(
            p.justification is not None and "[INDETERMINATE]" in p.justification for p in extracted_payloads
        )

        if is_valid_indeterminate:
            logger.warning("[ScoringHook] All matrices are INDETERMINATE. Skipping aggregation.")
            indet_dto = TraceScoringPayloadDTO(
                total_score=None,
                final_score=None,
                penalties_applied=penalties,
                aggregation_status="INDETERMINATE - Cognitive Collapse / Quality Check Failed",
            )
            return HookResult(
                success=True,
                state_delta=HookDeltaDTO(delta=indet_dto),
            )

        msg = (
            "Strict Fail-Fast Enforced: '_evaluative_matrices' missing from state. "
            "Matrix normalization failed or was bypassed."
        )
        logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
    else:
        average_score = total_score_accum / count

    # 4. Phase 1 Sovereign Execution Penalty Deduction
    effective_penalty = min(total_penalty, MAX_TOTAL_PENALTY_RATIO)
    final_score = round(max(0.0, average_score * (1.0 - effective_penalty)), 1)

    # 5. Create Result with TraceScoringPayloadDTO
    score_dto = TraceScoringPayloadDTO(
        total_score=final_score,
        final_score=final_score,
        penalties_applied=penalties,
        aggregation_status=f"V2 Commensurate Average of {count} matrices",
    )

    logger.info(
        "[ScoringHook] Scoring validation complete. Commensurate Base Average: %.1f, "
        "Final: %.1f. Penalties: %d (Effective: %.2f)",
        average_score,
        final_score,
        len(penalties),
        effective_penalty,
    )
    return HookResult(
        success=True,
        state_delta=HookDeltaDTO(delta=score_dto),
    )
