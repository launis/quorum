"""Domain model for Output Profiles.

SSOT for OutputProfile defining report recipes, section ordering, synthesis directives,
and presentation scaling.
"""

from __future__ import annotations

import logging
from typing import Annotated, Self

from pydantic import ConfigDict, Field, field_validator, model_validator

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX, I18nText, V2CoreBase, parse_prefixed_uuid7
from backend_v2.models.domain.synthesis import MatrixSynthesisGroup
from backend_v2.models.enums import (
    DisplayScale,
    EntityPrefix,
    LaxDisplayScale,
    LaxSourcesDisplayMode,
    LaxSystemLocale,
    LaxTargetBlockType,
    LaxXaiExtensionType,
    ReportMatrixColumn,
    SourcesDisplayMode,
    TargetBlockType,
    XaiExtensionType,
)
from backend_v2.models.view.sdui import AnySduiBlock

logger = logging.getLogger(__name__)

STANDARD_MATRIX_VISIBLE_COLUMNS: list[str] = [
    "label",
    "distribution",
    "row_explanation",
    "criteria",
    "normalized_score",
]

__all__ = ["OutputProfile", "STANDARD_MATRIX_VISIBLE_COLUMNS"]


class OutputProfile(V2CoreBase):
    """A distinct report variant containing a sequence of layout blocks."""

    model_config = ConfigDict(strict=True, extra="forbid")

    id: Annotated[str, Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Unique Profile ID")]
    slug: Annotated[str, Field(min_length=1, pattern=r"^[a-zA-Z0-9_\-]+$", description="Fallback slug identifier")]
    workflow_id: Annotated[str, Field(description="ID of the associated Workflow")]
    organization_id: Annotated[
        str,
        Field(
            pattern=OPAQUE_STRIPE_ID_REGEX,
            description="Owning tenant organization ID (org_<hex32>).",
        ),
    ]
    name: Annotated[
        I18nText,
        Field(description="Localized name of the profile (e.g. {'fi': 'Johdon tiivistelmä'})"),
    ]
    description: Annotated[I18nText | None, Field(default=None, description="Detailed profile context")] = None
    user_role_label: Annotated[
        I18nText | None,
        Field(
            default=None,
            description="Optional localized label prefixing the user role context (e.g., 'Target audience:').",
        ),
    ] = None
    custom_preface: Annotated[
        I18nText | None,
        Field(default=None, description="Rich text preface shown at the very beginning of the report."),
    ] = None
    language: Annotated[LaxSystemLocale | None, Field(default=None, description="Target output language.")] = None
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
            default_factory=lambda: list(STANDARD_MATRIX_VISIBLE_COLUMNS),
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
            description="Max number of items to show per grouped XAI extension.",
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
    matrix_graph_length_constraint: Annotated[
        int | None,
        Field(
            default=None,
            ge=50,
            le=2000,
            description="Max character length for each individual matrix graph causal explanation.",
        ),
    ] = None
    max_quotes_per_matrix: Annotated[
        int | None,
        Field(default=None, description="Per-profile override for quotes per matrix in explanations."),
    ] = None
    max_unmet_criteria: Annotated[
        int | None,
        Field(default=None, description="Per-profile override for unmet criteria per matrix."),
    ] = None
    target_block_order: Annotated[
        list[LaxTargetBlockType],
        Field(
            default_factory=lambda: [
                TargetBlockType.METADATA_BLOCK,
                TargetBlockType.EXECUTIVE_SUMMARY_BLOCK,
                TargetBlockType.GLOBAL_SCORE_BLOCK,
                TargetBlockType.SYNTHESIS_TEXT_BLOCK,
                TargetBlockType.MATRIX_GRAPHS_BLOCK,
                TargetBlockType.GROUPED_EXTENSIONS_BLOCK,
                TargetBlockType.PENALTIES_BLOCK,
                TargetBlockType.MATRIX_SUMMARY_TABLE_BLOCK,
                TargetBlockType.PRINTABLE_SOURCES_BLOCK,
                TargetBlockType.AUDIT_TRAIL_BLOCK,
            ],
            description=(
                "The exact dynamic block sequence for the SDUI output. Drives the dispatch loop in blueprint.py."
            ),
        ),
    ]
    matrix_synthesis_groups: Annotated[
        list[MatrixSynthesisGroup],
        Field(
            default_factory=list,
            description="Optional matrix synthesis groups for 2D/3D comparative graphs.",
        ),
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
    variance_target_block: Annotated[
        str | None,
        Field(
            default=None,
            pattern=OPAQUE_STRIPE_ID_REGEX,
            description="PromptBlock ID providing the cognitive evaluation score for variance validation.",
        ),
    ] = None
    user_role_target_block: Annotated[
        str | None,
        Field(
            default=None,
            pattern=OPAQUE_STRIPE_ID_REGEX,
            description="PromptBlock ID providing evaluated score for user role classification.",
        ),
    ] = None

    @field_validator("organization_id")
    @classmethod
    def _validate_organization_id(cls, v: str) -> str:
        """Validate that organization_id uses the canonical org_ prefix and RFC 9562 UUIDv7 format.

        Args:
            v: Candidate organization identifier string.

        Returns:
            Validated organization identifier string.

        Raises:
            ValueError: If organization_id fails org_<hex32> UUIDv7 validation.
        """
        try:
            parse_prefixed_uuid7(v, EntityPrefix.ORGANIZATION)
        except AppException as exc:
            raise ValueError(exc.message) from exc
        return v

    @field_validator("variance_target_block", "user_role_target_block")
    @classmethod
    def _validate_target_prompt_block_ids(cls, v: str | None) -> str | None:
        """Validate optional target block references against canonical blk_ UUIDv7 format.

        Args:
            v: Optional candidate prompt block identifier string.

        Returns:
            Validated prompt block identifier string, or None.

        Raises:
            ValueError: If v fails blk_<hex32> UUIDv7 validation.
        """
        if v is None:
            return None
        try:
            parse_prefixed_uuid7(v, EntityPrefix.PROMPT_BLOCK)
        except AppException as exc:
            raise ValueError(exc.message) from exc
        return v

    @model_validator(mode="after")
    def validate_variance_target_block_coherence(self) -> Self:
        """Enforce that variance_target_block is populated if variance validation is active.

        Returns:
            Validated OutputProfile instance.

        Raises:
            ValueError: If ErrorCodes.VALIDATION_FAILED is triggered due to missing variance_target_block.
        """
        has_variance_block = any(
            t
            in (
                TargetBlockType.VARIANCE_VALIDATION_BLOCK,
                TargetBlockType.VARIANCE_VALIDATION_BLOCK.value,
                "variance_validation_block",
            )
            for t in self.target_block_order
        )
        has_variance_extension = any(
            ext
            in (
                XaiExtensionType.VARIANCE_VALIDATION,
                XaiExtensionType.VARIANCE_VALIDATION.value,
                "variance_validation",
            )
            for ext in self.visible_workflow_extensions
        )
        if (has_variance_block or has_variance_extension) and not self.variance_target_block:
            msg = (
                f"OutputProfile '{self.id}': Variance validation is active (in target_block_order or "
                "visible_workflow_extensions) but 'variance_target_block' is missing or empty."
            )
            logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def validate_matrix_graphs_coherence(self) -> Self:
        """Enforce that matrix_synthesis_groups is populated if MATRIX_GRAPHS_BLOCK is in target_block_order.

        Returns:
            Validated OutputProfile instance.

        Raises:
            ValueError: If ErrorCodes.VALIDATION_FAILED is triggered due to empty matrix_synthesis_groups.
        """
        has_matrix_graphs = any(
            t in (TargetBlockType.MATRIX_GRAPHS_BLOCK, TargetBlockType.MATRIX_GRAPHS_BLOCK.value, "matrix_graphs_block")
            for t in self.target_block_order
        )
        if has_matrix_graphs and len(self.matrix_synthesis_groups) < 1:
            msg = (
                f"OutputProfile '{self.id}': MATRIX_GRAPHS_BLOCK is present in target_block_order "
                "but matrix_synthesis_groups is empty. At least one MatrixSynthesisGroup is required."
            )
            logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def validate_custom_scale_bounds(self) -> Self:
        """Enforce that custom scale bounds are valid when display_scale is CUSTOM.

        Returns:
            Validated OutputProfile instance.

        Raises:
            ValueError: If ErrorCodes.VALIDATION_FAILED is triggered due to missing or inverted scale bounds.
        """
        if self.display_scale in (DisplayScale.CUSTOM, "custom"):
            if self.custom_scale_min is None or self.custom_scale_max is None:
                msg = (
                    f"OutputProfile '{self.id}': custom_scale_min and custom_scale_max "
                    "are required when display_scale is CUSTOM."
                )
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
            if self.custom_scale_max <= self.custom_scale_min:
                msg = (
                    f"OutputProfile '{self.id}': custom_scale_max ({self.custom_scale_max}) "
                    f"must be strictly greater than custom_scale_min ({self.custom_scale_min})."
                )
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
        return self

    @field_validator("matrix_visible_columns")
    @classmethod
    def validate_matrix_visible_columns(cls, v: list[str]) -> list[str]:
        """Enforce that all visible columns match valid ReportMatrixColumn members Fail-Fast.

        Args:
            v: Candidate list of matrix visible column identifiers.

        Returns:
            Validated list of matrix visible column identifiers.

        Raises:
            ValueError: If any column string is not a valid ReportMatrixColumn member.
        """
        for col in v:
            ReportMatrixColumn(col)
        return v

    @property
    def requires_executive_synthesis(self) -> bool:
        """Check if executive summary synthesis is requested in target block order.

        Returns:
            True if EXECUTIVE_SUMMARY_BLOCK is present in target_block_order.
        """
        return any(
            t
            in (
                TargetBlockType.EXECUTIVE_SUMMARY_BLOCK,
                TargetBlockType.EXECUTIVE_SUMMARY_BLOCK.value,
                "executive_summary_block",
            )
            for t in self.target_block_order
        )

    @property
    def requires_group_synthesis(self) -> bool:
        """Check if comparative matrix groups synthesis is requested.

        Returns:
            True if MATRIX_GRAPHS_BLOCK is active and matrix_synthesis_groups is non-empty.
        """
        return (
            any(
                t
                in (
                    TargetBlockType.MATRIX_GRAPHS_BLOCK,
                    TargetBlockType.MATRIX_GRAPHS_BLOCK.value,
                    "matrix_graphs_block",
                )
                for t in self.target_block_order
            )
            and len(self.matrix_synthesis_groups) > 0
        )

    @property
    def requires_row_explanations(self) -> bool:
        """Check if row explanations are configured in visible matrix columns.

        Returns:
            True if 'row_explanation' is present in matrix_visible_columns.
        """
        if not self.matrix_visible_columns:
            return False
        return "row_explanation" in self.matrix_visible_columns

    @model_validator(mode="after")
    def validate_matrix_group_ids_unique(self) -> Self:
        """Enforce that all MatrixSynthesisGroup IDs in matrix_synthesis_groups are strictly unique.

        Returns:
            Validated OutputProfile instance.

        Raises:
            ValueError: If ErrorCodes.VALIDATION_FAILED is triggered due to duplicate synthesis group IDs.
        """
        seen_ids: set[str] = set()
        duplicate_ids: list[str] = []
        for grp in self.matrix_synthesis_groups:
            if grp.id in seen_ids:
                duplicate_ids.append(grp.id)
            seen_ids.add(grp.id)
        if duplicate_ids:
            msg = (
                f"OutputProfile '{self.id}': Duplicate synthesis group IDs detected in "
                f"matrix_synthesis_groups: {duplicate_ids}. All group IDs must be strictly unique."
            )
            logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise ValueError(msg)
        return self

    @property
    def is_synthesis_expected(self) -> bool:
        """Check if any synthesis phase generation is expected for this profile.

        Returns:
            True if executive, group, or row explanation synthesis is required.
        """
        return self.requires_executive_synthesis or self.requires_group_synthesis or self.requires_row_explanations


from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO

OutputProfile.model_rebuild(
    _types_namespace={
        "MatrixScorecardRowDTO": MatrixScorecardRowDTO,
        "MCPAuditTrace": MCPAuditTrace,
        "AnySduiBlock": AnySduiBlock,
    }
)
