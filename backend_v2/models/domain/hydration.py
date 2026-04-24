"""Hydration Domain Models.

Provides strict Pydantic V2 validation schemas for the hydration hooks
to eliminate legacy dictionary-based parsing and enforce Zero-Compromise protocols.
"""

from pydantic import BaseModel, ConfigDict, Field


class HydrationInputSourceDTO(BaseModel):
    """Strict schema for detecting and parsing legacy InputProcessorAgent outputs.

    Acts as a sieve to safely extract dynamically assigned top-level strings
    or nested `inputs` dictionaries without relying on duck-typing.
    """  # noqa: W291, W293

    agent_type: str | None = Field(default=None, description="Legacy agent type discriminator.")
    inputs: dict[str, str] | None = Field(default=None, description="Nested structured inputs if provided.")

    # We must allow extra fields to catch legacy top-level string outputs
    model_config = ConfigDict(extra="allow", frozen=True, strict=True)

    def is_valid_source(self) -> bool:
        """Determines if this parsed state node is indeed an InputProcessor output."""
        return self.agent_type == "InputProcessorAgent" or self.inputs is not None

    def extract_hydrated_inputs(self) -> dict[str, str]:
        """Extract strings securely without dict.items() duck typing on raw payloads."""
        updates: dict[str, str] = {}

        # 1. If explicit inputs dict exists, take string values from it
        if self.inputs:
            # Pydantic has already strictly validated this as dict[str, str]
            updates.update(self.inputs)

        # 2. Otherwise extract from extra fields (legacy top-level string returns)
        elif self.model_extra:
            for k, v in self.model_extra.items():
                if isinstance(v, str):
                    updates[k] = v

        return updates
