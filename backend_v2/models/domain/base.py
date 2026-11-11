"""Base domain models.

This module contains the foundational Pydantic models used by all other domain entities.
It includes Metadata, ReasoningTrace, and UsageRecord.
"""

import logging
from datetime import UTC, datetime
from typing import Annotated, Any

from pydantic import ConfigDict, Field, JsonValue, field_validator

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX, V2CoreBase, generate_uuid7, parse_prefixed_uuid7
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.base import BaseDTO
from backend_v2.models.enums import EntityPrefix
from backend_v2.models.llm import ProviderMetadataDTO

__all__ = [
    "AuditLogCreateDTO",
    "AuditLogEntry",
    "AuditLogRecord",
    "DetailedUsageDTO",
    "Metadata",
    "ReasoningTrace",
    "ReasoningTraceDTO",
    "UsageRecord",
    "UsageRollupSummaryDTO",
]

logger = logging.getLogger(__name__)


class AuditLogEntry(V2CoreBase):
    """Strict model for a single audit log entry.

    Attributes:
        timestamp: Timestamp of the log entry.
        level: Log level (INFO, WARN, ERROR).
        message: Log message.
        context: Additional context.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    timestamp: Annotated[datetime, Field(description="Timestamp of the log entry.")]
    level: Annotated[str, Field(min_length=1, description="Log level (INFO, WARN, ERROR).")]
    message: Annotated[str, Field(min_length=1, description="Log message.")]
    context: Annotated[dict[str, JsonValue] | None, Field(description="Additional context.")] = None


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

    model_config = ConfigDict(strict=True, extra="forbid")

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
        ProviderMetadataDTO | None,
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

        Raises:
            ValueError: If the string is not a valid ISO 8601 datetime.
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

    model_config = ConfigDict(strict=True, extra="forbid")

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
            AppException: If text is empty or contains hallucination markers (ErrorCodes.VALIDATION_FAILED).
        """
        if not v or not str(v).strip():
            msg = "Field cannot be empty."
            logger.error("[BaseDomainModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        clean_v = str(v).strip().lower()
        if clean_v in {"null", "none", "n/a", "ei saatavilla"}:
            msg = f"LLM returned an invalid empty-equivalent string: '{v}'"
            logger.error("[BaseDomainModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
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
            AppException: If score is out of bounds (0.0 - 1.0) (ErrorCodes.VALIDATION_FAILED).
        """
        if not (0.0 <= v <= 1.0):
            msg = f"Confidence score must be between 0.0 and 1.0, got {v}"
            logger.error("[BaseDomainModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
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

    model_config = ConfigDict(strict=True, extra="forbid")

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
        id: Canonical UsageRecord Opaque Stripe ID (usg_<hex32>).
        org_id: Organization ID.
        user_id: User ID.
        execution_id: Optional associated Execution Opaque Stripe ID.
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

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[
        str,
        Field(
            default_factory=lambda: f"usg_{generate_uuid7().hex}",
            pattern=OPAQUE_STRIPE_ID_REGEX,
            description="Canonical UsageRecord Opaque Stripe ID (usg_<hex32>).",
            json_schema_extra={"x-ui-label": "ID"},
        ),
    ]
    org_id: Annotated[
        str,
        Field(min_length=1, description="Organization ID.", json_schema_extra={"x-ui-label": "Organization ID"}),
    ]
    user_id: Annotated[str, Field(min_length=1, description="User ID.", json_schema_extra={"x-ui-label": "User ID"})]
    execution_id: Annotated[
        str | None,
        Field(default=None, description="Optional associated execution ID."),
    ] = None
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

    @field_validator("id")
    @classmethod
    def _validate_usage_record_id(cls, v: str) -> str:
        """Validate that the identifier uses the canonical usg_ prefix and RFC 9562 UUIDv7 format.

        Args:
            v: Candidate UsageRecord identifier string.

        Returns:
            Validated UsageRecord identifier string.

        Raises:
            AppException: With VALIDATION_FAILED if the prefix or UUIDv7 structure is invalid.
        """
        _ = parse_prefixed_uuid7(v, EntityPrefix.USAGE_RECORD)
        return v

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> Any:
        """Parse ISO datetime strings.

        Args:
            v: Input value to parse.

        Returns:
            Parsed datetime object or original value.

        Raises:
            ValueError: If the string is not a valid ISO 8601 datetime.
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
            logger.error("[BaseDomainModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v


class AuditLogRecord(V2CoreBase):
    """Immutable compliance record stored in the append-only audit_logs table.

    Attributes:
        id: Canonical AuditLogRecord Opaque Stripe ID (aud_<hex32>).
        organization_id: Optional owning Organization Opaque Stripe ID.
        actor_id: Optional actor User Opaque Stripe ID (None for system events).
        execution_id: Optional associated Execution Opaque Stripe ID.
        event_type: Audit event type identifier.
        resource_type: Audited resource type identifier.
        resource_id: Audited resource identifier.
        details: Typed scalar audit metadata dictionary.
        created_at: UTC timestamp extracted from the UUIDv7 primary key.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[
        str,
        Field(
            default_factory=lambda: f"aud_{generate_uuid7().hex}",
            pattern=OPAQUE_STRIPE_ID_REGEX,
            description="Canonical AuditLogRecord Opaque Stripe ID (aud_<hex32>).",
        ),
    ]
    organization_id: Annotated[
        str | None,
        Field(default=None, description="Owning Organization Opaque Stripe ID."),
    ] = None
    actor_id: Annotated[
        str | None,
        Field(default=None, description="Actor User Opaque Stripe ID or None for system events."),
    ] = None
    execution_id: Annotated[
        str | None,
        Field(default=None, description="Associated Execution Opaque Stripe ID."),
    ] = None
    event_type: Annotated[str, Field(min_length=1, description="Audit event type identifier.")]
    resource_type: Annotated[str, Field(min_length=1, description="Audited resource type identifier.")]
    resource_id: Annotated[str, Field(min_length=1, description="Audited resource identifier.")]
    details: Annotated[
        dict[str, str | int | float | bool | list[str]],
        Field(default_factory=dict, description="Typed scalar audit metadata dictionary."),
    ]
    created_at: Annotated[
        datetime,
        Field(default_factory=lambda: datetime.now(UTC), description="UTC creation timestamp."),
    ]

    @field_validator("id")
    @classmethod
    def _validate_audit_log_id(cls, v: str) -> str:
        """Validate that the identifier uses the canonical aud_ prefix and RFC 9562 UUIDv7 format.

        Args:
            v: Candidate AuditLogRecord identifier string.

        Returns:
            Validated AuditLogRecord identifier string.

        Raises:
            AppException: With VALIDATION_FAILED if the prefix or UUIDv7 structure is invalid.
        """
        _ = parse_prefixed_uuid7(v, EntityPrefix.AUDIT_LOG)
        return v

    @field_validator("created_at", mode="before")
    @classmethod
    def _parse_created_at(cls, v: Any) -> Any:
        """Parse ISO 8601 string timestamps into timezone-aware datetime objects.

        Args:
            v: Candidate timestamp value.

        Returns:
            Parsed datetime instance or original value.

        Raises:
            ValueError: If a string value is not valid ISO 8601 format.
        """
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v


class AuditLogCreateDTO(BaseDTO):
    """DTO for inserting a new compliance event into the append-only audit_logs ledger.

    Attributes:
        event_type: Audit event type identifier.
        actor_id: Optional actor user or system identifier.
        organization_id: Optional associated organization identifier.
        execution_id: Optional associated execution identifier.
        resource_type: Audited resource type identifier.
        resource_id: Audited resource identifier.
        details: Typed scalar details dictionary.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    event_type: Annotated[str, Field(min_length=1, description="Audit event type identifier")]
    actor_id: Annotated[str | None, Field(default=None, description="Actor user or system identifier")] = None
    organization_id: Annotated[str | None, Field(default=None, description="Associated organization ID")] = None
    execution_id: Annotated[str | None, Field(default=None, description="Associated execution ID")] = None
    resource_type: Annotated[str, Field(min_length=1, description="Audited resource type identifier")]
    resource_id: Annotated[str, Field(min_length=1, description="Audited resource identifier")]
    details: Annotated[
        dict[str, str | int | float | bool | list[str]],
        Field(default_factory=dict, description="Typed scalar details dictionary"),
    ]


class UsageRollupSummaryDTO(BaseDTO):
    """Immutable SQL SUM/COUNT FinOps rollup computed directly over append-only usage_records.

    Attributes:
        organization_id: Scoped organization identifier or None for global rollup.
        total_prompt_tokens: Aggregated prompt input tokens.
        total_completion_tokens: Aggregated completion output tokens.
        total_cached_tokens: Aggregated cached prompt tokens.
        total_reasoning_tokens: Aggregated reasoning tokens.
        total_cache_creation_input_tokens: Aggregated cache creation input tokens.
        total_cost_usd: Aggregated monetary cost in USD.
        total_estimated_savings_usd: Aggregated estimated cache savings in USD.
        record_count: Total matching usage_records count.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    organization_id: Annotated[
        str | None, Field(default=None, description="Scoped organization ID or None for system rollup")
    ] = None
    total_prompt_tokens: Annotated[int, Field(ge=0, description="Aggregated prompt input tokens")] = 0
    total_completion_tokens: Annotated[int, Field(ge=0, description="Aggregated completion output tokens")] = 0
    total_cached_tokens: Annotated[int, Field(ge=0, description="Aggregated cached prompt tokens")] = 0
    total_reasoning_tokens: Annotated[int, Field(ge=0, description="Aggregated reasoning tokens")] = 0
    total_cache_creation_input_tokens: Annotated[
        int, Field(ge=0, description="Aggregated cache creation input tokens")
    ] = 0
    total_cost_usd: Annotated[float, Field(ge=0.0, description="Aggregated monetary cost in USD")] = 0.0
    total_estimated_savings_usd: Annotated[
        float, Field(ge=0.0, description="Aggregated estimated cache savings in USD")
    ] = 0.0
    record_count: Annotated[int, Field(ge=0, description="Total matching usage record count")] = 0


class DetailedUsageDTO(BaseDTO):
    """DTO representing detailed usage analysis across models and workflows.

    Attributes:
        organization_id: Organization ID.
        total_cost_usd: Total cost across all models.
        total_tokens: Total tokens across all models.
        by_model: Tokens by model name.
        by_workflow: Executions by workflow ID.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    organization_id: Annotated[str, Field(description="Organization ID")]
    total_cost_usd: Annotated[float, Field(ge=0.0, description="Total cost across all models")]
    total_tokens: Annotated[int, Field(ge=0, description="Total tokens across all models")]
    by_model: Annotated[dict[str, int], Field(default_factory=dict, description="Tokens by model name")]
    by_workflow: Annotated[dict[str, int], Field(default_factory=dict, description="Executions by workflow ID")]
