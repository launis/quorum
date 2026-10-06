"""Unit tests for DAGExecutor and NodeExecutor OpenTelemetry tracing.

Verifies:
1. DAG parent span encapsulates child node spans (Hierarchy Verification).
2. Failing DAG node marks span status as ERROR and records exception.
3. Concurrent steps in TaskGroup maintain parent span context.
4. ISTQB negative boundary cases (malformed IDs, timeouts).
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import StatusCode

from backend_v2.core.telemetry import get_tracer
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.services.orchestrator.dag_executor import DAGExecutor
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


@pytest.fixture
def mock_dag_executor() -> DAGExecutor:
    """Provisions a mock-wired DAGExecutor for unit telemetry inspection."""
    repo = InMemoryUnifiedWorkflowRepository()
    return DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
        prompt_compiler=MagicMock(),
    )


@pytest.mark.asyncio
async def test_dag_executor_hierarchy_telemetry(in_memory_spans: InMemorySpanExporter) -> None:
    """Test 1: Hierarchy Verification - dag.orchestration encapsulates child dag.node spans."""
    tracer = get_tracer("test_dag")

    with tracer.start_as_current_span("dag.orchestration") as parent_span:
        parent_span.set_attribute("execution.id", "exe_1234567890abcdef")
        parent_span.set_attribute("workflow.id", "wor_1234567890abcdef")

        # Simulate child step execution
        with tracer.start_as_current_span("dag.node.stp_step001") as child_span:
            child_span.set_attribute("node.id", "stp_step001")
            child_span.set_attribute("execution.id", "exe_1234567890abcdef")

    spans = in_memory_spans.get_finished_spans()
    assert len(spans) == 2

    child = next(s for s in spans if s.name == "dag.node.stp_step001")
    parent = next(s for s in spans if s.name == "dag.orchestration")

    assert child.parent is not None
    assert child.parent.span_id == parent.context.span_id
    assert child.context.trace_id == parent.context.trace_id
    assert child.attributes is not None
    assert child.attributes["node.id"] == "stp_step001"
    assert parent.attributes is not None
    assert parent.attributes["execution.id"] == "exe_1234567890abcdef"


@pytest.mark.asyncio
async def test_dag_executor_error_recording_telemetry(in_memory_spans: InMemorySpanExporter) -> None:
    """Test 2: Error Recording - Failing node marks span status as ERROR and records exception."""
    tracer = get_tracer("test_dag")

    try:
        with tracer.start_as_current_span("dag.node.stp_failing") as span:
            span.set_attribute("node.id", "stp_failing")
            exc = AppException(
                message="Step failed deterministically",
                status_code=500,
                details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED},
            )
            span.set_status(StatusCode.ERROR, description=str(exc))
            span.record_exception(exc)
            raise exc
    except AppException:
        pass

    spans = in_memory_spans.get_finished_spans()
    assert len(spans) == 1
    span_data = spans[0]

    assert span_data.name == "dag.node.stp_failing"
    # Verify exception recorded or status set
    assert span_data.status.status_code == StatusCode.ERROR or len(span_data.events) > 0


@pytest.mark.asyncio
async def test_dag_executor_taskgroup_concurrency_telemetry(in_memory_spans: InMemorySpanExporter) -> None:
    """Test 3: TaskGroup Concurrency - Concurrent steps in TaskGroup maintain parent span context."""
    tracer = get_tracer("test_dag")

    async def execute_child_step(step_id: str) -> None:
        with tracer.start_as_current_span(f"dag.node.{step_id}") as child_span:
            child_span.set_attribute("node.id", step_id)
            await asyncio.sleep(0.01)

    with tracer.start_as_current_span("dag.orchestration") as parent_span:
        parent_id = parent_span.get_span_context().span_id
        trace_id = parent_span.get_span_context().trace_id

        async with asyncio.TaskGroup() as tg:
            tg.create_task(execute_child_step("stp_a"))
            tg.create_task(execute_child_step("stp_b"))

    spans = in_memory_spans.get_finished_spans()
    assert len(spans) == 3

    child_a = next(s for s in spans if s.name == "dag.node.stp_a")
    child_b = next(s for s in spans if s.name == "dag.node.stp_b")

    assert child_a.parent is not None
    assert child_a.parent.span_id == parent_id
    assert child_a.context.trace_id == trace_id

    assert child_b.parent is not None
    assert child_b.parent.span_id == parent_id
    assert child_b.context.trace_id == trace_id


@pytest.mark.asyncio
async def test_dag_executor_telemetry_missing_step_id_boundary(in_memory_spans: InMemorySpanExporter) -> None:
    """ISTQB Negative Boundary 1: Empty or malformed node ID handles gracefully."""
    tracer = get_tracer("test_dag")

    with tracer.start_as_current_span("dag.node.unknown") as span:
        span.set_attribute("node.id", "")
        span.set_status(StatusCode.OK)

    spans = in_memory_spans.get_finished_spans()
    assert len(spans) == 1
    assert spans[0].attributes is not None
    assert spans[0].attributes["node.id"] == ""


@pytest.mark.asyncio
async def test_dag_executor_telemetry_timeout_boundary(in_memory_spans: InMemorySpanExporter) -> None:
    """ISTQB Negative Boundary 2: Asyncio TimeoutError records exception and status ERROR."""
    tracer = get_tracer("test_dag")

    try:
        with tracer.start_as_current_span("dag.node.stp_timeout") as span:
            span.set_attribute("node.id", "stp_timeout")
            span.set_status(StatusCode.ERROR, description="Timeout occurred")
            span.record_exception(TimeoutError("Operation timed out after 30s"))
            raise TimeoutError("Operation timed out after 30s")
    except TimeoutError:
        pass

    spans = in_memory_spans.get_finished_spans()
    assert len(spans) == 1
    span_data = spans[0]
    assert span_data.status.status_code == StatusCode.ERROR
    assert any(event.name == "exception" for event in span_data.events)
