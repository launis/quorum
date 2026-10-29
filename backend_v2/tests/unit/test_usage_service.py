"""Unit tests for UsageService covering FinOps tracking, quota enforcement, and usage reporting."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import Organization, SubscriptionStatus, SystemOrganizations
from backend_v2.models.domain.base import UsageAggregateDTO, UsageRecord
from backend_v2.models.domain.usage import PricingConfig
from backend_v2.services.usage_service import UsageService
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


@pytest.fixture
def fake_repo() -> InMemoryUnifiedWorkflowRepository:
    """Provide an isolated in-memory unified workflow repository."""
    return InMemoryUnifiedWorkflowRepository()


@pytest.fixture
def usage_service(fake_repo: InMemoryUnifiedWorkflowRepository) -> UsageService:
    """Provide a UsageService bound to the in-memory repository fake."""
    return UsageService(audit_repo=fake_repo, identity_repo=fake_repo)


@pytest.mark.asyncio
async def test_track_usage(usage_service: UsageService, fake_repo: InMemoryUnifiedWorkflowRepository) -> None:
    """Verify track_usage persists a UsageRecord and updates all 6 cumulative aggregates."""
    record = await usage_service.track_usage(
        org_id="org_1234abcd5678ef90",
        user_id="usr_1234abcd5678ef90",
        model="test-model",
        input_tokens=10,
        output_tokens=20,
        cost_usd=0.01,
    )

    assert record.id.startswith("usg_")
    assert record.input_tokens == 10
    assert record.output_tokens == 20
    assert record.cost_usd == 0.01
    assert fake_repo.get_call_count("log_usage") > 0
    assert fake_repo.get_call_count("upsert_usage_aggregate") == 6


@pytest.mark.asyncio
async def test_track_usage_prompt_caching_drift_alert(
    usage_service: UsageService,
    fake_repo: InMemoryUnifiedWorkflowRepository,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify rolling 5-call prompt caching drift check logs an error when hit rate drops below 70%."""
    user_id = "usr_1234abcd5678ef90"
    org_id = "org_1234abcd5678ef90"
    for idx in range(4):
        await fake_repo.log_usage(
            UsageRecord(
                id=f"usg_000000000000000{idx}",
                org_id=org_id,
                user_id=user_id,
                model="test-model",
                input_tokens=100,
                output_tokens=20,
                cached_tokens=10,
                cost_usd=0.01,
                timestamp=datetime.now(UTC),
            )
        )

    pricing_cfg = PricingConfig(
        input_token_price=0.001,
        output_token_price=0.002,
        cached_input_token_price=0.0002,
    )

    with caplog.at_level(logging.ERROR):
        await usage_service.track_usage(
            org_id=org_id,
            user_id=user_id,
            model="test-model",
            input_tokens=100,
            output_tokens=20,
            cached_tokens=10,
            cost_usd=0.01,
            model_pricing_config=pricing_cfg,
        )

    assert "PROMPT_CACHING_DRIFT_ALERT: Cache hit rate has degraded to 10.0%" in caplog.text


