from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SectionType(str, Enum):
    SCORE_CARD = "SCORE_CARD"
    MARKDOWN_BLOCK = "MARKDOWN_BLOCK"
    TIMELINE_FEED = "TIMELINE_FEED"
    # Future extensibility
    HEADER = "HEADER"
    KEY_METRICS = "KEY_METRICS"
    EVIDENCE_LIST = "EVIDENCE_LIST"
    KEY_VALUE_GRID = "KEY_VALUE_GRID"  # For structured properties (e.g. Guard flags)
    DATA_TABLE = "DATA_TABLE"  # For lists of rows (e.g. Hypotheses)
    ACCORDION = "ACCORDION"  # For nested details
    USAGE_STATS = "USAGE_STATS"  # Token usage & cost
    HIGHLIGHT_BOXES = "HIGHLIGHT_BOXES"  # Colored XAI Extension boxes top-3 list

    # Specialist Agent Sections (Courtroom 3.0 Backbone)
    LOGIC_ANALYSIS = "LOGIC_ANALYSIS"  # Toulmin & Cognitive Level
    STRESS_TEST = "STRESS_TEST"  # Walton Falsification
    CAUSAL_ANALYSIS = "CAUSAL_ANALYSIS"  # Counterfactuals
    PERFORMATIVITY_CHECK = "PERFORMATIVITY_CHECK"  # Illusion of Competence
    FACT_CHECK = "FACT_CHECK"  # Hallucination & Ethics
    PROFILER_ANALYSIS = "PROFILER_ANALYSIS"  # Biases & Psych Profile
    ARCHIVIST_CHECK = "ARCHIVIST_CHECK"  # Compliance & Precedents
    DRIVER_PROFILE = "DRIVER_PROFILE"  # Interaction / Driver Classification
    SECURITY_CHECK = "SECURITY_CHECK"  # Security / Guard


class Authenticity(str, Enum):
    ORGANIC = "AUTH_ORGANIC"
    PERFORMATIVE = "AUTH_PERFORMATIVE"
    UNKNOWN = "AUTH_UNKNOWN"


class VerificationResult(str, Enum):
    VERIFIED = "VER_VERIFIED"
    DEBUNKED = "VER_DEBUNKED"
    UNCERTAIN = "VER_UNCERTAIN"


class ReferenceIntent(str, Enum):
    SEARCH = "SEARCH"
    GROUNDING = "GROUNDING"
    INTERNAL_KB = "INTERNAL_KB"


class ReferenceItem(BaseModel):
    """Strict View Model for a single Contextual Citation."""

    id: str = Field(..., description="Citation ID, e.g., H-1, F-1")
    intent: ReferenceIntent = Field(..., description="Type of the reference source")
    title: str | None = Field(default=None, description="Title of the source")
    snippet: str = Field(..., description="Extracted content, relevance, or reasoning")
    url: str | None = Field(default=None, description="Link to the source if available")

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")

    @field_validator("id", "snippet")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class EvidenceItem(BaseModel):
    """Strict View Model for a single piece of Evidence."""

    id: str
    source: str
    content: str
    score: float | None
    type: str  # "precedent" | "regulation" | "concept"

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")

    @field_validator("id", "source", "content", "type")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class MarkdownBlockDisplay(BaseModel):
    """Server-Driven UI Data for Markdown Content."""

    content: str

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")

    @field_validator("content")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class HighlightBoxDisplay(BaseModel):
    """Server-Driven UI Data for a highlighted XAI extension box."""

    content: str
    color_theme: Literal["danger", "info", "warning", "success", "primary"] = Field(
        default="info", description="UI background color class"
    )
    icon_name: str | None = Field(default=None, description="e.g. 'shield', 'warning', 'psychology'")

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")

    @field_validator("content")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class EvidenceList(BaseModel):
    """Server-Driven UI Data for Evidence List."""

    items: list[EvidenceItem]
    total_count: int

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")


