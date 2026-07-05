from enum import Enum
from typing import Annotated, Any, Literal

from pydantic import AliasChoices, ConfigDict, Field, StringConstraints

from backend_v2.models.core_base import V2CoreBase

StrictStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class SectionType(str, Enum):
    """Enum representing the Server-Driven UI section layout types."""

    SCORE_CARD = "SCORE_CARD"
    MARKDOWN_BLOCK = "MARKDOWN_BLOCK"
    TIMELINE_FEED = "TIMELINE_FEED"
    HEADER = "HEADER"
    KEY_METRICS = "KEY_METRICS"
    EVIDENCE_LIST = "EVIDENCE_LIST"
    KEY_VALUE_GRID = "KEY_VALUE_GRID"
    DATA_TABLE = "DATA_TABLE"
    ACCORDION = "ACCORDION"
    USAGE_STATS = "USAGE_STATS"
    HIGHLIGHT_BOXES = "HIGHLIGHT_BOXES"
    LOGIC_ANALYSIS = "LOGIC_ANALYSIS"
    STRESS_TEST = "STRESS_TEST"
    CAUSAL_ANALYSIS = "CAUSAL_ANALYSIS"
    PERFORMATIVITY_CHECK = "PERFORMATIVITY_CHECK"
    FACT_CHECK = "FACT_CHECK"
    PROFILER_ANALYSIS = "PROFILER_ANALYSIS"
    ARCHIVIST_CHECK = "ARCHIVIST_CHECK"
    DRIVER_PROFILE = "DRIVER_PROFILE"
    SECURITY_CHECK = "SECURITY_CHECK"


class Authenticity(str, Enum):
    """Enum representing driver authenticity levels."""

    ORGANIC = "AUTH_ORGANIC"
    PERFORMATIVE = "AUTH_PERFORMATIVE"
    UNKNOWN = "AUTH_UNKNOWN"


class VerificationResult(str, Enum):
    """Enum representing claim verification states."""

    VERIFIED = "VER_VERIFIED"
    DEBUNKED = "VER_DEBUNKED"
    UNCERTAIN = "VER_UNCERTAIN"


class ReferenceIntent(str, Enum):
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

    id: StrictStr = Field(..., description="Citation ID, e.g., H-1, F-1")
    intent: ReferenceIntent = Field(..., description="Type of the reference source")
    title: str | None = Field(default=None, description="Title of the source")
    snippet: StrictStr = Field(..., description="Extracted content, relevance, or reasoning")
    url: str | None = Field(default=None, description="Link to the source if available")


class EvidenceItem(V2CoreBase):
    """Strict View Model for a single piece of Evidence.

    Attributes:
        id: Unique evidence identifier.
        source: Source designation.
        content: Raw textual content.
        score: Extracted validation score.
        type: Type mapping string.
    """

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

    content: StrictStr


class HighlightBoxDisplay(V2CoreBase):
    """Server-Driven UI Data for a highlighted XAI extension box.

    Attributes:
        content: Visual highlight message content.
        color_theme: Color presentation semantic intent.
        icon_name: Semantic display icon helper.
    """

    content: StrictStr
    color_theme: Literal["danger", "info", "warning", "success", "primary"] = Field(
        default="info", description="UI background color class"
    )
    icon_name: str | None = Field(default=None, description="e.g. 'shield', 'warning', 'psychology'")


class EvidenceList(V2CoreBase):
    """Server-Driven UI Data for Evidence List.

    Attributes:
        items: Collection of compiled EvidenceItems.
        total_count: Total amount of scanned pieces of evidence.
    """

    items: list[EvidenceItem]
    total_count: int


class UiSection(V2CoreBase):
    """Abstract UI Section mapped via Server-Driven UI schemas.

    Attributes:
        id: Section unique logical string.
        type: Presentational render type of component.
        title: Globalized human visible header key.
        data: Highly flexible context payloads.
    """

    id: StrictStr = Field(..., description="Unique identifier for the section (e.g. 'verdict-card')")
    type: SectionType = Field(..., description="Determines which UI component to render")
    title: StrictStr = Field(..., description="User-facing title of the section")
    data: Any = Field(
        default_factory=dict, description="Flexible payload specific to the section type (dict or Pydantic Model)"
    )


