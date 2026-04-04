"""Data Transfer Objects for Output Profiles.

These models handle the ingestion and output formats for the Output Profile REST APIs.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from backend_v2.models.v2_core import (
    I18nText,
    OutputLayoutBlock,
    SynthesisConfigDTO,
)


class OutputProfileCreateDTO(BaseModel):
    """DTO for creating a new Output Profile."""

    id: str = Field(
        ...,
        pattern=r"^([a-z]{2,5})_[a-zA-Z0-9]{8,}$",
        description="Unique string ID for the profile. Must follow Stripe Pattern",
    )
    slug: str = Field(..., description="Human-readable routing identifier.")
    workflow_id: str = Field(..., description="References the execution DAG to scope Target Matrices.")
    name: I18nText = Field(..., description="Localized name.")
    description: I18nText | None = Field(default=None, description="Localized description.")
    visible_metadata: list[str] = Field(
        default_factory=lambda: ["date", "organization"],
        description="List of metadata fields visible on the UI and PDF cover header.",
    )
    display_scale: Literal["original", "custom", "normalized_100"] = Field(
        default="original", description="UI rendering scale instruction."
    )
    synthesis: SynthesisConfigDTO | None = Field(
        default=None, description="Nested definition for synthesis configurations."
    )
    layouts: list[OutputLayoutBlock] = Field(default_factory=list, description="Sequence of layouts.")

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")


class OutputProfileUpdateDTO(BaseModel):
    """DTO for updating an existing Output Profile."""

    slug: str | None = Field(default=None, description="Human-readable routing identifier.")
    workflow_id: str | None = Field(default=None, description="Optional workflow reassignment.")
    name: I18nText | None = Field(default=None, description="Localized name.")
    description: I18nText | None = Field(default=None, description="Localized description.")
    visible_metadata: list[str] | None = Field(
        default=None,
        description="List of metadata fields visible on the UI and PDF cover header.",
    )
    display_scale: Literal["original", "custom", "normalized_100"] | None = Field(
        default=None, description="UI rendering scale instruction."
    )
    synthesis: SynthesisConfigDTO | None = Field(
        default=None, description="Nested definition for synthesis configurations."
    )
    layouts: list[OutputLayoutBlock] | None = Field(default=None, description="Sequence of layouts.")

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")


class OutputProfileResponseDTO(BaseModel):
    """DTO for returning an Output Profile."""

    id: str
    slug: str
    workflow_id: str
    name: I18nText
    description: I18nText | None = None
    visible_metadata: list[str] = Field(default_factory=lambda: ["date", "organization"])
    display_scale: Literal["original", "custom", "normalized_100"] = "original"
    synthesis: SynthesisConfigDTO | None = None
    layouts: list[OutputLayoutBlock]

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
