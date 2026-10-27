"""Enumerations and taxonomy constants for the Quorum backend.

Strict definitions of allowed domain types enforcing the No-String Mandate.
"""

from dataclasses import dataclass
from enum import Enum, IntEnum, StrEnum
from typing import Annotated, Self

from pydantic import Field

__all__ = [
    "DEFAULT_ALIAS_LITERALS",
    "DEFAULT_NULL_HYPOTHESIS_BLACKLIST",
    "PIPELINE_REGISTRY",
    "XAI_EXTENSION_SCOPE",
    "AbductiveConclusion",
    "AlignmentVerdict",
    "AuthenticityLevel",
    "BlockDataType",
    "BloomLevel",
    "CausalRootCauseType",
    "CognitiveTier",
    "ComponentType",
    "DependencyRelationType",
    "DisplayScale",
    "EngineType",
    "EnsembleJitter",
    "EntityPrefix",
    "EthicalSeverity",
    "EvaluationCategory",
    "EvaluationMandate",
    "EvaluationRunCount",
    "EvidenceType",
    "ExecutionProfile",
    "ExecutionStatus",
    "FidelityLevel",
    "GCPVertexDiscoveryRegion",
    "GCPVertexLocation",
    "HelpTextKey",
    "HistoricalContextMode",
    "InteractionStrategy",
    "JSONSchemaPropertyType",
    "LLMCachingStrategy",
    "LLMPlatformType",
    "LLMProvider",
    "LLMProviderName",
    "LabelKey",
    "LaxAbductiveConclusion",
    "LaxAlignmentVerdict",
    "LaxAuthenticityLevel",
    "LaxBlockDataType",
    "LaxBloomLevel",
    "LaxCausalRootCauseType",
    "LaxCognitiveTier",
    "LaxComponentType",
    "LaxDependencyRelationType",
    "LaxDisplayScale",
    "LaxEngineType",
    "LaxEthicalSeverity",
    "LaxEvaluationRunCount",
    "LaxExecutionProfile",
    "LaxExecutionStatus",
    "LaxFidelityLevel",
    "LaxHistoricalContextMode",
    "LaxInteractionStrategy",
    "LaxJSONSchemaPropertyType",
    "LaxLLMCachingStrategy",
    "LaxLLMProvider",
    "LaxLLMProviderName",
    "LaxMCPAuthType",
    "LaxMCPTransportType",
    "LaxPlausibilityLevel",
    "LaxPresetView",
    "LaxPromptBlockCategory",
    "LaxPropositionNodeType",
    "LaxReportStatus",
    "LaxRiskLevel",
    "LaxRoleClassification",
    "LaxSDUIComponentType",
    "LaxSearchStatus",
    "LaxSimulationType",
    "LaxSourcesDisplayMode",
    "LaxStepFilterScope",
    "LaxStepType",
    "LaxStepZone",
    "LaxStorageBackend",
    "LaxStrategicDepth",
    "LaxSystemLocale",
    "LaxTargetBlockType",
    "LaxToolCapability",
    "LaxUiVariant",
    "LaxVerificationResult",
    "LaxVirtualSystemStepID",
    "LaxVisualIntent",
    "LaxXaiExtensionType",
    "MCPAuthType",
    "MCPTransportType",
    "PipelineConfig",
    "PlausibilityLevel",
    "PresetView",
    "PromptBlockCategory",
    "PromptCacheStatus",
    "PropositionNodeType",
    "ReferenceTitle",
    "ReportAtomColumn",
    "ReportMatrixColumn",
    "ReportSheetKey",
    "ReportStatus",
    "RiskLevel",
    "RoleClassification",
    "SDUIComponentType",
    "SearchStatus",
    "SelfHealingThresholdRatio",
    "SimulationType",
    "SourceSufficiencyThreshold",
    "SourcesDisplayMode",
    "SpecialAliasChoices",
    "StepFilterScope",
    "StepType",
    "StepZone",
    "StorageBackend",
    "StrategicDepth",
    "StrictnessAnchor",
    "SystemConfigID",
    "SystemLocale",
    "TargetBlockType",
    "TargetSpeaker",
    "TitleKey",
    "ToolCapability",
    "UiVariant",
    "ValidationThresholdRatio",
    "VerificationResult",
    "VirtualSystemStepID",
    "VisualIntent",
    "XaiExtensionScope",
    "XaiExtensionType",
]


