from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WorkflowStep(BaseModel):
    """Represents a single step in a workflow execution.

    This model defines the task to be executed and how data maps
    from the workflow state into the task's input schema.
    """

    id: str = Field(..., description="Unique step identifier, e.g., 'safety_check'")
    task_key: str = Field(..., description="Registry Task Name (matches @register_task name)")
    inputs: dict[str, str] = Field(
        default_factory=dict, description="Maps task inputs to state values. Example: {'text': '$inputs.history_text'}"
    )
    config: dict[str, Any] = Field(default_factory=dict, description="Optional static config for the task")
    hoist_keys: list[str] = Field(
        default_factory=list,
        description="Defines which keys from the task's result should be promoted to the top-level execution state",
    )

    model_config = ConfigDict(extra="ignore")


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
    steps: list[str] = Field(
        default_factory=list,
        description="Ordered list of Step IDs",
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
    ui_schema: dict[str, Any] = Field(
        default_factory=dict, description="JSON Schema for the dynamic input form"
    )

    model_config = ConfigDict(extra="ignore")
