"""Unit tests for AuditRepositoryImpl."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.audit import AuditRepositoryImpl
from backend_v2.models.domain.base import (
    AuditLogCreateDTO,
    AuditLogEntry,
    UsageAggregateDTO,
    UsageAggregateUpdateDTO,
    UsageRecord,
)


@pytest.fixture
def mock_driver() -> AsyncMock:
    """Mock storage driver."""
    driver = AsyncMock(spec=StorageDriver)
    driver.query.return_value = []
    driver.get.return_value = None
    driver.upsert.return_value = "aud_123"
    driver.update.return_value = True
    driver.delete.return_value = True
    return driver


@pytest.fixture
def repo(mock_driver: AsyncMock) -> AuditRepositoryImpl:
    """Audit repository fixture."""
    return AuditRepositoryImpl(mock_driver)


@pytest.mark.asyncio
async def test_audit_logs_filters_and_corruption(repo: AuditRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive: tests audit logging with multiple filters and skipping corrupted records."""
    valid_audit = AuditLogEntry(
        timestamp=datetime.now(timezone.utc),
        level="INFO",
        message="Workflow started",
        context={"org_id": "org_123"},
    ).model_dump(mode="json")
    corrupted_audit = {"id": "aud_corrupted", "timestamp": "invalid_date"}
    mock_driver.query.return_value = [corrupted_audit, valid_audit]

    logs = await repo.get_audit_logs(
        organization_id="org_123",
        actor_id="usr_123",
        action="execute",
        limit=50,
    )
    assert len(logs) == 1
    assert logs[0].level == "INFO"
    assert logs[0].message == "Workflow started"

    await repo.log_audit_event(AuditLogCreateDTO(action="create", actor_id="usr_123", organization_id="org_123"))
    mock_driver.upsert.assert_called()


@pytest.mark.asyncio
async def test_log_usage_model_and_dict(repo: AuditRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive: tests log_usage with UsageRecord model instance."""
    model_usage = UsageRecord(
        id="usg_1",
        org_id="org_123",
        user_id="usr_123",
        model="gpt-4o",
        input_tokens=10,
        output_tokens=5,
        cost_usd=0.001,
        timestamp=datetime.now(timezone.utc),
    )
    await repo.log_usage(model_usage)
    assert mock_driver.upsert.call_count == 1


@pytest.mark.asyncio
async def test_get_usage_records_scopes_and_corruption(repo: AuditRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive: tests get_usage_records across scopes and handles corruption gracefully."""
    valid_usage = UsageRecord(
        id="usg_1",
        org_id="org_123",
        user_id="usr_123",
        model="gpt-4o",
        input_tokens=100,
        output_tokens=50,
        cost_usd=0.005,
        timestamp=datetime.now(timezone.utc),
    ).model_dump(mode="json")
    corrupted_usage = {"id": "usg_bad", "input_tokens": "not_an_int"}
    mock_driver.query.return_value = [corrupted_usage, valid_usage]

    org_records = await repo.get_usage_records("organization", "org_123", since="2026-08-01T00:00:00Z")
    assert len(org_records) == 1
    assert org_records[0].input_tokens == 100

    user_records = await repo.get_usage_records("user", "usr_123")
    assert len(user_records) == 1


@pytest.mark.asyncio
async def test_usage_aggregates_upsert_and_merge(repo: AuditRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive: tests usage aggregate initial creation and subsequent merge updates."""
    # 1. Initial creation (not existing)
    mock_driver.get.return_value = None
    update_data = UsageAggregateUpdateDTO(
        input_tokens=500,
        output_tokens=200,
        cached_tokens=100,
        cost_usd=0.02,
        execution_count=5,
    )
    await repo.upsert_usage_aggregate("organization", "org_123", "2026-08", update_data)
    mock_driver.upsert.assert_called()

    # 2. Existing aggregate merge
    existing_agg = UsageAggregateDTO(
        organization_id="org_123",
        period="2026-08",
        total_input_tokens=500,
        total_output_tokens=200,
        total_cached_tokens=100,
        total_cost_usd=0.02,
        execution_count=5,
    ).model_dump(mode="json")
    mock_driver.get.return_value = existing_agg
    await repo.upsert_usage_aggregate(
        "organization",
        "org_123",
        "2026-08",
        UsageAggregateUpdateDTO(
            input_tokens=200,
            output_tokens=100,
            cached_tokens=50,
            cost_usd=0.01,
            execution_count=2,
        ),
    )
    mock_driver.upsert.assert_called()


@pytest.mark.asyncio
async def test_get_detailed_usage_calculation(repo: AuditRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive: tests detailed multi-dimensional usage calculations."""
    mock_execs = [
        {
            "id": "exe_1",
            "cost_estimate": 0.05,
            "duration_ms": 1200,
            "workflow_id": "wf_1",
            "models_used": {"gpt-4o": 2},
            "completed_at": "2026-08-15T12:00:00Z",
        },
        {
            "id": "exe_2",
            "cost_estimate": 0.03,
            "duration_ms": 800,
            "workflow_id": "wf_1",
            "models_used": {"claude-3-5-sonnet": 1},
            "completed_at": "2026-08-16T12:00:00Z",
        },
    ]
    mock_agg = UsageAggregateDTO(
        organization_id="org_123",
        period="2026-08",
        total_input_tokens=1000,
        total_output_tokens=400,
        total_cached_tokens=300,
        total_cost_usd=0.08,
        execution_count=2,
    ).model_dump(mode="json")

    mock_driver.query.return_value = mock_execs
    mock_driver.get.return_value = mock_agg

    usage = await repo.get_detailed_usage(
        scope="org",
        target_id="org_123",
        since="2026-08-01T00:00:00Z",
    )
    assert usage.total_cost_usd == pytest.approx(0.08)
    assert usage.total_tokens == 1400
    assert usage.by_model == {"gpt-4o": 2, "claude-3-5-sonnet": 1}
    assert usage.by_workflow == {"wf_1": 2}
