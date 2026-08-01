"""V2 Core Models for Backend.

Implements dynamic, append-only, and I18N-capable models according to V2 specs.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Annotated, Any, Literal, Self, cast  # noqa: F401

if TYPE_CHECKING:
    from backend_v2.models.state import ErrorTraceEvent, TombstoneEvent, TraceEvent

from fastapi import status
from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.inputs import WorkflowInputs, WorkflowInputsIngress
from backend_v2.models.dtos.lightweight_matrix import ReasoningStepDTO
from backend_v2.models.dtos.quote_evidence import LLMExtractedQuote, QuoteEvidenceDTO
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
    LaxTargetBlockType,
    LaxXaiExtensionType,
    ScoringStrategy,
    SDUIComponentType,
    StrictnessAnchor,
    TargetBlockType,
    VisualIntent,
)
from backend_v2.models.execution_core import ExecutionCoreFields
from backend_v2.models.view.sdui import AnySduiBlock
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)


__all__ = [
    "I18nText",
    "ModelProfile",
    "SystemConfigModelRegistry",
    "SystemConfigMCPGateways",
    "SystemConfigPerformativeLexicons",
    "LexiconConfigPayload",
    "LexiconSuggestionListDTO",
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
    "JobAcceptedDTO",
    "TDAAssertion",
    "MatrixClaim",
    "BaseTDAExtraction",
    "HumanOverrideRequest",
    "HumanOverrideDTO",
    "ScorecardAtomDTO",
    "ErrorDetailsDTO",
    "HydratedAtomDTO",
    "ExtractedValueDTO",
    "AtomResultDTO",
    "ExecutionMetricsDTO",
    "ReportDataDTO",
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
        """Validates that English translation is always present as a baseline fallback.
        The schema is multi-lingual, allowing any number of languages (primarily English and Finnish)
        to be added as needed.

        Raises:
            AppException: If the English translation is missing or empty.

        Returns:
            The validated I18nText instance.
        """
        # Enforce baseline fallback: 'en' translation must ALWAYS exist.
        en_trans = self.translations.get("en")
        if not en_trans or not en_trans.strip():
            msg = (
                "I18nText must contain a valid English ('en') translation as a baseline fallback. "
                f"Payload: {self.translations}"
            )
            logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

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


class AcceptanceCriterion(V2CoreBase):
    """Structured acceptance criterion with bilingual instruction."""

    instruction: str = Field(description="Structured monolingual instruction.")
    requires_contextual_override: bool = Field(default=False)


class AntiPattern(V2CoreBase):
    """Known anti-pattern with bilingual description."""

    pattern: str = Field(description="Known anti-pattern with monolingual description.")
    allows_contextual_excuse: bool = Field(default=False)


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

    tda_id: str = Field(
        default_factory=lambda: f"tda_{uuid.uuid4().hex}",
        pattern=r"^tda_[a-f0-9]{32}$",
        description="Opaque Stripe ID for this assertion.",
    )
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

    # Phase 4: Monolingual concept description for LLM (migrated from flat ai_rule_description)
    concept_description: str = Field(description="Vain tiivis kuvaus itse konseptista, ei ajo-ohjeita")
    anchor_target: str | None = Field(default=None, description="Mitä ankkuria etsitään (ent. STEP 1)")
    bounding_box_scope: Literal["sentence", "paragraph", "document", "adjacent_paragraphs"] = Field(default="paragraph")
    extraction_rule: str | None = Field(
        default=None, description="Varsinainen sääntö, joka datan on täytettävä (ent. EXTRACTION CONDITION)"
    )
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

    @model_validator(mode="after")
    def validate_math_logic(self) -> TDAAssertion:
        """Validates the consistency of the assertion constraints.

        Raises:
            AppException: If constraints are mathematically or logically invalid.

        Returns:
            The validated assertion.
        """
        if self.inverse_evidence and self.aggregation_mode == "ALL_MUST_COMPLY":
            msg = "Käänteinen sääntö (myrkyn etsintä) vaatii EHDOTTOMASTI 'EXISTS' -aggregaation..."
            logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise ValueError(msg)

        # Phase 1, Milestone 1: Enforce strict dual-track TDA validations
        if self.evaluation_track == "EXTRACTIVE_SENSOR":
            if not self.facts_to_find:
                msg = "EXTRACTIVE_SENSOR -rata vaatii vähintään yhden haettavan faktan (facts_to_find)."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
            if not self.logical_expression or not self.logical_expression.strip():
                msg = "EXTRACTIVE_SENSOR -rata vaatii määrittämään loogisen lausekkeen (logical_expression)."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
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
    # execution_persona field REMOVED. execution_persona_block_id now resides on the Step model.
    theory_grounding: TheoryGrounding | None = Field(
        default=None,
        description="Fetches and injects source theory as <theory_context>.",
    )
    is_lightweight_protocol: bool = Field(
        default=False,
        description="If True, enables Best-of-Three ensemble evaluation routing.",
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
            AppException: If structure is malformed or internally inconsistent.

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
            logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
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
                    logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                    raise ValueError(msg)
            if len(scales) == 0:
                msg = (
                    f"PromptBlock '{block_id}': Jos scales on valittu käyttöön, "
                    "siellä on pakko olla vähintään yksi MatrixScale (len > 0)."
                )
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
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
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
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
    frequency_penalty: float | None = Field(default=None, description="Frequency penalty")
    presence_penalty: float | None = Field(default=None, description="Presence penalty")
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
    type: str = Field(description="Type of config")
    slug: str | None = Field(default=None, description="System Config identifier slug")
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

    id: str = Field(pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$", description="System config ID")
    type: str = Field(description="Config type discriminator.")
    slug: str | None = Field(default=None, description="System Config identifier slug")
    tools: list[AllowedMCPTool] = Field(
        default_factory=list, description="Registry of all available MCP tools in the system."
    )


class LexiconConfigPayload(V2CoreBase):
    """Configuration for a single language lexicon."""

    language_code: str = Field(description="ISO language code (e.g., 'en', 'fi').")
    language_name: str = Field(description="Human readable language name.")
    fuzz_threshold: float = Field(default=85.0, description="RapidFuzz threshold (0-100).")
    words: list[str] = Field(default_factory=list, description="List of performative phrases.")


class SystemConfigPerformativeLexicons(V2CoreBase):
    """System configuration for multi-language performative lexicons."""

    id: str = Field(pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$", description="System config ID")
    type: Literal["performative_lexicons"] = Field(
        default="performative_lexicons", description="Config type discriminator."
    )
    slug: str | None = Field(default=None, description="System Config identifier slug")
    lexicons: dict[str, Any] | None = Field(default=None, description="Legacy payload mapping")
    lexicon: dict[str, Any] | None = Field(default=None, description="Legacy payload mapping")
    lexicon_configs: dict[str, LexiconConfigPayload] = Field(
        default_factory=dict, description="Map of language code to lexicon configuration."
    )


class LexiconSuggestionListDTO(V2CoreBase):
    """Structured DTO for LLM returned performative phrases."""

    suggested_phrases: list[str] = Field(
        default_factory=list, description="List of suggested performative or slop phrases."
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
            AppException: If structure is malformed or internally inconsistent.

        Returns:
            The sanitized Step matching schema expectations.
        """
        if self.type == "llm":
            if not self.model_strategy:
                msg = f"LLM Step '{self.slug}' must declare an explicit model_strategy (Zero-Fallback Rule)."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
            if not self.criteria_block_ids:
                msg = f"LLM Step '{self.slug}' must define at least one criteria_block_id."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
            if not self.extraction_protocol_block_id:
                msg = f"LLM Step '{self.slug}' must define a valid extraction_protocol_block_id."
                logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ValueError(msg)
        if self.type == "logic" and not self.hook:
            msg = f"Logic Step '{self.slug}' must define a native 'hook' execution target."
            logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
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
    expected_sdui_type: Annotated[
        Literal["markdown", "hero_insight", "grid"] | None,
        Field(description="Declares the expected SDUI output schema for schema compilation."),
    ] = None

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


