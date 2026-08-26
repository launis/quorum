from enum import StrEnum
from typing import Annotated, Any, Literal

from pydantic import AliasChoices, ConfigDict, Field, StringConstraints

from backend_v2.models.core_base import I18nText, V2CoreBase
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO
from backend_v2.models.enums import LaxUiVariant, LaxVisualIntent, LaxXaiExtensionType, VisualIntent

StrictStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class Authenticity(StrEnum):
    """Enum representing driver authenticity levels."""

    ORGANIC = "AUTH_ORGANIC"
    PERFORMATIVE = "AUTH_PERFORMATIVE"
    UNKNOWN = "AUTH_UNKNOWN"


class VerificationResult(StrEnum):
    """Enum representing claim verification states."""

    VERIFIED = "VER_VERIFIED"
    DEBUNKED = "VER_DEBUNKED"
    UNCERTAIN = "VER_UNCERTAIN"


class ReferenceIntent(StrEnum):
    """Enum representing the strategic intent of a contextual citation reference."""

    SEARCH = "SEARCH"
    GROUNDING = "GROUNDING"
    INTERNAL_KB = "INTERNAL_KB"


class ReferenceItem(V2CoreBase):
    """Strict View Model for a single Contextual Citation.

    Attributes:
        id: Citation ID, e.g., H-1, F-1.
        intent: Type of the reference source.
        title: Title of the source.
        snippet: Extracted content, relevance, or reasoning.
        url: Link to the source if available.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    id: Annotated[StrictStr, Field(..., description="Citation ID, e.g., H-1, F-1")]
    intent: Annotated[ReferenceIntent, Field(..., description="Type of the reference source")]
    title: Annotated[str | None, Field(default=None, description="Title of the source")]
    snippet: Annotated[StrictStr, Field(..., description="Extracted content, relevance, or reasoning")]
    url: Annotated[str | None, Field(default=None, description="Link to the source if available")]


class EvidenceItem(V2CoreBase):
    """Strict View Model for a single piece of Evidence.

    Attributes:
        id: Unique evidence identifier.
        source: Source designation.
        content: Raw textual content.
        score: Extracted validation score.
        type: Type mapping string.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    id: StrictStr
    source: StrictStr
    content: StrictStr
    score: float | None = None
    type: StrictStr


class MarkdownBlockDisplay(V2CoreBase):
    """Server-Driven UI Data for Markdown Content.

    Attributes:
        content: Markdown formatted raw content.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    content: StrictStr


class HighlightBoxDisplay(V2CoreBase):
    """Server-Driven UI Data for a highlighted XAI extension box.

    Attributes:
        content: Visual highlight message content.
        color_theme: Color presentation semantic intent.
        icon_name: Semantic display icon helper.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    content: StrictStr
    color_theme: Annotated[
        Literal["danger", "info", "warning", "success", "primary"],
        Field(default="info", description="UI background color class"),
    ]
    icon_name: Annotated[str | None, Field(default=None, description="e.g. 'shield', 'warning', 'psychology'")]


class EvidenceList(V2CoreBase):
    """Server-Driven UI Data for Evidence List.

    Attributes:
        items: Collection of compiled EvidenceItems.
        total_count: Total amount of scanned pieces of evidence.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    items: list[EvidenceItem]
    total_count: int


class SystemNotification(V2CoreBase):
    """Server-Driven Notification for the Report Header.

    Attributes:
        title: Notification header context.
        message: Underlying textual telemetry or notification message.
        level: Severe level indicators.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    title: StrictStr
    message: StrictStr
    level: StrictStr = "info"


class SectionType(StrEnum):
    SCORE_CARD = "SCORE_CARD"
    MARKDOWN_BLOCK = "MARKDOWN_BLOCK"
    USAGE_STATS = "USAGE_STATS"
    MATRIX_BLOCK = "MATRIX_BLOCK"


class UiSection(V2CoreBase):
    model_config = ConfigDict(strict=True, extra="forbid")
    id: str
    type: SectionType
    title: str
    data: Any


