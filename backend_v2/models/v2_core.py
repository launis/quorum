"""V2 Core Models for Backend.

Implements dynamic, append-only, and I18N-capable models according to V2 specs.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Annotated, Any, Literal, Self, cast  # noqa: F401

if TYPE_CHECKING:
    from backend_v2.models.domain.inputs import WorkflowInputs, WorkflowInputsIngress
    from backend_v2.models.dtos.dag_models import CausalEdge
    from backend_v2.models.dtos.trace import DataStarvationEvent
    from backend_v2.models.state import ErrorTraceEvent, TombstoneEvent, TraceEvent
    from backend_v2.models.view.sdui import AnySduiBlock

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, StringConstraints, field_validator, model_validator

from backend_v2.exceptions import ErrorCodes
from backend_v2.models.core_base import I18nText, V2CoreBase
from backend_v2.models.dtos.quote_evidence import LLMExtractedQuote
from backend_v2.models.dtos.synthesis import XaiHighlightItem
from backend_v2.models.enums import (
    BlockDataType,
    ComponentType,
    DisplayScale,
    ExecutionStatus,
    LaxComponentType,
    LaxDisplayScale,
    LaxExecutionStatus,
    LaxHistoricalContextMode,
    LaxPresetView,
    LaxScoringStrategy,
    LaxSDUIComponentType,
    LaxSourcesDisplayMode,
    LaxStepType,
    LaxTargetBlockType,
    LaxXaiExtensionType,
    PresetView,
    ScoringStrategy,
    SourcesDisplayMode,
    StepType,
    StrictnessAnchor,
    TargetBlockType,
)
from backend_v2.models.execution_core import ExecutionCoreFields, ExecutionMetadata
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)


__all__ = [
    "AcceptanceCriterion",
    "AllowedMCPTool",
    "AntiPattern",
    "AtomResultDTO",
    "BaseMatrixXAI",
    "BaseTDAExtraction",
    "BlockDataType",
    "ChatMessageDTO",
    "ChatHistoryDTO",
    "ComponentType",
    "DataDictionaryField",
    "DataStarvationEvent",
    "ErrorDetailsDTO",
    "EvidenceRejectionRequest",
    "ExecutionCoreFields",
    "ExecutionCreate",
    "ExecutionMetricsDTO",
    "ExecutionRecord",
    "ExecutionStatus",
    "ExecutionStepState",
    "ExpectedInput",
    "ExtensionMetricsDTO",
    "ExtractedValueDTO",
    "FrozenContext",
    "HumanOverrideDTO",
    "HumanOverrideRequest",
    "HydratedAtomDTO",
    "I18nText",
    "JobAcceptedDTO",
    "LexiconConfigPayload",
    "LexiconSuggestionListDTO",
    "MCPAuditTrace",
    "MatrixClaim",
    "MatrixRow",
    "MatrixScale",
    "MatrixScorecardRowDTO",
    "MatrixSynthesisGroup",
    "ModelProfile",
    "OutputProfile",
    "QuestionnaireItem",
    "RenderedSynthesisCache",
    "ReportDataDTO",
    "Role",
    "ScorecardAtomDTO",
    "Step",
    "StepRule",
    "SystemConfigMCPGateways",
    "SystemConfigModelRegistry",
    "SystemConfigPerformativeLexicons",
    "TDAAssertion",
    "TheoryGrounding",
    "Workflow",
    "WorkflowInputs",
    "XaiHighlightItem",
]


class TheoryGrounding(V2CoreBase):
    """Used in PromptBlock to bind criteria to organizational truth.

    Attributes:
        source_url: URL or reference to the source material.
        citation_reference: Specific section or phrase to cite from the source.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    source_url: str = Field(description="URL or reference to the source material.")
    citation_reference: str | None = Field(
        default=None, description="Specific section or phrase to cite from the source."
    )


class AcceptanceCriterion(V2CoreBase):
    """Structured acceptance criterion with bilingual instruction."""

    model_config = ConfigDict(strict=True, extra="forbid")

    instruction: str = Field(description="Structured monolingual instruction.")
    requires_contextual_override: bool = Field(default=False)


class AntiPattern(V2CoreBase):
    """Known anti-pattern with bilingual description."""

    model_config = ConfigDict(strict=True, extra="forbid")

    pattern: str = Field(description="Known anti-pattern with monolingual description.")
    allows_contextual_excuse: bool = Field(default=False)


def _coerce_to_tuple(v: Any) -> Any:
    """Coerces list to tuple for immutable DAG depends_on fields."""
    if isinstance(v, list):
        return tuple(v)
    return v


class TDAAssertion(V2CoreBase):
    """Deterministic rule evaluated by the backend.

    Attributes:
        tda_id: Opaque Stripe ID for this assertion.
        inverse_evidence: If True, acts as a poison/penalty detector.
        aggregation_mode: Aggregation constraint.
        evaluation_track: Decoupled evaluation track.
        facts_to_find: The list of facts to extract for this assertion.
        logical_expression: Whitelisted Boolean logical expression using extracted facts.
        allow_contextual_override: If True, allows overriding this assertion with a contextual excuse.
        high_entropy: If True, enables multi-agent ensemble majority voting for this assertion.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    tda_id: str = Field(
        default_factory=lambda: f"tda_{uuid.uuid4().hex}",
        pattern=r"^tda_[a-f0-9]{32}$",
        description="Opaque Stripe ID for this assertion.",
    )
    inverse_evidence: bool = Field(description="If True, acts as a poison/penalty detector.")
    aggregation_mode: Literal["EXISTS", "ALL_MUST_COMPLY"] = Field(description="Aggregation constraint.")

    # Decoupled evaluation track properties for extractive sensor and cognitive judgement pipelines
    evaluation_track: Literal["EXTRACTIVE_SENSOR", "COGNITIVE_JUDGEMENT"] = Field(
        default="COGNITIVE_JUDGEMENT",
        description="Decoupled evaluation track: extractive logic vs cognitive judgement.",
    )
    facts_to_find: list[str] = Field(
        default_factory=list,
        description="The list of facts to extract for this assertion.",
    )
    logical_expression: str | None = Field(
        default=None,
        description="Whitelisted Boolean logical expression using extracted facts.",
    )
    high_entropy: bool = Field(
        default=False,
        description="If True, enables multi-agent ensemble majority voting for this assertion.",
    )

    # Monolingual concept description consumed by the LLM extraction pipeline
    concept_description: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=10),
    ] = Field(description="Concise concept definition for this assertion, not runtime instructions")
    anchor_target: str | None = Field(default=None, description="Target anchor to search for during extraction")
    bounding_box_scope: Literal["sentence", "paragraph", "document", "adjacent_paragraphs"] = Field(default="paragraph")
    extraction_rule: str | None = Field(default=None, description="The extraction rule that data must satisfy")
    acceptance_criteria: list[AcceptanceCriterion] = Field(
        default_factory=list,
        description="Structured acceptance criteria with monolingual instructions.",
    )
    anti_patterns: list[AntiPattern] = Field(
        default_factory=list,
        description="Known anti-patterns with monolingual descriptions.",
    )
    contrastive_example: str | None = Field(
        default=None,
        description="Monolingual contrastive example showing correct vs incorrect.",
    )
    syntactic_anchors: list[str] = Field(
        default_factory=list,
        description="Exact syntactic markers for extractive matching.",
    )
    enforce_pre_flight: bool = Field(
        default=False,
        description="If True, enables pre-flight validation before LLM evaluation.",
    )
    depends_on: Annotated[
        tuple[CausalEdge, ...],
        BeforeValidator(_coerce_to_tuple),
        Field(
            default_factory=tuple,
            description="Causal preconditions required for this assertion.",
        ),
    ]

    @model_validator(mode="after")
    def validate_math_logic(self) -> TDAAssertion:
        """Validates the consistency of the assertion constraints.

        Raises:
            AppException: If constraints are mathematically or logically invalid.

        Returns:
            The validated assertion.
        """
        if self.inverse_evidence and self.aggregation_mode == "ALL_MUST_COMPLY":
            msg = "Inverse evidence (poison detection) strictly requires 'EXISTS' aggregation mode."
            logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise ValueError(msg)

        # Enforce strict dual-track TDA validations
        if self.evaluation_track == "EXTRACTIVE_SENSOR":
            if not self.facts_to_find:
                msg = "EXTRACTIVE_SENSOR track requires at least one fact in facts_to_find."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
            if not self.logical_expression or not self.logical_expression.strip():
                msg = "EXTRACTIVE_SENSOR track requires a defined logical_expression."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
        return self


class MatrixClaim(V2CoreBase):
    """Represents a single behavioral claim with empirical TDA assertions.

    Attributes:
        label: User-facing empirical claim.
        tda_assertions: Test-Driven Assertion rules explicitly set by experts.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    label: I18nText = Field(description="User-facing empirical claim.")
    tda_assertions: list[TDAAssertion] = Field(
        ...,
        min_length=1,
        description="Test-Driven Assertion rules explicitly set by experts.",
    )


