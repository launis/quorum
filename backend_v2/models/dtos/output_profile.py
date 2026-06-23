"""Data Transfer Objects for Output Profiles.

These models handle the ingestion and output formats for the Output Profile REST APIs.
"""

from typing import Literal

from pydantic import Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.dtos.base import BaseResponseDTO
from backend_v2.models.enums import LaxScoringStrategy, LaxXaiExtensionType
from backend_v2.models.v2_core import (
    I18nText,
    OutputLayoutBlock,
    SynthesisConfigDTO,
)


class OutputProfileCreateDTO(V2CoreBase):
    """DTO for creating a new Output Profile.

    Attributes:
        id: Unique string ID for the profile. Must follow Stripe Pattern.
        slug: Human-readable routing identifier.
        workflow_id: References the execution DAG to scope Target Matrices.
        organization_id: Tenant organization scope.
        name: Localized name of the profile.
        description: Localized description of the profile.
        custom_preface: Rich text preface shown on outputs.
        visible_metadata: List of metadata fields visible on the UI and PDF cover header.
        visible_block_extensions: Block-level XAI extensions (per-matrix, LLM-produced).
        visible_workflow_extensions: Workflow-level global extensions (mathematical engines).
        max_extension_items: Max number of items to show per grouped XAI extension. Sorted by severity.
        display_scale: UI rendering scale instruction (e.g., 'normalized_100').
        synthesis: Nested definition for synthesis configurations.
        include_diagnostic_scorecard: Epic 24 feature indicating whether to append independent scorecards.
        strictness_level: Profile-level strictness override setting.
        scoring_strategy: Profile-level strategy calculation override.
        layouts: Sequence of layout rendering blocks.
    """

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
    custom_preface: I18nText | None = Field(default=None, description="Rich text preface.")
    tone_instruction: I18nText | None = Field(default=None, description="Dynamic tone instruction for synthesis.")

    visible_metadata: list[str] = Field(
        default_factory=lambda: ["date", "organization", "user", "scoring_engine", "strictness"],
        description="List of metadata fields visible on the UI and PDF cover header.",
    )
    visible_block_extensions: list[LaxXaiExtensionType] = Field(
        default_factory=list,
        description="Block-level XAI extensions (per-matrix, LLM-produced).",
    )
    visible_workflow_extensions: list[LaxXaiExtensionType] = Field(
        default_factory=list,
        description="Workflow-level global extensions (mathematical engines).",
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
    strictness_level: Literal[85, 100] | None = Field(default=None, description="Profile-level strictness override.")
    scoring_strategy: LaxScoringStrategy | None = Field(default=None, description="Profile-level strategy override.")
    layouts: list[OutputLayoutBlock] = Field(default_factory=list, description="Sequence of layouts.")


class OutputProfileUpdateDTO(V2CoreBase):
    """DTO for updating an existing Output Profile.

    Attributes:
        slug: Optional human-readable routing identifier.
        workflow_id: Optional workflow reassignment string.
        name: Optional localized name of the profile.
        description: Optional localized description string.
        custom_preface: Optional rich text preface block.
        organization_id: Optional tenant organization scope override.
        visible_metadata: Optional list of metadata fields to render.
        visible_block_extensions: Optional block-level XAI extensions array.
        visible_workflow_extensions: Optional workflow-level global extensions array.
        max_extension_items: Optional max limits per grouped extension payload.
        display_scale: Optional UI rendering instructions flag.
        synthesis: Optional nested definition mapping synthesis configuration rules.
        include_diagnostic_scorecard: Optional flag to render diagnostics data.
        strictness_level: Optional override strictness bounds.
        scoring_strategy: Optional strategy engine overriding defaults.
        layouts: Optional mapped layout instructions.
    """

    slug: str | None = Field(default=None, description="Human-readable routing identifier.")
    workflow_id: str | None = Field(default=None, description="Optional workflow reassignment.")
    name: I18nText | None = Field(default=None, description="Localized name.")
    description: I18nText | None = Field(default=None, description="Localized description.")
    custom_preface: I18nText | None = Field(default=None, description="Rich text preface.")
    tone_instruction: I18nText | None = Field(default=None, description="Dynamic tone instruction for synthesis.")

    organization_id: str | None = Field(default=None, description="Tenant organization scope.")
    visible_metadata: list[str] | None = Field(
        default=None,
        description="List of metadata fields visible on the UI and PDF cover header.",
    )
    visible_block_extensions: list[LaxXaiExtensionType] | None = Field(
        default=None,
        description="Block-level XAI extensions (per-matrix, LLM-produced).",
    )
    visible_workflow_extensions: list[LaxXaiExtensionType] | None = Field(
        default=None,
        description="Workflow-level global extensions (mathematical engines).",
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
    strictness_level: Literal[85, 100] | None = Field(default=None, description="Profile-level strictness override.")
    scoring_strategy: LaxScoringStrategy | None = Field(default=None, description="Profile-level strategy override.")
    layouts: list[OutputLayoutBlock] | None = Field(default=None, description="Sequence of layouts.")


class OutputProfileResponseDTO(BaseResponseDTO):
    """DTO for returning an Output Profile.

    Attributes:
        id: Unique Stripe-pattern string ID of the output profile.
        slug: Safe HTTP routing identifier.
        workflow_id: Connected DAG workflow boundary UUID.
        name: Complex localizable dictionary string name mapping.
        description: Complex localizable mapping for structural profile descriptions.
        custom_preface: Presentation front-matter mapping instructions.
        visible_metadata: Output keys exposed cleanly to presentation layer UI.
        visible_block_extensions: Block-bound extra payload outputs mappings.
        visible_workflow_extensions: Workflow-bound logic output payload arrays.
        max_extension_items: Top limit cap applying constraints to presentation loops.
        display_scale: Exact enumeration of UI rendering modes ('normalized_100').
        synthesis: Specific payload mapped configuring report output logic.
        include_diagnostic_scorecard: Status flag defining scorecard rendering operations.
        strictness_level: Validated override value configuring verification rigor.
        scoring_strategy: Mapped logic algorithm enum mapping engine implementation.
        layouts: Ordered array of discrete layout definitions governing presentation.
    """

    id: str
    slug: str
    workflow_id: str
    name: I18nText
    description: I18nText | None = None
    custom_preface: I18nText | None = None
    tone_instruction: I18nText | None = None

    visible_metadata: list[str] = Field(
        default_factory=lambda: ["date", "organization", "user", "scoring_engine", "strictness"]
    )
    visible_block_extensions: list[LaxXaiExtensionType] = Field(default_factory=list)
    visible_workflow_extensions: list[LaxXaiExtensionType] = Field(default_factory=list)
    max_extension_items: int | None = None
    display_scale: Literal["original", "custom", "normalized_100"] = "original"
    synthesis: SynthesisConfigDTO = Field(default_factory=SynthesisConfigDTO)
    include_diagnostic_scorecard: bool = Field(
        default=False, description="Epic 24: Enable appending the independent diagnostic scorecard."
    )
    strictness_level: Literal[85, 100] | None = None
    scoring_strategy: LaxScoringStrategy | None = None
    layouts: list[OutputLayoutBlock]
