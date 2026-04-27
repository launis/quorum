from datetime import datetime
from typing import Any
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

from pydantic import ConfigDict

from backend_v2.models.domain.analyst import SearchResult
from backend_v2.models.domain.archivist import ArchivistOutputDTO
from backend_v2.models.domain.coach import BibliographyResult, CoachingPlanDTO
from backend_v2.models.view.sdui import ReferenceItem


class MatrixFieldsMixin(BaseDTO):
    justification: str | None = None
    raw_result: str | None = None
    normalized_score: float | None = None
    raw_score: float | None = None
    evaluated_atoms: dict[str, bool] | None = None
    extensions: dict[str, str] | None = None
    level_breakdown: dict[str, dict[str, int]] | None = None


class XaiReportData(MatrixFieldsMixin):
    executive_summary: str | None = None
    evaluation_notes: str | None = None
    model_config = ConfigDict(strict=True, extra="forbid")


class JudgeReportData(MatrixFieldsMixin):
    critical_findings: list[str] = Field(default_factory=list)
    model_config = ConfigDict(strict=True, extra="forbid")


class OverseerData(BaseDTO):
    ethical_issues: list[str] = Field(default_factory=list)
    model_config = ConfigDict(strict=True, extra="forbid")


class OverseerReportData(MatrixFieldsMixin):
    overseer_data: OverseerData | None = None
    model_config = ConfigDict(strict=True, extra="forbid")


class LogicianScheme(BaseDTO):
    critical_questions: list[str] = Field(default_factory=list)
    model_config = ConfigDict(strict=True, extra="forbid")


class LogicianData(BaseDTO):
    walton_scheme: LogicianScheme | None = None
    model_config = ConfigDict(strict=True, extra="forbid")


class LogicianReportData(MatrixFieldsMixin):
    logician_data: LogicianData | None = None
    model_config = ConfigDict(strict=True, extra="forbid")


class PerformativityAnalysis(BaseDTO):
    pre_mortem_analysis: str | None = None
    weak_signals: list[str] = Field(default_factory=list)
    model_config = ConfigDict(strict=True, extra="forbid")


class PerformativityReportData(MatrixFieldsMixin):
    performativity_analysis: PerformativityAnalysis | None = None
    model_config = ConfigDict(strict=True, extra="forbid")


class AnalystReportData(MatrixFieldsMixin):
    rag_evidence: list[str] = Field(default_factory=list)
    model_config = ConfigDict(strict=True, extra="forbid")


class FalsifierData(BaseDTO):
    vulnerabilities: list[str] = Field(default_factory=list)
    model_config = ConfigDict(strict=True, extra="forbid")


class CausalAnalysisData(BaseDTO):
    counterfactuals: list[str] = Field(default_factory=list)
    model_config = ConfigDict(strict=True, extra="forbid")


class PanelReportData(MatrixFieldsMixin):
    overseer_data: OverseerData | None = None
    logician_data: LogicianData | None = None
    performativity_analysis: PerformativityAnalysis | None = None
    falsifier_data: FalsifierData | None = None
    causal_analysis: CausalAnalysisData | None = None
    model_config = ConfigDict(strict=True, extra="forbid")


class ProfilerMetrics(BaseDTO):
    word_count: int = 0
    control_ratio: float = 0.0
    model_config = ConfigDict(strict=True, extra="forbid")


class ProfilerReportData(MatrixFieldsMixin):
    metrics: ProfilerMetrics | None = None
    model_config = ConfigDict(strict=True, extra="forbid")


class PenaltyData(BaseDTO):
    penalty_type: str
    impact: float
    model_config = ConfigDict(strict=True, extra="forbid")


class ScoreSummaryData(BaseDTO):
    total_score: float = 0.0
    normalized_score: float = 0.0
    model_config = ConfigDict(strict=True, extra="forbid")


class ScoringReportData(MatrixFieldsMixin):
    penalties_applied: list[PenaltyData] | None = None
    score_summary: ScoreSummaryData | None = None
    model_config = ConfigDict(strict=True, extra="forbid")


class ValidationWarningData(BaseDTO):
    warning_type: str
    message: str
    model_config = ConfigDict(strict=True, extra="forbid")


class ValidationReportData(MatrixFieldsMixin):
    warnings: list[ValidationWarningData] | None = None
    model_config = ConfigDict(strict=True, extra="forbid")


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
    step_archivist: ArchivistOutputDTO | list[ArchivistOutputDTO] | None = None
    step_coach: CoachingPlanDTO | None = None
    bibliography_result: BibliographyResult | list[BibliographyResult] | None = None
    search_result: SearchResult | list[SearchResult] | None = None

    model_config = ConfigDict(strict=True, extra="forbid")


class MatrixObservabilityItem(BaseDTO):
    normalized_score: float = 0.0
    raw_result: str = ""
    justification: str = ""
    model_config = ConfigDict(strict=True, extra="forbid")


class MatrixObservabilityDTO(BaseDTO):
    """Securely transmits only essential counts to prevent token explosions."""

    true_atoms_count: int = Field(default=0, description="Total number of true evaluation atoms.")
    false_atoms_count: int = Field(default=0, description="Total number of false evaluation atoms.")
    matrices: dict[str, MatrixObservabilityItem] = Field(default_factory=dict)

    # Strictly enforce Fail-Fast Pydantic V2 validations to prevent orphaned state.
    model_config = ConfigDict(strict=True, extra="forbid")


class ReportSynthesisDTO(BaseDTO):
    """Top-level container enforcing strict typing over the reporting hook payload."""

    inputs: MatrixObservabilityDTO
    global_context_vars: GlobalContextVarsDTO

    model_config = ConfigDict(strict=True, extra="forbid")


class AuditQuestionItem(BaseDTO):
    question: str
    status: str
    model_config = ConfigDict(strict=True, extra="forbid")


class ScoreItem(BaseDTO):
    score: float
    reasoning: str
    label: str
    model_config = ConfigDict(strict=True, extra="forbid")


class ReportContextDTO(BaseDTO):
    """Strictly typed schema for the aggregated report context injected into state."""

    inputs: MatrixObservabilityDTO
    generated_at: str
    timestamp: str
    summary: str
    critical_findings: list[str] = Field(default_factory=list)
    pre_mortem_signals: list[str] = Field(default_factory=list)
    ethical_issues: list[str] = Field(default_factory=list)
    audit_questions: list[AuditQuestionItem] = Field(default_factory=list)
    scores: dict[str, ScoreItem] = Field(default_factory=dict)
    average_score: float = 0.0
    hitl_required: bool = False
    uncertainty: dict[str, str] = Field(default_factory=dict)
    bibliography: list[dict[str, Any]] = Field(default_factory=list)
    references: list[ReferenceItem] = Field(default_factory=list)

    # Specialist Data (passthrough for templates)
    logician_data: dict[str, Any] | None = None
    overseer_data: dict[str, Any] | None = None
    falsifier_data: FalsifierData | None = None
    causal_analysis: CausalAnalysisData | None = None
    performativity_analysis: dict[str, Any] | None = None

    # Enrichment
    word_count: int | None = None
    input_control_ratio: float | None = None
    google_search_results: list[Any] = Field(default_factory=list)
    knowledge_items: list[Any] = Field(default_factory=list)

    archivist_precedents: ArchivistOutputDTO | list[ArchivistOutputDTO] | None = None
    penalties_applied: list[PenaltyData] | None = None
    score_summary: ScoreSummaryData | None = None
    structural_warnings: list[ValidationWarningData] | None = None
    coaching_plan: CoachingPlanDTO | None = None

    model_config = ConfigDict(strict=True, extra="forbid")
