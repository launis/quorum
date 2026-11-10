"""Falsifier and security scoring hook logic."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, ValidationError

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
from backend_v2.models.domain.security import InputProcessingOutputDTO
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.global_context import GlobalContextVarsDTO
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
    """Wrapper for intermediate payload extraction during scoring logic execution.

    Attributes:
        step_input_processing: Optional input security processing output DTO.
        step_falsifier: Optional step falsifier output DTO.
        step_panel: Optional step panel output DTO.
        evaluative_matrices: Optional mapping of matrix block IDs to normalized scores.
        passivity_detected: Optional flag indicating passivity penalty detection.
        justification: Optional textual justification for matrix evaluation.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, from_attributes=True)

    step_input_processing: InputProcessingOutputDTO | None = None
    step_falsifier: StepFalsifierDTO | None = None
    step_panel: StepPanelDTO | None = None
    evaluative_matrices: Annotated[dict[str, float] | None, Field(default=None, alias="_evaluative_matrices")] = None
    passivity_detected: bool | None = None
    justification: str | None = None

    @property
    def has_scoring_data(self) -> bool:
        """Checks whether at least one scoring payload field is populated.

        Returns:
            True if at least one scoring payload field is present, False otherwise.
        """
        return any(
            (
                self.step_input_processing is not None,
                self.step_falsifier is not None,
                self.step_panel is not None,
                self.evaluative_matrices is not None,
                self.passivity_detected is not None,
                self.justification is not None,
            )
        )


