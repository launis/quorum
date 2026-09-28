"""OpenTelemetry and Logfire Distributed Tracing Core Module.

Centralizes TracerProvider initialization, Logfire cloud configuration, W3C trace context
injection/extraction, and local diagnostic snapshot exporting for AI-assisted introspection.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

import opentelemetry.context as otel_context
import opentelemetry.trace as trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor, SpanExporter, SpanExportResult
from opentelemetry.sdk.trace.id_generator import RandomIdGenerator
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from backend_v2.models.dtos.telemetry import (
    SpanSnapshotDTO,
    TraceContextCarrierDTO,
    TraceSnapshotDTO,
)

if TYPE_CHECKING:
    from backend_v2.settings import Settings

logger = logging.getLogger(__name__)

__all__ = [
    "LocalTraceSnapshotExporter",
    "configure_telemetry",
    "extract_trace_context",
    "get_tracer",
    "inject_trace_context",
    "use_trace_context",
]

_TELEMETRY_CONFIGURED: bool = False
_ID_GENERATOR = RandomIdGenerator()


class LocalTraceSnapshotExporter(SpanExporter):
    """Exports structured trace snapshots atomically to local disk for AI-assisted diagnostics.

    Enforces a strict 60-span budget cap (<20 KB file size) prioritizing root, failing,
    and high-latency spans, and computes a deterministic error_fingerprint for root cause analysis.
    """

    def __init__(self, trace_dir: str | Path | None = None) -> None:
        """Initializes the local trace snapshot exporter.

        Args:
            trace_dir: Optional custom directory path for saving trace snapshots.
        """
        if trace_dir is not None:
            self._trace_dir = Path(trace_dir)
        else:
            self._trace_dir = Path("data/files/traces")
        self._target_file = self._trace_dir / "latest_execution_trace.json"

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """Exports a batch of completed spans into a consolidated trace snapshot.

        Args:
            spans: Ordered collection of completed readable spans.

        Returns:
            SpanExportResult indicating export outcome.
        """
        if not spans:
            return SpanExportResult.SUCCESS

        try:
            self._trace_dir.mkdir(parents=True, exist_ok=True)

            primary_trace_id = format(spans[0].context.trace_id, "032x")
            existing_spans: dict[str, SpanSnapshotDTO] = {}
            failing_step_id: str | None = None
            error_summary: str | None = None
            exception_class: str | None = None
            error_code: str | None = None
            existing_error_fingerprint: str | None = None
            root_span_name = "unknown"
            service_name = "quorum-backend"
            overall_status = "OK"

            if self._target_file.exists():
                try:
                    raw_prev = self._target_file.read_text(encoding="utf-8")
                    prev_snapshot = TraceSnapshotDTO.model_validate_json(raw_prev)
                    if prev_snapshot.trace_id == primary_trace_id:
                        for prev_s in prev_snapshot.span_tree:
                            existing_spans[prev_s.span_id] = prev_s
                        if prev_snapshot.status == "ERROR":
                            overall_status = "ERROR"
                        if prev_snapshot.failing_step_id is not None:
                            failing_step_id = prev_snapshot.failing_step_id
                        if prev_snapshot.error_fingerprint is not None:
                            existing_error_fingerprint = prev_snapshot.error_fingerprint
                        if prev_snapshot.error_summary is not None:
                            error_summary = prev_snapshot.error_summary
                        if prev_snapshot.service_name:
                            service_name = prev_snapshot.service_name
                except OSError, ValueError, TypeError, KeyError:
                    pass

            for span in spans:
                span_id_hex = format(span.context.span_id, "016x")
                parent_id_hex: str | None = None
                if span.parent is not None:
                    parent_id_hex = format(span.parent.span_id, "016x")
                if parent_id_hex is None:
                    root_span_name = span.name

                if span.resource and SERVICE_NAME in span.resource.attributes:
                    service_name = str(span.resource.attributes[SERVICE_NAME])

                duration_ms = 0.0
                if span.start_time and span.end_time:
                    duration_ms = round((span.end_time - span.start_time) / 1_000_000, 2)

                is_error = span.status.status_code == trace.StatusCode.ERROR
                span_status = "OK"
                if is_error:
                    span_status = "ERROR"
                    overall_status = "ERROR"

                clean_attrs: dict[str, str | int | float | bool] = {}
                if span.attributes:
                    for k, v in span.attributes.items():
                        if isinstance(v, (str, int, float, bool)):
                            clean_attrs[k] = v
                        else:
                            clean_attrs[k] = str(v)

                err_msg = span.status.description
                if is_error:
                    if "node.id" in clean_attrs and failing_step_id is None:
                        failing_step_id = str(clean_attrs["node.id"])
                    if "error_code" in clean_attrs and error_code is None:
                        error_code = str(clean_attrs["error_code"])

                    for event in span.events:
                        if event.name == "exception" and event.attributes:
                            if "exception.type" in event.attributes and exception_class is None:
                                exception_class = str(event.attributes["exception.type"])
                            if "exception.message" in event.attributes and err_msg is None:
                                err_msg = str(event.attributes["exception.message"])

                    if err_msg and error_summary is None:
                        error_summary = err_msg

                existing_spans[span_id_hex] = SpanSnapshotDTO(
                    span_id=span_id_hex,
                    parent_id=parent_id_hex,
                    name=span.name,
                    duration_ms=duration_ms,
                    status=span_status,
                    attributes=clean_attrs,
                    error_message=err_msg,
                )

            span_snapshots = list(existing_spans.values())

            total_input_tokens = 0
            total_output_tokens = 0
            cache_hit = False
            for s in span_snapshots:
                if "gen_ai.usage.input_tokens" in s.attributes:
                    in_t = s.attributes["gen_ai.usage.input_tokens"]
                    if isinstance(in_t, int):
                        total_input_tokens += in_t
                if "gen_ai.usage.output_tokens" in s.attributes:
                    out_t = s.attributes["gen_ai.usage.output_tokens"]
                    if isinstance(out_t, int):
                        total_output_tokens += out_t
                if "gen_ai.cache.hit" in s.attributes and s.attributes["gen_ai.cache.hit"] is True:
                    cache_hit = True

            # Context Window Protection Guard: cap at 60 spans
            if len(span_snapshots) > 60:
                root_and_errors = [s for s in span_snapshots if s.parent_id is None or s.status == "ERROR"]
                others = [s for s in span_snapshots if s.parent_id is not None and s.status != "ERROR"]
                others.sort(key=lambda s: s.duration_ms, reverse=True)
                budget_remaining = max(0, 60 - len(root_and_errors))
                span_snapshots = root_and_errors + others[:budget_remaining]

            error_fingerprint: str | None = existing_error_fingerprint
            if error_code is not None or exception_class is not None:
                f_node = "unknown_step"
                if failing_step_id is not None:
                    f_node = failing_step_id
                f_code = "UNKNOWN_ERROR"
                if error_code is not None:
                    f_code = error_code
                f_exc = "AppException"
                if exception_class is not None:
                    f_exc = exception_class
                error_fingerprint = f"{f_node}::{f_code}::{f_exc}"
            elif overall_status == "ERROR" and error_fingerprint is None:
                f_node = "unknown_step"
                if failing_step_id is not None:
                    f_node = failing_step_id
                error_fingerprint = f"{f_node}::UNKNOWN_ERROR::AppException"

            known_span_ids = set(existing_spans.keys())
            root_candidates = [s for s in span_snapshots if s.parent_id is None or s.parent_id not in known_span_ids]
            if root_candidates:
                root_span_name = root_candidates[0].name
            elif span_snapshots:
                root_span_name = span_snapshots[0].name
            else:
                root_span_name = "unknown"

            total_duration_ms = sum(s.duration_ms for s in root_candidates)
            if total_duration_ms == 0.0 and span_snapshots:
                total_duration_ms = max(s.duration_ms for s in span_snapshots)

            snapshot = TraceSnapshotDTO(
                trace_id=primary_trace_id,
                service_name=service_name,
                root_span=root_span_name,
                status=overall_status,
                duration_ms=round(total_duration_ms, 2),
                timestamp=datetime.now(timezone.utc).isoformat(),
                failing_step_id=failing_step_id,
                error_summary=error_summary,
                error_fingerprint=error_fingerprint,
                span_tree=span_snapshots,
                total_input_tokens=total_input_tokens,
                total_output_tokens=total_output_tokens,
                cache_hit=cache_hit,
            )

            temp_file = self._target_file.with_suffix(".tmp")
            temp_file.write_text(snapshot.model_dump_json(indent=2), encoding="utf-8")
            temp_file.replace(self._target_file)
            return SpanExportResult.SUCCESS
        except (OSError, ValueError, TypeError, KeyError) as e:
            logger.warning("LocalTraceSnapshotExporter failed to export snapshot: %s", e)
            return SpanExportResult.FAILURE

    def shutdown(self) -> None:
        """Shuts down the exporter."""

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Flushes buffered spans.

        Args:
            timeout_millis: Timeout in milliseconds for flushing.

        Returns:
            Boolean indicating successful flush.
        """
        return True


