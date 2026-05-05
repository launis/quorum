"""Security Domain Models.

Provides strict Pydantic V2 validation schemas for the security hooks
to eliminate legacy dictionary-based parsing and enforce Zero-Compromise protocols.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, RootModel


class SecurityPayloadDTO(RootModel[dict[str, Any]]):
    """Strict schema for inputs destined for text sanitization.

    By utilizing RootModel, we strictly enforce that the incoming state
    payload is explicitly a dictionary before any iterative logic executes,
    satisfying the Phase 9 Zero-Compromise mandate.
    """  # noqa: W293

    model_config = ConfigDict(frozen=True)


class SanitizationResultDTO(BaseModel):
    """Result payload for text sanitization."""

    sanitized_inputs: dict[str, str] = Field(..., description="The inputs after sanitization")
    security_status: str = Field(..., min_length=1, description="Status of the security check")
    threat_detected: bool = Field(..., description="Whether a threat was detected")

    model_config = ConfigDict(frozen=True, extra="forbid")