class EngineType(StrEnum):
    """Explicit ExecutionEngine responsible for computing a step."""

    TDA = "tda"
    SYNTHESIS = "synthesis"
    PROMPT = "prompt"
    CAUSAL_DISCOVERY = "causal_discovery"


class StepType(StrEnum):
    """Execution taxonomy for workflow steps."""

    LLM = "llm"
    LOGIC = "logic"
    CAUSAL_DISCOVERY = "causal_discovery"


class EvaluationMandate(StrEnum):
    """Architectural null hypothesis mandate attached to all strict evaluations."""

    FAIL_FAST_NO_EVIDENCE = (
        " ENFORCEMENT: Evaluate as FALSE immediately unless explicit, documented evidence is provided."
    )


class ExecutionProfile(StrEnum):
    """Defines the execution intent for an LLM client, overriding static configuration rules.

    Attributes:
        ONE_SHOT: A single execution for hooks or parsers. Explicitly bypasses Context Caching
                  because cache creation costs outweigh single-run benefits.
        ITERATIVE: A looped or heavily re-executed process for chunk workers or synthesis regeneration.
                   Strictly enforces Context Caching to minimize token costs over multiple identical runs.
        CONVERSATIONAL: Standard interactive multi-turn chat behavior.
    """

    ONE_SHOT = "one_shot"
    ITERATIVE = "iterative"
    CONVERSATIONAL = "chat"


class CognitiveTier(StrEnum):
    """Canonical vendor-neutral cognitive evaluation tiers."""

    FAST = "fast"
    BALANCED = "balanced"
    DEEP = "deep"
    REASONING = "reasoning"


class LLMProvider(StrEnum):
    """Supported foundational model providers."""

    VERTEX_AI = "vertex_ai"
    AI_STUDIO = "ai_studio"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"
    LOCAL = "local"


class EvaluationRunCount(int, Enum):
    """Defines the number of evaluation runs for TDA matrix evaluations."""

    STANDARD = 1
    ENSEMBLE = 3


class EnsembleJitter(float, Enum):
    """Defines the delay multiplier in seconds for ensemble runs.

    Used to force Vertex AI cache divergence across parallel runs.
    """

    BASE_DELAY = 0.200


class SourceSufficiencyThreshold(int, Enum):
    """Minimum source document length (chars) to bypass MCP tool declarations.

    When the source text exceeds this threshold, the full document is already
    in the prompt and there is no information gap for tools to fill.
    """

    MIN_CHARS = 200


class EntityPrefix(StrEnum):
    """Canonical Opaque Stripe ID prefix taxonomy."""

    WORKFLOW = "wf"
    STEP = "stp"
    STEP_REFERENCE = "sr"
    OUTPUT_PROFILE = "prf"
    PROMPT_BLOCK = "blk"
    SYSTEM_CONFIG = "sys"
    EXECUTION = "exe"
    USER = "usr"
    ORGANIZATION = "org"
    TDA = "tda"
    REPORT = "rep"
    # Proposition graph node and edge Opaque Stripe ID prefixes
    NODE = "nod"
    EDGE = "edg"


class StorageBackend(StrEnum):
    """Supported storage backend engines for Quorum persistence."""

    FIRESTORE = "FIRESTORE"
    LOCAL = "LOCAL"
    POSTGRES = "POSTGRES"


LaxStorageBackend = Annotated[StorageBackend, Field(strict=False)]


class PropositionNodeType(StrEnum):
    """Toulmin and Structural Causal Model (SCM) proposition node classifications."""

    CLAIM = "claim"
    GROUND = "ground"
    WARRANT = "warrant"
    REBUTTAL = "rebuttal"
    SCM_VAR = "scm_var"


LaxPropositionNodeType = Annotated[PropositionNodeType, Field(strict=False)]


