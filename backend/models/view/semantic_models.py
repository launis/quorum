from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SemanticIntent(str, Enum):
    """General intents for cognitive/display blocks."""
    WARNING = "WARNING"
    SUCCESS = "SUCCESS"
    NEUTRAL = "NEUTRAL"
    DANGER = "DANGER"
    INFO = "INFO"


class BlockType(str, Enum):
    """Agnostic Semantic Block Types."""
    PARAGRAPH = "PARAGRAPH"
    METRIC = "METRIC"
    LIST = "LIST"
    DATA_GRID = "DATA_GRID"
    CITATION = "CITATION"
    QUOTATION = "QUOTATION"
    CARD = "CARD"


class SemanticModel(BaseModel):
    """Base Configuration for all Semantic Models."""
    model_config = ConfigDict(frozen=True, strict=False)

    @classmethod
    def require_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class SemanticBlock(SemanticModel):
    """Abstract Semantic Block.
    Frontend and Jinja use 'type' and 'intent' to map to specific visual representations.
    """
    id: str = Field(..., description="Unique identifier for the block")
    type: BlockType = Field(..., description="Agnostic structural type (e.g. PARAGRAPH, METRIC)")
    intent: SemanticIntent = Field(default=SemanticIntent.NEUTRAL, description="Semantic meaning without visual styling")
    label: str | None = Field(default=None, description="Translation key or static label")
    value: Any = Field(default=None, description="Content payload (can be nested lists/dicts)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional non-visual context")

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        return cls.require_non_empty(v)


class ReferenceIntent(str, Enum):
    SEARCH = "SEARCH"
    GROUNDING = "GROUNDING"
    INTERNAL_KB = "INTERNAL_KB"


class ReferenceItem(SemanticModel):
    """Strict Model for a single Contextual Citation."""
    id: str = Field(..., description="Citation ID, e.g., H-1, F-1")
    intent: ReferenceIntent = Field(..., description="Type of the reference source")
    title: str | None = Field(default=None, description="Title of the source")
    snippet: str = Field(..., description="Extracted content, relevance, or reasoning")
    url: str | None = Field(default=None, description="Link to the source if available")

    @field_validator("id", "snippet")
    @classmethod
    def validate_fields(cls, v: str) -> str:
        return cls.require_non_empty(v)


class SystemNotification(SemanticModel):
    """Server-Driven Notification for the Report Header."""
    title: str
    message: str
    level: str = "info"  # info, warning, danger

    @field_validator("title", "message", "level")
    @classmethod
    def validate_fields(cls, v: str) -> str:
        return cls.require_non_empty(v)


class SemanticReport(SemanticModel):
    """Top-level Agile Semantic Model for the Execution Report.
    Replaces previously hard-coded ReportView/UiSection.
    """
    report_id: str = Field(..., description="The Execution ID")
    title: str = Field(default="TITLE_REPORT", description="Localization key for title")
    intent: SemanticIntent = Field(default=SemanticIntent.NEUTRAL, description="Overall severity/intent")
    blocks: list[SemanticBlock] = Field(default_factory=list, description="Ordered list of semantic blocks")
    metrics: dict[str, Any] | None = Field(default=None, description="Global numerical metrics")
    system_notification: SystemNotification | None = Field(default=None, description="Global notification/warning")
    references: list[ReferenceItem] = Field(default_factory=list, description="Global bibliography/references")

    @field_validator("report_id", "title")
    @classmethod
    def validate_strings(cls, v: str) -> str:
        return cls.require_non_empty(v)

class StepProgressItem(BaseModel):
    """Progress indicator for a single step (BFF)."""

    id: str = Field(..., description="Step ID (e.g. step_guard)")
    label: str = Field(..., description="Human-readable label")
    status: str = Field(..., description="Status: pending, running, completed, failed")

    model_config = ConfigDict(frozen=True, strict=False)

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

    model_config = ConfigDict(frozen=True, strict=False)

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

    model_config = ConfigDict(frozen=True, strict=False)

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
    bloom_percent_display: str | None = None
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
    toulmin_percent_display: str | None = None
    toulmin_help: str | None

    quadrant_key: str | None
    quadrant_label_key: str | None  # e.g. "QUADRANT_VISIONARY"
    position_label: str | None  # Pre-formatted "Bloom X / Toulmin Y"
    
    # Pre-computed Visual HINTS (BFF No-String / Logic-less Presentation)
    bubble_size: float | None = None
    bubble_style: str | None = None

    # Raw Data (for detail views if needed)
    bloom_level_raw: str | None
    strategic_depth_raw: str | None
    arguments: list[ToulminDisplay]

    model_config = ConfigDict(frozen=True, strict=False)


