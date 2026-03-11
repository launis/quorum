"""XAI Agent Domain Models.

This module contains the schemas for the XAI Reporter Agent,
including the final report output and context for report generation.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend_v2.models.domain.judge import JudgeOutput, JudgeScoreCard
from backend_v2.models.dtos.pdf_context import ReportContext
from backend_v2.models.dtos.report import XAIFlatReportDTO


class XAIReporterInput(BaseModel):
    """Strict input schema for XAIReporterAgent."""

    last_reasoning_trace: str | None = Field(default=None, description="Previous reasoning trace.")
    step_judge: JudgeOutput | None = Field(default=None, description="Standard evaluate output.")
    step_judge_cognitive: JudgeOutput | None = Field(default=None, description="Cognitive Judge output.")

    model_config = ConfigDict(frozen=True, extra="ignore")

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

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("label")
    @classmethod
    def validate_non_empty(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class XAIOutputDTO(ReasoningTraceDTO):
    """Data Transfer Object for XAI Reporter Agent (Content Only)."""

    executive_summary: str = Field(
        ...,
        description="High-level summary.",
        json_schema_extra={"x-ui-label": "Executive Summary"},
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
    comparison_data: dict[str, Any] | None = Field(
        default=None,
        description="Structured comparison data.",
        json_schema_extra={"x-ui-label": "Comparison Data"},
    )

    model_config = ConfigDict(frozen=True, extra="ignore")

    @field_validator(
        "executive_summary",
        "analysis_strengths",
        "analysis_weaknesses",
        "analysis_opportunities",
        "analysis_recommendations",
        "final_verdict",
    )
    @classmethod
    def validate_non_empty(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()

    @field_validator("confidence_score")
    @classmethod
    def validate_score(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("Confidence score must be between 0.0 and 1.0.")
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

    model_config = ConfigDict(frozen=True, strict=True)




class ReportResult(BaseModel):
    """Result of the report generation (Hook)."""

    report_content: str = Field(
        ..., description="The generated Markdown report.", json_schema_extra={"x-ui-label": "Report Content"}
    )
    format: str = Field(default="markdown", description="Report format.", json_schema_extra={"x-ui-label": "Format"})
    data: ReportContext | None = Field(
        default=None, description="The structured data used to generate the report (SSOT)."
    )

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("report_content")
    @classmethod
    def validate_non_empty(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not v or not v.strip():
            raise ValueError("Report content cannot be empty.")
        return v