class StateInputWrapper(V2CoreBase):
    """Wrapper for structured state inputs passed into the scoring context.

    Attributes:
        steps: Optional list of executed step output DTOs.
        inputs: Optional execution inputs DTO.
        raw_inputs: Optional raw execution inputs DTO.
        passivity_detected: Optional top-level passivity detection flag.
        evaluative_matrices: Optional top-level mapping of matrix block IDs to scores.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, from_attributes=True)

    steps: list[StepOutputDTO] | None = None
    inputs: ExecutionInputsDTO | None = None
    raw_inputs: ExecutionInputsDTO | None = None
    passivity_detected: bool | None = None
    evaluative_matrices: Annotated[dict[str, float] | None, Field(default=None, alias="_evaluative_matrices")] = None


def _resolve_state_input_wrapper(
    data: ExecutionInputsDTO | StateInputWrapper,
    error_context: str,
) -> tuple[StateInputWrapper, Mapping[str, DomainInputValue] | None]:
    """Hydrates a StateInputWrapper and raw source mapping from execution inputs.

    Args:
        data: The execution inputs DTO or StateInputWrapper representation.
        error_context: Contextual message prefix for validation errors.

    Returns:
        A 2-tuple of the hydrated StateInputWrapper and optional raw source mapping.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if state input validation fails.
    """
    if isinstance(data, StateInputWrapper):
        return data, None

    raw_source: Mapping[str, DomainInputValue] | None = data.dynamic_inputs if data.dynamic_inputs else data.raw_inputs
    filtered_source: dict[str, DomainInputValue] = {}
    if not isinstance(raw_source, (str, int, float, bool, list)) and raw_source is not None:
        filtered_source = {k: v for k, v in raw_source.items() if k in STATE_INPUT_KEYS}
    try:
        return StateInputWrapper.model_validate(filtered_source), raw_source
    except ValidationError as e:
        msg = f"Strict Fail-Fast Enforced: {error_context}: {e}"
        logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
        raise AppException(
            message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
        ) from e


def _validate_scoring_payload_wrapper(raw_payload: object, error_context: str) -> ScoringPayloadWrapper:
    """Validates a raw payload object into a ScoringPayloadWrapper.

    Args:
        raw_payload: Candidate payload dictionary or model to validate.
        error_context: Contextual description for validation failure reporting.

    Returns:
        The validated ScoringPayloadWrapper instance.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if payload validation fails.
    """
    try:
        return ScoringPayloadWrapper.model_validate(raw_payload)
    except ValidationError as e:
        msg = f"Strict Fail-Fast Enforced: {error_context}: {e}"
        logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
        raise AppException(
            message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
        ) from e


def _extract_payloads(data: ExecutionInputsDTO | StateInputWrapper) -> list[ScoringPayloadWrapper]:
    """Extracts and validates scoring payloads from execution inputs or state wrappers.

    Args:
        data: The execution inputs DTO or StateInputWrapper representation.

    Returns:
        A list of strictly parsed ScoringPayloadWrapper objects.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if data validation fails.
    """
    payloads: list[ScoringPayloadWrapper] = []
    hydrated_state, raw_source = _resolve_state_input_wrapper(data, "Execution snapshot validation failed")

    if hydrated_state.steps is None:
        msg = "Strict Fail-Fast Enforced: Execution snapshot 'steps' missing."
        logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    for valid_dto in hydrated_state.steps:
        if valid_dto.payload is None or isinstance(valid_dto.payload, (str, int, float, bool, list)):
            continue
        if valid_dto.block_id == "_evaluative_matrices":
            wrapper = _validate_scoring_payload_wrapper(
                {"_evaluative_matrices": valid_dto.payload},
                "Invalid StepOutputDTO '_evaluative_matrices' payload",
            )
            payloads.append(wrapper)
            continue
        payload_keys = (
            valid_dto.payload.model_fields.keys()
            if isinstance(valid_dto.payload, BaseModel)
            else set(valid_dto.payload)
        )
        if SCORING_PAYLOAD_KEYS.isdisjoint(payload_keys):
            continue
        wrapper = _validate_scoring_payload_wrapper(
            valid_dto.payload,
            "Invalid StepOutputDTO payload in execution snapshot",
        )
        if wrapper.has_scoring_data:
            payloads.append(wrapper)

    if hydrated_state.evaluative_matrices:
        payloads.append(
            ScoringPayloadWrapper.model_validate({"_evaluative_matrices": hydrated_state.evaluative_matrices})
        )

    for extra_inputs in (raw_source, hydrated_state.inputs, hydrated_state.raw_inputs):
        if extra_inputs is None:
            continue
        if isinstance(extra_inputs, ExecutionInputsDTO):
            candidate_dicts = [extra_inputs.raw_inputs, extra_inputs.dynamic_inputs]
        else:
            candidate_dicts = [extra_inputs]
        for extra_dict in candidate_dicts:
            if not extra_dict:
                continue
            if "_evaluative_matrices" in extra_dict:
                wrapper = _validate_scoring_payload_wrapper(
                    {"_evaluative_matrices": extra_dict["_evaluative_matrices"]},
                    "Invalid top-level '_evaluative_matrices'",
                )
                payloads.append(wrapper)
            for k, val in extra_dict.items():
                if k == "_evaluative_matrices" or val is None or isinstance(val, (str, int, float, bool, list)):
                    continue
                if k not in SCORING_PAYLOAD_KEYS:
                    val_keys = val.model_fields.keys() if isinstance(val, BaseModel) else set(val)
                    if SCORING_PAYLOAD_KEYS.isdisjoint(val_keys):
                        continue
                wrapper = _validate_scoring_payload_wrapper(
                    val,
                    f"Invalid scoring payload for key '{k}'",
                )
                if wrapper.has_scoring_data:
                    payloads.append(wrapper)

    return payloads


def _extract_guard_flag(
    data: ExecutionInputsDTO | StateInputWrapper,
    global_context_vars: GlobalContextVarsDTO | None = None,
) -> bool | None:
    """Extracts the security threat flag from the guard output in the state.

    Args:
        data: The execution inputs DTO or StateInputWrapper representation.
        global_context_vars: Optional global context variables DTO.

    Returns:
        Boolean indicating if a threat was detected, or None if guard data is missing.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if state payload validation fails.
    """
    for wrapper in _extract_payloads(data):
        if wrapper.step_input_processing and wrapper.step_input_processing.security_check:
            return wrapper.step_input_processing.security_check.threat_detected

    logger.info("[ScoringHook] security_check (Input Processing data) missing from state. Security step bypassed.")
    return None


def _extract_falsifier_data(data: ExecutionInputsDTO | StateInputWrapper) -> FalsifierData | None:
    """Extracts falsifier data from step_falsifier or step_panel outputs in execution state.

    Args:
        data: The execution inputs DTO or StateInputWrapper representation.

    Returns:
        FalsifierData if present, or None if falsifier data is missing.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if state payload validation fails.
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
        True if post-hoc rationalization is detected, False otherwise.
    """
    if falsifier_data and falsifier_data.fidelity_audit and falsifier_data.fidelity_audit.post_hoc_rationalization:
        return True
    return False


def _extract_passivity_flag(
    data: ExecutionInputsDTO | StateInputWrapper,
    global_context_vars: GlobalContextVarsDTO | None = None,
) -> bool:
    """Extracts passivity penalty detection flag from state snapshot, global context, or step payloads.

    Args:
        data: The execution inputs DTO or StateInputWrapper representation.
        global_context_vars: Optional global context variables DTO.

    Returns:
        True if passivity penalty was detected, False otherwise.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if data validation fails.
    """
    if global_context_vars and global_context_vars.passivity_detected is True:
        return True

    for wrapper in _extract_payloads(data):
        if wrapper.passivity_detected is True:
            return True

    hydrated_state, _ = _resolve_state_input_wrapper(data, "Invalid passivity detection state")
    return hydrated_state.passivity_detected is True


def _format_penalty_token(prefix: str, penalty_ratio: float) -> str:
    """Formats a penalty observation token with an optional integer percentage suffix.

    Args:
        prefix: Canonical penalty token prefix.
        penalty_ratio: Configured penalty weight ratio on the workflow.

    Returns:
        Formatted penalty token string.
    """
    if penalty_ratio > 0:
        pct = int(round(penalty_ratio * 100))
        return f"{prefix}:{pct}"
    return prefix


@hook_registry.register(name="apply_scoring_logic")
async def apply_scoring_logic_hook(state: HookState | None, deps: HookDependencies) -> HookResult:
    """Aggregates normalized matrix scores and applies workflow-configured penalties.

    Aggregates scores from evaluation steps, applies penalties based on
    Workflow configuration, Security (Guard), Falsifier findings, and Passivity detection,
    and returns the resulting TraceScoringPayloadDTO delta.

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
        logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    if not deps or deps.workflow_repo is None:
        msg = "Strict Fail-Fast Enforced: Missing workflow_repo dependency in apply_scoring_logic_hook."
        logger.error("[ScoringHook] %s: %s", ErrorCodes.HOOK_EXECUTION_FAILED.name, msg, exc_info=True)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.HOOK_EXECUTION_FAILED.value})

    workflow: Workflow | None = await deps.workflow_repo.get_workflow_by_id(state.workflow_id)
    if workflow is None:
        msg = f"Strict Fail-Fast Enforced: Workflow not found for ID '{state.workflow_id}'."
        logger.error("[ScoringHook] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg, exc_info=True)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value})

    security_threat = _extract_guard_flag(state.inputs, state.global_context_vars)
    falsifier_data = _extract_falsifier_data(state.inputs)
    is_post_hoc = _calculate_falsifier_penalty(falsifier_data)
    passivity_detected = _extract_passivity_flag(state.inputs, state.global_context_vars)

    penalties: list[str] = []
    total_penalty = 0.0

    if security_threat:
        total_penalty += workflow.security_penalty
        token = _format_penalty_token("PENALTY_SECURITY", workflow.security_penalty)
        penalties.append(token)
        logger.warning("[ScoringHook] Security threat detected; recorded %s observation token.", token)

    if is_post_hoc:
        total_penalty += workflow.post_hoc_penalty
        token = _format_penalty_token("PENALTY_POST_HOC", workflow.post_hoc_penalty)
        penalties.append(token)
        logger.warning("[ScoringHook] Post-hoc rationalization detected; recorded %s observation token.", token)

    if passivity_detected:
        total_penalty += workflow.passivity_penalty
        token = _format_penalty_token("PENALTY_PASSIVITY", workflow.passivity_penalty)
        penalties.append(token)
        logger.warning("[ScoringHook] Passivity detected; recorded %s observation token.", token)

    unique_matrices: dict[str, float] = {}

    if state.global_context_vars and state.global_context_vars.evaluative_matrices:
        for block_id, norm_val in state.global_context_vars.evaluative_matrices.items():
            unique_matrices[block_id] = float(norm_val)

    extracted_payloads = _extract_payloads(state.inputs)
    for wrapper in extracted_payloads:
        if wrapper.evaluative_matrices:
            for block_id, norm_val in wrapper.evaluative_matrices.items():
                unique_matrices[block_id] = float(norm_val)

    total_score_accum = sum(unique_matrices.values())
    count = len(unique_matrices)

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
        logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    average_score = total_score_accum / count
    effective_penalty = min(total_penalty, MAX_TOTAL_PENALTY_RATIO)
    final_score = round(max(0.0, average_score * (1.0 - effective_penalty)), 1)

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
