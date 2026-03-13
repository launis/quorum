"""V2 Core Models for Backend.
Implements dynamic, append-only, and I18N-capable models according to V2 specs.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend_v2.models.enums import BlockDataType, ComponentType, ExecutionStatus, StrictnessLevel

logger = logging.getLogger(__name__)

class V2CoreBase(BaseModel):
    """Base model enforcing Pydantic strict mode across all V2 schemas."""
    model_config = ConfigDict(strict=True)

__all__ = [
    "I18nText",
    "ModelProfile",
    "SystemConfigModelRegistry",
    "SystemConfigModelRegistry",
    "Step",
    "StepRule",
    "Role",
    "Workflow",
    "ComponentType",
    "BlockDataType",
    "ExecutionStatus",
    "FrozenContext",
    "ExecutionCreate",
    "ExecutionRecord",
    "Observation",
    "OutputConfig",
    "Reference",
    "ExpectedInput",
    "QuestionnaireItem"
]


class I18nText(V2CoreBase):
    """V2 Strict: Frontend no-string mandate requires all localized text to be structured."""

    default_locale: str = Field(
        description="The default locale used if a translation is missing."
    )
    translations: dict[str, str] = Field(
        default_factory=dict,
        description="Dictionary mapping locale code to translated string (e.g. {'fi': 'Teksti', 'en': 'Text'}).",
    )


class TheoryGrounding(V2CoreBase):
    """Used in PromptBlock to bind criteria to organizational truth."""

    source_url: str = Field(description="URL or reference to the source material.")
    citation_reference: str = Field(
        description="Specific section or phrase to cite from the source."
    )


class MatrixScale(V2CoreBase):
    """Represents a single score point in a BARS matrix scale."""
    score: int = Field(description="Numerical value of the scale point.")
    name: I18nText | None = Field(default=None, description="Optional name for the scale point (e.g., 'Excellent').")
    claims: list[I18nText] = Field(
        default_factory=list,
        description="List of behavioral claims/criteria for this score."
    )



class PromptBlock(V2CoreBase):
    """V2 PromptBlock representation.
    Fuses legacy Components and Matrices into a unified directive model.
    """

    id: str = Field(
        pattern=r"^[a-zA-Z][a-zA-Z0-9_]*$",
        description=(
            "Unique identifier for the prompt block. MUST be a valid Python identifier "
            "(letters, numbers, underscores, starting with letter) to guarantee dynamic schema compilation."
        )
    )
    label: I18nText = Field(description="Localizable label for the UI.")
    description: I18nText = Field(description="Localizable description or help text.")
    category_id: str = Field(description="Categorization identifier (e.g. 'scientific_theory', 'system_rule').")
    type: BlockDataType = Field(
        description="Data type of the expected extracted value."
    )
    allow_decimals: bool = Field(
        default=False, description="Whether float types allow decimals in validation."
    )
    strictness_level: int = Field(
        ge=0,
        le=100,
        description="0 = Absolute Leniency, 100 = Absolute Strictness. Translates to system prompt constraints.",
    )
    require_justification: bool = Field(
        description="If True, dynamically generates `{slug}_justification` and `{slug}_citation` fields.",
    )
    theory_grounding: TheoryGrounding | None = Field(
        default=None,
        description="If provided, fetches and injects source theory as <theory_context> to prompt.",
    )
    scale_min: int | None = Field(
        default=None,
        description="Minimum score for the scales matrix. Required if scales are present."
    )
    scale_max: int | None = Field(
        default=None,
        description="Maximum score for the scales matrix. Required if scales are present."
    )
    scales: list[MatrixScale] | None = Field(
        default=None,
        description="BARS scale definitions with scores and localized claims. If provided, must not be empty."
    )
    rows: list[I18nText] | None = Field(
        default=None,
        description="Optional rows for grid matrices."
    )
    columns: list[I18nText] | None = Field(
        default=None,
        description="Optional columns for grid matrices."
    )

    @model_validator(mode="before")
    @classmethod
    def pre_validate_type_enum(cls, data: Any) -> Any:
        """Parse string to Enum before strict mode rejects it."""
        if isinstance(data, dict):
            t = data.get("type")
            if isinstance(t, str):
                try:
                    data["type"] = BlockDataType(t)
                except ValueError:
                    pass # Let standard validation catch invalid strings
        return data

    @model_validator(mode="after")
    def validate_block_consistency(self) -> PromptBlock:
        """Strict validation for PromptBlock relations and logical constraints."""
        from backend_v2.exceptions import AppException, ErrorCodes
        # Fail-fast: Cannot allow decimals on non-numeric types
        # string permitted for BARS format
        valid_numeric = [BlockDataType.FLOAT, BlockDataType.INT, BlockDataType.STRING]
        if self.allow_decimals and self.type not in valid_numeric:
            msg = f"PromptBlock '{self.id}': allow_decimals is only valid for numeric logic."
            logger.error(f"[V2Core] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
            raise AppException(
                message=msg,
                details={"error_code": ErrorCodes.VALIDATION_FAILED},
                status_code=400
            )

        # Strict Business Logic Constraints from user rules
        if self.scales is not None:
            if self.scale_min is None or self.scale_max is None:
                msg = (
                    f"PromptBlock '{self.id}': Jos scales on valittu käyttöön, "
                    "scale_min ja scale_max on oltava määriteltynä."
                )
                logger.error(f"[V2Core] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
                raise AppException(
                    message=msg,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED},
                    status_code=400
                )
            if self.scale_max <= self.scale_min:
                msg = (
                    f"PromptBlock '{self.id}': scale_max ({self.scale_max}) "
                    f"on oltava suurempi kuin scale_min ({self.scale_min})."
                )
                logger.error(f"[V2Core] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
                raise AppException(
                    message=msg,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED},
                    status_code=400
                )
            if len(self.scales) == 0:
                msg = (
                    f"PromptBlock '{self.id}': Jos scales on valittu käyttöön, "
                    "siellä on pakko olla vähintään yksi MatrixScale (len > 0)."
                )
                logger.error(f"[V2Core] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
                raise AppException(
                    message=msg,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED},
                    status_code=400
                )
            for scale in self.scales:
                if not scale.claims or len(scale.claims) == 0:
                    msg = (
                        f"PromptBlock '{self.id}' / Scale '{scale.score}': "
                        "Jokaisella scorella pitää olla vähintään yksi claim."
                    )
                    logger.error(f"[V2Core] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
                    raise AppException(
                        message=msg,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED},
                        status_code=400
                    )
        return self


class ChatMessageDTO(V2CoreBase):
    """Schema for a single parsed chat message."""
    role: str = Field(description="The role of the speaker (e.g. 'user' or 'ai').")
    content: str = Field(description="The message text.")

class ChatHistoryDTO(V2CoreBase):
    """Strict schema for a complete parsed chat sequence."""
    conversation: list[ChatMessageDTO] = Field(description="List of messages in chronological order.")


class DataDictionaryField(V2CoreBase):
    """UI Hints mapping for dynamic form generation (SDUI)."""

    field_id: str
    component_type: ComponentType = Field(description="E.g., 'slider', 'text_input', 'dropdown'")
    options: list[dict[str, Any]] | None = None
    validation_rules: dict[str, Any] | None = None

    @model_validator(mode="before")
    @classmethod
    def pre_validate_type_enum(cls, data: Any) -> Any:
        """Parse string to Enum before strict mode rejects it."""
        if isinstance(data, dict):
            t = data.get("component_type")
            if isinstance(t, str):
                try:
                    data["component_type"] = ComponentType(t)
                except ValueError:
                    pass
        return data


class ModelProfile(V2CoreBase):
    """A flattened physical AI model representation."""
    provider: str = Field(description="E.g., 'google', 'openai'")
    model_name: str = Field(description="The underlying API model name")
    temperature: float | None = Field(default=None, description="Generation temperature")
    tpm_limit: int | None = Field(default=None, description="Tokens per minute limit")
    rpm_limit: int | None = Field(default=None, description="Requests per minute limit")
    max_tokens: int | None = Field(default=None, description="Max generated tokens")
    allowed_tools: list[str] = Field(default_factory=list, description="Enabled tools")
    supports_grounding: bool = Field(default=False, description="Supports Google Search Grounding")
    api_key: str | None = Field(default=None, description="Optional override API key")
    parsing_mode: str | None = Field(default=None, description="Parser logic flag (e.g. 'GEMINI_JSON')")

class SystemConfigModelRegistry(V2CoreBase):
    """V2 Flattened Model Registry System Config."""
    id: str = Field(description="System config ID")
    slug: str = Field(description="Slug identifier")
    type: str = Field(default="model_registry", description="Type of config")
    models: dict[str, ModelProfile] = Field(
        description="Dictionary mapping generic role names to specific ModelProfiles"
    )

class Step(V2CoreBase):
    """Isolated, reusable orchestrator cognitive module (e.g. Guard or step_input_processing).
    Formerly known as TaskBlueprint.
    """
    id: str = Field(description="Unique UUID for storage optionally")
    slug: str = Field(description="Human-readable identifier (e.g., 'step_guard')")
    name: I18nText | str = Field(description="Localized step name or string name")
    description: I18nText | str | None = Field(default=None, description="Detailed step context")
    task_key: str | None = Field(default=None, description="Legacy or internal key reference")
    prompt_blocks: list[str] = Field(
        default_factory=list,
        description="List of PromptBlock slugs containing directives and matrices for this step."
    )
    pre_hooks: list[str] = Field(
        default_factory=list,
        description="Native Python functions to execute BEFORE LLM context building."
    )
    post_hooks: list[str] = Field(
        default_factory=list,
        description="Native Python functions to execute AFTER LLM generation."
    )

    @model_validator(mode="after")
    def validate_step_consistency(self) -> Step:
        """Strict fail-fast validation to ensure Step is not purely empty."""
        if not self.prompt_blocks:
            from backend_v2.exceptions import AppException, ErrorCodes
            msg = f"Step '{self.slug}' must define at least one prompt_block."
            logger.error(f"[V2Core] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
            raise AppException(
                message=msg,
                details={"error_code": ErrorCodes.VALIDATION_FAILED},
                status_code=400
            )
        return self

class StepRule(V2CoreBase):
    """Execution step mapping (DAG Router Node)."""
    id: str = Field(description="Unique node ID in the workflow (e.g. step_node_1).")
    task_blueprint: str = Field(
        description="Slug reference to the isolated Step (e.g., 'step_input_processing')"
    )
    depends_on: list[str] = Field(default_factory=list, description="IDs of steps that must complete first.")
    input_mappings: dict[str, str] = Field(
        default_factory=dict,
        description='Maps upstream results to LLM inputs. e.g. {"context": "$inputs.document"}',
    )
    model_strategy: str | None = Field(
        default=None,
        description="Logical strategy profile from model registry (e.g., 'fast', 'deep')"
    )

class Role(V2CoreBase):
    """Role definition that locks physical models and pre_hooks."""
    id: str
    name: I18nText
    model_role: str = Field(description="Maps to SystemConfig.model_mappings (e.g., \"analyst_model\").")
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
        default=False,
        description="If True, routes to ChatParserService for special parsing."
    )
    input_modes: list[str] = Field(
        default_factory=list,
        description="Allowed modes: 'file', 'paste', 'questionnaire'."
    )
    description: I18nText | None = Field(default=None, description="Optional localized description/help text.")
    ai_description: I18nText | None = Field(
        default=None,
        description="Semantic description injected to LLM context.",
    )
    questionnaire_definition: list[QuestionnaireItem] = Field(
        default_factory=list, description="Definitions if 'questionnaire' is in input_modes."
    )

    @model_validator(mode="after")
    def validate_modes(self) -> ExpectedInput:
        """Strict validation for input modes."""
        from backend_v2.exceptions import AppException, ErrorCodes
        if not self.input_modes:
            msg = f"ExpectedInput '{self.input_key}' must have at least one input_mode."
            logger.error(f"[V2Core] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
            raise AppException(
                message=msg,
                details={"error_code": ErrorCodes.VALIDATION_FAILED},
                status_code=400
            )

        if "questionnaire" in self.input_modes:
            if self.is_chat_history:
                msg = (
                    f"ExpectedInput '{self.input_key}' cannot use "
                    "'questionnaire' mode when flagged as chat history."
                )
                logger.error(f"[V2Core] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
                raise AppException(
                    message=msg,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED},
                    status_code=400
                )
            if len(self.input_modes) > 1:
                msg = f"ExpectedInput '{self.input_key}' cannot mix 'questionnaire' with other input modes."
                logger.error(f"[V2Core] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
                raise AppException(
                    message=msg,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED},
                    status_code=400
                )
            if not self.questionnaire_definition:
                msg = f"ExpectedInput '{self.input_key}' uses 'questionnaire' mode but lacks definitions."
                logger.error(f"[V2Core] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
                raise AppException(
                    message=msg,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED},
                    status_code=400
                )
        return self

class Workflow(V2CoreBase):
    """Dynamic Directed Acyclic Graph orchestrator model."""
    id: str
    slug: str
    name: I18nText | str
    description: I18nText | str
    status: str = Field(default="draft")
    version: int = Field(default=1)
    is_public: bool = Field(default=False)
    organization_id: str | None = Field(default=None)
    scoring_logic: list[Any] = Field(default_factory=list)
    ui_schema: dict[str, Any] = Field(default_factory=dict)
    expected_inputs: list[ExpectedInput] = Field(
        default_factory=list,
        description="List of dynamic expected inputs required by the workflow",
    )
    steps: list[StepRule] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def set_slug_from_id(cls, data: Any) -> Any:
        # Fallback for seed data missing the slug
        if isinstance(data, dict):
            if "slug" not in data and "id" in data:
                data["slug"] = data["id"]
        return data

    @model_validator(mode="after")
    def check_cyclic_dependencies(self) -> Workflow:
        """Validate workflow steps form a valid DAG without cycles."""
        adj_list = {step.id: step.depends_on for step in self.steps}
        visited = set()
        rec_stack = set()

        def is_cyclic(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in adj_list.get(node, []):
                if neighbor not in visited:
                    if is_cyclic(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        from backend_v2.exceptions import AppException, ErrorCodes
        for step in self.steps:
            if step.id not in visited:
                if is_cyclic(step.id):
                    msg = f"Cyclic dependency detected involving step: {step.id}"
                    logger.error(f"[V2Core] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
                    raise AppException(
                        message=msg,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED},
                        status_code=400
                    )

        return self


class FrozenContext(V2CoreBase):
    """Deep copy of context state at execution time for auditability."""
    compiled_prompts: dict[str, str] = Field(
        default_factory=dict, description="Prompts sent to LLM.")
    injected_theory: dict[str, Any] = Field(
        default_factory=dict, description="Fetched theory texts.")
    generated_schemas: dict[str, dict[str, Any]] = Field(
        default_factory=dict, description="JSON schemas used.")
    ui_hints_snapshot: dict[str, DataDictionaryField] = Field(
        default_factory=dict, description="UI rendering instructions.")


class WorkflowInputs(V2CoreBase):
    """Schema for dynamic workflow inputs, allowing any extra keys for dynamic routing."""
    model_config = ConfigDict(strict=True, extra="allow")

class ExecutionCreate(V2CoreBase):
    """Schema for initiating a new workflow execution."""
    workflow_id: str = Field(description="ID of the workflow to execute")
    strictness_level: StrictnessLevel = Field(
        description="Cognitive strictness level (1-5). Determines the injection of Zero-Trust or Falsification blocks."
    )
    raw_inputs: WorkflowInputs = Field(default_factory=WorkflowInputs, description="User provided raw inputs")

    @model_validator(mode="before")
    @classmethod
    def pre_validate_type_enums(cls, data: Any) -> Any:
        """Parse string to Enum before strict mode rejects it."""
        if isinstance(data, dict):
            s = data.get("strictness_level")
            if s is not None and not isinstance(s, StrictnessLevel):
                try:
                    data["strictness_level"] = StrictnessLevel(int(s))
                except ValueError:
                    pass
        return data

class ExecutionStepState(V2CoreBase):
    """Real-time status tracking for a single DAG node."""
    id: str = Field(description="Step ID")
    label: str = Field(description="Localized label for UI tracking")
    status: str = Field(default="pending", description="Status: pending, running, completed, failed")

class ExecutionRecord(V2CoreBase):
    """Record of a workflow execution, including the frozen context and results."""
    id: str = Field(description="Execution ID, usually a uuid")
    workflow_id: str = Field(description="Workflow ID")
    strictness_level: StrictnessLevel = Field(
        default=StrictnessLevel.CAUSAL,
        description="Cognitive strictness level used for this execution."
    )
    status: ExecutionStatus = Field(description="Current status of execution")
    raw_inputs: WorkflowInputs = Field(
        default_factory=WorkflowInputs, description="Raw user inputs by role")
    frozen_context: FrozenContext = Field(
        default_factory=FrozenContext, description="Immutable snapshot of context")
    step_states: dict[str, ExecutionStepState] = Field(
        default_factory=dict, description="Real-time timeline status of individual nodes")
    results: dict[str, Any] = Field(
        default_factory=dict, description="Step-by-step LLM output results")
    error: str | None = Field(default=None, description="Error message if failed")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC creation timestamp")
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC update timestamp")

    @model_validator(mode="before")
    @classmethod
    def pre_validate_type_enums(cls, data: Any) -> Any:
        """Parse string to Enum & Datetime before strict mode rejects it."""
        if isinstance(data, dict):
            # Status
            st = data.get("status")
            if isinstance(st, str):
                try:
                    data["status"] = ExecutionStatus(st)
                except ValueError:
                    pass
            # Strictness Level
            sl = data.get("strictness_level")
            if sl is not None and not isinstance(sl, StrictnessLevel):
                try:
                    data["strictness_level"] = StrictnessLevel(int(sl))
                except ValueError:
                    pass
            # Datetimes
            for df in ["created_at", "updated_at"]:
                dt = data.get(df)
                if isinstance(dt, str):
                    try:
                        data[df] = datetime.fromisoformat(dt.replace('Z', '+00:00'))
                    except ValueError:
                        pass
        return data

# --- Legacy Collection Mapping for UI CRUD ---

class Observation(V2CoreBase):
    """Legacy V1 Observation mapped to V2 Strict structure."""
    id: str = Field(description="Unique Observation ID")
    workflow_id: str | None = Field(default=None, description="Associated Workflow ID")
    name: str | None = Field(default=None, description="Observation name")
    type: str | None = Field(default=None, description="Observation type")
    config: dict[str, Any] = Field(default_factory=dict, description="Configuration rules")


class OutputConfig(V2CoreBase):
    """Legacy V1 OutputConfig mapped to V2 Strict structure."""
    id: str = Field(description="Unique Output Config ID")
    workflow_id: str | None = Field(default=None, description="Associated Workflow ID")
    format: str | None = Field(default=None, description="Output format (e.g., pdf, markdown)")
    template: str | None = Field(default=None, description="Template identifier or content")


class Reference(V2CoreBase):
    """Legacy V1 Reference mapped to V2 Strict structure."""
    id: str = Field(description="Unique Reference ID")
    slug: str | None = Field(default=None, description="Legacy slug")
    type: str | None = Field(default=None, description="Reference type")
    definition: str = Field(description="Full reference definition")
    short_citation: str | None = Field(default=None, description="Short citation format")
    source_file: str | None = Field(default=None, description="Original source file name")
    ingested_at: datetime | str | None = Field(default=None, description="Time of ingestion")