class UiSection(BaseModel):
    """Abstract UI Section.
    Frontend renders the component based on 'type'.
    """

    id: str = Field(..., description="Unique identifier for the section (e.g. 'verdict-card')")
    type: SectionType = Field(..., description="Determines which UI component to render")
    title: str = Field(..., description="User-facing title of the section")
    data: Any = Field(
        default_factory=dict, description="Flexible payload specific to the section type (dict or Pydantic Model)"
    )

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")

    @field_validator("id", "title")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class SystemNotification(BaseModel):
    """Server-Driven Notification for the Report Header."""

    title: str
    message: str
    level: str = "info"  # info, warning, danger

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")

    @field_validator("title", "message", "level")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class ReportView(BaseModel):
    """Top-level View Model for the Execution Report.
    This replaces the raw 'Execution' object for frontend consumption.
    """

    view_id: str = Field(..., description="The Execution ID")
    title: str = Field(default="Auditintiraportti", description="Page title")
    status_theme: str = Field(default="success", description="Visual theme: 'success' | 'warning' | 'danger'")
    sections: list[UiSection] = Field(default_factory=list, description="Ordered list of UI sections")
    metrics: dict[str, Any] | None = Field(default=None, description="Global audit metrics (Word Count, etc.)")
    system_notification: SystemNotification | None = Field(default=None, description="Global notification/warning")
    references: list[ReferenceItem] = Field(default_factory=list, description="Global bibliography and references")

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")

    @field_validator("view_id", "title", "status_theme")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class StepProgressItem(BaseModel):
    """Progress indicator for a single step (BFF)."""

    id: str = Field(..., description="Step ID (e.g. step_guard)")
    label: str = Field(..., description="Human-readable label")
    status: str = Field(..., description="Status: pending, running, completed, failed")

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")

    @field_validator("id", "label", "status")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class AssessmentView(BaseModel):
    """BFF View Model for the Execution Monitor.

    Strictly typed for Server-Driven UI rendering.
    """

    sessionId: str = Field(..., description="Execution ID")
    statusLabel: str = Field(..., description="Human-readable status")
    uiVariant: Literal["default", "success", "warning", "error", "neutral"] = Field(
        ..., description="UI Theme: default, success, warning, error, neutral"
    )
    statusMessage: str = Field(..., description="Contextual status message")
    showWarningBanner: bool = Field(default=False, description="Whether to show warning banner")
    steps: list[StepProgressItem] = Field(default_factory=list, description="Ordered list of steps with status")
    finalScore: int | None = Field(default=None, description="Final score if available")

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")

    @field_validator("sessionId", "statusLabel", "statusMessage")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class ToulminDisplay(BaseModel):
    """Strict View Model for Toulmin Arguments."""

    claim: str
    data: str
    warrant: str
    backing: str | None = None
    rebuttal: str | None = None
    qualifier: str | None = None

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")

    @field_validator("claim", "data", "warrant")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class LogicAnalysisDisplay(BaseModel):
    """Server-Driven UI Data for Logic Analysis Section.
    Hoists presentation logic (quadrants, percentages, colors) from client to backend.
    """

    bloom_score: float | None
    bloom_percent: float | None
    bloom_label_key: str | None
    bloom_help: str | None  # Localized help text

    # Strategic
    strategic_score: float | None
    strategic_score_display: str | None
    strategic_percent: float | None
    strategic_percent_display: str | None
    strategic_label_key: str | None
    strategic_help: str | None

    # Toulmin
    toulmin_score: float | None
    toulmin_percent: float | None
    toulmin_help: str | None

    quadrant_key: str | None
    quadrant_label_key: str | None  # e.g. "QUADRANT_VISIONARY"
    position_label: str | None  # Pre-formatted "Bloom X / Toulmin Y"

    # Raw Data (for detail views if needed)
    bloom_level_raw: str | None
    strategic_depth_raw: str | None
    arguments: list[ToulminDisplay]

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")


class HeuristicDisplay(BaseModel):
    """Strict View Model for a single Heuristic."""

    name: str
    flag: bool
    color: str  # 'red' | 'green'

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")

    @field_validator("name", "color")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class PerformativityDisplay(BaseModel):
    """Server-Driven UI Data for Performativity Check."""

    authenticity_score: float | None
    authenticity_percent: float | None
    authenticity_assessment: str | None
    authenticity_help: str | None

    heuristics: list[HeuristicDisplay]

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")


class CausalDisplay(BaseModel):
    """Server-Driven UI Data for Causal Analysis."""

    # Abductive
    abductive_score: float | None
    abductive_score_display: str | None = None
    abductive_percent: float | None
    abductive_percent_display: str | None = None
    abductive_conclusion: str | None
    abductive_help: str | None

    # Counterfactual / Plausibility
    plausibility_score: float | None
    plausibility_score_display: str | None = None
    plausibility_percent: float | None
    plausibility_percent_display: str | None = None
    plausibility_label: str | None  # localized enum

    counterfactual_actual: str | None
    counterfactual_simulated: str | None

    observation: str | None
    hypothesis: str | None

    # Generic (if needed by base)
    score: float | None = None
    verdict: str | None = None

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")


