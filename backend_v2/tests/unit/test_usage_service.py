from unittest.mock import AsyncMock

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.auth import Organization, SystemOrganizations
from backend_v2.models.domain.base import UsageAggregateDTO
from backend_v2.services.usage_service import UsageService


@pytest.fixture
def mock_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.upsert_usage_aggregate = AsyncMock()
    repo.get_usage_aggregate = AsyncMock()
    repo.get_usage_records = AsyncMock()
    return repo


@pytest.fixture
def usage_service(mock_repo: AsyncMock) -> UsageService:
    return UsageService(audit_repo=mock_repo, identity_repo=mock_repo)


@pytest.mark.asyncio
async def test_track_usage(usage_service: UsageService, mock_repo: AsyncMock) -> None:
    # Setup mock to return cleanly
    mock_repo.log_usage.return_value = None

    record = await usage_service.track_usage(
        org_id="org_1234abcd",
        user_id="usr_1234abcd",
        model="test-model",
        input_tokens=10,
        output_tokens=20,
        cost_usd=0.01,
    )

    assert record.input_tokens == 10
    assert record.output_tokens == 20
    assert record.cost_usd == 0.01
    mock_repo.log_usage.assert_called_once()

    # Verify upsert logic is triggered
    assert mock_repo.upsert_usage_aggregate.call_count == 6


@pytest.mark.asyncio
async def test_check_quota_system_root(usage_service: UsageService, mock_repo: AsyncMock) -> None:
    res = await usage_service.check_quota(SystemOrganizations.ROOT_SYSTEM)
    assert res is True
    mock_repo.get_organization.assert_not_called()


@pytest.mark.asyncio
async def test_check_quota_pass(usage_service: UsageService, mock_repo: AsyncMock) -> None:
    mock_repo.get_organization.return_value = Organization(
        id="org_1234abcd",
        name="Test Org",
        is_active=True,
        tier="basic",
        subscription_status="active",
        quota_limit=10.0,
        tpm_limit=1000,
        rpm_limit=10,
    )
    mock_repo.get_org_usage_total.return_value = 5.0  # Used less than 10.0

    res = await usage_service.check_quota("org_1234abcd")
    assert res is True
    mock_repo.get_organization.assert_called_once_with("org_1234abcd")


@pytest.mark.asyncio
async def test_check_quota_exceed(usage_service: UsageService, mock_repo: AsyncMock) -> None:
    mock_repo.get_organization.return_value = Organization(
        id="org_1234abcd",
        name="Test Org",
        is_active=True,
        tier="basic",
        subscription_status="active",
        quota_limit=10.0,
        tpm_limit=1000,
        rpm_limit=10,
    )
    mock_repo.get_org_usage_total.return_value = 15.0  # Used more than 10.0

    res = await usage_service.check_quota("org_1234abcd")
    assert res is False


@pytest.mark.asyncio
async def test_check_quota_org_not_found(usage_service: UsageService, mock_repo: AsyncMock) -> None:
    mock_repo.get_organization.return_value = None

    with pytest.raises(AppException) as excinfo:
        await usage_service.check_quota("org_missing")

    assert excinfo.value.status_code == 404


@pytest.mark.asyncio
async def test_get_usage_report_with_aggregate(usage_service: UsageService, mock_repo: AsyncMock) -> None:
    mock_repo.get_usage_aggregate.return_value = UsageAggregateDTO(
        organization_id="org_1234abcd",
        period="2026-04",
        total_input_tokens=100,
        total_output_tokens=200,
        total_cached_tokens=0,
        total_cost_usd=0.5,
        execution_count=5,
    )

    mock_repo.get_organization.return_value = Organization(
        id="org_1234abcd",
        name="Test Org",
        is_active=True,
        tier="basic",
        subscription_status="active",
        quota_limit=10.0,
        tpm_limit=1000,
        rpm_limit=10,
    )

    report = await usage_service.get_usage_report(scope="org", entity_id="org_1234abcd")

    assert report.usage.total_tokens == 300
    assert report.percentage_used == 5.0  # 0.5 / 10.0 * 100
    mock_repo.get_usage_aggregate.assert_called_once()
