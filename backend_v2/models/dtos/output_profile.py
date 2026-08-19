"""Data Transfer Objects for Output Profiles.

These models handle the ingestion and output formats for the Output Profile REST APIs.
"""

from typing import Annotated, Literal

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.dtos.base import BaseResponseDTO
from backend_v2.models.enums import (
    DisplayScale,
    LaxDisplayScale,
    LaxScoringStrategy,
    LaxTargetBlockType,
    LaxXaiExtensionType,
    TargetBlockType,
)
from backend_v2.models.v2_core import (
    I18nText,
    OutputLayoutBlock,
    SynthesisConfigDTO,
)
from backend_v2.models.view.sdui import AnySduiBlock

__all__ = [
    "OutputProfileCreateDTO",
    "OutputProfileUpdateDTO",
    "OutputProfileResponseDTO",
]


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
        strictness_level: Profile-level strictness override setting.
        scoring_strategy: Profile-level strategy calculation override.
        layouts: Sequence of layout rendering blocks.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    id: Annotated[
        str,
        Field(
            ...,
            pattern=r"^([a-z]{2,5})_[a-zA-Z0-9]{8,}$",
            description="Unique string ID for the profile. Must follow Stripe Pattern",
        ),
    ]
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
        I18nText | None, Field(default=None, description="Dynamic tone instruction for synthesis.")
    ]
    language: Annotated[str | None, Field(default=None, description="Target output language.")]

    visible_metadata: Annotated[
        list[str],
        Field(
            default_factory=lambda: ["date", "organization", "user", "scoring_engine", "strictness"],
            description="List of metadata fields visible on the UI and PDF cover header.",
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
        Field(default=DisplayScale.ORIGINAL, description="UI rendering scale instruction."),
    ] = DisplayScale.ORIGINAL
    user_role_mappings: Annotated[
        dict[str, I18nText],
        Field(
            default_factory=dict,
            description="Localized values for RoleClassification enum values.",
        ),
    ]
    extension_labels: Annotated[
        dict[LaxXaiExtensionType, I18nText],
        Field(
            default_factory=dict,
            description="Localized labels for global XAI highlights at the profile level.",
        ),
    ]
    metric_mappings: Annotated[
        dict[str, I18nText],
        Field(
            default_factory=dict,
            description="Localized labels for internal metric variables (e.g. 'variance_mechanical').",
        ),
    ]
    strictness_level: Annotated[
        Literal[85, 100] | None, Field(default=None, description="Profile-level strictness override.")
    ]
    scoring_strategy: Annotated[
        LaxScoringStrategy | None, Field(default=None, description="Profile-level strategy override.")
    ]
    synthesis: Annotated[
        SynthesisConfigDTO | None, Field(default=None, description="Nested definition for synthesis configurations.")
    ]
    layouts: Annotated[list[OutputLayoutBlock], Field(default_factory=list, description="Sequence of layouts.")]
    content_blocks: Annotated[
        list[AnySduiBlock],
        Field(default_factory=list, description="Base SDUI content blocks predefined by the profile."),
    ]
    target_block_order: Annotated[
        list[LaxTargetBlockType] | None,
        Field(default=None, description="Optional block order override."),
    ] = None
    performativity_detector_step_id: Annotated[
        str | None,
        Field(default=None, description="Optional step ID for the performativity detector"),
    ] = None


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
        strictness_level: Optional override strictness bounds.
        scoring_strategy: Optional strategy engine overriding defaults.
        layouts: Optional mapped layout instructions.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

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
        I18nText | None, Field(default=None, description="Dynamic tone instruction for synthesis.")
    ]
    language: Annotated[str | None, Field(default=None, description="Target output language.")]
    metric_mappings: Annotated[
        dict[str, I18nText] | None, Field(default=None, description="Localized labels for internal metric variables.")
    ]

    organization_id: Annotated[str | None, Field(default=None, description="Tenant organization scope.")]
    visible_metadata: Annotated[
        list[str] | None,
        Field(
            default=None,
            description="List of metadata fields visible on the UI and PDF cover header.",
        ),
    ]
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
    strictness_level: Annotated[
        Literal[85, 100] | None, Field(default=None, description="Profile-level strictness override.")
    ]
    scoring_strategy: Annotated[
        LaxScoringStrategy | None, Field(default=None, description="Profile-level strategy override.")
    ]
    synthesis: Annotated[
        SynthesisConfigDTO | None, Field(default=None, description="Nested definition for synthesis configurations.")
    ]
    layouts: Annotated[list[OutputLayoutBlock] | None, Field(default=None, description="Sequence of layouts.")]
    content_blocks: Annotated[
        list[AnySduiBlock] | None,
        Field(default=None, description="Base SDUI content blocks predefined by the profile."),
    ]
    target_block_order: Annotated[
        list[LaxTargetBlockType] | None,
        Field(default=None, description="Optional block order override."),
    ] = None
    performativity_detector_step_id: Annotated[
        str | None,
        Field(default=None, description="Optional step ID for the performativity detector"),
    ] = None


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
        strictness_level: Validated override value configuring verification rigor.
        scoring_strategy: Mapped logic algorithm enum mapping engine implementation.
        layouts: Ordered array of discrete layout definitions governing presentation.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    id: str
    slug: str
    workflow_id: str
    name: I18nText
    description: I18nText | None = None
    custom_preface: I18nText | None = None
    user_role_label: I18nText | None = None
    tone_instruction: I18nText | None = None
    language: str | None = None
    user_role_mappings: Annotated[dict[str, I18nText], Field(default_factory=dict)]
    extension_labels: Annotated[dict[LaxXaiExtensionType, I18nText], Field(default_factory=dict)]
    metric_mappings: Annotated[dict[str, I18nText], Field(default_factory=dict)]
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
    strictness_level: Literal[85, 100] | None = None
    scoring_strategy: LaxScoringStrategy | None = None
    synthesis: SynthesisConfigDTO | None = None
    layouts: Annotated[list[OutputLayoutBlock], Field(default_factory=list, description="Sequence of layouts.")]
    content_blocks: Annotated[list[AnySduiBlock], Field(default_factory=list, description="Base SDUI content blocks.")]
    performativity_detector_step_id: Annotated[
        str | None,
        Field(default=None, description="Optional step ID for the performativity detector"),
    ] = None
