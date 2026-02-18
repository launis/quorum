"""Domain Models Package.

This package contains the strict Pydantic models for all agent outputs and domain entities.
It replaces the monolithic `domain.py`.
"""

# 0. Base
from backend.models.domain.analyst import (
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
    CausalInput,
    CausalOutput,
    CounterfactualTest,
)
from backend.models.domain.coach import (
    BibliographyItem,
    BibliographyResult,
    CoachingPlan,
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
    FalsifierInput,
    FalsifierOutput,
    ReasoningFidelity,
    WaltonStressTest,
)

# 2. Agent Modules
from backend.models.domain.guard import (
    GuardInput,
    GuardOutput,
    SanitizationResult,
    SecurityCheck,
    TaintedDataContent,
)
from backend.models.domain.interaction import InteractionAnalysis, InteractionInput
from backend.models.domain.judge import (
    DimensionResultItem,
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
    ToulminComponent,
    WaltonScheme,
)
from backend.models.domain.overseer import (
    EthicalObservation,
    FactCheckRFI,
    OverseerData,
    OverseerInput,
    OverseerOutput,
)
from backend.models.domain.panel import PanelInput, PanelOutput, PanelOutputDTO
from backend.models.domain.performativity import (
    LinguisticsResult,
    PerformativePattern,
    PerformativityAnalysis,
    PerformativityHeuristic,
    PerformativityInput,
    PerformativityOutput,
    PreMortemAnalysis,
)
from backend.models.domain.profiler import ProfilerAnalysis, ProfilerInput, TextMetrics
from backend.models.domain.retrieval import ContextData, Precedent, RetrievalInput
from backend.models.domain.xai import (
    ReportContext,
    ReportResult,
    XAIOutput,
    XAIScoreItem,
    XAIReporterInput,
)

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
    "ProfilerAnalysis": ProfilerAnalysis,
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
    "Hypothesis",
    "SearchResult",
    "SearchResultItem",
    "ContextData",
    "Precedent",
    "ProfilerInput",
    "ProfilerAnalysis",
    "TextMetrics",
    "LogicianInput",
    "LogicianOutput",
    "LogicianData",
    "ToulminComponent",
    "WaltonScheme",
    "CognitiveLevel",
    "FalsifierInput",
    "FalsifierOutput",
    "FalsifierData",
    "WaltonStressTest",
    "ReasoningFidelity",
    "CausalInput",
    "CausalOutput",
    "CausalAnalysis",
    "CausalAnalysisData",
    "CounterfactualTest",
    "PerformativityInput",
    "PerformativityOutput",
    "PerformativityAnalysis",
    "PerformativityHeuristic",
    "PreMortemAnalysis",
    "LinguisticsResult",
    "PerformativePattern",
    "OverseerInput",
    "OverseerOutput",
    "OverseerData",
    "FactCheckRFI",
    "EthicalObservation",
    "InteractionAnalysis",
    "ArchivistInput",
    "ArchivistOutput",
    "ArchivistOutputDTO",
    "ArchiveCase",
    "JudgeInput",
    "JudgeOutput",
    "JudgeScoreCard",
    "DimensionResultItem",
    "ScoringResult",
    "CoachingPlan",
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

