from typing import Any

from backend_v2.database.driver import Filter
from backend_v2.database.repositories.base import BaseRepository
from backend_v2.models.auth import SystemOrganizations


class IdentityRepositoryImpl(BaseRepository):
    """Repository implementation for Users and Organizations."""

    async def list_organizations(self) -> list[dict[str, Any]]:
        return await self.driver.query("organizations")

    async def get_organization(self, org_id: str) -> dict[str, Any] | None:
        return await self.driver.get("organizations", org_id)

    async def create_organization(self, org_data: dict[str, Any]) -> str:
        doc_id = org_data["id"]
        return await self.driver.upsert("organizations", org_data, doc_id)

    async def update_organization(self, org_id: str, updates: dict[str, Any]) -> bool:
        return await self.driver.update("organizations", org_id, updates)

    async def delete_organization(self, org_id: str) -> bool:
        return await self.driver.delete("organizations", org_id)

    async def list_users(self, org_id: str | None = None) -> list[dict[str, Any]]:
        filters = []
        if org_id:
            filters.append(Filter("organization_id", "==", org_id))
        return await self.driver.query("users", filters)

    async def get_user(self, user_id: str) -> dict[str, Any] | None:
        return await self.driver.get("users", user_id)

    async def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        res = await self.driver.query("users", [Filter("email", "==", email)], limit=1)
        return res[0] if res else None

    async def create_user(self, user_data: dict[str, Any]) -> str:
        doc_id = user_data["id"]
        return await self.driver.upsert("users", user_data, doc_id)

    async def update_user(self, user_id: str, updates: dict[str, Any]) -> bool:
        return await self.driver.update("users", user_id, updates)

    async def delete_user(self, user_id: str) -> bool:
        return await self.driver.delete("users", user_id)

    async def delete_org_data(self, org_id: str) -> None:
        users = await self.list_users(org_id)
        for u in users:
            await self.driver.delete("users", u["id"])

        execs = await self.driver.query("executions", [Filter("organization_id", "==", org_id)])
        for e in execs:
            await self.driver.delete("executions", e["id"])

        wfs = await self.driver.query(
            "workflows", [Filter("organization_id", "in", [org_id, SystemOrganizations.ROOT_SYSTEM])]
        )
        for w in wfs:
            # We don't want to delete ROOT_SYSTEM workflows when deleting a specific org.
            # The query shouldn't blindly delete system orgs if org_id is not ROOT.
            # Let's filter out system.
            if w.get("organization_id") == org_id:
                await self.driver.delete("workflows", w["id"])

    async def get_org_usage_total(self, org_id: str, since: str | None = None) -> float:
        filters = [Filter("organization_id", "==", org_id)]
        if since:
            filters.append(Filter("completed_at", ">=", since))

        execs = await self.driver.query("executions", filters)
        return float(sum(e.get("cost_estimate", 0.0) for e in execs))
