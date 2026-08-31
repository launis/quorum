"""Database repository implementation module for Workflows and Steps."""

import json
import logging
import os
from typing import Any, cast

from fastapi.concurrency import run_in_threadpool

from backend_v2.database.driver import Filter
from backend_v2.database.repositories.base import AppendOnlyRepositoryBase
from backend_v2.exceptions import AppException, ErrorCodes, WorkflowNotFoundError
from backend_v2.models.auth import SystemOrganizations
from backend_v2.models.v2_core import Step, Workflow

logger = logging.getLogger(__name__)


class WorkflowRepositoryImpl(AppendOnlyRepositoryBase):
    """Repository implementation for Workflows and Steps."""

    async def get_workflow_definition(self, workflow_id: str) -> Workflow | None:
        """Retrieves a workflow definition by its ID.

        Args:
            workflow_id: Unique identifier for the workflow.

        Returns:
            The validated Workflow domain model if found, otherwise None.

        Raises:
            AppException: If loading from disk or validation fails.
        """
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
                    logger.error("Failed to load workflow from disk: %s", e, exc_info=True)
                    raise AppException(
                        message=f"Failed to load workflow from disk: {e}",
                        status_code=500,
                        details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
                    ) from e
            else:
                return None

        return Workflow.model_validate(data, strict=False)

    async def get_workflow(self, workflow_id: str) -> Workflow | None:
        """Retrieves a workflow by ID.

        Args:
            workflow_id: Unique identifier for the workflow.

        Returns:
            The validated Workflow domain model if found, otherwise None.
        """
        return await self.get_workflow_definition(workflow_id)

    async def get_all_workflows(self, organization_id: str | None = None, role: str | None = None) -> list[Workflow]:
        """Retrieves all workflows accessible to the organization.

        Args:
            organization_id: Optional organization filter.
            role: User role (e.g. ROOT).

        Returns:
            List of validated Workflow domain models.
        """
        filters = []
        if role != "ROOT":
            if organization_id:
                filters.append(Filter("organization_id", "in", [organization_id, SystemOrganizations.ROOT_SYSTEM]))

        raw_workflows = await self.driver.query("workflows", filters)
        workflows: list[Workflow] = []
        for w in raw_workflows:
            try:
                workflows.append(Workflow.model_validate(w, strict=False))
            except Exception as e:
                item_id = w["id"] if "id" in w else "unknown"
                logger.error(
                    "[WorkflowRepository] %s: Skipping corrupted workflow %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    item_id,
                    e,
                    exc_info=True,
                )
        return workflows

    async def get_workflow_by_id(self, workflow_id: str) -> Workflow | None:
        """Retrieves a workflow by ID from storage.

        Args:
            workflow_id: Unique identifier for the workflow.

        Returns:
            The validated Workflow domain model if found, otherwise None.
        """
        data = await self.driver.get("workflows", workflow_id)
        if not data:
            return None
        return Workflow.model_validate(data, strict=False)

    async def create_workflow(self, workflow_data: dict[str, Any]) -> str:
        """Creates a new workflow.

        Args:
            workflow_data: Dictionary containing workflow fields.

        Returns:
            The created workflow ID.
        """
        doc_id = workflow_data["id"]
        return await self.driver.upsert("workflows", workflow_data, doc_id)

    async def update_workflow(self, workflow_id: str, updates: dict[str, Any]) -> str:
        """Updates a workflow, creating a new versioned entry.

        Args:
            workflow_id: Unique identifier for the workflow to update.
            updates: Dictionary of fields to update.

        Returns:
            The new versioned workflow ID.

        Raises:
            WorkflowNotFoundError: If the existing workflow cannot be found.
        """
        old_doc = await self.driver.get("workflows", workflow_id)
        if not old_doc:
            raise WorkflowNotFoundError(workflow_id)

        await self.driver.update("workflows", workflow_id, {"is_latest": False})

        base_id, new_id, ver = self._increment_version(workflow_id)

        new_doc = dict(old_doc)
        new_doc.update(updates)
        new_doc["id"] = new_id
        new_doc["is_latest"] = True
        new_doc["version"] = ver
        new_doc["slug"] = base_id

        await self.driver.upsert("workflows", new_doc, new_id)
        return new_id

    async def update_workflow_definition(self, workflow_id: str, definition_data: dict[str, Any]) -> str:
        """Updates workflow definition.

        Args:
            workflow_id: Unique identifier for the workflow.
            definition_data: Dictionary of fields to update.

        Returns:
            The new versioned workflow ID.
        """
        return await self.update_workflow(workflow_id, definition_data)

    async def delete_workflow(self, workflow_id: str) -> bool:
        """Deletes a workflow by ID.

        Args:
            workflow_id: Unique identifier for the workflow.

        Returns:
            True if deleted, False otherwise.
        """
        return await self.driver.delete("workflows", workflow_id)

    async def count_workflows(self) -> int:
        """Counts total workflows in the database.

        Returns:
            Total workflow count.
        """
        return await self.driver.count("workflows")

    # --- Steps ---

    async def get_all_steps(self) -> list[Step]:
        """Retrieves all steps from storage.

        Returns:
            List of validated Step domain models.
        """
        data = await self.driver.query("steps")
        steps: list[Step] = []
        for s in data:
            try:
                steps.append(Step.model_validate(s, strict=False))
            except Exception as e:
                item_id = s["id"] if "id" in s else "unknown"
                logger.error(
                    "[WorkflowRepository] %s: Skipping corrupted step %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    item_id,
                    e,
                    exc_info=True,
                )
        return steps

    async def get_step_by_id(self, step_id: str) -> Step | None:
        """Retrieves a step by its ID.

        Args:
            step_id: Unique identifier for the step.

        Returns:
            The validated Step domain model if found, otherwise None.
        """
        step = await self.driver.get("steps", step_id)
        if step:
            return Step.model_validate(step, strict=False)

        all_wfs = await self.driver.query("workflows")
        for wf in all_wfs:
            if "steps" in wf and wf["steps"]:
                for s in wf["steps"]:
                    try:
                        validated_step = Step.model_validate(s, strict=False)
                        if validated_step.id == step_id:
                            return validated_step
                    except Exception:
                        continue
        return None

    async def get_step(self, step_id: str) -> Step | None:
        """Retrieves a step by ID.

        Args:
            step_id: Unique identifier for the step.

        Returns:
            The validated Step domain model if found, otherwise None.
        """
        return await self.get_step_by_id(step_id)

    async def create_step(self, step_data: dict[str, Any]) -> str:
        """Creates a new step.

        Args:
            step_data: Dictionary containing step fields.

        Returns:
            The created step ID.
        """
        doc_id = step_data["id"]
        return await self.driver.upsert("steps", step_data, doc_id)

    async def update_step(self, step_id: str, updates: dict[str, Any]) -> str:
        """Updates an existing step.

        Args:
            step_id: Unique identifier for the step.
            updates: Dictionary of fields to update.

        Returns:
            The step ID.
        """
        await self.driver.update("steps", step_id, updates)
        return step_id

    async def delete_step(self, step_id: str, force_delete: bool = False) -> bool:
        """Deletes a step by ID after verifying workflow usage.

        Args:
            step_id: Unique identifier for the step.
            force_delete: Whether to bypass workflow usage check.

        Returns:
            True if deleted, False if step does not exist.

        Raises:
            AppException: If step deletion is blocked by active workflow usage.
        """
        step = await self.driver.get("steps", step_id)
        if not step:
            return False

        if not force_delete:
            wfs = await self.get_all_workflows()
            for wf in wfs:
                for rule in wf.steps:
                    if rule.task_blueprint == step_id:
                        raise AppException(
                            message="Step delete blocked by workflow usage.",
                            details={
                                "error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value,
                                "step_id": step_id,
                                "workflow_id": wf.id,
                            },
                            status_code=400,
                        )

        return await self.driver.delete("steps", step_id)