class MatrixRow(V2CoreBase):
    """Represents a row in a 2D matrix evaluating multiple dimensions.

    Attributes:
        label: User-facing row name.
        ai_description: Dedicated AI evaluation instruction for this sub-dimension.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    label: I18nText = Field(description="User-facing row name.")
    ai_description: str = Field(description="Dedicated AI evaluation instruction for this sub-dimension.")


class MatrixScale(V2CoreBase):
    """Represents a single score point in a BARS matrix scale.

    Attributes:
        score: Numerical value of the scale point.
        name: Optional name for the scale point (e.g., 'Excellent').
        ai_label: Short uppercase AI mnemonic replacing English target label, e.g. CATASTROPHIC FAILURE.
        claims: List of behavioral claims/criteria for this score.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    score: int = Field(description="Numerical value of the scale point.")
    name: I18nText | None = Field(default=None, description="Optional name for the scale point (e.g., 'Excellent').")
    ai_label: str = Field(
        description="Short uppercase AI mnemonic replacing English target label, e.g. CATASTROPHIC FAILURE"
    )
    claims: list[MatrixClaim] = Field(
        default_factory=list, description="List of behavioral claims/criteria for this score."
    )


class ChatMessageDTO(V2CoreBase):
    """Schema for a single parsed chat message.

    Attributes:
        role: The role of the speaker (e.g. 'user' or 'ai').
        content: The message text.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    role: str = Field(description="The role of the speaker (e.g. 'user' or 'ai').")
    content: str = Field(description="The message text.")


class ChatHistoryDTO(V2CoreBase):
    """Strict schema for a complete parsed chat sequence.

    Attributes:
        conversation: List of messages in chronological order.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    conversation: list[ChatMessageDTO] = Field(description="List of messages in chronological order.")


class DataDictionaryField(V2CoreBase):
    """UI Hints mapping for dynamic form generation (SDUI)."""

    model_config = ConfigDict(strict=True, extra="forbid")

    field_id: str
    component_type: LaxComponentType = Field(description="E.g., 'slider', 'text_input', 'dropdown'")
    options: list[dict[str, Any]] | None = None
    validation_rules: dict[str, Any] | None = None


class ModelProfile(V2CoreBase):
    """A flattened physical AI model representation."""

    model_config = ConfigDict(strict=True, extra="forbid")

    provider: str = Field(description="E.g., 'google', 'openai'")
    model_name: str = Field(description="The underlying API model name")
    temperature: float | None = Field(default=None, description="Generation temperature")
    top_p: float | None = Field(default=None, description="Nucleus sampling probability")
    top_k: int | None = Field(default=None, description="Top-K sampling")
    tpm_limit: int | None = Field(default=None, description="Tokens per minute limit")
    rpm_limit: int | None = Field(default=None, description="Requests per minute limit")
    max_tokens: int | None = Field(default=None, description="Max generated tokens")
    frequency_penalty: float | None = Field(default=None, description="Frequency penalty")
    presence_penalty: float | None = Field(default=None, description="Presence penalty")
    allowed_tools: list[str] = Field(default_factory=list, description="Enabled tools")
    supports_grounding: bool = Field(default=False, description="Supports Google Search Grounding")
    api_key: str | None = Field(default=None, description="Optional override API key")
    parsing_mode: str | None = Field(default=None, description="Parser logic flag (e.g. 'STRUCTURED_JSON')")
    caching_strategy: str | None = Field(
        default=None, description="Cache strategy identifier (e.g. 'anthropic_ephemeral')"
    )
    # Phase 1: Strongly-typed thinking/reasoning token budget
    thinking_budget_tokens: int | None = Field(
        default=None, description="Reasoning/thinking token budget for reasoning models (e.g. Gemini 3.7, Claude 3.7)"
    )
    # Phase 1, Milestone 1: Add additional_params dict field to ModelProfile
    additional_params: dict[str, Any] = Field(
        default_factory=dict, description="Additional provider-specific parameters."
    )
    is_active: bool = Field(default=True, description="Whether the model is actively available")


