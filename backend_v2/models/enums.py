"""Enums for V2 Backend.
Strict definition of allowed types to enforce the No-String Mandate.
"""

from dataclasses import dataclass
from enum import Enum, IntEnum, StrEnum
from typing import Annotated

from pydantic import Field


class EvaluationMandate(StrEnum):
    """Architectural Nollahypoteesi mandate attached to all strict evaluations."""

    FAIL_FAST_NO_EVIDENCE = (
        " ENFORCEMENT: Evaluate as FALSE immediately unless explicit, documented evidence is provided."
    )


class ExecutionProfile(StrEnum):
    """Defines the execution intent for an LLM client, overriding static configuration rules.

    Attributes:
        ONE_SHOT: A single execution (e.g. Hooks, ChatParser). Explicitly bypasses Context Caching
                  because cache creation costs outweigh single-run benefits.
        ITERATIVE: A looped or heavily re-executed process (e.g. ChunkWorker, Synthesis Regenerate).
                   Strictly enforces Context Caching to minimize token costs over multiple identical runs.
        CONVERSATIONAL: Standard interactive multi-turn chat behavior.
    """

    ONE_SHOT = "one_shot"
    ITERATIVE = "iterative"
    CONVERSATIONAL = "chat"


class EvaluationRunCount(int, Enum):
    """Määrittää suorituskertojen määrän TDA-matriisiarvioinneille."""

    STANDARD = 1
    ENSEMBLE = 3


class EnsembleJitter(float, Enum):
    """Määrittelee viivekertoimen (sekunneissa) ensemble-ajoille,
    jolla pakotetaan Vertex AI -välimuistin divergenssi.
    """

    BASE_DELAY = 0.200


class SourceSufficiencyThreshold(int, Enum):
    """Minimum source document length (chars) to bypass MCP tool declarations.

    When the source text exceeds this threshold, the full document is already
    in the prompt and there is no information gap for tools to fill.
    """

    MIN_CHARS = 200


class SystemConfigID(StrEnum):
    """Hardcoded Opaque Stripe IDs for global System Configurations."""

    MODEL_REGISTRY = "sys_e26807f3bfa3454d"
    MCP_GATEWAYS = "sys_8172bda70c8641c5"
    PERFORMATIVE_LEXICONS = "sys_e0b2a3c4d5e6f7a8"


class BlockDataType(StrEnum):
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


class PromptBlockCategory(StrEnum):
    """Strictly defined categories for PromptBlocks to guarantee Fail-Fast parity with Frontend."""

    MATRIX = "matrix"
    AGENT_ROLE = "agent_role"
    TASK_DEFINITION = "task_definition"
    SYSTEM_RULE = "system_rule"
    PROTOCOL = "protocol"
    RUNTIME_VARIABLES = "runtime_variables"
    EXECUTION_PERSONA = "execution_persona"


class ComponentType(StrEnum):
    """Component types allowed for SDUI Frontend Hint mapping."""

    SLIDER = "slider"
    TEXT_INPUT = "text_input"
    DROPDOWN = "dropdown"
    CHECKBOX = "checkbox"
    HIDDEN = "hidden"


class TargetBlockType(StrEnum):
    """Explicit layout hydration target blocks for SDUI."""

    GLOBAL_SCORE_BLOCK = "global_score_block"
    PENALTIES_BLOCK = "penalties_block"
    AUDIT_TRAIL_BLOCK = "audit_trail_block"
    JARGON_RATIO_BLOCK = "jargon_ratio_block"
    PRINTABLE_SOURCES_BLOCK = "printable_sources_block"
    GROUPED_EXTENSIONS_BLOCK = "grouped_extensions_block"


class VisualIntent(StrEnum):
    """UI intent mapping for SDUI visual rendering."""

    SUCCESS = "success"
    WARNING = "warning"
    CRITICAL_OVERRIDE = "critical_override"
    INFO = "info"
    NEUTRAL = "NEUTRAL"
    ERROR = "error"


class UiVariant(StrEnum):
    """UI display style variant mapping for SDUI."""

    DEFAULT = "default"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    NEUTRAL = "neutral"


