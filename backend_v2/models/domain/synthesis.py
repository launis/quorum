"""Synthesis Hook Domain Models.

Provides strict Pydantic V2 validation schemas for the synthesis pipeline
to eliminate legacy dictionary-based parsing.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SynthesisMetadataDTO(BaseModel):
    """Strict schema for execution metadata used during synthesis."""

    target_locale: str
    token_usage: dict[str, int] = Field(default_factory=dict)

    # Allow extra fields for safety in metadata, as other hooks may inject telemetry
    model_config = ConfigDict(extra="ignore", frozen=True)


class SynthesisStepDataDTO(BaseModel):
    """Schema to safely extract required synthesis flags from generic step outputs."""

    reasoning_trace: Any | None = Field(default=None)

    model_config = ConfigDict(extra="ignore", frozen=True)
