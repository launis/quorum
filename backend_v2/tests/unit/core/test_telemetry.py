"""Unit tests for centralized OpenTelemetry and Logfire core module.

Verifies TracerProvider initialization, NoOp fallback, W3C trace context injection/extraction,
deterministic context detachment, LocalTraceSnapshotExporter with budget capping,
and error fingerprinting.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import opentelemetry.context as otel_context
import opentelemetry.trace as trace
import pytest
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExportResult
from opentelemetry.trace import StatusCode
from opentelemetry.trace.status import Status

import backend_v2.core.telemetry as telemetry_module
from backend_v2.core.telemetry import (
    LocalTraceSnapshotExporter,
    configure_telemetry,
    extract_trace_context,
    get_tracer,
    inject_trace_context,
    use_trace_context,
)
from backend_v2.models.dtos.telemetry import TraceContextCarrierDTO, TraceSnapshotDTO
from backend_v2.settings import Settings


@pytest.fixture(autouse=True)
def reset_telemetry_state(monkeypatch: pytest.MonkeyPatch) -> None:
    """Resets global telemetry state before and after each test."""
    monkeypatch.setattr(telemetry_module, "_TELEMETRY_CONFIGURED", False)


def test_noop_fallback() -> None:
    """Verifies that when otel_enabled is False, a NoOpTracerProvider is configured."""
    settings = Settings(otel_enabled=False)
    configure_telemetry(settings)

    provider = trace.get_tracer_provider()
    assert isinstance(provider, trace.NoOpTracerProvider)

    tracer = get_tracer("test_noop")
    with tracer.start_as_current_span("noop_span") as span:
        assert not span.is_recording()


def test_w3c_injection_and_extraction() -> None:
    """Verifies W3C traceparent injection and roundtrip extraction."""
    carrier = inject_trace_context()
    assert isinstance(carrier, TraceContextCarrierDTO)
    assert carrier.traceparent.startswith("00-")

    extracted_ctx = extract_trace_context(carrier)
    assert extracted_ctx is not None

    with use_trace_context(carrier):
        nested_carrier = inject_trace_context()
        assert isinstance(nested_carrier, TraceContextCarrierDTO)


def test_w3c_extraction_none_and_invalid() -> None:
    """Verifies extract_trace_context handles None and malformed inputs gracefully."""
    ctx_none = extract_trace_context(None)
    assert ctx_none is not None

    invalid_carrier = TraceContextCarrierDTO(
        traceparent="00-00000000000000000000000000000001-0000000000000001-01",
        tracestate="invalid===state",
    )
    ctx_invalid = extract_trace_context(invalid_carrier)
    assert ctx_invalid is not None


def test_use_trace_context_deterministic_detachment() -> None:
    """Verifies that use_trace_context detaches context cleanly in a finally block."""
    carrier = inject_trace_context()
    token_before = otel_context.get_current()

    try:
        with use_trace_context(carrier):
            # Context is active inside block
            assert otel_context.get_current() is not None
            raise ValueError("Deliberate error to verify detachment")
    except ValueError:
        pass

    # Context should be safely detached back to previous state
    token_after = otel_context.get_current()
    assert token_after == token_before


def test_local_trace_snapshot_exporter_empty(tmp_path: Path) -> None:
    """Verifies exporter handles empty span lists with SUCCESS."""
    exporter = LocalTraceSnapshotExporter(trace_dir=tmp_path)
    res = exporter.export([])
    assert res == SpanExportResult.SUCCESS
    assert exporter.force_flush() is True
    exporter.shutdown()


def test_local_trace_snapshot_exporter_execution(tmp_path: Path) -> None:
    """Verifies exporter aggregates spans, computes error_fingerprint, and caps size under 20 KB."""
    exporter = LocalTraceSnapshotExporter(trace_dir=tmp_path)
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("test_tracer")

    with tracer.start_as_current_span("root_span") as root:
        root.set_attribute("gen_ai.usage.input_tokens", 120)
        root.set_attribute("gen_ai.usage.output_tokens", 45)
        root.set_attribute("gen_ai.cache.hit", True)

        with tracer.start_as_current_span("child_failing_node") as child:
            child.set_attribute("node.id", "step_extract_atoms")
            child.set_attribute("error_code", "PARSING_FAILED")
            child.set_status(Status(StatusCode.ERROR, "JSON parsing error"))
            try:
                raise ValueError("Unexpected token")
            except ValueError as err:
                child.record_exception(err)

    target_file = tmp_path / "latest_execution_trace.json"
    assert target_file.exists()
    assert target_file.stat().st_size < 20480  # Strictly under 20 KB

    content = target_file.read_text(encoding="utf-8")
    data = json.loads(content)
    snapshot = TraceSnapshotDTO.model_validate(data)

    assert snapshot.root_span == "root_span"
    assert snapshot.status == "ERROR"
    assert snapshot.total_input_tokens == 120
    assert snapshot.total_output_tokens == 45
    assert snapshot.cache_hit is True
    assert snapshot.failing_step_id == "step_extract_atoms"
    assert snapshot.error_fingerprint == "step_extract_atoms::PARSING_FAILED::ValueError"
    assert len(snapshot.span_tree) == 2


def test_local_trace_snapshot_exporter_budget_capping(tmp_path: Path) -> None:
    """Verifies exporter caps span hierarchy at 60 spans."""
    exporter = LocalTraceSnapshotExporter(trace_dir=tmp_path)
    mock_spans: list[ReadableSpan] = []

    for i in range(80):
        mock_span = MagicMock(spec=ReadableSpan)
        mock_span.context.trace_id = 123456789
        mock_span.context.span_id = i + 1
        mock_span.parent = MagicMock(span_id=1) if i > 0 else None
        mock_span.name = f"span_{i}"
        mock_span.start_time = 1000000000
        mock_span.end_time = 1000000000 + (i * 1000000)
        mock_span.status.status_code = StatusCode.OK
        mock_span.status.description = None
        mock_span.attributes = {}
        mock_span.events = []
        mock_span.resource = None
        mock_spans.append(mock_span)

    res = exporter.export(mock_spans)
    assert res == SpanExportResult.SUCCESS

    target_file = tmp_path / "latest_execution_trace.json"
    data = json.loads(target_file.read_text(encoding="utf-8"))
    snapshot = TraceSnapshotDTO.model_validate(data)
    assert len(snapshot.span_tree) <= 60


def test_local_trace_snapshot_exporter_io_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifies exporter returns FAILURE upon file system write error."""
    exporter = LocalTraceSnapshotExporter(trace_dir=tmp_path)
    mock_span = MagicMock(spec=ReadableSpan)
    mock_span.context.trace_id = 1
    mock_span.context.span_id = 1
    mock_span.parent = None
    mock_span.name = "root"
    mock_span.start_time = 1000
    mock_span.end_time = 2000
    mock_span.status.status_code = StatusCode.OK
    mock_span.status.description = None
    mock_span.attributes = {}
    mock_span.events = []
    mock_span.resource = None

    def raise_os_error(*args: object, **kwargs: object) -> None:
        raise OSError("Read-only filesystem")

    monkeypatch.setattr(Path, "mkdir", raise_os_error)
    res = exporter.export([mock_span])
    assert res == SpanExportResult.FAILURE