class XaiExtensionType(StrEnum):
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
    AUTHENTICITY_EVALUATION = "authenticity_evaluation"

    @property
    def l10n_key(self) -> str:
        """Explicit mapping between Backend UPPER_SNAKE_CASE enums and Frontend ARB camelCase translation keys."""
        mapping = {
            XaiExtensionType.COACHING: "xaiCoachingTip",
            XaiExtensionType.JUSTIFICATION: "xaiJustification",
            XaiExtensionType.FALSIFICATION: "xaiDevilsAdvocate",
            XaiExtensionType.MISSING_CONTEXT: "xaiMissingContext",
            XaiExtensionType.THEORY_LINK: "xaiTheoryLink",
            XaiExtensionType.RISK_FLAG: "xaiRiskFlag",
            XaiExtensionType.REMEDIATION_STEPS: "xaiRemediation",
            XaiExtensionType.EMOTIONAL_SENTIMENT: "xaiSentiment",
            XaiExtensionType.VARIANCE_VALIDATION: "xaiVarianceValidationTitle",
            XaiExtensionType.AUTHENTICITY_EVALUATION: "xaiAuthenticityEvaluationTitle",
        }
        return mapping.get(self, "")


class XaiExtensionScope(StrEnum):
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
    XaiExtensionType.AUTHENTICITY_EVALUATION: XaiExtensionScope.WORKFLOW,
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


class ScoringCalibrationThresholds(float, Enum):
    """Thresholds for Benefit of the Doubt leniency and Double Jeopardy caps."""

    DINA_FLOOR = 0.30
    PENALTY_CAP = 0.25
    BENEFIT_OF_DOUBT_BONUS = 0.15


class EvaluationCategory(StrEnum):
    """Broad categorization for component classification."""

    MATHEMATICAL = "MATHEMATICAL"
    SEMANTIC = "SEMANTIC"
    LINGUISTIC = "LINGUISTIC"
    LOGICAL = "LOGICAL"
    BEHAVIORAL = "BEHAVIORAL"
    UNKNOWN = "UNKNOWN"


class SearchStatus(StrEnum):
    """Execution status for batch multi-search tasks."""

    COMPLETED = "COMPLETED"
    DLQ_TIMEOUT = "DLQ_TIMEOUT"
    DLQ_ERROR = "DLQ_ERROR"


class ExecutionStatus(StrEnum):
    """Execution lifecycle status.

    Str-Enum is mandatory for OpenAPI/Swagger generation,
    ensuring Flutter receives type-safe classes instead of Literal strings.
    """

    PASSED = "PASSED"
    FAILED = "FAILED"
    N_A = "N_A"
    SYSTEM_ERROR = "SYSTEM_ERROR"
    BLOCKED = "BLOCKED"
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    QUEUED = "QUEUED"

    @property
    def l10n_key(self) -> str:
        """strict_enum_l10n_mapping: Guarantees Flutter .arb compatibility."""
        return f"status_{self.name.lower()}"


class SDUIComponentType(StrEnum):
    """no_raw_string_enum_mappings: Prevents Magic String crashes in Flutter."""

    BOOLEAN_CARD = "boolean_card"
    EXTRACTED_VALUE_CARD = "extracted_value_card"
    ERROR_CARD = "error_card"
    N_A_CARD = "n_a_card"

    @property
    def l10n_key(self) -> str:
        """strict_enum_l10n_mapping: Guarantees Flutter .arb compatibility."""
        return f"sdui_{self.name.lower()}"


class VirtualSystemStepID(StrEnum):
    """Reserved IDs for Virtual System Steps generated dynamically by the DAG Engine."""

    SCORING_RESULT = "scoring_result"
    HAS_WARNING = "has_warning"
    SYNTHESIZED_MARKDOWN = "synthesized_markdown"
    STEP_METADATA = "_step_metadata"


class HistoricalContextMode(StrEnum):
    """Modes for fetching historical execution data during synthesis."""

    DISABLED = "DISABLED"
    SLIDING_WINDOW_3 = "SLIDING_WINDOW_3"


class SystemLocale(StrEnum):
    """Supported system locales."""

    EN = "en"
    FI = "fi"


class LLMCachingStrategy(StrEnum):
    """Supported caching strategies."""

    PROMPT_CACHING = "prompt_caching"
    EPHEMERAL = "ephemeral"
    ANTHROPIC_EPHEMERAL = "anthropic_ephemeral"
    GEMINI_NATIVE = "gemini_native"
    NONE = "none"


class LLMProviderName(StrEnum):
    """Supported LLM provider names."""

    VERTEX_AI = "vertex_ai"
    GOOGLE = "google"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    MOCK = "mock_llm_99"


