"""XAI Agent Domain Models.

This module contains the schemas for the XAI Reporter Agent,
including the final report output and context for report generation.
"""

from __future__ import annotations

import logging
from typing import Annotated, Any, Literal

from pydantic import ConfigDict, Field, field_validator

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
    model_config = ConfigDict(strict=True, extra="forbid")

    chat_log: Annotated[str, Field(description="Conversation history.", json_schema_extra={"x-ui-label": "Chatlog"})]
    last_reasoning_trace: Annotated[str | None, Field(description="Previous reasoning trace.")] = None
    step_judge: Annotated[JudgeOutput | None, Field(description="Standard evaluate output.")] = None
    step_judge_cognitive: Annotated[JudgeOutput | None, Field(description="Cognitive Judge output.")] = None

    # --- Universal Routing Inputs ---
    step_analyst: Annotated[AnalystOutput | None, Field(description="Analyst hypotheses and RAG data.")] = None
    step_profiler: Annotated[ProfilerOutput | None, Field(description="Profiler cognitive bias data.")] = None
    step_falsifier: Annotated[FalsifierOutput | None, Field(description="Falsifier critical distance data.")] = None
    step_logician: Annotated[LogicianOutput | None, Field(description="Logician Toulmin analysis data.")] = None
    step_causal_analyst: Annotated[
        CausalOutput | None, Field(description="Causal Analyst post-hoc and counterfactual data.")
    ] = None
    step_performativity: Annotated[
        PerformativityOutput | None, Field(description="Cognitive performativity output.")
    ] = None
    step_metrics: Annotated[ProfilerMetricsDTO | None, Field(description="Mechanical text and behavioral metrics.")] = (
        None
    )
    step_linguistics: Annotated[LinguisticsResultDTO | None, Field(description="Mechanical linguistic patterns.")] = (
        None
    )
    dynamic_inputs: Annotated[dict[str, Any], Field(description="Dynamically passed variables.")] = Field(
        default_factory=dict
    )


class XAIScoreItem(V2CoreBase):
    """A single score item for the scorecard.

    Attributes:
        label: Label identifier for the score item.
        score: Computed numeric score value.
        reasoning: Textual reasoning explaining the score.
        weight: Importance multiplier weight of this item.
    """
    model_config = ConfigDict(strict=True, extra="forbid")

    label: Annotated[str, Field(min_length=1, description="Label for the score item.")]
    score: Annotated[float, Field(description="Score value.")]
    reasoning: Annotated[str | None, Field(description="Reasoning for the score.")] = None
    weight: Annotated[float, Field(description="Weight of this item.")] = 1.0


class CitationExtension(V2CoreBase):
    """Citation extension block metadata."""

    model_config = ConfigDict(title="citation", strict=True, extra="forbid")
    extension_type: Literal[XaiExtensionType.CITATION] = XaiExtensionType.CITATION
    source_id: Annotated[str, Field(description="Unique reference document source ID.")]
    snippet: Annotated[str, Field(description="The captured exact contextual snippet text.")]
    url: Annotated[str | None, Field(description="Optional direct reference web link.")] = None


class JustificationExtension(V2CoreBase):
    """Reasoning justification extension metadata."""

    model_config = ConfigDict(title="justification", strict=True, extra="forbid")
    extension_type: Literal[XaiExtensionType.JUSTIFICATION] = XaiExtensionType.JUSTIFICATION
    reasoning: Annotated[str, Field(description="The explanatory text justification.")]


class FalsificationExtension(V2CoreBase):
    """Falsification extension metadata."""

    model_config = ConfigDict(title="falsification", strict=True, extra="forbid")
    extension_type: Literal[XaiExtensionType.FALSIFICATION] = XaiExtensionType.FALSIFICATION
    counter_argument: Annotated[str, Field(description="The key falsification counter argument.")]
    vulnerabilities: Annotated[list[str], Field(description="Specific logical vulnerabilities detected.")] = Field(
        default_factory=list
    )


