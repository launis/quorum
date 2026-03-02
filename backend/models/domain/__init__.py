"""Domain Models Package.

This package contains the strict Pydantic models for all agent outputs and domain entities.
It replaces the monolithic `domain.py`.
"""

# 0. Base
from backend.models.domain.analyst import (
    AnalystDTO,
    AnalystInput,
    AnalystOutput,
    Hypothesis,
    SearchResult,
    SearchResultItem,
)
from backend.models.domain.archivist import ArchiveCase, ArchivistInput, ArchivistOutput, ArchivistOutputDTO
from backend.models.domain.base import Metadata, ReasoningTrace, UsageRecord
from backend.models.domain.causal import (
    CausalAnalysis,
    CausalAnalysisData,
    CausalDTO,
    CausalInput,
    CausalOutput,
    CounterfactualTest,
)
from backend.models.domain.coach import (
    BibliographyItem,
    BibliographyResult,
    CoachingPlan,
    CoachingPlanDTO,
    CoachInput,
)

# 1. Models moved to Workflow (for Evaluation/Validation)
from backend.models.domain.evaluation import (
    EvaluationCriterion,
    EvaluationMatrixConfig,
    EvaluationResult,
    ValidationResult,
)
from backend.models.domain.falsifier import (
    FalsifierData,
    FalsifierDTO,
    FalsifierInput,
    FalsifierOutput,
    ReasoningFidelity,
    WaltonStressTest,
)

# 2. Agent Modules
from backend.models.domain.guard import (
    GuardDTO,
    GuardInput,
    GuardOutput,
    SanitizationResult,
    SecurityCheck,
    TaintedDataContent,
)
from backend.models.domain.interaction import InteractionAnalysis, InteractionAnalysisDTO, InteractionInput
from backend.models.domain.judge import (
    DimensionResultItem,
    JudgeDTO,
    JudgeInput,
    JudgeOutput,
    JudgeScoreCard,
    ScoringResult,
)
from backend.models.domain.logician import (
    CognitiveLevel,
    LogicianData,
    LogicianInput,
    LogicianOutput,
    LogicianOutputDTO,
    ToulminComponent,
    WaltonScheme,
)
from backend.models.domain.overseer import (
    EthicalObservation,
    FactCheckRFI,
    OverseerData,
    OverseerDTO,
    OverseerInput,
    OverseerOutput,
)
from backend.models.domain.panel import PanelInput, PanelOutput, PanelOutputDTO
from backend.models.domain.performativity import (
    LinguisticsResult,
    PerformativePattern,
    PerformativityAnalysis,
    PerformativityDTO,
    PerformativityHeuristic,
    PerformativityInput,
    PerformativityOutput,
    PreMortemAnalysis,
)
from backend.models.domain.profiler import ProfilerDTO, ProfilerInput, ProfilerOutput, TextMetrics
from backend.models.domain.retrieval import ContextData, ContextDataDTO, Precedent, RetrievalInput
from backend.models.domain.xai import (
    ReportResult,
    XAIOutput,
    XAIOutputDTO,
    XAIReporterInput,
    XAIScoreItem,
)
from backend.models.dtos.pdf_context import ReportContext

# --- REGISTRY ---
DOMAIN_REGISTRY = {
    "GuardOutput": GuardOutput,
    "AnalystOutput": AnalystOutput,
    "LogicianOutput": LogicianOutput,
    "PanelOutput": PanelOutput,
    "JudgeInput": JudgeInput,
    "JudgeOutput": JudgeOutput,
    "XAIOutput": XAIOutput,
    "ArchivistOutput": ArchivistOutput,
    "CoachingPlan": CoachingPlan,
    "ProfilerDTO": ProfilerDTO,
    "ProfilerOutput": ProfilerOutput,
    "InteractionAnalysis": InteractionAnalysis,
    "ContextData": ContextData,
    # Hook Results
    "SanitizationResult": SanitizationResult,
    "LinguisticsResult": LinguisticsResult,
    "BibliographyResult": BibliographyResult,
    "TextMetrics": TextMetrics,
    "ScoringResult": ScoringResult,
    "ReportResult": ReportResult,
    "ValidationResult": ValidationResult,
    "SearchResult": SearchResult,
    # Inputs
    "RetrievalInput": RetrievalInput,
    "InteractionInput": InteractionInput,
    "CoachInput": CoachInput,
    "XAIReporterInput": XAIReporterInput,
}

__all__ = [
    "Metadata",
    "ReasoningTrace",
    "UsageRecord",
    "EvaluationCriterion",
    "EvaluationMatrixConfig",
    "EvaluationResult",
    "ValidationResult",
    "GuardInput",
    "GuardOutput",
    "SecurityCheck",
    "TaintedDataContent",
    "SanitizationResult",
    "AnalystInput",
    "AnalystOutput",
    "AnalystDTO",
    "Hypothesis",
    "SearchResult",
    "SearchResultItem",
    "ContextData",
    "Precedent",
    "ProfilerInput",
    "ProfilerDTO",
    "ProfilerOutput",
    "TextMetrics",
    "LogicianInput",
    "LogicianOutput",
    "LogicianOutputDTO",
    "LogicianData",
    "ToulminComponent",
    "WaltonScheme",
    "CognitiveLevel",
    "FalsifierInput",
    "FalsifierOutput",
    "FalsifierDTO",
    "FalsifierData",
    "WaltonStressTest",
    "ReasoningFidelity",
    "CausalInput",
    "CausalOutput",
    "CausalDTO",
    "CausalAnalysis",
    "CausalAnalysisData",
    "CounterfactualTest",
    "PerformativityInput",
    "PerformativityOutput",
    "PerformativityDTO",
    "PerformativityAnalysis",
    "PerformativityHeuristic",
    "PreMortemAnalysis",
    "LinguisticsResult",
    "PerformativePattern",
    "OverseerInput",
    "OverseerOutput",
    "OverseerDTO",
    "OverseerData",
    "FactCheckRFI",
    "EthicalObservation",
    "InteractionAnalysis",
    "InteractionAnalysisDTO",
    "ArchivistInput",
    "ArchivistOutput",
    "ArchivistOutputDTO",
    "ArchiveCase",
    "JudgeInput",
    "JudgeOutput",
    "JudgeDTO",
    "JudgeScoreCard",
    "DimensionResultItem",
    "ScoringResult",
    "CoachingPlan",
    "CoachingPlanDTO",
    "CoachInput",
    "BibliographyResult",
    "BibliographyItem",
    "XAIOutput",
    "XAIScoreItem",
    "ReportContext",
    "ReportResult",
    "PanelInput",
    "PanelOutput",
    "PanelOutputDTO",
    "DOMAIN_REGISTRY",
    "RetrievalInput",
    "InteractionInput",
    "CoachInput",
    "XAIReporterInput",
]
