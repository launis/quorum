"""XAI Agent Domain Models.

This module contains the schemas for the XAI Reporter Agent,
including the final report output and context for report generation.
"""

from __future__ import annotations

import logging
from typing import Annotated, Any, Literal

from pydantic import Field, field_validator

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import V2CoreBase
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
from backend_v2.models.enums import XaiExtensionType

logger = logging.getLogger(__name__)


class XAIReporterInput(V2CoreBase):
    """Strict input schema for XAIReporterAgent.

    V2 Dynamic: 'chat_log' is mandatory, but other inputs are allowed dynamically.

    Attributes:
        chat_log: Conversation history to be analyzed.
        last_reasoning_trace: Previous reasoning trace.
        step_judge: Standard evaluate output.
        step_judge_cognitive: Cognitive Judge output.
        step_analyst: Analyst hypotheses and RAG data.
        step_profiler: Profiler cognitive bias data.
        step_falsifier: Falsifier critical distance data.
        step_logician: Logician Toulmin analysis data.
        step_causal_analyst: Causal Analyst post-hoc and counterfactual data.
        step_performativity: Cognitive performativity output.
        step_metrics: Mechanical text and behavioral metrics.
        step_linguistics: Mechanical linguistic patterns.
        dynamic_inputs: Dynamically passed variables.
    """

    chat_log: str = Field(..., description="Conversation history.", json_schema_extra={"x-ui-label": "Chatlog"})
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
    """A single score item for the scorecard.

    Attributes:
        label: Label identifier for the score item.
        score: Computed numeric score value.
        reasoning: Textual reasoning explaining the score.
        weight: Importance multiplier weight of this item.
    """

    label: str = Field(..., min_length=1, description="Label for the score item.")
    score: float = Field(..., description="Score value.")
    reasoning: str | None = Field(default=None, description="Reasoning for the score.")
    weight: float = Field(default=1.0, description="Weight of this item.")


class CitationExtension(V2CoreBase):
    """Citation extension block metadata."""

    extension_type: Literal[XaiExtensionType.CITATION] = XaiExtensionType.CITATION
    source_id: str = Field(..., description="Unique reference document source ID.")
    snippet: str = Field(..., description="The captured exact contextual snippet text.")
    url: str | None = Field(default=None, description="Optional direct reference web link.")


class JustificationExtension(V2CoreBase):
    """Reasoning justification extension metadata."""

    extension_type: Literal[XaiExtensionType.JUSTIFICATION] = XaiExtensionType.JUSTIFICATION
    reasoning: str = Field(..., description="The explanatory text justification.")


class FalsificationExtension(V2CoreBase):
    """Falsification extension metadata."""

    extension_type: Literal[XaiExtensionType.FALSIFICATION] = XaiExtensionType.FALSIFICATION
    counter_argument: str = Field(..., description="The key falsification counter argument.")
    vulnerabilities: list[str] = Field(default_factory=list, description="Specific logical vulnerabilities detected.")


class TheoryLinkExtension(V2CoreBase):
    """Theory link extension metadata."""

    extension_type: Literal[XaiExtensionType.THEORY_LINK] = XaiExtensionType.THEORY_LINK
    theory_name: str = Field(..., description="Name of referenced academic/logical framework.")
    relevance: str = Field(..., description="Direct relevance alignment explanation.")


class RiskFlagExtension(V2CoreBase):
    """Risk flag extension metadata."""

    extension_type: Literal[XaiExtensionType.RISK_FLAG] = XaiExtensionType.RISK_FLAG
    risk_level: str = Field(..., description="Assessed hazard status.")
    description: str = Field(..., description="Explaining context behind hazard determination.")


class CoachingExtension(V2CoreBase):
    """Coaching guidance extensions metadata."""

    extension_type: Literal[XaiExtensionType.COACHING] = XaiExtensionType.COACHING
    actionable_steps: list[str] = Field(default_factory=list, description="Structured actions for improvement.")


class MissingContextExtension(V2CoreBase):
    """Missing context indicator metadata."""

    extension_type: Literal[XaiExtensionType.MISSING_CONTEXT] = XaiExtensionType.MISSING_CONTEXT
    context_needed: str = Field(..., description="Explicit context points missing from execution pipeline.")


class RemediationStepsExtension(V2CoreBase):
    """Remediation steps suggestions metadata."""

    extension_type: Literal[XaiExtensionType.REMEDIATION_STEPS] = XaiExtensionType.REMEDIATION_STEPS
    steps: list[str] = Field(default_factory=list, description="Sequence of operations to apply to mitigate errors.")