class TheoryLinkExtension(V2CoreBase):
    """Theory link extension metadata."""

    model_config = ConfigDict(title="theory_link", strict=True, extra="forbid")
    extension_type: Literal[XaiExtensionType.THEORY_LINK] = XaiExtensionType.THEORY_LINK
    theory_name: Annotated[str, Field(description="Name of referenced academic/logical framework.")]
    relevance: Annotated[str, Field(description="Direct relevance alignment explanation.")]


class RiskFlagExtension(V2CoreBase):
    """Risk flag extension metadata."""

    model_config = ConfigDict(title="risk_flag", strict=True, extra="forbid")
    extension_type: Literal[XaiExtensionType.RISK_FLAG] = XaiExtensionType.RISK_FLAG
    risk_level: Annotated[str, Field(description="Assessed hazard status.")]
    description: Annotated[str, Field(description="Explaining context behind hazard determination.")]


class CoachingExtension(V2CoreBase):
    """Coaching guidance extensions metadata."""

    model_config = ConfigDict(title="coaching", strict=True, extra="forbid")
    extension_type: Literal[XaiExtensionType.COACHING] = XaiExtensionType.COACHING
    actionable_steps: Annotated[list[str], Field(description="Structured actions for improvement.")] = Field(
        default_factory=list
    )


class MissingContextExtension(V2CoreBase):
    """Missing context indicator metadata."""

    model_config = ConfigDict(title="missing_context", strict=True, extra="forbid")
    extension_type: Literal[XaiExtensionType.MISSING_CONTEXT] = XaiExtensionType.MISSING_CONTEXT
    context_needed: Annotated[str, Field(description="Explicit context points missing from execution pipeline.")]


class RemediationStepsExtension(V2CoreBase):
    """Remediation steps suggestions metadata."""

    model_config = ConfigDict(title="remediation_steps", strict=True, extra="forbid")
    extension_type: Literal[XaiExtensionType.REMEDIATION_STEPS] = XaiExtensionType.REMEDIATION_STEPS
    steps: Annotated[list[str], Field(description="Sequence of operations to apply to mitigate errors.")] = Field(
        default_factory=list
    )


class EmotionalSentimentExtension(V2CoreBase):
    """Linguistic emotion assessment extension metadata."""

    model_config = ConfigDict(title="emotional_sentiment", strict=True, extra="forbid")
    extension_type: Literal[XaiExtensionType.EMOTIONAL_SENTIMENT] = XaiExtensionType.EMOTIONAL_SENTIMENT
    sentiment: Annotated[str, Field(description="Detected subjective linguistic tone.")]
    intensity: Annotated[float, Field(description="Numeric magnitude of evaluated emotional tone.")]


class ConfidenceExtension(V2CoreBase):
    """Mathematical confidence assessment extension metadata."""

    model_config = ConfigDict(title="confidence", strict=True, extra="forbid")
    extension_type: Literal[XaiExtensionType.CONFIDENCE] = XaiExtensionType.CONFIDENCE
    confidence_score: Annotated[
        float, Field(description="Numeric value between 0.0 and 1.0 indicating security factor.")
    ]
    rationale: Annotated[str, Field(description="Systematic evaluation context behind computed confidence level.")]


class SourceIDExtension(V2CoreBase):
    """Source referencing extension metadata."""

    model_config = ConfigDict(title="source_id", strict=True, extra="forbid")
    extension_type: Literal[XaiExtensionType.SOURCE_ID] = XaiExtensionType.SOURCE_ID
    source_id: Annotated[str, Field(description="The exact reference target key index identifier.")]


class VarianceValidationExtension(V2CoreBase):
    """Variance validation extension metadata."""

    model_config = ConfigDict(title="variance_validation", strict=True, extra="forbid")
    extension_type: Literal[XaiExtensionType.VARIANCE_VALIDATION] = XaiExtensionType.VARIANCE_VALIDATION
    mechanical_metric_ref: Annotated[str, Field(description="Reference to the mechanical metric key used.")]
    cognitive_metric_ref: Annotated[str, Field(description="Reference to the cognitive agent score key used.")]
    variance_score: Annotated[
        float, Field(description="Calculated absolute variance between mechanical and cognitive assessments.")
    ]
    alignment_verdict: Annotated[str, Field(description="Abstract verdict (e.g., 'ALIGNED', 'MISALIGNED_SYCOPHANCY').")]


