import json
import logging
import os
from typing import Any, cast

from fastapi.concurrency import run_in_threadpool

from backend_v2.database.driver import Filter
from backend_v2.database.repositories.base import AppendOnlyRepositoryBase
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import SystemOrganizations
from backend_v2.models.v2_core import Workflow

logger = logging.getLogger(__name__)


class WorkflowRepositoryImpl(AppendOnlyRepositoryBase):
    """Repository implementation for Workflows and Steps."""

    async def get_workflow_definition(self, workflow_id: str) -> Workflow | None:
        data = await self.driver.get("workflows", workflow_id)

        if not data:
            file_path = f"data/workflows/{workflow_id}.json"
            if os.path.exists(file_path):
                try:

                    def _read_file() -> dict[str, Any]:
                        with open(file_path, encoding="utf-8") as f:
                            return cast(dict[str, Any], json.load(f))

                    data = await run_in_threadpool(_read_file)
                    if "description" not in data:
                        data["description"] = "Loaded from file"
                except Exception as e:
                    logger.error("Failed to load workflow from disk: %s", e)
                    return None
            else:
                return None

        return Workflow(**data)

    async def get_workflow(self, workflow_id: str) -> Workflow | None:
        return await self.get_workflow_definition(workflow_id)

    async def get_all_workflows(
        self, organization_id: str | None = None, role: str | None = None
    ) -> list[dict[str, Any]]:
        filters = []
        if role != "ROOT":
            if organization_id:
                filters.append(Filter("organization_id", "in", [organization_id, SystemOrganizations.ROOT_SYSTEM]))

        return await self.driver.query("workflows", filters)

    async def get_workflow_by_id(self, workflow_id: str) -> dict[str, Any] | None:
        return await self.driver.get("workflows", workflow_id)

    async def get_workflow_by_slug(self, slug: str) -> dict[str, Any] | None:
        res = await self.driver.query("workflows", [Filter("slug", "==", slug)], limit=1)
        return res[0] if res else None

    async def create_workflow(self, workflow_data: dict[str, Any]) -> str:
        doc_id = workflow_data["id"]
        return await self.driver.upsert("workflows", workflow_data, doc_id)

    async def update_workflow(self, workflow_id: str, updates: dict[str, Any]) -> str:
        old_doc = await self.get_workflow_by_id(workflow_id)
        if not old_doc:
            from backend_v2.exceptions import WorkflowNotFoundError

            raise WorkflowNotFoundError(workflow_id)

        await self.driver.update("workflows", workflow_id, {"is_latest": False})

        slug, new_id, ver = self._increment_version(workflow_id)

        new_doc = dict(old_doc)
        new_doc.update(updates)
        new_doc["id"] = new_id
        new_doc["is_latest"] = True
        new_doc["version"] = ver
        new_doc["slug"] = slug

        await self.driver.upsert("workflows", new_doc, new_id)
        return new_id

    async def update_workflow_definition(self, workflow_id: str, definition_data: dict[str, Any]) -> str:
        return await self.update_workflow(workflow_id, definition_data)

    async def delete_workflow(self, workflow_id: str) -> bool:
        return await self.driver.delete("workflows", workflow_id)

    async def count_workflows(self) -> int:
        return await self.driver.count("workflows")

    # --- Steps ---

    async def get_all_steps(self) -> list[dict[str, Any]]:
        return await self.driver.query("steps")

    async def get_step_by_id(self, step_id: str) -> dict[str, Any] | None:
        step = await self.driver.get("steps", step_id)
        if step:
            return step

        all_wfs = await self.driver.query("workflows")
        for wf in all_wfs:
            steps = wf.get("steps", [])
            if not isinstance(steps, list):
                continue
            for s in steps:
                if isinstance(s, dict) and s.get("id") == step_id:
                    return s
        return None

    async def get_step(self, step_id: str) -> dict[str, Any] | None:
        return await self.get_step_by_id(step_id)

    async def create_step(self, step_data: dict[str, Any]) -> str:
        doc_id = step_data["id"]
        return await self.driver.upsert("steps", step_data, doc_id)

    async def update_step(self, step_id: str, updates: dict[str, Any]) -> str:
        await self.driver.update("steps", step_id, updates)
        return step_id

    async def delete_step(self, step_id: str, force_delete: bool = False) -> bool:
        step = await self.get_step_by_id(step_id)
        if not step:
            return False

        if not force_delete:
            wfs = await self.get_all_workflows()
            for wf in wfs:
                wf_steps = wf.get("steps", [])
                for s in wf_steps:
                    if isinstance(s, dict) and s.get("id") == step_id:
                        wf_id = wf.get("id", "unknown")
                        raise AppException(
                            message="Step delete blocked by workflow usage.",
                            details={
                                "error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value,
                                "step_id": step_id,
                                "workflow_id": wf_id,
                            },
                            status_code=400,
                        )
                    elif isinstance(s, str) and s == step_id:
                        wf_id = wf.get("id", "unknown")
                        raise AppException(
                            message="Step delete blocked by workflow usage.",
                            details={
                                "error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value,
                                "step_id": step_id,
                                "workflow_id": wf_id,
                            },
                            status_code=400,
                        )

        return await self.driver.delete("steps", step_id)
