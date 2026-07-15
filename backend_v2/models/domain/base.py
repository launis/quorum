"""Base domain models.

This module contains the foundational Pydantic models used by all other domain entities.
It includes Metadata, ReasoningTrace, and UsageRecord.
"""

import logging
import uuid
from datetime import datetime
from typing import Annotated, Any

from pydantic import Field, field_validator

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.usage import TokenUsage

logger = logging.getLogger(__name__)


class AuditLogEntry(V2CoreBase):
    """Strict model for a single audit log entry.

    Attributes:
        timestamp: Timestamp of the log entry.
        level: Log level (INFO, WARN, ERROR).
        message: Log message.
        context: Additional context.
    """

    timestamp: Annotated[datetime, Field(description="Timestamp of the log entry.")]
    level: Annotated[str, Field(min_length=1, description="Log level (INFO, WARN, ERROR).")]
    message: Annotated[str, Field(min_length=1, description="Log message.")]
    context: Annotated[dict[str, Any] | None, Field(description="Additional context.")] = None


class Metadata(V2CoreBase):
    """Metadata container for agent outputs.

    Attributes:
        luontiaika: Creation timestamp.
        agentti: Agent name.
        vaihe: Step number.
        versio: Schema version.
        suoritus_ymparisto: Environment.
        organization_id: Organization ID.
        user_id: User ID.
        execution_id: Execution ID.
        step_id: Step ID.
        model: Model used.
        provider: Model provider.
        duration_ms: Execution duration in milliseconds.
        workflow: Workflow name.
        audit_logs: Audit logs.
        token_usage: Token usage statistics from language model.
        system_fingerprint: System fingerprint identifying exact model weights used.
        provider_metadata: Raw provider specific metadata (e.g. rate limits, safety ratings, citations).
    """

    luontiaika: Annotated[
        datetime, Field(description="Creation timestamp.", json_schema_extra={"x-ui-label": "Creation Time"})
    ]
    agentti: Annotated[
        str, Field(min_length=1, description="Agent name.", json_schema_extra={"x-ui-label": "Agent Name"})
    ]
    vaihe: Annotated[int, Field(description="Step number.", json_schema_extra={"x-ui-label": "Step Number"})] = 0
    versio: Annotated[str, Field(description="Schema version.", json_schema_extra={"x-ui-label": "Version"})] = "1.0"
    suoritus_ymparisto: Annotated[
        str,
        Field(min_length=1, description="Environment.", json_schema_extra={"x-ui-label": "Environment"}),
    ]
    organization_id: Annotated[
        str | None, Field(description="Organization ID.", json_schema_extra={"x-ui-label": "Organization ID"})
    ] = None
    user_id: Annotated[str | None, Field(description="User ID.", json_schema_extra={"x-ui-label": "User ID"})] = None
    execution_id: Annotated[
        str | None, Field(description="Execution ID.", json_schema_extra={"x-ui-label": "Execution ID"})
    ] = None
    step_id: Annotated[str | None, Field(description="Step ID.", json_schema_extra={"x-ui-label": "Step ID"})] = None
    model: Annotated[str | None, Field(description="Model used.", json_schema_extra={"x-ui-label": "Model"})] = None
    provider: Annotated[
        str | None, Field(description="Model provider.", json_schema_extra={"x-ui-label": "Provider"})
    ] = None
    duration_ms: Annotated[
        int | None,
        Field(description="Execution duration in milliseconds.", json_schema_extra={"x-ui-label": "Duration (ms)"}),
    ] = None
    workflow: Annotated[
        str | None, Field(description="Workflow name.", json_schema_extra={"x-ui-label": "Workflow"})
    ] = None
    audit_logs: Annotated[
        list[AuditLogEntry] | None, Field(description="Audit logs.", json_schema_extra={"x-ui-label": "Audit Logs"})
    ] = None
    token_usage: Annotated[TokenUsage | None, Field(description="Token usage statistics from language model.")] = None
    system_fingerprint: Annotated[
        str | None,
        Field(
            description="System fingerprint identifying exact model weights used.",
            json_schema_extra={"x-ui-label": "System Fingerprint"},
        ),
    ] = None
    provider_metadata: Annotated[
        dict[str, Any] | None,
        Field(
            description="Raw provider specific metadata (e.g. rate limits, safety ratings, citations).",
            json_schema_extra={"x-ui-label": "Provider Metadata"},
        ),
    ] = None

    @field_validator("luontiaika", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> Any:
        """Parse ISO datetime strings.

        Args:
            v: Input value to parse.

        Returns:
            Parsed datetime object or original value.
        """
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v


class ReasoningTraceDTO(V2CoreBase):
    """Data Transfer Object for LLM reasoning responses (Content Only).

    This contains the 'Reasoning' that the LLM generates.
    It DOES NOT contain system metadata (timestamps, versions) which must be injected by the Backend.

    Attributes:
        thought_process: Step-by-step thinking process leading to the result.
        conclusion: Synthesized conclusion or summary of the reasoning.
        confidence_score: Self-assessed confidence score (0.0 - 1.0).
        reasoning_token: Encrypted Reasoning Blob / Thought signature from the LLM.
    """

    thought_process: Annotated[
        str,
        Field(
            description="Step-by-step thinking process leading to the result.",
            json_schema_extra={"x-ui-label": "Reasoning Process"},
        ),
    ]
    conclusion: Annotated[
        str,
        Field(
            description="Synthesized conclusion or summary of the reasoning.",
            json_schema_extra={"x-ui-label": "Conclusion"},
        ),
    ]
    confidence_score: Annotated[
        float,
        Field(
            description="Self-assessed confidence score (0.0 - 1.0).",
            json_schema_extra={"x-ui-label": "Confidence Score"},
        ),
    ]
    reasoning_token: Annotated[
        str | None,
        Field(
            description="Encrypted Reasoning Blob / Thought signature from the LLM.",
            json_schema_extra={"x-ui-hidden": True},
        ),
    ] = None

    @field_validator("thought_process", "conclusion")
    @classmethod
    def validate_hallucinations(cls, v: str | None) -> str:
        """Validate that the text does not contain typical LLM hallucination markers for empty values.

        Args:
            v: Input text to validate.

        Returns:
            Cleaned and validated text string.

        Raises:
            AppException: If text is empty or contains hallucination markers (VALIDATION_FAILED).
        """
        if not v or not str(v).strip():
            msg = "Field cannot be empty."
            logger.error("[BaseDomainModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        clean_v = str(v).strip().lower()
        if clean_v in {"null", "none", "n/a", "ei saatavilla"}:
            msg = f"LLM returned an invalid empty-equivalent string: '{v}'"
            logger.error("[BaseDomainModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return str(v).strip()

    @field_validator("confidence_score")
    @classmethod
    def validate_confidence_score(cls, v: float) -> float:
        """Validate that the confidence score is a valid probability.

        Args:
            v: Confidence score.

        Returns:
            Validated confidence score.

        Raises:
            AppException: If score is out of bounds (0.0 - 1.0) (VALIDATION_FAILED).
        """
        if not (0.0 <= v <= 1.0):
            msg = f"Confidence score must be between 0.0 and 1.0, got {v}"
            logger.error("[BaseDomainModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v


class ReasoningTrace(ReasoningTraceDTO):
    """Domain model with system-authoritative metadata.

    Inherits content from ReasoningTraceDTO and adds system-managed fields.
    LLMs never see or generate this model directly.

    Attributes:
        metadata: System metadata (Injected by Backend).
        semanttinen_tarkistussumma: Semantic checksum (Calculated by Backend).
    """

    metadata: Annotated[
        Metadata | None,
        Field(description="System metadata (Injected by Backend).", json_schema_extra={"x-ui-label": "Metadata"}),
    ] = None
    semanttinen_tarkistussumma: Annotated[
        str | None,
        Field(description="Semantic checksum (Calculated by Backend).", json_schema_extra={"x-ui-label": "Checksum"}),
    ] = None


class UsageRecord(V2CoreBase):
    """Immutable record of LLM token usage and cost.

    Attributes:
        id: Unique ID for the usage event.
        org_id: Organization ID.
        user_id: User ID.
        model: Model name.
        input_tokens: Input token count.
        output_tokens: Output token count.
        cached_tokens: Cached tokens.
        cache_creation_input_tokens: Tokens written to cache.
        reasoning_tokens: Reasoning tokens.
        latency_ms: Request latency in ms.
        finish_reason: Finish reason.
        system_fingerprint: System fingerprint.
        cost_usd: Cost in USD.
        estimated_savings_usd: Estimated savings in USD.
        timestamp: Timestamp of usage.
    """

    id: Annotated[
        str,
        Field(
            default_factory=lambda: f"usg_{uuid.uuid4().hex}",
            min_length=1,
            description="Unique ID for the usage event.",
            json_schema_extra={"x-ui-label": "ID"},
        ),
    ]
    org_id: Annotated[
        str,
        Field(min_length=1, description="Organization ID.", json_schema_extra={"x-ui-label": "Organization ID"}),
    ]
    user_id: Annotated[str, Field(min_length=1, description="User ID.", json_schema_extra={"x-ui-label": "User ID"})]
    model: Annotated[str, Field(min_length=1, description="Model name.", json_schema_extra={"x-ui-label": "Model"})]
    input_tokens: Annotated[
        int,
        Field(ge=0, description="Input token count.", json_schema_extra={"x-ui-label": "Input Tokens"}),
    ]
    output_tokens: Annotated[
        int, Field(ge=0, description="Output token count.", json_schema_extra={"x-ui-label": "Output Tokens"})
    ]
    cached_tokens: Annotated[
        int, Field(ge=0, description="Cached tokens.", json_schema_extra={"x-ui-label": "Cached Tokens"})
    ] = 0
    cache_creation_input_tokens: Annotated[
        int,
        Field(ge=0, description="Tokens written to cache.", json_schema_extra={"x-ui-label": "Cache Creation Tokens"}),
    ] = 0
    reasoning_tokens: Annotated[
        int, Field(ge=0, description="Reasoning tokens.", json_schema_extra={"x-ui-label": "Reasoning Tokens"})
    ] = 0
    latency_ms: Annotated[
        int | None, Field(description="Request latency in ms.", json_schema_extra={"x-ui-label": "Latency (ms)"})
    ] = None
    finish_reason: Annotated[
        str | None, Field(description="Finish reason.", json_schema_extra={"x-ui-label": "Finish Reason"})
    ] = None
    system_fingerprint: Annotated[
        str | None, Field(description="System fingerprint.", json_schema_extra={"x-ui-label": "System Fingerprint"})
    ] = None
    cost_usd: Annotated[float, Field(description="Cost in USD.", json_schema_extra={"x-ui-label": "Cost (USD)"})]
    estimated_savings_usd: Annotated[
        float, Field(description="Estimated savings.", json_schema_extra={"x-ui-label": "Savings (USD)"})
    ] = 0.0
    timestamp: Annotated[
        datetime, Field(description="Timestamp of usage.", json_schema_extra={"x-ui-label": "Timestamp"})
    ]

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> Any:
        """Parse ISO datetime strings.

        Args:
            v: Input value to parse.

        Returns:
            Parsed datetime object or original value.
        """
        if isinstance(v, str):
            # Parse explicit ISO strings in strict mode
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v

    @field_validator("cost_usd", "estimated_savings_usd")
    @classmethod
    def validate_usd_amounts(cls, v: float) -> float:
        """Validate USD amount bounds.

        Args:
            v: Amount in USD.

        Returns:
            Validated float amount.

        Raises:
            AppException: If amount is negative (ErrorCodes.VALIDATION_FAILED).
        """
        if v < 0.0:
            msg = f"USD amount cannot be negative, got {v}"
            logger.error("[BaseDomainModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v
