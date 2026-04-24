"""Security Domain Models.

Provides strict Pydantic V2 validation schemas for the security hooks
to eliminate legacy dictionary-based parsing and enforce Zero-Compromise protocols.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, RootModel


class SecurityPayloadDTO(RootModel[dict[str, Any]]):
    """Strict schema for inputs destined for text sanitization.

    By utilizing RootModel, we strictly enforce that the incoming state
    payload is explicitly a dictionary before any iterative logic executes,
    satisfying the Phase 9 Zero-Compromise mandate.
    """  # noqa: W293

    model_config = ConfigDict(frozen=True)


class SanitizationResultDTO(BaseModel):
    """Result payload for text sanitization."""

    sanitized_inputs: dict[str, str]
    security_status: str

    model_config = ConfigDict(frozen=True)
