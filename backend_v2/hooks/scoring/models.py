"""Temporary DTO models for scoring hook decomposition.

Note: Mandatory sunset in Sub-Phase 3B per Epic 149 specifications.
"""

import logging
from typing import Annotated, Any

from pydantic import ConfigDict, Field, ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.scoring import StepFalsifierDTO, StepPanelDTO
from backend_v2.models.domain.security import InputProcessingOutputDTO, SanitizationResultDTO
from backend_v2.models.state import StepOutputDTO

logger = logging.getLogger(__name__)

__all__ = [
    "ScoringPayloadWrapper",
    "StateInputWrapper",
    "_extract_payloads",
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
