"""Matrix Scorecard Data Transfer Objects.

Decoupled schema definitions for evaluated matrix rows and presentation logic.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Annotated, Any, Literal

from pydantic import ConfigDict, Field, model_validator

from backend_v2.models.core_base import I18nText, V2CoreBase
from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.enums import ExecutionStatus, LaxExecutionStatus, VisualIntent

if TYPE_CHECKING:
    from backend_v2.models.v2_core import MCPAuditTrace
    from backend_v2.models.view.sdui import AnySduiBlock

__all__ = [
    "HumanOverrideDTO",
    "HumanOverrideRequest",
    "MatrixScorecardRowDTO",
    "ScorecardAtomDTO",
    "TDADlq",
    "TDAEvaluated",
    "TDAPending",
    "TDAStateUnion",
]


class HumanOverrideRequest(V2CoreBase):
    """Payload for human override requests.

    Attributes:
        new_status: The overridden status (PASSED, FAILED, SYSTEM_ERROR).
        reason: The reason for the override.
        evidence_quotes: Selected quotes to support the override.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    new_status: Annotated[
        LaxExecutionStatus, Field(description="The overridden status (PASSED, FAILED, SYSTEM_ERROR).")
    ]
    reason: Annotated[str, Field(description="The reason for the override.")]
    evidence_quotes: Annotated[
        list[QuoteEvidenceDTO],
        Field(default_factory=list, description="Selected quotes to support the override."),
    ]


class HumanOverrideDTO(V2CoreBase):
    """Schema for human-initiated state override.

    Attributes:
        new_status: The overridden status (PASSED, FAILED, SYSTEM_ERROR).
        reason: The reason for the override.
        evidence_quotes: Selected quotes to support the override.
        overridden_by: User ID who performed the override.
        overridden_at: Timestamp of the override.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    new_status: Annotated[ExecutionStatus, Field(description="The overridden status (PASSED, FAILED, SYSTEM_ERROR).")]
    reason: Annotated[str, Field(description="The reason for the override.")]
    evidence_quotes: Annotated[list[QuoteEvidenceDTO], Field(description="Selected quotes to support the override.")]
    overridden_by: Annotated[str, Field(description="User ID who performed the override.")]
    overridden_at: Annotated[datetime, Field(description="Timestamp of the override.")]


class ScorecardAtomDTO(V2CoreBase):
    """Explicit DTO firewall for presentation logic of individual atom evaluations.

    Attributes:
        atom_id: Unique atom identifier.
        level: Cognitive evaluation level integer.
        level_name: Display name for the level.
        claim_label: Display claim label.
        extracted_facts: Key-value facts extracted from source.
        exact_quotes: Exact quote evidence items.
        internal_logic_en: Step-by-step reasoning logic.
        status: Evaluation execution status.
        semantic_reasoning: Natural language semantic justification.
        contextual_override: Whether contextual override was applied.
        structural_location: Location reference in source text.
        chart_display_label: Label for chart display.
        visual_intent: Visual theme intent (e.g. WARNING, NEUTRAL).
        human_override: Optional human override details.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    atom_id: Annotated[str, Field(description="Unique atom identifier.")]
    level: Annotated[int, Field(description="Cognitive evaluation level integer.")]
    level_name: Annotated[str, Field(description="Display name for the level.")]
    claim_label: Annotated[str, Field(description="Display claim label.")]
    extracted_facts: Annotated[dict[str, str | None], Field(description="Key-value facts extracted from source.")]
    exact_quotes: Annotated[list[QuoteEvidenceDTO], Field(description="Exact quote evidence items.")]
    internal_logic_en: Annotated[ReasoningStepDTO, Field(description="Step-by-step reasoning logic.")]
    status: Annotated[LaxExecutionStatus | None, Field(description="Evaluation execution status.")]
    semantic_reasoning: Annotated[str, Field(description="Natural language semantic justification.")]
    contextual_override: Annotated[bool, Field(description="Whether contextual override was applied.")]
    structural_location: Annotated[str | None, Field(default=None, description="Location reference in source text.")]
    chart_display_label: Annotated[str, Field(description="Label for chart display.")]
    visual_intent: Annotated[VisualIntent, Field(description="Visual theme intent (e.g. WARNING, NEUTRAL).")]
    human_override: Annotated[
        HumanOverrideDTO | None, Field(default=None, description="Optional human override details.")
    ] = None

    @model_validator(mode="before")
    @classmethod
    def map_contested_to_warning(cls, data: Any) -> Any:
        """Remaps visual intent to WARNING if passed atom has contextual override applied.

        Args:
            data: Raw input dictionary or instance before validation.

        Returns:
            Sanitized dictionary with visual_intent adjusted if contested.
        """
        try:
            d = dict(data)
        except (TypeError, ValueError):  # fmt: skip
            return data

        status_val = d.get("status")
        is_passed = status_val == "PASSED" or status_val == ExecutionStatus.PASSED
        if is_passed and d.get("contextual_override"):
            d["visual_intent"] = VisualIntent.WARNING
        return d


