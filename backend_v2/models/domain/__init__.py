"""Domain Models Package.

This package contains the strict Pydantic models for all agent outputs and domain entities.
It replaces the monolithic `domain.py`.
"""

# 0. Base
from backend_v2.models.domain.analyst import (
    AnalystDTO,
    AnalystInput,
    AnalystOutput,
    Hypothesis,
    SearchResult,
    SearchResultItem,
)
from backend_v2.models.domain.archivist import ArchiveCase, ArchivistInput, ArchivistOutput, ArchivistOutputDTO
from backend_v2.models.domain.base import Metadata, ReasoningTrace, UsageRecord
from backend_v2.models.domain.causal import (
    CausalAnalysis,
    CausalAnalysisData,
    CausalDTO,
    CausalInput,
    CausalOutput,
    CounterfactualTest,
)
from backend_v2.models.domain.coach import (
    BibliographyItem,
    BibliographyResult,
    CoachingPlan,
    CoachingPlanDTO,
    CoachInput,
)

# 1. Models moved to Workflow (for Evaluation/Validation)
from backend_v2.models.domain.evaluation import (
    EvaluationCriterion,
    EvaluationMatrixConfig,
    EvaluationResult,
    ValidationResult,
)
from backend_v2.models.domain.falsifier import (
    FalsifierData,
    FalsifierDTO,
    FalsifierInput,
    FalsifierOutput,
    ReasoningFidelity,
    WaltonStressTest,
)
from backend_v2.models.domain.interaction import InteractionAnalysis, InteractionAnalysisDTO, InteractionInput
from backend_v2.models.domain.judge import (
    DimensionResultItem,
    JudgeDTO,
    JudgeInput,
    JudgeOutput,
    JudgeScoreCard,
    ScoringResult,
)
from backend_v2.models.domain.logician import (
    CognitiveLevel,
    LogicianData,
    LogicianInput,
    LogicianOutput,
    LogicianOutputDTO,
    ToulminComponent,
    WaltonScheme,
)
from backend_v2.models.domain.mechanical_anchors import MechanicalAnchorsPayload
from backend_v2.models.domain.overseer import (
    EthicalObservation,
    FactCheckRFI,
    OverseerData,
    OverseerDTO,
    OverseerInput,
    OverseerOutput,
)
from backend_v2.models.domain.performativity import (
    LinguisticsResult,
    PerformativePattern,
    PerformativityAnalysis,
    PerformativityDTO,
    PerformativityHeuristic,
    PerformativityInput,
    PerformativityOutput,
    PreMortemAnalysis,
)
from backend_v2.models.domain.profiler import ProfilerDTO, ProfilerInput, ProfilerOutput, TextMetrics
from backend_v2.models.domain.prompt_blocks import (
    AnyPromptBlock,
    MatrixPromptBlock,
    PersonaPromptBlock,
    PromptBlock,
    PromptBlockAdapter,
    PromptBlockBase,
    ProtocolPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.domain.retrieval import RetrievalDTO, RetrievalInput, RetrievalOutput, RetrievedFact

# 2. Agent Modules
from backend_v2.models.domain.security import (
    InputProcessingOutputDTO,
    SanitizationResultDTO,
    SecurityCheck,
    SecurityPayloadDTO,
)
from backend_v2.models.domain.xai import (
    ReportResult,
    XAIOutput,
    XAIReporterInput,
    XAIScoreItem,
)

# --- REGISTRY ---
DOMAIN_REGISTRY = {
    "InputProcessingOutputDTO": InputProcessingOutputDTO,
    "AnalystOutput": AnalystOutput,
    "LogicianOutput": LogicianOutput,
    "JudgeInput": JudgeInput,
    "JudgeOutput": JudgeOutput,
    "XAIOutput": XAIOutput,
    "ArchivistOutput": ArchivistOutput,
    "CoachingPlan": CoachingPlan,
    "ProfilerDTO": ProfilerDTO,
    "ProfilerOutput": ProfilerOutput,
    "InteractionAnalysis": InteractionAnalysis,
    # Hook Results
    "SanitizationResultDTO": SanitizationResultDTO,
    "LinguisticsResult": LinguisticsResult,
    "BibliographyResult": BibliographyResult,
    "TextMetrics": TextMetrics,
    "ScoringResult": ScoringResult,
    "ReportResult": ReportResult,
    "ValidationResult": ValidationResult,
    "SearchResult": SearchResult,
    # Inputs
    "RetrievalInput": RetrievalInput,
    "RetrievalOutput": RetrievalOutput,
    "InteractionInput": InteractionInput,
    "CoachInput": CoachInput,
    "XAIReporterInput": XAIReporterInput,
    # Prompt Blocks
    "AnyPromptBlock": AnyPromptBlock,
}

__all__ = [
    "Metadata",
    "ReasoningTrace",
    "UsageRecord",
    "EvaluationCriterion",
    "EvaluationMatrixConfig",
    "EvaluationResult",
    "ValidationResult",
    "InputProcessingOutputDTO",
    "SecurityCheck",
    "SecurityPayloadDTO",
    "SanitizationResultDTO",
    "AnalystInput",
    "AnalystOutput",
    "AnalystDTO",
    "Hypothesis",
    "SearchResult",
    "SearchResultItem",
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
    "MechanicalAnchorsPayload",
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
    "ReportResult",
    "DOMAIN_REGISTRY",
    "RetrievalInput",
    "RetrievalOutput",
    "RetrievedFact",
    "RetrievalDTO",
    "InteractionInput",
    "CoachInput",
    "XAIReporterInput",
    "AnyPromptBlock",
    "PromptBlock",
    "PromptBlockAdapter",
    "PromptBlockBase",
    "MatrixPromptBlock",
    "SystemRulePromptBlock",
    "PersonaPromptBlock",
    "ProtocolPromptBlock",
]
