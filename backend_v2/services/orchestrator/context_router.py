"""Context Router for dynamic UI-driven state pruning."""

from typing import Any

from backend_v2.exceptions import (
    ConfigurationError,
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
        if not output_profile:
            raise ConfigurationError(message="Synthesis requests require an explicit output_profile.")

        try:
            normalized_score = float(trace_event["normalized_score"])
            level_breakdown = str(trace_event["level_breakdown"])
            justification = str(trace_event["justification"])
            evaluated_atoms = dict(trace_event["evaluated_atoms"])
            raw_extensions = trace_event["extensions"]
        except KeyError as e:
            raise ConfigurationError(message=f"Missing required base field in trace_event: {e}") from e

        extensions_extracted = {}
        for ext in output_profile.visible_extensions:
            ext_val = ext.value if hasattr(ext, "value") else str(ext)
            try:
                if ext in raw_extensions:
                    val = raw_extensions[ext]
                else:
                    val = raw_extensions[ext_val]
                extensions_extracted[ext] = str(val)
            except KeyError as e:
                raise MissingXaiExtensionError(extension_name=str(ext)) from e

        return LightweightMatrixOutput(
            normalized_score=normalized_score,
            level_breakdown=level_breakdown,
            justification=justification,
            evaluated_atoms=evaluated_atoms,
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
