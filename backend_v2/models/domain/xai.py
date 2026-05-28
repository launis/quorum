"""XAI Agent Domain Models.

from __future__ import annotations

This module contains the schemas for the XAI Reporter Agent,
including the final report output and context for report generation.
"""

import logging
from typing import Annotated, Any, Literal

from pydantic import Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.enums import XaiExtensionType

logger = logging.getLogger(__name__)

from backend_v2.models.domain.analyst import AnalystOutput
from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend_v2.models.domain.causal import CausalOutput
from backend_v2.models.domain.falsifier import FalsifierOutput
from backend_v2.models.domain.judge import JudgeOutput, JudgeScoreCard
from backend_v2.models.domain.linguistics import LinguisticsResultDTO
from backend_v2.models.domain.logician import LogicianOutput
from backend_v2.models.domain.metrics import ProfilerMetricsDTO
from backend_v2.models.domain.performativity import PerformativityOutput
from backend_v2.models.domain.profiler import ProfilerOutput


class XAIReporterInput(V2CoreBase):
    """Strict input schema for XAIReporterAgent.

    V2 Dynamic: 'chatlog' is mandatory, but other inputs are allowed dynamically.
    """

    chat_log: str = Field(
        ..., description="The mandatory conversation history.", json_schema_extra={"x-ui-label": "Chatlog"}
    )
    last_reasoning_trace: str | None = Field(default=None, description="Previous reasoning trace.")
    step_judge: JudgeOutput | None = Field(default=None, description="Standard evaluate output.")
    step_judge_cognitive: JudgeOutput | None = Field(default=None, description="Cognitive Judge output.")

    # --- Universal Routing Inputs ---
    step_analyst: AnalystOutput | None = Field(default=None, description="Analyst hypotheses and RAG data.")
    step_profiler: ProfilerOutput | None = Field(default=None, description="Profiler cognitive bias data.")
    step_falsifier: FalsifierOutput | None = Field(default=None, description="Falsifier critical distance data.")
    step_logician: LogicianOutput | None = Field(default=None, description="Logician Toulmin analysis data.")
    step_causal_analyst: CausalOutput | None = Field(
        default=None, description="Causal Analyst post-hoc and counterfactual data."
    )
    step_performativity: PerformativityOutput | None = Field(
        default=None, description="Cognitive performativity output."
    )
    step_metrics: ProfilerMetricsDTO | None = Field(default=None, description="Mechanical text and behavioral metrics.")
    step_linguistics: LinguisticsResultDTO | None = Field(default=None, description="Mechanical linguistic patterns.")
    dynamic_inputs: dict[str, Any] = Field(default_factory=dict, description="Dynamically passed variables.")


class XAIScoreItem(V2CoreBase):
    """A single score item for the scorecard."""

    label: str = Field(..., min_length=1, description="Label for the score item.")
    score: float = Field(..., description="Score value.")
    reasoning: str | None = Field(default=None, description="Reasoning for the score.")
    weight: float = Field(default=1.0, description="Weight of this item.")


class CitationExtension(V2CoreBase):
    extension_type: Literal[XaiExtensionType.CITATION] = XaiExtensionType.CITATION
    source_id: str
    snippet: str
    url: str | None = None


class JustificationExtension(V2CoreBase):
    extension_type: Literal[XaiExtensionType.JUSTIFICATION] = XaiExtensionType.JUSTIFICATION
    reasoning: str


class FalsificationExtension(V2CoreBase):
    extension_type: Literal[XaiExtensionType.FALSIFICATION] = XaiExtensionType.FALSIFICATION
    counter_argument: str
    vulnerabilities: list[str]


class TheoryLinkExtension(V2CoreBase):
    extension_type: Literal[XaiExtensionType.THEORY_LINK] = XaiExtensionType.THEORY_LINK
    theory_name: str
    relevance: str


class RiskFlagExtension(V2CoreBase):
    extension_type: Literal[XaiExtensionType.RISK_FLAG] = XaiExtensionType.RISK_FLAG
    risk_level: str
    description: str


class CoachingExtension(V2CoreBase):
    extension_type: Literal[XaiExtensionType.COACHING] = XaiExtensionType.COACHING
    actionable_steps: list[str]


class MissingContextExtension(V2CoreBase):
    extension_type: Literal[XaiExtensionType.MISSING_CONTEXT] = XaiExtensionType.MISSING_CONTEXT
    context_needed: str


class RemediationStepsExtension(V2CoreBase):
    extension_type: Literal[XaiExtensionType.REMEDIATION_STEPS] = XaiExtensionType.REMEDIATION_STEPS
    steps: list[str]


class EmotionalSentimentExtension(V2CoreBase):
    extension_type: Literal[XaiExtensionType.EMOTIONAL_SENTIMENT] = XaiExtensionType.EMOTIONAL_SENTIMENT
    sentiment: str
    intensity: float


