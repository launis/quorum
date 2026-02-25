"""Base domain models.

This module contains the foundational Pydantic models used by all other domain entities.
It includes Metadata, ReasoningTrace, and UsageRecord.
"""

from datetime import datetime
from typing import Any
import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AuditLogEntry(BaseModel):
    """Strict model for a single audit log entry."""

    timestamp: datetime = Field(..., description="Timestamp of the log entry.")
    level: str = Field(..., description="Log level (INFO, WARN, ERROR).")
    message: str = Field(..., description="Log message.")
    context: dict[str, Any] | None = Field(default=None, description="Additional context.")

    model_config = ConfigDict(frozen=True)

    @field_validator("level", "message")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class Metadata(BaseModel):
    """Metadata container for agent outputs."""

    luontiaika: datetime = Field(
        ..., description="Creation timestamp.", json_schema_extra={"x-ui-label": "Creation Time"}
    )
    agentti: str = Field(..., description="Agent name.", json_schema_extra={"x-ui-label": "Agent Name"})
    vaihe: int = Field(default=0, description="Step number.", json_schema_extra={"x-ui-label": "Step Number"})
    versio: str = Field(default="1.0", description="Schema version.", json_schema_extra={"x-ui-label": "Version"})
    suoritus_ymparisto: str = Field(..., description="Environment.", json_schema_extra={"x-ui-label": "Environment"})
    organization_id: str | None = Field(
        default=None, description="Organization ID.", json_schema_extra={"x-ui-label": "Organization ID"}
    )
    user_id: str | None = Field(
        default=None, description="User ID.", json_schema_extra={"x-ui-label": "User ID"}
    )
    execution_id: str | None = Field(
        default=None, description="Execution ID.", json_schema_extra={"x-ui-label": "Execution ID"}
    )
    step_id: str | None = Field(
        default=None, description="Step ID.", json_schema_extra={"x-ui-label": "Step ID"}
    )
    model: str | None = Field(
        default=None, description="Model used.", json_schema_extra={"x-ui-label": "Model"}
    )
    provider: str | None = Field(
        default=None, description="Model provider.", json_schema_extra={"x-ui-label": "Provider"}
    )
    duration_ms: int | None = Field(
        default=None, description="Execution duration in milliseconds.", json_schema_extra={"x-ui-label": "Duration (ms)"}
    )
    workflow: str | None = Field(
        default=None, description="Workflow name.", json_schema_extra={"x-ui-label": "Workflow"}
    )
    audit_logs: list[AuditLogEntry] | None = Field(
        default=None, description="Audit logs.", json_schema_extra={"x-ui-label": "Audit Logs"}
    )
    token_usage: dict[str, float | int] | None = Field(default=None, description="Token usage statistics from language model.")

    @field_validator("agentti", "suoritus_ymparisto")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()

    @field_validator("luontiaika", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> Any:
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v

    model_config = ConfigDict(frozen=True)


class ReasoningTraceDTO(BaseModel):
    """Data Transfer Object for LLM reasoning responses (Content Only).

    This contains the 'Reasoning' that the LLM generates.
    It DOES NOT contain system metadata (timestamps, versions) which must be injected by the Backend.
    """

    thought_process: str = Field(
        ...,
        description="Step-by-step thinking process leading to the result.",
        json_schema_extra={"x-ui-label": "Reasoning Process"},
    )
    conclusion: str = Field(
        ...,
        description="Synthesized conclusion or summary of the reasoning.",
        json_schema_extra={"x-ui-label": "Conclusion"},
    )
    confidence_score: float = Field(
        ...,
        description="Self-assessed confidence score (0.0 - 1.0).",
        json_schema_extra={"x-ui-label": "Confidence Score"},
    )

    model_config = ConfigDict(frozen=True)

    @field_validator("thought_process", "conclusion")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()

    @field_validator("confidence_score")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("Confidence score must be between 0.0 and 1.0.")
        return v


class ReasoningTrace(ReasoningTraceDTO):
    """Domain model with system-authoritative metadata.

    Inherits content from ReasoningTraceDTO and adds system-managed fields.
    LLMs never see or generate this model directly.
    """

    metadata: Metadata | None = Field(
        default=None,
        description="System metadata (Injected by Backend).",
        json_schema_extra={"x-ui-label": "Metadata"},
    )
    semanttinen_tarkistussumma: str | None = Field(
        default=None,
        description="Semantic checksum (Calculated by Backend).",
        json_schema_extra={"x-ui-label": "Checksum"},
    )

    model_config = ConfigDict(frozen=True, strict=True)


class UsageRecord(BaseModel):
    """Immutable record of LLM token usage and cost."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique ID for the usage event.", json_schema_extra={"x-ui-label": "ID"})
    org_id: str = Field(..., description="Organization ID.", json_schema_extra={"x-ui-label": "Organization ID"})
    user_id: str = Field(..., description="User ID.", json_schema_extra={"x-ui-label": "User ID"})
    model: str = Field(..., description="Model name.", json_schema_extra={"x-ui-label": "Model"})
    input_tokens: int = Field(..., description="Input token count.", json_schema_extra={"x-ui-label": "Input Tokens"})
    output_tokens: int = Field(
        ..., description="Output token count.", json_schema_extra={"x-ui-label": "Output Tokens"}
    )
    cost_usd: float = Field(..., description="Cost in USD.", json_schema_extra={"x-ui-label": "Cost (USD)"})
    timestamp: datetime = Field(..., description="Timestamp of usage.", json_schema_extra={"x-ui-label": "Timestamp"})

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> Any:
        if isinstance(v, str):
            # Fallback for ISO strings in strict mode
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("id", "org_id", "user_id", "model")
    @classmethod
    def validate_non_empty_strings(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()

    @field_validator("input_tokens", "output_tokens")
    @classmethod
    def validate_non_negative_int(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Token count cannot be negative.")
        return v

    @field_validator("cost_usd")
    @classmethod
    def validate_non_negative_float(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Cost cannot be negative.")
        return v
