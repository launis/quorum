"""V2 Core Models for Backend.

Implements dynamic, append-only, and I18N-capable models according to V2 specs.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Literal, cast

if TYPE_CHECKING:
    from backend_v2.models.state import ErrorTraceEvent, TombstoneEvent, TraceEvent

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend_v2.exceptions import ErrorCodes
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.inputs import WorkflowInputs, WorkflowInputsIngress
from backend_v2.models.dtos.synthesis import XaiHighlightItem
from backend_v2.models.enums import (
    BlockDataType,
    ComponentType,
    ExecutionStatus,
    HistoricalContextMode,
    LaxBlockDataType,
    LaxComponentType,
    LaxExecutionStatus,
    LaxHistoricalContextMode,
    LaxPromptBlockCategory,
    LaxScoringStrategy,
    LaxXaiExtensionType,
    ScoringStrategy,
    SystemConcurrency,
)
from backend_v2.models.execution_core import ExecutionCoreFields

logger = logging.getLogger(__name__)


__all__ = [
    "I18nText",
    "ModelProfile",
    "SystemConfigModelRegistry",
    "SystemConfigMCPGateways",
    "AllowedMCPTool",
    "MCPAuditTrace",
    "Step",
    "StepRule",
    "Role",
    "Workflow",
    "ComponentType",
    "BlockDataType",
    "ExecutionStatus",
    "ExecutionCoreFields",
    "FrozenContext",
    "ExecutionCreate",
    "ExecutionRecord",
    "ExpectedInput",
    "WorkflowInputs",
    "QuestionnaireItem",
    "OutputLayoutBlock",
    "SynthesisConfigDTO",
    "OutputProfile",
    "EmbeddedOutputProfile",
    "JobAcceptedDTO",
    "TDAAssertion",
    "MatrixClaim",
    "BaseTDAExtraction",
]


class I18nText(V2CoreBase):
    """V2 Strict: Frontend no-string mandate requires all localized text to be structured.

    Attributes:
        default_locale: The default locale used if a translation is missing.
        translations: Dictionary mapping locale code to translated string.
    """

    default_locale: str = Field(description="The default locale used if a translation is missing.")
    translations: dict[str, str] = Field(
        default_factory=dict,
        description="Dictionary mapping locale code to translated string (e.g. {'fi': 'Teksti', 'en': 'Text'}).",
    )

    @model_validator(mode="after")
    def validate_i18n(self) -> I18nText:
        """Validates that English translation is always present.

        Raises:
            ValueError: If the English translation is missing or empty.

        Returns:
            The validated I18nText instance.
        """
        # Enforce English-Only Mandate: 'en' translation must ALWAYS exist.
        en_trans = self.translations.get("en")
        if not en_trans or not en_trans.strip():
            msg = (
                "I18nText must contain a valid English ('en') translation due to the "
                f"English-Only Mandate. Payload: {self.translations}"
            )
            raise ValueError(msg)

        if self.default_locale not in self.translations or not self.translations.get(self.default_locale):
            logger.warning(
                "[V2Core] I18nText missing translation for default_locale '%s'. Will fallback to 'en'.",
                self.default_locale,
            )

        return self

    def resolve(self, target_locale: str | None = None) -> str:
        """Strictly typed method to resolve the best localization, avoiding 'naked dict' fallback logic.

        Args:
            target_locale: The requested locale code.

        Returns:
            The resolved localized string.
        """
        if not self.translations:
            return ""

        if target_locale:
            target_lang = target_locale.split("-")[0].lower()
            if target_lang in self.translations:
                return self.translations[target_lang]

        if self.default_locale in self.translations:
            return self.translations[self.default_locale]

        return self.translations["en"]

    def get(self, lang_code: str, fallback: str = "") -> str:
        """Extracts the localized string safely for templates (Jinja2) and programmatic access.

        Args:
            lang_code: Target locale code.
            fallback: Default value if unable to resolve.

        Returns:
            The resolved string or fallback value.
        """
        if not self.translations:
            return fallback

        if lang_code in self.translations and self.translations[lang_code].strip():
            return self.translations[lang_code]
        if self.default_locale in self.translations and self.translations[self.default_locale].strip():
            return self.translations[self.default_locale]

        return self.translations["en"]


class TheoryGrounding(V2CoreBase):
    """Used in PromptBlock to bind criteria to organizational truth.

    Attributes:
        source_url: URL or reference to the source material.
        citation_reference: Specific section or phrase to cite from the source.
    """

    source_url: str = Field(description="URL or reference to the source material.")
    citation_reference: str = Field(description="Specific section or phrase to cite from the source.")


class TDAAssertion(V2CoreBase):
    """Deterministic rule evaluated by the backend.

    Attributes:
        tda_id: Opaque Stripe ID for this assertion.
        ai_rule_description: Strict enforcement rule.
        inverse_evidence: If True, acts as a poison/penalty detector.
        aggregation_mode: Aggregation constraint.
        evaluation_track: Decoupled evaluation track.
        facts_to_find: The list of facts to extract for this assertion.
        logical_expression: Whitelisted Boolean logical expression using extracted facts.
        allow_contextual_override: If True, allows overriding this assertion with a contextual excuse.
        high_entropy: If True, enables multi-agent ensemble majority voting for this assertion.
    """

    tda_id: str = Field(
        default_factory=lambda: f"tda_{uuid.uuid4().hex}",
        pattern=r"^tda_[a-f0-9]{32}$",
        description="Opaque Stripe ID for this assertion.",
    )
    ai_rule_description: str = Field(description="Strict enforcement rule.")
    inverse_evidence: bool = Field(description="If True, acts as a poison/penalty detector.")
    aggregation_mode: Literal["EXISTS", "ALL_MUST_COMPLY"] = Field(description="Aggregation constraint.")

    # Phase 1, Milestone 1: Add new properties for decoupled TDA
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
    allow_contextual_override: bool = Field(
        default=False,
        description="If True, allows overriding this assertion with a contextual excuse.",
    )
    high_entropy: bool = Field(
        default=False,
        description="If True, enables multi-agent ensemble majority voting for this assertion.",
    )

    @model_validator(mode="after")
    def validate_math_logic(self) -> TDAAssertion:
        """Validates the consistency of the assertion constraints.

        Raises:
            ValueError: If constraints are mathematically or logically invalid.

        Returns:
            The validated assertion.
        """
        if self.inverse_evidence and self.aggregation_mode == "ALL_MUST_COMPLY":
            raise ValueError("Käänteinen sääntö (myrkyn etsintä) vaatii EHDOTTOMASTI 'EXISTS' -aggregaation...")

        # Phase 1, Milestone 1: Enforce strict dual-track TDA validations
        if self.evaluation_track == "EXTRACTIVE_SENSOR":
            if not self.facts_to_find:
                raise ValueError("EXTRACTIVE_SENSOR -rata vaatii vähintään yhden haettavan faktan (facts_to_find).")
            if not self.logical_expression or not self.logical_expression.strip():
                raise ValueError(
                    "EXTRACTIVE_SENSOR -rata vaatii määrittämään loogisen lausekkeen (logical_expression)."
                )
        return self


class MatrixClaim(V2CoreBase):
    """Represents a single behavioral claim with an AI evaluation directive.

    Attributes:
        label: User-facing empirical claim.
        ai_description: Specific AI enforcement rule for this claim.
        tda_assertions: Test-Driven Assertion rules explicitly set by experts.
    """

    label: I18nText = Field(description="User-facing empirical claim.")
    ai_description: str = Field(description="Specific AI enforcement rule for this claim.")
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

    score: int = Field(description="Numerical value of the scale point.")
    name: I18nText | None = Field(default=None, description="Optional name for the scale point (e.g., 'Excellent').")
    ai_label: str = Field(
        description="Short uppercase AI mnemonic replacing English target label, e.g. CATASTROPHIC FAILURE"
    )
    claims: list[MatrixClaim] = Field(
        default_factory=list, description="List of behavioral claims/criteria for this score."
    )


class PromptBlock(V2CoreBase):
    """V2 PromptBlock representation.
    Fuses legacy Components and Matrices into a unified directive model.

    Attributes:
        id: Unique identifier for the prompt block.
        slug: URL routing helper field.
        organization_id: Tenant organization ID.
        label: Localizable label for the UI.
        description: Localizable description or help text for the UI.
        ai_description: MANDATORY: English cognitive instructions for the LLM.
        category_id: Categorization identifier.
        is_evaluative: Whether this matrix is mathematically commensurate.
        type: Data type of the expected extracted value.
        allow_decimals: Whether float types allow decimals in validation.
        output_extensions: List of requested XAI output extensions.
        execution_persona: Defines the global system prompt rules applied to this block.
        theory_grounding: Fetches and injects source theory as <theory_context>.
        scale_min: Minimum score for the scales matrix.
        scale_max: Maximum score for the scales matrix.
        scales: BARS scale definitions with scores and localized claims.
        rows: Optional rows for grid matrices.
        columns: Optional columns for grid matrices.
        computed_min: Dynamically computed absolute minimum score.
        computed_max: Dynamically computed absolute maximum score.
    """

    id: str = Field(
        pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$",
        description=(
            "Unique identifier for the prompt block. MUST be a valid Stripe Pattern Opaque ID "
            "to guarantee dynamic schema compilation."
        ),
    )
    slug: str = Field(description="URL routing helper field. Strictly no data relation role.")
    organization_id: str | None = Field(default=None, description="Tenant organization ID.")
    label: I18nText = Field(description="Localizable label for the UI.")
    description: I18nText = Field(description="Localizable description or help text for the UI.")
    ai_description: str | None = Field(
        default=None,
        description=(
            "MANDATORY: English cognitive instructions for the LLM. Completely isolates "
            "AI prompt from UI localizations."
        ),
    )
    category_id: LaxPromptBlockCategory = Field(
        description="Categorization identifier (e.g. 'scientific_theory', 'system_rule')."
    )
    is_evaluative: bool = Field(
        default=True,
        description="Whether this matrix is mathematically commensurate and contributes to the global average score.",
    )
    type: LaxBlockDataType = Field(description="Data type of the expected extracted value.")
    allow_decimals: bool = Field(default=False, description="Whether float types allow decimals in validation.")
    output_extensions: list[str] = Field(
        default_factory=list,
        description="List of requested XAI output extensions (e.g. 'justification', 'risk_flag').",
    )
    # Epic 55: execution_persona field REMOVED. execution_persona_block_id now resides on the Step model.
    theory_grounding: TheoryGrounding | None = Field(
        default=None,
        description="If provided, fetches and injects source theory as <theory_context> to prompt.",
    )
    scale_min: int | None = Field(
        default=None, description="Minimum score for the scales matrix. Required if scales are present."
    )
    scale_max: int | None = Field(
        default=None, description="Maximum score for the scales matrix. Required if scales are present."
    )
    scales: list[MatrixScale] | None = Field(
        default=None,
        description="BARS scale definitions with scores and localized claims. If provided, must not be empty.",
    )
    rows: list[MatrixRow] | None = Field(default=None, description="Optional rows for grid matrices.")
    columns: list[I18nText] | None = Field(default=None, description="Optional columns for grid matrices.")

    computed_min: int | None = Field(default=None, description="Dynamically computed absolute minimum score")
    computed_max: int | None = Field(default=None, description="Dynamically computed absolute maximum score")

    @model_validator(mode="before")
    @classmethod
    def pre_validate_block_consistency(cls, data: Any) -> Any:
        """Strict validation for PromptBlock relations and logical constraints.

        Args:
            data: Unvalidated dictionary input mapping.

        Raises:
            ValueError: If structure is malformed or internally inconsistent.

        Returns:
            The sanitized dictionary matching schema expectations.
        """
        if not isinstance(data, dict):
            return data

        new_min = None
        new_max = None
        scales = data.get("scales")
        if scales and isinstance(scales, list) and len(scales) > 0:
            scores = []
            for s in scales:
                if isinstance(s, dict) and "score" in s:
                    scores.append(s["score"])
                elif hasattr(s, "score"):
                    scores.append(s.score)
            if scores:
                new_min = min(scores)
                new_max = max(scores)

        allow_decimals = data.get("allow_decimals", False)
        block_type = data.get("type")
        block_id = data.get("id", "Unknown")

        valid_numeric = ["float", "int", "string", BlockDataType.FLOAT, BlockDataType.INT, BlockDataType.STRING]
        if allow_decimals and block_type not in valid_numeric:
            msg = f"PromptBlock '{block_id}': allow_decimals is only valid for numeric logic."
            raise ValueError(msg)

        if scales is not None:
            scale_min = data.get("scale_min")
            scale_max = data.get("scale_max")
            if scale_min is not None and scale_max is not None:
                if scale_max <= scale_min:
                    msg = (
                        f"PromptBlock '{block_id}': scale_max ({scale_max}) "
                        f"on oltava suurempi kuin scale_min ({scale_min})."
                    )
                    raise ValueError(msg)
            if len(scales) == 0:
                msg = (
                    f"PromptBlock '{block_id}': Jos scales on valittu käyttöön, "
                    "siellä on pakko olla vähintään yksi MatrixScale (len > 0)."
                )
                raise ValueError(msg)
            for scale in scales:
                claims = scale.get("claims") if isinstance(scale, dict) else getattr(scale, "claims", None)
                if not claims or len(claims) == 0:
                    score_val = scale.get("score") if isinstance(scale, dict) else getattr(scale, "score", None)
                    msg = (
                        f"PromptBlock '{block_id}' / Scale '{score_val}': "
                        "Jokaisella scorella pitää olla vähintään yksi claim."
                    )
                    logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                    raise ValueError(msg)

        if new_min is not None:
            data["computed_min"] = new_min
        if new_max is not None:
            data["computed_max"] = new_max

        category_id = data.get("category_id")
        if category_id == "matrix":
            if data.get("computed_min") is None or data.get("computed_max") is None:
                msg = (
                    f"PromptBlock '{block_id}': Kun category_id on 'matrix', "
                    "computed_min ja computed_max on pakko pystyä laskemaan (scales-taulukosta)."
                )
                raise ValueError(msg)

        return data


class ChatMessageDTO(V2CoreBase):
    """Schema for a single parsed chat message.

    Attributes:
        role: The role of the speaker (e.g. 'user' or 'ai').
        content: The message text.
    """

    role: str = Field(description="The role of the speaker (e.g. 'user' or 'ai').")
    content: str = Field(description="The message text.")


class ChatHistoryDTO(V2CoreBase):
    """Strict schema for a complete parsed chat sequence.

    Attributes:
        conversation: List of messages in chronological order.
    """

    conversation: list[ChatMessageDTO] = Field(description="List of messages in chronological order.")


class DataDictionaryField(V2CoreBase):
    """UI Hints mapping for dynamic form generation (SDUI)."""

    field_id: str
    component_type: LaxComponentType = Field(description="E.g., 'slider', 'text_input', 'dropdown'")
    options: list[dict[str, Any]] | None = None
    validation_rules: dict[str, Any] | None = None


class ModelProfile(V2CoreBase):
    """A flattened physical AI model representation."""

    provider: str = Field(description="E.g., 'google', 'openai'")
    model_name: str = Field(description="The underlying API model name")
    temperature: float | None = Field(default=None, description="Generation temperature")
    top_p: float | None = Field(default=None, description="Nucleus sampling probability")
    top_k: int | None = Field(default=None, description="Top-K sampling")
    tpm_limit: int | None = Field(default=None, description="Tokens per minute limit")
    rpm_limit: int | None = Field(default=None, description="Requests per minute limit")
    max_tokens: int | None = Field(default=None, description="Max generated tokens")
    allowed_tools: list[str] = Field(default_factory=list, description="Enabled tools")
    supports_grounding: bool = Field(default=False, description="Supports Google Search Grounding")
    api_key: str | None = Field(default=None, description="Optional override API key")
    parsing_mode: str | None = Field(default=None, description="Parser logic flag (e.g. 'STRUCTURED_JSON')")
    caching_strategy: str | None = Field(
        default=None, description="Cache strategy identifier (e.g. 'anthropic_ephemeral')"
    )
    # Phase 1, Milestone 1: Add additional_params dict field to ModelProfile
    additional_params: dict[str, Any] = Field(
        default_factory=dict, description="Additional provider-specific parameters."
    )
    is_active: bool = Field(default=True, description="Whether the model is actively available")


class SystemConfigModelRegistry(V2CoreBase):
    """V2 Flattened Model Registry System Config."""

    id: str = Field(pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$", description="System config ID")
    slug: str = Field(description="Slug identifier")
    type: str = Field(description="Type of config")
    models: dict[str, ModelProfile] = Field(
        description="Dictionary mapping generic role names to specific ModelProfiles"
    )


class AllowedMCPTool(V2CoreBase):
    """Declares a single MCP tool available for LLM function calling."""

    tool_id: str = Field(description="Unique slug (e.g. 'mcp_tavily_search').")
    name: I18nText = Field(description="Localized display name.")
    description: str = Field(description="English-only LLM description for function calling schema.")
    input_schema: dict[str, Any] = Field(
        default_factory=dict, description="JSON Schema defining the tool's input parameters."
    )


class MCPAuditTrace(V2CoreBase):
    """Immutable audit log entry for a single MCP tool invocation."""

    id: str | None = Field(default=None, description="Unique identifier for the trace injected by the driver.")
    tool_id: str = Field(description="Which tool was called.")
    step_name: str = Field(description="DAG step that triggered the call.")
    query: str = Field(description="The search query or tool input.")
    response_summary: str = Field(default="", description="Extracted text summary.")
    source_urls: list[str] = Field(default_factory=list, description="Source URLs returned.")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="UTC timestamp of the tool call."
    )
    duration_ms: int = Field(default=0, description="Round-trip latency in milliseconds.")


class SystemConfigMCPGateways(V2CoreBase):
    """System-level registry of available MCP tool gateways."""

    id: str = Field(pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$", description="System config ID")
    slug: str = Field(description="Slug identifier.")
    type: str = Field(description="Config type discriminator.")
    tools: list[AllowedMCPTool] = Field(
        default_factory=list, description="Registry of all available MCP tools in the system."
    )


class Step(V2CoreBase):
    """Isolated, reusable orchestrator cognitive module (e.g. Guard or step_input_processing).
    Formerly known as TaskBlueprint.
    """

    id: str = Field(pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$", description="Unique UUID for storage optionally")
    slug: str = Field(description="Human-readable identifier (e.g., 'step_guard')")
    organization_id: str | None = Field(default=None, description="Tenant organization ID.")
    name: I18nText = Field(description="Localized step name")
    description: I18nText | None = Field(default=None, description="Detailed step context")
    type: Literal["llm", "logic"] = Field(default="llm", description="Step execution type (llm or native logic)")
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

    @model_validator(mode="after")
    def validate_step_consistency(self) -> Step:
        """Strict fail-fast validation to ensure Step is structurally complete.

        Raises:
            ValueError: If structure is malformed or internally inconsistent.

        Returns:
            The sanitized Step matching schema expectations.
        """
        if self.type == "llm":
            if not self.model_strategy:
                msg = f"LLM Step '{self.slug}' must declare an explicit model_strategy (Zero-Fallback Rule)."
                raise ValueError(msg)
            if not self.criteria_block_ids:
                msg = f"LLM Step '{self.slug}' must define at least one criteria_block_id."
                raise ValueError(msg)
            if not self.extraction_protocol_block_id:
                msg = f"LLM Step '{self.slug}' must define a valid extraction_protocol_block_id."
                raise ValueError(msg)
        if self.type == "logic" and not self.hook:
            msg = f"Logic Step '{self.slug}' must define a native 'hook' execution target."
            raise ValueError(msg)
        return self


class StepRule(V2CoreBase):
    """Execution step mapping (DAG Router Node)."""

    id: str = Field(
        pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$", description="Unique node ID in the workflow (e.g. blk_node_1)."
    )
    task_blueprint: str = Field(
        min_length=1, description="ID reference to the isolated Step (e.g., 'step_f15853d2584e4096aeb60f11a3e6ea7c')"
    )
    depends_on: list[str] = Field(default_factory=list, description="IDs of steps that must complete first.")
    input_mappings: dict[str, str] = Field(
        default_factory=dict,
        description='Maps upstream results to LLM inputs. e.g. {"context": "$inputs.document"}',
    )

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

    id: str = Field(pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$", description="Unique Role ID")
    name: I18nText
    model_role: str = Field(description='Maps to SystemConfig.model_mappings (e.g., "analyst_model").')
    pre_hooks: list[str] = Field(default_factory=list, description="List of registered hook logic to run BEFORE llm.")
    post_hooks: list[str] = Field(default_factory=list, description="List of registered hook logic to run AFTER llm.")


class QuestionnaireItem(V2CoreBase):
    """A single question definition within a dynamic questionnaire."""

    question_id: str = Field(description="Unique identifier for the question (e.g., 'q1').")
    question: I18nText = Field(description="Localized question text.")
    type: str = Field(description="Input type, e.g., 'text'.")


class ExpectedInput(V2CoreBase):
    """Dynamic input definition for a workflow (0-N inputs)."""

    input_key: str = Field(description="The internal key for routing this input (e.g., 'history_text').")
    label: I18nText = Field(description="Localized label for the UI.")
    required: bool = Field(description="Whether this input is universally required.")
    is_chat_history: bool = Field(
        default=False, description="If True, routes to ChatParserService for special parsing."
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
            raise ValueError(msg)

        if "questionnaire" in self.input_modes:
            if self.is_chat_history:
                msg = f"ExpectedInput '{self.input_key}' cannot use 'questionnaire' mode when flagged as chat history."
                raise ValueError(msg)
            if len(self.input_modes) > 1:
                msg = f"ExpectedInput '{self.input_key}' cannot mix 'questionnaire' with other input modes."
                raise ValueError(msg)
            if not self.questionnaire_definition:
                msg = f"ExpectedInput '{self.input_key}' uses 'questionnaire' mode but lacks definitions."
                raise ValueError(msg)
        else:
            if self.questionnaire_definition:
                msg = (
                    f"ExpectedInput '{self.input_key}' cannot have questionnaire_definition "
                    "when 'questionnaire' mode is not active."
                )
                raise ValueError(msg)

        return self


class MatrixScorecardRowDTO(V2CoreBase):
    """Represents a single evaluated matrix row in the scorecard and plot axes."""

    block_id: str = Field(..., description="The opaque Stripe ID of the prompt block.")
    name: str = Field(..., description="Pre-localized name for PDF layouts and static charts.")
    label_fi: str = Field(..., description="Finnish human-readable label.")
    label_en: str = Field(..., description="English human-readable label.")
    description: str | None = Field(
        default=None, description="Detailed instructions or prompt context behind this axis."
    )

    score: float | None = Field(default=None, description="Raw scaled score.")
    scale_min: float | None = Field(default=None, description="Minimum possible score.")
    scale_max: float | None = Field(default=None, description="Maximum possible score.")
    normalized_score: float | None = Field(default=None, description="Normalized score (0-100) if evaluative.")

    true_atoms: int | None = Field(default=None, description="Global hits found.")
    total_atoms: int | None = Field(default=None, description="Total atoms available to evaluate.")

    row_explanation: str = Field(..., description="The one-sentence justification.")
    evidence_type: str | None = Field(default=None, description="The EvidenceType extracted from AtomResponse")

    cited_source_id: str | None = None
    cited_text_quote: str | None = None
    cited_web_citation: str | None = None

    # Epic 6: XAI Output Extensions
    coaching: str | None = None
    confidence: float | None = None
    falsification: str | None = None
    missing_context: str | None = None
    risk_flag: bool | None = None
    remediation_steps: str | None = None
    emotional_sentiment: str | None = None
    theory_link: str | None = None

    contextual_override: bool | None = Field(default=None, description="Whether contextual override was applied.")
    semantic_reasoning: str | None = Field(
        default=None, description="Detailed semantic justification for the override."
    )

    level_breakdown: dict[str, str] | None = Field(
        default=None,
        description="Epic 24 Breakdowns: DINA hits vs total per scale floor e.g. {'1.0': '5/5'}",
    )

    level_names: dict[str, str] | None = Field(
        default=None,
        description="Map of level keys to their human readable names e.g. {'1': 'Heikko'}",
    )

    ui_plot_ratio: float | None = Field(
        default=None, description="Absolute normalized plot plot ratio [0.0 - 1.0] for mathless Flutter plotting"
    )
    ui_boundary_labels: dict[str, str] = Field(
        default_factory=dict, description="Pre-computed labels for extremes, e.g. {'0.0': 'Low', '1.0': 'High'}"
    )

    is_evaluative: bool = Field(..., description="Whether this block contributes to global average.")

    quotes_list: list[str] | None = Field(
        default=None, description="Array of exact quotes hoisted from successful atoms. Truncated to 150 chars each."
    )

    tda_state: dict[str, Any] | None = Field(default=None, description="TDAState union representation.")


class SynthesisConfigDTO(V2CoreBase):
    """Configuration for LLM output synthesis length, masking, and formatting."""

    system_prompt: str | None = Field(default=None, description="Optional system prompt overriding default synthesis.")
    length_constraint: int | None = Field(default=None, description="Length constraint for the synthesized text.")
    preamble_text: I18nText | None = Field(
        default=None, description="Multilingual preamble text added before synthesis."
    )
    historical_context_mode: LaxHistoricalContextMode = Field(
        default=HistoricalContextMode.DISABLED, description="Mode for fetching historical context."
    )
    enable_pii_masking: bool = Field(default=False, description="Flag to enable algorithmic PII redaction.")
    allowed_exports: list[Literal["pdf", "docx", "raw_json"]] = Field(
        default_factory=lambda: cast(list[Literal["pdf", "docx", "raw_json"]], ["pdf", "raw_json"]),
        description="Supported export file formats.",
    )
    omit_empty_sections: bool = Field(default=True, description="Flag to drop logically empty evaluation sections.")
    allowed_mcp_tools: list[str] = Field(
        default_factory=list, description="Enabled MCP tool identifiers for pre-fetch synthesis phase."
    )
    matrix_visible_columns: list[str] = Field(
        default_factory=lambda: ["label", "score", "distribution", "row_explanation", "quotes"],
        description="Visible columns for the global matrix summary table.",
    )


class ReportLayoutDTO(V2CoreBase):
    preset_view: Literal["1d_metrics", "2d_compare", "3d_complex", "3d_matrix", "default", "text_only"]
    title: I18nText | None = Field(default=None)
    description: I18nText | None = Field(default=None)
    axes: list[MatrixScorecardRowDTO] = Field(default_factory=list)
    text_delivery_mode: Literal["full", "titles_only", "none"] = Field(
        default="full", description="Granularity of text output for this layout."
    )

    synthesis: SynthesisConfigDTO | None = Field(default=None)
    synthesis_md: str | None = Field(default=None, description="The rendered synthesis text for this layout block")


class ReportDataDTO(V2CoreBase):
    workflow_id: str
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
    available_profiles: dict[str, I18nText] = Field(default_factory=dict)
    global_score: float | None = Field(
        default=None, description="The mathematical average extracted from the scoring_result hook."
    )
    has_warning: bool = Field(
        default=False, description="Flag indicating if the report generation had non-fatal warnings."
    )
    evaluative_matrices: list[MatrixScorecardRowDTO] | None = Field(
        default=None, description="Matrices that impact the final grade."
    )
    informational_matrices: list[MatrixScorecardRowDTO] | None = Field(
        default=None, description="Matrices strictly for informational/tracking purposes."
    )
    synthesized_markdown: str | None = Field(default=None, description="Global synthesis markdown text")
    visible_metadata: list[str] = Field(
        default_factory=list, description="Fields visible on the UI and PDF cover header."
    )
    layouts: list[ReportLayoutDTO] = Field(default_factory=list)
    matrix_visible_columns: list[str] = Field(
        default_factory=lambda: ["label", "score", "distribution", "row_explanation", "quotes"]
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

    grouped_extensions: dict[str, list[Any]] | None = Field(
        default_factory=dict, description="Keskitetysti ryhmitellyt XAI-laajennukset (esim. 'citation': [...])"
    )

    penalties_applied: list[str] = Field(
        default_factory=list, description="List of penalty warnings formatted for print."
    )


class OutputLayoutBlock(V2CoreBase):
    """A single sequential rendering block for a report profile."""

    preset_view: Literal["1d_metrics", "2d_compare", "3d_complex", "3d_matrix", "default", "text_only"] = Field(
        description="The static UI renderer preset (e.g. 1d_metrics, 3d_complex)."
    )
    title: I18nText | None = Field(default=None, description="Optional localized layout title.")
    description: I18nText | None = Field(default=None, description="Optional localized layout description.")
    steps: list[str] = Field(default_factory=list, description="List of step IDs providing the axes.")
    target_blocks: list[str] = Field(
        default_factory=list, description="Optional explicit block IDs to plot, filtering and ordering the axes."
    )
    text_delivery_mode: Literal["full", "titles_only", "none"] = Field(
        default="full", description="Granularity of text output in PDF and UI grids."
    )

    synthesis: SynthesisConfigDTO | None = Field(
        default=None, description="Optional Section-Level Synthesis configuration for this block."
    )
    synthesis_md: str | None = Field(default=None, description="Optional Section-Level Synthesis content.")
    strictness_level: int | None = Field(
        default=None, ge=0, le=100, description="Override for strictness_level in this layout."
    )
    scoring_strategy: LaxScoringStrategy | None = Field(
        default=None, description="Override for scoring_strategy in this layout."
    )


class OutputProfile(V2CoreBase):
    """A distinct report variant containing a sequence of layout blocks."""

    id: str = Field(pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$", description="Unique Profile ID")
    slug: str = Field(min_length=1, pattern=r"^[a-zA-Z0-9_\-]+$", description="Fallback slug identifier")
    workflow_id: str = Field(description="ID of the associated Workflow")
    organization_id: str | None = Field(default=None, description="Tenant organization ID.")
    name: I18nText = Field(description="Localized name of the profile (e.g. {'fi': 'Johdon tiivistelmä'})")
    description: I18nText | None = Field(default=None, description="Detailed profile context")
    custom_preface: I18nText | None = Field(
        default=None, description="Rich text preface shown at the very beginning of the report."
    )
    visible_metadata: list[str] = Field(
        default_factory=lambda: ["date", "organization", "user", "scoring_engine", "strictness"],
        description="List of metadata fields visible on the UI and PDF cover header.",
    )
    visible_block_extensions: list[LaxXaiExtensionType] = Field(
        default_factory=list,
        description="Block-level XAI extensions (per-matrix, LLM-produced).",
    )
    visible_workflow_extensions: list[LaxXaiExtensionType] = Field(
        default_factory=list,
        description="Workflow-level global extensions (mathematical engines).",
    )
    max_extension_items: int = Field(
        default=3,
        ge=1,
        le=100,
        description="Max number of items to show per grouped XAI extension.",
    )

    display_scale: Literal["original", "custom", "normalized_100"] = Field(
        default="original",
        description="Selects the source scaling for the scores printed by Blueprint.",
    )
    synthesis: SynthesisConfigDTO | None = Field(
        default=None, description="Nested definition for synthesis configurations."
    )
    include_diagnostic_scorecard: bool = Field(
        default=False, description="Epic 24: Enable appending the independent diagnostic scorecard."
    )
    strictness_level: int | None = Field(default=None, ge=0, le=100, description="Profile-level strictness override.")
    scoring_strategy: LaxScoringStrategy | None = Field(default=None, description="Profile-level strategy override.")
    layouts: list[OutputLayoutBlock] = Field(default_factory=list, description="Ordered sequence of layout blocks.")


class EmbeddedOutputProfile(V2CoreBase):
    """Embedded configuration mapping for workflow output profiles."""

    name: I18nText = Field(description="Localized name of the profile.")
    description: I18nText | None = Field(default=None, description="Detailed profile context")
    custom_preface: I18nText | None = Field(
        default=None, description="Rich text preface shown at the very beginning of the report."
    )
    visible_metadata: list[str] = Field(
        default_factory=lambda: ["date", "organization", "user", "scoring_engine", "strictness"],
        description="List of metadata fields visible on the UI and PDF cover header.",
    )
    visible_block_extensions: list[LaxXaiExtensionType] = Field(
        default_factory=list,
        description="Block-level XAI extensions (per-matrix, LLM-produced).",
    )
    visible_workflow_extensions: list[LaxXaiExtensionType] = Field(
        default_factory=list,
        description="Workflow-level global extensions (mathematical engines).",
    )
    max_extension_items: int | None = Field(
        default=None,
        ge=1,
        description="Max number of items to show per grouped XAI extension. Sorted by severity.",
    )
    display_scale: Literal["original", "custom", "normalized_100"] = Field(
        default="original",
        description="Selects the source scaling for the scores printed by Blueprint.",
    )
    synthesis: SynthesisConfigDTO | None = Field(
        default=None, description="Nested definition for synthesis configurations."
    )
    include_diagnostic_scorecard: bool = Field(
        default=False, description="Epic 24: Enable appending the independent diagnostic scorecard."
    )
    strictness_level: int | None = Field(default=None, ge=0, le=100, description="Profile-level strictness override.")
    scoring_strategy: LaxScoringStrategy | None = Field(default=None, description="Profile-level strategy override.")
    layouts: list[OutputLayoutBlock] = Field(default_factory=list, description="Ordered sequence of layout blocks.")


class Workflow(V2CoreBase):
    """Dynamic Directed Acyclic Graph orchestrator model."""

    id: str = Field(pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$", description="Unique Workflow ID")
    slug: str
    name: I18nText | str
    description: I18nText | str
    status: str
    version: int
    is_public: bool = Field(default=False)
    organization_id: str | None = Field(default=None)
    ui_schema: dict[str, Any] = Field(default_factory=dict)
    output_profiles: dict[str, EmbeddedOutputProfile] = Field(
        default_factory=dict, description="Dictionary of named output profiles for reporting."
    )
    default_profile_id: str = Field(description="The ID of the default output profile to use.")
    default_strictness_level: int = Field(default=50, ge=0, le=100, description="Fallback strictness level.")
    default_scoring_strategy: LaxScoringStrategy = Field(
        default=ScoringStrategy.AVERAGE, description="Fallback strategy."
    )
    enable_contextual_overrides: bool = Field(
        default=False,
        description="Global flag to enable contextual overrides across assertions.",
    )
    expected_inputs: list[ExpectedInput] = Field(
        default_factory=list,
        description="List of dynamic expected inputs required by the workflow",
    )
    steps: list[StepRule] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_dag_integrity(self) -> Workflow:
        """Enforces Directed Acyclic Graph (DAG) structural integrity.

        Raises:
            ValueError: If structure is malformed or internally inconsistent.

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
                    logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
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
                    logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                    raise ValueError(msg)

        return self


