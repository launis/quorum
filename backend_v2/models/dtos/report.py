from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from backend_v2.models.domain.analyst import SearchResult
from backend_v2.models.domain.archivist import ArchivistOutputDTO
from backend_v2.models.domain.coach import BibliographyResult, CoachingPlanDTO
from backend_v2.models.domain.linguistics import LinguisticsResultDTO
from backend_v2.models.dtos.base import BaseDTO
from backend_v2.models.view.sdui import ReferenceItem


class XAIFlatReportDTO(BaseDTO):
    """A flattened, machine-readable report summary optimized for BI tools and external integration.

    Attributes:
        execution_id: The unique ID of the workflow execution.
        timestamp: When this report was generated.
        verdict: Final decision (e.g., 'Approved', 'Rejected').
        score_total: The total calculated score (0.0 - 5.0).
        confidence_score: AI confidence in the result (0.0 - 1.0).
        top_strength_id: ID of the highest scoring dimension.
        top_weakness_id: ID of the lowest scoring dimension.
        flattened_scores: Key-value map of dimension IDs to their numeric scores.
    """

    execution_id: str = Field(..., description="The unique ID of the workflow execution.")
    timestamp: datetime = Field(..., description="When this report was generated.")

    # High-Level Outcomes
    verdict: str = Field(..., description="Final decision (e.g., 'Approved', 'Rejected').")
    score_total: float = Field(..., description="The total calculated score (0.0 - 5.0).")
    confidence_score: float = Field(..., description="AI confidence in the result (0.0 - 1.0).")

    # Key Drivers
    top_strength_id: str | None = Field(None, description="ID of the highest scoring dimension.")
    top_weakness_id: str | None = Field(None, description="ID of the lowest scoring dimension.")

    # Flattened Metrics (Key-Value for easy BI pivoting)
    flattened_scores: dict[str, float] = Field(
        default_factory=dict, description="Key-value map of dimension IDs to their numeric scores."
    )


class MatrixFieldsMixin(BaseDTO):
    """Mixin capturing typical automated scoring assessment outcomes across matrices.

    Attributes:
        justification: Free-text justification for the assigned matrix assessment.
        normalized_score: Matrix score normalized to a percentage or standard range.
        raw_score: Absolute computed unnormalized numeric score.
        evaluated_atoms: Evaluation indicators evaluated during execution.
        extensions: Flexible additional telemetry metadata mapped dynamically.
        level_breakdown: Multi-tier level outcomes computed during execution.
        xai_log: Rich log variables tracing decision parameters.
    """

    justification: str | None = None
    normalized_score: float | None = None
    raw_score: float | None = None
    evaluated_atoms: dict[str, bool | str] | None = None
    extensions: dict[str, str] | None = None
    level_breakdown: dict[str, dict[str, int]] | None = None
    xai_log: dict[str, Any] | None = None


class XaiReportData(MatrixFieldsMixin):
    """Xai execution step payload model.

    Attributes:
        executive_summary: Concise overview of findings from execution run.
        evaluation_notes: Supporting operational analysis notes.
    """

    executive_summary: str | None = None
    evaluation_notes: str | None = None


class JudgeReportData(MatrixFieldsMixin):
    """Judge execution step payload model.

    Attributes:
        critical_findings: List of critical issues identified during validation.
    """

    critical_findings: list[str] = Field(default_factory=list)


class OverseerData(BaseDTO):
    """Overseer critical indicators mapping.

    Attributes:
        ethical_issues: Ethical issues detected during text inspection.
    """

    ethical_issues: list[str] = Field(default_factory=list)


class OverseerReportData(MatrixFieldsMixin):
    """Overseer step wrapper payload model.

    Attributes:
        overseer_data: Contained critical flags and parsed issue lists.
    """

    overseer_data: OverseerData | None = None


class LogicianScheme(BaseDTO):
    """Logician Walton critical argument analysis scheme schema.

    Attributes:
        critical_questions: Evaluated questions matching Walton argumentation structure.
    """

    critical_questions: list[str] = Field(default_factory=list)


class LogicianData(BaseDTO):
    """Logician container for argument mappings.

    Attributes:
        walton_scheme: Specific Walton argumentation criteria structured output.
    """

    walton_scheme: LogicianScheme | None = None


class LogicianReportData(MatrixFieldsMixin):
    """Logician execution step payload model.

    Attributes:
        logician_data: Structured argumentation metrics container.
    """

    logician_data: LogicianData | None = None


class PerformativityAnalysis(BaseDTO):
    """Detailed behavioral authenticity or performative actions metric structures.

    Attributes:
        pre_mortem_analysis: Proactive simulation analysis identifying soft failures.
        weak_signals: Non-obvious behavioral or structural anomalies.
    """

    pre_mortem_analysis: str | None = None
    weak_signals: list[str] = Field(default_factory=list)


class PerformativityReportData(MatrixFieldsMixin):
    """Detector execution step payload model.

    Attributes:
        performativity_analysis: Authenticity assessment structured model attributes.
    """

    performativity_analysis: PerformativityAnalysis | None = None