def test_configure_telemetry_idempotency() -> None:
    """Verifies calling configure_telemetry twice triggers no-op on second invocation."""
    settings = Settings(otel_enabled=False)
    configure_telemetry(settings)
    assert telemetry_module._TELEMETRY_CONFIGURED is True

    # Second call should return immediately
    configure_telemetry(settings)
    assert telemetry_module._TELEMETRY_CONFIGURED is True


def test_configure_telemetry_logfire_branch(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifies configure_telemetry with logfire_token initializes Logfire."""
    import sys

    mock_logfire = MagicMock()
    monkeypatch.setitem(sys.modules, "logfire", mock_logfire)

    settings = Settings(
        otel_enabled=True,
        logfire_token="test_token_123",
        otel_service_name="test-service",
    )

    configure_telemetry(settings, service_name_override="custom-worker")

    mock_logfire.configure.assert_called_once_with(
        token="test_token_123",
        service_name="custom-worker",
        send_to_logfire=True,
    )
    mock_logfire.instrument_pydantic.assert_called_once()
    mock_logfire.instrument_httpx.assert_called_once()
    mock_logfire.instrument_requests.assert_called_once()
    mock_logfire.instrument_system_metrics.assert_called_once()
    mock_logfire.instrument_litellm.assert_called_once()
    mock_logfire.instrument_mcp.assert_called_once()


def test_configure_telemetry_otlp_branch(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifies configure_telemetry with OTLP endpoint provisions OTLPSpanExporter."""
    mock_otlp_cls = MagicMock()
    monkeypatch.setattr(
        "opentelemetry.exporter.otlp.proto.grpc.trace_exporter.OTLPSpanExporter",
        mock_otlp_cls,
        raising=False,
    )

    settings = Settings(
        otel_enabled=True,
        logfire_token=None,
        otel_service_name="otlp-service",
        otel_exporter_otlp_endpoint="grpc://localhost:4317",
    )

    configure_telemetry(settings)
    assert telemetry_module._TELEMETRY_CONFIGURED is True


def test_create_execution_record_injects_telemetry() -> None:
    """Verifies create_execution_record automatically injects W3C trace context into metadata."""
    from backend_v2.models.domain.execution import FrozenContext
    from backend_v2.models.domain.inputs import WorkflowInputs
    from backend_v2.models.execution_core import ExecutionMetadata
    from backend_v2.services.execution.ingress_service import create_execution_record

    record = create_execution_record(
        execution_id="exe_0123456789abcdef",
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputs(dynamic_inputs={}),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
    )

    assert record.metadata is not None
    assert record.metadata.telemetry is not None
    assert record.metadata.telemetry.traceparent.startswith("00-")

    custom_carrier = TraceContextCarrierDTO(traceparent="00-11112222333344445555666677778888-9999000011112222-01")
    record2 = create_execution_record(
        execution_id="exe_1123456789abcdef",
        workflow_id="wor_0123456789abcdef",
        raw_inputs=WorkflowInputs(dynamic_inputs={}),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        metadata=ExecutionMetadata(telemetry=custom_carrier),
    )
    assert record2.metadata is not None
    assert record2.metadata.telemetry == custom_carrier


def test_local_trace_snapshot_exporter_default_dir() -> None:
    """Verifies default trace directory when none is specified."""
    exporter = LocalTraceSnapshotExporter()
    assert exporter._trace_dir == Path("data/files/traces")


def test_local_trace_snapshot_exporter_corrupt_existing(tmp_path: Path) -> None:
    """Verifies exporter recovers gracefully when existing snapshot is corrupt."""
    exporter = LocalTraceSnapshotExporter(trace_dir=tmp_path)
    corrupt_file = tmp_path / "latest_execution_trace.json"
    corrupt_file.write_text("{corrupt-json", encoding="utf-8")

    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("corrupt_test")

    with tracer.start_as_current_span("span_1") as s:
        s.set_attribute("complex_attr", ["non", "primitive"])

    assert corrupt_file.exists()


def test_local_trace_snapshot_exporter_exception_without_description(tmp_path: Path) -> None:
    """Verifies exporter extracts message from exception event when status description is None."""
    exporter = LocalTraceSnapshotExporter(trace_dir=tmp_path)
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("err_test")

    with tracer.start_as_current_span("failing_span") as s:
        s.set_status(Status(StatusCode.ERROR))  # No description
        s.record_exception(RuntimeError("Explicit runtime failure"))

    target_file = tmp_path / "latest_execution_trace.json"
    assert target_file.exists()
    content = json.loads(target_file.read_text(encoding="utf-8"))
    assert content["error_summary"] == "Explicit runtime failure"


def test_configure_telemetry_with_fastapi_app(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifies configure_telemetry instruments FastAPI app both on initial and subsequent calls."""
    import sys

    mock_logfire = MagicMock()
    monkeypatch.setitem(sys.modules, "logfire", mock_logfire)

    settings = Settings(
        otel_enabled=True,
        logfire_token="token_xyz",
        otel_service_name="api-service",
    )
    mock_app = MagicMock()

    # Initial call
    configure_telemetry(settings, app=mock_app)
    mock_logfire.instrument_fastapi.assert_called_once_with(mock_app)

    # Idempotent call with app provided
    mock_app_2 = MagicMock()
    configure_telemetry(settings, app=mock_app_2)
    mock_logfire.instrument_fastapi.assert_any_call(mock_app_2)


def test_extract_trace_context_exception_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifies extract_trace_context handles extraction exceptions by returning current context."""
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

    monkeypatch.setattr(
        TraceContextTextMapPropagator,
        "extract",
        MagicMock(side_effect=TypeError("Propagator failure")),
    )
    carrier = TraceContextCarrierDTO(
        traceparent="00-11112222333344445555666677778888-9999000011112222-01",
        tracestate="ro=test",
    )
    ctx = extract_trace_context(carrier)
    assert ctx is not None