class FrozenContext(V2CoreBase):
    """Deep copy of context state at execution time for auditability."""

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

    workflow_id: str = Field(description="ID of the workflow to execute")
    target_locale: str = Field(
        description="Desired target locale for output generated by the workflow "
        "(e.g., 'fi'). Must be explicitly provided."
    )
    profile_id: str | None = Field(
        default=None,
        description=(
            "Epic 13 M1: Optional Opaque ID of the Output Profile to apply. If omitted, fallback to workflow default."
        ),
    )
    matrix_sampling_strategy: int = Field(
        default=SystemConcurrency.MATRIX_SAMPLING_LIMIT.value,
        description=(
            "Explicit dynamic strategy for Matrix Flattening. Defaulted from ALL to "
            "10 locally to mitigate LLM JSON schema context limits."
        ),
    )
    raw_inputs: WorkflowInputsIngress = Field(
        default_factory=WorkflowInputsIngress, description="User provided raw inputs"
    )


class ExecutionStepState(V2CoreBase):
    """Real-time status tracking for a single DAG node."""

    id: str = Field(pattern=r"^([a-z0-9_]{2,15})_[a-zA-Z0-9_-]+$", description="Step ID")
    label: str = Field(description="Localized label for UI tracking")
    status: str = Field(default="pending", description="Status: pending, running, completed, failed")
    last_error: str | None = Field(default=None, description="Error message if the step failed")
    message_code: str | None = Field(default=None, description="Optional UX message code for SSE")


