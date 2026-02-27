from typing import Annotated, Any

from pydantic import BaseModel, Field

from backend.models.workflow import WorkflowStep


class ValidationResponse(BaseModel):
    """Result of a connection validation check."""

    valid: Annotated[bool, Field(description="Whether the connection is valid.")]
    reason: Annotated[str | None, Field(description="Reason for validity or failure.")] = None


class CompilationResponse(BaseModel):
    """Result of a fusion compilation."""

    status: Annotated[str, Field(description="Compilation status (e.g. 'compiled').")]
    composite_step_id: Annotated[str, Field(description="The ID of the resulting composite step.")]
    new_steps: Annotated[list[str], Field(description="The updated list of step IDs in the workflow.")]


class WorkflowTemplate(BaseModel):
    """Model representing an empty workflow template."""

    name: str
    description: str
    steps: list[str]
    default_model_mapping: dict[str, str]
    ui_schema: dict[str, Any]


class AgentMetadataDTO(BaseModel):
    """Metadata for an available agent."""

    name: str = Field(description="Agent class name.")
    description: str = Field(description="Agent docstring/description.")
    inputs: list[str] = Field(description="List of required input keys.")
    outputs: list[str] = Field(description="List of produced output keys.", default_factory=list)


class FusionRuleDTO(BaseModel):
    """Rule for prompt fusion."""

    composite_step_id: str
    name: str
    replaces_components: list[str]
    min_steps: int


class SeedDataResponse(BaseModel):
    """Full seed data configuration."""

    components: list[dict[str, Any]]
    steps: list[dict[str, Any]]
    workflows: list[dict[str, Any]]


class ComponentSchemaResponse(BaseModel):
    """JSON Schema wrapper."""

    schema_data: dict[str, Any] = Field(alias="schema")


class PlaygroundRequest(BaseModel):
    """Payload for executing a prompt in the playground."""

    system_instruction: str = Field(description="System prompt template.")
    user_message: str = Field(description="User message.")
    variables: dict[str, str] = Field(default_factory=dict, description="Variables to inject into system prompt.")
    strategy: str = Field(default="playground_test", description="The SSOT execution strategy to use (e.g. 'playground_test').")


class PlaygroundResponse(BaseModel):
    """Response from the playground execution."""

    content: str = Field(description="The LLM response content.")
    usage: dict[str, Any] | None = Field(default=None, description="Token usage stats.")


class StepDTO(BaseModel):
    """Generic Step Configuration."""

    id: str
    name: str | None = None
    task_key: str
    description: str | None = None
    config: dict[str, Any] | None = None
    inputs: dict[str, str] = {}
    model_config = {"extra": "forbid"}


class StepUpdateRequest(BaseModel):
    """Payload for updating a step configuration."""

    name: Annotated[str | None, Field(description="New step name.")] = None
    config: Annotated[dict[str, Any] | None, Field(description="Updated execution config.")] = None


class CustomStepCreateRequest(BaseModel):
    """Payload for creating a custom step."""

    component_type: Annotated[str, Field(description="Base component type (e.g. 'Judge', 'Analyst').")]
    name_hint: Annotated[str | None, Field(description="Optional name override.")] = None


class StepPreviewResponse(BaseModel):
    """Response model for step prompt preview."""

    system_instruction: str = Field(
        ..., description="The full system prompt.", json_schema_extra={"x-ui-label": "System Instruction"}
    )
    user_prompt: str = Field(
        ..., description="The user prompt template logic.", json_schema_extra={"x-ui-label": "User Prompt"}
    )
    agent_class: str = Field(..., description="The agent component class.")


class GeneratedIdResponse(BaseModel):
    """Response for ID generation."""

    id: str


class BuilderWorkflowCreateRequest(BaseModel):
    """Payload for creating a new workflow."""

    name: Annotated[str, Field(description="Name of the new workflow.")]
    description: Annotated[str, Field(description="Optional description.")] = ""
    steps: Annotated[list[str], Field(description="List of step IDs.")] = []
    default_model_mapping: Annotated[dict[str, str] | None, Field(description="Initial model mapping.")] = {}
    ui_schema: Annotated[dict[str, Any] | None, Field(description="UI Layout metadata.")] = {}
    is_public: Annotated[bool, Field(description="If True, visible to all tenants (System Only).")] = False
    status: Annotated[str, Field(description="Lifecycle status.")] = "draft"
    version: Annotated[int, Field(description="Version number.")] = 1
    scoring_logic: Annotated[list[dict[str, Any]], Field(description="Scoring configuration.")] = []


class WorkflowUpdateRequest(BaseModel):
    """Payload for updating an existing workflow."""

    name: Annotated[str | None, Field(description="New name.")] = None
    description: Annotated[str, Field(description="New description.")] = ""
    steps: Annotated[list[str] | None, Field(description="New step sequence IDs.")] = None
    ui_schema: Annotated[dict[str, Any] | None, Field(description="New UI metadata.")] = None
    default_model_mapping: Annotated[dict[str, str] | None, Field(description="Updated model mapping.")] = None
    is_public: Annotated[bool | None, Field(description="Update visibility.")] = None
    status: Annotated[str | None, Field(description="Update status.")] = None
    version: Annotated[int | None, Field(description="Update version.")] = None
    scoring_logic: Annotated[list[dict[str, Any]] | None, Field(description="Updated scoring configuration.")] = None


class CopyWorkflowRequest(BaseModel):
    """Payload for copying a workflow."""

    new_name: Annotated[str, Field(description="Name for the copy.", json_schema_extra={"x-ui-label": "Workflow Name"})]


class ChainPreviewResponse(BaseModel):
    """Response model for workflow chain preview."""

    markdown_content: str = Field(
        ...,
        description="The full Markdown concatenation of all step prompts.",
        json_schema_extra={"x-ui-label": "Chain Content"},
    )


class WorkflowResponse(BaseModel):
    """Full workflow configuration."""

    id: str
    name: str
    description: str = ""
    steps: list[WorkflowStep]  # Expanded steps can be complex
    default_model_mapping: dict[str, str] = {}
    ui_schema: dict[str, Any] = {}
    is_public: bool = False
    status: str = "draft"
    version: int = 1
    scoring_logic: list[dict[str, Any]] = []
    created_at: Any | None = None  # allow datetime or string
    updated_at: Any | None = None
    organization_id: str
    model_config = {"extra": "allow"}


class BuilderWorkflowDeleteResponse(BaseModel):
    """Response for workflow deletion."""

    status: str
    deleted_steps: list[str]
