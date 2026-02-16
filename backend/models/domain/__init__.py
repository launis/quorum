"""Domain Models Package.

This package contains the strict Pydantic models for all agent outputs and domain entities.
It replaces the monolithic `domain.py`.
"""

# 0. Base
from backend.models.domain.analyst import (
    AnalystOutput,
    Hypothesis,
    SearchResult,
    SearchResultItem,
)
from backend.models.domain.archivist import ArchiveCase, ArchivistOutput, ArchivistOutputDTO
from backend.models.domain.base import Metadata, ReasoningTrace, UsageRecord
from backend.models.domain.causal import (
    CausalAnalysis,
    CausalAnalysisData,
    CausalOutput,
    CounterfactualTest,
)
from backend.models.domain.coach import (
    BibliographyItem,
    BibliographyResult,
    CoachingPlan,
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
from backend.models.domain.interaction import InteractionAnalysis
from backend.models.domain.judge import (
    DimensionResultItem,
    JudgeOutput,
    JudgeScoreCard,
    ScoringResult,
)
from backend.models.domain.logician import (
    CognitiveLevel,
    LogicianData,
    LogicianOutput,
    ToulminComponent,
    WaltonScheme,
)
from backend.models.domain.overseer import (
    EthicalObservation,
    FactCheckRFI,
    OverseerData,
    OverseerOutput,
)
from backend.models.domain.panel import PanelOutput, PanelOutputDTO
from backend.models.domain.performativity import (
    LinguisticsResult,
    PerformativePattern,
    PerformativityAnalysis,
    PerformativityHeuristic,
    PerformativityOutput,
    PreMortemAnalysis,
)
from backend.models.domain.profiler import ProfilerAnalysis, TextMetrics
from backend.models.domain.retrieval import ContextData, Precedent
from backend.models.domain.xai import (
    ReportContext,
    ReportResult,
    XAIOutput,
    XAIScoreItem,
)

# --- REGISTRY ---
DOMAIN_REGISTRY = {
    "GuardOutput": GuardOutput,
    "AnalystOutput": AnalystOutput,
    "LogicianOutput": LogicianOutput,
    "PanelOutput": PanelOutput,
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
    "SearchResult": SearchResult,
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
    "AnalystOutput",
    "Hypothesis",
    "SearchResult",
    "SearchResultItem",
    "ContextData",
    "Precedent",
    "ProfilerAnalysis",
    "TextMetrics",
    "LogicianOutput",
    "LogicianData",
    "ToulminComponent",
    "WaltonScheme",
    "CognitiveLevel",
    "FalsifierOutput",
    "FalsifierData",
    "WaltonStressTest",
    "ReasoningFidelity",
    "CausalOutput",
    "CausalAnalysis",
    "CausalAnalysisData",
    "CounterfactualTest",
    "PerformativityOutput",
    "PerformativityAnalysis",
    "PerformativityHeuristic",
    "PreMortemAnalysis",
    "LinguisticsResult",
    "PerformativePattern",
    "OverseerOutput",
    "OverseerData",
    "FactCheckRFI",
    "EthicalObservation",
    "InteractionAnalysis",
    "ArchivistOutput",
    "ArchivistOutputDTO",
    "ArchiveCase",
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
    "PanelOutput",
    "PanelOutputDTO",
    "DOMAIN_REGISTRY",
]
