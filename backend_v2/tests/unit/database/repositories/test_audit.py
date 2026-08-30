"""Unit tests for AuditRepositoryImpl."""

from unittest.mock import AsyncMock

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.audit import AuditRepositoryImpl
from backend_v2.models.domain.base import UsageRecord


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
    valid_audit = {
        "timestamp": "2026-08-30T12:00:00Z",
        "level": "INFO",
        "message": "Workflow started",
        "context": {"org_id": "org_123"},
    }
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

    await repo.log_audit_event({"message": "Audit event"})
    mock_driver.upsert.assert_called()


@pytest.mark.asyncio
async def test_log_usage_model_and_dict(repo: AuditRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive: tests log_usage with both dict and UsageRecord model instance."""
    dict_usage = {
        "id": "usg_1",
        "org_id": "org_123",
        "user_id": "usr_123",
        "model": "gpt-4o",
        "input_tokens": 10,
        "output_tokens": 5,
        "cost_usd": 0.001,
        "timestamp": "2026-08-30T12:00:00Z",
    }
    await repo.log_usage(dict_usage)

    model_usage = UsageRecord.model_validate(dict_usage, strict=False)
    await repo.log_usage(model_usage)
    assert mock_driver.upsert.call_count >= 2


@pytest.mark.asyncio
async def test_get_usage_records_scopes_and_corruption(repo: AuditRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive: tests get_usage_records across scopes and handles corruption gracefully."""
    valid_usage = {
        "id": "usg_1",
        "org_id": "org_123",
        "user_id": "usr_123",
        "model": "gpt-4o",
        "input_tokens": 100,
        "output_tokens": 50,
        "cost_usd": 0.005,
        "timestamp": "2026-08-30T12:00:00Z",
    }
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
    update_data = {
        "total_executions": 5,
        "prompt_tokens": 500,
        "completion_tokens": 200,
        "total_tokens": 700,
        "cached_tokens": 100,
        "reasoning_tokens": 50,
        "cost_usd": 0.02,
    }
    await repo.upsert_usage_aggregate("organization", "org_123", "2026-08", update_data)
    mock_driver.upsert.assert_called()

    # 2. Existing aggregate merge
    existing_agg = {
        "id": "organization_org_123_2026-08",
        "total_executions": 5,
        "usage": {
            "prompt_tokens": 500,
            "completion_tokens": 200,
            "total_tokens": 700,
            "cached_tokens": 100,
            "reasoning_tokens": 50,
            "cost_usd": 0.02,
        },
    }
    mock_driver.get.return_value = existing_agg
    await repo.upsert_usage_aggregate(
        "organization",
        "org_123",
        "2026-08",
        {
            "total_executions": 2,
            "usage": {
                "prompt_tokens": 200,
                "completion_tokens": 100,
                "total_tokens": 300,
                "cached_tokens": 50,
                "reasoning_tokens": 25,
                "cost_usd": 0.01,
            },
        },
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
        },
        {
            "id": "exe_2",
            "cost_estimate": 0.03,
            "duration_ms": 800,
            "workflow_id": "wf_1",
            "models_used": {"claude-3-5-sonnet": 1},
        },
    ]
    mock_workflows = [{"id": "wf_1", "name": "Strategic Audit"}]
    mock_agg = {
        "usage": {
            "prompt_tokens": 1000,
            "completion_tokens": 400,
            "total_tokens": 1400,
            "cached_tokens": 300,
            "reasoning_tokens": 100,
        }
    }

    mock_driver.query.side_effect = [mock_execs, mock_workflows]
    mock_driver.get.return_value = mock_agg

    usage = await repo.get_detailed_usage(
        scope="org",
        target_id="org_123",
        since="2026-08-01T00:00:00Z",
    )
    assert usage["total_cost_usd"] == pytest.approx(0.08)
    assert usage["total_runs"] == 2
    assert usage["total_processing_time_ms"] == 2000
    assert usage["models_used"] == {"gpt-4o": 2, "claude-3-5-sonnet": 1}
    assert usage["workflows_used"] == {"Strategic Audit": 2}
    assert usage["prompt_tokens"] == 1000
    assert usage["completion_tokens"] == 400
    assert usage["total_tokens"] == 1400
