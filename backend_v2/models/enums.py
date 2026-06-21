"""Enums for V2 Backend.
Strict definition of allowed types to enforce the No-String Mandate.
"""

from enum import Enum, IntEnum
from typing import Annotated

from pydantic import Field


class EvaluationMandate(str, Enum):
    """Architectural Nollahypoteesi mandate attached to all strict evaluations."""

    FAIL_FAST_NO_EVIDENCE = (
        " ENFORCEMENT: Evaluate as FALSE immediately unless explicit, documented evidence is provided."
    )


class EvaluationRunCount(int, Enum):
    """Määrittää suorituskertojen määrän TDA-matriisiarvioinneille."""

    STANDARD = 1
    ENSEMBLE = 3


class BlockDataType(str, Enum):
    """Data types allowed for PromptBlock extracted values.
    Accepts core extraction types, plus valid legacy structural types.
    """

    FLOAT = "float"
    INT = "int"
    STRING = "string"
    INSTRUCTION = "instruction"
    PANEL = "panel"
    COMPLIANCE = "compliance"
    QUESTION = "question"
    CRITERIA = "criteria"


class PromptBlockCategory(str, Enum):
    """Strictly defined categories for PromptBlocks to guarantee Fail-Fast parity with Frontend."""

    MATRIX = "matrix"
    AGENT_ROLE = "agent_role"
    TASK_DEFINITION = "task_definition"
    SYSTEM_RULE = "system_rule"
    PROTOCOL = "protocol"
    RUNTIME_VARIABLES = "runtime_variables"
    EXECUTION_PERSONA = "execution_persona"


class ComponentType(str, Enum):
    """Component types allowed for SDUI Frontend Hint mapping."""

    SLIDER = "slider"
    TEXT_INPUT = "text_input"
    DROPDOWN = "dropdown"
    CHECKBOX = "checkbox"
    HIDDEN = "hidden"


class XaiExtensionType(str, Enum):
    """Supported XAI Output Extensions for global visibility."""

    CITATION = "citation"
    JUSTIFICATION = "justification"
    FALSIFICATION = "falsification"
    THEORY_LINK = "theory_link"
    RISK_FLAG = "risk_flag"
    COACHING = "coaching"
    MISSING_CONTEXT = "missing_context"
    REMEDIATION_STEPS = "remediation_steps"
    EMOTIONAL_SENTIMENT = "emotional_sentiment"
    CONFIDENCE = "confidence"
    SOURCE_ID = "source_id"
    CONTEXTUAL_OVERRIDE = "contextual_override"
    VARIANCE_VALIDATION = "variance_validation"


class XaiExtensionScope(str, Enum):
    """Scope classification for XAI Extensions.

    Attributes:
        BLOCK: Extensions computed at the matrix/block level by the LLM.
        WORKFLOW: Global extensions computed by deterministic engines at the workflow level.
    """

    BLOCK = "block"
    WORKFLOW = "workflow"


XAI_EXTENSION_SCOPE: dict[XaiExtensionType, XaiExtensionScope] = {
    XaiExtensionType.CITATION: XaiExtensionScope.BLOCK,
    XaiExtensionType.JUSTIFICATION: XaiExtensionScope.BLOCK,
    XaiExtensionType.FALSIFICATION: XaiExtensionScope.BLOCK,
    XaiExtensionType.THEORY_LINK: XaiExtensionScope.BLOCK,
    XaiExtensionType.RISK_FLAG: XaiExtensionScope.BLOCK,
    XaiExtensionType.COACHING: XaiExtensionScope.BLOCK,
    XaiExtensionType.MISSING_CONTEXT: XaiExtensionScope.BLOCK,
    XaiExtensionType.REMEDIATION_STEPS: XaiExtensionScope.BLOCK,
    XaiExtensionType.EMOTIONAL_SENTIMENT: XaiExtensionScope.BLOCK,
    XaiExtensionType.CONFIDENCE: XaiExtensionScope.BLOCK,
    XaiExtensionType.SOURCE_ID: XaiExtensionScope.BLOCK,
    XaiExtensionType.CONTEXTUAL_OVERRIDE: XaiExtensionScope.BLOCK,
    XaiExtensionType.VARIANCE_VALIDATION: XaiExtensionScope.WORKFLOW,
}


class SelfHealingThresholdRatio(float, Enum):
    """Semantic Self-Healing strictness ratios for LLM Evaluation.
    Defines what top percentage of a numerical scale triggers mandatory evidence constraints.
    """

    STRICT = 0.75
    LENIENT = 0.50
    NONE = 0.00


