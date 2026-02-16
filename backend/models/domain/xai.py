"""XAI Agent Domain Models.

This module contains the schemas for the XAI Reporter Agent,
including the final report output and context for report generation.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.models.domain.base import ReasoningTrace
from backend.models.domain.causal import CausalAnalysis
from backend.models.domain.coach import BibliographyItem
from backend.models.domain.falsifier import FalsifierData
from backend.models.domain.judge import JudgeScoreCard
from backend.models.domain.logician import LogicianData
from backend.models.domain.overseer import OverseerData
from backend.models.domain.performativity import PerformativityAnalysis
from backend.models.domain.retrieval import KnowledgeItem


class XAIScoreItem(BaseModel):
    """A single score item for the scorecard."""
    label: str = Field(..., description="Label for the score item.")
    score: float = Field(..., description="Score value.")
    reasoning: str | None = Field(default=None, description="Reasoning for the score.")
    weight: float = Field(default=1.0, description="Weight of this item.")

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("label")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class XAIOutput(ReasoningTrace):
    """Output schema for the XAI Reporter Agent."""

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
    score_cards: list[JudgeScoreCard] = Field(
        default_factory=list,
        description="Aggregated scores from all judges.",
        json_schema_extra={"x-ui-label": "Scorecards"},
    )

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator(
        "executive_summary",
        "analysis_strengths",
        "analysis_weaknesses",
        "analysis_opportunities",
        "analysis_recommendations",
        "final_verdict"
    )
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()

    @field_validator("confidence_score")
    @classmethod
    def validate_score(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("Confidence score must be between 0.0 and 1.0.")
        return v


class ReportContext(BaseModel):
    """Context for the Jinja2 report template."""
    summary: str = Field(..., description="Executive summary.")
    critical_findings: list[str] = Field(..., description="Critical findings.")
    pre_mortem_signals: list[str] = Field(..., description="Pre-mortem signals.")
    hitl_required: bool = Field(..., description="HITL required.")
    ethical_issues: list[dict[str, Any]] = Field(..., description="Ethical issues.")
    audit_questions: list[dict[str, Any]] = Field(..., description="Audit questions.")
    uncertainty: dict[str, Any] = Field(..., description="Uncertainty metrics.")
    scores: dict[str, dict[str, Any]] = Field(..., description="Scores (arvosana, perustelu).")
    average_score: float = Field(..., description="Average score.")
    timestamp: str = Field(..., description="Report timestamp.")
    coaching_plan: dict[str, Any] | None = Field(default=None, description="Coaching plan.")
    penalties_applied: list[str] = Field(default_factory=list, description="Penalties applied.")
    score_summary: str | None = Field(default=None, description="Score summary.")
    input_control_ratio: float | None = Field(default=None, description="Input control ratio.")
    word_count: int | None = Field(default=None, description="Total word count.")
    structural_warnings: list[str] = Field(default_factory=list, description="Structural warnings.")
    archivist_precedents: Any | None = Field(default=None, description="Archivist precedents.")
    google_search_results: list[dict[str, Any]] = Field(default_factory=list, description="Google search results.")
    bibliography: list[BibliographyItem] = Field(default_factory=list, description="Authoritative bibliography.")

    # Specialist Agents (Deep Analysis)
    logician_data: LogicianData | None = Field(default=None, description="Logician analysis.")
    falsifier_data: FalsifierData | None = Field(default=None, description="Falsifier analysis.")
    causal_analysis: CausalAnalysis | None = Field(default=None, description="Causal analysis.")
    performativity_analysis: PerformativityAnalysis | None = Field(default=None, description="Performativity analysis.")
    overseer_data: OverseerData | None = Field(default=None, description="Overseer analysis.")
    knowledge_items: list[KnowledgeItem] = Field(default_factory=list, description="Knowledge Base items.")

    model_config = ConfigDict(frozen=False, strict=True)


class ReportResult(BaseModel):
    """Result of the report generation (Hook)."""
    report_content: str = Field(..., description="The generated Markdown report.", json_schema_extra={"x-ui-label": "Report Content"})
    format: str = Field(default="markdown", description="Report format.", json_schema_extra={"x-ui-label": "Format"})
    data: ReportContext | None = Field(default=None, description="The structured data used to generate the report (SSOT).")

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("report_content")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
             raise ValueError("Report content cannot be empty.")
        return v
