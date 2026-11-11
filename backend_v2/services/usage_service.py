"""Usage Service for tracking LLM token consumption, quota limits, and SQL FinOps rollups.

Persists immutable UsageRecord entries to the append-only usage_records ledger and
computes FinOps totals exclusively via SQL SUM/COUNT rollups with zero shadow counter tables.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from backend_v2.database.interfaces import IAuditRepository, IIdentityRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import SubscriptionStatus, SystemOrganizations
from backend_v2.models.core_base import generate_uuid7
from backend_v2.models.domain import UsageRecord
from backend_v2.models.domain.usage import PricingConfig, TokenUsage, UsageReport

logger = logging.getLogger(__name__)

__all__ = ["UsageService"]


class UsageService:
    """Service for tracking LLM usage, enforcing monthly USD quotas, and compiling FinOps reports.

    Attributes:
        identity_repo: Repository for organization and user identity lookups.
        audit_repo: Repository for append-only usage persistence and SQL rollups.
    """

    def __init__(self, identity_repo: IIdentityRepository, audit_repo: IAuditRepository) -> None:
        """Initialize the UsageService.

        Args:
            identity_repo: Repository for identity lookups.
            audit_repo: Repository for usage and audit persistence.
        """
        self.identity_repo = identity_repo
        self.audit_repo = audit_repo

    @staticmethod
    def _parse_since_timestamp(since: str | None) -> datetime | None:
        """Parse an optional ISO 8601 timestamp string into a UTC-aware datetime.

        Args:
            since: Optional ISO 8601 timestamp string.

        Returns:
            Parsed UTC-aware datetime instance, or None when omitted.

        Raises:
            ValueError: If the string is not a valid ISO 8601 timestamp.
        """
        if not since:
            return None
        parsed = datetime.fromisoformat(since.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed

    async def _evaluate_prompt_caching_drift(
        self,
        user_id: str,
        record: UsageRecord,
        model_pricing_config: PricingConfig | None,
    ) -> None:
        """Evaluate rolling prompt caching hit rate and log drift alerts if degraded.

        Args:
            user_id: User identifier for rolling window history lookup.
            record: Newly persisted usage record for the current call.
            model_pricing_config: Optional model pricing configuration indicating cache support.
        """
        has_prompt_caching = (
            model_pricing_config is not None and model_pricing_config.cached_input_token_price is not None
        )
        if not has_prompt_caching:
            return

        recent_records_data = await self.audit_repo.get_usage_records(scope="user", entity_id=user_id)
        # Inspect rolling window of up to 5 records including the current record
        records = list(recent_records_data[-4:])
        if not recent_records_data or recent_records_data[-1].id != record.id:
            records.append(record)
        else:
            records = list(recent_records_data[-5:])

        if len(records) >= 5:
            total_tokens = sum(r.input_tokens for r in records)
            total_cached = sum(r.cached_tokens for r in records)

            if total_tokens > 0:
                hit_rate = total_cached / total_tokens
                hit_rate_pct = round(hit_rate * 100, 2)

                if hit_rate < 0.70:
                    logger.error(
                        "PROMPT_CACHING_DRIFT_ALERT: Cache hit rate has degraded "
                        f"to {hit_rate_pct}% for workflow Y. Investigate prompt mutations immediately."
                    )

    async def track_usage(
        self,
        org_id: str,
        user_id: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: int = 0,
        cached_tokens: int = 0,
        cache_creation_input_tokens: int = 0,
        reasoning_tokens: int = 0,
        finish_reason: str | None = None,
        system_fingerprint: str | None = None,
        cost_usd: float = 0.0,
        estimated_savings_usd: float = 0.0,
        model_pricing_config: PricingConfig | None = None,
        execution_id: str | None = None,
    ) -> UsageRecord:
        """Track and persist immutable LLM usage to the append-only usage_records ledger.

        Args:
            org_id: Organization identifier.
            user_id: User identifier.
            model: Model identifier string.
            input_tokens: Number of prompt input tokens consumed.
            output_tokens: Number of completion output tokens generated.
            latency_ms: Request execution latency in milliseconds.
            cached_tokens: Number of prompt tokens read from cache.
            cache_creation_input_tokens: Number of prompt tokens written to cache.
            reasoning_tokens: Number of internal reasoning tokens generated.
            finish_reason: Optional provider finish reason.
            system_fingerprint: Optional provider system fingerprint.
            cost_usd: Monetary cost in USD calculated by LiteLLM.
            estimated_savings_usd: Estimated monetary savings in USD from caching.
            model_pricing_config: Optional model pricing configuration for cache drift monitoring.
            execution_id: Optional associated execution identifier.

        Returns:
            Persisted UsageRecord domain model instance.

        Raises:
            AppException: If persisting usage fails (ErrorCodes.USAGE_TRACKING_FAILED).
        """
        try:
            record = UsageRecord(
                id=f"usg_{generate_uuid7().hex}",
                org_id=org_id,
                user_id=user_id,
                execution_id=execution_id,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cached_tokens=cached_tokens,
                cache_creation_input_tokens=cache_creation_input_tokens,
                reasoning_tokens=reasoning_tokens,
                latency_ms=latency_ms,
                finish_reason=finish_reason,
                system_fingerprint=system_fingerprint,
                cost_usd=cost_usd,
                estimated_savings_usd=estimated_savings_usd,
                timestamp=datetime.now(UTC),
            )

            await self.audit_repo.log_usage(record)
            await self._evaluate_prompt_caching_drift(
                user_id=user_id,
                record=record,
                model_pricing_config=model_pricing_config,
            )

            return record

        except Exception as e:
            logger.error(
                "[Usage] %s for %s (Org: %s): %s",
                ErrorCodes.USAGE_TRACKING_FAILED.value,
                user_id,
                org_id,
                e,
                exc_info=True,
            )
            raise AppException(
                message=f"Failed to track usage: {e}",
                status_code=500,
                details={"error_code": ErrorCodes.USAGE_TRACKING_FAILED.value},
            ) from e

    async def check_quota(self, org_id: str) -> bool:
        """Check whether the organization has an active subscription and is within monthly USD quota limits.

        Args:
            org_id: Organization identifier to evaluate.

        Returns:
            True if the organization subscription is active and monthly usage is below quota_limit.

        Raises:
            AppException: If org_id is empty (ErrorCodes.VALIDATION_FAILED), organization does not
                exist (ErrorCodes.RESOURCE_NOT_FOUND), subscription is inactive or monthly USD budget
                is exhausted (ErrorCodes.QUOTA_EXCEEDED), or evaluation fails (ErrorCodes.QUOTA_CHECK_FAILED).
        """
        try:
            if not org_id:
                msg = "Quota Check: Missing Organization ID (Orphan User). Execution denied."
                logger.error("[UsageService] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise AppException(
                    message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                )

            if org_id == SystemOrganizations.ROOT_SYSTEM:
                return True

            org = await self.identity_repo.get_organization(org_id)
            if org is None:
                msg = f"Quota Check: Organization '{org_id}' not found. Execution denied."
                logger.error("[UsageService] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg, exc_info=True)
                raise AppException(
                    message=msg, status_code=404, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value}
                )

            if not org.is_active or org.subscription_status not in (
                SubscriptionStatus.ACTIVE,
                SubscriptionStatus.TRIAL,
            ):
                msg = (
                    f"Quota Check: Organization '{org_id}' subscription is not active "
                    f"(status={org.subscription_status}). Execution denied."
                )
                logger.error(
                    "[UsageService] %s: %s",
                    ErrorCodes.QUOTA_EXCEEDED.name,
                    msg,
                    extra={"error_code": ErrorCodes.QUOTA_EXCEEDED.value},
                    exc_info=True,
                )
                raise AppException(
                    message=msg,
                    status_code=402,
                    details={"error_code": ErrorCodes.QUOTA_EXCEEDED.value},
                )

            limit = float(org.quota_limit)
            start_of_month_dt = datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            rollup = await self.audit_repo.aggregate_organization_usage(
                organization_id=org_id,
                since=start_of_month_dt,
            )
            used = float(rollup.total_cost_usd)

            if used >= limit:
                msg = f"Quota Exceeded for {org_id}: Used ${used} >= Limit ${limit}"
                logger.error(
                    "[UsageService] %s: %s",
                    ErrorCodes.QUOTA_EXCEEDED.name,
                    msg,
                    extra={"error_code": ErrorCodes.QUOTA_EXCEEDED.value},
                    exc_info=True,
                )
                raise AppException(
                    message=msg,
                    status_code=402,
                    details={"error_code": ErrorCodes.QUOTA_EXCEEDED.value},
                )

            return True

        except AppException:
            raise
        except Exception as e:
            logger.error(
                "[Usage] %s check failed for %s: %s", ErrorCodes.QUOTA_CHECK_FAILED.value, org_id, e, exc_info=True
            )
            raise AppException(
                message=f"Quota check failed: {e}",
                status_code=500,
                details={"error_code": ErrorCodes.QUOTA_CHECK_FAILED.value},
            ) from e

    def _compute_token_usage_from_records(self, records: list[UsageRecord]) -> TokenUsage:
        """Compute aggregated TokenUsage statistics from raw UsageRecord rows.

        Args:
            records: Sequence of UsageRecord domain models to sum.

        Returns:
            Aggregated TokenUsage domain model.
        """
        prompt_tokens = sum(r.input_tokens for r in records)
        completion_tokens = sum(r.output_tokens for r in records)
        total_tokens = sum((r.input_tokens + r.output_tokens) for r in records)
        cached_tokens = sum(r.cached_tokens for r in records)
        reasoning_tokens = sum(r.reasoning_tokens for r in records)
        cache_creation_tokens = sum(r.cache_creation_input_tokens for r in records)
        cost_usd = sum(float(r.cost_usd) for r in records)
        estimated_savings = sum(float(r.estimated_savings_usd) for r in records)

        return TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cached_tokens=cached_tokens,
            reasoning_tokens=reasoning_tokens,
            cache_creation_input_tokens=cache_creation_tokens,
            cost_usd=cost_usd,
            estimated_savings_usd=estimated_savings,
        )

    async def get_usage_report(self, scope: str, entity_id: str | None = None, since: str | None = None) -> UsageReport:
        """Retrieve a consolidated FinOps usage report computed via SQL rollups.

        Args:
            scope: Reporting scope identifier ('org', 'organization', 'user', or 'system').
            entity_id: Optional target entity ID.
            since: Optional start date in ISO-8601 format.

        Returns:
            Computed UsageReport containing token and cost aggregations.

        Raises:
            AppException: With RESOURCE_NOT_FOUND (HTTP 404) when the target organization does not exist,
                or USAGE_TRACKING_FAILED (HTTP 500) on retrieval failure.
        """
        try:
            mapped_scope = "organization" if scope == "org" else scope
            since_dt = self._parse_since_timestamp(since)

            quota_limit: float | None = None
            percentage_used: float | None = None

            if mapped_scope == "organization":
                if entity_id:
                    org = await self.identity_repo.get_organization(entity_id)
                    if org is None:
                        msg = f"Usage Report: Organization '{entity_id}' not found."
                        logger.error(
                            "[UsageService] %s: %s",
                            ErrorCodes.RESOURCE_NOT_FOUND.name,
                            msg,
                            extra={
                                "error_code": ErrorCodes.RESOURCE_NOT_FOUND.value,
                                "organization_id": entity_id,
                            },
                        )
                        raise AppException(
                            message=msg,
                            status_code=404,
                            details={
                                "error_code": ErrorCodes.RESOURCE_NOT_FOUND.value,
                                "organization_id": entity_id,
                            },
                        )
                    quota_limit = float(org.quota_limit)

                rollup = await self.audit_repo.aggregate_organization_usage(
                    organization_id=entity_id,
                    since=since_dt,
                )
                token_usage = TokenUsage(
                    prompt_tokens=rollup.total_prompt_tokens,
                    completion_tokens=rollup.total_completion_tokens,
                    total_tokens=rollup.total_prompt_tokens + rollup.total_completion_tokens,
                    cached_tokens=rollup.total_cached_tokens,
                    reasoning_tokens=rollup.total_reasoning_tokens,
                    cache_creation_input_tokens=rollup.total_cache_creation_input_tokens,
                    cost_usd=rollup.total_cost_usd,
                    estimated_savings_usd=rollup.total_estimated_savings_usd,
                )
                if quota_limit is not None and quota_limit > 0:
                    percentage_used = min(100.0, (token_usage.cost_usd / quota_limit) * 100.0)
            elif mapped_scope == "system":
                rollup = await self.audit_repo.aggregate_organization_usage(
                    organization_id=None,
                    since=since_dt,
                )
                token_usage = TokenUsage(
                    prompt_tokens=rollup.total_prompt_tokens,
                    completion_tokens=rollup.total_completion_tokens,
                    total_tokens=rollup.total_prompt_tokens + rollup.total_completion_tokens,
                    cached_tokens=rollup.total_cached_tokens,
                    reasoning_tokens=rollup.total_reasoning_tokens,
                    cache_creation_input_tokens=rollup.total_cache_creation_input_tokens,
                    cost_usd=rollup.total_cost_usd,
                    estimated_savings_usd=rollup.total_estimated_savings_usd,
                )
            else:
                records = await self.audit_repo.get_usage_records(
                    scope=mapped_scope,
                    entity_id=entity_id,
                    since=since,
                )
                token_usage = self._compute_token_usage_from_records(records)

            return UsageReport(
                scope=scope,
                entity_id=entity_id,
                period="Custom" if since else "All-time",
                usage=token_usage,
                quota_limit_usd=quota_limit,
                percentage_used=percentage_used,
            )
        except AppException:
            raise
        except Exception as e:
            logger.error(
                "[Usage] %s report retrieval failed for scope=%s (entity=%s): %s",
                ErrorCodes.USAGE_TRACKING_FAILED.value,
                scope,
                entity_id,
                e,
                exc_info=True,
            )
            raise AppException(
                message=f"Failed to retrieve usage report: {e}",
                status_code=500,
                details={"error_code": ErrorCodes.USAGE_TRACKING_FAILED.value},
            ) from e
