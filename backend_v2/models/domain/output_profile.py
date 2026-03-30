"""Domain models for Output Profiles.

This module contains the domain entities defining the Output Profiles for the V2 Reporting Architecture.
It enforces the Semantic Routing and I18n standards, guaranteeing safe outputs.
"""

import logging
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)
from backend_v2.models.v2_core import I18nText, OutputLayoutBlock


class OutputProfile(BaseModel):
    """Domain model representing a single Output Profile."""

    id: str = Field(..., description="Unique ID for the Output Profile. Must follow Stripe Pattern.")
    slug: str = Field(..., description="Human-readable routing identifier (e.g. 'default').")
    workflow_id: str = Field(..., description="References the execution DAG to scope Target Matrices.")
    name: I18nText = Field(..., description="Localized name of the Output Profile.")
    description: I18nText | None = Field(default=None, description="Localized description.")
    display_scale: Literal["original", "custom", "normalized_100"] = Field(
        default="original",
        description="Selects the source scaling for the scores printed by Blueprint.",
    )
    layouts: list[OutputLayoutBlock] = Field(
        default_factory=list, description="The sequence of layouts composing the entire document."
    )

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    @field_validator("id")
    @classmethod
    def validate_id_opaque(cls, v: str) -> str:
        import re

        if not re.match(r"^([a-z]{2,5})_[a-zA-Z0-9]{8,}$", v):
            msg = f"Profile ID '{v}' does not match Opaque Stripe Pattern."
            logger.error("[OutputProfileDomain] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return v

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if not v or not v.strip():
            msg = "Profile Slug cannot be empty."
            logger.error("[OutputProfileDomain] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return v.strip()