class ComparisonDataDTO(V2CoreBase):
    """Baseline comparison and progress analysis data.

    Attributes:
        baseline_score: Optional baseline rating reference context.
        delta: Difference factor between current run and baseline.
        trend: Evaluated qualitative vector indicator.
    """
    model_config = ConfigDict(strict=True, extra="forbid")

    baseline_score: Annotated[float | None, Field(description="Baseline rating reference context.")] = None
    delta: Annotated[float | None, Field(description="Difference factor between current run and baseline.")] = None
    trend: Annotated[str | None, Field(description="Evaluated qualitative vector indicator.")] = None


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
    model_config = ConfigDict(strict=True, extra="forbid")

    output_extensions: Annotated[list[XAIExtension], Field(description="XAI extensions.")] = Field(default_factory=list)
    comparison_data: Annotated[
        ComparisonDataDTO | None,
        Field(description="Structured comparison data.", json_schema_extra={"x-ui-label": "Comparison Data"}),
    ] = None

    executive_summary: Annotated[
        str,
        Field(min_length=1, description="High-level summary.", json_schema_extra={"x-ui-label": "Executive Summary"}),
    ]
    verified_facts: Annotated[
        str, Field(min_length=1, description="Synthesis of facts.", json_schema_extra={"x-ui-label": "Verified Facts"})
    ]
    cognitive_behavior: Annotated[
        str,
        Field(
            min_length=1,
            description="Synthesis of Profiler and Falsifier findings.",
            json_schema_extra={"x-ui-label": "Cognitive Behavior"},
        ),
    ]
    causal_chain: Annotated[
        str,
        Field(
            min_length=1,
            description="Synthesis of Causal and Logician findings.",
            json_schema_extra={"x-ui-label": "Causal Chain"},
        ),
    ]
    analysis_strengths: Annotated[
        str, Field(min_length=1, description="Strengths identified.", json_schema_extra={"x-ui-label": "Strengths"})
    ]
    analysis_weaknesses: Annotated[
        str, Field(min_length=1, description="Weaknesses identified.", json_schema_extra={"x-ui-label": "Weaknesses"})
    ]
    analysis_opportunities: Annotated[
        str,
        Field(min_length=1, description="Opportunities identified.", json_schema_extra={"x-ui-label": "Opportunities"}),
    ]
    analysis_recommendations: Annotated[
        str, Field(min_length=1, description="Recommendations.", json_schema_extra={"x-ui-label": "Recommendations"})
    ]
    final_verdict: Annotated[
        str, Field(min_length=1, description="Final conclusion.", json_schema_extra={"x-ui-label": "Verdict"})
    ]
    confidence_score: Annotated[
        float, Field(description="Confidence score (0.0-1.0).", json_schema_extra={"x-ui-label": "Confidence"})
    ]
    xai_report_formatted: Annotated[
        str | None,
        Field(description="Markdown formatted report.", json_schema_extra={"x-ui-label": "Formatted Report"}),
    ] = None

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
    model_config = ConfigDict(strict=True, extra="forbid")

    score_cards: Annotated[
        list[JudgeScoreCard],
        Field(description="Aggregated scores from all judges.", json_schema_extra={"x-ui-label": "Scorecards"}),
    ] = Field(default_factory=list)
    flat_report: Annotated[
        dict[str, Any] | None,
        Field(
            description="Flattened, machine-readable report summary.", json_schema_extra={"x-ui-label": "Flat Report"}
        ),
    ] = None


class ReportResult(V2CoreBase):
    """Result of the report generation (Hook).

    Attributes:
        report_content: Generated Markdown report.
        format: Report format.
        data: Structured data used to generate the report.
    """
    model_config = ConfigDict(strict=True, extra="forbid")

    report_content: Annotated[
        str,
        Field(
            min_length=1, description="Generated Markdown report.", json_schema_extra={"x-ui-label": "Report Content"}
        ),
    ]
    format: Annotated[
        str, Field(min_length=1, description="Report format.", json_schema_extra={"x-ui-label": "Format"})
    ] = "markdown"
    data: Annotated[dict[str, Any] | None, Field(description="Structured data used to generate the report (SSOT).")] = (
        None
    )