class HumanOverrideRequest(V2CoreBase):
    """Payload for human override requests."""

    new_status: LaxExecutionStatus = Field(description="The overridden status (e.g., TRUE, FALSE, DLQ).")
    reason: str = Field(description="The reason for the override.")
    evidence_quotes: list[QuoteEvidenceDTO] = Field(
        default_factory=list, description="Selected quotes to support the override."
    )


class HumanOverrideDTO(V2CoreBase):
    """Schema for human-initiated state override."""

    new_status: ExecutionStatus = Field(description="The overridden status (e.g., TRUE, FALSE, DLQ).")
    reason: str = Field(description="The reason for the override.")
    evidence_quotes: list[QuoteEvidenceDTO] = Field(description="Selected quotes to support the override.")
    overridden_by: str = Field(description="User ID who performed the override.")
    overridden_at: datetime = Field(description="Timestamp of the override.")


class ScorecardAtomDTO(V2CoreBase):
    """Explicit DTO firewall for presentation logic of individual atom evaluations."""

    model_config = ConfigDict(extra="ignore", strict=True)

    atom_id: str
    level: int
    level_name: str
    claim_label: str
    extracted_facts: dict[str, str | None]
    exact_quotes: list[QuoteEvidenceDTO]
    internal_logic_en: ReasoningStepDTO
    status: ExecutionStatus | None
    semantic_reasoning: str
    contextual_override: bool
    structural_location: str
    chart_display_label: str
    visual_intent: VisualIntent
    human_override: HumanOverrideDTO | None = None


