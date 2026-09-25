from __future__ import annotations

"""Context Router for dynamic UI-driven state pruning.

This module isolates UI-driven routing, step-to-step variable normalization,
and data culling/pruning logic matching the Phase 9 architecture standards.
"""

import logging
from collections.abc import Mapping, Sequence
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from backend_v2.exceptions import (
    AppException,
    ConfigurationError,
    ErrorCodes,
    MissingRoutingModeError,
)
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput, OutputProfileConfig
from backend_v2.models.state import StepOutputDTO

__all__ = [
    "ContextRouter",
    "RoutingModeConfig",
]

logger = logging.getLogger(__name__)


class RoutingModeConfig(BaseModel):
    """Pydantic model for validating routing configurations strictly.

    Attributes:
        routing_mode: The routing behavior configuration string.
        target: Optional destination key or path.
        source: Optional source key or path.
        description: Optional routing description.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
    routing_mode: Annotated[str, Field(description="The routing behavior configuration string.")]
    target: Annotated[str | None, Field(default=None, description="Optional destination key or path.")] = None
    source: Annotated[str | None, Field(default=None, description="Optional source key or path.")] = None
    description: Annotated[str | None, Field(default=None, description="Optional routing description.")] = None


class ContextRouter:
    """Isolates UI-driven routing and data culling logic conforming to Phase 9 directives."""

    @staticmethod
    def route_and_prune(
        trace_event: LightweightMatrixOutput, output_profile: OutputProfileConfig | None
    ) -> LightweightMatrixOutput:
        """Extracts strictly what the UI demands from the execution trace.

        Args:
            trace_event: Validated matrix output model.
            output_profile: The UI-defined output profile specifying required extensions.

        Returns:
            A LightweightMatrixOutput containing only the requested pruned data.
        """
        if not isinstance(trace_event, LightweightMatrixOutput):
            logger.error(
                "Invalid trace_event provided to route_and_prune. Expected LightweightMatrixOutput, got %s.",
                type(trace_event).__name__,
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )
            raise ConfigurationError(
                f"Missing required base field or invalid trace event type: expected LightweightMatrixOutput, got {type(trace_event).__name__}"
            )

        extensions_extracted: dict[Any, Any] = {}
        if output_profile:
            for ext in output_profile.visible_block_extensions:
                # If block explicitly defines supported extensions, check suitability
                if trace_event.allowed_extensions is not None and ext not in trace_event.allowed_extensions:
                    continue
                if ext in trace_event.extensions:
                    extensions_extracted[ext] = trace_event.extensions[ext]
                else:
                    logger.debug("Missing XAI extension: %s. Skipping and omitting from trace.", ext)
                    continue

        return LightweightMatrixOutput(
            raw_score=trace_event.raw_score,
            normalized_score=trace_event.normalized_score,
            level_breakdown=trace_event.level_breakdown,
            justification=trace_event.justification,
            evaluated_atoms=trace_event.evaluated_atoms,
            extensions=extensions_extracted,
        )

    @staticmethod
    def validate_routing_mode(mapping_path: str, mapping_config: Any) -> str:
        """Ensures that step-to-step mappings have a strict routing mode defined.

        Args:
            mapping_path: The dot-notation path being mapped.
            mapping_config: The configuration dictionary for this mapping.

        Returns:
            The routing mode string.

        Raises:
            MissingRoutingModeError: If routing_mode is not present.
        """
        try:
            config = RoutingModeConfig.model_validate(mapping_config)
            return config.routing_mode
        except ValidationError as e:
            logger.error(
                "RoutingMode validation failed for path %s.",
                mapping_path,
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                exc_info=True,
            )
            raise MissingRoutingModeError(mapping_path=mapping_path) from e

    @staticmethod
    def normalize_and_validate_variable(path: str, steps: Sequence[StepOutputDTO]) -> str:
        """Validates dynamic variables (Fail-Fast) and strictly forbids legacy V1 paths.

        Enforces strict V2 nomenclature: No implicit stripping of '.output'.

        Args:
            path: The variable reference path (e.g. $steps.step_1).
            steps: The sequence of executed StepOutputDTO objects.

        Returns:
            The normalized path string if validated successfully.

        Raises:
            AppException: If step is not found or legacy V1 '.output' notation is used.
        """
        if not path:
            return path

        if path.startswith("$"):
            clean_path = path[1:]
        else:
            clean_path = path

        if clean_path.startswith("steps."):
            if not isinstance(steps, Sequence) or isinstance(steps, (str, bytes, Mapping)):
                msg = "Fail-Fast: Snapshot validation failed. Must match sequence of StepOutputDTO."
                logger.error(msg, extra={"error_code": ErrorCodes.VALIDATION_FAILED.value})
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

            for item in steps:
                if not isinstance(item, StepOutputDTO):
                    msg = "Fail-Fast: Snapshot validation failed. Items must be StepOutputDTO."
                    logger.error(msg, extra={"error_code": ErrorCodes.VALIDATION_FAILED.value})
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    )

            parts = clean_path.split(".")
            if len(parts) >= 2:
                step_key = parts[1]

                found = any(dto.step_id == step_key for dto in steps)
                if not found:
                    msg = f"Fail-Fast: Required step '{step_key}' not found in state (Orphaned Step)."
                    logger.error(msg, extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value})
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
                    )

                # STRICT V2 MANDATE: Explicitly reject legacy V1 `.output` notation.
                # All inputs must use the exact V2 format (e.g. $steps.step_1) without wrappers.
                if len(parts) >= 3 and parts[2] == "output":
                    msg = (
                        "Fail-Fast: Legacy V1 '.output' variable format is strictly forbidden. "
                        f"Update the UI mapping to use strict V2 format (e.g. $steps.{step_key})."
                    )
                    logger.error(msg, extra={"error_code": ErrorCodes.VALIDATION_FAILED.value})
                    raise AppException(
                        message=msg,
                        status_code=400,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    )

        return path
