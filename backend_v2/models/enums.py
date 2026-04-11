"""Enums for V2 Backend.
Strict definition of allowed types to enforce the No-String Mandate.
"""

from enum import Enum


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

    STRICT = 1.00
    STANDARD = 0.90
    LENIENT = 0.75

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


class ExecutionStatus(str, Enum):
    """Execution lifecycle status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SystemConcurrency(int, Enum):
    """Global concurrency limits for DAG Execution to prevent API Rate Limits."""

    MAX_CONCURRENT_WORKFLOWS = 1
    MAX_CONCURRENT_LLM_STEPS = 2
    LLM_MAX_RETRIES = 10
    LLM_DEFAULT_TIMEOUT_SECONDS = 120


class MatrixSamplingStrategy(int, Enum):
    """Dynamic sampling limits for Matrix Flattening Hook.
    0 means no sampling (flatten all atoms). N means select N atoms per specific BARS scale point.
    """

    ALL = 0
    STRATIFIED_1 = 1
    STRATIFIED_3 = 3
    STRATIFIED_5 = 5


# --- Restored V1 Enums ---


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


class ScoringPenalty(str, Enum):
    SECURITY_THREAT = "PENALTY_SECURITY_THREAT"
    POST_HOC = "PENALTY_POST_HOC"


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