class SystemNotification(V2CoreBase):
    """Server-Driven Notification for the Report Header.

    Attributes:
        title: Notification header context.
        message: Underlying textual telemetry or notification message.
        level: Severe level indicators.
    """

    title: StrictStr
    message: StrictStr
    level: StrictStr = "info"


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

    view_id: StrictStr = Field(..., description="The Execution ID")
    title: StrictStr = Field(default="Auditintiraportti", description="Page title")
    status_theme: StrictStr = Field(default="success", description="Visual theme: 'success' | 'warning' | 'danger'")
    sections: list[UiSection] = Field(default_factory=list, description="Ordered list of UI sections")
    metrics: dict[str, Any] | None = Field(default=None, description="Global audit metrics (Word Count, etc.)")
    system_notification: SystemNotification | None = Field(default=None, description="Global notification/warning")
    references: list[ReferenceItem] = Field(default_factory=list, description="Global bibliography and references")


class StepProgressItem(V2CoreBase):
    """Progress indicator for a single step (BFF).

    Attributes:
        id: System node ID identifier.
        label: Translated title reference.
        status: Execution lifecycle state mapping.
    """

    id: StrictStr = Field(..., description="Step ID (e.g. step_guard)")
    label: StrictStr = Field(..., description="Human-readable label")
    status: StrictStr = Field(..., description="Status: pending, running, completed, failed")


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

    sessionId: StrictStr = Field(..., description="Execution ID")
    statusLabel: StrictStr = Field(..., description="Human-readable status")
    uiVariant: Literal["default", "success", "warning", "error", "neutral"] = Field(
        ..., description="UI Theme: default, success, warning, error, neutral"
    )
    statusMessage: StrictStr = Field(..., description="Contextual status message")
    showWarningBanner: bool = Field(default=False, description="Whether to show warning banner")
    steps: list[StepProgressItem] = Field(default_factory=list, description="Ordered list of steps with status")
    finalScore: int | None = Field(default=None, description="Final score if available")


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

    claim: StrictStr
    data: StrictStr
    warrant: StrictStr
    backing: str | None = None
    rebuttal: str | None = None
    qualifier: str | None = None


class LogicAnalysisDisplay(V2CoreBase):
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
    """Strict View Model for a single Heuristic validation check."""

    name: StrictStr
    flag: bool
    color: StrictStr


class PerformativityDisplay(V2CoreBase):
    """Server-Driven UI Data for Performativity Check."""

    authenticity_score: float | None = None
    authenticity_percent: float | None = None
    authenticity_assessment: str | None = None
    authenticity_help: str | None = None
    heuristics: list[HeuristicDisplay]


class CausalDisplay(V2CoreBase):
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
    """Strict View Model for a Verified Fact."""

    claim: str | None = None
    source: str | None = None
    color: str
    label_key: str
    label: str | None = None
    verification_result: str | None = None
    is_verified: bool | None = None


class EthicalIssueDisplay(V2CoreBase):
    """Strict View Model for an Ethical Issue detected in context."""

    issue_type: str | None = None
    description: str | None = None
    color: str
    label_key: str
    label: str | None = None
    is_critical: bool
    severity: str | None = None


class FactCheckDisplay(V2CoreBase):
    """Server-Driven UI Data for Fact & Ethics Check."""

    fact_checks: list[VerifiedFactDisplay]
    ethical_issues: list[EthicalIssueDisplay]


class SecurityDisplay(V2CoreBase):
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
    """Single finding for Walton Falsification Stress Test."""

    question: StrictStr
    result_label: StrictStr
    is_held: bool
    color_class: StrictStr
    text_class: StrictStr
    observation: StrictStr


class FidelityAudit(V2CoreBase):
    """Strict View Model for Fidelity Audit."""

    fidelity_score_display: str
    fidelity_percent: float | None = None
    fidelity_label: str
    post_hoc_rationalization_suspected: bool
    reasoning: str