class DependencyRelationType(StrEnum):
    """Directed Toulmin and causal dependency edge relation classifications."""

    SUPPORTS = "supports"
    WARRANTS = "warrants"
    REBUTS = "rebuts"
    CAUSES = "causes"


LaxDependencyRelationType = Annotated[DependencyRelationType, Field(strict=False)]


class SystemConfigID(StrEnum):
    """Hardcoded Opaque Stripe IDs for global System Configurations."""

    MCP_GATEWAYS = "sys_8172bda70c8641c5"


class EvidenceType(StrEnum):
    """Categorizes the type of evidence discovered during TDA extraction."""

    EXPLICIT_QUOTE = "EXPLICIT_QUOTE"
    IMPLIED_INTENT = "IMPLIED_INTENT"
    NO_EVIDENCE = "NO_EVIDENCE"


class AlignmentVerdict(StrEnum):
    """Verdict characterizing mathematical alignment between mechanical and cognitive evaluations."""

    ALIGNED = "ALIGNED"
    MISALIGNED_SYCOPHANCY = "MISALIGNED_SYCOPHANCY"
    MISALIGNED = "MISALIGNED"


class DisplayScale(StrEnum):
    """Display scale configuration for matrix score rendering."""

    ORIGINAL = "original"
    CUSTOM = "custom"
    NORMALIZED_100 = "normalized_100"

    @property
    def l10n_key(self) -> str:
        """Return the camelCase Flutter ARB localization key for this display scale.

        Returns:
            Localization key string for the display scale.
        """
        match self:
            case DisplayScale.ORIGINAL:
                return "displayScaleOriginal"
            case DisplayScale.CUSTOM:
                return "displayScaleCustom"
            case DisplayScale.NORMALIZED_100:
                return "displayScaleNormalized100"