class TDAPending(V2CoreBase):
    """Represents a pending TDA evaluation state.

    Attributes:
        runtimeType: Discriminated union key with value 'pending'.
    """

    model_config = ConfigDict(strict=True, extra="forbid")
    runtimeType: Annotated[Literal["pending"], Field(default="pending", description="Discriminated union key.")]


class TDAEvaluated(V2CoreBase):
    """Represents a completed TDA evaluation state with quote evidence.

    Attributes:
        runtimeType: Discriminated union key with value 'evaluated'.
        passed: Whether evaluation criteria passed.
        display_quote: Formatted quote string for display.
        raw_anchor: Original raw text anchor.
    """

    model_config = ConfigDict(strict=True, extra="forbid")
    runtimeType: Annotated[Literal["evaluated"], Field(default="evaluated", description="Discriminated union key.")]
    passed: Annotated[bool, Field(description="Whether evaluation criteria passed.")]
    display_quote: Annotated[str, Field(description="Formatted quote string for display.")]
    raw_anchor: Annotated[str, Field(description="Original raw text anchor.")]


class TDADlq(V2CoreBase):
    """Represents a failed or dead-letter-queued TDA evaluation state.

    Attributes:
        runtimeType: Discriminated union key with value 'dlq'.
        user_reason: Human-readable failure explanation.
        backend_trace: Technical backend error trace.
    """

    model_config = ConfigDict(strict=True, extra="forbid")
    runtimeType: Annotated[Literal["dlq"], Field(default="dlq", description="Discriminated union key.")]
    user_reason: Annotated[str, Field(description="Human-readable failure explanation.")]
    backend_trace: Annotated[str, Field(description="Technical backend error trace.")]


TDAStateUnion = Annotated[TDAPending | TDAEvaluated | TDADlq, Field(discriminator="runtimeType")]


