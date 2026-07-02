"""Usage Service for tracking LLM token consumption and costs.

This module persists immutable usage records to the repository, utilizing
the cost calculated by LiteLLM (no local pricing logic).
"""

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from backend_v2.database.interfaces import IAuditRepository, IIdentityRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import SystemOrganizations
from backend_v2.models.domain import UsageRecord
from backend_v2.models.domain.usage import TokenUsage, UsageReport

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
        cost_usd: float,
        cached_tokens: int = 0,
        cache_creation_input_tokens: int = 0,
        estimated_savings_usd: float = 0.0,
        reasoning_tokens: int = 0,
        latency_ms: int | None = None,
        finish_reason: str | None = None,
        system_fingerprint: str | None = None,
        provider_name: str | None = None,
        model_pricing_config: dict[str, Any] | None = None,
    ) -> UsageRecord:
        """Track and persist a usage record.

        This method accepts the cost calculated by the LLM Provider (LiteLLM)
        and persists the record.

        Args:
            org_id (str): Organization ID.
            user_id (str): User ID.
            model (str): Model name.
            input_tokens (int): Input token count.
            output_tokens (int): Output token count.
            cost_usd (float): The cost calculated by LiteLLM.

        Returns:
            UsageRecord: The created record.

        Raises:
            AppException: If logging usage fails.
        """
        try:
            from backend_v2.llm.adapters.adapter_factory import LLMCacheAdapterFactory

            if provider_name and model_pricing_config:
                usage_obj = TokenUsage(
                    prompt_tokens=input_tokens,
                    completion_tokens=output_tokens,
                    total_tokens=input_tokens + output_tokens,
                    cached_tokens=cached_tokens,
                    cache_creation_input_tokens=cache_creation_input_tokens,
                    reasoning_tokens=reasoning_tokens,
                    cost_usd=cost_usd,
                    estimated_savings_usd=estimated_savings_usd,
                )
                try:
                    adapter = LLMCacheAdapterFactory.get_adapter(provider_name)
                    final_usage = adapter.calculate_cost(usage_obj, model_pricing_config)
                    cost_usd = final_usage.cost_usd
                    estimated_savings_usd = final_usage.estimated_savings_usd
                except Exception as e:
                    logger.warning("Failed to calculate cost via adapter: %s", e)

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
            if hasattr(self.audit_repo, "upsert_usage_aggregate"):
                period = datetime.now(UTC).strftime("%Y-%m")
                total_t = input_tokens + output_tokens
                update_data = {
                    "total_executions": 1,
                    "usage": TokenUsage(
                        prompt_tokens=input_tokens,
                        completion_tokens=output_tokens,
                        total_tokens=total_t,
                        cached_tokens=cached_tokens,
                        cache_creation_input_tokens=cache_creation_input_tokens,
                        reasoning_tokens=reasoning_tokens,
                        cost_usd=cost_usd,
                        estimated_savings_usd=estimated_savings_usd,
                    ).model_dump(mode="json"),
                }

                # System Level (All traffic)
                await self.audit_repo.upsert_usage_aggregate(SystemOrganizations.ROOT_SYSTEM, None, period, update_data)
                await self.audit_repo.upsert_usage_aggregate(
                    SystemOrganizations.ROOT_SYSTEM, None, "all-time", update_data
                )  # noqa: E501

                # Organization Level
                if org_id:
                    await self.audit_repo.upsert_usage_aggregate("organization", org_id, period, update_data)
                    await self.audit_repo.upsert_usage_aggregate("organization", org_id, "all-time", update_data)
                if user_id:
                    await self.audit_repo.upsert_usage_aggregate("user", user_id, period, update_data)
                    await self.audit_repo.upsert_usage_aggregate("user", user_id, "all-time", update_data)

            # --- PROMPT_CACHING_DRIFT_ALERT ---
            caching_strategy = None
            if model_pricing_config:
                caching_strategy = model_pricing_config.get("caching_strategy")

            if caching_strategy == "prompt_caching":
                # Get recent records (assuming last 5 exist in db)
                if hasattr(self.audit_repo, "get_usage_records"):
                    recent_records_data = await self.audit_repo.get_usage_records(scope="user", entity_id=user_id)
                    # Use last 4 from DB + current record
                    recent_records_data = recent_records_data[-4:]
                    records = [UsageRecord.model_validate(r) for r in recent_records_data]
                    records.append(record)

                    if len(records) == 5:
                        total_cached = sum(r.cached_tokens for r in records)
                        total_all_tokens = sum((r.input_tokens + r.output_tokens + r.cached_tokens) for r in records)

                        if total_all_tokens > 0:
                            hit_rate = total_cached / total_all_tokens
                            if hit_rate < 0.80:
                                hit_rate_pct = int(hit_rate * 100)
                                logger.error(
                                    "PROMPT_CACHING_DRIFT_ALERT: Cache hit rate has degraded "
                                    f"to {hit_rate_pct}% for workflow Y. Investigate prompt mutations immediately."
                                )

            return record

        except Exception as e:
            error_code = ErrorCodes.USAGE_TRACKING_FAILED
            logger.error("[Usage] %s for %s (Org: %s): %s", error_code.value, user_id, org_id, e, exc_info=True)
            raise AppException(
                message=f"Failed to track usage: {e}", status_code=500, details={"error_code": error_code}
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
                raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED})

            if org_id == SystemOrganizations.ROOT_SYSTEM:
                return True  # System internal tasks are exempt from hard quota ceilings

            from backend_v2.models.auth import Organization

            org_data = await self.identity_repo.get_organization(org_id)
            if not org_data:
                # Fail-Fast: Unknown orgs cannot consume LLM traffic
                msg = f"Quota Check: Organization '{org_id}' not found. Execution denied."
                logger.error("[UsageService] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
                raise AppException(message=msg, status_code=404, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND})

            org = Organization.model_validate(org_data)
            limit = float(org.quota_limit)

            # 2. Calculate Usage (Current Month)
            now = datetime.now(UTC)
            # ISO Format for simple string comparison in JSON/TinyDB
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
            error_code = ErrorCodes.QUOTA_CHECK_FAILED
            logger.error("[Usage] %s check failed for %s: %s", error_code.value, org_id, e, exc_info=True)
            # Fail FAST. Do not swallow errors.
            raise AppException(
                message=f"Quota check failed: {e}", status_code=500, details={"error_code": error_code}
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

        from backend_v2.models.domain.usage import UsageAggregate

        agg_data = None
        if hasattr(self.audit_repo, "get_usage_aggregate"):
            # Map frontend scope 'org' to 'organization' exactly as aggregated
            mapped_scope = "organization" if scope == "org" else scope
            agg_data = await self.audit_repo.get_usage_aggregate(mapped_scope, entity_id, period)

        if agg_data:
            agg = UsageAggregate.model_validate(agg_data)
            token_usage = agg.usage
        else:
            records_data = []
            if hasattr(self.audit_repo, "get_usage_records"):
                mapped_scope = "organization" if scope == "org" else scope
                records_data = await self.audit_repo.get_usage_records(
                    scope=mapped_scope, entity_id=entity_id, since=since
                )

            records = [UsageRecord.model_validate(r) for r in records_data]

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
            from backend_v2.models.auth import Organization

            org_data = await self.identity_repo.get_organization(entity_id)
            if org_data:
                org = Organization.model_validate(org_data)
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