class RenderedSynthesisCache(V2CoreBase):
    """Cached synthesis results tied to a specific OutputProfile ID."""

    synthesized_markdown: str = Field(description="Global synthesis markdown text")
    section_syntheses: dict[str, str] = Field(
        default_factory=dict, description="Mapping of layout ID to LLM generated Section-Level synthesis"
    )
    row_explanations: dict[str, str] = Field(
        default_factory=dict, description="Synthesized row explanations by matrix ID"
    )
    cited_sources: list[str] = Field(default_factory=list, description="Citations used in this profile's synthesis")
    xai_highlights: list[XaiHighlightItem] = Field(default_factory=list, description="Generated XAI highlight boxes")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExecutionRecord(ExecutionCoreFields):
    """Record of a workflow execution, including the frozen context and results."""

    if TYPE_CHECKING:
        status: LaxExecutionStatus = Field(default=ExecutionStatus.PENDING)
        execution_trace: list[ErrorTraceEvent | TombstoneEvent | TraceEvent] = Field(default_factory=list)
        execution_trace_storage_path: str | None = Field(default=None)
        context_variables: dict[str, Any] = Field(default_factory=dict)
        context_variables_storage_path: str | None = Field(default=None)

    id: str = Field(pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$", description="Execution ID, usually a uuid")
    workflow_id: str = Field(description="Workflow ID")
    # Phase 1: status is inherited from ExecutionCoreFields (LaxExecutionStatus SSOT).
    active_profile_id: str | None = Field(
        default=None, description="The ID of the output profile selected for formatting and printing."
    )
    raw_inputs: WorkflowInputs = Field(default_factory=WorkflowInputs, description="Raw user inputs by role")
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
    is_resumable: bool = Field(
        default=False, description="Dynamic flag indicating if a failed/pending execution can be safely resumed."
    )

    duration_ms: int = Field(default=0, description="Total execution duration in milliseconds")
    cost_estimate: float = Field(default=0.0, description="Estimated total cost of the execution in USD")
    models_used: dict[str, int] = Field(
        default_factory=dict, description="Dictionary of models used and their usage count/tokens"
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata for the execution")
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

    status: str
    message: str
    execution_id: str


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

    localized_anchors_found: list[str] = Field(description="Keywords in target language mapping English rule.")
    semantic_reasoning: str = Field(description="Mapping logic explanation in target language.")
    contextual_override: bool = Field(description="Escape hatch for implicit matches.")
    exact_quote: str | None = Field(
        default=None,
        description="Verbatim quote from original text.",
    )

    @model_validator(mode="before")
    @classmethod
    def validate_override_logic(cls, data: Any) -> Any:
        """Validates the consistency of the extraction rules before hydration.

        Raises:
            ValueError: If structure is malformed or internally inconsistent.

        Returns:
            The sanitized data matching schema expectations.
        """
        if not isinstance(data, dict):
            return data

        is_override = data.get("contextual_override") is True
        quote = data.get("exact_quote")

        if is_override:
            data["exact_quote"] = None
        else:
            if quote == "[CONTEXTUAL_OVERRIDE_APPLIED]":
                raise ValueError(
                    "Cross-validation failed: exact_quote cannot be "
                    "'[CONTEXTUAL_OVERRIDE_APPLIED]' if contextual_override is False."
                )
        return data
