"""Unit tests for UsageService covering FinOps tracking, quota enforcement, and SQL rollup reporting."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import Organization, SubscriptionStatus, SystemOrganizations
from backend_v2.models.domain.usage import PricingConfig
from backend_v2.services.usage_service import UsageService
from backend_v2.tests.factories.model_factories import UsageRecordFactory
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


@pytest.fixture
def fake_repo() -> InMemoryUnifiedWorkflowRepository:
    """Provide an isolated in-memory unified workflow repository."""
    return InMemoryUnifiedWorkflowRepository()


@pytest.fixture
def usage_service(fake_repo: InMemoryUnifiedWorkflowRepository) -> UsageService:
    """Provide a UsageService bound to the in-memory repository fake."""
    return UsageService(audit_repo=fake_repo, identity_repo=fake_repo)


async def _seed_monthly_org_spend(
    fake_repo: InMemoryUnifiedWorkflowRepository,
    org_id: str,
    spend_usd: float,
) -> None:
    """Replace current-month organization usage records with a deterministic USD spend total."""
    fake_repo._audit._usage_records.clear()
    if spend_usd > 0.0:
        await fake_repo.log_usage(
            UsageRecordFactory.build(
                org_id=org_id,
                user_id="usr_0195f3a0000070018234abcd5678ef90",
                model="gemini-2.5-flash",
                input_tokens=100,
                output_tokens=50,
                cost_usd=spend_usd,
                timestamp=datetime.now(UTC),
            )
        )


@pytest.mark.asyncio
async def test_track_usage(usage_service: UsageService, fake_repo: InMemoryUnifiedWorkflowRepository) -> None:
    """Verify track_usage persists an append-only UsageRecord without shadow counter tables."""
    record = await usage_service.track_usage(
        org_id="org_0195f3a0000070018234abcd5678ef90",
        user_id="usr_0195f3a0000070018234abcd5678ef90",
        model="gemini-2.5-flash",
        input_tokens=10,
        output_tokens=20,
        cost_usd=0.01,
    )

    assert record.id.startswith("usg_")
    assert record.input_tokens == 10
    assert record.output_tokens == 20
    assert record.cost_usd == 0.01
    assert fake_repo.get_call_count("log_usage") > 0
    stored = await fake_repo.get_usage_records("organization", "org_0195f3a0000070018234abcd5678ef90")
    assert len(stored) == 1


@pytest.mark.asyncio
async def test_track_usage_prompt_caching_drift_alert(
    usage_service: UsageService,
    fake_repo: InMemoryUnifiedWorkflowRepository,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify rolling 5-call prompt caching drift check logs an error when hit rate drops below 70%."""
    user_id = "usr_0195f3a0000070018234abcd5678ef90"
    org_id = "org_0195f3a0000070018234abcd5678ef90"
    for idx in range(4):
        await fake_repo.log_usage(
            UsageRecordFactory.build(
                id=f"usg_0195f3a000007001800000000000000{idx}",
                org_id=org_id,
                user_id=user_id,
                model="gemini-2.5-flash",
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
            model="gemini-2.5-flash",
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
                org_id="org_0195f3a0000070018234abcd5678ef90",
                user_id="usr_0195f3a0000070018234abcd5678ef90",
                model="gemini-2.5-flash",
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
    """Verify check_quota returns True when monthly rollup usage is below organization quota_limit."""
    org_id = "org_0195f3a0000070018234abcd5678ef90"
    org = Organization(
        id=org_id,
        name="Test Org",
        is_active=True,
        tier="basic",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=10.0,
        tpm_limit=1000,
        rpm_limit=10,
        allowed_email_domains=[],
    )
    await fake_repo.create_organization(org)
    await _seed_monthly_org_spend(fake_repo, org_id, 5.0)

    res = await usage_service.check_quota(org_id)
    assert res is True
    assert fake_repo.get_call_count("get_organization") > 0
    assert fake_repo.get_call_count("aggregate_organization_usage") > 0


@pytest.mark.asyncio
async def test_check_quota_exceed(
    usage_service: UsageService,
    fake_repo: InMemoryUnifiedWorkflowRepository,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify check_quota logs QUOTA_EXCEEDED and raises AppException when monthly rollup exceeds quota_limit."""
    org_id = "org_0195f3a0000070018234abcd5678ef90"
    org = Organization(
        id=org_id,
        name="Test Org",
        is_active=True,
        tier="basic",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=10.0,
        tpm_limit=1000,
        rpm_limit=10,
        allowed_email_domains=[],
    )
    await fake_repo.create_organization(org)
    await _seed_monthly_org_spend(fake_repo, org_id, 15.0)

    with caplog.at_level(logging.ERROR), pytest.raises(AppException) as exc_info:
        await usage_service.check_quota(org_id)

    assert exc_info.value.status_code == 402
    assert exc_info.value.details == {"error_code": ErrorCodes.QUOTA_EXCEEDED.value}
    assert ErrorCodes.QUOTA_EXCEEDED.name in caplog.text


@pytest.mark.asyncio
async def test_usage_service_check_quota_bva_and_subscription_boundary(
    usage_service: UsageService,
    fake_repo: InMemoryUnifiedWorkflowRepository,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Contract: Monthly spend at quota_limit - 0.01 passes; >= quota_limit or inactive subscription raises QUOTA_EXCEEDED."""
    org_id = "org_0195f3a0000070018234abcd5678ef90"
    quota_limit = 100.0

    for active_status in (SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL):
        org = Organization(
            id=org_id,
            name="BVA Org",
            is_active=True,
            tier="enterprise",
            subscription_status=active_status,
            quota_limit=quota_limit,
            tpm_limit=10000,
            rpm_limit=60,
            allowed_email_domains=[],
        )
        await fake_repo.create_organization(org)
        await _seed_monthly_org_spend(fake_repo, org_id, quota_limit - 0.01)

        assert await usage_service.check_quota(org_id) is True

    for exhausted_spend in (quota_limit, quota_limit + 0.01):
        await _seed_monthly_org_spend(fake_repo, org_id, exhausted_spend)
        caplog.clear()
        with caplog.at_level(logging.ERROR), pytest.raises(AppException) as budget_exc:
            await usage_service.check_quota(org_id)
        assert budget_exc.value.status_code == 402
        assert budget_exc.value.details == {"error_code": ErrorCodes.QUOTA_EXCEEDED.value}
        assert ErrorCodes.QUOTA_EXCEEDED.name in caplog.text

    await _seed_monthly_org_spend(fake_repo, org_id, 0.0)
    for inactive_status in (
        SubscriptionStatus.PAST_DUE,
        SubscriptionStatus.CANCELED,
    ):
        inactive_org = Organization(
            id=org_id,
            name="Inactive Sub Org",
            is_active=True,
            tier="enterprise",
            subscription_status=inactive_status,
            quota_limit=quota_limit,
            tpm_limit=10000,
            rpm_limit=60,
            allowed_email_domains=[],
        )
        await fake_repo.create_organization(inactive_org)
        caplog.clear()
        with caplog.at_level(logging.ERROR), pytest.raises(AppException) as sub_exc:
            await usage_service.check_quota(org_id)
        assert sub_exc.value.status_code == 402
        assert sub_exc.value.details == {"error_code": ErrorCodes.QUOTA_EXCEEDED.value}
        assert ErrorCodes.QUOTA_EXCEEDED.name in caplog.text

    disabled_org = Organization(
        id=org_id,
        name="Disabled Org",
        is_active=False,
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=quota_limit,
        tpm_limit=10000,
        rpm_limit=60,
        allowed_email_domains=[],
    )
    await fake_repo.create_organization(disabled_org)
    with pytest.raises(AppException) as disabled_exc:
        await usage_service.check_quota(org_id)
    assert disabled_exc.value.status_code == 402
    assert disabled_exc.value.details == {"error_code": ErrorCodes.QUOTA_EXCEEDED.value}


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
        await usage_service.check_quota("org_0195f3a0000070018000000000000099")

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
            await usage_service.check_quota("org_0195f3a0000070018234abcd5678ef90")

    assert excinfo.value.status_code == 500
    assert excinfo.value.details == {"error_code": ErrorCodes.QUOTA_CHECK_FAILED.value}


@pytest.mark.asyncio
async def test_get_usage_report_with_sql_rollup(
    usage_service: UsageService, fake_repo: InMemoryUnifiedWorkflowRepository
) -> None:
    """Verify get_usage_report computes organization totals via aggregate_organization_usage and percentage_used."""
    org_id = "org_0195f3a0000070018234abcd5678ef90"
    org = Organization(
        id=org_id,
        name="Test Org",
        is_active=True,
        tier="basic",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=10.0,
        tpm_limit=1000,
        rpm_limit=10,
        allowed_email_domains=[],
    )
    await fake_repo.create_organization(org)
    await fake_repo.log_usage(
        UsageRecordFactory.build(
            org_id=org_id,
            user_id="usr_0195f3a0000070018234abcd5678ef90",
            model="gemini-2.5-pro",
            input_tokens=100,
            output_tokens=200,
            cached_tokens=0,
            cost_usd=0.5,
            timestamp=datetime.now(UTC),
        )
    )

    report = await usage_service.get_usage_report(scope="org", entity_id=org_id)

    assert report.usage.total_tokens == 300
    assert report.percentage_used == pytest.approx(5.0)
    assert fake_repo.get_call_count("aggregate_organization_usage") > 0


@pytest.mark.asyncio
async def test_get_usage_report_from_records_with_since(
    usage_service: UsageService,
    fake_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify get_usage_report computes usage for custom since timestamp and user scope."""
    now = datetime.now(UTC)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    org_id = "org_0195f3a0000070018234abcd5678ef90"
    user_id = "usr_0195f3a0000070018234abcd5678ef90"

    await fake_repo.create_organization(
        Organization(
            id=org_id,
            name="Scoped Org",
            is_active=True,
            tier="basic",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=10.0,
            tpm_limit=1000,
            rpm_limit=10,
            allowed_email_domains=[],
        )
    )

    await fake_repo.log_usage(
        UsageRecordFactory.build(
            id="usg_0195f3a0000070018111222233334444",
            org_id=org_id,
            user_id=user_id,
            model="gemini-2.5-flash",
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

    user_report = await usage_service.get_usage_report(scope="user", entity_id=user_id, since=start_of_month)
    assert user_report.usage.total_tokens == 100


@pytest.mark.asyncio
async def test_usage_service_get_usage_report_unknown_org_raises_resource_not_found(
    usage_service: UsageService,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify get_usage_report for a nonexistent organization logs error and raises 404 RESOURCE_NOT_FOUND."""
    missing_org_id = "org_0195f3a0000070018999999999999999"
    with caplog.at_level(logging.ERROR), pytest.raises(AppException) as excinfo:
        await usage_service.get_usage_report(scope="org", entity_id=missing_org_id)

    assert excinfo.value.status_code == 404
    assert excinfo.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value
    assert ErrorCodes.RESOURCE_NOT_FOUND.value in caplog.text


@pytest.mark.asyncio
async def test_get_usage_report_failure_raises_app_exception(
    usage_service: UsageService,
    fake_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify repository error during get_usage_report raises 500 AppException with USAGE_TRACKING_FAILED."""
    org_id = "org_0195f3a0000070018234abcd5678ef90"
    await fake_repo.create_organization(
        Organization(
            id=org_id,
            name="Fault Org",
            is_active=True,
            tier="basic",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=10.0,
            tpm_limit=1000,
            rpm_limit=10,
            allowed_email_domains=[],
        )
    )
    async with fake_repo._audit.fault_context("aggregate_organization_usage", RuntimeError("read error")):
        with pytest.raises(AppException) as excinfo:
            await usage_service.get_usage_report(scope="org", entity_id=org_id)

    assert excinfo.value.status_code == 500
    assert excinfo.value.details == {"error_code": ErrorCodes.USAGE_TRACKING_FAILED.value}


@pytest.mark.asyncio
async def test_get_usage_report_app_exception_passthrough(
    usage_service: UsageService,
    fake_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify explicit AppException raised during get_usage_report is re-raised without double-wrapping."""
    org_id = "org_0195f3a0000070018234abcd5678ef90"
    await fake_repo.create_organization(
        Organization(
            id=org_id,
            name="Domain Error Org",
            is_active=True,
            tier="basic",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=10.0,
            tpm_limit=1000,
            rpm_limit=10,
            allowed_email_domains=[],
        )
    )
    domain_err = AppException(
        message="Invalid rollup state",
        status_code=422,
        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
    )
    async with fake_repo._audit.fault_context("aggregate_organization_usage", domain_err):
        with pytest.raises(AppException) as excinfo:
            await usage_service.get_usage_report(scope="org", entity_id=org_id)

    assert excinfo.value.status_code == 422
    assert excinfo.value.details == {"error_code": ErrorCodes.VALIDATION_FAILED.value}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("input_tokens", "cost_usd"),
    [
        (-1, 0.01),
        (10, -0.01),
    ],
)
async def test_track_usage_negative_boundary_values_raise_app_exception(
    usage_service: UsageService,
    input_tokens: int,
    cost_usd: float,
) -> None:
    """Verify negative boundary values for tokens or cost_usd fail fast via AppException."""
    with pytest.raises(AppException) as excinfo:
        await usage_service.track_usage(
            org_id="org_0195f3a0000070018234abcd5678ef90",
            user_id="usr_0195f3a0000070018234abcd5678ef90",
            model="gemini-2.5-flash",
            input_tokens=input_tokens,
            output_tokens=20,
            cost_usd=cost_usd,
        )

    assert excinfo.value.status_code == 500
    assert excinfo.value.details == {"error_code": ErrorCodes.USAGE_TRACKING_FAILED.value}
