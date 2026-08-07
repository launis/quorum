"""Context Router for dynamic UI-driven state pruning.

This module isolates UI-driven routing, step-to-step variable normalization,
and data culling/pruning logic matching the Phase 9 architecture standards.
"""

import logging
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError

from backend_v2.exceptions import (
    AppException,
    ConfigurationError,
    ErrorCodes,
    MissingRoutingModeError,
)
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput, OutputProfileConfig

logger = logging.getLogger(__name__)


class RoutingModeConfig(BaseModel):
    """Pydantic model for validating routing configurations strictly.

    Attributes:
        routing_mode: The routing behavior configuration string.
    """

    model_config = ConfigDict(extra="allow")
    routing_mode: str


class SnapshotState(BaseModel):
    """Pydantic model to encapsulate execution state snapshots without using naked dicts.

    Attributes:
        steps: Optional list of executed step data.
        raw_inputs: Optional dictionary representing starting inputs.
    """

    model_config = ConfigDict(extra="allow")
    steps: list[Any] | None = None
    raw_inputs: dict[str, Any] | None = None


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
            MissingXaiExtensionError: If a requested extension is missing in the trace.
        """
        try:
            if isinstance(trace_event, dict):
                if "evaluated_atoms" not in trace_event:
                    msg = "Missing required base field in trace_event: evaluated_atoms"
                    logger.error(msg)
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
            logger.error("Trace event validation failed during prune.", exc_info=True)
            raise ConfigurationError(
                message=f"Fail-Fast: Invalid trace_event format: {e}",
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e
        except Exception as e:
            logger.error("Unexpected parsing error during trace event validation.", exc_info=True)
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
            logger.error("RoutingMode validation failed for path %s.", mapping_path, exc_info=True)
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

        clean_path = path[1:] if path.startswith("$") else path

        if clean_path.startswith("steps."):
            parts = clean_path.split(".")
            if len(parts) >= 2:
                step_key = parts[1]

                try:
                    state = SnapshotState.model_validate(snapshot)
                except ValidationError as e:
                    logger.error("SnapshotState validation failed.", exc_info=True)
                    raise AppException(
                        message="Fail-Fast: Snapshot validation failed. Must match SnapshotState.",
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    ) from e

                if isinstance(snapshot, dict) and "steps" in snapshot and isinstance(snapshot["steps"], dict):
                    msg = (
                        "Fail-Fast: Legacy dictionary state detected in trace. "
                        "Epic 43 Zero-Compromise Pledge forbids unstructured data; "
                        "must be a list of StepOutputDTO."
                    )
                    logger.error(msg)
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.STATE_INTEGRITY_ERROR.value},
                    )

                found = False
                if state.steps:
                    found = any(getattr(dto, "step_id", None) == step_key for dto in state.steps)

                if not found:
                    msg = f"Fail-Fast: Required step '{step_key}' not found in state (Orphaned Step)."
                    logger.error(msg)
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
                    logger.error(msg)
                    raise AppException(
                        message=msg,
                        status_code=400,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    )

        return path
