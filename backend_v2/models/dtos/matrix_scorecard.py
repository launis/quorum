from __future__ import annotations

"""Matrix Scorecard Data Transfer Objects.

Decoupled schema definitions for evaluated matrix rows and presentation logic.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Annotated, Literal

from pydantic import ConfigDict, Field, model_validator

from backend_v2.models.core_base import I18nText, V2CoreBase
from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.enums import ExecutionStatus, LaxExecutionStatus, VisualIntent

if TYPE_CHECKING:
    from backend_v2.models.v2_core import MCPAuditTrace
    from backend_v2.models.view.sdui import AnySduiBlock


class HumanOverrideRequest(V2CoreBase):
    model_config = ConfigDict(strict=True, extra="forbid")
    """Payload for human override requests."""

    new_status: LaxExecutionStatus = Field(description="The overridden status (PASSED, FAILED, SYSTEM_ERROR).")
    reason: str = Field(description="The reason for the override.")
    evidence_quotes: list[QuoteEvidenceDTO] = Field(
        default_factory=list, description="Selected quotes to support the override."
    )


class HumanOverrideDTO(V2CoreBase):
    model_config = ConfigDict(strict=True, extra="forbid")
    """Schema for human-initiated state override."""

    new_status: ExecutionStatus = Field(description="The overridden status (PASSED, FAILED, SYSTEM_ERROR).")
    reason: str = Field(description="The reason for the override.")
    evidence_quotes: list[QuoteEvidenceDTO] = Field(description="Selected quotes to support the override.")
    overridden_by: str = Field(description="User ID who performed the override.")
    overridden_at: datetime = Field(description="Timestamp of the override.")


class ScorecardAtomDTO(V2CoreBase):
    """Explicit DTO firewall for presentation logic of individual atom evaluations."""

    model_config = ConfigDict(strict=True, extra="forbid")

    atom_id: str
    level: int
    level_name: str
    claim_label: str
    extracted_facts: dict[str, str | None]
    exact_quotes: list[QuoteEvidenceDTO]
    internal_logic_en: ReasoningStepDTO
    status: LaxExecutionStatus | None
    semantic_reasoning: str
    contextual_override: bool
    structural_location: str | None
    chart_display_label: str
    visual_intent: VisualIntent
    human_override: HumanOverrideDTO | None = None

    @model_validator(mode="before")
    @classmethod
    def map_contested_to_warning(cls, data: dict[str, object] | object) -> dict[str, object] | object:
        if isinstance(data, dict):
            status_val = data.get("status")
            is_passed = status_val == "PASSED" or (
                isinstance(status_val, ExecutionStatus) and status_val == ExecutionStatus.PASSED
            )
            if is_passed and data.get("contextual_override"):
                data["visual_intent"] = VisualIntent.WARNING
        return data


class TDAPending(V2CoreBase):
    """Represents a pending TDA evaluation state."""

    model_config = ConfigDict(strict=True, extra="forbid")
    runtimeType: Literal["pending"] = Field(default="pending")


class TDAEvaluated(V2CoreBase):
    """Represents a completed TDA evaluation state with quote evidence."""

    model_config = ConfigDict(strict=True, extra="forbid")
    runtimeType: Literal["evaluated"] = Field(default="evaluated")
    passed: bool
    display_quote: str
    raw_anchor: str


class TDADlq(V2CoreBase):
    """Represents a failed or dead-letter-queued TDA evaluation state."""

    model_config = ConfigDict(strict=True, extra="forbid")
    runtimeType: Literal["dlq"] = Field(default="dlq")
    user_reason: str
    backend_trace: str


TDAStateUnion = Annotated[TDAPending | TDAEvaluated | TDADlq, Field(discriminator="runtimeType")]


class MatrixScorecardRowDTO(V2CoreBase):
    model_config = ConfigDict(strict=True, extra="forbid")
    """Represents a single evaluated matrix row in the scorecard and plot axes."""

    block_id: str = Field(..., description="The opaque Stripe ID of the prompt block.")
    name: str = Field(..., description="Pre-localized name for PDF layouts and static charts.")
    label_i18n: I18nText = Field(..., description="Full I18n translations dictionary for the UI.")
    description: str | None = Field(
        default=None, description="Detailed instructions or prompt context behind this axis."
    )

    score: float | None = Field(default=None, description="Raw scaled score.")
    score_display_label: str | None = None
    scale_min: float | None = Field(default=None, description="Minimum possible score.")
    scale_max: float | None = Field(default=None, description="Maximum possible score.")
    normalized_score: float | None = Field(default=None, description="Normalized score (0-100) if evaluative.")

    true_atoms: int | None = Field(default=None, description="Global hits found.")
    total_atoms: int | None = Field(default=None, description="Total atoms available to evaluate.")
    row_explanation: str = Field(..., description="The one-sentence justification.")
    evidence_type: Literal["EXPLICIT_QUOTE", "IMPLIED_INTENT", "NO_EVIDENCE"] | None = Field(
        default=None, description="The EvidenceType extracted from AtomResponse"
    )

    cited_source_id: str | None = None
    cited_text_quote: str | None = None
    cited_web_citation: str | None = None

    # XAI Output Extensions
    confidence: float | None = None

    inner_sdui_blocks: list[AnySduiBlock] = Field(
        default_factory=list, description="Strict SDUI components rendered for this row."
    )

    contextual_override: bool | None = Field(default=None, description="Whether contextual override was applied.")
    semantic_reasoning: str | None = Field(
        default=None, description="Detailed semantic justification for the override."
    )

    level_breakdown: dict[str, str] | None = Field(
        default=None,
        description="Breakdowns: DINA hits vs total per scale floor e.g. {'1.0': '5/5'}",
    )

    level_names: dict[str, str] | None = Field(
        default=None,
        description="Map of level keys to their human readable names e.g. {'1': 'Heikko'}",
    )

    ui_plot_ratio: float | None = Field(
        default=None, description="Absolute normalized plot plot ratio [0.0 - 1.0] for mathless Flutter plotting"
    )
    ui_boundary_labels: dict[str, str] = Field(
        default_factory=dict, description="Pre-computed labels for extremes, e.g. {'0.0': 'Low', '1.0': 'High'}"
    )

    is_evaluative: bool = Field(..., description="Whether this block contributes to global average.")
    allow_contextual_override: bool = Field(
        default=False, description="Whether contextual override is allowed on this PromptBlock matrix."
    )

    used_evidence_ids: list[str] = Field(default_factory=list, description="Trace IDs used for this row.")
    evaluated_atoms: list[ScorecardAtomDTO] = Field(
        default_factory=list, description="Flat presentation-only atoms evaluated for this row."
    )
    clustered_row_sources: list[MCPAuditTrace] = Field(
        default_factory=list, description="Purity Paradox resolution, cluster arrays at row level."
    )

    tda_state: TDAStateUnion | None = Field(default=None, description="TDAState union representation.")
