from typing import Any
from pydantic import BaseModel, ConfigDict, Field, field_validator

class AgentDefinition(BaseModel):
    """Schema for agent metadata exposed by discovery endpoint."""
    name: str
    class_name: str = Field(..., alias="class")
    description: str
    model: str
    input_schema: dict[str, Any] | None = None
    output_schema: dict[str, Any] | None = None

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("name", "class_name", "description", "model")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()

class AgentRunResponse(BaseModel):
    """Schema for single agent execution result."""
    agent: str
    result: Any  # The result might be a complex object or dict, but we wrap it.

    model_config = ConfigDict(frozen=True)

    @field_validator("agent")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()
