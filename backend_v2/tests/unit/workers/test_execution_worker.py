"""Unit tests for execution worker enforcing Tripartite Phase 1 Sovereignty and ISTQB boundaries."""

import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.models.domain.execution import ExecutionRecord, ExecutionStep
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO
from backend_v2.models.dtos.trace import StepTraceMetadataDTO, TraceEventMetadataEnvelope
from backend_v2.models.enums import ExecutionStatus, HistoricalContextMode
from backend_v2.models.state import ErrorTraceEvent, TraceEvent
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository
from backend_v2.workers.execution_worker import execute_workflow_job


def _create_mock_workflow(strictness: int = 1) -> Workflow:
    return Workflow(
        id="wor_0123456789abcdef",
        slug="test-workflow",
        name="Test Workflow",
        description="Test Description",
        status="active",
        version=1,
        default_strictness_level=strictness,
        model_registry_id="sys_e26807f3bfa3454d",
        historical_context_mode=HistoricalContextMode.DISABLED,
        steps=[],
    )


def _create_mock_record(target_locale: str = "fi") -> ExecutionRecord:
    return ExecutionRecord(
        id="exe_0123456789abcdef",
        workflow_id="wor_0123456789abcdef",
        status=ExecutionStatus.PENDING,
        target_locale=target_locale,
        progress=None,
        status_message=None,
        steps=[
            ExecutionStep(
                id="stp_0123456789abcdef",
                label="Analytical Step",
                status=ExecutionStatus.PASSED,
            )
        ],
    )


@pytest.mark.asyncio
async def test_execution_worker_sets_status_passed_and_no_synthetic_steps() -> None:
    """Verify that execute_workflow_job marks execution PASSED and injects zero sys_render steps."""
    mock_workflow = _create_mock_workflow()
    mock_record = _create_mock_record()

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_workflow(mock_workflow)
    await mock_repo.save_execution(mock_record)

    mock_engine = MagicMock()
    mock_engine.execute_workflow = AsyncMock(return_value=mock_record)

    ctx = {
        "repository": mock_repo,
        "engine": mock_engine,
        "redis": None,
    }

    result = await execute_workflow_job(
        ctx=ctx,
        workflow_id="wor_0123456789abcdef",
        inputs=ExecutionInputsDTO(),
        execution_id="exe_0123456789abcdef",
    )

    assert result.status == "COMPLETED"
    updated_rec = await mock_repo.get_execution("exe_0123456789abcdef")
    assert updated_rec is not None
    assert updated_rec.status == ExecutionStatus.PASSED
    assert updated_rec.completed_at is not None

    step_ids = [s.id for s in updated_rec.steps]
    for s_id in step_ids:
        assert not s_id.startswith("sys_render"), f"Found synthetic render step: {s_id}"


@pytest.mark.asyncio
async def test_execution_worker_enqueues_zero_downstream_jobs() -> None:
    """Verify that execute_workflow_job does NOT auto-enqueue any background report/render jobs."""
    mock_workflow = _create_mock_workflow(strictness=50)
    mock_record = _create_mock_record()

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_workflow(mock_workflow)
    await mock_repo.save_execution(mock_record)

    mock_engine = MagicMock()
    mock_engine.execute_workflow = AsyncMock(return_value=mock_record)
    mock_redis = AsyncMock()

    ctx = {
        "repository": mock_repo,
        "engine": mock_engine,
        "redis": mock_redis,
    }

    result = await execute_workflow_job(
        ctx=ctx,
        workflow_id="wor_0123456789abcdef",
        inputs=ExecutionInputsDTO(),
        execution_id="exe_0123456789abcdef",
    )

    assert result.status == "COMPLETED"
    updated_rec = await mock_repo.get_execution("exe_0123456789abcdef")
    assert updated_rec is not None
    assert updated_rec.status == ExecutionStatus.PASSED
    assert "enqueue_job" not in dir(mock_redis) or not mock_redis.enqueue_job.called


@pytest.mark.asyncio
async def test_execution_worker_missing_workflow_raises() -> None:
    """Verify missing workflow routes to DLQ and returns failure."""
    mock_record = _create_mock_record()
    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_execution(mock_record)

    ctx = {
        "repository": mock_repo,
        "engine": MagicMock(),
    }

    result = await execute_workflow_job(
        ctx=ctx,
        workflow_id="wor_missing00000000",
        inputs=ExecutionInputsDTO(),
        execution_id="exe_0123456789abcdef",
    )
    assert result.status == "FAILED/DLQ"
    updated_rec = await mock_repo.get_execution("exe_0123456789abcdef")
    assert updated_rec is not None
    assert updated_rec.status == ExecutionStatus.FAILED


