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

    STRICT = 0.70    # Requires ~70% consensus (Tiukka 85)
    STANDARD = 0.40  # Requires ~40% consensus (Tasapainoinen 50)
    LENIENT = 0.15   # Requires ~15% consensus (Salliva 15)


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
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class HistoricalContextMode(str, Enum):
    """Modes for fetching historical execution data during synthesis."""

    DISABLED = "DISABLED"
    SLIDING_WINDOW_3 = "SLIDING_WINDOW_3"


class SystemConcurrency(int, Enum):
    """Global concurrency limits for DAG Execution to prevent API Rate Limits."""

    MAX_CONCURRENT_WORKFLOWS = 1
    MAX_CONCURRENT_LLM_STEPS = 2
    LLM_MAX_RETRIES = 8
    LLM_MAX_CHUNK_SIZE = 60
    MATRIX_SAMPLING_LIMIT = 25
    LLM_DEFAULT_TIMEOUT_SECONDS = 600
    RATE_LIMIT_COOLDOWN_SECONDS = 65
    MAX_SAFE_TOKENS = 1000000


# --- Restored V1 Enums ---


class StrictnessAnchor(IntEnum):
    """UI:n kiinteät Strictness-tasot. Määrittää pehmeyden (forgiveness) ankkuripisteet."""

    FLEXIBLE = 0
    LENIENT = 15
    BALANCED = 50
    STRICT = 85
    ABSOLUTE = 100


class RiskLevel(str, Enum):
    LOW = "RISK_LOW"
    MEDIUM = "RISK_MEDIUM"
    HIGH = "RISK_HIGH"


class SimulationType(str, Enum):
    PASSIVE = "SIM_PASSIVE"
    ACTIVE = "SIM_ACTIVE"
    MALICIOUS = "SIM_MALICIOUS"


class BloomLevel(str, Enum):
    REMEMBERING = "BLOOM_REMEMBERING"
    UNDERSTANDING = "BLOOM_UNDERSTANDING"
    APPLYING = "BLOOM_APPLYING"
    ANALYZING = "BLOOM_ANALYZING"
    EVALUATING = "BLOOM_EVALUATING"
    CREATING = "BLOOM_CREATING"


class StrategicDepth(str, Enum):
    LOW = "STRAT_LOW"
    MEDIUM = "STRAT_MEDIUM"
    HIGH = "STRAT_HIGH"
    VISIONARY = "STRAT_VISIONARY"


class FidelityLevel(str, Enum):
    WEAK = "FIDELITY_WEAK"
    UNCERTAIN = "FIDELITY_UNCERTAIN"
    HIGH = "FIDELITY_HIGH"


class PlausibilityLevel(str, Enum):
    IMPOSSIBLE = "IMPOSSIBLE"
    PLAUSIBLE = "PLAUSIBLE"
    HIGH = "HIGH"


class AbductiveConclusion(str, Enum):
    POST_HOC = "POST_HOC"
    UNCERTAIN = "UNCERTAIN"
    GENUINE = "GENUINE"


class AuthenticityLevel(str, Enum):
    ORGANIC = "AUTH_ORGANIC"
    PERFORMATIVE = "AUTH_PERFORMATIVE"
    UNKNOWN = "AUTH_UNKNOWN"


class RoleClassification(str, Enum):
    PASSENGER = "ROLE_PASSENGER"
    NAVIGATOR = "ROLE_NAVIGATOR"
    DRIVER = "ROLE_DRIVER"
    ARCHITECT = "ROLE_ARCHITECT"


class InteractionStrategy(str, Enum):
    ZERO_SHOT = "STRATEGY_ZERO_SHOT"
    FEW_SHOT = "STRATEGY_FEW_SHOT"
    CHAIN_OF_THOUGHT = "STRATEGY_CHAIN_OF_THOUGHT"


class ScoringPenalty(str, Enum):
    SECURITY_THREAT = "PENALTY_SECURITY_THREAT"
    POST_HOC = "PENALTY_POST_HOC"


class VerificationResult(str, Enum):
    VERIFIED = "RESULT_VERIFIED"
    DEBUNKED = "RESULT_DEBUNKED"
    UNVERIFIED = "RESULT_UNVERIFIED"


class EthicalSeverity(str, Enum):
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
    HYPOTHESES = "Analyst Hypotheses"  # Key in l10n


class LabelKey(str, Enum):
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

    WATERFALL_FLOOR = "WATERFALL_FLOOR"
    PROGRESSIVE_DAMPENING = "PROGRESSIVE_DAMPENING"
    PURE_AVERAGE = "PURE_AVERAGE"
    WEIGHTED_AVERAGE = "WEIGHTED_AVERAGE"


# --- Lax Type Aliases (Pydantic V2) ---
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
