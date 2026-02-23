from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ComponentUpdate(BaseModel):
    """Payload for updating a configuration component."""

    content: Annotated[
        str | dict[str, Any] | list[Any],
        Field(description="The template content (prompt text, rule text, or config object)."),
    ]
    description: Annotated[str | None, Field(description="Metadata description.")] = None
    citation: Annotated[str | None, Field(description="Short citation anchor.")] = None
    citation_full: Annotated[str | None, Field(description="Complete bibliographic reference.")] = None
    type: Annotated[
        str | None,
        Field(description="Component categorization (e.g. 'mandate', 'prompt', 'evaluation_matrix')."),
    ] = None

    model_config = {
        "json_schema_extra": {
            "properties": {
                "content": {"x-ui-label": "Content"},
                "description": {"x-ui-label": "Description"},
                "citation": {"x-ui-label": "Citation"},
                "citation_full": {"x-ui-label": "Citation (Full)"},
                "type": {"x-ui-label": "Type"},
            }
        }
    }


class ComponentCreate(BaseModel):
    """Payload for creating a new component."""

    id: Annotated[str, Field(description="Unique Identifier for the component.")]
    name: Annotated[str, Field(description="Human readable name.")]
    type: Annotated[str, Field(description="Component Type (header, prompt, evaluation_matrix, etc).")]
    content: Annotated[str | dict[str, Any] | list[Any], Field(description="The content (text or JSON object).")]
    description: Annotated[str | None, Field(description="Description of purpose.")] = None
    citation: Annotated[str | None, Field(description="Short citation.")] = None
    citation_full: Annotated[str | None, Field(description="Full citation.")] = None
    module: Annotated[str | None, Field(description="Source module (legacy).")] = "config"
    component_class: Annotated[str | None, Field(description="Class name.")] = "ConfigComponent"

    model_config = {
        "json_schema_extra": {
            "properties": {
                "id": {"x-ui-label": "ID"},
                "name": {"x-ui-label": "Name"},
                "type": {"x-ui-label": "Type"},
                "content": {"x-ui-label": "Content"},
                "description": {"x-ui-label": "Description"},
                "citation": {"x-ui-label": "Citation"},
                "citation_full": {"x-ui-label": "Citation (Full)"},
                "module": {"x-ui-label": "Module"},
                "component_class": {"x-ui-label": "Component Class"},
            }
        }
    }


class RegistryComponentItem(BaseModel):
    """Schema for a component item in the registry list."""

    id: Annotated[
        str,
        Field(description="Component ID", json_schema_extra={"x-ui-label": "ID"}),
    ]
    name: Annotated[
        str,
        Field(description="Meaningful Label", json_schema_extra={"x-ui-label": "Label"}),
    ]
    type: Annotated[
        str,
        Field(description="Type category", json_schema_extra={"x-ui-label": "Type"}),
    ]
    description: Annotated[
        str | None,
        Field(
            description="Short description",
            json_schema_extra={"x-ui-label": "Description"},
        ),
    ] = None
    content: Annotated[
        Any,
        Field(description="The actual content", json_schema_extra={"x-ui-label": "Content"}),
    ] = None
    citation: Annotated[
        str | None,
        Field(description="Short reference", json_schema_extra={"x-ui-label": "Citation"}),
    ] = None


# --- Strict Polymorphic Component Models ---


class AgentBaseResponse(BaseModel):
    """Base fields for all components."""

    id: str
    name: str | None = None
    description: str | None = None
    citation: str | None = None
    citation_full: str | None = None
    module: str | None = None
    # 'class' is a reserved keyword, so we use component_class.
    # backward compatibility alias removed. Data must be migrated.
    component_class: str | None = Field(default=None)
    class_name: str | None = None  # Explicitly allow class_name found in seed data
    registered_at: str | None = None

    model_config = ConfigDict(extra="forbid")


class AgentComponentResponse(AgentBaseResponse):
    """Strict model for Agents/Processors (No content allowed)."""

    type: Literal["agent", "processor"]
    content: None = None

    model_config = ConfigDict(extra="forbid")


class MatrixContentDTO(BaseModel):
    """Strict nested model for Matrix content parsing."""
    scale: dict[str, int] = Field(default_factory=dict)
    criteria: list[dict[str, Any]] = Field(default_factory=list)
    role_description: str | None = None

class MatrixComponentResponse(AgentBaseResponse):
    """Strict model for Evaluation Matrices."""

    type: Literal["evaluation_matrix"]
    content: MatrixContentDTO

    model_config = ConfigDict(extra="forbid")


class ConfigComponentResponse(AgentBaseResponse):
    """Strict model for List-based Configs (Output Config, Knowledge Base)."""

    type: Literal["output_config", "knowledge_base"]
    content: list[Any]
    ui_hints: dict[str, Any] | None = Field(
        default=None,
        description="Optional UI hints/metadata (e.g., icons, grouping) not used by backend logic.",
    )

    model_config = ConfigDict(extra="forbid")


class TextComponentResponse(AgentBaseResponse):
    """Strict model for Text-based components (Rules, Prompts, etc)."""

    type: str  # Catch-all for text types
    content: str

    model_config = ConfigDict(extra="forbid")

    @field_validator("type")
    @classmethod
    def validate_known_types(cls, v: str) -> str:
        # STRICT: Ensure Agents/Processors never validate as TextComponentResponse
        # even if they somehow have string content.
        if v in ("agent", "processor"):
            raise ValueError(
                f"Type '{v}' cannot be a TextComponentResponse (must use AgentComponentResponse and have NO content)."
            )
        return v


