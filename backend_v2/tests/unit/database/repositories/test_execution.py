"""Unit tests for ExecutionRepositoryImpl over EntityPersistencePort."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.database.postgres.pool import PostgresPoolManager
from backend_v2.database.postgres.uow import PostgresUnitOfWork
from backend_v2.database.repositories.execution import ExecutionRepositoryImpl
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.execution import ExecutionRecord, FrozenContext, MCPAuditTrace
from backend_v2.models.domain.inputs import WorkflowInputs, WorkflowInputsIngress
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.dtos.trace import (
    ExecutionCreateDTO,
    ExecutionUpdateDTO,
    ProgressTracePayloadDTO,
    TraceEventMetadataDTO,
)
from backend_v2.models.enums import ExecutionStatus, StorageBackend, SystemLocale
from backend_v2.models.state import TraceEvent
from backend_v2.services.file_driver import FileDriver
from backend_v2.settings import Settings
from backend_v2.tests.factories.model_factories import ExecutionRecordFactory
from backend_v2.tests.fakes.in_memory_uow import InMemoryAsyncPgPool, InMemoryUnitOfWork

_EXE_ID = "exe_0195f3a0000070018234567890abcdef"
_EXE_ID_2 = "exe_0195f3a0000070028234567890abcdef"
_EXE_MISSING = "exe_0195f3a0000070008000000000000099"
_WF_ID = "wf_0195f3a0000070018234567890abcdef"
_PRF_ID = "prf_0195f3a0000070018234567890abcdef"
_ORG_ID = "org_0195f3a0000070018234567890abcdef"
_ORG_OTHER = "org_0195f3a0000070028234567890abcdef"
_USR_ID = "usr_0195f3a0000070018234567890abcdef"
_USR_OTHER = "usr_0195f3a0000070028234567890abcdef"
_STP_ID = "stp_0195f3a0000070018234567890abcdef"
_BLK_ID = "blk_0195f3a0000070018234567890abcdef"
_TRC_ID_1 = "trc_0195f3a0000070018234567890abcdef"


def _make_trace_event(content_text: str = "ok") -> TraceEvent:
    """Build a strict TraceEvent with canonical step ID and explicit optional fields."""
    return TraceEvent(
        step_name=_STP_ID,
        event_type="progress",
        content=ProgressTracePayloadDTO(message=content_text, progress_pct=50),
        reasoning=None,
        metadata=TraceEventMetadataDTO(mcp_audit_traces=[]),
        mcp_audit_traces=[],
    )


@pytest.fixture
def base_uow() -> InMemoryUnitOfWork:
    """Provide a shared InMemoryUnitOfWork store for stateful repository tests."""
    return InMemoryUnitOfWork()


@pytest.fixture
def repo(base_uow: InMemoryUnitOfWork) -> ExecutionRepositoryImpl:
    """Provide an ExecutionRepositoryImpl backed by the stateful InMemoryUnitOfWork store."""
    return ExecutionRepositoryImpl(uow_factory=lambda: InMemoryUnitOfWork(base_uow.store))


@pytest.fixture
def valid_execution_doc() -> ExecutionRecord:
    """Provide a valid ExecutionRecord instance via Polyfactory."""
    return ExecutionRecordFactory.build(
        id=_EXE_ID,
        workflow_id=_WF_ID,
        output_profile_id=_PRF_ID,
        target_locale=SystemLocale.FI,
        status=ExecutionStatus.PASSED,
        organization_id=_ORG_ID,
        created_by=_USR_ID,
        completed_at=datetime(2026, 8, 30, 12, 0, 0, tzinfo=UTC),
        execution_trace_storage_path=None,
        frozen_context_storage_path=None,
        context_variables_storage_path=None,
    )


@pytest.mark.asyncio
async def test_execution_status_and_get_roundtrip(
    repo: ExecutionRepositoryImpl,
    base_uow: InMemoryUnitOfWork,
    valid_execution_doc: ExecutionRecord,
) -> None:
    """Positive & Negative: verify get_execution_status and get_execution roundtrip and missing returns."""
    assert await repo.get_execution_status(_EXE_MISSING) is None
    assert await repo.get_execution(_EXE_MISSING) is None

    async with InMemoryUnitOfWork(base_uow.store) as uow:
        await uow.entities.save_execution(valid_execution_doc)

    assert await repo.get_execution_status(_EXE_ID) == "PASSED"
    record = await repo.get_execution(_EXE_ID)
    assert isinstance(record, ExecutionRecord)
    assert record.id == _EXE_ID
    assert record.status == ExecutionStatus.PASSED

    unhydrated = await repo.get_execution(_EXE_ID, hydrate=False)
    assert unhydrated is not None
    assert unhydrated.id == _EXE_ID


@pytest.mark.asyncio
async def test_create_update_append_delete_and_matrix_count(
    repo: ExecutionRepositoryImpl,
) -> None:
    """Positive: verify create_execution across raw_inputs variants, update, append_trace_event, count, and delete."""
    dto_none_inputs = ExecutionCreateDTO(
        workflow_id=_WF_ID,
        output_profile_id=_PRF_ID,
        target_locale="fi",
        active_profile_id=_PRF_ID,
        organization_id=_ORG_ID,
        created_by=_USR_ID,
    )
    created_id = await repo.create_execution(dto_none_inputs)
    assert created_id.startswith("exe_")

    dto_wf_inputs = ExecutionCreateDTO(
        workflow_id=_WF_ID,
        target_locale="en",
        raw_inputs=WorkflowInputs(dynamic_inputs={"memo": "text"}),
        organization_id=_ORG_ID,
        created_by=_USR_ID,
    )
    created_wf_id = await repo.create_execution(dto_wf_inputs)
    assert created_wf_id.startswith("exe_")

    dto_ingress_inputs = ExecutionCreateDTO(
        workflow_id=_WF_ID,
        target_locale="fi",
        raw_inputs=WorkflowInputsIngress(dynamic_inputs={"memo": "ingress text"}),
        organization_id=_ORG_ID,
        created_by=_USR_ID,
    )
    created_ing_id = await repo.create_execution(dto_ingress_inputs)
    assert created_ing_id.startswith("exe_")

    assert (
        await repo.update_execution(
            created_id,
            ExecutionUpdateDTO(
                status=ExecutionStatus.RUNNING,
                context_variables=ContextVariablesDTO(variables={"matrix_id": _BLK_ID}),
            ),
        )
        is True
    )

    event = _make_trace_event("step completed")
    assert await repo.append_trace_event(created_id, event) is True
    assert await repo.append_trace_event(_EXE_MISSING, event) is False

    refetched = await repo.get_execution(created_id)
    assert refetched is not None
    assert len(refetched.execution_trace) == 1

    assert await repo.delete_execution(created_id) is True
    assert await repo.delete_execution(created_id) is False


@pytest.mark.asyncio
async def test_get_all_executions_filters_and_recent_completed(
    repo: ExecutionRepositoryImpl,
    base_uow: InMemoryUnitOfWork,
    valid_execution_doc: ExecutionRecord,
) -> None:
    """Verify organization/user filtering on get_all_executions and sorting/limits on get_recent_completed_executions."""
    older_completed = ExecutionRecordFactory.build(
        id=_EXE_ID_2,
        workflow_id=_WF_ID,
        status=ExecutionStatus.PASSED,
        organization_id=_ORG_OTHER,
        created_by=_USR_OTHER,
        completed_at=datetime(2026, 8, 29, 8, 0, 0),
        execution_trace_storage_path=None,
        frozen_context_storage_path=None,
        context_variables_storage_path=None,
    )
    running_rec = ExecutionRecordFactory.build(
        workflow_id=_WF_ID,
        status=ExecutionStatus.RUNNING,
        organization_id=_ORG_ID,
        created_by=_USR_OTHER,
        completed_at=None,
        execution_trace_storage_path=None,
        frozen_context_storage_path=None,
        context_variables_storage_path=None,
    )
    null_completed_ts = ExecutionRecordFactory.build(
        workflow_id=_WF_ID,
        status=ExecutionStatus.PASSED,
        organization_id=_ORG_ID,
        created_by=_USR_ID,
        completed_at=None,
        execution_trace_storage_path=None,
        frozen_context_storage_path=None,
        context_variables_storage_path=None,
    )

    async with InMemoryUnitOfWork(base_uow.store) as uow:
        await uow.entities.save_execution(valid_execution_doc)
        await uow.entities.save_execution(older_completed)
        await uow.entities.save_execution(running_rec)
        await uow.entities.save_execution(null_completed_ts)

    filtered = await repo.get_all_executions(organization_id=_ORG_ID, user_id=_USR_ID)
    assert {r.id for r in filtered} == {_EXE_ID, null_completed_ts.id}

    assert await repo.get_recent_completed_executions(limit=0) == []
    recent = await repo.get_recent_completed_executions(limit=2)
    assert [r.id for r in recent] == [_EXE_ID, _EXE_ID_2]


@pytest.mark.asyncio
async def test_frozen_context_preserves_mcp_tool_audit_inline(
    repo: ExecutionRepositoryImpl,
    base_uow: InMemoryUnitOfWork,
) -> None:
    """Verify FrozenContext.mcp_tool_audit persists inline on ExecutionRecord without subcollection stripping."""
    audit_item = MCPAuditTrace(
        id=_TRC_ID_1,
        tool_id="tavily_search",
        step_name=_STP_ID,
        query="market growth",
        reasoning="verify claim",
        timestamp=datetime(2026, 8, 31, 1, 0, 0, tzinfo=UTC),
    )
    fc = FrozenContext(
        compiled_prompts={"p1": "prompt"},
        injected_theory={},
        generated_schemas={},
        ui_hints_snapshot={},
        mcp_tool_audit=[audit_item],
    )
    rec = ExecutionRecordFactory.build(
        id=_EXE_ID,
        workflow_id=_WF_ID,
        status=ExecutionStatus.PASSED,
        frozen_context=fc,
        execution_trace_storage_path=None,
        frozen_context_storage_path=None,
        context_variables_storage_path=None,
    )
    async with InMemoryUnitOfWork(base_uow.store) as uow:
        await uow.entities.save_execution(rec)

    loaded = await repo.get_execution(_EXE_ID)
    assert loaded is not None
    assert loaded.frozen_context is not None
    assert len(loaded.frozen_context.mcp_tool_audit) == 1
    assert loaded.frozen_context.mcp_tool_audit[0].id == _TRC_ID_1


@pytest.mark.asyncio
async def test_update_execution_optimistic_concurrency_control_conflict_failure(
    repo: ExecutionRepositoryImpl,
    base_uow: InMemoryUnitOfWork,
    valid_execution_doc: ExecutionRecord,
) -> None:
    """Positive & Negative: verify OCC state_version increments, missing returns False, and stale raises 409 CONFLICT."""
    assert (
        await repo.update_execution(
            _EXE_MISSING,
            ExecutionUpdateDTO(status=ExecutionStatus.RUNNING, expected_state_version=1),
        )
        is False
    )

    seeded = valid_execution_doc.model_copy(update={"state_version": 2})
    async with InMemoryUnitOfWork(base_uow.store) as uow:
        await uow.entities.save_execution(seeded)

    assert (
        await repo.update_execution(
            _EXE_ID,
            ExecutionUpdateDTO(status=ExecutionStatus.PASSED, expected_state_version=2),
        )
        is True
    )
    after_update = await repo.get_execution(_EXE_ID)
    assert after_update is not None
    assert after_update.state_version == 3

    with pytest.raises(AppException) as exc_info:
        await repo.update_execution(
            _EXE_ID,
            ExecutionUpdateDTO(status=ExecutionStatus.FAILED, expected_state_version=2),
        )
    assert exc_info.value.status_code == 409
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFLICT.value


@pytest.mark.asyncio
async def test_large_blob_offload_and_hydration_roundtrip_and_errors(
    repo: ExecutionRepositoryImpl,
    base_uow: InMemoryUnitOfWork,
    valid_execution_doc: ExecutionRecord,
) -> None:
    """Positive & Negative: verify >100KB blob offloading, hydration, pending empty-blob tolerance, and corruption errors."""
    big_events = [_make_trace_event("x" * 600) for _ in range(220)]
    big_fc = FrozenContext(
        compiled_prompts={"large": "p" * 110_000},
        injected_theory={},
        generated_schemas={},
        ui_hints_snapshot={},
        mcp_tool_audit=[],
    )
    big_cv = ContextVariablesDTO(variables={"blob": "v" * 110_000})

    saved_blobs: dict[str, bytes] = {}
    mock_storage = AsyncMock(spec=FileDriver)

    async def _save_blob(path: str, data: bytes | str) -> bool:
        saved_blobs[path] = data.encode("utf-8") if isinstance(data, str) else data
        return True

    async def _read_blob(path: str) -> bytes:
        return saved_blobs[path]

    mock_storage.save.side_effect = _save_blob
    mock_storage.read.side_effect = _read_blob

    async with InMemoryUnitOfWork(base_uow.store) as uow:
        await uow.entities.save_execution(valid_execution_doc)

    with patch("backend_v2.database.repositories.execution.get_storage_driver", return_value=mock_storage):
        assert await repo.update_execution(_EXE_MISSING, ExecutionUpdateDTO(execution_trace=big_events)) is False
        assert (
            await repo.update_execution(
                _EXE_ID,
                ExecutionUpdateDTO(
                    execution_trace=big_events,
                    frozen_context=big_fc,
                    context_variables=big_cv,
                ),
            )
            is True
        )

        raw_stored = await repo.get_execution(_EXE_ID, hydrate=False)
        assert raw_stored is not None
        assert raw_stored.execution_trace == []
        assert raw_stored.frozen_context is None or raw_stored.frozen_context.compiled_prompts == {}
        assert raw_stored.execution_trace_storage_path is not None
        assert raw_stored.frozen_context_storage_path is not None
        assert raw_stored.context_variables_storage_path is not None

        hydrated = await repo.get_execution(_EXE_ID, hydrate=True)
        assert hydrated is not None
        assert len(hydrated.execution_trace) == 220
        assert hydrated.frozen_context is not None
        assert "large" in hydrated.frozen_context.compiled_prompts
        assert "blob" in hydrated.context_variables.variables

        # Running execution tolerates empty trace blob
        running_offloaded = ExecutionRecordFactory.build(
            id=_EXE_ID_2,
            workflow_id=_WF_ID,
            status=ExecutionStatus.RUNNING,
            execution_trace_storage_path=f"executions/{_EXE_ID_2}/execution_trace.json",
            frozen_context_storage_path=None,
            context_variables_storage_path=None,
        )
        saved_blobs[f"executions/{_EXE_ID_2}/execution_trace.json"] = b""
        async with InMemoryUnitOfWork(base_uow.store) as uow:
            await uow.entities.save_execution(running_offloaded)
        hydrated_running = await repo.get_execution(_EXE_ID_2)
        assert hydrated_running is not None
        assert hydrated_running.execution_trace == []

        # Completed execution with empty trace blob raises DATA_CORRUPTION
        passed_empty = running_offloaded.model_copy(update={"status": ExecutionStatus.PASSED})
        async with InMemoryUnitOfWork(base_uow.store) as uow:
            await uow.entities.save_execution(passed_empty)
        with pytest.raises(AppException) as empty_exc:
            await repo.get_execution(_EXE_ID_2)
        assert empty_exc.value.status_code == 500
        assert empty_exc.value.details["error_code"] == ErrorCodes.DATA_CORRUPTION.value

        # Storage save failure raises INTERNAL_SERVER_ERROR
        mock_storage.save.side_effect = RuntimeError("disk full")
        with pytest.raises(AppException) as save_exc:
            await repo.update_execution(_EXE_ID, ExecutionUpdateDTO(execution_trace=big_events))
        assert save_exc.value.status_code == 500
        assert save_exc.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR.value


@pytest.mark.asyncio
async def test_hydrate_frozen_context_and_context_vars_corruption_failures(
    repo: ExecutionRepositoryImpl,
    base_uow: InMemoryUnitOfWork,
) -> None:
    """Negative: corrupt or empty frozen_context / context_variables blobs raise DATA_CORRUPTION."""
    mock_storage = AsyncMock(spec=FileDriver)
    mock_storage.read.return_value = b""

    fc_rec = ExecutionRecordFactory.build(
        id=_EXE_ID,
        workflow_id=_WF_ID,
        status=ExecutionStatus.PASSED,
        execution_trace_storage_path=None,
        frozen_context_storage_path=f"executions/{_EXE_ID}/frozen_context.json",
        context_variables_storage_path=None,
    )
    cv_rec = ExecutionRecordFactory.build(
        id=_EXE_ID_2,
        workflow_id=_WF_ID,
        status=ExecutionStatus.PASSED,
        execution_trace_storage_path=None,
        frozen_context_storage_path=None,
        context_variables_storage_path=f"executions/{_EXE_ID_2}/context_variables.json",
    )
    async with InMemoryUnitOfWork(base_uow.store) as uow:
        await uow.entities.save_execution(fc_rec)
        await uow.entities.save_execution(cv_rec)

    with patch("backend_v2.database.repositories.execution.get_storage_driver", return_value=mock_storage):
        with pytest.raises(AppException) as fc_exc:
            await repo.get_execution(_EXE_ID)
        assert fc_exc.value.details["error_code"] == ErrorCodes.DATA_CORRUPTION.value

        mock_storage.read.return_value = json.dumps({"invalid_cv": 1}).encode("utf-8")
        with pytest.raises(AppException) as cv_exc:
            await repo.get_execution(_EXE_ID_2)
        assert cv_exc.value.details["error_code"] == ErrorCodes.DATA_CORRUPTION.value


@pytest.mark.asyncio
async def test_execution_postgres_invalid_prefix_and_storage_fault_failure() -> None:
    """Negative: invalid ID prefix raises VALIDATION_FAILED and SQL fault raises STORAGE_ACCESS_FAILED."""
    pool = InMemoryAsyncPgPool()
    settings = Settings(
        storage_backend=StorageBackend.POSTGRES,
        postgres_host="db.internal",
        postgres_port=5432,
        postgres_user="quorum",
        postgres_db="quorum",
        postgres_command_timeout_seconds=5.0,
    )
    pool_mgr = PostgresPoolManager(settings=settings, pool=pool)
    pg_repo = ExecutionRepositoryImpl(uow_factory=lambda: PostgresUnitOfWork(pool_mgr))

    with pytest.raises(AppException) as invalid_exc:
        await pg_repo.get_execution(_WF_ID)
    assert invalid_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    try:
        pool.inject_fault("fetch", RuntimeError("simulated list failure"))
        with pytest.raises(AppException) as fault_exc:
            await pg_repo.get_all_executions()
        assert fault_exc.value.status_code == 500
        assert fault_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value
    finally:
        pool.clear_faults()