def configure_telemetry(
    settings: Settings,
    service_name_override: str | None = None,
    app: Any | None = None,
) -> None:
    """Configures centralized OpenTelemetry and Logfire distributed tracing.

    Enforces strict idempotency via global _TELEMETRY_CONFIGURED guard.
    Provisions a zero-overhead NoOpTracerProvider when otel_enabled is False.
    Consolidates built-in Logfire instrumentations (Pydantic, HTTPX, Requests,
    System Metrics, LiteLLM, FastAPI) with zero duplicate initialization.

    Args:
        settings: Application Settings containing OpenTelemetry configuration.
        service_name_override: Optional logical service name override.
        app: Optional FastAPI application instance for framework instrumentation.
    """
    global _TELEMETRY_CONFIGURED
    if _TELEMETRY_CONFIGURED:
        if app is not None and settings.logfire_token:
            try:
                import logfire

                logfire.instrument_fastapi(app)
            except Exception as e:
                logger.error("Failed to instrument FastAPI with Logfire: %s", e)
                raise
        return
    _TELEMETRY_CONFIGURED = True

    if not settings.otel_enabled:
        trace.set_tracer_provider(trace.NoOpTracerProvider())
        logger.info("OpenTelemetry distributed tracing is disabled; using NoOpTracerProvider.")
        return

    service_name = service_name_override or settings.otel_service_name

    if settings.logfire_token:
        try:
            import logfire

            os.environ.setdefault("LOGFIRE_BASE_URL", "https://api-eu.pydantic.dev/")
            os.environ["LOGFIRE_CONSOLE"] = "false"

            logfire.configure(
                token=settings.logfire_token,
                service_name=service_name,
                send_to_logfire=True,
            )
            logfire.instrument_pydantic()
            logfire.instrument_httpx()
            logfire.instrument_requests()
            logfire.instrument_system_metrics()
            logfire.instrument_litellm()
            if app is not None:
                logfire.instrument_fastapi(app)
            logger.info("Configured Pydantic Logfire cloud distributed tracing for %s", service_name)
        except (RuntimeError, ValueError, TypeError, AttributeError, ImportError, OSError) as e:
            logger.warning("Failed to configure Logfire cloud telemetry: %s", e)
    else:
        resource = Resource.create({SERVICE_NAME: service_name})
        provider = TracerProvider(resource=resource)

        if settings.otel_exporter_otlp_endpoint:
            try:
                from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

                otlp_exporter = OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint)
                provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
            except (RuntimeError, ValueError, TypeError, AttributeError, ImportError, OSError) as e:
                logger.warning("Failed to initialize OTLPSpanExporter: %s", e)

        trace.set_tracer_provider(provider)
        logger.info("Configured native OpenTelemetry TracerProvider for %s", service_name)

    active_provider = trace.get_tracer_provider()
    if isinstance(active_provider, TracerProvider) and (
        settings.environment == "development" or os.getenv("DEBUG", "").lower() == "true"
    ):
        active_provider.add_span_processor(SimpleSpanProcessor(LocalTraceSnapshotExporter()))