class ReportView(V2CoreBase):
    """Top-level View Model for the Execution Report mapped strictly for client rendering.

    Attributes:
        view_id: Session Execution unique identifier.
        title: Localization title key reference.
        status_theme: Status color theme indicator.
        sections: Array of polymorphic UI rendering nodes.
        metrics: Extra global key-value performance indicators.
        system_notification: Global alerts if applicable.
        references: Structured citations matrix.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    view_id: Annotated[StrictStr, Field(..., description="The Execution ID")]
    title: Annotated[StrictStr, Field(default="Auditintiraportti", description="Page title")] = "Auditintiraportti"
    status_theme: Annotated[
        VisualIntent, Field(default=VisualIntent.SUCCESS, description="Visual theme: 'success' | 'warning' | 'danger'")
    ]
    sections: Annotated[
        list[UiSection], Field(default_factory=list, description="Legacy sections array for backward compatibility")
    ]
    inner_sdui_blocks: Annotated[
        list[AnySduiBlock], Field(default_factory=list, description="Ordered list of SDUI components")
    ]
    metrics: Annotated[
        dict[str, Any] | None, Field(default=None, description="Global audit metrics (Word Count, etc.)")
    ]
    system_notification: Annotated[
        SystemNotification | None, Field(default=None, description="Global notification/warning")
    ] = None
    references: Annotated[
        list[ReferenceItem], Field(default_factory=list, description="Global bibliography and references")
    ] = Field(default_factory=list)


class StepProgressItem(V2CoreBase):
    """Progress indicator for a single step (BFF).

    Attributes:
        id: System node ID identifier.
        label: Translated title reference.
        status: Execution lifecycle state mapping.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    id: Annotated[StrictStr, Field(..., description="Step ID (e.g. step_guard)")]
    label: Annotated[StrictStr, Field(..., description="Human-readable label")]
    status: Annotated[StrictStr, Field(..., description="Status: pending, running, completed, failed")]


class AssessmentView(V2CoreBase):
    """BFF View Model for the Execution Monitor.

    Attributes:
        sessionId: Unique session identifier.
        statusLabel: Localization key text for progress status.
        uiVariant: UI display style.
        statusMessage: Detailed diagnostic status context.
        showWarningBanner: Condition for displaying alerts.
        steps: Pipeline steps list for stepper visualizations.
        finalScore: Overall computed math scoring.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    sessionId: Annotated[StrictStr, Field(..., description="Execution ID")]
    statusLabel: Annotated[StrictStr, Field(..., description="Human-readable status")]
    uiVariant: Annotated[
        LaxUiVariant,
        Field(..., description="UI Theme: default, success, warning, error, neutral"),
    ]
    statusMessage: Annotated[StrictStr, Field(..., description="Contextual status message")]
    showWarningBanner: Annotated[bool, Field(default=False, description="Whether to show warning banner")]
    steps: Annotated[
        list[StepProgressItem], Field(default_factory=list, description="Ordered list of steps with status")
    ]
    finalScore: Annotated[int | None, Field(default=None, description="Final score if available")]


class ToulminDisplay(V2CoreBase):
    """Strict View Model for Toulmin Arguments.

    Attributes:
        claim: Core argument assertion statement.
        data: Underpinning evidence or grounding inputs.
        warrant: Logic bridge linking data to claim.
        backing: Support credentials for validation.
        rebuttal: Recognized exceptions or constraints.
        qualifier: Force of certainty metrics.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    claim: StrictStr
    data: StrictStr
    warrant: StrictStr
    backing: str | None = None
    rebuttal: str | None = None
    qualifier: str | None = None


class LogicAnalysisDisplay(V2CoreBase):
    model_config = ConfigDict(strict=True, extra="forbid")
    """Server-Driven UI Data for Logic Analysis Section."""

    bloom_score: float | None = None
    bloom_percent: float | None = None
    bloom_label_key: str | None = None
    bloom_help: str | None = None
    strategic_score: float | None = None
    strategic_score_display: str | None = None
    strategic_percent: float | None = None
    strategic_percent_display: str | None = None
    strategic_label_key: str | None = None
    strategic_help: str | None = None
    toulmin_score: float | None = None
    toulmin_percent: float | None = None
    toulmin_help: str | None = None
    quadrant_key: str | None = None
    quadrant_label_key: str | None = None
    position_label: str | None = None
    bloom_level_raw: str | None = None
    strategic_depth_raw: str | None = None
    arguments: list[ToulminDisplay]


