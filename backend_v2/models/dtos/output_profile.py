"""Data Transfer Objects for Output Profiles.

These models handle the ingestion and output formats for the Output Profile REST APIs.
"""

from typing import Literal

from pydantic import Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.dtos.base import BaseResponseDTO
from backend_v2.models.enums import LaxXaiExtensionType
from backend_v2.models.v2_core import (
    I18nText,
    OutputLayoutBlock,
    SynthesisConfigDTO,
)


class OutputProfileCreateDTO(V2CoreBase):
    """DTO for creating a new Output Profile."""

    id: str = Field(
        ...,
        pattern=r"^([a-z]{2,5})_[a-zA-Z0-9]{8,}$",
        description="Unique string ID for the profile. Must follow Stripe Pattern",
    )
    slug: str = Field(..., description="Human-readable routing identifier.")
    workflow_id: str = Field(..., description="References the execution DAG to scope Target Matrices.")
    organization_id: str | None = Field(default=None, description="Tenant organization scope.")
    name: I18nText = Field(..., description="Localized name.")
    description: I18nText | None = Field(default=None, description="Localized description.")
    visible_metadata: list[str] = Field(
        default_factory=lambda: ["date", "organization"],
        description="List of metadata fields visible on the UI and PDF cover header.",
    )
    visible_extensions: list[LaxXaiExtensionType] = Field(
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


class OutputProfileUpdateDTO(V2CoreBase):
    """DTO for updating an existing Output Profile."""

    slug: str | None = Field(default=None, description="Human-readable routing identifier.")
    workflow_id: str | None = Field(default=None, description="Optional workflow reassignment.")
    name: I18nText | None = Field(default=None, description="Localized name.")
    description: I18nText | None = Field(default=None, description="Localized description.")
    organization_id: str | None = Field(default=None, description="Tenant organization scope.")
    visible_metadata: list[str] | None = Field(
        default=None,
        description="List of metadata fields visible on the UI and PDF cover header.",
    )
    visible_extensions: list[LaxXaiExtensionType] | None = Field(
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


class OutputProfileResponseDTO(BaseResponseDTO):
    """DTO for returning an Output Profile."""

    id: str
    slug: str
    workflow_id: str
    name: I18nText
    description: I18nText | None = None
    visible_metadata: list[str] = Field(default_factory=lambda: ["date", "organization"])
    visible_extensions: list[LaxXaiExtensionType] = Field(default_factory=list)
    max_extension_items: int | None = None
    display_scale: Literal["original", "custom", "normalized_100"] = "original"
    synthesis: SynthesisConfigDTO = Field(default_factory=SynthesisConfigDTO)
    include_diagnostic_scorecard: bool = Field(
        default=False, description="Epic 24: Enable appending the independent diagnostic scorecard."
    )
    layouts: list[OutputLayoutBlock]
