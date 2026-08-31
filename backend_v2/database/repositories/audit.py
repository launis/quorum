"""Database repository implementation module for Audit Logs and Usage Data."""

import copy
import logging
import uuid
from typing import Any

from backend_v2.database.driver import Filter
from backend_v2.database.repositories.base import BaseRepository
from backend_v2.exceptions import ErrorCodes
from backend_v2.models.auth import SystemOrganizations
from backend_v2.models.domain.base import AuditLogEntry, UsageRecord

logger = logging.getLogger(__name__)


class AuditRepositoryImpl(BaseRepository):
    """Repository implementation for Audit Logs and Usage Data."""

    async def log_audit_event(self, event_data: dict[str, Any]) -> None:
        """Logs an audit event into storage.

        Args:
            event_data: Dictionary containing audit event fields.
        """
        doc_id = event_data["id"] if "id" in event_data else str(uuid.uuid4())
        event_data["id"] = doc_id
        await self.driver.upsert("audit_logs", event_data, doc_id)

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

    async def log_usage(self, record: UsageRecord | dict[str, Any]) -> None:
        """Logs a resource usage record.

        Args:
            record: UsageRecord model or dictionary.
        """
        if isinstance(record, UsageRecord):
            data = record.model_dump(mode="json")
        else:
            data = record

        doc_id = data["id"] if "id" in data else str(uuid.uuid4())
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

    async def get_usage_aggregate(self, scope: str, entity_id: str | None, period: str) -> dict[str, Any] | None:
        """Retrieves an aggregated usage summary document.

        Args:
            scope: Scope type.
            entity_id: Optional entity ID.
            period: Aggregation period (e.g. '2026-08' or 'all-time').

        Returns:
            The aggregate dictionary if found, otherwise None.
        """
        agg_id = f"{scope}_{entity_id or 'system'}_{period}"
        return await self.driver.get("usage_aggregates", agg_id)

    async def upsert_usage_aggregate(
        self, scope: str, entity_id: str | None, period: str, update_data: dict[str, Any]
    ) -> None:
        """Upserts an aggregated usage record, merging token and execution totals.

        Args:
            scope: Scope type.
            entity_id: Optional entity ID.
            period: Aggregation period.
            update_data: Dictionary of usage increments.
        """
        agg_id = f"{scope}_{entity_id or 'system'}_{period}"
        update_data["id"] = agg_id
        update_data["scope"] = scope
        if entity_id:
            update_data["entity_id"] = entity_id
        update_data["period"] = period

        existing = await self.get_usage_aggregate(scope, entity_id, period)
        if existing:
            merged = copy.deepcopy(existing)
            ex_execs = existing["total_executions"] if "total_executions" in existing else 0
            up_execs = update_data["total_executions"] if "total_executions" in update_data else 0
            merged["total_executions"] = ex_execs + up_execs

            ex_usage = existing["usage"] if "usage" in existing else {}
            up_usage = update_data["usage"] if "usage" in update_data else {}
            merged["usage"] = {
                "prompt_tokens": (ex_usage["prompt_tokens"] if "prompt_tokens" in ex_usage else 0)
                + (up_usage["prompt_tokens"] if "prompt_tokens" in up_usage else 0),
                "completion_tokens": (ex_usage["completion_tokens"] if "completion_tokens" in ex_usage else 0)
                + (up_usage["completion_tokens"] if "completion_tokens" in up_usage else 0),
                "total_tokens": (ex_usage["total_tokens"] if "total_tokens" in ex_usage else 0)
                + (up_usage["total_tokens"] if "total_tokens" in up_usage else 0),
                "cached_tokens": (ex_usage["cached_tokens"] if "cached_tokens" in ex_usage else 0)
                + (up_usage["cached_tokens"] if "cached_tokens" in up_usage else 0),
                "reasoning_tokens": (ex_usage["reasoning_tokens"] if "reasoning_tokens" in ex_usage else 0)
                + (up_usage["reasoning_tokens"] if "reasoning_tokens" in up_usage else 0),
                "cost_usd": (ex_usage["cost_usd"] if "cost_usd" in ex_usage else 0.0)
                + (up_usage["cost_usd"] if "cost_usd" in up_usage else 0.0),
            }
            await self.driver.upsert("usage_aggregates", merged, agg_id)
        else:
            if "usage" not in update_data:
                update_data["usage"] = {}
            for k in ["prompt_tokens", "completion_tokens", "total_tokens", "cached_tokens", "reasoning_tokens"]:
                if k not in update_data["usage"]:
                    update_data["usage"][k] = update_data[k] if k in update_data else 0
            if "cost_usd" not in update_data["usage"]:
                update_data["usage"]["cost_usd"] = update_data["cost_usd"] if "cost_usd" in update_data else 0.0

            await self.driver.upsert("usage_aggregates", update_data, agg_id)

    async def get_detailed_usage(
        self, scope: str, target_id: str | None = None, since: str | None = None
    ) -> dict[str, Any]:
        """Calculates detailed multi-dimensional usage metrics.

        Args:
            scope: Scope ('user', 'org', 'system').
            target_id: Optional ID for the targeted scope.
            since: Optional ISO timestamp filter.

        Returns:
            Dictionary of calculated metrics including totals, token breakdown, and workflow usage.
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
        total_runs = len(execs)
        total_time = 0
        models_used: dict[str, int] = {}
        workflows_used: dict[str, int] = {}

        for e in execs:
            if "cost_estimate" in e and e["cost_estimate"] is not None:
                total_cost += float(e["cost_estimate"])
            if "duration_ms" in e and e["duration_ms"] is not None:
                total_time += int(e["duration_ms"])
            if "workflow_id" in e and e["workflow_id"]:
                wid = str(e["workflow_id"])
                workflows_used[wid] = (workflows_used[wid] if wid in workflows_used else 0) + 1
            if "models_used" in e and e["models_used"]:
                try:
                    from pydantic import TypeAdapter

                    parsed_models = TypeAdapter(dict[str, int]).validate_python(e["models_used"])
                    for m, count in parsed_models.items():
                        models_used[m] = (models_used[m] if m in models_used else 0) + count
                except Exception:
                    pass

        if workflows_used:
            try:
                wf_filters = []
                if scope == "org" and target_id:
                    wf_filters.append(Filter("organization_id", "in", [target_id, SystemOrganizations.ROOT_SYSTEM]))
                all_workflows = await self.driver.query("workflows", wf_filters)
                wf_names = {w["id"]: (w["name"] if "name" in w else w["id"]) for w in all_workflows if "id" in w}

                named_workflows_used: dict[str, int] = {}
                for wid, count in workflows_used.items():
                    name = wf_names[wid] if wid in wf_names else wid
                    name_str = str(name)
                    named_workflows_used[name_str] = (
                        named_workflows_used[name_str] if name_str in named_workflows_used else 0
                    ) + count
                workflows_used = named_workflows_used
            except Exception as ex:
                logger.warning("Could not map workflow names: %s", ex)

        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0
        cached_tokens = 0
        reasoning_tokens = 0

        period = "all-time"
        if since:
            try:
                from datetime import datetime

                dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
                period = dt.strftime("%Y-%m")
            except Exception as e:
                logger.warning("Invalid date format '%s', returning to all-time view: %s", since, e)

        mapped_scope = "organization" if scope == "org" else scope
        agg = await self.get_usage_aggregate(mapped_scope, target_id, period)
        if agg:
            usage_data = agg["usage"] if "usage" in agg else {}
            prompt_tokens = usage_data["prompt_tokens"] if "prompt_tokens" in usage_data else 0
            completion_tokens = usage_data["completion_tokens"] if "completion_tokens" in usage_data else 0
            total_tokens = usage_data["total_tokens"] if "total_tokens" in usage_data else 0
            cached_tokens = usage_data["cached_tokens"] if "cached_tokens" in usage_data else 0
            reasoning_tokens = usage_data["reasoning_tokens"] if "reasoning_tokens" in usage_data else 0

        return {
            "total_cost_usd": total_cost,
            "total_runs": total_runs,
            "total_processing_time_ms": total_time,
            "models_used": models_used,
            "workflows_used": workflows_used,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "cached_tokens": cached_tokens,
            "reasoning_tokens": reasoning_tokens,
        }
