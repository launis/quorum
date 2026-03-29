"""Usage Service for tracking LLM token consumption and costs.

This module persists immutable usage records to the repository, utilizing
the cost calculated by LiteLLM (no local pricing logic).
"""

import logging
import uuid
from datetime import UTC, datetime

from backend_v2.database.repository import AbstractWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain import UsageRecord
from backend_v2.models.domain.usage import TokenUsage, UsageReport

logger = logging.getLogger(__name__)


class UsageService:
    """Service for tracking and logging LLM usage (LiteLLM-compliant)."""

    def __init__(self, repo: AbstractWorkflowRepository):
        """Initialize the UsageService.

        Args:
            repo (AbstractWorkflowRepository): The repository for data persistence.
        """
        self.repo = repo

    async def track_usage(
        self,
        org_id: str,
        user_id: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        cached_tokens: int = 0,
        reasoning_tokens: int = 0,
        latency_ms: int | None = None,
        finish_reason: str | None = None,
        system_fingerprint: str | None = None,
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
            record = UsageRecord(
                id=str(uuid.uuid4()),
                org_id=org_id,
                user_id=user_id,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cached_tokens=cached_tokens,
                reasoning_tokens=reasoning_tokens,
                latency_ms=latency_ms,
                finish_reason=finish_reason,
                system_fingerprint=system_fingerprint,
                cost_usd=cost_usd,
                timestamp=datetime.now(UTC),
            )

            await self.repo.log_usage(record)

            # --- CUMULATIVE AGGREGATION ---
            if hasattr(self.repo, "upsert_usage_aggregate"):
                period = datetime.now(UTC).strftime("%Y-%m")
                total_t = input_tokens + output_tokens
                update_data = {
                    "total_executions": 1,
                    "usage": {
                        "prompt_tokens": input_tokens,
                        "completion_tokens": output_tokens,
                        "total_tokens": total_t,
                        "cached_tokens": cached_tokens,
                        "reasoning_tokens": reasoning_tokens,
                        "cost_usd": cost_usd,
                    },
                }

                # System Level (All traffic)
                await self.repo.upsert_usage_aggregate("system", None, period, update_data)
                await self.repo.upsert_usage_aggregate("system", None, "all-time", update_data)

                # Organization Level
                if org_id:
                    await self.repo.upsert_usage_aggregate("organization", org_id, period, update_data)
                    await self.repo.upsert_usage_aggregate("organization", org_id, "all-time", update_data)
                if user_id:
                    await self.repo.upsert_usage_aggregate("user", user_id, period, update_data)
                    await self.repo.upsert_usage_aggregate("user", user_id, "all-time", update_data)

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
                logger.warning("Quota Check: No Organization ID (Orphan User). Allowing execution (Default Policy).")
                return True

            org = await self.repo.get_organization(org_id)
            if not org:
                # If org doesn't exist, we probably shouldn't run executions, but maybe it's system?
                # System org usually has no limit or high limit.
                logger.warning(
                    "Quota Check: Organization '%s' not found. Allowing execution (Fail Open for Pilot).", org_id
                )
                return True

            limit = float(org.get("quota_limit", 10.0))  # Default $10.00 conservative

            # 2. Calculate Usage (Current Month)
            now = datetime.now(UTC)
            # ISO Format for simple string comparison in JSON/TinyDB
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()

            used = await self.repo.get_org_usage_total(org_id, since=start_of_month)

            if used >= limit:
                logger.warning("Quota Exceeded for %s: Used $%s >= Limit $%s", org_id, used, limit)
                return False

            return True

        except Exception as e:
            error_code = ErrorCodes.QUOTA_CHECK_FAILED
            logger.error("[Usage] %s check failed for %s: %s", error_code.value, org_id, e, exc_info=True)
            # Fail FAST. Do not swallow errors.
            raise AppException(
                message=f"Quota check failed: {e}", status_code=500, details={"error_code": error_code}
            ) from e

    async def get_usage_report(self, scope: str, entity_id: str | None = None, since: str | None = None) -> UsageReport:
        # Determine period
        period = "all-time"
        if since:
            now = datetime.now(UTC)
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
            if since >= start_of_month:
                period = now.strftime("%Y-%m")

        agg = None
        if hasattr(self.repo, "get_usage_aggregate"):
            # Map frontend scope 'org' to 'organization' exactly as aggregated
            mapped_scope = "organization" if scope == "org" else scope
            agg = await self.repo.get_usage_aggregate(mapped_scope, entity_id, period)

        if agg:
            usage_data = agg.get("usage", {})
            token_usage = TokenUsage(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0),
                cached_tokens=usage_data.get("cached_tokens", 0),
                reasoning_tokens=usage_data.get("reasoning_tokens", 0),
                cost_usd=usage_data.get("cost_usd", 0.0),
            )
        else:
            records_data = []
            if hasattr(self.repo, "get_usage_records"):
                mapped_scope = "organization" if scope == "org" else scope
                records_data = await self.repo.get_usage_records(scope=mapped_scope, entity_id=entity_id, since=since)

            prompt_tokens = sum(r.get("input_tokens", 0) for r in records_data)
            completion_tokens = sum(r.get("output_tokens", 0) for r in records_data)
            total_tokens = sum(
                r.get("total_tokens", r.get("input_tokens", 0) + r.get("output_tokens", 0)) for r in records_data
            )
            cached_tokens = sum(r.get("cached_tokens", 0) for r in records_data)
            reasoning_tokens = sum(r.get("reasoning_tokens", 0) for r in records_data)
            cost_usd = sum(float(r.get("cost_usd", 0.0)) for r in records_data)

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
            org = await self.repo.get_organization(entity_id)
            if org:
                quota_limit = float(org.get("quota_limit", 10.0))
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