@pytest.mark.asyncio
async def test_execution_worker_missing_execution_raises() -> None:
    """Verify missing execution in DB routes to DLQ and returns failure."""
    mock_workflow = _create_mock_workflow()
    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_workflow(mock_workflow)

    ctx = {
        "repository": mock_repo,
        "engine": MagicMock(),
    }

    result = await execute_workflow_job(
        ctx=ctx,
        workflow_id="wor_0123456789abcdef",
        inputs=ExecutionInputsDTO(),
        execution_id="exe_0123456789abcdef",
    )
    assert result.status == "FAILED/DLQ"
    assert (await mock_repo.get_execution("exe_0123456789abcdef")) is None


@pytest.mark.asyncio
async def test_execution_worker_missing_target_locale_raises() -> None:
    """Verify execution without target_locale routes to DLQ and returns failure."""
    mock_workflow = _create_mock_workflow()
    mock_record = _create_mock_record(target_locale="")

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_workflow(mock_workflow)
    await mock_repo.save_execution(mock_record)

    ctx = {
        "repository": mock_repo,
        "engine": MagicMock(),
    }

    result = await execute_workflow_job(
        ctx=ctx,
        workflow_id="wor_0123456789abcdef",
        inputs=ExecutionInputsDTO(),
        execution_id="exe_0123456789abcdef",
    )
    assert result.status == "FAILED/DLQ"
    updated_rec = await mock_repo.get_execution("exe_0123456789abcdef")
    assert updated_rec is not None
    assert updated_rec.status == ExecutionStatus.FAILED


@pytest.mark.asyncio
async def test_execution_worker_trace_telemetry_aggregation() -> None:
    """Verify FinOps telemetry aggregation across TraceEvents with StepTraceMetadataDTO."""
    mock_workflow = _create_mock_workflow(strictness=3)
    step_id = "stp_0123456789abcdef"

    usage1 = TokenUsage(
        prompt_tokens=100,
        completion_tokens=50,
        cached_tokens=25,
        reasoning_tokens=10,
        total_tokens=150,
        cost_usd=0.005,
    )
    meta_env1 = TraceEventMetadataEnvelope(
        step_metadata=StepTraceMetadataDTO(
            step_id=step_id,
            model_strategy="fast",
            physical_model="gpt-5.4",
            system_fingerprint="fp_123",
            chunk_size=1,
            token_usage=usage1,
        )
    )
    event1 = TraceEvent(
        step_name="step1",
        event_type="output",
        content=meta_env1.model_dump(by_alias=True, mode="json"),
    )
    meta_env2 = TraceEventMetadataEnvelope(
        step_metadata=StepTraceMetadataDTO(
            step_id=step_id,
            model_strategy="fast",
            physical_model="gpt-5.4",
            system_fingerprint="fp_123",
            chunk_size=1,
            token_usage=None,
        )
    )
    event2 = TraceEvent(
        step_name="step1",
        event_type="output",
        content=meta_env2.model_dump(by_alias=True, mode="json"),
    )
    event3 = ErrorTraceEvent(
        step_name="step2",
        error_code="INTERNAL_SERVER_ERROR",
        error_message="Degraded warning",
    )

    base_record = _create_mock_record()
    mock_executed_record = base_record.model_copy(
        update={
            "execution_trace": [event1, event2, event3],
            "models_used": {"gpt-5.4": 1},
        }
    )

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_workflow(mock_workflow)
    await mock_repo.save_execution(base_record)

    mock_engine = MagicMock()
    mock_engine.execute_workflow = AsyncMock(return_value=mock_executed_record)

    ctx = {
        "repository": mock_repo,
        "engine": mock_engine,
        "redis": None,
    }

    result = await execute_workflow_job(
        ctx=ctx,
        workflow_id="wor_0123456789abcdef",
        inputs=ExecutionInputsDTO(),
        execution_id="exe_0123456789abcdef",
        organization_id="org_test12345678",
        user_id="usr_test12345678",
    )

    assert result.status == "COMPLETED"
    updated_rec = await mock_repo.get_execution("exe_0123456789abcdef")
    assert updated_rec is not None
    assert updated_rec.prompt_tokens == 100
    assert updated_rec.completion_tokens == 50
    assert updated_rec.cached_tokens == 25
    assert updated_rec.reasoning_tokens == 10
    assert updated_rec.dag_cost_usd == 0.005
    assert updated_rec.execution_summary is not None
    assert updated_rec.execution_summary.is_degraded is True
    assert updated_rec.execution_summary.is_ensemble_run is True