class HeuristicDisplay(V2CoreBase):
    model_config = ConfigDict(strict=True, extra="forbid")
    """Strict View Model for a single Heuristic validation check."""

    name: StrictStr
    flag: bool
    color: StrictStr


class PerformativityDisplay(V2CoreBase):
    model_config = ConfigDict(strict=True, extra="forbid")
    """Server-Driven UI Data for Performativity Check."""

    authenticity_score: float | None = None
    authenticity_percent: float | None = None
    authenticity_assessment: str | None = None
    authenticity_help: str | None = None
    heuristics: list[HeuristicDisplay]


class CausalDisplay(V2CoreBase):
    model_config = ConfigDict(strict=True, extra="forbid")
    """Server-Driven UI Data for Causal Analysis and counterfactual simulation."""

    abductive_score: float | None = None
    abductive_score_display: str | None = None
    abductive_percent: float | None = None
    abductive_percent_display: str | None = None
    abductive_conclusion: str | None = None
    abductive_help: str | None = None
    plausibility_score: float | None = None
    plausibility_score_display: str | None = None
    plausibility_percent: float | None = None
    plausibility_percent_display: str | None = None
    plausibility_label: str | None = None
    counterfactual_actual: str | None = None
    counterfactual_simulated: str | None = None
    observation: str | None = None
    hypothesis: str | None = None
    score: float | None = None
    verdict: str | None = None


class VerifiedFactDisplay(V2CoreBase):
    model_config = ConfigDict(strict=True, extra="forbid")
    """Strict View Model for a Verified Fact."""

    claim: str | None = None
    source: str | None = None
    color: str
    label_key: str
    label: str | None = None
    verification_result: str | None = None
    is_verified: bool | None = None


class EthicalIssueDisplay(V2CoreBase):
    model_config = ConfigDict(strict=True, extra="forbid")
    """Strict View Model for an Ethical Issue detected in context."""

    issue_type: str | None = None
    description: str | None = None
    color: str
    label_key: str
    label: str | None = None
    is_critical: bool
    severity: str | None = None


class FactCheckDisplay(V2CoreBase):
    model_config = ConfigDict(strict=True, extra="forbid")
    """Server-Driven UI Data for Fact & Ethics Check."""

    fact_checks: list[VerifiedFactDisplay]
    ethical_issues: list[EthicalIssueDisplay]


class SecurityDisplay(V2CoreBase):
    model_config = ConfigDict(strict=True, extra="forbid")
    """Server-Driven UI Data for Security Guard Checks."""

    threat_detected: bool
    threat_color: StrictStr
    threat_label: StrictStr
    risk_level: StrictStr
    risk_color: StrictStr
    risk_label: str | None = None
    anonymized: bool
    anonymized_color: StrictStr
    anonymized_label: StrictStr
    findings: list[str]


class StressFindingDisplay(V2CoreBase):
    model_config = ConfigDict(strict=True, extra="forbid")
    """Single finding for Walton Falsification Stress Test."""

    question: StrictStr
    result_label: StrictStr
    is_held: bool
    color_class: StrictStr
    text_class: StrictStr
    observation: StrictStr


class FidelityAudit(V2CoreBase):
    model_config = ConfigDict(strict=True, extra="forbid")
    """Strict View Model for Fidelity Audit."""

    fidelity_score_display: str
    fidelity_percent: float | None = None
    fidelity_label: str
    post_hoc_rationalization_suspected: bool
    reasoning: str