class MatrixScorecardRowDTO(V2CoreBase):
    """Represents a single evaluated matrix row in the scorecard and plot axes.

    Attributes:
        block_id: The opaque Stripe ID of the prompt block.
        name: Pre-localized name for PDF layouts and static charts.
        label_i18n: Full I18n translations dictionary for the UI.
        description: Detailed instructions or prompt context behind this axis.
        score: Raw scaled score.
        score_display_label: Human-readable score display label.
        scale_min: Minimum possible score.
        scale_max: Maximum possible score.
        normalized_score: Normalized score (0-100) if evaluative.
        true_atoms: Global hits found.
        total_atoms: Total atoms available to evaluate.
        row_explanation: The one-sentence justification.
        evidence_type: The EvidenceType extracted from AtomResponse.
        cited_source_id: Source ID cited.
        cited_text_quote: Quoted text from source.
        cited_web_citation: Web citation link if applicable.
        cited_source_title: Title / citation reference of the theoretical framework.
        cited_source_url: Authoritative external URL for the theoretical framework.
        context_target: Dynamic input file or stream key evaluated.
        context_target_label: Localized human-readable name of the evaluated input target.
        remediation_steps: Concrete actionable remediation steps from XAI extensions.
        coaching: Coaching tips and guidance from XAI extensions.
        falsification: Falsification criteria from XAI extensions.
        confidence: Confidence score of evaluation.
        inner_sdui_blocks: Strict SDUI components rendered for this row.
        contextual_override: Whether contextual override was applied.
        semantic_reasoning: Detailed semantic justification for the override.
        level_breakdown: Breakdown of hits vs total per scale floor.
        level_names: Map of level keys to their human readable names.
        ui_plot_ratio: Absolute normalized plot ratio [0.0 - 1.0].
        ui_boundary_labels: Pre-computed labels for extremes.
        is_evaluative: Whether this block contributes to global average.
        allow_contextual_override: Whether contextual override is allowed.
        used_evidence_ids: Trace IDs used for this row.
        evaluated_atoms: Flat presentation-only atoms evaluated for this row.
        clustered_row_sources: Cluster arrays at row level.
        tda_state: TDAState union representation.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    block_id: Annotated[str, Field(description="The opaque Stripe ID of the prompt block.")]
    name: Annotated[str, Field(description="Pre-localized name for PDF layouts and static charts.")]
    label_i18n: Annotated[I18nText, Field(description="Full I18n translations dictionary for the UI.")]
    description: Annotated[
        str | None,
        Field(default=None, description="Detailed instructions or prompt context behind this axis."),
    ]

    score: Annotated[float | None, Field(default=None, description="Raw scaled score.")]
    score_display_label: Annotated[str | None, Field(default=None, description="Human-readable score display label.")]
    scale_min: Annotated[float | None, Field(default=None, description="Minimum possible score.")]
    scale_max: Annotated[float | None, Field(default=None, description="Maximum possible score.")]
    normalized_score: Annotated[
        float | None, Field(default=None, description="Normalized score (0-100) if evaluative.")
    ]

    true_atoms: Annotated[int | None, Field(default=None, description="Global hits found.")]
    total_atoms: Annotated[int | None, Field(default=None, description="Total atoms available to evaluate.")]
    row_explanation: Annotated[str, Field(description="The one-sentence justification.")]
    evidence_type: Annotated[
        Literal["EXPLICIT_QUOTE", "IMPLIED_INTENT", "NO_EVIDENCE"] | None,
        Field(default=None, description="The EvidenceType extracted from AtomResponse."),
    ]

    cited_source_id: Annotated[str | None, Field(default=None, description="Source ID cited.")]
    cited_text_quote: Annotated[str | None, Field(default=None, description="Quoted text from source.")]
    cited_web_citation: Annotated[str | None, Field(default=None, description="Web citation link if applicable.")]
    cited_source_title: Annotated[
        str | None, Field(default=None, description="Title / citation reference of the theoretical framework.")
    ]
    cited_source_url: Annotated[
        str | None, Field(default=None, description="Authoritative external URL for the theoretical framework.")
    ]

    context_target: Annotated[
        str | None,
        Field(
            default=None,
            description=(
                "Dynamic input file or stream key evaluated, including 'chat_log', 'product_text', or filename."
            ),
        ),
    ] = None
    context_target_label: Annotated[
        I18nText | None,
        Field(default=None, description="Localized human-readable name of the evaluated input target."),
    ] = None
    remediation_steps: Annotated[
        str | None,
        Field(default=None, description="Concrete actionable remediation steps from XAI extensions."),
    ] = None
    coaching: Annotated[
        str | None,
        Field(default=None, description="Coaching tips and guidance from XAI extensions."),
    ] = None
    falsification: Annotated[
        str | None,
        Field(default=None, description="Falsification criteria from XAI extensions."),
    ] = None

    # XAI Output Extensions
    confidence: Annotated[float | None, Field(default=None, description="Confidence score of evaluation.")]

    inner_sdui_blocks: Annotated[
        list[AnySduiBlock],
        Field(default_factory=list, description="Strict SDUI components rendered for this row."),
    ]

    contextual_override: Annotated[
        bool | None, Field(default=None, description="Whether contextual override was applied.")
    ]
    semantic_reasoning: Annotated[
        str | None,
        Field(default=None, description="Detailed semantic justification for the override."),
    ]

    level_breakdown: Annotated[
        dict[str, str] | None,
        Field(default=None, description="Breakdowns: DINA hits vs total per scale floor e.g. {'1.0': '5/5'}."),
    ]

    level_names: Annotated[
        dict[str, str] | None,
        Field(default=None, description="Map of level keys to their human readable names e.g. {'1': 'Heikko'}."),
    ]

    ui_plot_ratio: Annotated[
        float | None,
        Field(default=None, description="Absolute normalized plot ratio [0.0 - 1.0] for mathless Flutter plotting."),
    ]
    ui_boundary_labels: Annotated[
        dict[str, str],
        Field(
            default_factory=dict, description="Pre-computed labels for extremes, e.g. {'0.0': 'Low', '1.0': 'High'}."
        ),
    ]

    is_evaluative: Annotated[bool, Field(description="Whether this block contributes to global average.")]
    allow_contextual_override: Annotated[
        bool, Field(default=False, description="Whether contextual override is allowed on this PromptBlock matrix.")
    ]

    used_evidence_ids: Annotated[list[str], Field(default_factory=list, description="Trace IDs used for this row.")]
    evaluated_atoms: Annotated[
        list[ScorecardAtomDTO],
        Field(default_factory=list, description="Flat presentation-only atoms evaluated for this row."),
    ]
    clustered_row_sources: Annotated[
        list[MCPAuditTrace],
        Field(default_factory=list, description="Purity Paradox resolution, cluster arrays at row level."),
    ]

    tda_state: Annotated[TDAStateUnion | None, Field(default=None, description="TDAState union representation.")]
