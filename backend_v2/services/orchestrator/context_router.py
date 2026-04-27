"""Context Router for dynamic UI-driven state pruning."""

from typing import Any

from backend_v2.exceptions import (
    AppException,
    ConfigurationError,
    ErrorCodes,
    MissingRoutingModeError,
    MissingXaiExtensionError,
)
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput, OutputProfileConfig


class ContextRouter:
    """Isolates UI-driven routing and data culling logic."""

    @staticmethod
    def route_and_prune(
        trace_event: dict[str, Any], output_profile: OutputProfileConfig | None
    ) -> LightweightMatrixOutput:
        """Extracts strictly what the UI demands from the execution trace.

        Args:
            trace_event: The full execution state dictionary (e.g. from an atom evaluation).
            output_profile: The UI-defined output profile specifying required extensions.

        Returns:
            A LightweightMatrixOutput containing only the requested data.

        Raises:
            ConfigurationError: If output_profile is None or required fields are missing.
            MissingXaiExtensionError: If a requested extension is missing in the trace.
        """
        try:
            validated_trace = LightweightMatrixOutput.model_validate(trace_event)
        except Exception as e:
            raise ConfigurationError(message=f"Missing required base field in trace_event: {e}") from e

        extensions_extracted = {}
        if output_profile:
            for ext in output_profile.visible_extensions:
                if ext in validated_trace.extensions:
                    extensions_extracted[ext] = str(validated_trace.extensions[ext])
                else:
                    raise MissingXaiExtensionError(extension_name=str(ext))
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
    def validate_routing_mode(mapping_path: str, mapping_config: dict[str, Any]) -> str:
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
            return str(mapping_config["routing_mode"])
        except KeyError as e:
            raise MissingRoutingModeError(mapping_path=mapping_path) from e

    @staticmethod
    def normalize_and_validate_variable(path: str, snapshot: dict[str, Any]) -> str:
        """Validates dynamic variables (Fail-Fast) and strictly forbids legacy V1 paths.

        Enforces strict V2 nomenclature: No implicit stripping of '.output'.
        """
        if not path:
            return path

        clean_path = path[1:] if path.startswith("$") else path

        if clean_path.startswith("steps."):
            parts = clean_path.split(".")
            if len(parts) >= 2:
                step_key = parts[1]
                if step_key not in snapshot:
                    raise AppException(
                        message=f"Fail-Fast: Required step '{step_key}' not found in state (Orphaned Step).",
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    )

                # STRICT V2 MANDATE: Explicitly reject legacy V1 `.output` notation.
                # All inputs must use the exact V2 format (e.g. $steps.step_1) without wrappers.
                if len(parts) >= 3 and parts[2] == "output":
                    raise AppException(
                        message=f"Fail-Fast: Legacy V1 '.output' variable format is strictly forbidden. "
                        f"Update the UI mapping to use strict V2 format (e.g. $steps.{step_key}).",
                        status_code=400,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    )

        return path
