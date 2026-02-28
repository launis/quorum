import uuid
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator


class WorkflowStep(BaseModel):
    """Represents a single step in a workflow execution.

    This model defines the task to be executed and how data maps
    from the workflow state into the task's input schema.
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique step identifier, e.g., 'safety_check'",
        json_schema_extra={"x-ui-label": "ID"},
    )
    slug: str | None = Field(
        default=None,
        description="Legacy human-readable identifier",
        json_schema_extra={"x-ui-label": "Slug"},
    )
    name: str = Field(
        ...,
        description="Human-readable name of the step",
        json_schema_extra={"x-ui-label": "Step Name"},
    )
    description: str | None = Field(
        None,
        description="Optional description of the step's purpose",
        json_schema_extra={"x-ui-label": "Description"},
    )
    task_key: str = Field(
        ...,
        validation_alias=AliasChoices("task_key", "component"),
        description="Registry Task Name (matches @register_task name)",
        json_schema_extra={"x-ui-label": "Task Key"},
    )
    inputs: dict[str, str] = Field(
        default_factory=dict,
        description="Maps task inputs to state values. Example: {'text': '$inputs.history_text'}",
        json_schema_extra={"x-ui-label": "Inputs"},
    )
    config: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional static config for the task",
        json_schema_extra={"x-ui-label": "Configuration"},
    )
    is_missing_registry: bool = Field(
        default=False,
        description="UI Helper: True if this step references a task_key not in the backend registry.",
    )

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    @field_validator("id", "task_key")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class ComponentScoringRule(BaseModel):
    """Defines how a specific component contributes to a score."""

    component_id: str = Field(
        ...,
        description="ID of the component being scored",
        json_schema_extra={"x-ui-label": "Component ID"},
    )
    weight: float = Field(
        1.0,
        description="Weight multiplier for this component",
        json_schema_extra={"x-ui-label": "Weight"},
    )
    metric_key: str = Field(
        ...,
        description="Key of the metric to extract (e.g., 'compliance_score')",
        json_schema_extra={"x-ui-label": "Metric Key"},
    )

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("component_id", "metric_key")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class ScoringLogic(BaseModel):
    """Named collection of scoring rules."""

    label: str = Field(
        ...,
        description="Display label for this scoring logic",
        json_schema_extra={"x-ui-label": "Label"},
    )
    rules: list[ComponentScoringRule] = Field(
        default_factory=list,
        description="List of rules defining the score",
        json_schema_extra={"x-ui-label": "Rules"},
    )

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("label")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class WorkflowDefinition(BaseModel):
    """Defines the structure of a workflow stored in the DB.

    A workflow is an ordered sequence of steps that process data
    transformation through registered tasks.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique Workflow ID, e.g., 'comprehensive_audit_v1'")
    slug: str | None = Field(
        default=None,
        description="Legacy human-readable identifier",
        json_schema_extra={"x-ui-label": "Slug"},
    )
    name: str = Field(
        "Untitled Workflow",
        min_length=3,
        description="Human-readable name for the workflow",
        json_schema_extra={
            "x-ui-widget": "text",
            "x-ui-label": "Workflow Name",
        },
    )
    steps: list[str] = Field(
        default_factory=list,
        description="Ordered list of step IDs to execute",
        json_schema_extra={"x-ui-widget": "reorderable-list", "x-ui-group": "Steps", "x-ui-label": "Steps"},
    )
    description: str = Field(
        ...,
        description="Human-readable description of what this workflow does",
        json_schema_extra={
            "x-ui-widget": "textarea",
            "x-ui-label": "Description",
        },
    )
    status: str = Field(
        "draft",
        description="Workflow lifecycle status",
        json_schema_extra={
            "x-ui-widget": "select",
            "enum": ["draft", "active", "deprecated", "archived"],
            "x-ui-label": "Status",
        },
    )
    version: int = Field(1, description="Numeric version")
    is_public: bool = Field(
        False,
        description="If checked, visible to all tenants (System Only)",
        json_schema_extra={"x-ui-label": "Publicly Available"},
    )
    organization_id: str = Field(
        ...,
        description="Organization ID this workflow belongs to (or 'system')",
        json_schema_extra={"x-ui-label": "Organization ID"},
    )
    scoring_logic: list[ScoringLogic] = Field(
        default_factory=list,
        description="Defined scoring methods for this workflow",
        json_schema_extra={
            "x-ui-group": "Scoring Logic",
            "x-ui-label": "Scoring Logic",
        },
    )
    ui_schema: dict[str, Any] = Field(
        default_factory=dict,
        description="JSON Schema for the dynamic input form",
        json_schema_extra={"x-ui-label": "UI Schema"},
    )

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("id", "name", "description")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


# --- EVALUATION MODELS (Imported from domain.evaluation) ---
