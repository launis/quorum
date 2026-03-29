"""Data Transfer Objects for Output Profiles.

These models handle the ingestion and output formats for the Output Profile REST APIs.
"""

from pydantic import BaseModel, ConfigDict, Field

from backend_v2.models.domain.output_profile import OutputProfileLayout
from backend_v2.models.v2_core import I18nText


class OutputProfileCreateDTO(BaseModel):
    """DTO for creating a new Output Profile."""

    id: str = Field(..., description="Unique string ID for the profile. Must follow Stripe Pattern")
    slug: str = Field(..., description="Human-readable routing identifier.")
    workflow_id: str = Field(..., description="References the execution DAG to scope Target Matrices.")
    name: I18nText = Field(..., description="Localized name.")
    description: I18nText | None = Field(default=None, description="Localized description.")
    layouts: list[OutputProfileLayout] = Field(default_factory=list, description="Sequence of layouts.")

    model_config = ConfigDict(strict=True, extra="forbid")


class OutputProfileUpdateDTO(BaseModel):
    """DTO for updating an existing Output Profile."""

    slug: str | None = Field(default=None, description="Human-readable routing identifier.")
    workflow_id: str | None = Field(default=None, description="Optional workflow reassignment.")
    name: I18nText | None = Field(default=None, description="Localized name.")
    description: I18nText | None = Field(default=None, description="Localized description.")
    layouts: list[OutputProfileLayout] | None = Field(default=None, description="Sequence of layouts.")

    model_config = ConfigDict(strict=True, extra="forbid")


class OutputProfileResponseDTO(BaseModel):
    """DTO for returning an Output Profile."""

    id: str
    slug: str
    workflow_id: str
    name: I18nText
    description: I18nText | None = None
    layouts: list[OutputProfileLayout]

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
