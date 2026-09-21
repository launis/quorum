from __future__ import annotations

"""Context Router for dynamic UI-driven state pruning.

This module isolates UI-driven routing, step-to-step variable normalization,
and data culling/pruning logic matching the Phase 9 architecture standards.
"""

import logging
from collections.abc import Mapping
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from backend_v2.exceptions import (
    AppException,
    ConfigurationError,
    ErrorCodes,
    MissingRoutingModeError,
)
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput, OutputProfileConfig

__all__ = [
    "ContextRouter",
    "RoutingModeConfig",
    "SnapshotState",
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


class SnapshotState(BaseModel):
    """Pydantic model to encapsulate execution state snapshots without using naked dicts.

    Attributes:
        steps: Optional list of executed step data.
        raw_inputs: Optional dictionary representing starting inputs.
        inputs: Optional dynamic inputs structure.
        metadata: Optional execution metadata.
        global_context_vars: Optional global context variables.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
    steps: Annotated[list[Any] | None, Field(default=None, description="Optional list of executed step data.")] = None
    raw_inputs: Annotated[
        dict[str, Any] | None, Field(default=None, description="Optional dictionary representing starting inputs.")
    ] = None
    inputs: Annotated[Any | None, Field(default=None, description="Optional dynamic inputs structure.")] = None
    metadata: Annotated[Any | None, Field(default=None, description="Optional execution metadata.")] = None
    global_context_vars: Annotated[
        Any | None, Field(default=None, description="Optional global context variables.")
    ] = None


class ContextRouter:
    """Isolates UI-driven routing and data culling logic conforming to Phase 9 directives."""

    @staticmethod
    def route_and_prune(trace_event: Any, output_profile: OutputProfileConfig | None) -> LightweightMatrixOutput:
        """Extracts strictly what the UI demands from the execution trace.

        Args:
            trace_event: The full execution state dictionary or validated matrix output.
            output_profile: The UI-defined output profile specifying required extensions.

        Returns:
            A LightweightMatrixOutput containing only the requested pruned data.

        Raises:
            ConfigurationError: If trace event validation fails structurally or has missing base fields.
        """
        try:
            if isinstance(trace_event, LightweightMatrixOutput):
                validated_trace = trace_event
            elif isinstance(trace_event, Mapping):
                if "evaluated_atoms" not in trace_event:
                    msg = "Missing required base field in trace_event: evaluated_atoms"
                    logger.error("[ContextRouter] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                    raise ConfigurationError(
                        message=msg,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    )
                validated_trace = LightweightMatrixOutput.model_validate(trace_event)
            else:
                validated_trace = LightweightMatrixOutput.model_validate(trace_event)
        except ConfigurationError:
            raise
        except ValidationError as e:
            logger.error(
                "[ContextRouter] %s: Trace event validation failed during prune: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                e,
                exc_info=True,
            )
            raise ConfigurationError(
                message=f"Fail-Fast: Invalid trace_event format: {e}",
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e
        except (TypeError, ValueError, KeyError) as e:
            logger.error(
                "[ContextRouter] %s: Unexpected parsing error during trace event validation: %s",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                e,
                exc_info=True,
            )
            raise ConfigurationError(
                message=f"Missing required base field in trace_event: {e}",
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            ) from e

        extensions_extracted = {}
        if output_profile:
            for ext in output_profile.visible_block_extensions:
                # If block explicitly defines supported extensions, check suitability
                if validated_trace.allowed_extensions is not None and ext not in validated_trace.allowed_extensions:
                    continue
                if ext in validated_trace.extensions:
                    extensions_extracted[ext] = str(validated_trace.extensions[ext])
                else:
                    logger.debug("Missing XAI extension: %s. Skipping and omitting from trace.", ext)
                    continue
        else:
            # Fallback to include all extensions if no profile is explicitly provided during execution
            extensions_extracted = validated_trace.extensions

        return LightweightMatrixOutput(
            raw_score=validated_trace.raw_score,
            normalized_score=validated_trace.normalized_score,
            level_breakdown=validated_trace.level_breakdown,
            justification=validated_trace.justification,
            evaluated_atoms=validated_trace.evaluated_atoms,
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
    def normalize_and_validate_variable(path: str, snapshot: Any) -> str:
        """Validates dynamic variables (Fail-Fast) and strictly forbids legacy V1 paths.

        Enforces strict V2 nomenclature: No implicit stripping of '.output'.

        Args:
            path: The variable reference path (e.g. $steps.step_1.output).
            snapshot: The execution context state snapshot.

        Returns:
            The normalized path string if validated successfully.

        Raises:
            AppException: If snapshot validation fails, a legacy dictionary format is detected,
                the step is not found, or legacy V1 '.output' notation is used.
        """
        if not path:
            return path

        if path.startswith("$"):
            clean_path = path[1:]
        else:
            clean_path = path

        if clean_path.startswith("steps."):
            parts = clean_path.split(".")
            if len(parts) >= 2:
                step_key = parts[1]

                try:
                    state = SnapshotState.model_validate(snapshot)
                except ValidationError as e:
                    logger.error(
                        "SnapshotState validation failed.",
                        extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                        exc_info=True,
                    )
                    raise AppException(
                        message="Fail-Fast: Snapshot validation failed. Must match SnapshotState.",
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    ) from e

                found = False
                if state.steps:
                    found = any(dto.step_id == step_key for dto in state.steps)

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