class TDAPending(V2CoreBase):
    runtimeType: Literal["pending"] = Field(default="pending")


class TDAEvaluated(V2CoreBase):
    runtimeType: Literal["evaluated"] = Field(default="evaluated")
    passed: bool
    display_quote: str
    raw_anchor: str


class TDADlq(V2CoreBase):
    runtimeType: Literal["dlq"] = Field(default="dlq")
    user_reason: str
    backend_trace: str


TDAStateUnion = Annotated[TDAPending | TDAEvaluated | TDADlq, Field(discriminator="runtimeType")]


class MatrixScorecardRowDTO(V2CoreBase):
    """Represents a single evaluated matrix row in the scorecard and plot axes."""

    block_id: str = Field(..., description="The opaque Stripe ID of the prompt block.")
    name: str = Field(..., description="Pre-localized name for PDF layouts and static charts.")
    label_i18n: I18nText = Field(..., description="Full I18n translations dictionary for the UI.")
    description: str | None = Field(
        default=None, description="Detailed instructions or prompt context behind this axis."
    )

    score: float | None = Field(default=None, description="Raw scaled score.")
    score_display_label: str | None = None
    scale_min: float | None = Field(default=None, description="Minimum possible score.")
    scale_max: float | None = Field(default=None, description="Maximum possible score.")
    normalized_score: float | None = Field(default=None, description="Normalized score (0-100) if evaluative.")

    true_atoms: int | None = Field(default=None, description="Global hits found.")
    total_atoms: int | None = Field(default=None, description="Total atoms available to evaluate.")
    row_explanation: str = Field(..., description="The one-sentence justification.")
    evidence_type: Literal["EXPLICIT_QUOTE", "IMPLIED_INTENT", "NO_EVIDENCE"] | None = Field(
        default=None, description="The EvidenceType extracted from AtomResponse"
    )

    cited_source_id: str | None = None
    cited_text_quote: str | None = None
    cited_web_citation: str | None = None

    # XAI Output Extensions
    confidence: float | None = None

    inner_sdui_blocks: list[AnySduiBlock] = Field(
        default_factory=list, description="Strict SDUI components rendered for this row."
    )

    contextual_override: bool | None = Field(default=None, description="Whether contextual override was applied.")
    semantic_reasoning: str | None = Field(
        default=None, description="Detailed semantic justification for the override."
    )

    level_breakdown: dict[str, str] | None = Field(
        default=None,
        description="Breakdowns: DINA hits vs total per scale floor e.g. {'1.0': '5/5'}",
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

    used_evidence_ids: list[str] = Field(default_factory=list, description="Trace IDs used for this row.")
    evaluated_atoms: list[ScorecardAtomDTO] = Field(
        default_factory=list, description="Flat presentation-only atoms evaluated for this row."
    )
    clustered_row_sources: list[MCPAuditTrace] = Field(
        default_factory=list, description="Purity Paradox resolution, cluster arrays at row level."
    )

    tda_state: TDAStateUnion | None = Field(default=None, description="TDAState union representation.")


class SynthesisConfigDTO(V2CoreBase):
    """Configuration for LLM output synthesis length, masking, and formatting."""

    system_prompt: str | None = Field(default=None, description="Optional system prompt overriding default synthesis.")
    synthesis_block_id: str | None = Field(
        default=None,
        description="Optional explicit reference to the extraction block UUID that generates the global synthesis (e.g. blk_8f7e6d5c4b3a2019).",
    )
    row_explanations_block_id: str | None = Field(
        default=None,
        description="Optional explicit reference to the extraction block UUID that generates row explanations.",
    )
    model_strategy: str = Field(
        default="synthesis",
        description=(
            "Pointer to Model Registry strategy key. "
            "Determines which model/temperature is used for the main synthesis LLM call. "
            "MUST exist as a key in system_config.model_registry.models."
        ),
    )
    length_constraint: int | None = Field(default=None, description="Length constraint for the synthesized text.")
    preamble_text: I18nText | None = Field(
        default=None, description="Multilingual preamble text added before synthesis."
    )
    historical_context_mode: LaxHistoricalContextMode = Field(
        default=HistoricalContextMode.DISABLED, description="Mode for fetching historical context."
    )
    enable_pii_masking: bool = Field(default=False, description="Flag to enable algorithmic PII redaction.")
    allowed_exports: list[Literal["pdf", "docx", "raw_json", "xlsx"]] = Field(
        default_factory=lambda: cast(list[Literal["pdf", "docx", "raw_json", "xlsx"]], ["pdf", "raw_json"]),
        description="Supported export file formats.",
    )
    omit_empty_sections: bool = Field(default=True, description="Flag to drop logically empty evaluation sections.")
    allowed_mcp_tools: list[str] = Field(
        default_factory=list, description="Enabled MCP tool identifiers for pre-fetch synthesis phase."
    )
    tone_instruction: I18nText | None = Field(default=None, description="Dynamic tone instruction for synthesis.")



class ErrorDetailsDTO(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")
    error_code: Annotated[str, Field(description="Standardized error code, e.g., LLM_TIMEOUT")]
    message: Annotated[str, Field(description="Technical error message or stack trace")]


class HydratedAtomDTO(BaseModel):
    """Static ontology data. Perfectly cacheable.
    Must not contain any dynamic execution-related data.
    """

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")
    sdui_component: Annotated[SDUIComponentType, Field(description="Server-Driven UI hint for frontend.")]
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
    status: ExecutionStatus
    extracted_data: Annotated[
        ExtractedValueDTO | None, Field(default=None, description="Quantitative or isolated result")
    ]
    source_quote: Annotated[str | None, Field(default=None, description="Verbatim original quote from the document")]
    contextual_override: Annotated[
        bool, Field(default=False, description="Allows cognitive override without a verbatim quote")
    ]
    evaluation_reasoning: Annotated[
        str | None, Field(default=None, description="Strictly AI cognitive reasoning, no infra errors")
    ]
    error_details: Annotated[
        ErrorDetailsDTO | None, Field(default=None, description="Populated only if status is SYSTEM_ERROR")
    ]
    extensions: Annotated[dict[str, str], Field(default_factory=dict, description="Requested XAI extensions mapping")]

    depends_on_tda_ids: Annotated[list[str], Field(default_factory=list, description="DAG adjacency list")]
    short_circuit_reason_tda_ids: Annotated[list[str], Field(default_factory=list)]

    @model_validator(mode="before")
    @classmethod
    def validate_cognitive_vs_system_state(cls, data: Any) -> Any:
        """Fail-Fast & Graceful Healing: Prevents hallucinations and incomplete data before freeze."""
        if isinstance(data, dict):
            if data.get("contextual_override") is True and data.get("source_quote") is not None:
                data["source_quote"] = None

            status_val = data.get("status")
            if status_val in ("PASSED", "FAILED", ExecutionStatus.PASSED, ExecutionStatus.FAILED):
                if not data.get("evaluation_reasoning"):
                    raise ValueError(f"Reasoning is mandatory for cognitive status {status_val}")
                if not data.get("contextual_override") and not data.get("source_quote"):
                    raise ValueError("source_quote is mandatory unless contextual_override is True")

            if status_val in ("SYSTEM_ERROR", ExecutionStatus.SYSTEM_ERROR) and not data.get("error_details"):
                raise ValueError("Error details are mandatory when status is SYSTEM_ERROR")
        return data


class ExecutionMetricsDTO(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")
    total_atoms: int
    evaluated: int
    short_circuited_na: int
    duration_ms: Annotated[int, Field(default=0, description="Execution duration in milliseconds for observability")]


class ReportDataDTO(V2CoreBase):
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

    # NEW FIELDS FROM EPIC 91.5 (Strict Topological DAG Execution Model)
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


class OutputLayoutBlock(V2CoreBase):
    """A single sequential rendering block for a report profile."""

    preset_view: Literal["1d_metrics", "2d_compare", "3d_matrix", "default", "text_only", "matrix_summary"] = Field(
        description="The static UI renderer preset (e.g. 1d_metrics, 3d_matrix)."
    )
    is_synthesis_enabled: bool = Field(default=True, description="Toggle for UI section-level synthesis.")
    title: I18nText | None = Field(default=None, description="Optional localized layout title.")
    description: I18nText | None = Field(default=None, description="Optional localized layout description.")
    steps: list[str] = Field(default_factory=list, description="List of step IDs providing the axes.")
    target_blocks: list[str | LaxTargetBlockType] = Field(
        default_factory=list, description="Optional explicit block IDs to plot, filtering and ordering the axes."
    )
    text_delivery_mode: Literal["full", "titles_only", "none"] = Field(
        default="full", description="Granularity of text output in PDF and UI grids."
    )

    synthesis: SynthesisConfigDTO | None = Field(
        default=None, description="Optional Section-Level Synthesis configuration for this block."
    )
    synthesis_blocks: list[AnySduiBlock] | None = Field(
        default=None, description="Optional Section-Level Synthesis content blocks."
    )
    strictness_level: int | None = Field(
        default=None, ge=0, le=100, description="Override for strictness_level in this layout."
    )
    scoring_strategy: LaxScoringStrategy | None = Field(
        default=None, description="Override for scoring_strategy in this layout."
    )
    matrix_column_labels: dict[str, I18nText] = Field(
        default_factory=dict,
        description="Optional mapping of UI column identifiers to localized labels.",
    )
    matrix_visible_columns: list[str] = Field(
        default_factory=list,
        description="Visible columns for this matrix UI.",
    )


class OutputProfile(V2CoreBase):
    """A distinct report variant containing a sequence of layout blocks."""

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
    include_diagnostic_scorecard: bool = Field(
        default=False, description="Enable appending the independent diagnostic scorecard."
    )
    strictness_level: Literal[85, 100] | None = Field(default=None, description="Profile-level strictness override.")
    scoring_strategy: LaxScoringStrategy | None = Field(default=None, description="Profile-level strategy override.")
    user_role_mappings: dict[str, I18nText] = Field(
        default_factory=dict,
        description="Localized values for RoleClassification enum values (e.g. ROLE_ARCHITECT).",
    )
    extension_labels: dict[LaxXaiExtensionType, I18nText] = Field(
        default_factory=dict,
        description="Localized labels for global XAI highlights at the profile level.",
    )
    metric_mappings: dict[str, I18nText] = Field(
        default_factory=dict,
        description="Localized labels for internal metric variables (e.g. 'variance_mechanical').",
    )
    synthesis: SynthesisConfigDTO | None = Field(
        default=None, description="Global synthesis configuration for the executive summary."
    )
    layouts: list[OutputLayoutBlock] = Field(default_factory=list, description="Ordered sequence of layout blocks.")
    content_blocks: list[AnySduiBlock] = Field(
        default_factory=list, description="Base SDUI content blocks predefined by the profile."
    )
    performativity_detector_step_id: str | None = Field(
        default=None, description="Optional step ID for the performativity detector"
    )


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
    default_profile_id: str = Field(description="The ID of the default output profile to use.")
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
        description=("Optional Opaque ID of the Output Profile to apply. If omitted, fallback to workflow default."),
    )
    matrix_sampling_strategy: int = Field(
        default_factory=lambda: get_settings().matrix_sampling_limit,
        description=(
            "Explicit dynamic strategy for Matrix Flattening. Defaulted from ALL to "
            "10 locally to mitigate LLM JSON schema context limits."
        ),
    )
    raw_inputs: WorkflowInputsIngress = Field(
        default_factory=lambda: WorkflowInputsIngress(), description="User provided raw inputs"
    )


class ExecutionStepState(V2CoreBase):
    """Real-time status tracking for a single DAG node."""

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


class RenderedSynthesisCache(V2CoreBase):
    """Cached synthesis results tied to a specific OutputProfile ID."""

    synthesized_markdown: str = Field(default="", description="Compiled Markdown content for the report")
    content_blocks: list[AnySduiBlock] = Field(default_factory=list, description="Global synthesis SDUI content blocks")
    section_syntheses: dict[str, list[AnySduiBlock]] = Field(
        default_factory=dict, description="Mapping of layout ID to LLM generated Section-Level synthesis blocks"
    )
    row_explanations: dict[str, str] = Field(
        default_factory=dict, description="Synthesized row explanations by matrix ID"
    )
    row_curated_quotes: dict[str, list[str]] = Field(default_factory=dict, description="Curated quotes by matrix ID")
    cited_sources: list[str] = Field(default_factory=list, description="Citations used in this profile's synthesis")
    user_role: str | None = Field(default=None, description="User role")
    user_role_justification: str | None = Field(default=None, description="User role justification")
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


class EvidenceRejectionRequest(V2CoreBase):
    """Request DTO for rejecting a specific evidence quote."""

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

    @model_validator(mode="before")
    @classmethod
    def validate_override_logic(cls, data: Any) -> Any:
        """Validates the consistency of the extraction rules before hydration.

        Raises:
            AppException: If structure is malformed or internally inconsistent.

        Returns:
            The sanitized data matching schema expectations.
        """
        if not isinstance(data, dict):
            return data

        is_override = data.get("contextual_override") is True
        quotes = data.get("exact_quotes", [])
        if quotes is None:
            quotes = []

        if is_override:
            data["exact_quotes"] = []
        else:
            if isinstance(quotes, list):
                for q in quotes:
                    if isinstance(q, str) and q == "[CONTEXTUAL_OVERRIDE_APPLIED]":
                        msg = (
                            "Cross-validation failed: exact_quotes cannot contain "
                            "'[CONTEXTUAL_OVERRIDE_APPLIED]' if contextual_override is False."
                        )
                        logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                        raise ValueError(msg)
                    elif isinstance(q, dict) and q.get("text") == "[CONTEXTUAL_OVERRIDE_APPLIED]":
                        msg = (
                            "Cross-validation failed: exact_quotes cannot contain "
                            "'[CONTEXTUAL_OVERRIDE_APPLIED]' if contextual_override is False."
                        )
                        logger.error("[V2Core] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                        raise ValueError(msg)
        return data


from backend_v2.models.state import ErrorTraceEvent, TombstoneEvent, TraceEvent

from backend_v2.models.view.sdui import (
    SduiRadarChartBlock,
    SduiScatterPlotBlock,
    SduiMatrixTableBlock,
    SduiMetrics1DBlock,
)

ExecutionRecord.model_rebuild()

_sdui_localns = {
    "I18nText": I18nText,
    "MatrixScorecardRowDTO": MatrixScorecardRowDTO,
    "LaxXaiExtensionType": LaxXaiExtensionType
}
SduiRadarChartBlock.model_rebuild(_types_namespace=_sdui_localns)
SduiScatterPlotBlock.model_rebuild(_types_namespace=_sdui_localns)
SduiMatrixTableBlock.model_rebuild(_types_namespace=_sdui_localns)
SduiMetrics1DBlock.model_rebuild(_types_namespace=_sdui_localns)
