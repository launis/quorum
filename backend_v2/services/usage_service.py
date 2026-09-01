"""Usage Service for tracking LLM token consumption and costs.

This module persists immutable usage records to the repository, utilizing
the cost calculated by LiteLLM (no local pricing logic).
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from backend_v2.database.interfaces import IAuditRepository, IIdentityRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import SystemOrganizations
from backend_v2.models.domain import UsageRecord
from backend_v2.models.domain.base import UsageAggregateUpdateDTO
from backend_v2.models.domain.usage import PricingConfig, TokenUsage, UsageReport

logger = logging.getLogger(__name__)


class UsageService:
    """Service for tracking and logging LLM usage (LiteLLM-compliant)."""

    def __init__(self, identity_repo: IIdentityRepository, audit_repo: IAuditRepository):
        """Initialize the UsageService.

        Args:
            identity_repo (IIdentityRepository): Repository for identity lookups.
            audit_repo (IAuditRepository): Repository for usage/audit persistence.
        """
        self.identity_repo = identity_repo
        self.audit_repo = audit_repo

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
        model_pricing_config: PricingConfig | dict[str, Any] | None = None,
    ) -> UsageRecord:
        """Tracks and logs usage securely to the audit repository.

        Calculates no pricing internally; persists metadata and cost passed from LiteLLM.
        """
        try:
            record = UsageRecord(
                id=str(uuid.uuid4()),
                org_id=org_id,
                user_id=user_id,
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

            # --- CUMULATIVE AGGREGATION ---
            period = datetime.now(UTC).strftime("%Y-%m")
            update_dto = UsageAggregateUpdateDTO(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cached_tokens=cached_tokens,
                cost_usd=cost_usd,
                execution_count=1,
            )

            # System Level (All traffic)
            await self.audit_repo.upsert_usage_aggregate(SystemOrganizations.ROOT_SYSTEM, None, period, update_dto)
            await self.audit_repo.upsert_usage_aggregate(SystemOrganizations.ROOT_SYSTEM, None, "all-time", update_dto)

            # Organization Level
            if org_id:
                await self.audit_repo.upsert_usage_aggregate("organization", org_id, period, update_dto)
                await self.audit_repo.upsert_usage_aggregate("organization", org_id, "all-time", update_dto)
            if user_id:
                await self.audit_repo.upsert_usage_aggregate("user", user_id, period, update_dto)
                await self.audit_repo.upsert_usage_aggregate("user", user_id, "all-time", update_dto)

            # --- PROMPT_CACHING_DRIFT_ALERT ---
            pricing_cfg = (
                model_pricing_config
                if isinstance(model_pricing_config, PricingConfig)
                else (PricingConfig.model_validate(model_pricing_config) if model_pricing_config else None)
            )
            has_prompt_caching = pricing_cfg.cached_input_token_price is not None if pricing_cfg else False

            if has_prompt_caching:
                recent_records_data = await self.audit_repo.get_usage_records(scope="user", entity_id=user_id)
                # Use last 4 from DB + current record
                records = list(recent_records_data[-4:])
                records.append(record)

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
        """Checks if organization is within quota limits (Current Month).

        Returns True if SAFE (under limit), False if EXCEEDED.

        Raises:
            AppException: If checking quota fails (infrastructure error).
        """
        try:
            # 1. Get Org Limits
            if not org_id:
                msg = "Quota Check: Missing Organization ID (Orphan User). Execution denied."
                logger.error("[UsageService] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                )

            if org_id == SystemOrganizations.ROOT_SYSTEM:
                return True  # System internal tasks are exempt from hard quota ceilings

            org = await self.identity_repo.get_organization(org_id)
            if not org:
                # Fail-Fast: Unknown orgs cannot consume LLM traffic
                msg = f"Quota Check: Organization '{org_id}' not found. Execution denied."
                logger.error("[UsageService] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
                raise AppException(
                    message=msg, status_code=404, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value}
                )

            limit = float(org.quota_limit)

            # 2. Calculate Usage (Current Month)
            now = datetime.now(UTC)
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()

            used = await self.identity_repo.get_org_usage_total(org_id, since=start_of_month)

            if used >= limit:
                logger.warning("Quota Exceeded for %s: Used $%s >= Limit $%s", org_id, used, limit)
                return False

            return True

        except AppException:
            # Re-raise explicit AppExceptions without double-wrapping
            raise
        except Exception as e:
            logger.error(
                "[Usage] %s check failed for %s: %s", ErrorCodes.QUOTA_CHECK_FAILED.value, org_id, e, exc_info=True
            )
            # Fail FAST. Do not swallow errors.
            raise AppException(
                message=f"Quota check failed: {e}",
                status_code=500,
                details={"error_code": ErrorCodes.QUOTA_CHECK_FAILED.value},
            ) from e

    async def get_usage_report(self, scope: str, entity_id: str | None = None, since: str | None = None) -> UsageReport:
        """Retrieves a consolidated usage report for a given scope.

        Args:
            scope (str): The reporting scope (e.g., "org", "user", "system").
            entity_id (str | None): The target entity ID. Defaults to None.
            since (str | None): The start date in ISO format. Defaults to None.

        Returns:
            UsageReport: The computed usage report with token and cost aggregations.

        Raises:
            AppException: If retrieval from the repository fails.
        """
        # Determine period
        period = "all-time"
        if since:
            now = datetime.now(UTC)
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
            if since >= start_of_month:
                period = now.strftime("%Y-%m")

        # Map frontend scope 'org' to 'organization' exactly as aggregated
        mapped_scope = "organization" if scope == "org" else scope
        agg_dto = await self.audit_repo.get_usage_aggregate(mapped_scope, entity_id, period)

        if agg_dto:
            token_usage = TokenUsage(
                prompt_tokens=agg_dto.total_input_tokens,
                completion_tokens=agg_dto.total_output_tokens,
                total_tokens=agg_dto.total_input_tokens + agg_dto.total_output_tokens,
                cached_tokens=agg_dto.total_cached_tokens,
                cost_usd=agg_dto.total_cost_usd,
            )
        else:
            records = await self.audit_repo.get_usage_records(scope=mapped_scope, entity_id=entity_id, since=since)

            prompt_tokens = sum(r.input_tokens for r in records)
            completion_tokens = sum(r.output_tokens for r in records)
            total_tokens = sum((r.input_tokens + r.output_tokens) for r in records)
            cached_tokens = sum((r.cached_tokens or 0) for r in records)
            reasoning_tokens = sum((r.reasoning_tokens or 0) for r in records)
            cost_usd = sum(float(r.cost_usd) for r in records)

            token_usage = TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cached_tokens=cached_tokens,
                reasoning_tokens=reasoning_tokens,
                cost_usd=cost_usd,
            )

        quota_limit = None
        percentage_used = None
        mapped_scope = "organization" if scope == "org" else scope
        if mapped_scope == "organization" and entity_id:
            org = await self.identity_repo.get_organization(entity_id)
            if org:
                quota_limit = float(org.quota_limit)
                if quota_limit > 0:
                    percentage_used = min(100.0, (token_usage.cost_usd / quota_limit) * 100.0)

        return UsageReport(
            scope=scope,
            entity_id=entity_id,
            period="Custom" if since else "All-time",
            usage=token_usage,
            quota_limit_usd=quota_limit,
            percentage_used=percentage_used,
        )