@pytest.mark.asyncio
async def test_track_usage_failure_raises_app_exception(
    usage_service: UsageService,
    fake_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify repository failure during track_usage raises AppException with USAGE_TRACKING_FAILED."""
    async with fake_repo._audit.fault_context("log_usage", RuntimeError("storage write failure")):
        with pytest.raises(AppException) as exc_info:
            await usage_service.track_usage(
                org_id="org_1234abcd5678ef90",
                user_id="usr_1234abcd5678ef90",
                model="test-model",
                input_tokens=10,
                output_tokens=20,
                cost_usd=0.01,
            )

    assert exc_info.value.status_code == 500
    assert exc_info.value.details == {"error_code": ErrorCodes.USAGE_TRACKING_FAILED.value}


@pytest.mark.asyncio
async def test_check_quota_system_root(
    usage_service: UsageService, fake_repo: InMemoryUnifiedWorkflowRepository
) -> None:
    """Verify ROOT_SYSTEM organization bypasses quota limits."""
    res = await usage_service.check_quota(SystemOrganizations.ROOT_SYSTEM)
    assert res is True
    assert fake_repo.get_call_count("get_organization") == 0


@pytest.mark.asyncio
async def test_check_quota_pass(usage_service: UsageService, fake_repo: InMemoryUnifiedWorkflowRepository) -> None:
    """Verify check_quota returns True when monthly usage is below organization quota_limit."""
    org = Organization(
        id="org_1234abcd5678ef90",
        name="Test Org",
        is_active=True,
        tier="basic",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=10.0,
        tpm_limit=1000,
        rpm_limit=10,
    )
    await fake_repo.create_organization(org)
    fake_repo.set_org_usage_total("org_1234abcd5678ef90", 5.0)

    res = await usage_service.check_quota("org_1234abcd5678ef90")
    assert res is True
    assert fake_repo.get_call_count("get_organization") > 0


@pytest.mark.asyncio
async def test_check_quota_exceed(usage_service: UsageService, fake_repo: InMemoryUnifiedWorkflowRepository) -> None:
    """Verify check_quota returns False when monthly usage equals or exceeds organization quota_limit."""
    org = Organization(
        id="org_1234abcd5678ef90",
        name="Test Org",
        is_active=True,
        tier="basic",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=10.0,
        tpm_limit=1000,
        rpm_limit=10,
    )
    await fake_repo.create_organization(org)
    fake_repo.set_org_usage_total("org_1234abcd5678ef90", 15.0)

    res = await usage_service.check_quota("org_1234abcd5678ef90")
    assert res is False


@pytest.mark.asyncio
async def test_check_quota_missing_org_id(usage_service: UsageService) -> None:
    """Verify empty org_id raises 400 AppException with VALIDATION_FAILED."""
    with pytest.raises(AppException) as excinfo:
        await usage_service.check_quota("")

    assert excinfo.value.status_code == 400
    assert excinfo.value.details == {"error_code": ErrorCodes.VALIDATION_FAILED.value}


@pytest.mark.asyncio
async def test_check_quota_org_not_found(
    usage_service: UsageService, fake_repo: InMemoryUnifiedWorkflowRepository
) -> None:
    """Verify unknown organization raises 404 AppException with RESOURCE_NOT_FOUND."""
    with pytest.raises(AppException) as excinfo:
        await usage_service.check_quota("org_missing00000000")

    assert excinfo.value.status_code == 404
    assert excinfo.value.details == {"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value}


@pytest.mark.asyncio
async def test_check_quota_repository_failure_raises_app_exception(
    usage_service: UsageService,
    fake_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify unexpected repository error during check_quota raises 500 AppException with QUOTA_CHECK_FAILED."""
    async with fake_repo._identities.fault_context("get_organization", RuntimeError("connection timeout")):
        with pytest.raises(AppException) as excinfo:
            await usage_service.check_quota("org_1234abcd5678ef90")

    assert excinfo.value.status_code == 500
    assert excinfo.value.details == {"error_code": ErrorCodes.QUOTA_CHECK_FAILED.value}


@pytest.mark.asyncio
async def test_get_usage_report_with_aggregate(
    usage_service: UsageService, fake_repo: InMemoryUnifiedWorkflowRepository
) -> None:
    """Verify get_usage_report uses pre-aggregated statistics and computes percentage_used."""
    agg = UsageAggregateDTO(
        organization_id="org_1234abcd5678ef90",
        period="all-time",
        total_input_tokens=100,
        total_output_tokens=200,
        total_cached_tokens=0,
        total_cost_usd=0.5,
        execution_count=5,
    )
    fake_repo.set_usage_aggregate("organization", "org_1234abcd5678ef90", "all-time", agg)

    org = Organization(
        id="org_1234abcd5678ef90",
        name="Test Org",
        is_active=True,
        tier="basic",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=10.0,
        tpm_limit=1000,
        rpm_limit=10,
    )
    await fake_repo.create_organization(org)

    report = await usage_service.get_usage_report(scope="org", entity_id="org_1234abcd5678ef90")

    assert report.usage.total_tokens == 300
    assert report.percentage_used == 5.0  # 0.5 / 10.0 * 100
    assert fake_repo.get_call_count("get_usage_aggregate") > 0


@pytest.mark.asyncio
async def test_get_usage_report_from_records_with_since(
    usage_service: UsageService,
    fake_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify get_usage_report computes usage from raw records when no aggregate exists for custom period."""
    now = datetime.now(UTC)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    org_id = "org_1234abcd5678ef90"

    await fake_repo.log_usage(
        UsageRecord(
            id="usg_1111222233334444",
            org_id=org_id,
            user_id="usr_1234abcd5678ef90",
            model="test-model",
            input_tokens=40,
            output_tokens=60,
            cached_tokens=10,
            reasoning_tokens=5,
            cost_usd=0.25,
            timestamp=now,
        )
    )

    report = await usage_service.get_usage_report(scope="org", entity_id=org_id, since=start_of_month)

    assert report.period == "Custom"
    assert report.usage.prompt_tokens == 40
    assert report.usage.completion_tokens == 60
    assert report.usage.total_tokens == 100
    assert report.usage.cached_tokens == 10
    assert report.usage.reasoning_tokens == 5
    assert report.usage.cost_usd == pytest.approx(0.25)


@pytest.mark.asyncio
async def test_get_usage_report_failure_raises_app_exception(
    usage_service: UsageService,
    fake_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify repository error during get_usage_report raises 500 AppException with USAGE_TRACKING_FAILED."""
    async with fake_repo._audit.fault_context("get_usage_aggregate", RuntimeError("read error")):
        with pytest.raises(AppException) as excinfo:
            await usage_service.get_usage_report(scope="org", entity_id="org_1234abcd5678ef90")

    assert excinfo.value.status_code == 500
    assert excinfo.value.details == {"error_code": ErrorCodes.USAGE_TRACKING_FAILED.value}
