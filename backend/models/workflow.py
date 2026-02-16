from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WorkflowStep(BaseModel):
    """Represents a single step in a workflow execution.

    This model defines the task to be executed and how data maps
    from the workflow state into the task's input schema.
    """

    id: str = Field(
        ...,
        description="Unique step identifier, e.g., 'safety_check'",
        json_schema_extra={"x-ui-label": "ID"},
    )
    task_key: str = Field(
        ...,
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
    hoist_keys: list[str] = Field(
        default_factory=list,
        description="Defines which keys from the task's result should be promoted to the top-level execution state",
        json_schema_extra={"x-ui-label": "Hoist Keys"},
    )

    model_config = ConfigDict(frozen=True, strict=True)

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

    id: str = Field(..., description="Unique Workflow ID, e.g., 'comprehensive_audit_v1'")
    name: str = Field(
        "Untitled Workflow",
        min_length=3,
        description="Human-readable name for the workflow",
        json_schema_extra={
            "x-ui-widget": "text",
            "x-ui-label": "Workflow Name",
        },
    )
    steps: list[WorkflowStep] = Field(
        default_factory=list,
        description="Ordered list of Step Definitions",
        json_schema_extra={
            "x-ui-widget": "reorderable-list",
            "x-ui-group": "Steps",
        },
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
            "x-ui-label": "Status"
        }
    )
    version: int = Field(1, description="Numeric version")
    is_public: bool = Field(
        False,
        description="If checked, visible to all tenants (System Only)",
        json_schema_extra={"x-ui-label": "Publicly Available"}
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