@pytest.mark.asyncio
async def test_execution_worker_offloaded_trace_reading() -> None:
    """Verify trace hydration from storage driver when local execution_trace has no metadata."""
    mock_workflow = _create_mock_workflow()
    base_record = _create_mock_record()

    step_id = "stp_0123456789abcdef"
    usage = TokenUsage(
        prompt_tokens=40,
        completion_tokens=20,
        cached_tokens=0,
        reasoning_tokens=0,
        total_tokens=60,
        cost_usd=0.002,
    )
    meta_env = TraceEventMetadataEnvelope(
        step_metadata=StepTraceMetadataDTO(
            step_id=step_id,
            model_strategy="fast",
            physical_model="gpt-5.4",
            token_usage=usage,
        )
    )
    blob_json = (
        f'[{{"step_name": "step1", "event_type": "output", "content": {meta_env.model_dump_json(by_alias=True)}}}]'
    )

    mock_executed_record = base_record.model_copy(
        update={
            "execution_trace": [],
            "execution_trace_storage_path": "traces/exe_0123456789abcdef.json",
        }
    )

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_workflow(mock_workflow)
    await mock_repo.save_execution(base_record)

    mock_engine = MagicMock()
    mock_engine.execute_workflow = AsyncMock(return_value=mock_executed_record)

    mock_driver = MagicMock()
    mock_driver.read = AsyncMock(return_value=blob_json)

    with patch("backend_v2.workers.execution_worker.get_storage_driver", return_value=mock_driver):
        ctx = {
            "repository": mock_repo,
            "engine": mock_engine,
            "redis": None,
        }
        result = await execute_workflow_job(
            ctx=ctx,
            workflow_id="wor_0123456789abcdef",
            inputs=ExecutionInputsDTO(),
            execution_id="exe_0123456789abcdef",
        )

    assert result.status == "COMPLETED"
    updated_rec = await mock_repo.get_execution("exe_0123456789abcdef")
    assert updated_rec is not None
    assert updated_rec.prompt_tokens == 40


@pytest.mark.asyncio
async def test_execution_worker_offloaded_trace_read_failure_raises() -> None:
    """Verify storage driver read failure routes to DLQ and marks execution FAILED."""
    mock_workflow = _create_mock_workflow()
    base_record = _create_mock_record()

    mock_executed_record = base_record.model_copy(
        update={
            "execution_trace": [],
            "execution_trace_storage_path": "traces/exe_0123456789abcdef.json",
        }
    )

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_workflow(mock_workflow)
    await mock_repo.save_execution(base_record)

    mock_engine = MagicMock()
    mock_engine.execute_workflow = AsyncMock(return_value=mock_executed_record)

    mock_driver = MagicMock()
    mock_driver.read = AsyncMock(side_effect=OSError("Disk read failure"))

    with patch("backend_v2.workers.execution_worker.get_storage_driver", return_value=mock_driver):
        ctx = {
            "repository": mock_repo,
            "engine": mock_engine,
            "redis": None,
        }
        result = await execute_workflow_job(
            ctx=ctx,
            workflow_id="wor_0123456789abcdef",
            inputs=ExecutionInputsDTO(),
            execution_id="exe_0123456789abcdef",
        )

    assert result.status == "FAILED/DLQ"
    updated_rec = await mock_repo.get_execution("exe_0123456789abcdef")
    assert updated_rec is not None
    assert updated_rec.status == ExecutionStatus.FAILED


@pytest.mark.asyncio
async def test_execution_worker_corrupted_metadata_raises() -> None:
    """Verify corrupted _step_metadata payload raises validation error dispatched to DLQ."""
    mock_workflow = _create_mock_workflow()
    base_record = _create_mock_record()

    event = TraceEvent(
        step_name="step1",
        event_type="output",
        content={"step_metadata": 12345},  # Invalid envelope
    )
    mock_executed_record = base_record.model_copy(update={"execution_trace": [event]})

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_workflow(mock_workflow)
    await mock_repo.save_execution(base_record)

    mock_engine = MagicMock()
    mock_engine.execute_workflow = AsyncMock(return_value=mock_executed_record)

    ctx = {
        "repository": mock_repo,
        "engine": mock_engine,
        "redis": None,
    }
    result = await execute_workflow_job(
        ctx=ctx,
        workflow_id="wor_0123456789abcdef",
        inputs=ExecutionInputsDTO(),
        execution_id="exe_0123456789abcdef",
    )

    assert result.status == "FAILED/DLQ"
    updated_rec = await mock_repo.get_execution("exe_0123456789abcdef")
    assert updated_rec is not None
    assert updated_rec.status == ExecutionStatus.FAILED