def get_tracer(name: str) -> trace.Tracer:
    """Returns a named OpenTelemetry tracer.

    Args:
        name: Name of the requesting module or domain.

    Returns:
        Configured OpenTelemetry Tracer instance.
    """
    return trace.get_tracer(name)


def inject_trace_context() -> TraceContextCarrierDTO:
    """Extracts the active OpenTelemetry context into a validated W3C carrier DTO.

    If no active span exists, generates a synthetic valid W3C traceparent.

    Returns:
        Validated TraceContextCarrierDTO containing traceparent and optional tracestate.
    """
    carrier_dict: dict[str, str] = {}
    TraceContextTextMapPropagator().inject(carrier_dict)

    traceparent = ""
    if "traceparent" in carrier_dict:
        traceparent = carrier_dict["traceparent"]
    if not traceparent:
        t_id = format(_ID_GENERATOR.generate_trace_id(), "032x")
        s_id = format(_ID_GENERATOR.generate_span_id(), "016x")
        traceparent = f"00-{t_id}-{s_id}-01"

    tracestate: str | None = None
    if "tracestate" in carrier_dict:
        tracestate = carrier_dict["tracestate"]
    return TraceContextCarrierDTO(traceparent=traceparent, tracestate=tracestate)


def extract_trace_context(carrier: TraceContextCarrierDTO | None) -> otel_context.Context:
    """Safely extracts W3C traceparent from a carrier DTO into an OpenTelemetry Context.

    Args:
        carrier: W3C trace context carrier DTO, or None.

    Returns:
        Extracted OpenTelemetry Context, or active Context if carrier is None/invalid.
    """
    if carrier is None:
        return otel_context.get_current()

    try:
        carrier_dict = {"traceparent": carrier.traceparent}
        if carrier.tracestate:
            carrier_dict["tracestate"] = carrier.tracestate
        return TraceContextTextMapPropagator().extract(carrier_dict)
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        logger.warning("Failed to extract W3C trace context from carrier: %s", e)
        return otel_context.get_current()


@contextmanager
def use_trace_context(carrier: TraceContextCarrierDTO | None) -> Iterator[otel_context.Context]:
    """Context manager attaching extracted trace context with deterministic token cleanup.

    Guarantees that attached context tokens are detached in a finally block,
    preventing context contamination across concurrent asyncio tasks.

    Args:
        carrier: W3C trace context carrier DTO to attach during context lifecycle.

    Yields:
        Attached OpenTelemetry Context.
    """
    ctx = extract_trace_context(carrier)
    token = otel_context.attach(ctx)
    try:
        yield ctx
    finally:
        otel_context.detach(token)