class PromptCacheStatus(StrEnum):
    """Status states for prompt caching in shared ledger."""

    CREATING = "CREATING"
    CREATED = "CREATED"
    FAILED = "FAILED"


class ValidationThresholdRatio(float, Enum):
    """Float threshold limits for validation safety nets."""

    COVERAGE_SAFETY_NET = 0.60


# --- Restored V1 Enums ---


class StrictnessAnchor(IntEnum):
    """UI:n kiinteät Strictness-tasot. Määrittää pehmeyden (forgiveness) ankkuripisteet."""

    NONE = 0
    RELAXED = 30
    STANDARD = 50
    BALANCED = 70
    STRICT = 85
    ABSOLUTE = 100


class RiskLevel(StrEnum):
    """Tri-level risk classification for security and compliance evaluations."""

    LOW = "RISK_LOW"
    MEDIUM = "RISK_MEDIUM"
    HIGH = "RISK_HIGH"


class SimulationType(StrEnum):
    """Classifies the type of adversarial simulation applied during security analysis."""

    PASSIVE = "SIM_PASSIVE"
    ACTIVE = "SIM_ACTIVE"
    MALICIOUS = "SIM_MALICIOUS"


class BloomLevel(StrEnum):
    """Bloom's Taxonomy cognitive complexity levels for learning objective classification."""

    REMEMBERING = "BLOOM_REMEMBERING"
    UNDERSTANDING = "BLOOM_UNDERSTANDING"
    APPLYING = "BLOOM_APPLYING"
    ANALYZING = "BLOOM_ANALYZING"
    EVALUATING = "BLOOM_EVALUATING"
    CREATING = "BLOOM_CREATING"


class StrategicDepth(StrEnum):
    """Graduated scale for evaluating strategic thinking depth in user responses."""

    LOW = "STRAT_LOW"
    MEDIUM = "STRAT_MEDIUM"
    HIGH = "STRAT_HIGH"
    VISIONARY = "STRAT_VISIONARY"


class FidelityLevel(StrEnum):
    """Source fidelity classification for evidence quality assessment."""

    WEAK = "FIDELITY_WEAK"
    UNCERTAIN = "FIDELITY_UNCERTAIN"
    HIGH = "FIDELITY_HIGH"


class PlausibilityLevel(StrEnum):
    """Plausibility classification for abductive reasoning conclusions."""

    IMPOSSIBLE = "IMPOSSIBLE"
    PLAUSIBLE = "PLAUSIBLE"
    HIGH = "HIGH"


class AbductiveConclusion(StrEnum):
    """Abductive inference outcome classification for causal reasoning evaluations."""

    POST_HOC = "POST_HOC"
    UNCERTAIN = "UNCERTAIN"
    GENUINE = "GENUINE"


class AuthenticityLevel(StrEnum):
    """Authenticity classification for performativity detection in user discourse."""

    ORGANIC = "AUTH_ORGANIC"
    PERFORMATIVE = "AUTH_PERFORMATIVE"
    UNKNOWN = "AUTH_UNKNOWN"


class RoleClassification(StrEnum):
    """User agency classification from passive observer to active architect."""

    PASSENGER = "ROLE_PASSENGER"
    NAVIGATOR = "ROLE_NAVIGATOR"
    DRIVER = "ROLE_DRIVER"
    ARCHITECT = "ROLE_ARCHITECT"

    @property
    def l10n_key(self) -> str:
        """Explicit mapping between Backend UPPER_SNAKE_CASE enums and Frontend ARB camelCase translation keys."""
        mapping = {
            RoleClassification.PASSENGER: "rolePassenger",
            RoleClassification.NAVIGATOR: "roleNavigator",
            RoleClassification.DRIVER: "roleDriver",
            RoleClassification.ARCHITECT: "roleArchitect",
        }
        return mapping.get(self, "")


class InteractionStrategy(StrEnum):
    """Prompt engineering strategy classification for interaction quality assessment."""

    ZERO_SHOT = "STRATEGY_ZERO_SHOT"
    FEW_SHOT = "STRATEGY_FEW_SHOT"
    CHAIN_OF_THOUGHT = "STRATEGY_CHAIN_OF_THOUGHT"


class ScoringPenalty(StrEnum):
    """Penalty types applied during deterministic score calibration."""

    SECURITY_THREAT = "PENALTY_SECURITY_THREAT"
    POST_HOC = "PENALTY_POST_HOC"


