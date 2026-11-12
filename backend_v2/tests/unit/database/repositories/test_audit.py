"""Unit tests for AuditRepositoryImpl backed by EntityPersistencePort."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from backend_v2.database.repositories.audit import AuditRepositoryImpl
from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.models.domain.base import AuditLogCreateDTO
from backend_v2.tests.factories.model_factories import ExecutionRecordFactory, UsageRecordFactory
from backend_v2.tests.fakes.in_memory_uow import InMemoryUnitOfWork


@pytest.fixture
def base_uow() -> InMemoryUnitOfWork:
    """Provide a shared InMemoryUnitOfWork backing store for repository unit tests."""
    return InMemoryUnitOfWork()


@pytest.fixture
def repo(base_uow: InMemoryUnitOfWork) -> AuditRepositoryImpl:
    """Provide an AuditRepositoryImpl bound to the shared InMemoryUnitOfWork store."""
    return AuditRepositoryImpl(uow_factory=lambda: InMemoryUnitOfWork(base_uow.store))


@pytest.mark.asyncio
async def test_audit_logs_insert_and_filters(repo: AuditRepositoryImpl) -> None:
    """Verify log_audit_event and get_audit_logs filter by organization, actor, and event_type."""
    org_id = "org_0195f3a0000070018234567890abcdef"
    usr_id = "usr_0195f3a0000070018234567890abcdef"
    exe_id = "exe_0195f3a0000070018234567890abcdef"

    await repo.log_audit_event(
        AuditLogCreateDTO(
            event_type="WORKFLOW_EXECUTED",
            actor_id=usr_id,
            organization_id=org_id,
            execution_id=exe_id,
            resource_type="execution",
            resource_id=exe_id,
            details={"zone": "eu-north-1"},
        )
    )
    await repo.log_audit_event(
        AuditLogCreateDTO(
            event_type="SYSTEM_SYNC",
            actor_id="system",
            organization_id="system",
            resource_type="system",
            resource_id="seed",
            details={},
        )
    )

    logs = await repo.get_audit_logs(
        organization_id=org_id,
        actor_id=usr_id,
        event_type="WORKFLOW_EXECUTED",
        limit=50,
    )
    assert len(logs) == 1
    assert logs[0].event_type == "WORKFLOW_EXECUTED"
    assert logs[0].organization_id == org_id
    assert logs[0].actor_id == usr_id
    assert logs[0].execution_id == exe_id
    assert logs[0].details == {"zone": "eu-north-1"}


@pytest.mark.asyncio
async def test_log_usage_get_usage_records_and_rollup(repo: AuditRepositoryImpl) -> None:
    """Verify log_usage, get_usage_records across scopes, and aggregate_organization_usage."""
    org_id = "org_0195f3a0000070018234567890abcdef"
    usr_id = "usr_0195f3a0000070018234567890abcdef"
    rec1 = UsageRecordFactory.build(
        org_id=org_id,
        user_id=usr_id,
        model="gemini-2.5-pro",
        input_tokens=100,
        output_tokens=50,
        cached_tokens=20,
        cost_usd=0.005,
        timestamp=datetime(2026, 8, 15, 12, 0, 0, tzinfo=UTC),
    )
    rec2 = UsageRecordFactory.build(
        org_id=org_id,
        user_id="system",
        model="gemini-2.5-flash",
        input_tokens=40,
        output_tokens=10,
        cached_tokens=5,
        cost_usd=0.001,
        timestamp=datetime(2026, 8, 16, 12, 0, 0, tzinfo=UTC),
    )
    await repo.log_usage(rec1)
    await repo.log_usage(rec2)

    org_records = await repo.get_usage_records("organization", org_id, since="2026-08-01T00:00:00Z")
    assert len(org_records) == 2

    user_records = await repo.get_usage_records("user", usr_id)
    assert len(user_records) == 1
    assert user_records[0].id == rec1.id

    sys_records = await repo.get_usage_records("system")
    assert len(sys_records) == 2

    rollup = await repo.aggregate_organization_usage(
        organization_id=org_id,
        since=datetime(2026, 8, 1, 0, 0, 0, tzinfo=UTC),
    )
    assert rollup.record_count == 2
    assert rollup.total_prompt_tokens == 140
    assert rollup.total_completion_tokens == 60
    assert rollup.total_cached_tokens == 25
    assert rollup.total_cost_usd == pytest.approx(0.006)


@pytest.mark.asyncio
async def test_get_detailed_usage_org_and_user_scopes(
    repo: AuditRepositoryImpl,
    base_uow: InMemoryUnitOfWork,
) -> None:
    """Verify get_detailed_usage combines SQL rollup totals with execution model and workflow breakdowns."""
    org_id = "org_0195f3a0000070018234567890abcdef"
    usr_id = "usr_0195f3a0000070028234567890abcdef"
    wf_id = "wor_0195f3a0000070018234567890abcdef"
    completed_1 = datetime(2026, 8, 15, 12, 0, 0, tzinfo=UTC)
    completed_2 = datetime(2026, 8, 16, 12, 0, 0, tzinfo=UTC)

    exe_1 = ExecutionRecordFactory.build(
        organization_id=org_id,
        created_by=usr_id,
        workflow_id=wf_id,
        cost_estimate=0.05,
        models_used={"gemini-2.5-pro": 2},
        completed_at=completed_1,
        created_at=completed_1,
    )
    exe_2 = ExecutionRecordFactory.build(
        organization_id=org_id,
        created_by=usr_id,
        workflow_id=wf_id,
        cost_estimate=0.03,
        models_used={"gemini-2.5-flash": 1, "gemini-2.5-pro": 1},
        completed_at=completed_2,
        created_at=completed_2,
    )
    async with InMemoryUnitOfWork(base_uow.store) as uow:
        await uow.entities.save_execution(exe_1)
        await uow.entities.save_execution(exe_2)
        await uow.commit()

    await repo.log_usage(
        UsageRecordFactory.build(
            org_id=org_id,
            user_id=usr_id,
            execution_id=exe_1.id,
            input_tokens=1000,
            output_tokens=400,
            cost_usd=0.08,
            timestamp=completed_1,
        )
    )

    org_usage = await repo.get_detailed_usage(
        scope="org",
        target_id=org_id,
        since="2026-08-01T00:00:00Z",
    )
    assert org_usage.total_cost_usd == pytest.approx(0.08)
    assert org_usage.total_tokens == 1400
    assert org_usage.by_model == {"gemini-2.5-pro": 3, "gemini-2.5-flash": 1}
    assert org_usage.by_workflow == {wf_id: 2}

    user_usage = await repo.get_detailed_usage(
        scope="user",
        target_id=usr_id,
        since="2026-08-01T00:00:00Z",
    )
    assert user_usage.total_cost_usd == pytest.approx(0.08)
    assert user_usage.total_tokens == 1400
    assert user_usage.by_model == {"gemini-2.5-pro": 3, "gemini-2.5-flash": 1}
    assert user_usage.by_workflow == {wf_id: 2}


@pytest.mark.asyncio
async def test_audit_repository_invalid_since_and_missing_uow_failure(
    repo: AuditRepositoryImpl,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify invalid ISO timestamps raise VALIDATION_FAILED and unconfigured UoW raises ConfigurationError."""
    with pytest.raises(AppException) as exc_since:
        await repo.get_usage_records("organization", "org_0195f3a0000070018234567890abcdef", since="not-a-date")
    assert exc_since.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    with pytest.raises(AppException) as exc_detailed:
        await repo.get_detailed_usage("org", "org_0195f3a0000070018234567890abcdef", since="invalid_date_format")
    assert exc_detailed.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    monkeypatch.setattr("backend_v2.database.repositories.base.get_registered_uow_factory", lambda: None)
    unconfigured_repo = AuditRepositoryImpl(uow_factory=None)
    with pytest.raises(ConfigurationError) as cfg_exc:
        await unconfigured_repo.get_audit_logs()
    assert cfg_exc.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value