class ConfidenceExtension(V2CoreBase):
    extension_type: Literal[XaiExtensionType.CONFIDENCE] = XaiExtensionType.CONFIDENCE
    confidence_score: float
    rationale: str


class SourceIDExtension(V2CoreBase):
    extension_type: Literal[XaiExtensionType.SOURCE_ID] = XaiExtensionType.SOURCE_ID
    source_id: str


class VarianceValidationExtension(V2CoreBase):
    extension_type: Literal[XaiExtensionType.VARIANCE_VALIDATION] = XaiExtensionType.VARIANCE_VALIDATION
    mechanical_metric_ref: str = Field(..., description="Reference to the mechanical metric key used.")
    cognitive_metric_ref: str = Field(..., description="Reference to the cognitive agent score key used.")
    variance_score: float = Field(
        ...,
        description="Calculated absolute variance between mechanical and cognitive assessments.",
    )
    alignment_verdict: str = Field(
        ...,
        description="Abstract verdict (e.g., 'ALIGNED', 'MISALIGNED_SYCOPHANCY').",
    )


class ComparisonDataDTO(V2CoreBase):
    baseline_score: float | None = None
    delta: float | None = None
    trend: str | None = None


XAIExtension = Annotated[
    CitationExtension
    | JustificationExtension
    | FalsificationExtension
    | TheoryLinkExtension
    | RiskFlagExtension
    | CoachingExtension
    | MissingContextExtension
    | RemediationStepsExtension
    | EmotionalSentimentExtension
    | ConfidenceExtension
    | SourceIDExtension
    | VarianceValidationExtension,
    Field(discriminator="extension_type"),
]


class XAIOutputDTO(ReasoningTraceDTO):
    """Data Transfer Object for XAI Reporter Agent (Content Only)."""

    output_extensions: list[XAIExtension] = Field(
        default_factory=list,
        description="Polymorphic list of XAI extensions.",
    )
    comparison_data: ComparisonDataDTO | None = Field(
        default=None,
        description="Structured comparison data.",
        json_schema_extra={"x-ui-label": "Comparison Data"},
    )

    executive_summary: str = Field(
        ...,
        min_length=1,
        description="High-level summary.",
        json_schema_extra={"x-ui-label": "Executive Summary"},
    )
    verified_facts: str = Field(
        ...,
        min_length=1,
        description="Synthesis of facts.",
        json_schema_extra={"x-ui-label": "Verified Facts"},
    )
    cognitive_behavior: str = Field(
        ...,
        min_length=1,
        description="Synthesis of Profiler and Falsifier findings.",
        json_schema_extra={"x-ui-label": "Cognitive Behavior"},
    )
    causal_chain: str = Field(
        ...,
        min_length=1,
        description="Synthesis of Causal and Logician findings.",
        json_schema_extra={"x-ui-label": "Causal Chain"},
    )
    analysis_strengths: str = Field(
        ...,
        min_length=1,
        description="Strengths identified.",
        json_schema_extra={"x-ui-label": "Strengths"},
    )
    analysis_weaknesses: str = Field(
        ...,
        min_length=1,
        description="Weaknesses identified.",
        json_schema_extra={"x-ui-label": "Weaknesses"},
    )
    analysis_opportunities: str = Field(
        ...,
        min_length=1,
        description="Opportunities identified.",
        json_schema_extra={"x-ui-label": "Opportunities"},
    )
    analysis_recommendations: str = Field(
        ...,
        min_length=1,
        description="Recommendations.",
        json_schema_extra={"x-ui-label": "Recommendations"},
    )
    final_verdict: str = Field(
        ...,
        min_length=1,
        description="Final conclusion.",
        json_schema_extra={"x-ui-label": "Verdict"},
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0-1.0).",
        json_schema_extra={"x-ui-label": "Confidence"},
    )
    xai_report_formatted: str | None = Field(
        default=None,
        description="Markdown formatted report.",
        json_schema_extra={"x-ui-label": "Formatted Report"},
    )


class XAIOutput(XAIOutputDTO, ReasoningTrace):
    """Output schema for the XAI Reporter Agent."""

    score_cards: list[JudgeScoreCard] = Field(
        default_factory=list,
        description="Aggregated scores from all judges.",
        json_schema_extra={"x-ui-label": "Scorecards"},
    )
    flat_report: dict[str, Any] | None = Field(
        default=None,
        description="Flattened, machine-readable report summary.",
        json_schema_extra={"x-ui-label": "Flat Report"},
    )


class ReportResult(V2CoreBase):
    """Result of the report generation (Hook)."""

    report_content: str = Field(
        ...,
        min_length=1,
        description="The generated Markdown report.",
        json_schema_extra={"x-ui-label": "Report Content"},
    )
    format: str = Field(
        default="markdown",
        min_length=1,
        description="Report format.",
        json_schema_extra={"x-ui-label": "Format"},
    )
    data: dict[str, Any] | None = Field(
        default=None, description="The structured data used to generate the report (SSOT)."
    )
