"""Data Transfer Objects for Output Profiles.

These models handle the ingestion and output formats for the Output Profile REST APIs.
"""

import logging
from typing import Annotated, Literal, Self

from pydantic import ConfigDict, Field, model_validator

from backend_v2.exceptions import ErrorCodes
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX, V2CoreBase
from backend_v2.models.dtos.base import BaseResponseDTO
from backend_v2.models.enums import (
    DisplayScale,
    LaxDisplayScale,
    LaxScoringStrategy,
    LaxSourcesDisplayMode,
    LaxSystemLocale,
    LaxTargetBlockType,
    LaxXaiExtensionType,
    SourcesDisplayMode,
    TargetBlockType,
)
from backend_v2.models.v2_core import (
    I18nText,
    MatrixSynthesisGroup,
)
from backend_v2.models.view.sdui import AnySduiBlock

logger = logging.getLogger(__name__)

__all__ = [
    "OutputProfileCreateDTO",
    "OutputProfileUpdateDTO",
    "OutputProfileResponseDTO",
]


class OutputProfileCreateDTO(V2CoreBase):
    """DTO for creating a new Output Profile without client-specified ID.

    Attributes:
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
        synthesis_length_constraint: Optional length constraint for synthesized text.
        max_quotes_per_matrix: Per-profile override for quotes per matrix in explanations.
        max_unmet_criteria: Per-profile override for unmet criteria per matrix.
        strictness_level: Profile-level strictness override setting.
        scoring_strategy: Profile-level strategy calculation override.
        matrix_synthesis_groups: Sequence of comparative matrix synthesis groups.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    slug: Annotated[str, Field(..., description="Human-readable routing identifier.")]
    workflow_id: Annotated[str, Field(..., description="References the execution DAG to scope Target Matrices.")]
    organization_id: Annotated[str | None, Field(default=None, description="Tenant organization scope.")]
    name: Annotated[I18nText, Field(..., description="Localized name.")]
    description: Annotated[I18nText | None, Field(default=None, description="Localized description.")]
    custom_preface: Annotated[I18nText | None, Field(default=None, description="Rich text preface.")]
    user_role_label: Annotated[
        I18nText | None,
        Field(
            default=None,
            description="Optional localized label prefixing the user role context (e.g., 'Target audience:').",
        ),
    ]
    tone_instruction: Annotated[
        str | None, Field(default=None, description="Dynamic tone instruction for synthesis.")
    ] = None
    executive_summary_directive: Annotated[
        str | None, Field(default=None, description="Dedicated prompt directive for executive summary synthesis.")
    ] = None
    matrix_1d_synthesis_directive: Annotated[
        str | None, Field(default=None, description="Dedicated prompt directive for 1D metrics synthesis.")
    ] = None
    matrix_2d_synthesis_directive: Annotated[
        str | None, Field(default=None, description="Dedicated prompt directive for 2D comparison synthesis.")
    ] = None
    matrix_3d_synthesis_directive: Annotated[
        str | None, Field(default=None, description="Dedicated prompt directive for 3D radar synthesis.")
    ] = None
    matrix_text_synthesis_directive: Annotated[
        str | None,
        Field(default=None, description="Dedicated prompt directive for text-only matrix synthesis."),
    ] = None
    row_explanation_directive: Annotated[
        str | None,
        Field(default=None, description="Dedicated prompt directive for matrix summary table row causal explanations."),
    ] = None
    xai_synthesis_directive: Annotated[
        str | None,
        Field(default=None, description="Dedicated prompt directive for XAI highlights and extensions synthesis."),
    ] = None
    variance_synthesis_directive: Annotated[
        str | None,
        Field(
            default=None,
            description="Dedicated prompt directive for variance and cognitive authenticity evaluation synthesis.",
        ),
    ] = None
    language: Annotated[LaxSystemLocale | None, Field(default=None, description="Target output language.")] = None

    visible_metadata: Annotated[
        list[str],
        Field(
            default_factory=lambda: ["date", "organization", "user", "scoring_engine", "strictness"],
            description="List of metadata fields visible on the UI and PDF cover header.",
        ),
    ]
    matrix_visible_columns: Annotated[
        list[str],
        Field(
            default_factory=lambda: [
                "label",
                "distribution",
                "row_explanation",
                "quotes",
                "normalized_score",
                "score",
            ],
            description="List of column keys visible in the matrix summary table.",
        ),
    ]
    visible_block_extensions: Annotated[
        list[LaxXaiExtensionType],
        Field(
            default_factory=list,
            description="Block-level XAI extensions (per-matrix, LLM-produced).",
        ),
    ]
    visible_workflow_extensions: Annotated[
        list[LaxXaiExtensionType],
        Field(
            default_factory=list,
            description="Workflow-level global extensions (mathematical engines).",
        ),
    ]
    max_extension_items: Annotated[
        int,
        Field(
            default=3,
            ge=1,
            le=100,
            description="Max number of items to show per grouped XAI extension. Sorted by severity.",
        ),
    ] = 3

    display_scale: Annotated[
        LaxDisplayScale,
        Field(
            default=DisplayScale.ORIGINAL,
            description="Selects the source scaling for the scores printed by Blueprint.",
        ),
    ] = DisplayScale.ORIGINAL
    custom_scale_min: Annotated[
        float | None,
        Field(default=None, description="Minimum score boundary when display_scale is CUSTOM."),
    ] = None
    custom_scale_max: Annotated[
        float | None,
        Field(default=None, description="Maximum score boundary when display_scale is CUSTOM."),
    ] = None
    strictness_level: Annotated[
        Literal[85, 100] | None, Field(default=None, description="Profile-level strictness override.")
    ]
    scoring_strategy: Annotated[
        LaxScoringStrategy | None, Field(default=None, description="Profile-level strategy override.")
    ]
    synthesis_length_constraint: Annotated[
        int | None,
        Field(default=None, ge=100, le=5000, description="Optional length constraint for synthesized text."),
    ] = None
    row_explanation_length_constraint: Annotated[
        int | None,
        Field(default=None, ge=50, le=1000, description="Max character length for each row causal explanation."),
    ] = None
    xai_length_constraint: Annotated[
        int | None,
        Field(default=None, ge=50, le=1000, description="Max character length for each XAI extension highlight."),
    ] = None
    variance_length_constraint: Annotated[
        int | None,
        Field(default=None, ge=50, le=2000, description="Max character length for variance evaluation."),
    ] = None
    max_quotes_per_matrix: Annotated[
        int | None,
        Field(default=None, description="Per-profile override for quotes per matrix in explanations."),
    ] = None
    max_unmet_criteria: Annotated[
        int | None,
        Field(default=None, description="Per-profile override for unmet criteria per matrix."),
    ] = None
    matrix_synthesis_groups: Annotated[
        list[MatrixSynthesisGroup],
        Field(default_factory=list, description="Optional matrix synthesis groups for 2D/3D comparative graphs."),
    ]
    content_blocks: Annotated[
        list[AnySduiBlock],
        Field(default_factory=list, description="Base SDUI content blocks predefined by the profile."),
    ]
    show_sources_summary_box: Annotated[
        bool,
        Field(default=True, description="Whether to show the source verification summary box in the report."),
    ] = True
    sources_display_mode: Annotated[
        LaxSourcesDisplayMode,
        Field(
            default=SourcesDisplayMode.VERIFIED_EVIDENCE,
            description="Display mode for the bibliography and source verification section.",
        ),
    ] = SourcesDisplayMode.VERIFIED_EVIDENCE
    target_block_order: Annotated[
        list[LaxTargetBlockType] | None,
        Field(default=None, description="Optional block order override."),
    ] = None
    performativity_detector_step_id: Annotated[
        str | None,
        Field(default=None, description="Optional step ID for the performativity detector"),
    ] = None

    @model_validator(mode="after")
    def validate_custom_scale_bounds(self) -> Self:
        """Enforce that custom scale bounds are valid when display_scale is CUSTOM."""
        if self.display_scale in (DisplayScale.CUSTOM, "custom"):
            if self.custom_scale_min is None or self.custom_scale_max is None:
                msg = (
                    "OutputProfileCreateDTO: custom_scale_min and custom_scale_max "
                    "are required when display_scale is CUSTOM."
                )
                logger.error("[DTO] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
            if self.custom_scale_max <= self.custom_scale_min:
                msg = (
                    f"OutputProfileCreateDTO: custom_scale_max ({self.custom_scale_max}) "
                    f"must be strictly greater than custom_scale_min ({self.custom_scale_min})."
                )
                logger.error("[DTO] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
        return self


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
        synthesis_length_constraint: Optional length constraint for synthesized text.
        max_quotes_per_matrix: Optional override for quotes per matrix in explanations.
        max_unmet_criteria: Optional override for unmet criteria per matrix.
        strictness_level: Optional override strictness bounds.
        scoring_strategy: Optional strategy engine overriding defaults.
        matrix_synthesis_groups: Optional sequence of comparative matrix synthesis groups.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    id: Annotated[
        str | None,
        Field(
            default=None,
            pattern=OPAQUE_STRIPE_ID_REGEX,
            description="Optional Profile ID supplied in PUT payload for client-state preservation.",
        ),
    ] = None
    slug: Annotated[str | None, Field(default=None, description="Human-readable routing identifier.")]
    workflow_id: Annotated[str | None, Field(default=None, description="Optional workflow reassignment.")]
    name: Annotated[I18nText | None, Field(default=None, description="Localized name.")]
    description: Annotated[I18nText | None, Field(default=None, description="Localized description.")]
    custom_preface: Annotated[I18nText | None, Field(default=None, description="Rich text preface.")]
    user_role_label: Annotated[
        I18nText | None,
        Field(
            default=None,
            description="Optional localized label prefixing the user role context (e.g., 'Target audience:').",
        ),
    ]
    tone_instruction: Annotated[
        str | None, Field(default=None, description="Dynamic tone instruction for synthesis.")
    ] = None
    executive_summary_directive: Annotated[
        str | None, Field(default=None, description="Dedicated prompt directive for executive summary synthesis.")
    ] = None
    matrix_1d_synthesis_directive: Annotated[
        str | None, Field(default=None, description="Dedicated prompt directive for 1D metrics synthesis.")
    ] = None
    matrix_2d_synthesis_directive: Annotated[
        str | None, Field(default=None, description="Dedicated prompt directive for 2D comparison synthesis.")
    ] = None
    matrix_3d_synthesis_directive: Annotated[
        str | None, Field(default=None, description="Dedicated prompt directive for 3D radar synthesis.")
    ] = None
    matrix_text_synthesis_directive: Annotated[
        str | None,
        Field(default=None, description="Dedicated prompt directive for text-only matrix synthesis."),
    ] = None
    row_explanation_directive: Annotated[
        str | None,
        Field(default=None, description="Dedicated prompt directive for matrix summary table row causal explanations."),
    ] = None
    xai_synthesis_directive: Annotated[
        str | None,
        Field(default=None, description="Dedicated prompt directive for XAI highlights and extensions synthesis."),
    ] = None
    variance_synthesis_directive: Annotated[
        str | None,
        Field(
            default=None,
            description="Dedicated prompt directive for variance and cognitive authenticity evaluation synthesis.",
        ),
    ] = None
    language: Annotated[LaxSystemLocale | None, Field(default=None, description="Target output language.")] = None

    organization_id: Annotated[str | None, Field(default=None, description="Tenant organization scope.")]
    visible_metadata: Annotated[
        list[str] | None,
        Field(
            default=None,
            description="List of metadata fields visible on the UI and PDF cover header.",
        ),
    ]
    matrix_visible_columns: Annotated[
        list[str] | None,
        Field(
            default=None,
            description="Optional list of column keys visible in the matrix summary table.",
        ),
    ] = None
    visible_block_extensions: Annotated[
        list[LaxXaiExtensionType] | None,
        Field(
            default=None,
            description="Block-level XAI extensions (per-matrix, LLM-produced).",
        ),
    ]
    visible_workflow_extensions: Annotated[
        list[LaxXaiExtensionType] | None,
        Field(
            default=None,
            description="Workflow-level global extensions (mathematical engines).",
        ),
    ]
    max_extension_items: Annotated[
        int | None,
        Field(
            default=None,
            ge=1,
            le=100,
            description="Max number of items to show per grouped XAI extension. Sorted by severity.",
        ),
    ] = None
    display_scale: Annotated[
        LaxDisplayScale | None,
        Field(default=None, description="UI rendering scale instruction."),
    ] = None
    custom_scale_min: Annotated[
        float | None,
        Field(default=None, description="Minimum score boundary when display_scale is CUSTOM."),
    ] = None
    custom_scale_max: Annotated[
        float | None,
        Field(default=None, description="Maximum score boundary when display_scale is CUSTOM."),
    ] = None
    strictness_level: Annotated[
        Literal[85, 100] | None, Field(default=None, description="Profile-level strictness override.")
    ]
    scoring_strategy: Annotated[
        LaxScoringStrategy | None, Field(default=None, description="Profile-level strategy override.")
    ]
    synthesis_length_constraint: Annotated[
        int | None,
        Field(default=None, ge=100, le=5000, description="Optional length constraint for synthesized text."),
    ] = None
    row_explanation_length_constraint: Annotated[
        int | None,
        Field(default=None, ge=50, le=1000, description="Max character length for each row causal explanation."),
    ] = None
    xai_length_constraint: Annotated[
        int | None,
        Field(default=None, ge=50, le=1000, description="Max character length for each XAI extension highlight."),
    ] = None
    variance_length_constraint: Annotated[
        int | None,
        Field(default=None, ge=2000, description="Max character length for variance evaluation."),
    ] = None
    max_quotes_per_matrix: Annotated[
        int | None,
        Field(default=None, description="Per-profile override for quotes per matrix in explanations."),
    ] = None
    max_unmet_criteria: Annotated[
        int | None,
        Field(default=None, description="Per-profile override for unmet criteria per matrix."),
    ] = None
    matrix_synthesis_groups: Annotated[
        list[MatrixSynthesisGroup] | None,
        Field(default=None, description="Optional matrix synthesis groups for 2D/3D comparative graphs."),
    ]
    content_blocks: Annotated[
        list[AnySduiBlock] | None,
        Field(default=None, description="Base SDUI content blocks predefined by the profile."),
    ]
    show_sources_summary_box: Annotated[
        bool | None,
        Field(default=None, description="Optional override to show/hide source verification summary box."),
    ] = None
    sources_display_mode: Annotated[
        LaxSourcesDisplayMode | None,
        Field(default=None, description="Optional override for sources display mode."),
    ] = None
    target_block_order: Annotated[
        list[LaxTargetBlockType] | None,
        Field(default=None, description="Optional block order override."),
    ] = None
    performativity_detector_step_id: Annotated[
        str | None,
        Field(default=None, description="Optional step ID for the performativity detector"),
    ] = None

    @model_validator(mode="after")
    def validate_custom_scale_bounds(self) -> Self:
        """Enforce that custom scale bounds are valid when display_scale is CUSTOM."""
        if self.display_scale in (DisplayScale.CUSTOM, "custom"):
            if self.custom_scale_min is not None and self.custom_scale_max is not None:
                if self.custom_scale_max <= self.custom_scale_min:
                    msg = (
                        f"OutputProfileUpdateDTO: custom_scale_max ({self.custom_scale_max}) "
                        f"must be strictly greater than custom_scale_min ({self.custom_scale_min})."
                    )
                    logger.error("[DTO] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                    raise ValueError(msg)
        return self


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
        synthesis_length_constraint: Optional length constraint for synthesized text.
        max_quotes_per_matrix: Per-profile override for quotes per matrix in explanations.
        max_unmet_criteria: Per-profile override for unmet criteria per matrix.
        strictness_level: Validated override value configuring verification rigor.
        scoring_strategy: Mapped logic algorithm enum mapping engine implementation.
        matrix_synthesis_groups: Ordered array of discrete comparative synthesis groups.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    id: str
    slug: str
    workflow_id: str
    name: I18nText
    description: I18nText | None = None
    custom_preface: I18nText | None = None
    user_role_label: I18nText | None = None
    tone_instruction: str | None = None
    executive_summary_directive: str | None = None
    matrix_1d_synthesis_directive: str | None = None
    matrix_2d_synthesis_directive: str | None = None
    matrix_3d_synthesis_directive: str | None = None
    matrix_text_synthesis_directive: Annotated[
        str | None,
        Field(default=None, description="Dedicated prompt directive for text-only matrix synthesis."),
    ] = None
    row_explanation_directive: Annotated[
        str | None,
        Field(default=None, description="Dedicated prompt directive for matrix summary table row causal explanations."),
    ] = None
    xai_synthesis_directive: Annotated[
        str | None,
        Field(default=None, description="Dedicated prompt directive for XAI highlights and extensions synthesis."),
    ] = None
    variance_synthesis_directive: Annotated[
        str | None,
        Field(
            default=None,
            description="Dedicated prompt directive for variance and cognitive authenticity evaluation synthesis.",
        ),
    ] = None
    language: LaxSystemLocale | None = None
    target_block_order: Annotated[
        list[LaxTargetBlockType],
        Field(
            default_factory=lambda: [
                TargetBlockType.METADATA_BLOCK,
                TargetBlockType.EXECUTIVE_SUMMARY_BLOCK,
                TargetBlockType.SYNTHESIS_TEXT_BLOCK,
                TargetBlockType.MATRIX_GRAPHS_BLOCK,
                TargetBlockType.GROUPED_EXTENSIONS_BLOCK,
                TargetBlockType.PENALTIES_BLOCK,
                TargetBlockType.MATRIX_SUMMARY_TABLE_BLOCK,
                TargetBlockType.VARIANCE_VALIDATION_BLOCK,
                TargetBlockType.AUTHENTICITY_EVALUATION_BLOCK,
                TargetBlockType.PRINTABLE_SOURCES_BLOCK,
                TargetBlockType.GLOBAL_SCORE_BLOCK,
                TargetBlockType.AUDIT_TRAIL_BLOCK,
            ]
        ),
    ]

    visible_metadata: Annotated[
        list[str], Field(default_factory=lambda: ["date", "organization", "user", "scoring_engine", "strictness"])
    ]
    matrix_visible_columns: Annotated[
        list[str],
        Field(
            default_factory=lambda: [
                "label",
                "distribution",
                "row_explanation",
                "quotes",
                "normalized_score",
                "score",
            ]
        ),
    ]
    visible_block_extensions: Annotated[list[LaxXaiExtensionType], Field(default_factory=list)]
    visible_workflow_extensions: Annotated[list[LaxXaiExtensionType], Field(default_factory=list)]
    max_extension_items: Annotated[
        int,
        Field(default=3, ge=1, le=100, description="Top limit cap applying constraints to presentation loops."),
    ] = 3
    display_scale: Annotated[
        LaxDisplayScale,
        Field(
            default=DisplayScale.ORIGINAL,
            description="Exact enumeration of UI rendering modes ('normalized_100').",
        ),
    ] = DisplayScale.ORIGINAL
    custom_scale_min: float | None = None
    custom_scale_max: float | None = None
    strictness_level: Literal[85, 100] | None = None
    scoring_strategy: LaxScoringStrategy | None = None
    synthesis_length_constraint: int | None = None
    row_explanation_length_constraint: int | None = None
    xai_length_constraint: int | None = None
    variance_length_constraint: int | None = None
    max_quotes_per_matrix: int | None = None
    max_unmet_criteria: int | None = None
    matrix_synthesis_groups: Annotated[
        list[MatrixSynthesisGroup],
        Field(default_factory=list, description="Optional matrix synthesis groups for 2D/3D comparative graphs."),
    ]
    content_blocks: Annotated[list[AnySduiBlock], Field(default_factory=list, description="Base SDUI content blocks.")]
    show_sources_summary_box: Annotated[
        bool,
        Field(default=True, description="Whether to show the source verification summary box in the report."),
    ] = True
    sources_display_mode: Annotated[
        LaxSourcesDisplayMode,
        Field(
            default=SourcesDisplayMode.VERIFIED_EVIDENCE,
            description="Display mode for the bibliography and source verification section.",
        ),
    ] = SourcesDisplayMode.VERIFIED_EVIDENCE
    performativity_detector_step_id: Annotated[
        str | None,
        Field(default=None, description="Optional step ID for the performativity detector"),
    ] = None