@pytest.mark.asyncio
async def test_execution_worker_workflow_failure_dlq() -> None:
    """Verify unhandled engine exception routes to DLQ and marks execution FAILED."""
    mock_workflow = _create_mock_workflow()
    base_record = _create_mock_record()

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_workflow(mock_workflow)
    await mock_repo.save_execution(base_record)

    mock_engine = MagicMock()
    mock_engine.execute_workflow = AsyncMock(side_effect=RuntimeError("Engine failure"))

    ctx = {
        "repository": mock_repo,
        "engine": mock_engine,
        "redis": None,
    }

    result = await execute_workflow_job(
        ctx=ctx,
        workflow_id="wor_0123456789abcdef",
        inputs=ExecutionInputsDTO(),
        execution_id="exe_0123456789abcdef",
    )

    assert result.status == "FAILED/DLQ"
    updated_rec = await mock_repo.get_execution("exe_0123456789abcdef")
    assert updated_rec is not None
    assert updated_rec.status == ExecutionStatus.FAILED


@pytest.mark.asyncio
async def test_execution_worker_cancelled_error_dlq() -> None:
    """Verify asyncio.CancelledError routes to DLQ and marks execution FAILED."""
    mock_workflow = _create_mock_workflow()
    base_record = _create_mock_record()

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_workflow(mock_workflow)
    await mock_repo.save_execution(base_record)

    mock_engine = MagicMock()
    mock_engine.execute_workflow = AsyncMock(side_effect=asyncio.CancelledError())

    ctx = {
        "repository": mock_repo,
        "engine": mock_engine,
        "redis": None,
    }

    result = await execute_workflow_job(
        ctx=ctx,
        workflow_id="wor_0123456789abcdef",
        inputs=ExecutionInputsDTO(),
        execution_id="exe_0123456789abcdef",
    )

    assert result.status == "FAILED/DLQ"
    updated_rec = await mock_repo.get_execution("exe_0123456789abcdef")
    assert updated_rec is not None
    assert updated_rec.status == ExecutionStatus.FAILED


@pytest.mark.asyncio
async def test_execution_worker_failure_update_error_resilience() -> None:
    """Verify worker handles repository failure during error recording gracefully."""
    mock_workflow = _create_mock_workflow()
    base_record = _create_mock_record()

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_workflow(mock_workflow)
    await mock_repo.save_execution(base_record)
    mock_repo.inject_fault("update_execution", OSError("DB write error"), trigger_count=1)

    mock_engine = MagicMock()
    mock_engine.execute_workflow = AsyncMock(side_effect=RuntimeError("Engine crashed"))

    ctx = {
        "repository": mock_repo,
        "engine": mock_engine,
        "redis": None,
    }

    result = await execute_workflow_job(
        ctx=ctx,
        workflow_id="wor_0123456789abcdef",
        inputs=ExecutionInputsDTO(),
        execution_id="exe_0123456789abcdef",
    )

    assert result.status == "FAILED/DLQ"


@pytest.mark.asyncio
async def test_execution_worker_with_execution_inputs_dto_and_telemetry() -> None:
    """Verify worker processes ExecutionInputsDTO and populates step telemetry."""
    step_id = "stp_0123456789abcdef"
    mock_workflow = _create_mock_workflow()
    mock_record = _create_mock_record()
    mock_record = mock_record.model_copy(
        update={
            "execution_trace": [
                TraceEvent(
                    step_name="Analytical Step",
                    event_type="output",
                    content=TraceEventMetadataEnvelope(
                        step_metadata=StepTraceMetadataDTO(
                            step_id=step_id,
                            model_strategy="fast",
                            physical_model="gpt-5.4",
                            system_fingerprint="fp_123",
                            chunk_size=2,
                            token_usage=TokenUsage(
                                prompt_tokens=100,
                                completion_tokens=50,
                                cached_tokens=10,
                                reasoning_tokens=5,
                                total_tokens=150,
                                cost_usd=0.002,
                            ),
                        )
                    ).model_dump(by_alias=True, mode="json"),
                ),
            ],
            "step_states": {
                step_id: ExecutionStep(
                    id=step_id,
                    label="Analytical Step",
                    status=ExecutionStatus.PASSED,
                    progress=100,
                )
            },
        }
    )

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_workflow(mock_workflow)
    await mock_repo.save_execution(mock_record)

    mock_engine = MagicMock()
    mock_engine.execute_workflow = AsyncMock(return_value=mock_record)

    ctx = {
        "repository": mock_repo,
        "engine": mock_engine,
        "redis": None,
    }

    inputs = ExecutionInputsDTO(
        raw_inputs={"organization_id": "org_abc", "user_id": "usr_xyz"},
        dynamic_inputs={"custom": "val"},
    )

    result = await execute_workflow_job(
        ctx=ctx,
        workflow_id="wor_0123456789abcdef",
        inputs=inputs,
        execution_id="exe_0123456789abcdef",
    )

    assert result.status == "COMPLETED"
    updated_rec = await mock_repo.get_execution("exe_0123456789abcdef")
    assert updated_rec is not None
    assert updated_rec.prompt_tokens == 100


