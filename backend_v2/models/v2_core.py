"""V2 Core Models for Backend.
Implements dynamic, append-only, and I18N-capable models according to V2 specs.
"""

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, model_validator

from backend_v2.models.enums import BlockDataType, ComponentType, ExecutionStatus

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
    "Reference"
]


class I18nText(BaseModel):
    """V2 Strict: Frontend no-string mandate requires all localized text to be structured."""

    default_locale: str = Field(
        description="The default locale used if a translation is missing."
    )
    translations: dict[str, str] = Field(
        default_factory=dict,
        description="Dictionary mapping locale code to translated string (e.g. {'fi': 'Teksti', 'en': 'Text'}).",
    )


class TheoryGrounding(BaseModel):
    """Used in PromptBlock to bind criteria to organizational truth."""

    source_url: str = Field(description="URL or reference to the source material.")
    citation_reference: str = Field(
        description="Specific section or phrase to cite from the source."
    )


class MatrixScale(BaseModel):
    """Represents a single score point in a BARS matrix scale."""
    score: int = Field(description="Numerical value of the scale point.")
    name: I18nText | None = Field(default=None, description="Optional name for the scale point (e.g., 'Excellent').")
    claims: list[I18nText] = Field(
        default_factory=list,
        description="List of behavioral claims/criteria for this score."
    )



class PromptBlock(BaseModel):
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
    scales: list[MatrixScale] = Field(
        default_factory=list,
        description="BARS scale definitions with scores and localized claims."
    )
    rows: list[I18nText] | None = Field(
        default=None,
        description="Optional rows for grid matrices."
    )
    columns: list[I18nText] | None = Field(
        default=None,
        description="Optional columns for grid matrices."
    )

    @model_validator(mode="after")
    def validate_block_consistency(self) -> PromptBlock:
        """Strict validation for PromptBlock relations and logical constraints."""
        # Fail-fast: Cannot allow decimals on non-numeric types
        if self.allow_decimals and self.type not in ["numeric", "string"]: # string permitted for BARS format
            from backend_v2.exceptions import AppException, ErrorCodes
            raise AppException(
                message=f"PromptBlock '{self.id}': allow_decimals is only valid for numeric logic.",
                details={"error_code": ErrorCodes.VALIDATION_FAILED},
                status_code=400
            )
        return self


class ChatMessageDTO(BaseModel):
    """Schema for a single parsed chat message."""
    role: str = Field(description="The role of the speaker (e.g. 'user' or 'ai').")
    content: str = Field(description="The message text.")

class ChatHistoryDTO(BaseModel):
    """Strict schema for a complete parsed chat sequence."""
    conversation: list[ChatMessageDTO] = Field(description="List of messages in chronological order.")


class DataDictionaryField(BaseModel):
    """UI Hints mapping for dynamic form generation (SDUI)."""

    field_id: str
    component_type: ComponentType = Field(description="E.g., 'slider', 'text_input', 'dropdown'")
    options: list[dict[str, Any]] | None = None
    validation_rules: dict[str, Any] | None = None


class ModelProfile(BaseModel):
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

class SystemConfigModelRegistry(BaseModel):
    """V2 Flattened Model Registry System Config."""
    id: str = Field(description="System config ID")
    slug: str = Field(description="Slug identifier")
    type: str = Field(default="model_registry", description="Type of config")
    models: dict[str, ModelProfile] = Field(
        description="Dictionary mapping generic role names to specific ModelProfiles"
    )

class Step(BaseModel):
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
            raise AppException(
                message=f"Step '{self.slug}' must define at least one prompt_block.",
                details={"error_code": ErrorCodes.VALIDATION_FAILED},
                status_code=400
            )
        return self

class StepRule(BaseModel):
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

class Role(BaseModel):
    """Role definition that locks physical models and pre_hooks."""
    id: str
    name: I18nText
    model_role: str = Field(description="Maps to SystemConfig.model_mappings (e.g., \"analyst_model\").")
    pre_hooks: list[str] = Field(default_factory=list, description="List of registered hook logic to run BEFORE llm.")
    post_hooks: list[str] = Field(default_factory=list, description="List of registered hook logic to run AFTER llm.")

class Workflow(BaseModel):
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
                    raise AppException(
                        message=f"Cyclic dependency detected involving step: {step.id}",
                        details={"error_code": ErrorCodes.VALIDATION_FAILED},
                        status_code=400
                    )

        return self


class FrozenContext(BaseModel):
    """Deep copy of context state at execution time for auditability."""
    compiled_prompts: dict[str, str] = Field(
        default_factory=dict, description="Prompts sent to LLM.")
    injected_theory: dict[str, Any] = Field(
        default_factory=dict, description="Fetched theory texts.")
    generated_schemas: dict[str, dict[str, Any]] = Field(
        default_factory=dict, description="JSON schemas used.")
    ui_hints_snapshot: dict[str, DataDictionaryField] = Field(
        default_factory=dict, description="UI rendering instructions.")


class ExecutionCreate(BaseModel):
    """Schema for initiating a new workflow execution."""
    workflow_id: str = Field(description="ID of the workflow to execute")
    raw_inputs: dict[str, Any] = Field(default_factory=dict, description="User provided raw inputs")


class ExecutionRecord(BaseModel):
    """Record of a workflow execution, including the frozen context and results."""
    id: str = Field(description="Execution ID, usually a uuid")
    workflow_id: str = Field(description="Workflow ID")
    status: ExecutionStatus = Field(description="Current status of execution")
    raw_inputs: dict[str, Any] = Field(
        default_factory=dict, description="Raw user inputs by role")
    frozen_context: FrozenContext = Field(
        default_factory=FrozenContext, description="Immutable snapshot of context")
    results: dict[str, Any] = Field(
        default_factory=dict, description="Step-by-step LLM output results")
    error: str | None = Field(default=None, description="Error message if failed")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC creation timestamp")
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC update timestamp")

# --- Legacy Collection Mapping for UI CRUD ---

class Observation(BaseModel):
    """Legacy V1 Observation mapped to V2 Strict structure."""
    id: str = Field(description="Unique Observation ID")
    workflow_id: str | None = Field(default=None, description="Associated Workflow ID")
    name: str | None = Field(default=None, description="Observation name")
    type: str | None = Field(default=None, description="Observation type")
    config: dict[str, Any] = Field(default_factory=dict, description="Configuration rules")


class OutputConfig(BaseModel):
    """Legacy V1 OutputConfig mapped to V2 Strict structure."""
    id: str = Field(description="Unique Output Config ID")
    workflow_id: str | None = Field(default=None, description="Associated Workflow ID")
    format: str | None = Field(default=None, description="Output format (e.g., pdf, markdown)")
    template: str | None = Field(default=None, description="Template identifier or content")


class Reference(BaseModel):
    """Legacy V1 Reference mapped to V2 Strict structure."""
    id: str = Field(description="Unique Reference ID")
    slug: str | None = Field(default=None, description="Legacy slug")
    type: str | None = Field(default=None, description="Reference type")
    definition: str = Field(description="Full reference definition")
    short_citation: str | None = Field(default=None, description="Short citation format")
    source_file: str | None = Field(default=None, description="Original source file name")
    ingested_at: datetime | str | None = Field(default=None, description="Time of ingestion")