class WaterfallThreshold(float, Enum):
    """Guttman Waterfall mathematical passing threshold.
    Defines the hit rate percentage required to pass a scale level.
    """

    STRICT = 0.70  # Requires ~70% consensus (Tiukka 85)
    STANDARD = 0.40  # Requires ~40% consensus (Tasapainoinen 50)
    LENIENT = 0.15  # Requires ~15% consensus (Salliva 15)


class CognitiveFlowThreshold(float, Enum):
    """Progressive Dampening thresholds for cognitive flow degradation."""

    OPTIMAL = 1.00
    ACCEPTABLE = 0.70
    SIGNIFICANT_DROP_DIFF = 0.50


class CognitiveFlowStatus(str, Enum):
    """Logging texts for XAI justification of cognitive dampening."""

    OPTIMAL = "Hits flowed completely through"
    ACCEPTABLE = "Hits were dampened according to the flow"
    WEAK = "Cognitive flow degrades significantly"


class ScoringCalibrationThresholds(float, Enum):
    """Thresholds for Benefit of the Doubt leniency and Double Jeopardy caps."""

    DINA_FLOOR = 0.30
    PENALTY_CAP = 0.25
    BENEFIT_OF_DOUBT_BONUS = 0.15


class EvaluationCategory(str, Enum):
    """Broad categorization for component classification."""

    MATHEMATICAL = "MATHEMATICAL"
    SEMANTIC = "SEMANTIC"
    LINGUISTIC = "LINGUISTIC"
    LOGICAL = "LOGICAL"
    BEHAVIORAL = "BEHAVIORAL"
    UNKNOWN = "UNKNOWN"


class ExecutionStatus(str, Enum):
    """Execution lifecycle status."""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class VirtualSystemStepID(str, Enum):
    """Reserved IDs for Virtual System Steps generated dynamically by the DAG Engine."""

    SCORING_RESULT = "scoring_result"
    HAS_WARNING = "has_warning"
    SYNTHESIZED_MARKDOWN = "synthesized_markdown"
    STEP_METADATA = "_step_metadata"


class HistoricalContextMode(str, Enum):
    """Modes for fetching historical execution data during synthesis."""

    DISABLED = "DISABLED"
    SLIDING_WINDOW_3 = "SLIDING_WINDOW_3"


class SystemLocale(str, Enum):
    """Supported system locales."""

    EN = "en"
    FI = "fi"


class LLMCachingStrategy(str, Enum):
    """Supported caching strategies."""

    PROMPT_CACHING = "prompt_caching"
    EPHEMERAL = "ephemeral"
    ANTHROPIC_EPHEMERAL = "anthropic_ephemeral"
    GEMINI_NATIVE = "gemini_native"
    NONE = "none"


class LLMProviderName(str, Enum):
    """Supported LLM provider names."""

    VERTEX_AI = "vertex_ai"
    GOOGLE = "google"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    MOCK = "mock_llm_99"


class PromptCacheStatus(str, Enum):
    """Status states for prompt caching in shared ledger."""

    CREATING = "CREATING"
    CREATED = "CREATED"
    FAILED = "FAILED"