class StressTestDisplay(V2CoreBase):
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
    """Server-Driven UI for Archivist Check."""

    compliance_score: float | None = None
    compliance_score_display: str | None = None
    compliance_analysis: str | None = None
    compliance_help: str | None = None
    recommendations: list[str]


class DimensionDisplay(V2CoreBase):
    """Strict View Model for a single Scoring Dimension."""

    dimension_id: str
    dimension_label: str
    score: float
    max_score: float
    weight: float
    reasoning: str


class ScoreCardDisplay(V2CoreBase):
    """Server-Driven UI Data for Judge Score Card."""

    agent_name: str
    total_score: float
    min_score: int
    max_score: int
    verdict: str
    dimensions: list[DimensionDisplay] = Field(default_factory=list)


class DriverProfileDisplay(V2CoreBase):
    """Server-Driven UI for Driver Profile."""

    role_classification: str
    high_dependency: bool
    imperative_command_count: int
    strategy: str
    input_control_ratio: float | None = None


class SduiBlockBase(V2CoreBase):
    """Base schema for SDUI Polymorphic Blocks."""

    block_type: str


class HeroInsightBlock(SduiBlockBase):
    """Specific block for Hero Insights."""

    model_config = ConfigDict(title="hero_insight")
    block_type: Literal["hero_insight"] = "hero_insight"
    exact_quotes: list[str] = Field(default_factory=list)


class ParagraphBlock(SduiBlockBase):
    """A standard text paragraph with optional citations."""

    model_config = ConfigDict(title="paragraph")
    block_type: Literal["paragraph"] = "paragraph"
    text: str = Field(validation_alias=AliasChoices("text", "content"))
    exact_quotes: list[str] = Field(default_factory=list)
    citations: list[int] = Field(default_factory=list)


class BulletListItem(V2CoreBase):
    """Helper model for a single item within a bullet list."""

    text: str = Field(validation_alias=AliasChoices("text", "content"))
    exact_quotes: list[str] = Field(default_factory=list)
    citations: list[int] = Field(default_factory=list)


class BulletListBlock(SduiBlockBase):
    """A bullet list containing multiple items."""

    model_config = ConfigDict(title="bullet_list")
    block_type: Literal["bullet_list"] = "bullet_list"
    items: list[BulletListItem]


class AlertBlock(SduiBlockBase):
    """An alert box for highlighting important information."""

    model_config = ConfigDict(title="alert_box")
    block_type: Literal["alert_box"] = "alert_box"
    severity: Literal["info", "warning"]
    text: str = Field(validation_alias=AliasChoices("text", "content"))
    exact_quotes: list[str] = Field(default_factory=list)
    citations: list[int] = Field(default_factory=list)


class MarkdownBlock(SduiBlockBase):
    """Direct Markdown rendering block, bypassing structural SDUI templates.

    Used strictly for static Admin texts (like preambles) and legacy V1 data,
    NOT for dynamic LLM content generation to preserve the UI structural mandate.
    """

    model_config = ConfigDict(title="markdown")
    block_type: Literal["markdown"] = "markdown"
    text: StrictStr = Field(
        ..., validation_alias=AliasChoices("text", "content"), description="The exact markdown string to be rendered."
    )


class SduiQuoteCard(SduiBlockBase):
    """SDUI component representing a valid quote evidence."""

    model_config = ConfigDict(title="quote_card")
    block_type: Literal["quote_card"] = "quote_card"
    quote: str = Field(..., description="The exact text of the quote.")
    source_aliases: list[str] = Field(default_factory=list, description="Resolved source aliases.")


class SduiWarningCard(SduiBlockBase):
    """SDUI component representing a warning message (e.g. hallucinated alias)."""

    model_config = ConfigDict(title="warning_card")
    block_type: Literal["warning_card"] = "warning_card"
    message: str = Field(..., description="Warning message for the user.")
    quote_text: str | None = Field(default=None, description="The original quote text that triggered the warning.")


AnySduiBlock = Annotated[
    HeroInsightBlock | ParagraphBlock | BulletListBlock | AlertBlock | MarkdownBlock | SduiQuoteCard | SduiWarningCard,
    Field(discriminator="block_type"),
]