class VerificationResult(StrEnum):
    """Fact-check verification outcome for falsification agent evaluations."""

    VERIFIED = "RESULT_VERIFIED"
    DEBUNKED = "RESULT_DEBUNKED"
    UNVERIFIED = "RESULT_UNVERIFIED"


class EthicalSeverity(StrEnum):
    """Ethical concern severity levels for overseer agent flagging."""

    NONE = "SEVERITY_NONE"
    WARNING = "SEVERITY_WARNING"
    CRITICAL = "SEVERITY_CRITICAL"


class HelpTextKey(StrEnum):
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


class TitleKey(StrEnum):
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


class LabelKey(StrEnum):
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


class ReferenceTitle(StrEnum):
    """Strict Enum for UI Reference Strings to prevent hardcoded L10N (No String Mandate)."""

    WEB_SEARCH = "REF_WEB_SEARCH"
    INTERNAL_DOCUMENT = "REF_INTERNAL_DOCUMENT"
    EXPERT_QUOTATION = "REF_EXPERT_QUOTATION"
    PREVIOUS_REPORT = "REF_PREVIOUS_REPORT"


class ScoringStrategy(StrEnum):
    """Selects the mathematical engine used to calculate final matrix scores."""

    WATERFALL = "WATERFALL"
    AVERAGE = "AVERAGE"
    WEIGHTED_AVERAGE = "WEIGHTED_AVERAGE"
    PURE_MATH = "PURE_MATH"


# --- Lax Type Aliases (Pydantic V2) ---
LaxSearchStatus = Annotated[SearchStatus, Field(strict=False)]
LaxUiVariant = Annotated[UiVariant, Field(strict=False)]
LaxExecutionProfile = Annotated[ExecutionProfile, Field(strict=False)]
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
LaxVisualIntent = Annotated[VisualIntent, Field(strict=False)]
LaxHistoricalContextMode = Annotated[HistoricalContextMode, Field(strict=False)]
LaxScoringStrategy = Annotated[ScoringStrategy, Field(strict=False)]
LaxVirtualSystemStepID = Annotated[VirtualSystemStepID, Field(strict=False)]
LaxPromptBlockCategory = Annotated[PromptBlockCategory, Field(strict=False)]
LaxEvaluationRunCount = Annotated[EvaluationRunCount, Field(strict=False)]
LaxPlausibilityLevel = Annotated[PlausibilityLevel, Field(strict=False)]
LaxAbductiveConclusion = Annotated[AbductiveConclusion, Field(strict=False)]
LaxFidelityLevel = Annotated[FidelityLevel, Field(strict=False)]
LaxRiskLevel = Annotated[RiskLevel, Field(strict=False)]
LaxSimulationType = Annotated[SimulationType, Field(strict=False)]
LaxRoleClassification = Annotated[RoleClassification, Field(strict=False)]
LaxInteractionStrategy = Annotated[InteractionStrategy, Field(strict=False)]
LaxTargetBlockType = Annotated[TargetBlockType, Field(strict=False)]


class SpecialAliasChoices(StrEnum):
    """Globaalit sallitut poikkeusarvot AliasEnginelle ja Pydantic-validaatiolle."""

    NA = "N/A"


# Declared as a constant set for O(1) declarative logic lookups
DEFAULT_ALIAS_LITERALS: frozenset[str] = frozenset(item.value for item in SpecialAliasChoices)


@dataclass
class PipelineConfig:
    """Static configuration for internal execution pipelines."""

    profile: ExecutionProfile
    default_strategy: str | None = None


# Static registry for execution pipelines.
# This prevents putting backend physical logic into the mutable database.
PIPELINE_REGISTRY: dict[str, PipelineConfig] = {
    "chat_parser": PipelineConfig(profile=ExecutionProfile.ONE_SHOT, default_strategy="fast"),
    "mcp_tool_loop": PipelineConfig(profile=ExecutionProfile.ITERATIVE),
    "chunk_worker": PipelineConfig(profile=ExecutionProfile.ITERATIVE),
    "studio_generation": PipelineConfig(profile=ExecutionProfile.ONE_SHOT, default_strategy="fast"),
    "interaction_hook": PipelineConfig(profile=ExecutionProfile.ONE_SHOT, default_strategy="fast"),
    "synthesis": PipelineConfig(profile=ExecutionProfile.ITERATIVE),
    "synthesis_strict": PipelineConfig(profile=ExecutionProfile.ONE_SHOT),
}