# Strict SSOT Refactor (Feb 2026): Polymorphic Union dismantled.
# Components table now strictly contains Text components (Prompts, Mandates, etc).
# Agents, Matrices, and Output Configs have their own explicit APIs and Models.
ComponentResponse = TextComponentResponse


class ComponentDeleteResponse(BaseModel):
    """Response for component deletion."""

    status: str
    id: str


class KnowledgeIngestResponse(BaseModel):
    """Response for starting an ingestion job."""

    job_id: str


class KnowledgeJobStatusResponse(BaseModel):
    """Status of an ingestion job."""

    job_id: str
    status: str
    progress: int
    stage: str
    result: Any | None = None
    error: str | None = None
    error_code: str | None = None


class KnowledgeResetResponse(BaseModel):
    """Response for knowledge base reset."""

    message: str


class ModelOptionsResponse(BaseModel):
    """Available model options per provider."""

    options: dict[str, list[str]]


class DimensionDefinition(BaseModel):
    """Model definition for an evaluation dimension."""

    id: Annotated[str, Field(description="Unique dimension ID (e.g. 'analyysi').")]
    label: Annotated[str, Field(description="Human readable default label.")]
    description: Annotated[str | None, Field(description="Explanation of what this measures.")] = None
    is_system: Annotated[bool, Field(description="If true, is a core system dimension.")] = False


class DimensionDeleteResponse(BaseModel):
    """Response for dimension deletion."""

    status: str
    id: str


class SchemaInfo(BaseModel):
    """Schema information wrapper."""

    schema_def: dict[str, Any] = Field(alias="schema")
    example: Any | None = None


class SchemaListResponse(BaseModel):
    """List of all available schemas."""

    items: dict[str, SchemaInfo]


class SchemaResponse(BaseModel):
    """Single schema definition response."""

    model_name: str
    schema_def: dict[str, Any]


class StepDefinition(BaseModel):
    """Step configuration definition."""

    id: Annotated[str, Field(description="Unique step identifier", json_schema_extra={"x-ui-label": "Step ID"})]
    name: Annotated[str, Field(description="Human-readable name", json_schema_extra={"x-ui-label": "Nimi"})]
    description: Annotated[str | None, Field(description="Description", json_schema_extra={"x-ui-label": "Kuvaus"})] = (
        None
    )
    task_key: Annotated[str, Field(description="Task Key (DB source)", json_schema_extra={"x-ui-label": "Agentti"})] = (
        "analyst"
    )
    config: Annotated[
        dict[str, Any], Field(description="Configuration (DB source)", json_schema_extra={"x-ui-label": "Asetukset"})
    ] = {}
    inputs: Annotated[
        dict[str, str], Field(description="Default Input Mapping", json_schema_extra={"x-ui-label": "Oletussyötteet"})
    ] = {}

    model_config = ConfigDict(extra="forbid")


class StepDeleteResponse(BaseModel):
    """Response for step deletion."""

    status: str
    id: str


class WorkflowConfigDefinition(BaseModel):
    """Workflow configuration definition."""

    id: Annotated[str, Field(description="Workflow UUID/Slug")]
    name: Annotated[str, Field(description="Workflow Name")]
    description: Annotated[str | None, Field(description="Description")] = None
    sequence: Annotated[list[str], Field(description="Ordered list of Step IDs")] = []
    # steps field might be hydrated or just references. In config view, usually hydration is needed.
    steps: Annotated[
        list[dict[str, Any]] | list[StepDefinition], Field(description="Hydrated steps or references")
    ] = []
    ui_schema: Annotated[dict[str, Any] | None, Field(description="Dynamic UI Schema")] = None
    default_model_mapping: Annotated[dict[str, str] | None, Field(description="Step-Model map")] = {}


class WorkflowConfigCreate(BaseModel):
    """Payload for creating a workflow."""

    id: Annotated[str, Field(description="New Workflow UUID/Slug")]
    name: Annotated[str, Field(description="Workflow Name")]
    sequence: Annotated[list[str], Field(description="List of Step IDs")] = []
    description: Annotated[str | None, Field(description="Description")] = None
    default_model_mapping: Annotated[dict[str, str] | None, Field(description="Step-Model map")] = {}


class WorkflowConfigUpdate(BaseModel):
    """Payload for updating a workflow."""

    steps: Annotated[list[dict[str, Any]] | None, Field(description="Complete list of step configurations.")] = None
    sequence: Annotated[list[str] | None, Field(description="Ordered list of Step IDs.")] = None
    description: Annotated[str | None, Field(description="User-facing workflow description.")] = None
    default_model_mapping: Annotated[dict[str, str] | None, Field(description="Map of StepID -> ModelStrategyKey.")] = (
        None
    )


class ConfigWorkflowDeleteResponse(BaseModel):
    """Response for workflow deletion."""

    status: str
    id: str


class ValidationReportResponse(BaseModel):
    """Workflow validation report."""

    valid: bool
    errors: list[str]
    trace: list[str]
    final_state_keys: list[str]
