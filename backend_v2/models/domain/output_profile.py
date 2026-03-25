"""Domain models for Output Profiles.

This module contains the domain entities defining the Output Profiles for the V2 Reporting Architecture.
It enforces the Semantic Routing and I18n standards, guaranteeing safe outputs.
"""

import logging
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)


from backend_v2.models.v2_core import I18nText


class LayoutType(str, Enum):
    """Supported render types for Output Profiles."""
    AUTOMATIC = "automatic"
    BOX_1D = "box_1d"
    MATRIX_2D = "matrix_2d"
    RADAR_3D = "radar_3d"
    EXCEL_ROW = "excel_row"
    TEXT_ONLY = "text_only"


class OutputProfileLayout(BaseModel):
    """Layout definition mapping a presentation type to DAG components."""

    layout_type: LayoutType = Field(..., description="The type of layout to render.")
    title: I18nText = Field(..., description="Localized title for this layout block.")
    description: I18nText | None = Field(default=None, description="Optional localized description.")
    components: list[str] = Field(
        ...,
        description="List of block IDs (e.g. blk_123abc) representing the axes/components to include.",
    )
    show_text: bool = Field(default=True, description="Whether to include text justifications in this block.")

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("layout_type", mode="before")
    @classmethod
    def parse_layout_type(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return LayoutType(v)
            except ValueError as e:
                msg = f"OutputProfileLayout parsing failed: Invalid LayoutType '{v}'."
                logger.error(f"[OutputProfileDomain] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
                err_details = {"error_code": ErrorCodes.VALIDATION_FAILED.value}
                raise AppException(message=msg, status_code=422, details=err_details) from e
        return v

    @field_validator("components")
    @classmethod
    def validate_components(cls, v: list[str]) -> list[str]:
        if not v:
            msg = "An OutputProfileLayout must have at least one component mapped."
            logger.error(f"[OutputProfileDomain] {ErrorCodes.VALIDATION_FAILED.name}: {msg}")
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return v


class OutputProfile(BaseModel):
    """Domain model representing a single Output Profile."""

    id: str = Field(..., description="Unique ID for the Output Profile. Must follow Stripe Pattern.")
    slug: str = Field(..., description="Human-readable routing identifier (e.g. 'default').")
    workflow_id: str = Field(..., description="References the execution DAG to scope Target Matrices.")
    name: I18nText = Field(..., description="Localized name of the Output Profile.")
    description: I18nText | None = Field(default=None, description="Localized description.")
    layouts: list[OutputProfileLayout] = Field(
        default_factory=list, description="The sequence of layouts composing the entire document."
    )

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("id")
    @classmethod
    def validate_id_opaque(cls, v: str) -> str:
        import re
        if not re.match(r"^([a-z]+)_[a-zA-Z0-9]{8,}$", v):
            msg = f"Profile ID '{v}' does not match Opaque Stripe Pattern."
            logger.error(f"[OutputProfileDomain] {ErrorCodes.VALIDATION_FAILED.name}: {msg}")
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return v

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if not v or not v.strip():
            msg = "Profile Slug cannot be empty."
            logger.error(f"[OutputProfileDomain] {ErrorCodes.VALIDATION_FAILED.name}: {msg}")
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return v.strip()