class SystemConcurrency(int, Enum):
    """Global concurrency limits for DAG Execution. Optimized for Context Caching (V3)."""

    MAX_CONCURRENT_WORKFLOWS = 10
    MAX_CONCURRENT_LLM_STEPS = 2
    LLM_MAX_RETRIES = 2
    LLM_RETRY_MULTIPLIER = 2
    LLM_RETRY_MIN_SECONDS = 2
    LLM_RETRY_MAX_SECONDS = 60
    LLM_RETRY_JITTER_INITIAL_SECONDS = 2
    LLM_RETRY_JITTER_EXP_BASE = 2
    LLM_MAX_CHUNK_SIZE = 10
    MATRIX_SAMPLING_LIMIT = 0
    LLM_DEFAULT_TIMEOUT_SECONDS = 600
    RATE_LIMIT_COOLDOWN_SECONDS = 10
    SEMAPHORE_LOW_RPM_THRESHOLD = 20
    SEMAPHORE_LOW_RPM_LIMIT = 2
    SEMAPHORE_MAX_CONCURRENCY = 10
    SEMAPHORE_RPM_DIVISOR = 10
    MAX_SAFE_TOKENS = 1000000
    SCHEMA_MAX_LOCALIZED_ANCHORS = 15
    SCHEMA_MAX_EVALUATIONS = 10
    SCHEMA_MAX_CHUNK_RECORDS = 15
    CONTEXT_CACHE_LOCK_TTL_SECONDS = 300
    CONTEXT_CACHE_PASSIVE_TTL_SECONDS = 3600
    CONTEXT_CACHE_LOCK_POLL_INTERVAL_MS = 500
    CONTEXT_CACHE_LOCK_WAIT_LIMIT_SECONDS = 20
    # Note: 2048 is the absolute minimum for Gemini 2.0/2.5.
    # IMPORTANT: Must be raised to 4096 when migrating to Gemini 3.0/3.1+.
    CONTEXT_CACHE_MINIMUM_TOKEN_LIMIT = 2048
    PACING_DELAY_VERTEX_SECONDS = 12
    PACING_DELAY_OPENAI_SECONDS = 1
    PACING_DELAY_MOCK_SECONDS = 0
    REDIS_CONNECTION_TIMEOUT_SECONDS = 10
    # Epic 80: Content Cache feature flag. When enabled (1), the base_system_prompt
    # is moved from 'system' role to 'user' role, allowing Vertex AI to cache ONLY
    # the PDF document for 100% cache hit rate across matrices. HOWEVER, this causes
    # ~29% evaluation quality degradation due to Role Degradation (the LLM treats
    # user-role instructions less strictly than system-role). Default: DISABLED (0).
    CONTENT_CACHE_ENABLED = 0


# --- Restored V1 Enums ---


class FuzzThresholdConfig(float, Enum):
    """Kielityyppikohtaiset kynnysarvot fuzzy-mätsäykseen."""

    AGGLUTINATIVE = 85.0  # Suomi, unkari, turkki
    ANALYTIC = 92.0  # Englanti, ruotsi, saksa, ranska, espanja
    ISOLATING = 98.0  # Kiina, japani, korea
    DEFAULT = 90.0  # Turvallinen kompromissi tuntemattomille kielille


def get_lexical_fuzz_threshold(locale: str | None) -> float:
    """Ratkaisee oikean kynnyksen lokaalin perusteella.

    Args:
        locale: The system locale string (e.g., 'fi', 'en').

    Returns:
        float: The fuzzy matching threshold percentage.
    """
    if not locale:
        return FuzzThresholdConfig.DEFAULT.value

    match locale.lower():
        case "fi" | "hu" | "tr":
            return FuzzThresholdConfig.AGGLUTINATIVE.value
        case "en" | "sv" | "de" | "fr" | "es":
            return FuzzThresholdConfig.ANALYTIC.value
        case "zh" | "ja" | "ko":
            return FuzzThresholdConfig.ISOLATING.value
        case _:
            return FuzzThresholdConfig.DEFAULT.value


class StrictnessAnchor(IntEnum):
    """UI:n kiinteät Strictness-tasot. Määrittää pehmeyden (forgiveness) ankkuripisteet."""

    NONE = 0
    RELAXED = 30
    STANDARD = 50
    BALANCED = 70
    STRICT = 85
    ABSOLUTE = 100


class RiskLevel(str, Enum):
    """Tri-level risk classification for security and compliance evaluations."""

    LOW = "RISK_LOW"
    MEDIUM = "RISK_MEDIUM"
    HIGH = "RISK_HIGH"


class SimulationType(str, Enum):
    """Classifies the type of adversarial simulation applied during security analysis."""

    PASSIVE = "SIM_PASSIVE"
    ACTIVE = "SIM_ACTIVE"
    MALICIOUS = "SIM_MALICIOUS"


class BloomLevel(str, Enum):
    """Bloom's Taxonomy cognitive complexity levels for learning objective classification."""

    REMEMBERING = "BLOOM_REMEMBERING"
    UNDERSTANDING = "BLOOM_UNDERSTANDING"
    APPLYING = "BLOOM_APPLYING"
    ANALYZING = "BLOOM_ANALYZING"
    EVALUATING = "BLOOM_EVALUATING"
    CREATING = "BLOOM_CREATING"


class StrategicDepth(str, Enum):
    """Graduated scale for evaluating strategic thinking depth in user responses."""

    LOW = "STRAT_LOW"
    MEDIUM = "STRAT_MEDIUM"
    HIGH = "STRAT_HIGH"
    VISIONARY = "STRAT_VISIONARY"


class FidelityLevel(str, Enum):
    """Source fidelity classification for evidence quality assessment."""

    WEAK = "FIDELITY_WEAK"
    UNCERTAIN = "FIDELITY_UNCERTAIN"
    HIGH = "FIDELITY_HIGH"


