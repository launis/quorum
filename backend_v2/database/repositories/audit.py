import copy
import logging
import uuid
from typing import Any

from backend_v2.database.driver import Filter
from backend_v2.database.repositories.base import BaseRepository
from backend_v2.models.auth import SystemOrganizations

logger = logging.getLogger(__name__)


class AuditRepositoryImpl(BaseRepository):
    """Repository implementation for Audit Logs and Usage Data."""

    async def log_audit_event(self, event_data: dict[str, Any]) -> None:
        doc_id = event_data.get("id") or str(uuid.uuid4())
        event_data["id"] = doc_id
        await self.driver.upsert("audit_logs", event_data, doc_id)

    async def get_audit_logs(
        self,
        organization_id: str | None = None,
        actor_id: str | None = None,
        action: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        filters = []
        if organization_id:
            filters.append(Filter("organization_id", "==", organization_id))
        if actor_id:
            filters.append(Filter("actor_id", "==", actor_id))
        if action:
            filters.append(Filter("action", "==", action))

        return await self.driver.query(
            "audit_logs", filters=filters, limit=limit, order_by="timestamp", descending=True
        )

    async def log_usage(self, record: Any) -> None:
        if hasattr(record, "model_dump"):
            data = record.model_dump()
        else:
            data = record

        doc_id = data.get("id") or str(uuid.uuid4())
        data["id"] = doc_id
        await self.driver.upsert("usage", data, doc_id)

    async def get_usage_records(
        self, scope: str, entity_id: str | None = None, since: str | None = None
    ) -> list[dict[str, Any]]:
        filters = []
        if scope == "organization" and entity_id:
            filters.append(Filter("org_id", "==", entity_id))
        elif scope == "user" and entity_id:
            filters.append(Filter("user_id", "==", entity_id))

        if since:
            filters.append(Filter("timestamp", ">=", since))

        return await self.driver.query("usage", filters)

    async def get_usage_aggregate(self, scope: str, entity_id: str | None, period: str) -> dict[str, Any] | None:
        agg_id = f"{scope}_{entity_id or 'system'}_{period}"
        return await self.driver.get("usage_aggregates", agg_id)

    async def upsert_usage_aggregate(
        self, scope: str, entity_id: str | None, period: str, update_data: dict[str, Any]
    ) -> None:
        agg_id = f"{scope}_{entity_id or 'system'}_{period}"
        update_data["id"] = agg_id
        update_data["scope"] = scope
        if entity_id:
            update_data["entity_id"] = entity_id
        update_data["period"] = period

        existing = await self.get_usage_aggregate(scope, entity_id, period)
        if existing:
            merged = copy.deepcopy(existing)
            merged["total_executions"] = existing.get("total_executions", 0) + update_data.get("total_executions", 0)

            ex_usage = existing.get("usage", {})
            up_usage = update_data.get("usage", {})
            merged["usage"] = {
                "prompt_tokens": ex_usage.get("prompt_tokens", 0) + up_usage.get("prompt_tokens", 0),
                "completion_tokens": ex_usage.get("completion_tokens", 0) + up_usage.get("completion_tokens", 0),
                "total_tokens": ex_usage.get("total_tokens", 0) + up_usage.get("total_tokens", 0),
                "cached_tokens": ex_usage.get("cached_tokens", 0) + up_usage.get("cached_tokens", 0),
                "reasoning_tokens": ex_usage.get("reasoning_tokens", 0) + up_usage.get("reasoning_tokens", 0),
                "cost_usd": ex_usage.get("cost_usd", 0.0) + up_usage.get("cost_usd", 0.0),
            }
            await self.driver.upsert("usage_aggregates", merged, agg_id)
        else:
            if "usage" not in update_data:
                update_data["usage"] = {}
            for k in ["prompt_tokens", "completion_tokens", "total_tokens", "cached_tokens", "reasoning_tokens"]:
                if k not in update_data["usage"]:
                    update_data["usage"][k] = update_data.get(k, 0)
            if "cost_usd" not in update_data["usage"]:
                update_data["usage"]["cost_usd"] = update_data.get("cost_usd", 0.0)

            await self.driver.upsert("usage_aggregates", update_data, agg_id)

    async def get_detailed_usage(
        self, scope: str, target_id: str | None = None, since: str | None = None
    ) -> dict[str, Any]:
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
            total_cost += e.get("cost_estimate", 0.0)
            total_time += e.get("duration_ms", 0)
            wid = e.get("workflow_id")
            if wid:
                workflows_used[wid] = workflows_used.get(wid, 0) + 1
            mu = e.get("models_used", {})
            if isinstance(mu, dict):
                for m, count in mu.items():
                    models_used[m] = models_used.get(m, 0) + count

        if workflows_used:
            try:
                wf_filters = []
                if scope == "org" and target_id:
                    wf_filters.append(Filter("organization_id", "in", [target_id, SystemOrganizations.ROOT_SYSTEM]))
                all_workflows = await self.driver.query("workflows", wf_filters)
                wf_names = {w["id"]: w.get("name", w["id"]) for w in all_workflows}

                named_workflows_used: dict[str, int] = {}
                for wid, count in workflows_used.items():
                    name = wf_names.get(wid, wid)
                    name_str = str(name)
                    named_workflows_used[name_str] = named_workflows_used.get(name_str, 0) + count
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
            usage_data = agg.get("usage", {})
            prompt_tokens = usage_data.get("prompt_tokens", 0)
            completion_tokens = usage_data.get("completion_tokens", 0)
            total_tokens = usage_data.get("total_tokens", 0)
            cached_tokens = usage_data.get("cached_tokens", 0)
            reasoning_tokens = usage_data.get("reasoning_tokens", 0)

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