class EmotionalSentimentExtension(V2CoreBase):
    """Linguistic emotion assessment extension metadata."""

    extension_type: Literal[XaiExtensionType.EMOTIONAL_SENTIMENT] = XaiExtensionType.EMOTIONAL_SENTIMENT
    sentiment: str = Field(..., description="Detected subjective linguistic tone.")
    intensity: float = Field(..., description="Numeric magnitude of evaluated emotional tone.")


class ConfidenceExtension(V2CoreBase):
    """Mathematical confidence assessment extension metadata."""

    extension_type: Literal[XaiExtensionType.CONFIDENCE] = XaiExtensionType.CONFIDENCE
    confidence_score: float = Field(..., description="Numeric value between 0.0 and 1.0 indicating security factor.")
    rationale: str = Field(..., description="Systematic evaluation context behind computed confidence level.")


class SourceIDExtension(V2CoreBase):
    """Simple source indexing extension metadata."""

    extension_type: Literal[XaiExtensionType.SOURCE_ID] = XaiExtensionType.SOURCE_ID
    source_id: str = Field(..., description="The exact reference target key index identifier.")


class VarianceValidationExtension(V2CoreBase):
    """Variance validation extension metadata."""

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
    """Baseline comparison and progress analysis data.

    Attributes:
        baseline_score: Optional baseline rating reference context.
        delta: Difference factor between current run and baseline.
        trend: Evaluated qualitative vector indicator.
    """

    baseline_score: float | None = Field(default=None, description="Baseline rating reference context.")
    delta: float | None = Field(default=None, description="Difference factor between current run and baseline.")
    trend: str | None = Field(default=None, description="Evaluated qualitative vector indicator.")


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
    """Data Transfer Object for XAI Reporter Agent (Content Only).

    Attributes:
        output_extensions: XAI extensions.
        comparison_data: Structured progress and comparison data.
        executive_summary: High-level summary.
        verified_facts: Synthesis of verified facts.
        cognitive_behavior: Synthesis of Profiler and Falsifier findings.
        causal_chain: Synthesis of Causal and Logician findings.
        analysis_strengths: Identified strengths.
        analysis_weaknesses: Identified weaknesses.
        analysis_opportunities: Identified opportunities.
        analysis_recommendations: Recommendations.
        final_verdict: Final conclusion.
        confidence_score: Confidence factor (0.0-1.0).
        xai_report_formatted: Markdown formatted report.
    """

    output_extensions: list[XAIExtension] = Field(
        default_factory=list,
        description="XAI extensions.",
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
        description="Confidence score (0.0-1.0).",
        json_schema_extra={"x-ui-label": "Confidence"},
    )
    xai_report_formatted: str | None = Field(
        default=None,
        description="Markdown formatted report.",
        json_schema_extra={"x-ui-label": "Formatted Report"},
    )

    @field_validator("confidence_score")
    @classmethod
    def validate_confidence_score_bounds(cls, v: float) -> float:
        """Enforce float bounds on confidence_score to prevent Vertex AI 400 errors.

        Args:
            v: The computed raw confidence score value.

        Returns:
            The validated confidence score value.

        Raises:
            AppException: If the computed value is outside of the physical closed boundary [0.0, 1.0].
        """
        if not (0.0 <= v <= 1.0):
            msg = "confidence_score must be between 0.0 and 1.0"
            logger.error("[XAIOutputDTO] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v


class XAIOutput(XAIOutputDTO, ReasoningTrace):
    """Output schema for the XAI Reporter Agent.

    WARNING (Rule 84): flat_report acts as a polymorphic boundary with extra='allow' configured
    implicitly at parent classes. Keep structure dynamic for raw client processing.

    Attributes:
        score_cards: Aggregated scorecard items from all judges.
        flat_report: Flattened machine-readable dict report summary.
    """

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
    """Result of the report generation (Hook).

    Attributes:
        report_content: Generated Markdown report.
        format: Report format.
        data: Structured data used to generate the report.
    """

    report_content: str = Field(
        ...,
        min_length=1,
        description="Generated Markdown report.",
        json_schema_extra={"x-ui-label": "Report Content"},
    )
    format: str = Field(
        default="markdown",
        min_length=1,
        description="Report format.",
        json_schema_extra={"x-ui-label": "Format"},
    )
    data: dict[str, Any] | None = Field(default=None, description="Structured data used to generate the report (SSOT).")