class StressTestDisplay(V2CoreBase):
    model_config = ConfigDict(strict=True, extra="forbid")
    """Server-Driven UI Data for Stress Test / Falsifier."""

    fidelity_audit: FidelityAudit | None = None
    fidelity_help: str | None = None
    abductive_score: float | None = None
    abductive_percent: float | None = None
    abductive_conclusion: str | None = None
    abductive_help: str | None = None
    counterfactual_actual: str | None = None
    counterfactual_simulated: str | None = None
    plausibility_score: float | None = None
    plausibility_percent: float | None = None
    plausibility_display: str | None = None
    plausibility_help: str | None = None
    findings: list[StressFindingDisplay]


class ProfilerDisplay(V2CoreBase):
    model_config = ConfigDict(strict=True, extra="forbid")
    """Server-Driven UI for Profiler Analysis."""

    control_ratio_percent: float | None = None
    control_label_key: str | None = None
    control_help: str | None = None
    word_count: int
    word_count_display: str | None = None
    word_count_help: str | None = None
    avg_sentence_length: float
    avg_sentence_length_display: str | None = None
    lexical_diversity: float
    lexical_diversity_display: str | None = None
    capitalization_ratio_percent: float | int
    capitalization_ratio_display: str | None = None
    automation_bias_label: str
    automation_bias_color: str
    say_do_gap_label: str
    say_do_gap_color: str
    psychological_profile: str | None = None
    intent_analysis: str | None = None


class ArchivistDisplay(V2CoreBase):
    model_config = ConfigDict(strict=True, extra="forbid")
    """Server-Driven UI for Archivist Check."""

    compliance_score: float | None = None
    compliance_score_display: str | None = None
    compliance_analysis: str | None = None
    compliance_help: str | None = None
    recommendations: list[str]


class DimensionDisplay(V2CoreBase):
    model_config = ConfigDict(strict=True, extra="forbid")
    """Strict View Model for a single Scoring Dimension."""

    dimension_id: str
    dimension_label: str
    score: float
    max_score: float
    weight: float
    reasoning: str


class ScoreCardDisplay(V2CoreBase):
    model_config = ConfigDict(strict=True, extra="forbid")
    """Server-Driven UI Data for Judge Score Card."""

    agent_name: str
    total_score: float
    min_score: int
    max_score: int
    verdict: str
    dimensions: Annotated[list[DimensionDisplay], Field(default_factory=list)]


class DriverProfileDisplay(V2CoreBase):
    model_config = ConfigDict(strict=True, extra="forbid")
    """Server-Driven UI for Driver Profile."""

    role_classification: str
    high_dependency: bool
    imperative_command_count: int
    strategy: str
    input_control_ratio: float | None = None


class SduiBlockBase(V2CoreBase):
    model_config = ConfigDict(strict=True, extra="forbid")
    """Base schema for SDUI Polymorphic Blocks."""

    id: Annotated[str | None, Field(default=None, description="Optional block identifier")] = None
    block_type: str


class HeroInsightBlock(SduiBlockBase):
    """Specific block for Hero Insights."""

    model_config = ConfigDict(title="hero_insight", strict=True, extra="forbid")
    block_type: Literal["hero_insight"] = "hero_insight"
    text: Annotated[str, Field(validation_alias=AliasChoices("text", "content"), default="")]
    exact_quotes: Annotated[list[str], Field(default_factory=list)]
    citations: Annotated[list[int], Field(default_factory=list)]


class ParagraphBlock(SduiBlockBase):
    """A standard text paragraph with optional citations."""

    model_config = ConfigDict(title="paragraph", strict=True, extra="forbid")
    block_type: Literal["paragraph"] = "paragraph"
    text: Annotated[str, Field(validation_alias=AliasChoices("text", "content"))]
    exact_quotes: Annotated[list[str], Field(default_factory=list)]
    citations: Annotated[list[int], Field(default_factory=list)]


class BulletListItem(V2CoreBase):
    model_config = ConfigDict(strict=True, extra="forbid")
    """Helper model for a single item within a bullet list."""

    text: Annotated[str, Field(validation_alias=AliasChoices("text", "content"))]
    exact_quotes: Annotated[list[str], Field(default_factory=list)]
    citations: Annotated[list[int], Field(default_factory=list)]