class AnalystReportData(MatrixFieldsMixin):
    """Analyst execution step payload model containing direct citation sources.

    Attributes:
        rag_evidence: Explicit evidence strings derived from external search or KB.
    """

    rag_evidence: list[str] = Field(default_factory=list)


class FalsifierData(BaseDTO):
    """Falsifier execution metrics payload mapping.

    Attributes:
        vulnerabilities: Identified systemic issues and blindspots.
    """

    vulnerabilities: list[str] = Field(default_factory=list)


class CausalAnalysisData(BaseDTO):
    """Causal scenario testing parameters mapping.

    Attributes:
        counterfactuals: Hypothetical structural alterations analyzed during execution.
    """

    counterfactuals: list[str] = Field(default_factory=list)


class PanelReportData(MatrixFieldsMixin):
    """Combined panel execution step payload model.

    Attributes:
        overseer_data: Merged ethical review metadata.
        logician_data: Merged logical analysis mappings.
        performativity_analysis: Merged behavioral metrics.
        falsifier_data: Dynamic vulnerabilities assessment data.
        causal_analysis: Alternative logic metrics.
    """

    overseer_data: OverseerData | None = None
    logician_data: LogicianData | None = None
    performativity_analysis: PerformativityAnalysis | None = None
    falsifier_data: FalsifierData | None = None
    causal_analysis: CausalAnalysisData | None = None


class ProfilerMetrics(BaseDTO):
    """Linguistic profile statistics metadata representation.

    Attributes:
        word_count: Total size of input text evaluated.
        control_ratio: Computed ratio tracking sentence structuring.
    """

    word_count: int = 0
    control_ratio: float = 0.0


class ProfilerReportData(MatrixFieldsMixin):
    """Profiler execution step payload model.

    Attributes:
        metrics: Text length and formatting patterns metadata.
    """

    metrics: ProfilerMetrics | None = None


class PenaltyData(BaseDTO):
    """Scoring penalty application metrics details.

    Attributes:
        penalty_type: Machine-readable key describing the category of penalty.
        impact: Score reduction applied to final assessment.
    """

    penalty_type: str
    impact: float


class ScoreSummaryData(BaseDTO):
    """Consolidated summary metrics schema.

    Attributes:
        total_score: Absolute unweighted scoring average.
        normalized_score: Final scaled scoring percentage.
    """

    total_score: float = 0.0
    normalized_score: float = 0.0


class ScoringReportData(MatrixFieldsMixin):
    """Scoring engine step output payload model.

    Attributes:
        penalties_applied: Specific deductions applied based on compliance markers.
        score_summary: Standardized high-level totals.
    """

    penalties_applied: list[PenaltyData] | None = None
    score_summary: ScoreSummaryData | None = None


class ValidationWarningData(BaseDTO):
    """Preflight system warning structural model.

    Attributes:
        warning_type: Specific rule identifier.
        message: Descriptive notification detailing dynamic issues.
    """

    warning_type: str
    message: str


class ValidationReportData(MatrixFieldsMixin):
    """Validator execution step output payload model.

    Attributes:
        warnings: Identified validation or schema issues.
    """

    warnings: list[ValidationWarningData] | None = None


class GlobalContextVarsDTO(BaseDTO):
    """Schema for parsing agent outputs dynamically from global_context_vars.

    Attributes:
        step_xai: Xai payload.
        step_judge: Judge payload.
        step_overseer: Overseer payload.
        step_logician: Logician payload.
        step_detector: Detector payload.
        step_linguistics: Linguistics payload.
        step_analyst: Analyst payload.
        step_panel: Combined panel payload.
        step_profiler: Profiler payload.
        step_scoreengine1: Scoring results payload.
        step_validation: Preflight validator outcomes.
        step_archivist: Historical records or templates matching context.
        step_coach: Performance recommendations data.
        bibliography_result: Parsed research bibliographies.
        search_result: External API engine outputs.
    """

    step_xai: XaiReportData | None = None
    step_judge: JudgeReportData | None = None
    step_overseer: OverseerReportData | None = None
    step_logician: LogicianReportData | None = None
    step_detector: PerformativityReportData | None = None
    step_linguistics: LinguisticsResultDTO | None = None
    step_analyst: AnalystReportData | None = None
    step_panel: PanelReportData | None = None
    step_profiler: ProfilerReportData | None = None
    step_scoreengine1: ScoringReportData | None = None
    step_validation: ValidationReportData | None = None
    step_archivist: ArchivistOutputDTO | list[ArchivistOutputDTO] | None = None
    step_coach: CoachingPlanDTO | None = None
    bibliography_result: BibliographyResult | list[BibliographyResult] | None = None
    search_result: SearchResult | list[SearchResult] | None = None


class MatrixObservabilityItem(BaseDTO):
    """Individual dimension tracking diagnostic item.

    Attributes:
        normalized_score: Normalised score value representation.
        justification: Text detailing reasons for evaluation output.
    """

    normalized_score: float = 0.0
    justification: str = ""


