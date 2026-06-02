"""Base domain models.

This module contains the foundational Pydantic models used by all other domain entities.
It includes Metadata, ReasoningTrace, and UsageRecord.
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from fastapi import status
from pydantic import Field, field_validator

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.usage import TokenUsage

logger = logging.getLogger(__name__)


class AuditLogEntry(V2CoreBase):
    """Strict model for a single audit log entry."""

    timestamp: datetime = Field(..., description="Timestamp of the log entry.")
    level: str = Field(..., min_length=1, description="Log level (INFO, WARN, ERROR).")
    message: str = Field(..., min_length=1, description="Log message.")
    context: dict[str, Any] | None = Field(default=None, description="Additional context.")


class Metadata(V2CoreBase):
    """Metadata container for agent outputs."""

    luontiaika: datetime = Field(
        ..., description="Creation timestamp.", json_schema_extra={"x-ui-label": "Creation Time"}
    )
    agentti: str = Field(..., min_length=1, description="Agent name.", json_schema_extra={"x-ui-label": "Agent Name"})
    vaihe: int = Field(default=0, description="Step number.", json_schema_extra={"x-ui-label": "Step Number"})
    versio: str = Field(default="1.0", description="Schema version.", json_schema_extra={"x-ui-label": "Version"})
    suoritus_ymparisto: str = Field(
        ...,
        min_length=1,
        description="Environment.",
        json_schema_extra={"x-ui-label": "Environment"},
    )
    organization_id: str | None = Field(
        default=None, description="Organization ID.", json_schema_extra={"x-ui-label": "Organization ID"}
    )
    user_id: str | None = Field(default=None, description="User ID.", json_schema_extra={"x-ui-label": "User ID"})
    execution_id: str | None = Field(
        default=None, description="Execution ID.", json_schema_extra={"x-ui-label": "Execution ID"}
    )
    step_id: str | None = Field(default=None, description="Step ID.", json_schema_extra={"x-ui-label": "Step ID"})
    model: str | None = Field(default=None, description="Model used.", json_schema_extra={"x-ui-label": "Model"})
    provider: str | None = Field(
        default=None, description="Model provider.", json_schema_extra={"x-ui-label": "Provider"}
    )
    duration_ms: int | None = Field(
        default=None,
        description="Execution duration in milliseconds.",
        json_schema_extra={"x-ui-label": "Duration (ms)"},
    )
    workflow: str | None = Field(
        default=None, description="Workflow name.", json_schema_extra={"x-ui-label": "Workflow"}
    )
    audit_logs: list[AuditLogEntry] | None = Field(
        default=None, description="Audit logs.", json_schema_extra={"x-ui-label": "Audit Logs"}
    )
    token_usage: TokenUsage | None = Field(default=None, description="Token usage statistics from language model.")
    system_fingerprint: str | None = Field(
        default=None,
        description="System fingerprint identifying exact model weights used.",
        json_schema_extra={"x-ui-label": "System Fingerprint"},
    )
    provider_metadata: dict[str, Any] | None = Field(
        default=None,
        description="Raw provider specific metadata (e.g. rate limits, safety ratings, citations).",
        json_schema_extra={"x-ui-label": "Provider Metadata"},
    )

    @field_validator("luontiaika", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> Any:
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v


class ReasoningTraceDTO(V2CoreBase):
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
    reasoning_token: str | None = Field(
        default=None,
        description="Encrypted Reasoning Blob / Thought signature from the LLM.",
        json_schema_extra={"x-ui-hidden": True},
    )

    @field_validator("thought_process", "conclusion")
    @classmethod
    def validate_hallucinations(cls, v: str) -> str:
        if not v or not v.strip():
            msg = "Field cannot be empty."
            logger.error("[BaseDomainModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        clean_v = v.strip().lower()
        if clean_v in {"null", "none", "n/a", "ei saatavilla"}:
            msg = f"LLM returned an invalid empty-equivalent string: '{v}'"
            logger.error("[BaseDomainModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        return v.strip()

    @field_validator("confidence_score")
    @classmethod
    def validate_confidence_score(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            msg = f"Confidence score must be between 0.0 and 1.0, got {v}"
            logger.error("[BaseDomainModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
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


class UsageRecord(V2CoreBase):
    """Immutable record of LLM token usage and cost."""

    id: str = Field(
        default_factory=lambda: f"usg_{uuid.uuid4().hex[:8]}",
        min_length=1,
        description="Unique ID for the usage event.",
        json_schema_extra={"x-ui-label": "ID"},
    )
    org_id: str = Field(
        ...,
        min_length=1,
        description="Organization ID.",
        json_schema_extra={"x-ui-label": "Organization ID"},
    )
    user_id: str = Field(..., min_length=1, description="User ID.", json_schema_extra={"x-ui-label": "User ID"})
    model: str = Field(..., min_length=1, description="Model name.", json_schema_extra={"x-ui-label": "Model"})
    input_tokens: int = Field(
        ...,
        ge=0,
        description="Input token count.",
        json_schema_extra={"x-ui-label": "Input Tokens"},
    )
    output_tokens: int = Field(
        ..., ge=0, description="Output token count.", json_schema_extra={"x-ui-label": "Output Tokens"}
    )
    cached_tokens: int = Field(
        default=0, ge=0, description="Cached tokens.", json_schema_extra={"x-ui-label": "Cached Tokens"}
    )
    cache_creation_input_tokens: int = Field(
        default=0,
        ge=0,
        description="Tokens written to cache.",
        json_schema_extra={"x-ui-label": "Cache Creation Tokens"},
    )
    reasoning_tokens: int = Field(
        default=0, ge=0, description="Reasoning tokens.", json_schema_extra={"x-ui-label": "Reasoning Tokens"}
    )
    latency_ms: int | None = Field(
        default=None, description="Request latency in ms.", json_schema_extra={"x-ui-label": "Latency (ms)"}
    )
    finish_reason: str | None = Field(
        default=None, description="Finish reason.", json_schema_extra={"x-ui-label": "Finish Reason"}
    )
    system_fingerprint: str | None = Field(
        default=None, description="System fingerprint.", json_schema_extra={"x-ui-label": "System Fingerprint"}
    )
    cost_usd: float = Field(..., ge=0.0, description="Cost in USD.", json_schema_extra={"x-ui-label": "Cost (USD)"})
    estimated_savings_usd: float = Field(
        default=0.0, ge=0.0, description="Estimated savings.", json_schema_extra={"x-ui-label": "Savings (USD)"}
    )
    timestamp: datetime = Field(..., description="Timestamp of usage.", json_schema_extra={"x-ui-label": "Timestamp"})

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> Any:
        if isinstance(v, str):
            # Parse explicit ISO strings in strict mode
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v