class VerifiedFactDisplay(BaseModel):
    """Strict View Model for a Verified Fact."""

    claim: str | None
    source: str | None
    color: str  # 'green' | 'red' | 'orange'
    label_key: str
    label: str | None
    verification_result: str | None
    is_verified: bool | None

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")


class EthicalIssueDisplay(BaseModel):
    """Strict View Model for an Ethical Issue."""

    issue_type: str | None
    description: str | None
    color: str  # 'red' | 'orange'
    label_key: str
    label: str | None
    is_critical: bool
    severity: str | None

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")


class FactCheckDisplay(BaseModel):
    """Server-Driven UI Data for Fact & Ethics Check."""

    fact_checks: list[VerifiedFactDisplay]
    ethical_issues: list[EthicalIssueDisplay]

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")


class SecurityDisplay(BaseModel):
    """Server-Driven UI Data for Security Check."""

    threat_detected: bool
    threat_color: str  # 'red' | 'green'
    threat_label: str  # 'UHKA: KYLLÄ' | 'UHKA: EI'

    risk_level: str
    risk_color: str  # 'red' | 'orange' | 'green'
    risk_label: str | None = None

    anonymized: bool
    anonymized_color: str  # 'blue' | 'orange'
    anonymized_label: str

    findings: list[str]

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")

    @field_validator("threat_color", "threat_label", "risk_level", "risk_color", "anonymized_color", "anonymized_label")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class StressFindingDisplay(BaseModel):
    """Single finding for Stress Test."""

    question: str
    result_label: str  # "HELD" / "BROKEN" (Localized key or value)
    is_held: bool
    color_class: str  # "finding-held" / "finding-broken"
    text_class: str  # "text-held" / "text-broken"
    observation: str

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")

    @field_validator("question", "result_label", "color_class", "text_class", "observation")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class FidelityAudit(BaseModel):
    """Strict View Model for Fidelity Audit."""

    fidelity_score_display: str
    fidelity_percent: float | None
    fidelity_label: str
    post_hoc_rationalization_suspected: bool
    reasoning: str

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")


class StressTestDisplay(BaseModel):
    """Server-Driven UI Data for Stress Test / Falsifier."""

    fidelity_audit: FidelityAudit | None
    fidelity_help: str | None

    # Abductive Logic Gauge
    abductive_score: float | None
    abductive_percent: float | None
    abductive_conclusion: str | None
    abductive_help: str | None

    # Counterfactual
    counterfactual_actual: str | None
    counterfactual_simulated: str | None
    plausibility_score: float | None
    plausibility_percent: float | None
    plausibility_display: str | None = None
    plausibility_help: str | None

    # Findings (Hoisted Logic)
    findings: list[StressFindingDisplay]

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")


class ProfilerDisplay(BaseModel):
    """Server-Driven UI for Profiler Analysis."""

    # Control Ratio
    control_ratio_percent: float | None
    control_label_key: str | None
    control_help: str | None

    # Metrics
    word_count: int
    word_count_display: str | None = None
    word_count_help: str | None

    avg_sentence_length: float
    avg_sentence_length_display: str | None = None

    lexical_diversity: float
    lexical_diversity_display: str | None = None

    capitalization_ratio_percent: float | int
    capitalization_ratio_display: str | None = None

    # Bias / Gap (Hoisted Thresholds)
    automation_bias_label: str
    automation_bias_color: str  # "red" | "black"

    say_do_gap_label: str
    say_do_gap_color: str  # "red" | "black"

    psychological_profile: str | None
    intent_analysis: str | None

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")


class ArchivistDisplay(BaseModel):
    """Server-Driven UI for Archivist Check."""

    compliance_score: float | None
    compliance_score_display: str | None = None
    compliance_analysis: str | None
    compliance_help: str | None
    recommendations: list[str]

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")


class DimensionDisplay(BaseModel):
    """Strict View Model for a single Scoring Dimension."""

    dimension_id: str
    dimension_label: str  # Localization key
    score: float
    max_score: float
    weight: float
    reasoning: str

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")


class ScoreCardDisplay(BaseModel):
    """Server-Driven UI Data for Judge Score Card."""

    agent_name: str
    total_score: float
    min_score: int
    max_score: int
    verdict: str
    dimensions: list[DimensionDisplay] = Field(default_factory=list)

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")


class DriverProfileDisplay(BaseModel):
    """Server-Driven UI for Driver Profile."""

    role_classification: str
    high_dependency: bool
    imperative_command_count: int
    strategy: str
    input_control_ratio: float | None = None

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
