"""XAI Agent Domain Models.

This module contains the schemas for the XAI Reporter Agent,
including the final report output and context for report generation.
"""

import logging
from typing import Any, Literal, Union, Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from backend_v2.models.enums import XaiExtensionType

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)

from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend_v2.models.domain.judge import JudgeOutput, JudgeScoreCard
from backend_v2.models.dtos.pdf_context import ReportContext
from backend_v2.models.dtos.report import XAIFlatReportDTO


class XAIReporterInput(BaseModel):
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
    step_analyst: Any | None = Field(default=None, description="Analyst hypotheses and RAG data.")
    step_profiler: Any | None = Field(default=None, description="Profiler cognitive bias data.")
    step_falsifier: Any | None = Field(default=None, description="Falsifier critical distance data.")
    step_logician: Any | None = Field(default=None, description="Logician Toulmin analysis data.")
    step_causal_analyst: Any | None = Field(
        default=None, description="Causal Analyst post-hoc and counterfactual data."
    )

    model_config = ConfigDict(frozen=True, extra="allow")

    @model_validator(mode="after")
    def check_judges(self) -> XAIReporterInput:
        # The Agent execute still has Fail Fast, but we can do a quick check here too if desired.
        return self


class XAIScoreItem(BaseModel):
    """A single score item for the scorecard."""

    label: str = Field(..., description="Label for the score item.")
    score: float = Field(..., description="Score value.")
    reasoning: str | None = Field(default=None, description="Reasoning for the score.")
    weight: float = Field(default=1.0, description="Weight of this item.")

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    @field_validator("label")
    @classmethod
    def validate_non_empty(cls, v: str | None) -> str:
        if not v or not str(v).strip():
            msg = "Field cannot be empty or whitespace only."
            logger.error("[XAIModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return str(v).strip()


class CitationExtension(BaseModel):
    extension_type: Literal[XaiExtensionType.CITATION] = XaiExtensionType.CITATION
    source_id: str
    snippet: str
    url: str | None = None
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

class JustificationExtension(BaseModel):
    extension_type: Literal[XaiExtensionType.JUSTIFICATION] = XaiExtensionType.JUSTIFICATION
    reasoning: str
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

class FalsificationExtension(BaseModel):
    extension_type: Literal[XaiExtensionType.FALSIFICATION] = XaiExtensionType.FALSIFICATION
    counter_argument: str
    vulnerabilities: list[str]
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

class TheoryLinkExtension(BaseModel):
    extension_type: Literal[XaiExtensionType.THEORY_LINK] = XaiExtensionType.THEORY_LINK
    theory_name: str
    relevance: str
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

class RiskFlagExtension(BaseModel):
    extension_type: Literal[XaiExtensionType.RISK_FLAG] = XaiExtensionType.RISK_FLAG
    risk_level: str
    description: str
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

class CoachingExtension(BaseModel):
    extension_type: Literal[XaiExtensionType.COACHING] = XaiExtensionType.COACHING
    actionable_steps: list[str]
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

class MissingContextExtension(BaseModel):
    extension_type: Literal[XaiExtensionType.MISSING_CONTEXT] = XaiExtensionType.MISSING_CONTEXT
    context_needed: str
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

class RemediationStepsExtension(BaseModel):
    extension_type: Literal[XaiExtensionType.REMEDIATION_STEPS] = XaiExtensionType.REMEDIATION_STEPS
    steps: list[str]
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

class EmotionalSentimentExtension(BaseModel):
    extension_type: Literal[XaiExtensionType.EMOTIONAL_SENTIMENT] = XaiExtensionType.EMOTIONAL_SENTIMENT
    sentiment: str
    intensity: float
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

class ConfidenceExtension(BaseModel):
    extension_type: Literal[XaiExtensionType.CONFIDENCE] = XaiExtensionType.CONFIDENCE
    confidence_score: float
    rationale: str
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

class SourceIDExtension(BaseModel):
    extension_type: Literal[XaiExtensionType.SOURCE_ID] = XaiExtensionType.SOURCE_ID
    source_id: str
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

XAIExtension = Annotated[
    Union[
        CitationExtension,
        JustificationExtension,
        FalsificationExtension,
        TheoryLinkExtension,
        RiskFlagExtension,
        CoachingExtension,
        MissingContextExtension,
        RemediationStepsExtension,
        EmotionalSentimentExtension,
        ConfidenceExtension,
        SourceIDExtension,
    ],
    Field(discriminator="extension_type")
]


class ComparisonDataDTO(BaseModel):
    baseline_score: float | None = None
    delta: float | None = None
    trend: str | None = None
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")


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
        description="High-level summary.",
        json_schema_extra={"x-ui-label": "Executive Summary"},
    )
    verified_facts: str = Field(
        ...,
        description="Synthesis of facts.",
        json_schema_extra={"x-ui-label": "Verified Facts"},
    )
    cognitive_behavior: str = Field(
        ...,
        description="Synthesis of Profiler and Falsifier findings.",
        json_schema_extra={"x-ui-label": "Cognitive Behavior"},
    )
    causal_chain: str = Field(
        ...,
        description="Synthesis of Causal and Logician findings.",
        json_schema_extra={"x-ui-label": "Causal Chain"},
    )
    analysis_strengths: str = Field(
        ...,
        description="Strengths identified.",
        json_schema_extra={"x-ui-label": "Strengths"},
    )
    analysis_weaknesses: str = Field(
        ...,
        description="Weaknesses identified.",
        json_schema_extra={"x-ui-label": "Weaknesses"},
    )
    analysis_opportunities: str = Field(
        ...,
        description="Opportunities identified.",
        json_schema_extra={"x-ui-label": "Opportunities"},
    )
    analysis_recommendations: str = Field(
        ...,
        description="Recommendations.",
        json_schema_extra={"x-ui-label": "Recommendations"},
    )
    final_verdict: str = Field(
        ...,
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
    
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    @field_validator(
        "executive_summary",
        "verified_facts",
        "cognitive_behavior",
        "causal_chain",
        "analysis_strengths",
        "analysis_weaknesses",
        "analysis_opportunities",
        "analysis_recommendations",
        "final_verdict",
    )
    @classmethod
    def validate_non_empty(cls, v: str | None) -> str:
        if not v or not str(v).strip():
            msg = "Field cannot be empty or whitespace only."
            logger.error("[XAIModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return str(v).strip()

    @field_validator("confidence_score")
    @classmethod
    def validate_score(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            msg = "Confidence score must be between 0.0 and 1.0."
            logger.error("[XAIModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return v


class XAIOutput(XAIOutputDTO, ReasoningTrace):
    """Output schema for the XAI Reporter Agent."""

    score_cards: list[JudgeScoreCard] = Field(
        default_factory=list,
        description="Aggregated scores from all judges.",
        json_schema_extra={"x-ui-label": "Scorecards"},
    )
    flat_report: XAIFlatReportDTO | None = Field(
        default=None,
        description="Flattened, machine-readable report summary.",
        json_schema_extra={"x-ui-label": "Flat Report"},
    )

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")


class ReportResult(BaseModel):
    """Result of the report generation (Hook)."""

    report_content: str = Field(
        ..., description="The generated Markdown report.", json_schema_extra={"x-ui-label": "Report Content"}
    )
    format: str = Field(default="markdown", description="Report format.", json_schema_extra={"x-ui-label": "Format"})
    data: ReportContext | None = Field(
        default=None, description="The structured data used to generate the report (SSOT)."
    )

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    @field_validator("report_content")
    @classmethod
    def validate_non_empty(cls, v: str | None) -> str:
        if not v or not str(v).strip():
            msg = "Report content cannot be empty."
            logger.error("[XAIModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return v