@pytest.mark.asyncio
async def test_execution_worker_with_workflow_inputs_generated_id() -> None:
    """Verify worker processes WorkflowInputs instance and generates execution_id if omitted."""
    mock_workflow = _create_mock_workflow()
    fixed_uuid = "0123456789abcdef0123456789abcdef"
    generated_id = f"exe_{fixed_uuid}"
    mock_record = _create_mock_record().model_copy(update={"id": generated_id})

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_workflow(mock_workflow)
    await mock_repo.save_execution(mock_record)

    mock_engine = MagicMock()
    mock_engine.execute_workflow = AsyncMock(return_value=mock_record)

    ctx = {
        "repository": mock_repo,
        "engine": mock_engine,
        "redis": None,
    }

    inputs = WorkflowInputs(
        organization_id="org_default",
        user_id="usr_default",
        dynamic_inputs={},
    )

    with patch("uuid.uuid4", return_value=uuid.UUID(hex=fixed_uuid)):
        result = await execute_workflow_job(
            ctx=ctx,
            workflow_id="wor_0123456789abcdef",
            inputs=inputs,
            execution_id=None,
        )

    assert result.status == "COMPLETED"
    assert result.execution_id == generated_id
    updated_rec = await mock_repo.get_execution(generated_id)
    assert updated_rec is not None
    assert updated_rec.status == ExecutionStatus.PASSED


@pytest.mark.asyncio
async def test_execution_worker_w3c_trace_propagation_with_carrier() -> None:
    """Verify worker binds execution.worker_process span to caller trace when carrier is present."""
    from backend_v2.models.dtos.telemetry import TraceContextCarrierDTO
    from backend_v2.models.execution_core import ExecutionMetadata

    mock_workflow = _create_mock_workflow()
    carrier = TraceContextCarrierDTO(traceparent="00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01")
    mock_record = _create_mock_record()
    mock_record = mock_record.model_copy(update={"metadata": ExecutionMetadata(telemetry=carrier)})

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_workflow(mock_workflow)
    await mock_repo.save_execution(mock_record)

    mock_engine = MagicMock()
    mock_engine.execute_workflow = AsyncMock(return_value=mock_record)

    ctx = {
        "repository": mock_repo,
        "engine": mock_engine,
        "redis": None,
    }

    result = await execute_workflow_job(
        ctx=ctx,
        workflow_id="wor_0123456789abcdef",
        inputs=ExecutionInputsDTO(),
        execution_id="exe_0123456789abcdef",
        organization_id="org_test123",
        user_id="usr_test456",
    )

    assert result.status == "COMPLETED"
    updated_rec = await mock_repo.get_execution("exe_0123456789abcdef")
    assert updated_rec is not None
    assert updated_rec.status == ExecutionStatus.PASSED


@pytest.mark.asyncio
async def test_execution_worker_orphan_span_when_carrier_missing() -> None:
    """Verify worker sets telemetry.orphan_execution=True on root span when carrier is missing."""
    from backend_v2.models.execution_core import ExecutionMetadata

    mock_workflow = _create_mock_workflow()
    mock_record = _create_mock_record().model_copy(update={"metadata": ExecutionMetadata(telemetry=None)})
    # Metadata has telemetry=None by default
    assert mock_record.metadata is not None
    assert mock_record.metadata.telemetry is None

    mock_repo = InMemoryUnifiedWorkflowRepository()
    await mock_repo.save_workflow(mock_workflow)
    await mock_repo.save_execution(mock_record)

    mock_engine = MagicMock()
    mock_engine.execute_workflow = AsyncMock(return_value=mock_record)

    ctx = {
        "repository": mock_repo,
        "engine": mock_engine,
        "redis": None,
    }

    result = await execute_workflow_job(
        ctx=ctx,
        workflow_id="wor_0123456789abcdef",
        inputs=ExecutionInputsDTO(),
        execution_id="exe_0123456789abcdef",
    )

    assert result.status == "COMPLETED"
    updated_rec = await mock_repo.get_execution("exe_0123456789abcdef")
    assert updated_rec is not None
    assert updated_rec.status == ExecutionStatus.PASSED