class PlausibilityLevel(str, Enum):
    """Plausibility classification for abductive reasoning conclusions."""

    IMPOSSIBLE = "IMPOSSIBLE"
    PLAUSIBLE = "PLAUSIBLE"
    HIGH = "HIGH"


class AbductiveConclusion(str, Enum):
    """Abductive inference outcome classification for causal reasoning evaluations."""

    POST_HOC = "POST_HOC"
    UNCERTAIN = "UNCERTAIN"
    GENUINE = "GENUINE"


class AuthenticityLevel(str, Enum):
    """Authenticity classification for performativity detection in user discourse."""

    ORGANIC = "AUTH_ORGANIC"
    PERFORMATIVE = "AUTH_PERFORMATIVE"
    UNKNOWN = "AUTH_UNKNOWN"


class RoleClassification(str, Enum):
    """User agency classification from passive observer to active architect."""

    PASSENGER = "ROLE_PASSENGER"
    NAVIGATOR = "ROLE_NAVIGATOR"
    DRIVER = "ROLE_DRIVER"
    ARCHITECT = "ROLE_ARCHITECT"


class InteractionStrategy(str, Enum):
    """Prompt engineering strategy classification for interaction quality assessment."""

    ZERO_SHOT = "STRATEGY_ZERO_SHOT"
    FEW_SHOT = "STRATEGY_FEW_SHOT"
    CHAIN_OF_THOUGHT = "STRATEGY_CHAIN_OF_THOUGHT"


class ScoringPenalty(str, Enum):
    """Penalty types applied during deterministic score calibration."""

    SECURITY_THREAT = "PENALTY_SECURITY_THREAT"
    POST_HOC = "PENALTY_POST_HOC"


class VerificationResult(str, Enum):
    """Fact-check verification outcome for falsification agent evaluations."""

    VERIFIED = "RESULT_VERIFIED"
    DEBUNKED = "RESULT_DEBUNKED"
    UNVERIFIED = "RESULT_UNVERIFIED"


class EthicalSeverity(str, Enum):
    """Ethical concern severity levels for overseer agent flagging."""

    NONE = "SEVERITY_NONE"
    WARNING = "SEVERITY_WARNING"
    CRITICAL = "SEVERITY_CRITICAL"


class HelpTextKey(str, Enum):
    BLOOM = "helpBloom"
    TOULMIN = "helpToulmin"
    STRATEGIC_DEPTH = "helpStrategicDepth"
    FIDELITY = "helpFidelity"
    ABDUCTIVE = "helpAbductive"
    CAUSAL = "helpCausal"
    PLAUSIBILITY = "plausibility_desc"  # Mapped to desc in client
    AUTHENTICITY = "helpAuthenticity"
    PERFORMATIVITY = "helpPerformativity"
    CONTROL_RATIO = "helpControlRatio"
    WORD_COUNT = "helpWordCount"
    FACT_CHECK = "helpFactCheck"
    ARCHIVIST = "helpArchivist"


class TitleKey(str, Enum):
    SECURITY = "TITLE_SECURITY"
    USAGE = "TITLE_USAGE"
    PROFILER = "TITLE_PROFILER"
    INTERACTION = "TITLE_INTERACTION"
    COACH = "TITLE_COACH"
    ARCHIVIST = "TITLE_ARCHIVIST"
    LOGICIAN = "TITLE_LOGICIAN"
    FALSIFIER = "TITLE_FALSIFIER"
    CAUSAL = "TITLE_CAUSAL"
    PERFORMATIVITY = "TITLE_PERFORMATIVITY"
    OVERSEER = "TITLE_OVERSEER"
    CONTEXT = "TITLE_CONTEXT"
    TIMELINE = "Process Timeline"  # Key in l10n
    HYPOTHESES = "Analyst Hypotheses"  # Key in l10n"


