from datetime import datetime
from uuid import UUID

from pydantic import Field

from backend_v2.models.dtos.base import BaseDTO


class XAIFlatReportDTO(BaseDTO):
    """A flattened, machine-readable report summary optimized for BI tools and external integration.
    Contains no Markdown, no nested structures (except the scores dict), and strictly typed fields.
    """

    execution_id: UUID = Field(..., description="The unique ID of the workflow execution.")
    timestamp: datetime = Field(..., description="When this report was generated.")

    # High-Level Outcomes
    verdict: str = Field(..., description="Final decision (e.g., 'Approved', 'Rejected').")
    score_total: float = Field(..., description="The total calculated score (0.0 - 5.0).")
    confidence_score: float = Field(..., description="AI confidence in the result (0.0 - 1.0).")

    # Key Drivers
    top_strength_id: str | None = Field(None, description="ID of the highest scoring dimension.")
    top_weakness_id: str | None = Field(None, description="ID of the lowest scoring dimension.")

    # Flattened Metrics (Key-Value for easy BI pivoting)
    # Example: {"clarity": 4.5, "logic": 3.0, "evidence": 5.0}
    flattened_scores: dict[str, float] = Field(
        default_factory=dict, description="Key-value map of dimension IDs to their numeric scores."
    )


# Epic 34: Global Hooks Zero-Compromise Hardening - Schema-First Templating
from typing import Any

from pydantic import ConfigDict


class ScoreCardDimension(BaseDTO):
    dimension_id: str
    dimension_label: str
    score: float
    reasoning: str


class ScoreCard(BaseDTO):
    total_score: float = 0.0
    dimensions: list[ScoreCardDimension] = Field(default_factory=list)


class XaiReportData(BaseDTO):
    executive_summary: str | None = None
    score_cards: list[ScoreCard] | None = None
    evaluation_notes: str | None = None


class JudgeReportData(BaseDTO):
    critical_findings: list[str] = Field(default_factory=list)
    score_card: ScoreCard | None = None


class OverseerData(BaseDTO):
    ethical_issues: list[dict[str, Any]] = Field(default_factory=list)


class OverseerReportData(BaseDTO):
    overseer_data: OverseerData | None = None


class LogicianScheme(BaseDTO):
    critical_questions: list[str] = Field(default_factory=list)


class LogicianData(BaseDTO):
    walton_scheme: LogicianScheme | None = None


class LogicianReportData(BaseDTO):
    logician_data: LogicianData | None = None


class PerformativityAnalysis(BaseDTO):
    pre_mortem_analysis: dict[str, Any] | None = None
    weak_signals: list[str] = Field(default_factory=list)


class PerformativityReportData(BaseDTO):
    performativity_analysis: PerformativityAnalysis | None = None


class AnalystReportData(BaseDTO):
    rag_evidence: list[dict[str, Any]] = Field(default_factory=list)


class PanelReportData(BaseDTO):
    overseer_data: OverseerData | None = None
    logician_data: LogicianData | None = None
    performativity_analysis: PerformativityAnalysis | None = None
    falsifier_data: dict[str, Any] | None = None
    causal_analysis: dict[str, Any] | None = None


class ProfilerMetrics(BaseDTO):
    word_count: int = 0
    control_ratio: float = 0.0


class ProfilerReportData(BaseDTO):
    metrics: ProfilerMetrics | None = None


class ScoringReportData(BaseDTO):
    penalties_applied: list[Any] | None = None
    score_summary: dict[str, Any] | None = None


class ValidationReportData(BaseDTO):
    warnings: list[Any] | None = None


class GlobalContextVarsDTO(BaseDTO):
    """Schema for parsing agent outputs dynamically from global_context_vars."""

    step_xai: XaiReportData | None = None
    step_judge: JudgeReportData | None = None
    step_overseer: OverseerReportData | None = None
    step_logician: LogicianReportData | None = None
    step_detector: PerformativityReportData | None = None
    step_analyst: AnalystReportData | None = None
    step_panel: PanelReportData | None = None
    step_profiler: ProfilerReportData | None = None
    step_scoreengine1: ScoringReportData | None = None
    step_validation: ValidationReportData | None = None
    step_archivist: dict[str, Any] | list[Any] | None = None
    step_coach: dict[str, Any] | None = None
    bibliography_result: dict[str, Any] | list[Any] | None = None
    search_result: dict[str, Any] | list[Any] | None = None

    model_config = ConfigDict(extra="ignore")


class ReportSynthesisDTO(BaseDTO):
    """Top-level container enforcing strict typing over the reporting hook payload."""

    inputs: dict[str, Any]
    global_context_vars: GlobalContextVarsDTO

    model_config = ConfigDict(extra="ignore")