class HeuristicDisplay(BaseModel):
    """Strict View Model for a single Heuristic."""

    name: str
    flag: bool
    color: str  # 'red' | 'green'

    model_config = ConfigDict(frozen=True, strict=False)

    @field_validator("name", "color")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class PerformativityDisplay(BaseModel):
    """Server-Driven UI Data for Performativity Check."""

    authenticity_score: float | None
    authenticity_score_display: str | None = None
    authenticity_percent: float | None
    authenticity_percent_display: str | None = None
    authenticity_assessment: str | None
    authenticity_help: str | None

    heuristics: list[HeuristicDisplay]

    model_config = ConfigDict(frozen=True, strict=False)


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

    model_config = ConfigDict(frozen=True, strict=False)


class VerifiedFactDisplay(BaseModel):
    """Strict View Model for a Verified Fact."""

    claim: str | None
    source: str | None
    color: str  # 'green' | 'red' | 'orange'
    label_key: str
    label: str | None
    verification_result: str | None
    is_verified: bool | None

    model_config = ConfigDict(frozen=True, strict=False)


class EthicalIssueDisplay(BaseModel):
    """Strict View Model for an Ethical Issue."""

    issue_type: str | None
    description: str | None
    color: str  # 'red' | 'orange'
    label_key: str
    label: str | None
    is_critical: bool
    severity: str | None

    model_config = ConfigDict(frozen=True, strict=False)


class FactCheckDisplay(BaseModel):
    """Server-Driven UI Data for Fact & Ethics Check."""

    fact_checks: list[VerifiedFactDisplay]
    ethical_issues: list[EthicalIssueDisplay]

    model_config = ConfigDict(frozen=True, strict=False)


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

    model_config = ConfigDict(frozen=True, strict=False)

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

    model_config = ConfigDict(frozen=True, strict=False)

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
    fidelity_percent_display: str | None = None
    fidelity_label: str
    post_hoc_rationalization_suspected: bool
    reasoning: str

    model_config = ConfigDict(frozen=True, strict=False)


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

    model_config = ConfigDict(frozen=True, strict=False)


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

    model_config = ConfigDict(frozen=True, strict=False)


class ArchivistDisplay(BaseModel):
    """Server-Driven UI for Archivist Check."""

    compliance_score: float | None
    compliance_score_display: str | None = None
    compliance_analysis: str | None
    compliance_help: str | None
    recommendations: list[str]

    model_config = ConfigDict(frozen=True, strict=False)


class DimensionDisplay(BaseModel):
    """Strict View Model for a single Scoring Dimension."""

    dimension_id: str
    dimension_label: str  # Localization key
    score: float
    score_display: str | None = None
    max_score: float
    weight: float
    reasoning: str

    model_config = ConfigDict(frozen=True, strict=False)


class ScoreCardDisplay(BaseModel):
    """Server-Driven UI Data for Judge Score Card."""

    agent_name: str
    total_score: float
    total_score_display: str | None = None
    min_score: int
    max_score: int
    verdict: str
    dimensions: list[DimensionDisplay] = Field(default_factory=list)

    model_config = ConfigDict(frozen=True, strict=False)


class DriverProfileDisplay(BaseModel):
    """Server-Driven UI for Driver Profile."""

    role_classification: str
    high_dependency: bool
    imperative_command_count: int
    strategy: str
    input_control_ratio: float | None = None
    input_control_ratio_display: str | None = None
    control_ratio_percent: float | None = None
    control_ratio_display: str | None = None
    control_label: str | None = None

    model_config = ConfigDict(frozen=True, strict=True)


class EvidenceItem(BaseModel):
    """Strict View Model for a single piece of Evidence."""

    id: str
    source: str
    content: str
    score: float | None
    type: str  # "precedent" | "regulation" | "concept"

    model_config = ConfigDict(frozen=True, strict=False)

    @field_validator("id", "source", "content", "type")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class EvidenceList(BaseModel):
    """Server-Driven UI Data for Evidence List."""

    items: list[EvidenceItem]
    total_count: int

    model_config = ConfigDict(frozen=True, strict=False)