class BulletListBlock(SduiBlockBase):
    """A bullet list containing multiple items."""

    model_config = ConfigDict(title="bullet_list", strict=True, extra="forbid")
    block_type: Literal["bullet_list"] = "bullet_list"
    items: list[BulletListItem]


class AlertBlock(SduiBlockBase):
    """An alert box for highlighting important information."""

    model_config = ConfigDict(title="alert_box", strict=True, extra="forbid")
    block_type: Literal["alert_box"] = "alert_box"
    severity: Annotated[LaxVisualIntent, Field(default=VisualIntent.INFO)]
    text: Annotated[str, Field(validation_alias=AliasChoices("text", "content"))]
    exact_quotes: Annotated[list[str], Field(default_factory=list)]
    citations: Annotated[list[int], Field(default_factory=list)]


class AccordionBlock(SduiBlockBase):
    """An accordion block for grouping nested SDUI blocks under a collapsible header."""

    model_config = ConfigDict(title="accordion", strict=True, extra="forbid")
    block_type: Literal["accordion"] = "accordion"
    title: Annotated[str, Field(..., description="The title displayed on the accordion header.")]
    severity: Annotated[
        Literal["info", "warning", "critical_override", "success", "error", "default"],
        Field(default="default", description="Color intent for the accordion header."),
    ]
    icon_name: Annotated[str | None, Field(default=None, description="Optional icon name for the header.")]
    children: Annotated[
        list[AnySduiBlock], Field(default_factory=list, description="Nested SDUI blocks inside the accordion.")
    ]


class MarkdownBlock(SduiBlockBase):
    """Direct Markdown rendering block, bypassing structural SDUI templates.

    Used strictly for static Admin texts (like preambles) and legacy V1 data,
    NOT for dynamic LLM content generation to preserve the UI structural mandate.
    """

    model_config = ConfigDict(title="markdown", strict=True, extra="forbid")
    block_type: Literal["markdown"] = "markdown"
    text: Annotated[
        StrictStr,
        Field(
            ...,
            validation_alias=AliasChoices("text", "content"),
            description="The exact markdown string to be rendered.",
        ),
    ]


class SduiQuoteCard(SduiBlockBase):
    """SDUI component representing a valid quote evidence."""

    model_config = ConfigDict(title="quote_card", strict=True, extra="forbid")
    block_type: Literal["quote_card"] = "quote_card"
    quote: Annotated[
        str,
        Field(
            ..., validation_alias=AliasChoices("quote", "text", "content"), description="The exact text of the quote."
        ),
    ]
    source_aliases: Annotated[list[str], Field(default_factory=list, description="Resolved source aliases.")]
    citations: Annotated[
        list[int], Field(default_factory=list, description="Fallback for LLM hallucinated citations field.")
    ]


class SduiWarningCard(SduiBlockBase):
    """SDUI component representing a warning message (e.g. hallucinated alias)."""

    model_config = ConfigDict(title="warning_card", strict=True, extra="forbid")
    block_type: Literal["warning_card"] = "warning_card"
    message: Annotated[str, Field(..., description="Warning message for the user.")]
    quote_text: Annotated[
        str | None, Field(default=None, description="The original quote text that triggered the warning.")
    ]


class SduiNACard(SduiBlockBase):
    """SDUI component representing a Short-Circuit N/A outcome."""

    model_config = ConfigDict(title="n_a_card", strict=True, extra="forbid")
    block_type: Literal["n_a_card"] = "n_a_card"
    short_circuit_reason_tda_ids: Annotated[
        list[str], Field(default_factory=list, description="IDs of the TDAs that triggered N/A.")
    ]
    message: Annotated[str, Field(..., description="Contextual message for the N/A outcome.")]


class SduiGridBlock(SduiBlockBase):
    """SDUI component representing a data grid."""

    model_config = ConfigDict(title="grid", strict=True, extra="forbid")
    block_type: Literal["grid"] = "grid"
    items: Annotated[list[AnySduiBlock], Field(default_factory=list, description="Items in the grid.")]