class BlockDataType(StrEnum):
    """Data types allowed for PromptBlock extracted values.

    Encompasses primitive extraction types and structural block types.
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
    PRINTABLE_SOURCES_BLOCK = "printable_sources_block"
    GROUPED_EXTENSIONS_BLOCK = "grouped_extensions_block"
    EXECUTIVE_SUMMARY_BLOCK = "executive_summary_block"
    METADATA_BLOCK = "metadata_block"
    SYNTHESIS_TEXT_BLOCK = "synthesis_text_block"
    MATRIX_GRAPHS_BLOCK = "matrix_graphs_block"
    MATRIX_SUMMARY_TABLE_BLOCK = "matrix_summary_table_block"
    VARIANCE_VALIDATION_BLOCK = "variance_validation_block"


class SourcesDisplayMode(StrEnum):
    """Configuration mode for bibliography and source verification presentation."""

    VERIFIED_EVIDENCE = "verified_evidence"
    SIMPLE_BIBLIOGRAPHY = "simple_bibliography"


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
        """Return the camelCase Flutter ARB localization key for this XAI extension.

        Returns:
            Localization key string, or empty string if unmapped in UI.
        """
        match self:
            case XaiExtensionType.COACHING:
                return "xaiCoachingTip"
            case XaiExtensionType.JUSTIFICATION:
                return "xaiJustification"
            case XaiExtensionType.FALSIFICATION:
                return "xaiDevilsAdvocate"
            case XaiExtensionType.MISSING_CONTEXT:
                return "xaiMissingContext"
            case XaiExtensionType.THEORY_LINK:
                return "xaiTheoryLink"
            case XaiExtensionType.RISK_FLAG:
                return "xaiRiskFlag"
            case XaiExtensionType.REMEDIATION_STEPS:
                return "xaiRemediation"
            case XaiExtensionType.EMOTIONAL_SENTIMENT:
                return "xaiSentiment"
            case XaiExtensionType.VARIANCE_VALIDATION:
                return "xaiVarianceValidationTitle"
            case XaiExtensionType.AUTHENTICITY_EVALUATION:
                return "xaiAuthenticityEvaluationTitle"
            case _:
                return ""


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
    """Semantic self-healing strictness ratios for LLM evaluation.

    Defines what top percentage of a numerical scale triggers mandatory evidence constraints.
    """

    STRICT = 0.75
    LENIENT = 0.50
    NONE = 0.00


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
        """Return the localization key for this execution status.

        Returns:
            Localization key string matching Flutter ARB definitions.
        """
        match self:
            case ExecutionStatus.PASSED:
                return "status_passed"
            case ExecutionStatus.FAILED:
                return "status_failed"
            case ExecutionStatus.N_A:
                return "status_n_a"
            case ExecutionStatus.SYSTEM_ERROR:
                return "status_system_error"
            case ExecutionStatus.BLOCKED:
                return "status_blocked"
            case ExecutionStatus.PENDING:
                return "status_pending"
            case ExecutionStatus.RUNNING:
                return "status_running"
            case ExecutionStatus.QUEUED:
                return "status_queued"


class ReportStatus(StrEnum):
    """Lifecycle status of a materialized report artifact."""

    PENDING = "pending"
    GENERATING = "generating"
    READY = "ready"
    FAILED = "failed"

    @property
    def l10n_key(self) -> str:
        """Map enum value to camelCase Flutter ARB key.

        Returns:
            Localization key string for the report status.
        """
        match self:
            case ReportStatus.PENDING:
                return "reportStatusPending"
            case ReportStatus.GENERATING:
                return "reportStatusGenerating"
            case ReportStatus.READY:
                return "reportStatusReady"
            case ReportStatus.FAILED:
                return "reportStatusFailed"


LaxReportStatus = Annotated[ReportStatus, Field(strict=False)]


class SDUIComponentType(StrEnum):
    """Canonical SDUI card component identifiers for frontend rendering."""

    BOOLEAN_CARD = "boolean_card"
    EXTRACTED_VALUE_CARD = "extracted_value_card"
    ERROR_CARD = "error_card"
    N_A_CARD = "n_a_card"

    @property
    def l10n_key(self) -> str:
        """Return the localization key for this SDUI component type.

        Returns:
            Localization key string matching Flutter ARB definitions.
        """
        match self:
            case SDUIComponentType.BOOLEAN_CARD:
                return "sdui_boolean_card"
            case SDUIComponentType.EXTRACTED_VALUE_CARD:
                return "sdui_extracted_value_card"
            case SDUIComponentType.ERROR_CARD:
                return "sdui_error_card"
            case SDUIComponentType.N_A_CARD:
                return "sdui_n_a_card"


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
    SV = "sv"


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
    AI_STUDIO = "ai_studio"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    MOCK = "mock_llm_99"


class GCPVertexLocation(StrEnum):
    """Static GCP Vertex AI regional locations."""

    EUROPE_NORTH1 = "europe-north1"  # Hamina, Finland
    EUROPE_WEST1 = "europe-west1"  # St. Ghislain, Belgium
    EUROPE_WEST4 = "europe-west4"  # Eemshaven, Netherlands
    EUROPE_WEST3 = "europe-west3"  # Frankfurt, Germany
    US_CENTRAL1 = "us-central1"  # Council Bluffs, Iowa
    US_EAST4 = "us-east4"  # Ashburn, Virginia


class GCPVertexDiscoveryRegion(StrEnum):
    """Authoritative Google Cloud Vertex AI central hub for Model Garden discovery."""

    US_CENTRAL1 = "us-central1"  # Council Bluffs, Iowa (Google AI Model Garden primary launch region)


class LLMPlatformType(StrEnum):
    """Target platform type for LLM model discovery and execution routing."""

    VERTEX_AI = "vertex_ai"
    AI_STUDIO = "ai_studio"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    ALL = "all"


class PromptCacheStatus(StrEnum):
    """Status states for prompt caching in shared ledger."""

    CREATING = "CREATING"
    CREATED = "CREATED"
    FAILED = "FAILED"


class ValidationThresholdRatio(float, Enum):
    """Float threshold limits for validation safety nets."""

    COVERAGE_SAFETY_NET = 0.60


class StrictnessAnchor(IntEnum):
    """Fixed UI strictness levels defining forgiveness anchor points."""

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

    @classmethod
    def from_score(cls, score: float | int) -> Self:
        """Map a numeric matrix evaluation score to a deterministic user agency role.

        Clamps score to 1-5 integer bounds:
        - <= 2: PASSENGER
        - 3: NAVIGATOR
        - 4: DRIVER
        - 5: ARCHITECT

        Args:
            score: Raw numeric score from evaluated matrix.

        Returns:
            RoleClassification enum member corresponding to clamped score.

        Raises:
            ValueError: If score is NaN or cannot be converted to float.
            OverflowError: If score is positive or negative infinity.
        """
        clamped = max(1, min(5, int(round(float(score)))))
        match clamped:
            case 1 | 2:
                return cls.PASSENGER
            case 3:
                return cls.NAVIGATOR
            case 4:
                return cls.DRIVER
            case _:
                return cls.ARCHITECT

    @property
    def l10n_key(self) -> str:
        """Map enum member to camelCase Flutter ARB translation key.

        Returns:
            Localization key string for the role classification.
        """
        match self:
            case RoleClassification.PASSENGER:
                return "rolePassenger"
            case RoleClassification.NAVIGATOR:
                return "roleNavigator"
            case RoleClassification.DRIVER:
                return "roleDriver"
            case RoleClassification.ARCHITECT:
                return "roleArchitect"


class InteractionStrategy(StrEnum):
    """Prompt engineering strategy classification for interaction quality assessment."""

    ZERO_SHOT = "STRATEGY_ZERO_SHOT"
    FEW_SHOT = "STRATEGY_FEW_SHOT"
    CHAIN_OF_THOUGHT = "STRATEGY_CHAIN_OF_THOUGHT"


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
    """Localization keys for contextual help tooltips across UI evaluation cards."""

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
    """Canonical section title identifiers for agent and report cards."""

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
    TITLE_TIMELINE = "TITLE_TIMELINE"
    TITLE_HYPOTHESES = "TITLE_HYPOTHESES"

    @property
    def l10n_key(self) -> str:
        """Return the camelCase Flutter ARB localization key for this title.

        Returns:
            Localization key string, or empty string if resolved via enum value.
        """
        match self:
            case TitleKey.TITLE_TIMELINE:
                return "titleTimeline"
            case TitleKey.TITLE_HYPOTHESES:
                return "titleHypotheses"
            case _:
                return ""


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


# --- Lax Type Aliases (Pydantic V2) ---
LaxSearchStatus = Annotated[SearchStatus, Field(strict=False)]
LaxUiVariant = Annotated[UiVariant, Field(strict=False)]
LaxExecutionProfile = Annotated[ExecutionProfile, Field(strict=False)]
LaxLLMCachingStrategy = Annotated[LLMCachingStrategy, Field(strict=False)]
LaxLLMProviderName = Annotated[LLMProviderName, Field(strict=False)]
LaxXaiExtensionType = Annotated[XaiExtensionType, Field(strict=False)]
LaxAuthenticityLevel = Annotated[AuthenticityLevel, Field(strict=False)]
LaxBloomLevel = Annotated[BloomLevel, Field(strict=False)]
LaxCognitiveTier = Annotated[CognitiveTier, Field(strict=False)]
LaxLLMProvider = Annotated[LLMProvider, Field(strict=False)]
LaxStrategicDepth = Annotated[StrategicDepth, Field(strict=False)]
LaxEngineType = Annotated[EngineType, Field(strict=False)]
LaxStepType = Annotated[StepType, Field(strict=False)]
LaxVerificationResult = Annotated[VerificationResult, Field(strict=False)]
LaxEthicalSeverity = Annotated[EthicalSeverity, Field(strict=False)]
LaxExecutionStatus = Annotated[ExecutionStatus, Field(strict=False)]
LaxBlockDataType = Annotated[BlockDataType, Field(strict=False)]
LaxComponentType = Annotated[ComponentType, Field(strict=False)]
LaxVisualIntent = Annotated[VisualIntent, Field(strict=False)]
LaxHistoricalContextMode = Annotated[HistoricalContextMode, Field(strict=False)]
LaxVirtualSystemStepID = Annotated[VirtualSystemStepID, Field(strict=False)]
LaxPromptBlockCategory = Annotated[PromptBlockCategory, Field(strict=False)]
LaxEvaluationRunCount = Annotated[EvaluationRunCount, Field(strict=False)]
LaxPlausibilityLevel = Annotated[PlausibilityLevel, Field(strict=False)]
LaxAbductiveConclusion = Annotated[AbductiveConclusion, Field(strict=False)]
LaxAlignmentVerdict = Annotated[AlignmentVerdict, Field(strict=False)]
LaxFidelityLevel = Annotated[FidelityLevel, Field(strict=False)]
LaxRiskLevel = Annotated[RiskLevel, Field(strict=False)]
LaxSimulationType = Annotated[SimulationType, Field(strict=False)]
LaxRoleClassification = Annotated[RoleClassification, Field(strict=False)]
LaxInteractionStrategy = Annotated[InteractionStrategy, Field(strict=False)]
LaxTargetBlockType = Annotated[TargetBlockType, Field(strict=False)]
LaxSourcesDisplayMode = Annotated[SourcesDisplayMode, Field(strict=False)]
LaxDisplayScale = Annotated[DisplayScale, Field(strict=False)]
LaxSDUIComponentType = Annotated[SDUIComponentType, Field(strict=False)]
LaxSystemLocale = Annotated[SystemLocale, Field(strict=False)]


class SpecialAliasChoices(StrEnum):
    """Global allowed exception values for AliasEngine and Pydantic validation."""

    NA = "N/A"


# Declared as a constant set for O(1) declarative logic lookups
DEFAULT_ALIAS_LITERALS: frozenset[str] = frozenset(item.value for item in SpecialAliasChoices)

DEFAULT_NULL_HYPOTHESIS_BLACKLIST: frozenset[str] = frozenset(
    [
        "null",
        "none",
        "n/a",
        "false",
        "",
        "ei löydy",
        "not found",
        "-",
        "ei mainittu",
        "none detected",
        "[]",
        "{}",
        "ei sovelleta",
        "ei lainausta",
        "no quote",
        "ei ole",
        "[contextual_override_applied]",
    ]
)


@dataclass(frozen=True)
class PipelineConfig:
    """Immutable static configuration for internal execution pipelines.

    Attributes:
        profile: Execution profile governing caching and iteration behavior.
        default_strategy: Optional cognitive tier strategy name.
    """

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


class PresetView(StrEnum):
    """UI Renderer presets for matrix graph visualization blocks."""

    METRICS_1D = "1d_metrics"
    COMPARE_2D = "2d_compare"
    MATRIX_3D = "3d_matrix"
    TEXT_ONLY = "text_only"
    DEFAULT = "default"
    MATRIX_SUMMARY = "matrix_summary"


LaxPresetView = Annotated[PresetView, Field(strict=False)]


class TargetSpeaker(StrEnum):
    """Evaluated target speaker for dialogue or deliverable claims."""

    USER = "USER"
    AI = "AI"


class ReportMatrixColumn(StrEnum):
    """Columns for standard matrix summary table projections."""

    EXECUTION_ID = "execution_id"
    LABEL = "label"
    CONTEXT_TARGET = "context_target"
    DISTRIBUTION = "distribution"
    HITS = "hits"
    TOTAL_ATOMS = "total_atoms"
    HIT_RATIO = "hit_ratio"
    RAW_SCORE = "raw_score"
    SCALE_MAX = "scale_max"
    NORMALIZED_SCORE = "normalized_score"
    ROW_EXPLANATION = "row_explanation"
    CRITERIA = "criteria"
    SOURCE = "source"

    @property
    def l10n_key(self) -> str:
        """Return the localization key in backend translation files.

        Returns:
            Localization key string for the matrix summary column.
        """
        return f"matrix_col_{self.value}"


class ReportAtomColumn(StrEnum):
    """Columns for evaluated atom forensic export tables."""

    MATRIX = "matrix"
    CONTEXT_TARGET = "context_target"
    LEVEL = "level"
    LEVEL_NAME = "level_name"
    CRITERION = "criterion"
    CLAIM_TYPE = "claim_type"
    IS_INVERSE = "is_inverse"
    POINTS_AWARDED = "points_awarded"
    RESULT_STATUS = "result_status"
    QUOTES = "quotes"
    AI_REASONING = "ai_reasoning"
    CAUSAL_STATUS = "causal_status"
    BLAME_PARENT_ID = "blame_parent_id"
    DEPENDENT_COUNT = "dependent_count"

    @property
    def l10n_key(self) -> str:
        """Return the localization key in backend translation files.

        Returns:
            Localization key string for the atom export column.
        """
        return f"export_col_{self.value}"


class ReportSheetKey(StrEnum):
    """Sheet names for workbook spreadsheet exports."""

    SUMMARY = "summary"
    RAW_DATA = "raw_data"

    @property
    def l10n_key(self) -> str:
        """Return the localization key in backend translation files.

        Returns:
            Localization key string for the workbook sheet.
        """
        return f"export_sheet_{self.value}"


class CausalRootCauseType(StrEnum):
    """Categorization of failure as node claim flaw, warrant grounding failure, or precondition mismatch."""

    NODE_FAILURE = "node_failure"
    WARRANT_GROUNDING_FAILURE = "warrant_grounding_failure"
    PRECONDITION_MISMATCH = "precondition_mismatch"

    @property
    def l10n_key(self) -> str:
        """Return the localization key in backend translation files.

        Returns:
            Localization key string for the causal root cause type.
        """
        match self:
            case CausalRootCauseType.NODE_FAILURE:
                return "causal_root_cause_node_failure"
            case CausalRootCauseType.WARRANT_GROUNDING_FAILURE:
                return "causal_root_cause_warrant_grounding_failure"
            case CausalRootCauseType.PRECONDITION_MISMATCH:
                return "causal_root_cause_precondition_mismatch"


LaxCausalRootCauseType = Annotated[CausalRootCauseType, Field(strict=False)]


class ToolCapability(StrEnum):
    """Operational capability category of an MCP tool."""

    SEARCH = "search"
    DOCUMENT_READER = "document_reader"
    ACTION = "action"
    GENERAL = "general"

    @property
    def l10n_key(self) -> str:
        """Return the localization key in backend translation files.

        Returns:
            Localization key string for the MCP tool capability.
        """
        return f"mcp_capability_{self.value}"


LaxToolCapability = Annotated[ToolCapability, Field(strict=False)]


class StepFilterScope(StrEnum):
    """Scope filtering for workflow step blueprints in Admin Studio."""

    SPECIALISTS = "specialists"
    SYSTEM_CORE = "system_core"
    ALL = "all"


LaxStepFilterScope = Annotated[StepFilterScope, Field(strict=False)]


class StepZone(StrEnum):
    """Functional workflow zone classification (Zone A Ingestion, Zone B Specialists, Zone C Funnel Anchors)."""

    ZONE_A = "zone_a"
    ZONE_B = "zone_b"
    ZONE_C = "zone_c"


LaxStepZone = Annotated[StepZone, Field(strict=False)]


class MCPTransportType(StrEnum):
    """Supported transport protocols for external MCP servers."""

    STREAMABLE_HTTP = "streamable_http"
    SSE = "sse"


LaxMCPTransportType = Annotated[MCPTransportType, Field(strict=False)]


class MCPAuthType(StrEnum):
    """Authentication schemes for outbound MCP gateway requests."""

    NONE = "none"
    BEARER = "bearer"
    API_KEY_HEADER = "api_key_header"


LaxMCPAuthType = Annotated[MCPAuthType, Field(strict=False)]


class JSONSchemaPropertyType(StrEnum):
    """JSON Schema Draft 2020-12 primitive and structural property types."""

    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    NULL = "null"


LaxJSONSchemaPropertyType = Annotated[JSONSchemaPropertyType, Field(strict=False)]