class SystemConfigModelRegistry(V2CoreBase):
    """V2 Flattened Model Registry System Config."""

    model_config = ConfigDict(strict=True, extra="forbid")

    id: str = Field(pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$", description="System config ID")
    type: str = Field(description="Type of config")
    slug: str | None = Field(default=None, description="System Config identifier slug")
    models: dict[str, ModelProfile] = Field(
        description="Dictionary mapping generic role names to specific ModelProfiles"
    )


class AllowedMCPTool(V2CoreBase):
    """Declares a single MCP tool available for LLM function calling."""

    model_config = ConfigDict(strict=True, extra="forbid")

    tool_id: str = Field(description="Unique slug (e.g. 'mcp_tavily_search').")
    name: I18nText = Field(description="Localized display name.")
    description: str = Field(description="English-only LLM description for function calling schema.")
    input_schema: dict[str, Any] = Field(
        default_factory=dict, description="JSON Schema defining the tool's input parameters."
    )


class MCPAuditTrace(V2CoreBase):
    """Immutable audit log entry for a single MCP tool invocation."""

    model_config = ConfigDict(strict=True, extra="forbid")

    id: str | None = Field(default=None, description="Unique identifier for the trace injected by the driver.")
    tool_id: str = Field(description="Which tool was called.")
    step_name: str = Field(description="DAG step that triggered the call.")
    claim_text: str | None = Field(default=None, description="The verbatim claim that triggered this search.")
    query: str = Field(description="The search query or tool input.")
    knowledge_gap: str = Field(default="", description="The knowledge gap that needs to be resolved.")
    search_rationale: str = Field(default="", description="The rationale for the search query.")
    reasoning: str = Field(default="", description="Brief explanation of why this claim was verified.")
    response_summary: str = Field(default="", description="Extracted text summary.")
    source_urls: list[str] = Field(default_factory=list, description="Source URLs returned.")
    impacted_axis_names: list[str] = Field(
        default_factory=list, description="List of matrix axis names that used this trace."
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="UTC timestamp of the tool call."
    )
    duration_ms: int = Field(default=0, description="Round-trip latency in milliseconds.")


class SystemConfigMCPGateways(V2CoreBase):
    """System-level registry of available MCP tool gateways."""

    model_config = ConfigDict(strict=True, extra="forbid")

    id: str = Field(pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$", description="System config ID")
    type: str = Field(description="Config type discriminator.")
    slug: str | None = Field(default=None, description="System Config identifier slug")
    tools: list[AllowedMCPTool] = Field(
        default_factory=list, description="Registry of all available MCP tools in the system."
    )


class LexiconConfigPayload(V2CoreBase):
    """Configuration for a single language lexicon."""

    model_config = ConfigDict(strict=True, extra="forbid")

    language_code: str = Field(description="ISO language code (e.g., 'en', 'fi').")
    language_name: str = Field(description="Human readable language name.")
    fuzz_threshold: float = Field(default=85.0, description="RapidFuzz threshold (0-100).")
    words: list[str] = Field(default_factory=list, description="List of performative phrases.")


class SystemConfigPerformativeLexicons(V2CoreBase):
    """System configuration for multi-language performative lexicons."""

    model_config = ConfigDict(strict=True, extra="forbid")

    id: str = Field(pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$", description="System config ID")
    type: Literal["performative_lexicons"] = Field(
        default="performative_lexicons", description="Config type discriminator."
    )
    slug: str | None = Field(default=None, description="System Config identifier slug")
    lexicon_configs: dict[str, LexiconConfigPayload] = Field(
        default_factory=dict, description="Map of language code to lexicon configuration."
    )


class LexiconSuggestionListDTO(V2CoreBase):
    """Structured DTO for LLM returned performative phrases."""

    model_config = ConfigDict(strict=True, extra="forbid")

    suggested_phrases: list[str] = Field(
        default_factory=list, description="List of suggested performative or slop phrases."
    )


class Step(V2CoreBase):
    """Isolated, reusable orchestrator cognitive module (e.g. Guard or step_input_processing).
    Formerly known as TaskBlueprint.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    id: str = Field(pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$", description="Unique UUID for storage optionally")
    slug: str = Field(description="Human-readable identifier (e.g., 'step_guard')")
    organization_id: str | None = Field(default=None, description="Tenant organization ID.")
    name: I18nText = Field(description="Localized step name")
    description: I18nText | None = Field(default=None, description="Detailed step context")
    type: LaxStepType = Field(default=StepType.LLM, description="Step execution type (llm or native logic)")
    hook: str | None = Field(default=None, description="Native Python hook to execute if type is 'logic'")
    role_block_id: str | None = Field(
        default=None,
        pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$",
        description="Reference to role block (e.g. blk_role_critic)",
    )
    extraction_protocol_block_id: str | None = Field(
        default=None,
        pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$",
        description="Reference to global evidence extraction protocol block",
    )
    execution_persona_block_id: str | None = Field(
        default=None,
        pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$",
        description="Reference to the Execution Persona PromptBlock",
    )
    criteria_block_ids: list[str] = Field(
        default_factory=list,
        description="References to matrix or text blocks",
    )
    pre_hooks: list[str] = Field(
        default_factory=list, description="Native Python functions to execute BEFORE LLM context building."
    )
    post_hooks: list[str] = Field(
        default_factory=list, description="Native Python functions to execute AFTER LLM generation."
    )
    safety: Literal["safe", "unsafe"] = Field(
        default="safe",
        description="Marks step as safe (read-only MCP) or unsafe (email/API mutations) for strict execution security.",
    )
    allowed_mcp_tools: list[str] = Field(
        default_factory=list, description="List of allowed MCP tools for this step (e.g. ['mcp_tavily_search'])."
    )
    model_strategy: str | None = Field(
        default=None,
        description=(
            "Step-level override for cognitive strategy profile (e.g., 'fast'). "
            "Takes precedence over workflow strategy."
        ),
    )
    expected_inputs: list[str] = Field(
        default_factory=list,
        description="List of expected input keys required for this step. Replaces free-text generic routing.",
    )
    output_schema: dict[str, Any] | None = Field(
        default=None,
        description="Optional JSON schema defining the structured output of this step.",
    )
    # Phase 1, Step 2: Workflow context governance field
    is_system_core: Annotated[
        bool,
        Field(description="Whether this step blueprint is a protected system foundational component."),
    ] = False

    @model_validator(mode="after")
    def validate_step_consistency(self) -> Step:
        """Strict fail-fast validation to ensure Step is structurally complete.

        Raises:
            AppException: If structure is malformed or internally inconsistent.

        Returns:
            The sanitized Step matching schema expectations.
        """
        if self.type == "llm":
            if not self.model_strategy:
                msg = f"LLM Step '{self.id}' must declare an explicit model_strategy (Zero-Fallback Rule)."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
            if not self.criteria_block_ids:
                msg = f"LLM Step '{self.id}' must define at least one criteria_block_id."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
            if not self.extraction_protocol_block_id:
                msg = f"LLM Step '{self.id}' must define a valid extraction_protocol_block_id."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
        if self.type == "logic" and not self.hook:
            msg = f"Logic Step '{self.id}' must define a native 'hook' execution target."
            logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise ValueError(msg)
        return self


class StepRule(V2CoreBase):
    """Execution step mapping (DAG Router Node)."""

    id: str = Field(
        default_factory=lambda: f"sr_{uuid.uuid4().hex[:16]}",
        pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$",
        description="Unique node ID in the workflow (e.g. blk_node_1).",
    )
    task_blueprint: str = Field(
        min_length=1, description="ID reference to the isolated Step (e.g., 'step_f15853d2584e4096aeb60f11a3e6ea7c')"
    )
    depends_on: list[str] = Field(default_factory=list, description="IDs of steps that must complete first.")
    input_mappings: dict[str, str] = Field(
        default_factory=dict,
        description='Maps upstream results to LLM inputs. e.g. {"context": "$inputs.document"}',
    )
    expected_sdui_type: Annotated[
        Literal["markdown", "hero_insight", "grid"] | None,
        Field(description="Declares the expected SDUI output schema for schema compilation."),
    ] = None
    # Phase 1, Step 2: Synthesis context governance field
    is_synthesis_source: Annotated[
        bool,
        Field(description="Whether this step's narrative text output is forwarded to the synthesis LLM context."),
    ] = True

    ui_pos_x: float = Field(default=0.0, description="X coordinate on the 2D DAG canvas.")
    ui_pos_y: float = Field(default=0.0, description="Y coordinate on the 2D DAG canvas.")

    def extract_variable_references(self) -> list[str]:
        """Extracts dynamic variable references (e.g. $inputs.x, $steps.y) from input_mappings.

        Returns:
            List of variables discovered in mapping.
        """
        refs = []
        for val in self.input_mappings.values():
            if isinstance(val, str) and val.startswith("$"):
                refs.append(val)
        return refs


class Role(V2CoreBase):
    """Role definition that locks physical models and pre_hooks."""

    model_config = ConfigDict(strict=True, extra="forbid")

    id: str = Field(pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$", description="Unique Role ID")
    name: I18nText
    model_role: str = Field(description='Maps to SystemConfig.model_mappings (e.g., "analyst_model").')
    type: str | None = Field(default="role", description="Component type indicator.")
    pre_hooks: list[str] = Field(default_factory=list, description="List of registered hook logic to run BEFORE llm.")
    post_hooks: list[str] = Field(default_factory=list, description="List of registered hook logic to run AFTER llm.")


class QuestionnaireItem(V2CoreBase):
    """A single question definition within a dynamic questionnaire."""

    model_config = ConfigDict(strict=True, extra="forbid")

    question_id: str = Field(description="Unique identifier for the question (e.g., 'q1').")
    question: I18nText = Field(description="Localized question text.")
    type: str = Field(description="Input type, e.g., 'text'.")


class ExpectedInput(V2CoreBase):
    """Definition of an input required by a workflow."""

    model_config = ConfigDict(strict=True, extra="forbid")

    input_key: str = Field(pattern=r"^[A-Za-z0-9_]{1,32}$", description="System identifier for the input.")
    label: I18nText = Field(description="Localized label for the UI.")
    required: bool = Field(description="Whether this input is universally required.")
    is_chat_history: bool = Field(
        default=False, description="If True, routes to ChatParserService for special parsing."
    )
    scan_for_performative_patterns: bool = Field(
        default=False, description="Whether to scan this input for performative AI jargon."
    )
    input_modes: list[str] = Field(default_factory=list, description="Allowed modes: 'file', 'paste', 'questionnaire'.")
    description: I18nText = Field(description="Localized description/help text.")
    ai_description: str | None = Field(
        default=None,
        description="MANDATORY: English cognitive instructions for the LLM. Isolates AI prompt from UI localizations.",
    )
    questionnaire_definition: list[QuestionnaireItem] = Field(
        default_factory=list, description="Definitions if 'questionnaire' is in input_modes."
    )

    @model_validator(mode="after")
    def validate_modes(self) -> ExpectedInput:
        """Strict validation for input modes.

        Raises:
            ValueError: If structure is malformed or internally inconsistent.

        Returns:
            The sanitized ExpectedInput matching schema expectations.
        """
        if not self.input_modes:
            msg = f"ExpectedInput '{self.input_key}' must have at least one input_mode."
            logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise ValueError(msg)

        if "questionnaire" in self.input_modes:
            if self.is_chat_history:
                msg = f"ExpectedInput '{self.input_key}' cannot use 'questionnaire' mode when flagged as chat history."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
            if len(self.input_modes) > 1:
                msg = f"ExpectedInput '{self.input_key}' cannot mix 'questionnaire' with other input modes."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
            if not self.questionnaire_definition:
                msg = f"ExpectedInput '{self.input_key}' uses 'questionnaire' mode but lacks definitions."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
        else:
            if self.questionnaire_definition:
                msg = (
                    f"ExpectedInput '{self.input_key}' cannot have questionnaire_definition "
                    "when 'questionnaire' mode is not active."
                )
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)

        return self


from backend_v2.models.dtos.matrix_scorecard import (  # noqa: F401
    HumanOverrideDTO,
    HumanOverrideRequest,
    MatrixScorecardRowDTO,
    ScorecardAtomDTO,
    TDADlq,
    TDAEvaluated,
    TDAPending,
    TDAStateUnion,
)


class ErrorDetailsDTO(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")
    error_code: Annotated[str, Field(description="Standardized error code, e.g., LLM_TIMEOUT")]
    message: Annotated[str, Field(description="Technical error message or stack trace")]


class HydratedAtomDTO(BaseModel):
    """Static ontology data. Perfectly cacheable.
    Must not contain any dynamic execution-related data.
    """

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")
    sdui_component: Annotated[LaxSDUIComponentType, Field(description="Server-Driven UI hint for frontend.")]
    resolved_claim: Annotated[str, Field(description="Cleaned claim in human language")]
    source_quote: Annotated[str | None, Field(default=None, description="Verbatim original quote")]


class ExtractedValueDTO(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")
    value: str | float | int | bool
    unit: Annotated[str | None, Field(default=None, description="Unit of measurement, e.g., 'tCO2e' or 'EUR'")]


class AtomResultDTO(BaseModel):
    """Dynamic execution data (DAG node)."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")
    tda_id: Annotated[str, Field(description="Opaque ID pointing to the hydrated_references dictionary key")]
    matrix_id: Annotated[
        str | None, Field(default=None, description="Opaque ID of the matrix block that requested this evaluation")
    ] = None
    status: LaxExecutionStatus
    extracted_data: Annotated[
        ExtractedValueDTO | None, Field(default=None, description="Quantitative or isolated result")
    ] = None
    source_quote: Annotated[
        str | None, Field(default=None, description="Verbatim original quote from the document")
    ] = None
    contextual_override: Annotated[
        bool, Field(default=False, description="Allows cognitive override without a verbatim quote")
    ] = False
    evaluation_reasoning: Annotated[
        str | None, Field(default=None, description="Strictly AI cognitive reasoning, no infra errors")
    ] = None
    error_details: Annotated[
        ErrorDetailsDTO | None, Field(default=None, description="Populated only if status is SYSTEM_ERROR")
    ] = None
    extensions: Annotated[
        dict[str, str], Field(default_factory=dict, description="Requested XAI extensions mapping")
    ] = Field(default_factory=dict)

    depends_on_tda_ids: Annotated[list[str], Field(default_factory=list, description="DAG adjacency list")] = Field(
        default_factory=list
    )
    short_circuit_reason_tda_ids: Annotated[list[str], Field(default_factory=list)] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_cognitive_vs_system_state(self) -> Self:
        """Fail-Fast validation for cognitive state consistency."""
        if self.status == ExecutionStatus.FAILED:
            if not self.evaluation_reasoning:
                raise ValueError(f"Reasoning is mandatory for cognitive status {self.status.value}")
            if self.contextual_override:
                object.__setattr__(self, "contextual_override", False)
            if self.source_quote is not None:
                object.__setattr__(self, "source_quote", None)

        elif self.status == ExecutionStatus.PASSED:
            if not self.evaluation_reasoning:
                raise ValueError(f"Reasoning is mandatory for cognitive status {self.status.value}")
            if not self.contextual_override and not self.source_quote:
                raise ValueError("source_quote is mandatory unless contextual_override is True")
            if self.contextual_override and self.source_quote is not None:
                object.__setattr__(self, "source_quote", None)

        elif self.status == ExecutionStatus.SYSTEM_ERROR and not self.error_details:
            raise ValueError("Error details are mandatory when status is SYSTEM_ERROR")

        return self


class ExecutionMetricsDTO(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")
    total_atoms: int
    evaluated: int
    short_circuited_na: int
    duration_ms: Annotated[int, Field(default=0, description="Execution duration in milliseconds for observability")]


class ReportDataDTO(V2CoreBase):
    model_config = ConfigDict(strict=True, extra="forbid")
    workflow_id: str
    execution_id: str = Field(description="The execution's opaque Stripe ID.")
    scoring_strategy: str | None = Field(
        default=None, description="The mathematical strategy used for scoring (e.g. WATERFALL)"
    )
    user_name: str | None = Field(default=None, description="Initiating user's name")
    scoring_engine_name: str | None = Field(default=None, description="Human readable name of the scoring engine")
    strictness_level: int | None = Field(default=None, description="Numeric strictness level (0-100)")
    local_time_str: str | None = Field(default=None, description="Localized time string from the client")
    custom_preface_md: str | None = Field(default=None, description="Custom user preface rendered as Markdown")
    profile_id: str
    profile_name: I18nText | None = Field(default=None)
    profile_description: I18nText | None = Field(
        default=None, description="Detailed profile context mapped from OutputProfile"
    )
    available_profiles: dict[str, I18nText] = Field(default_factory=dict)
    global_score: float | None = Field(
        default=None, description="The mathematical average extracted from the scoring_result hook."
    )
    has_warning: bool = Field(
        default=False, description="Flag indicating if the report generation had non-fatal warnings."
    )

    # Strict Topological DAG Execution Model fields
    global_metrics: ExecutionMetricsDTO | None = Field(default=None)
    inner_sdui_blocks: list[AnySduiBlock] = Field(
        default_factory=list, description="Stores the final structured SDUI blocks."
    )
    results: list[AtomResultDTO] = Field(
        default_factory=list,
        description="SDUI-RULE: Backend must return this list strictly topologically sorted. Frontend does not compute the DAG.",
    )
    hydrated_references: dict[str, HydratedAtomDTO] = Field(
        default_factory=dict, description="O(1) Dictionary: tda_id -> Static text."
    )

    visible_metadata: list[str] = Field(
        default_factory=list, description="Fields visible on the UI and PDF cover header."
    )

    # Execution Diagnostic Metadata
    created_at: datetime | None = None
    org_name: str | None = None
    cost_estimate: float | None = None
    total_tokens: int | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    reasoning_tokens: int | None = None

    # MCP Tool Loop Audit Trail (XAI Evidence for Frontend)
    mcp_tool_audit: list[MCPAuditTrace] = Field(
        default_factory=list, description="Serialized MCPAuditTrace entries for XAI Evidence Box rendering."
    )

    @model_validator(mode="after")
    def enforce_referential_integrity(self) -> Self:
        """FAIL-FAST ARCHITECTURE INVARIANT:
        Ensures that every tda_id present in the results list and dependencies
        actually exists in the hydrated_references dictionary.
        """
        ref_keys = set(self.hydrated_references.keys())

        # Declarative Set Logic
        used_ids = {res.tda_id for res in self.results}
        dep_ids = {dep for res in self.results for dep in res.depends_on_tda_ids}
        sc_ids = {sc for res in self.results for sc in res.short_circuit_reason_tda_ids}

        all_referenced_ids = used_ids | dep_ids | sc_ids
        missing_keys = all_referenced_ids - ref_keys

        if missing_keys:
            raise ValueError(f"Referential Integrity Error: Missing keys in hydrated_references: {missing_keys}")

        return self


class MatrixSynthesisGroup(V2CoreBase):
    """Represents a comparative matrix synthesis group for 2D/3D graphs and multi-matrix synthesis."""

    model_config = ConfigDict(strict=True, extra="forbid")

    id: str = Field(
        default_factory=lambda: f"grp_{uuid.uuid4().hex[:16]}",
        pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$",
        description="Unique Opaque Synthesis Group ID (e.g. grp_440a5fef9331451b)",
    )
    title: I18nText = Field(description="Localized title for the synthesis group")
    target_blocks: list[str] = Field(min_length=1, description="List of prompt block IDs targeted by this group")
    synthesis_directive: str | None = Field(default=None, description="Optional custom synthesis directive")
    view_type: LaxPresetView = Field(
        default=PresetView.METRICS_1D,
        description="UI presentation preset view for this matrix group (e.g. 1d_metrics, 2d_compare, 3d_matrix, text_only).",
    )


class OutputProfile(V2CoreBase):
    """A distinct report variant containing a sequence of layout blocks."""

    model_config = ConfigDict(strict=True, extra="forbid")

    id: str = Field(pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$", description="Unique Profile ID")
    slug: str = Field(min_length=1, pattern=r"^[a-zA-Z0-9_\-]+$", description="Fallback slug identifier")
    workflow_id: str = Field(description="ID of the associated Workflow")
    organization_id: str | None = Field(default=None, description="Tenant organization ID.")
    name: I18nText = Field(description="Localized name of the profile (e.g. {'fi': 'Johdon tiivistelmä'})")
    description: I18nText | None = Field(default=None, description="Detailed profile context")
    user_role_label: I18nText | None = Field(
        default=None, description="Optional localized label prefixing the user role context (e.g., 'Target audience:')."
    )
    custom_preface: I18nText | None = Field(
        default=None, description="Rich text preface shown at the very beginning of the report."
    )
    language: str | None = Field(default=None, description="Target output language.")
    tone_instruction: I18nText | None = Field(default=None, description="Dynamic tone instruction for synthesis.")

    visible_metadata: list[str] = Field(
        default_factory=lambda: ["date", "organization", "user", "scoring_engine", "strictness"],
        description="List of metadata fields visible on the UI and PDF cover header.",
    )
    matrix_visible_columns: list[str] = Field(
        default_factory=lambda: [
            "label",
            "distribution",
            "row_explanation",
            "quotes",
            "normalized_score",
            "score",
        ],
        description="List of column keys visible in the matrix summary table.",
    )
    visible_block_extensions: list[LaxXaiExtensionType] = Field(
        default_factory=list,
        description="Block-level XAI extensions (per-matrix, LLM-produced).",
    )
    visible_workflow_extensions: list[LaxXaiExtensionType] = Field(
        default_factory=list,
        description="Workflow-level global extensions (mathematical engines).",
    )
    max_extension_items: Annotated[
        int,
        Field(
            default=3,
            ge=1,
            le=100,
            description="Max number of items to show per grouped XAI extension.",
        ),
    ] = 3

    display_scale: Annotated[
        LaxDisplayScale,
        Field(
            default=DisplayScale.ORIGINAL,
            description="Selects the source scaling for the scores printed by Blueprint.",
        ),
    ] = DisplayScale.ORIGINAL
    custom_scale_min: Annotated[
        float | None,
        Field(default=None, description="Minimum score boundary when display_scale is CUSTOM."),
    ] = None
    custom_scale_max: Annotated[
        float | None,
        Field(default=None, description="Maximum score boundary when display_scale is CUSTOM."),
    ] = None
    strictness_level: Literal[85, 100] | None = Field(default=None, description="Profile-level strictness override.")
    scoring_strategy: LaxScoringStrategy | None = Field(default=None, description="Profile-level strategy override.")
    synthesis_length_constraint: Annotated[
        int | None,
        Field(default=None, description="Optional length constraint for synthesized text."),
    ] = None
    max_quotes_per_matrix: Annotated[
        int | None,
        Field(default=None, description="Per-profile override for quotes per matrix in explanations."),
    ] = None
    max_unmet_criteria: Annotated[
        int | None,
        Field(default=None, description="Per-profile override for unmet criteria per matrix."),
    ] = None
    target_block_order: Annotated[
        list[LaxTargetBlockType],
        Field(
            default_factory=lambda: [
                TargetBlockType.METADATA_BLOCK,
                TargetBlockType.EXECUTIVE_SUMMARY_BLOCK,
                TargetBlockType.SYNTHESIS_TEXT_BLOCK,
                TargetBlockType.MATRIX_GRAPHS_BLOCK,
                TargetBlockType.GROUPED_EXTENSIONS_BLOCK,
                TargetBlockType.PENALTIES_BLOCK,
                TargetBlockType.MATRIX_SUMMARY_TABLE_BLOCK,
                TargetBlockType.VARIANCE_VALIDATION_BLOCK,
                TargetBlockType.AUTHENTICITY_EVALUATION_BLOCK,
                TargetBlockType.PRINTABLE_SOURCES_BLOCK,
                TargetBlockType.GLOBAL_SCORE_BLOCK,
                TargetBlockType.AUDIT_TRAIL_BLOCK,
            ],
            description=(
                "The exact dynamic block sequence for the SDUI output. Drives the dispatch loop in blueprint.py."
            ),
        ),
    ]
    matrix_synthesis_groups: list[MatrixSynthesisGroup] = Field(
        default_factory=list, description="Optional matrix synthesis groups for 2D/3D comparative graphs."
    )
    content_blocks: list[AnySduiBlock] = Field(
        default_factory=list, description="Base SDUI content blocks predefined by the profile."
    )
    show_sources_summary_box: Annotated[
        bool,
        Field(default=True, description="Whether to show the source verification summary box in the report."),
    ] = True
    sources_display_mode: Annotated[
        LaxSourcesDisplayMode,
        Field(
            default=SourcesDisplayMode.VERIFIED_EVIDENCE,
            description="Display mode for the bibliography and source verification section.",
        ),
    ] = SourcesDisplayMode.VERIFIED_EVIDENCE
    performativity_detector_step_id: str | None = Field(
        default=None, description="Optional step ID for the performativity detector"
    )

    @model_validator(mode="after")
    def validate_matrix_graphs_coherence(self) -> Self:
        """Enforce that matrix_synthesis_groups is populated if MATRIX_GRAPHS_BLOCK is in target_block_order."""
        has_matrix_graphs = any(
            t in (TargetBlockType.MATRIX_GRAPHS_BLOCK, TargetBlockType.MATRIX_GRAPHS_BLOCK.value, "matrix_graphs_block")
            for t in self.target_block_order
        )
        if has_matrix_graphs and len(self.matrix_synthesis_groups) < 1:
            msg = (
                f"OutputProfile '{self.id}': MATRIX_GRAPHS_BLOCK is present in target_block_order "
                "but matrix_synthesis_groups is empty. At least one MatrixSynthesisGroup is required."
            )
            logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def validate_custom_scale_bounds(self) -> Self:
        """Enforce that custom scale bounds are valid when display_scale is CUSTOM."""
        if self.display_scale in (DisplayScale.CUSTOM, "custom"):
            if self.custom_scale_min is None or self.custom_scale_max is None:
                msg = (
                    f"OutputProfile '{self.id}': custom_scale_min and custom_scale_max "
                    "are required when display_scale is CUSTOM."
                )
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
            if self.custom_scale_max <= self.custom_scale_min:
                msg = (
                    f"OutputProfile '{self.id}': custom_scale_max ({self.custom_scale_max}) "
                    f"must be strictly greater than custom_scale_min ({self.custom_scale_min})."
                )
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
        return self

    @property
    def requires_executive_synthesis(self) -> bool:
        """Check if executive summary synthesis is requested in target block order."""
        return any(
            t
            in (
                TargetBlockType.EXECUTIVE_SUMMARY_BLOCK,
                TargetBlockType.EXECUTIVE_SUMMARY_BLOCK.value,
                "executive_summary_block",
            )
            for t in self.target_block_order
        )

    @property
    def requires_group_synthesis(self) -> bool:
        """Check if comparative matrix groups synthesis is requested."""
        return (
            any(
                t
                in (
                    TargetBlockType.MATRIX_GRAPHS_BLOCK,
                    TargetBlockType.MATRIX_GRAPHS_BLOCK.value,
                    "matrix_graphs_block",
                )
                for t in self.target_block_order
            )
            and len(self.matrix_synthesis_groups) > 0
        )

    @property
    def requires_row_explanations(self) -> bool:
        """Check if row explanations are configured in visible matrix columns."""
        if not self.matrix_visible_columns:
            return False
        return "row_explanation" in self.matrix_visible_columns

    @property
    def is_synthesis_expected(self) -> bool:
        """Check if any synthesis phase generation is expected for this profile."""
        return self.requires_executive_synthesis or self.requires_group_synthesis or self.requires_row_explanations


class Workflow(V2CoreBase):
    """Dynamic Directed Acyclic Graph orchestrator model."""

    model_config = ConfigDict(strict=True, extra="forbid")

    id: str = Field(pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$", description="Unique Workflow ID")
    slug: str
    name: I18nText | str
    description: I18nText | str
    status: str
    version: int
    is_public: bool = Field(default=False)
    organization_id: str | None = Field(default=None)
    ui_schema: dict[str, Any] = Field(default_factory=dict)
    default_profile_id: str = Field(description="The ID of the default output profile to use.")
    mcp_gateway_id: str | None = Field(
        default="sys_8172bda70c8641c5",
        pattern=r"^sys_[a-fA-F0-9]{16,32}$",
        description="The system_config ID of the MCP gateways configuration attached to this workflow.",
    )
    default_strictness_level: int = Field(
        default=StrictnessAnchor.STANDARD.value, ge=0, le=100, description="Fallback strictness level."
    )
    default_scoring_strategy: LaxScoringStrategy = Field(
        default=ScoringStrategy.AVERAGE, description="Fallback strategy."
    )
    enable_contextual_overrides: bool = Field(
        default=False,
        description="Global flag to enable contextual overrides across assertions.",
    )
    enable_semantic_smoothing: bool = Field(
        default=False,
        description="If True, uses SpaCy to fix hyphenations and merge broken PDF lines into cohesive semantic sentences.",
    )
    enable_eager_anonymization: bool = Field(
        default=False,
        description="If True, Microsoft Presidio will mask all PII data from raw inputs before they enter the system state.",
    )
    system_audit_trail: bool = Field(
        default=False,
        description="If True, activates the background XAI Citation Extraction tracking mechanism.",
    )
    expected_inputs: list[ExpectedInput] = Field(
        default_factory=list,
        description="List of dynamic expected inputs required by the workflow",
    )
    steps: list[StepRule] = Field(default_factory=list)
    allowed_exports: Annotated[
        list[Literal["pdf", "docx", "raw_json", "xlsx"]],
        Field(description="Supported export file formats for this workflow."),
    ]
    historical_context_mode: Annotated[
        LaxHistoricalContextMode,
        Field(description="Mode for fetching historical context at workflow level."),
    ]

    @model_validator(mode="after")
    def validate_dag_integrity(self) -> Workflow:
        """Enforces Directed Acyclic Graph (DAG) structural integrity.

        Raises:
            AppException: If structure is malformed or internally inconsistent.

        Returns:
            The sanitized Workflow matching schema expectations.
        """
        step_ids = {step.id for step in self.steps}
        graph: dict[str, list[str]] = {step.id: [] for step in self.steps}

        # 1. Orphan Reference Check
        for step in self.steps:
            for dep in step.depends_on:
                if dep not in step_ids:
                    msg = f"Step '{step.id}' depends on '{dep}', which does not exist in this workflow."
                    logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                    raise ValueError(msg)
                graph[step.id].append(dep)

        # 2. Cycle Detection (DFS)
        visited = set()
        rec_stack = set()

        def is_cyclic(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph[node]:
                if neighbor not in visited:
                    if is_cyclic(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for node in step_ids:
            if node not in visited:
                if is_cyclic(node):
                    msg = (
                        f"Circular dependency detected involving step '{node}'. "
                        "Workflows must be strict Directed Acyclic Graphs (DAG)."
                    )
                    logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                    raise ValueError(msg)

        return self

    def get_allowed_layout_targets(self, hydrated_steps: list[Step]) -> set[str]:
        """Calculates all allowed layout targets including system blocks.

        Args:
            hydrated_steps: List of full Step objects from the database.

        Returns:
            A set of allowed block IDs and system TargetBlockTypes.
        """
        allowed_blocks = set()

        # 1. Add blocks from the hydrated steps that belong to this workflow
        task_blueprints = {rule.task_blueprint for rule in self.steps}
        for step in hydrated_steps:
            if step.id in task_blueprints:
                if step.role_block_id:
                    allowed_blocks.add(step.role_block_id)
                if step.extraction_protocol_block_id:
                    allowed_blocks.add(step.extraction_protocol_block_id)
                if step.criteria_block_ids:
                    allowed_blocks.update(step.criteria_block_ids)

        # 2. Add system blocks natively supported by the architecture
        allowed_blocks.update([e.value for e in TargetBlockType])

        return allowed_blocks


class FrozenContext(V2CoreBase):
    """Deep copy of context state at execution time for auditability."""

    model_config = ConfigDict(strict=True, extra="forbid")

    compiled_prompts: dict[str, str] = Field(default_factory=dict, description="Prompts sent to LLM.")
    injected_theory: dict[str, Any] = Field(default_factory=dict, description="Fetched theory texts.")
    generated_schemas: dict[str, dict[str, Any]] = Field(default_factory=dict, description="JSON schemas used.")
    ui_hints_snapshot: dict[str, DataDictionaryField] = Field(
        default_factory=dict, description="UI rendering instructions."
    )
    mcp_tool_audit: list[MCPAuditTrace] = Field(
        default_factory=list, description="Immutable log of all external MCP tool calls made during execution."
    )


class ExecutionCreate(V2CoreBase):
    """Schema for initiating a new workflow execution."""

    model_config = ConfigDict(strict=True, extra="forbid")

    workflow_id: str = Field(description="ID of the workflow to execute")
    target_locale: str = Field(
        description="Desired target locale for output generated by the workflow "
        "(e.g., 'fi'). Must be explicitly provided."
    )
    profile_id: str | None = Field(
        default=None,
        description=("Optional Opaque ID of the Output Profile to apply. If omitted, fallback to workflow default."),
    )
    matrix_sampling_strategy: Annotated[
        int,
        Field(
            default_factory=lambda: get_settings().matrix_sampling_limit,
            description=(
                "Explicit dynamic strategy for Matrix Flattening. Defaulted from ALL to "
                "10 locally to mitigate LLM JSON schema context limits."
            ),
        ),
    ]
    raw_inputs: WorkflowInputsIngress = Field(
        default_factory=lambda: WorkflowInputsIngress(), description="User provided raw inputs"
    )

    @model_validator(mode="before")
    @classmethod
    def _resolve_matrix_sampling_strategy(cls, data: Any) -> Any:
        """Resolve matrix_sampling_strategy if passed explicitly as None."""
        if isinstance(data, dict):  # noqa: QGR012 [REASON: Pydantic before validator raw ingress coercion]
            if "matrix_sampling_strategy" in data and data["matrix_sampling_strategy"] is None:
                data["matrix_sampling_strategy"] = get_settings().matrix_sampling_limit
        return data


class ExecutionStepState(V2CoreBase):
    """Real-time status tracking for a single DAG node."""

    model_config = ConfigDict(strict=True, extra="forbid")

    id: str = Field(pattern=r"^([a-z0-9_]{2,15})_[a-zA-Z0-9_-]+$", description="Step ID")
    label: str = Field(description="Localized label for UI tracking")
    status: LaxExecutionStatus = Field(
        default=ExecutionStatus.PENDING, description="Status: pending, running, passed, failed"
    )
    last_error: str | None = Field(default=None, description="Error message if the step failed")
    message_code: str | None = Field(default=None, description="Optional UX message code for SSE")
    scorecard_atoms: dict[str, ScorecardAtomDTO] = Field(
        default_factory=dict, description="Presentation atoms including potential human overrides."
    )


class ExtensionMetricsDTO(V2CoreBase):
    """Pre-calculated numeric or boolean metrics for UI adapters."""

    model_config = ConfigDict(strict=True, extra="forbid")

    authenticity_score: float | None = None
    performative_phrases_count: float | None = None
    variance_score: float | None = None
    alignment_verdict: str | None = None


class RenderedSynthesisCache(V2CoreBase):
    """Cached synthesis results tied to a specific OutputProfile ID."""

    model_config = ConfigDict(strict=True, extra="forbid")

    section_syntheses: dict[str, list[AnySduiBlock]] = Field(
        default_factory=dict, description="Mapping of layout ID to LLM generated Section-Level synthesis blocks"
    )
    row_explanations: dict[str, str] = Field(
        default_factory=dict, description="Synthesized row explanations by matrix ID"
    )
    row_curated_quotes: dict[str, list[str]] = Field(default_factory=dict, description="Curated quotes by matrix ID")
    cited_sources: list[str] = Field(default_factory=list, description="Citations used in this profile's synthesis")
    xai_highlights: list[XaiHighlightItem] = Field(
        default_factory=list, description="Synthesized XAI highlights and tips"
    )
    user_role: str | None = Field(default=None, description="User role")
    user_role_justification: str | None = Field(default=None, description="User role justification")
    extension_metrics: ExtensionMetricsDTO | None = Field(
        default=None, description="Pre-calculated numeric or boolean metrics for UI adapters"
    )
    data_starvation: DataStarvationEvent | None = Field(
        default=None, description="Domain event indicating synthesis short-circuit due to atom starvation"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExecutionRecord(ExecutionCoreFields):
    """Record of a workflow execution, including the frozen context and results."""

    model_config = ConfigDict(strict=True, extra="forbid")

    if TYPE_CHECKING:
        status: LaxExecutionStatus = Field(default=ExecutionStatus.PENDING)
        target_locale: str = Field(...)
        execution_trace: list[ErrorTraceEvent | TombstoneEvent | TraceEvent] = Field(default_factory=list)
        execution_trace_storage_path: str | None = Field(default=None)
        context_variables: dict[str, Any] = Field(default_factory=dict)
        context_variables_storage_path: str | None = Field(default=None)

    id: str = Field(pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$", description="Execution ID, usually a uuid")
    workflow_id: str = Field(description="Workflow ID")
    # Phase 1: status and target_locale are inherited from ExecutionCoreFields (LaxExecutionStatus SSOT).
    active_profile_id: str | None = Field(
        default=None, description="The ID of the output profile selected for formatting and printing."
    )
    raw_inputs: WorkflowInputs = Field(default_factory=lambda: WorkflowInputs(), description="Raw user inputs by role")
    frozen_context: FrozenContext = Field(default_factory=FrozenContext, description="Immutable snapshot of context")
    frozen_context_storage_path: str | None = Field(
        default=None, description="Optional path to Blob Storage offloaded Frozen Context JSON"
    )
    # Phase 1: execution_trace, execution_trace_storage_path, context_variables,
    # context_variables_storage_path are inherited from ExecutionCoreFields (SSOT).
    pdf_report_path: str | None = Field(default=None, description="Path to the generated PDF Execution Report.")
    output_profile_id: str | None = Field(
        default=None, description="Target profile ID for formatting instructions and synthesis."
    )
    step_states: dict[str, ExecutionStepState] = Field(
        default_factory=dict, description="Real-time status tracking for DAG nodes"
    )
    profile_syntheses: dict[str, RenderedSynthesisCache] = Field(
        default_factory=dict, description="Multi-profile synthesis caching"
    )
    source_identity_manifest: dict[str, str] = Field(
        default_factory=dict, description="O(1) Snapshot mapping Opaque ID to Display Name for inputs."
    )
    is_resumable: bool = Field(
        default=False, description="Dynamic flag indicating if a failed/pending execution can be safely resumed."
    )
    cumulative_synthesis_tokens: int = Field(default=0, description="Cumulative tokens used across all synthesis runs.")
    cumulative_synthesis_cost: float = Field(
        default=0.0, description="Cumulative cost in USD across all synthesis runs."
    )

    duration_ms: int = Field(default=0, description="Total execution duration in milliseconds")
    cost_estimate: float = Field(default=0.0, description="Estimated total cost of the execution in USD")
    models_used: dict[str, int] = Field(
        default_factory=dict, description="Dictionary of models used and their usage count/tokens"
    )
    metadata: ExecutionMetadata = Field(
        description="Strictly typed metadata for the execution",
    )
    error: str | None = Field(default=None, description="Error message if failed")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="UTC creation timestamp"
    )
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="UTC update timestamp")
    completed_at: datetime | None = Field(default=None, description="UTC completion timestamp")
    created_by: str | None = Field(default=None, description="ID of the user who started the execution")
    organization_id: str | None = Field(default=None, description="ID of the organization for this execution")


class JobAcceptedDTO(V2CoreBase):
    """Omni-channel render endpoint accepted response."""

    model_config = ConfigDict(strict=True, extra="forbid")

    status: str
    message: str
    execution_id: str


class EvidenceRejectionRequest(V2CoreBase):
    """Request DTO for rejecting a specific evidence quote."""

    model_config = ConfigDict(strict=True, extra="forbid")

    rejection_reason: str = Field(description="Reason for rejecting the evidence quote.")


WorkflowSchemaResponse = dict[str, Any]


class BaseMatrixXAI(BaseModel):
    """Pydantic model for matrix XAI qualitative extensions without physical extraction guarantees."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    semantic_reasoning: str = Field(
        default="",
        description="Matrix-level assessment explanation.",
    )


class BaseTDAExtraction(BaseModel):
    """Core Pydantic model for Micro-CoT extraction with deterministic cross-validation."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    @field_validator("exact_quotes", mode="before")
    @classmethod
    def _coerce_exact_quotes(cls, v: Any) -> Any:
        if v is None:
            return []
        return v

    exact_quotes: list[LLMExtractedQuote] = Field(
        default_factory=list,
        max_length=3,
        description="List of verbatim quotes from original text.",
    )
    localized_anchors_found: list[str] = Field(
        max_length=15, description="Keywords in target language mapping English rule."
    )
    contextual_override: bool = Field(description="Escape hatch for implicit matches.")
    semantic_reasoning: str = Field(description="Mapping logic explanation in target language.")

    @model_validator(mode="after")
    def validate_override_logic(self) -> Self:
        """Validates the consistency of the extraction rules after typed hydration.

        Raises:
            ValueError: If structure is malformed or internally inconsistent.

        Returns:
            The sanitized model instance matching schema expectations.
        """
        if self.contextual_override:
            if self.exact_quotes:
                raise ValueError("contextual_override=True cannot be combined with exact_quotes")
        else:
            for q in self.exact_quotes:
                if q.text == "[CONTEXTUAL_OVERRIDE_APPLIED]":
                    msg = (
                        "Cross-validation failed: exact_quotes cannot contain "
                        "'[CONTEXTUAL_OVERRIDE_APPLIED]' if contextual_override is False."
                    )
                    logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                    raise ValueError(msg)
        return self


import backend_v2.models.view.sdui as sdui_mod
from backend_v2.models.domain.inputs import WorkflowInputs, WorkflowInputsIngress
from backend_v2.models.dtos.dag_models import CausalEdge
from backend_v2.models.dtos.trace import DataStarvationEvent
from backend_v2.models.execution_core import ExecutionCoreFields
from backend_v2.models.view.sdui import AnySduiBlock

_sdui_localns = {
    "MatrixScorecardRowDTO": MatrixScorecardRowDTO,
    "LaxXaiExtensionType": LaxXaiExtensionType,
    "AnySduiBlock": AnySduiBlock,
    "MCPAuditTrace": MCPAuditTrace,
}
sdui_mod.SduiRadarChartBlock.model_rebuild(_types_namespace=_sdui_localns)
sdui_mod.SduiScatterPlotBlock.model_rebuild(_types_namespace=_sdui_localns)
sdui_mod.SduiMatrixTableBlock.model_rebuild(_types_namespace=_sdui_localns)
sdui_mod.SduiMetrics1DBlock.model_rebuild(_types_namespace=_sdui_localns)
sdui_mod.SduiGridBlock.model_rebuild(_types_namespace=_sdui_localns)

RenderedSynthesisCache.model_rebuild(
    _types_namespace={
        "DataStarvationEvent": DataStarvationEvent,
        "AnySduiBlock": AnySduiBlock,
    }
)
ReportDataDTO.model_rebuild(
    _types_namespace={
        "AnySduiBlock": AnySduiBlock,
    }
)
MatrixScorecardRowDTO.model_rebuild(
    _types_namespace={
        "AnySduiBlock": AnySduiBlock,
        "MCPAuditTrace": MCPAuditTrace,
    }
)
ExecutionCreate.model_rebuild()
TDAAssertion.model_rebuild(_types_namespace={"CausalEdge": CausalEdge})

import backend_v2.models.state  # noqa: F401, E402