class LabelKey(str, Enum):
    """Strict L10N label keys for No-String Mandate compliance across UI boundaries."""

    # Agents
    AGENT_GUARD = "AGENT_GUARD"
    AGENT_ANALYST = "AGENT_ANALYST"
    AGENT_INTERACTION = "AGENT_INTERACTION"
    AGENT_PROFILER = "AGENT_PROFILER"
    AGENT_LOGICIAN = "AGENT_LOGICIAN"
    AGENT_FALSIFIER = "AGENT_FALSIFIER"
    AGENT_CAUSAL = "AGENT_CAUSAL"
    AGENT_DETECTOR = "AGENT_DETECTOR"
    AGENT_JUDGE = "AGENT_JUDGE"
    AGENT_COGNITIVE_JUDGE = "AGENT_COGNITIVE_JUDGE"
    AGENT_COACH = "AGENT_COACH"
    AGENT_REPORTER = "AGENT_REPORTER"

    # Analysis Titles (Dynamic)
    ANALYSIS_RESULT = "ANALYSIS_RESULT"
    COGNITIVE_ASSESSMENT = "COGNITIVE_ASSESSMENT"

    # Security
    SEC_THREAT_DETECTED = "SEC_THREAT_DETECTED"
    SEC_THREAT_NONE = "SEC_THREAT_NONE"
    SEC_ANONYMIZED = "SEC_ANONYMIZED"
    SEC_NOT_ANONYMIZED = "SEC_NOT_ANONYMIZED"

    # Profiler
    BIAS_DETECTED = "BIAS_DETECTED"
    BIAS_NONE = "BIAS_NONE"
    GAP_DETECTED = "GAP_DETECTED"
    GAP_NONE = "GAP_NONE"

    # Coach
    FOCUS_AREAS = "FOCUS_AREAS"
    ACTIONABLE_STEPS = "ACTIONABLE_STEPS"
    REFERENCES = "REFERENCES"

    # General / Table
    ID = "LBL_ID"
    CLAIM = "LBL_CLAIM"
    VERIFIED = "LBL_VERIFIED"
    AI_REASONING = "LBL_AI_REASONING"
    EVIDENCE_FOUND = "LBL_EVIDENCE_FOUND"

    # Fact Check / Overseer
    VERIFIED_LABEL = "VERIFIED_LABEL"
    DEBUNKED_LABEL = "DEBUNKED_LABEL"
    CRITICAL_LABEL = "CRITICAL_LABEL"
    WARNING_LABEL = "WARNING_LABEL"
    UNCERTAIN_LABEL = "UNCERTAIN_LABEL"


class ReferenceTitle(str, Enum):
    """Strict Enum for UI Reference Strings to prevent hardcoded L10N (No String Mandate)."""

    WEB_SEARCH = "REF_WEB_SEARCH"
    INTERNAL_DOCUMENT = "REF_INTERNAL_DOCUMENT"
    EXPERT_QUOTATION = "REF_EXPERT_QUOTATION"
    PREVIOUS_REPORT = "REF_PREVIOUS_REPORT"


class ScoringStrategy(str, Enum):
    """Selects the mathematical engine used to calculate final matrix scores."""

    WATERFALL = "WATERFALL"
    DAMPENING = "DAMPENING"
    AVERAGE = "AVERAGE"
    WEIGHTED_AVERAGE = "WEIGHTED_AVERAGE"
    PURE_MATH = "PURE_MATH"


# --- Lax Type Aliases (Pydantic V2) ---
LaxLLMCachingStrategy = Annotated[LLMCachingStrategy, Field(strict=False)]
LaxLLMProviderName = Annotated[LLMProviderName, Field(strict=False)]
LaxXaiExtensionType = Annotated[XaiExtensionType, Field(strict=False)]
LaxAuthenticityLevel = Annotated[AuthenticityLevel, Field(strict=False)]
LaxBloomLevel = Annotated[BloomLevel, Field(strict=False)]
LaxStrategicDepth = Annotated[StrategicDepth, Field(strict=False)]
LaxVerificationResult = Annotated[VerificationResult, Field(strict=False)]
LaxEthicalSeverity = Annotated[EthicalSeverity, Field(strict=False)]
LaxExecutionStatus = Annotated[ExecutionStatus, Field(strict=False)]
LaxBlockDataType = Annotated[BlockDataType, Field(strict=False)]
LaxComponentType = Annotated[ComponentType, Field(strict=False)]
LaxHistoricalContextMode = Annotated[HistoricalContextMode, Field(strict=False)]
LaxScoringStrategy = Annotated[ScoringStrategy, Field(strict=False)]
LaxVirtualSystemStepID = Annotated[VirtualSystemStepID, Field(strict=False)]
LaxPromptBlockCategory = Annotated[PromptBlockCategory, Field(strict=False)]
LaxEvaluationRunCount = Annotated[EvaluationRunCount, Field(strict=False)]
LaxPlausibilityLevel = Annotated[PlausibilityLevel, Field(strict=False)]
LaxAbductiveConclusion = Annotated[AbductiveConclusion, Field(strict=False)]
LaxFidelityLevel = Annotated[FidelityLevel, Field(strict=False)]