class MatrixObservabilityDTO(BaseDTO):
    """Securely transmits only essential counts to prevent token explosions.

    Attributes:
        true_atoms_count: Total number of true evaluation atoms.
        false_atoms_count: Total number of false evaluation atoms.
        matrices: Evaluated parameters indexed by dimension key.
    """

    true_atoms_count: int = Field(default=0, description="Total number of true evaluation atoms.")
    false_atoms_count: int = Field(default=0, description="Total number of false evaluation atoms.")
    matrices: dict[str, MatrixObservabilityItem] = Field(default_factory=dict)


class ReportSynthesisDTO(BaseDTO):
    """Top-level container enforcing strict typing over the reporting hook payload.

    Attributes:
        inputs: Captured analytical metrics state.
        global_context_vars: State variables resolved during execution stages.
    """

    inputs: MatrixObservabilityDTO
    global_context_vars: GlobalContextVarsDTO


class AuditQuestionItem(BaseDTO):
    """Key diagnostic question generated by structural nodes.

    Attributes:
        question: Explicit inquiry detailing logic limits.
        status: Evaluated context tracking marker.
    """

    question: str
    status: str


class ScoreItem(BaseDTO):
    """A normalized dimension score evaluation object.

    Attributes:
        score: Assigned quantitative value.
        reasoning: Analytical proof justifying total assigned.
        label: Translated presentation string ID.
    """

    score: float
    reasoning: str
    label: str


class ReportContextDTO(BaseDTO):
    """Strictly typed schema for the aggregated report context injected into state.

    Attributes:
        inputs: Dimension evaluations telemetry tracking metrics.
        generated_at: Localization timeline metadata string.
        timestamp: Formatted generation identifier time.
        summary: Extracted core narrative of report contents.
        critical_findings: Essential security or structure issues identified.
        pre_mortem_signals: Soft failure signals resolved across state.
        ethical_issues: Filtered risk triggers evaluated in Overseer.
        audit_questions: Targeted questions checking reasoning consistency.
        scores: Dynamic dimension parameters keyed mapping.
        average_score: Summary evaluation total.
        hitl_required: Flag indicating intervention protocols.
        uncertainty: Logical boundaries mapping parameters.
        bibliography: Referenced publications structure records.
        references: Cleaned web or context references list.
        output_extensions: Interactive components metadata mapped dynamically.
        logician_data: Core argumentation metrics mapping properties.
        overseer_data: Core compliance indicators metadata context.
        falsifier_data: Identified structural security constraints.
        causal_analysis: Scenarios mapping evaluation counterfactuals.
        performativity_analysis: Authenticity parameters mapped in detector.
        word_count: Total count metrics computed during evaluation.
        input_control_ratio: Formatted text patterns density ratio.
        google_search_results: Live search telemetry entries parsed.
        knowledge_items: Context items selected from internal vector DB.
        archivist_precedents: Matches identified from historical snapshots.
        penalties_applied: Direct deductions processed during scoring.
        score_summary: Aggregated rating metrics computed by engine.
        structural_warnings: Validations flags that occurred before compilation.
        coaching_plan: Structured personal growth steps derived from trace.
    """

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
    output_extensions: list[Any] = Field(default_factory=list)

    # Specialist Data (passthrough for templates)
    logician_data: LogicianData | None = None
    overseer_data: OverseerData | None = None
    falsifier_data: FalsifierData | None = None
    causal_analysis: CausalAnalysisData | None = None
    performativity_analysis: PerformativityAnalysis | None = None

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


class TraceScoringPayloadDTO(BaseDTO):
    """Strict hydration schema for extracting scoring results in BlueprintTransformer.

    Attributes:
        total_score: Absolute unweighted scoring average parsed.
        final_score: Final scaled result value representation.
        normalized_score: Scaled percentage equivalent indicator.
        penalties_applied: deductions traced back during parsing.
        aggregation_status: Internal workflow engine status message tracking calculations.
    """

    total_score: float | None = None
    final_score: float | None = None
    normalized_score: float | None = None
    penalties_applied: list[Any] | None = None
    aggregation_status: str | None = None


class TraceMatrixPayloadDTO(BaseDTO):
    """Strict hydration schema for extracting matrix payloads from execution trace.

    Attributes:
        raw_score: Original quantitative output evaluation parsed.
        normalized_score: Scaled matrix performance standard calculated.
        justification: Underlying reasoning evaluated for matrix dimension.
        level_breakdown: Trace levels details mapping.
        extensions: Trace options dynamic mapping.
        evaluated_atoms: Trace indicators tracking mapped parameters.
        xai_log: System decision metadata tracking dynamic operations.
        allowed_extensions: Trace allowed extensions metadata lists.
    """

    raw_score: float | None = None
    normalized_score: float | None = None
    justification: str | None = None

    level_breakdown: dict[str, Any] | None = None
    extensions: dict[str, Any] | None = None
    evaluated_atoms: dict[str, bool | str] | None = None
    xai_log: dict[str, Any] | None = None
    allowed_extensions: list[str] | None = None

