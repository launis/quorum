"""Database repository implementation module for Audit Logs and Usage Data."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime

from backend_v2.database.driver import Filter
from backend_v2.database.repositories.base import BaseRepository
from backend_v2.exceptions import ErrorCodes
from backend_v2.models.domain.base import (
    AuditLogCreateDTO,
    AuditLogEntry,
    DetailedUsageDTO,
    UsageAggregateDTO,
    UsageAggregateUpdateDTO,
    UsageRecord,
)

logger = logging.getLogger(__name__)


class AuditRepositoryImpl(BaseRepository):
    """Repository implementation for Audit Logs and Usage Data."""

    async def log_audit_event(self, event_data: AuditLogCreateDTO) -> None:
        """Logs an audit event into storage.

        Args:
            event_data: AuditLogCreateDTO containing audit event fields.
        """
        payload = event_data.model_dump(mode="json")
        doc_id = str(uuid.uuid4())
        payload["id"] = doc_id
        if "timestamp" not in payload or not payload["timestamp"]:
            payload["timestamp"] = datetime.now().isoformat()
        await self.driver.upsert("audit_logs", payload, doc_id)

    async def get_audit_logs(
        self,
        organization_id: str | None = None,
        actor_id: str | None = None,
        action: str | None = None,
        limit: int = 100,
    ) -> list[AuditLogEntry]:
        """Retrieves audit logs filtered by organization, actor, or action.

        Args:
            organization_id: Optional organization filter.
            actor_id: Optional actor ID filter.
            action: Optional action filter.
            limit: Maximum number of records to return.

        Returns:
            List of validated AuditLogEntry domain models.
        """
        filters = []
        if organization_id:
            filters.append(Filter("organization_id", "==", organization_id))
        if actor_id:
            filters.append(Filter("actor_id", "==", actor_id))
        if action:
            filters.append(Filter("action", "==", action))

        raw_logs = await self.driver.query(
            "audit_logs", filters=filters, limit=limit, order_by="timestamp", descending=True
        )
        logs: list[AuditLogEntry] = []
        for entry in raw_logs:
            try:
                logs.append(AuditLogEntry.model_validate(entry, strict=False))
            except Exception as e:
                item_id = entry["id"] if "id" in entry else "unknown"
                logger.error(
                    "[AuditRepository] %s: Skipping corrupted audit log %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    item_id,
                    e,
                    exc_info=True,
                )
        return logs

    async def log_usage(self, record: UsageRecord) -> None:
        """Logs a resource usage record.

        Args:
            record: UsageRecord model.
        """
        data = record.model_dump(mode="json")
        doc_id = data["id"] if "id" in data and data["id"] else str(uuid.uuid4())
        data["id"] = doc_id
        await self.driver.upsert("usage", data, doc_id)

    async def get_usage_records(
        self, scope: str, entity_id: str | None = None, since: str | None = None
    ) -> list[UsageRecord]:
        """Retrieves usage records for a specific scope and entity.

        Args:
            scope: Scope type (e.g. 'organization' or 'user').
            entity_id: Optional entity ID.
            since: Optional ISO timestamp filter.

        Returns:
            List of validated UsageRecord domain models.
        """
        filters = []
        if scope == "organization" and entity_id:
            filters.append(Filter("org_id", "==", entity_id))
        elif scope == "user" and entity_id:
            filters.append(Filter("user_id", "==", entity_id))

        if since:
            filters.append(Filter("timestamp", ">=", since))

        raw_records = await self.driver.query("usage", filters)
        records: list[UsageRecord] = []
        for u in raw_records:
            try:
                records.append(UsageRecord.model_validate(u, strict=False))
            except Exception as e:
                item_id = u["id"] if "id" in u else "unknown"
                logger.error(
                    "[AuditRepository] %s: Skipping corrupted usage record %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    item_id,
                    e,
                    exc_info=True,
                )
        return records

    async def get_usage_aggregate(self, scope: str, entity_id: str | None, period: str) -> UsageAggregateDTO | None:
        """Retrieves an aggregated usage summary document.

        Args:
            scope: Scope type.
            entity_id: Optional entity ID.
            period: Aggregation period (e.g. '2026-08' or 'all-time').

        Returns:
            The UsageAggregateDTO if found, otherwise None.
        """
        agg_id = f"{scope}_{entity_id or 'system'}_{period}"
        doc = await self.driver.get("usage_aggregates", agg_id)
        if not doc:
            return None
        return UsageAggregateDTO.model_validate(doc, strict=False)

    async def upsert_usage_aggregate(
        self, scope: str, entity_id: str | None, period: str, update_data: UsageAggregateUpdateDTO
    ) -> None:
        """Upserts an aggregated usage record, merging token and execution totals.

        Args:
            scope: Scope type.
            entity_id: Optional entity ID.
            period: Aggregation period.
            update_data: UsageAggregateUpdateDTO of usage increments.
        """
        agg_id = f"{scope}_{entity_id or 'system'}_{period}"
        existing = await self.get_usage_aggregate(scope, entity_id, period)

        if existing:
            new_input = existing.total_input_tokens + update_data.input_tokens
            new_output = existing.total_output_tokens + update_data.output_tokens
            new_cached = existing.total_cached_tokens + update_data.cached_tokens
            new_cost = existing.total_cost_usd + update_data.cost_usd
            new_execs = existing.execution_count + update_data.execution_count
        else:
            new_input = update_data.input_tokens
            new_output = update_data.output_tokens
            new_cached = update_data.cached_tokens
            new_cost = update_data.cost_usd
            new_execs = update_data.execution_count

        merged = UsageAggregateDTO(
            organization_id=entity_id or "system",
            period=period,
            total_input_tokens=new_input,
            total_output_tokens=new_output,
            total_cached_tokens=new_cached,
            total_cost_usd=new_cost,
            execution_count=new_execs,
        )
        await self.driver.upsert("usage_aggregates", merged.model_dump(mode="json"), agg_id)

    async def get_detailed_usage(
        self, scope: str, target_id: str | None = None, since: str | None = None
    ) -> DetailedUsageDTO:
        """Calculates detailed multi-dimensional usage metrics.

        Args:
            scope: Scope ('user', 'org', 'system').
            target_id: Optional ID for the targeted scope.
            since: Optional ISO timestamp filter.

        Returns:
            DetailedUsageDTO containing calculated metrics.
        """
        filters = []
        if since:
            filters.append(Filter("completed_at", ">=", since))

        if scope == "user" and target_id:
            filters.append(Filter("user_id", "==", target_id))
        elif scope == "org" and target_id:
            filters.append(Filter("organization_id", "==", target_id))

        execs = await self.driver.query("executions", filters)

        total_cost = 0.0
        total_tokens = 0
        models_used: dict[str, int] = {}
        workflows_used: dict[str, int] = {}

        for e in execs:
            if "cost_estimate" in e and e["cost_estimate"] is not None:
                total_cost += float(e["cost_estimate"])
            if "workflow_id" in e and e["workflow_id"]:
                wid_str = str(e["workflow_id"])
                workflows_used[wid_str] = (workflows_used[wid_str] + 1) if wid_str in workflows_used else 1
            if "models_used" in e and e["models_used"]:
                for m, count in e["models_used"].items():
                    models_used[m] = (models_used[m] + int(count)) if m in models_used else int(count)

        period = "all-time"
        if since:
            try:
                dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
                period = dt.strftime("%Y-%m")
            except Exception as e:
                logger.warning("Invalid date format '%s', returning to all-time view: %s", since, e)

        mapped_scope = "organization" if scope == "org" else scope
        agg = await self.get_usage_aggregate(mapped_scope, target_id, period)
        if agg:
            total_tokens = agg.total_input_tokens + agg.total_output_tokens

        return DetailedUsageDTO(
            organization_id=target_id or "system",
            total_cost_usd=total_cost,
            total_tokens=total_tokens,
            by_model=models_used,
            by_workflow=workflows_used,
        )
