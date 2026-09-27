"""OpenTelemetry and Logfire Telemetry DTOs Module.

Defines immutable Pydantic V2 DTOs for W3C distributed trace context carriers,
individual span snapshots, and aggregated local trace diagnostic snapshots.
"""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "SpanSnapshotDTO",
    "TraceContextCarrierDTO",
    "TraceSnapshotDTO",
]


class TraceContextCarrierDTO(BaseModel):
    """W3C distributed trace context carrier for OpenTelemetry.

    Attributes:
        traceparent: W3C traceparent header string conforming to 00-traceid-spanid-flags.
        tracestate: Optional W3C tracestate header string.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    traceparent: Annotated[
        str,
        Field(
            pattern=r"^00-[0-9a-f]{32}-[0-9a-f]{16}-[0-9a-f]{2}$",
            description="W3C traceparent header string conforming to 00-traceid-spanid-flags",
        ),
    ]
    tracestate: Annotated[
        str | None,
        Field(default=None, description="Optional W3C tracestate header string"),
    ] = None


class SpanSnapshotDTO(BaseModel):
    """Snapshot representation of an individual completed OpenTelemetry span.

    Attributes:
        span_id: Hex span identifier.
        parent_id: Hex parent span identifier if child span.
        name: Span operation name.
        duration_ms: Span duration in milliseconds.
        status: Span completion status: OK or ERROR.
        attributes: Captured span attributes.
        error_message: Exception error message if failed.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    span_id: Annotated[str, Field(description="Hex span identifier")]
    parent_id: Annotated[
        str | None,
        Field(default=None, description="Hex parent span identifier if child span"),
    ] = None
    name: Annotated[str, Field(description="Span operation name")]
    duration_ms: Annotated[float, Field(ge=0.0, description="Span duration in milliseconds")]
    status: Annotated[str, Field(description="Span completion status: OK or ERROR")]
    attributes: Annotated[
        dict[str, str | int | float | bool],
        Field(default_factory=dict, description="Captured span attributes"),
    ]
    error_message: Annotated[
        str | None,
        Field(default=None, description="Exception error message if failed"),
    ] = None


class TraceSnapshotDTO(BaseModel):
    """Aggregated local trace diagnostic snapshot for AI-assisted introspection.

    Attributes:
        trace_id: Hex trace identifier.
        service_name: Emitting service name.
        root_span: Name of root span.
        status: Overall trace status: OK or ERROR.
        duration_ms: Total trace duration in milliseconds.
        timestamp: ISO-8601 UTC timestamp of trace completion.
        failing_step_id: Identifier of first failing DAG step if failed.
        error_summary: Summary message of root failure if failed.
        error_fingerprint: Deterministic error signature hash.
        span_tree: Ordered hierarchy of completed spans.
        total_input_tokens: Aggregated LLM input tokens.
        total_output_tokens: Aggregated LLM output tokens.
        cache_hit: Whether prompt caching hit occurred.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    trace_id: Annotated[str, Field(description="Hex trace identifier")]
    service_name: Annotated[str, Field(description="Emitting service name")]
    root_span: Annotated[str, Field(description="Name of root span")]
    status: Annotated[str, Field(description="Overall trace status: OK or ERROR")]
    duration_ms: Annotated[float, Field(ge=0.0, description="Total trace duration in milliseconds")]
    timestamp: Annotated[str, Field(description="ISO-8601 UTC timestamp of trace completion")]
    failing_step_id: Annotated[
        str | None,
        Field(default=None, description="Identifier of first failing DAG step if failed"),
    ] = None
    error_summary: Annotated[
        str | None,
        Field(default=None, description="Summary message of root failure if failed"),
    ] = None
    error_fingerprint: Annotated[
        str | None,
        Field(
            default=None, description="Deterministic error signature hash: failing_node::error_code::exception_class"
        ),
    ] = None
    span_tree: Annotated[
        list[SpanSnapshotDTO],
        Field(default_factory=list, description="Ordered hierarchy of completed spans"),
    ]
    total_input_tokens: Annotated[
        int,
        Field(ge=0, default=0, description="Aggregated LLM input tokens"),
    ] = 0
    total_output_tokens: Annotated[
        int,
        Field(ge=0, default=0, description="Aggregated LLM output tokens"),
    ] = 0
    cache_hit: Annotated[
        bool,
        Field(default=False, description="Whether prompt caching hit occurred"),
    ] = False