class SduiMetadataBlock(SduiBlockBase):
    """A visually distinct report header summarizing metadata.

    Attributes:
        title: Main title of the report profile.
        badges: Array of small highlighted pills (e.g., scoring engine, strictness).
        metadata_lines: Array of strings for execution metadata (time, id, user, org).
        costs: Optional formatted cost string.
        tokens: Optional dictionary of token usage strings.
        custom_preface_md: Optional preface markdown text.
    """

    model_config = ConfigDict(title="metadata", strict=True, extra="forbid")
    block_type: Literal["metadata"] = "metadata"
    title: str = Field(..., description="Main title of the report")
    badges: list[str] = Field(default_factory=list, description="Highlighted badges")
    metadata_lines: list[str] = Field(default_factory=list, description="Metadata strings")
    costs: str | None = Field(default=None, description="Formatted cost string")
    tokens: dict[str, str] | None = Field(default=None, description="Token usage details")
    custom_preface_md: str | None = Field(default=None, description="Optional preface markdown")


class SduiScoreCardBlock(SduiBlockBase):
    """SDUI component representing the global score card."""

    model_config = ConfigDict(title="score_card", strict=True, extra="forbid")
    block_type: Literal["score_card"] = "score_card"
    global_score: float | None = Field(default=None, description="The mathematical average extracted.")


class SduiAuditTrailBlock(SduiBlockBase):
    """SDUI component representing the execution audit trail."""

    model_config = ConfigDict(title="audit_trail", strict=True, extra="forbid")
    block_type: Literal["audit_trail"] = "audit_trail"
    # Keeping any structure needed for rendering the audit trail
    # For now, it might be empty or hold hydrated references if passed
    pass


class SduiRadarChartBlock(SduiBlockBase):
    """Specific block for 3D Matrix / Radar Chart visualization."""

    model_config = ConfigDict(title="3d_matrix", strict=True, extra="forbid")
    block_type: Literal["3d_matrix"] = "3d_matrix"
    title: I18nText | None = None
    axes: list[MatrixScorecardRowDTO] = Field(default_factory=list)


class SduiScatterPlotBlock(SduiBlockBase):
    """Specific block for 2D Compare / Scatter Plot visualization."""

    model_config = ConfigDict(title="2d_compare", strict=True, extra="forbid")
    block_type: Literal["2d_compare"] = "2d_compare"
    title: I18nText | None = None
    axes: list[MatrixScorecardRowDTO] = Field(default_factory=list)


class SduiMatrixTableBlock(SduiBlockBase):
    """Specific block for Matrix Summary Table visualization."""

    model_config = ConfigDict(title="matrix_summary", strict=True, extra="forbid")
    block_type: Literal["matrix_summary"] = "matrix_summary"
    title: I18nText | None = None
    axes: list[MatrixScorecardRowDTO] = Field(default_factory=list)
    matrix_column_labels: dict[str, I18nText] = Field(default_factory=dict)
    extension_labels: dict[LaxXaiExtensionType, I18nText] = Field(default_factory=dict)
    matrix_visible_columns: list[str] = Field(default_factory=list)


class SduiMetrics1DBlock(SduiBlockBase):
    """Specific block for 1D Metrics visualization."""

    model_config = ConfigDict(title="1d_metrics", strict=True, extra="forbid")
    block_type: Literal["1d_metrics"] = "1d_metrics"
    title: I18nText | None = None
    axes: list[MatrixScorecardRowDTO] = Field(default_factory=list)


AnySduiBlock = Annotated[
    HeroInsightBlock
    | ParagraphBlock
    | BulletListBlock
    | AlertBlock
    | AccordionBlock
    | MarkdownBlock
    | SduiQuoteCard
    | SduiWarningCard
    | SduiNACard
    | SduiGridBlock
    | SduiMetadataBlock
    | SduiRadarChartBlock
    | SduiScatterPlotBlock
    | SduiMatrixTableBlock
    | SduiMetrics1DBlock
    | SduiScoreCardBlock
    | SduiAuditTrailBlock,
    Field(discriminator="block_type"),
]
