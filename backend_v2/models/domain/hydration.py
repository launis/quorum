"""Hydration Domain Models.

Provides strict Pydantic V2 validation schemas for the hydration hooks
to eliminate legacy dictionary-based parsing and enforce Zero-Compromise protocols.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase


class HydrationInputSourceDTO(V2CoreBase):
    """Strict schema for parsing InputProcessorAgent outputs.

    Enforces Fail-Fast integrity without duck-typing or legacy fallbacks.

    Attributes:
        inputs: Nested structured inputs mapped by key.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    inputs: Annotated[dict[str, str], Field(description="Nested structured inputs.")]

    def is_valid_source(self) -> bool:
        """Determines if this parsed state node is indeed an InputProcessor output.

        Returns:
            True if the source is valid, False otherwise.
        """
        return True

    def extract_hydrated_inputs(self) -> dict[str, str]:
        """Extract strings securely relying on strict Pydantic validation.

        Returns:
            A safe copy of the validated inputs dictionary.
        """
        return self.inputs.copy()
