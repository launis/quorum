"""Data Transfer Objects for Output Profiles.

These models handle the ingestion and output formats for the Output Profile REST APIs.
"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend_v2.models.enums import XaiExtensionType
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
    visible_extensions: list[XaiExtensionType] = Field(
        default_factory=list,
        description="List of XAI extensions visible at the end of the report.",
    )
    max_extension_items: int | None = Field(
        default=None,
        ge=1,
        description="Max number of items to show per grouped XAI extension. Sorted by severity.",
    )
    display_scale: Literal["original", "custom", "normalized_100"] = Field(
        default="original", description="UI rendering scale instruction."
    )
    synthesis: SynthesisConfigDTO | None = Field(
        default=None, description="Nested definition for synthesis configurations."
    )
    include_diagnostic_scorecard: bool = Field(
        default=False, description="Epic 24: Enable appending the independent diagnostic scorecard."
    )
    layouts: list[OutputLayoutBlock] = Field(default_factory=list, description="Sequence of layouts.")

    @field_validator("visible_extensions", mode="before")
    @classmethod
    def coerce_xai_extensions(cls, v: Any) -> Any:
        if isinstance(v, list):
            return [XaiExtensionType(x) if isinstance(x, str) else x for x in v]
        return v

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
    visible_extensions: list[XaiExtensionType] | None = Field(
        default=None,
        description="List of XAI extensions visible at the end of the report.",
    )
    max_extension_items: int | None = Field(
        default=None,
        ge=1,
        description="Max number of items to show per grouped XAI extension. Sorted by severity.",
    )
    display_scale: Literal["original", "custom", "normalized_100"] | None = Field(
        default=None, description="UI rendering scale instruction."
    )
    synthesis: SynthesisConfigDTO | None = Field(
        default=None, description="Nested definition for synthesis configurations."
    )
    include_diagnostic_scorecard: bool | None = Field(
        default=None, description="Epic 24: Enable appending the independent diagnostic scorecard."
    )
    layouts: list[OutputLayoutBlock] | None = Field(default=None, description="Sequence of layouts.")

    @field_validator("visible_extensions", mode="before")
    @classmethod
    def coerce_xai_extensions(cls, v: Any) -> Any:
        if isinstance(v, list):
            return [XaiExtensionType(x) if isinstance(x, str) else x for x in v]
        return v

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")


class OutputProfileResponseDTO(BaseModel):
    """DTO for returning an Output Profile."""

    id: str
    slug: str
    workflow_id: str
    name: I18nText
    description: I18nText | None = None
    visible_metadata: list[str] = Field(default_factory=lambda: ["date", "organization"])
    visible_extensions: list[XaiExtensionType] = Field(default_factory=list)
    max_extension_items: int | None = None
    display_scale: Literal["original", "custom", "normalized_100"] = "original"
    synthesis: SynthesisConfigDTO = Field(default_factory=SynthesisConfigDTO)
    include_diagnostic_scorecard: bool = Field(
        default=False, description="Epic 24: Enable appending the independent diagnostic scorecard."
    )
    layouts: list[OutputLayoutBlock]

    @field_validator("visible_extensions", mode="before")
    @classmethod
    def coerce_xai_extensions(cls, v: Any) -> Any:
        if isinstance(v, list):
            return [XaiExtensionType(x) if isinstance(x, str) else x for x in v]
        return v

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
