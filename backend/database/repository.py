"""Unified Repository Implementation.

This module implements the 'Storage Driver Pattern' (V2.9/V2026).
Business logic is written ONCE in UnifiedWorkflowRepository and delegates
I/O to the injected StorageDriver.
"""

import logging
import uuid
from abc import ABC, abstractmethod
from typing import Any

from backend.database.driver import Filter, StorageDriver
from backend.models.workflow import WorkflowDefinition

logger = logging.getLogger(__name__)


class AbstractWorkflowRepository(ABC):
    """Abstract base class for asynchronous data access.
    
    Kept for dependency injection compatibility.
    """

    @abstractmethod
    async def get_execution(self, execution_id: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    async def get_execution_status(self, execution_id: str) -> str | None:
        pass

    @abstractmethod
    async def create_execution(self, execution_data: dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def update_execution(self, execution_id: str, updates: dict[str, Any]) -> bool:
        pass

    @abstractmethod
    async def delete_execution(self, execution_id: str) -> bool:
        pass

    @abstractmethod
    async def get_all_executions(
        self, organization_id: str | None = None, user_id: str | None = None
    ) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def get_workflow_definition(self, workflow_id: str) -> WorkflowDefinition | None:
        pass

    async def get_workflow(self, workflow_id: str) -> WorkflowDefinition | None:
        return await self.get_workflow_definition(workflow_id)

    @abstractmethod
    async def log_audit_event(self, event_data: dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def get_audit_logs(
        self,
        organization_id: str | None = None,
        actor_uid: str | None = None,
        action: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def get_all_workflows(
        self, organization_id: str | None = None, role: str | None = None
    ) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def get_workflow_by_id(self, workflow_id: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    async def create_workflow(self, workflow_data: dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def update_workflow(self, workflow_id: str, updates: dict[str, Any]) -> bool:
        pass

    @abstractmethod
    async def delete_workflow(self, workflow_id: str) -> bool:
        pass

    @abstractmethod
    async def get_all_steps(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def get_step_by_id(self, step_id: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    async def create_step(self, step_data: dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def update_step(self, step_id: str, updates: dict[str, Any]) -> bool:
        pass

    @abstractmethod
    async def delete_step(self, step_id: str) -> bool:
        pass

    @abstractmethod
    async def get_all_components(
        self, type: str | None = None, exclude_types: list[str] | None = None
    ) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def get_component_by_id(self, component_id: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    async def get_component_by_name(self, name: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    async def update_component_metadata(self, component_id: str, module: str, component_class: str) -> bool:
        pass

    @abstractmethod
    async def register_component(self, component_data: dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def get_banned_phrases(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def add_banned_phrase(self, phrase: str, language: str = "en") -> None:
        pass

    @abstractmethod
    async def delete_banned_phrase(self, phrase: str) -> bool:
        pass

    @abstractmethod
    async def count_workflows(self) -> int:
        pass

    @abstractmethod
    async def get_prompt_template(self, template_id: str) -> dict[str, str] | None:
        pass

    @abstractmethod
    async def get_knowledge_base_items(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def clear_knowledge_base(self) -> None:
        pass

    @abstractmethod
    async def get_model_registry(self) -> dict[str, Any]:
        pass

    @abstractmethod
    async def update_model_registry(self, registry_data: dict[str, Any]) -> bool:
        pass

    @abstractmethod
    async def count_executions_by_matrix(self, matrix_id: str) -> int:
        pass

    @abstractmethod
    async def get_components_using_dimension(self, dimension_id: str) -> list[str]:
        pass

    @abstractmethod
    async def log_usage(self, record: Any) -> None:
        pass

    @abstractmethod
    async def list_organizations(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def get_organization(self, org_id: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    async def create_organization(self, org_data: dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def update_organization(self, org_id: str, updates: dict[str, Any]) -> bool:
        pass

    @abstractmethod
    async def delete_organization(self, org_id: str) -> bool:
        pass

    @abstractmethod
    async def list_users(self, org_id: str | None = None) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def delete_org_data(self, org_id: str) -> None:
        pass

    @abstractmethod
    async def get_org_usage_total(self, org_id: str, since: str | None = None) -> float:
        pass

    @abstractmethod
    async def add_knowledge_base_item(self, item: dict[str, Any]) -> str:
        """Adds an item to the knowledge base collection.

        Args:
            item: The knowledge base item to add. Must contain an 'id' field.

        Returns:
            The ID of the added item.
        """
        pass


class UnifiedWorkflowRepository(AbstractWorkflowRepository):
    """Unified implementation using the StorageDriver pattern.
    
    This replaces both TinyDBRepository and FirestoreWorkflowRepository.
    """

    def __init__(self, driver: StorageDriver):
        self.driver = driver

    # --- Executions ---

    async def get_execution(self, execution_id: str) -> dict[str, Any] | None:
        return await self.driver.get("executions", execution_id)

    async def get_execution_status(self, execution_id: str) -> str | None:
        exec_data = await self.get_execution(execution_id)
        return exec_data.get("status") if exec_data else None

    async def create_execution(self, execution_data: dict[str, Any]) -> str:
        doc_id = execution_data.get("id") or str(uuid.uuid4())
        execution_data["id"] = doc_id
        return await self.driver.upsert("executions", execution_data, doc_id)

    async def update_execution(self, execution_id: str, updates: dict[str, Any]) -> bool:
        return await self.driver.update("executions", execution_id, updates)

    async def delete_execution(self, execution_id: str) -> bool:
        return await self.driver.delete("executions", execution_id)

    async def get_all_executions(
        self, organization_id: str | None = None, user_id: str | None = None
    ) -> list[dict[str, Any]]:
        filters = []
        if organization_id:
            filters.append(Filter("organization_id", "==", organization_id))
        if user_id:
            filters.append(Filter("user_id", "==", user_id))

        return await self.driver.query("executions", filters)

    # --- Workflows ---

    async def get_workflow_definition(self, workflow_id: str) -> WorkflowDefinition | None:
        """Hydrates workflow with steps from registry."""
        data = await self.driver.get("workflows", workflow_id)

        # Disk Fallback (Critical for Dev)
        if not data:
            import json
            import os
            file_path = f"data/workflows/{workflow_id}.json"
            if os.path.exists(file_path):
                try:
                    with open(file_path, encoding="utf-8") as f:
                        data = json.load(f)
                        if "description" not in data:
                            data["description"] = "Loaded from file"
                except Exception as e:
                    logger.error(f"Failed to load workflow from disk: {e}")
                    return None
            else:
                return None

        # Hydrate steps from Registry
        if "steps" in data and isinstance(data["steps"], list):
            # Fetch all steps for hydration
            # Optimization: Could cache steps or fetch by ID if driver supports 'in'
            # For now fetch all is safer for small step counts
            all_steps = await self.driver.query("steps")
            registry_steps = {s["id"]: s for s in all_steps if "id" in s}

            hydrated = []
            for step in data["steps"]:
                sid = step.get("id")
                if sid and sid in registry_steps:
                    merged = registry_steps[sid].copy()
                    merged.update(step)
                    hydrated.append(merged)
                else:
                    hydrated.append(step)
            data["steps"] = hydrated

        return WorkflowDefinition(**data)

    async def log_audit_event(self, event_data: dict[str, Any]) -> None:
        doc_id = event_data.get("id") or str(uuid.uuid4())
        event_data["id"] = doc_id
        await self.driver.upsert("audit_logs", event_data, doc_id)

    async def get_audit_logs(
        self,
        organization_id: str | None = None,
        actor_uid: str | None = None,
        action: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        filters = []
        if organization_id:
            filters.append(Filter("organization_id", "==", organization_id))
        if actor_uid:
            filters.append(Filter("actor_uid", "==", actor_uid))
        if action:
            filters.append(Filter("action", "==", action))

        return await self.driver.query(
            "audit_logs",
            filters=filters,
            limit=limit,
            order_by="timestamp",
            descending=True
        )

    async def get_all_workflows(
        self, organization_id: str | None = None, role: str | None = None
    ) -> list[dict[str, Any]]:
        filters = []
        if role != "ROOT":
            if organization_id:
                # Logic: org_id IN [target, "system"]
                # Driver support 'in'? Yes.
                filters.append(Filter("organization_id", "in", [organization_id, "system"]))

        return await self.driver.query("workflows", filters)

    async def get_workflow_by_id(self, workflow_id: str) -> dict[str, Any] | None:
        return await self.driver.get("workflows", workflow_id)

    async def create_workflow(self, workflow_data: dict[str, Any]) -> str:
        doc_id = workflow_data["id"]
        return await self.driver.upsert("workflows", workflow_data, doc_id)

    async def update_workflow(self, workflow_id: str, updates: dict[str, Any]) -> bool:
        return await self.driver.update("workflows", workflow_id, updates)

    async def delete_workflow(self, workflow_id: str) -> bool:
        return await self.driver.delete("workflows", workflow_id)

    # --- Steps ---

    async def get_all_steps(self) -> list[dict[str, Any]]:
        return await self.driver.query("steps")

    async def get_step_by_id(self, step_id: str) -> dict[str, Any] | None:
        step = await self.driver.get("steps", step_id)
        if step:
            return step

        # Fallback: Check inside workflows (V2 pattern)
        all_wfs = await self.driver.query("workflows")
        for wf in all_wfs:
            steps = wf.get("steps", [])
            if not isinstance(steps, list):
                continue
            for s in steps:
                if isinstance(s, dict) and s.get("id") == step_id:
                    return s
        return None

    async def create_step(self, step_data: dict[str, Any]) -> str:
        doc_id = step_data["id"]
        return await self.driver.upsert("steps", step_data, doc_id)

    async def update_step(self, step_id: str, updates: dict[str, Any]) -> bool:
        return await self.driver.update("steps", step_id, updates)

    async def delete_step(self, step_id: str) -> bool:
        return await self.driver.delete("steps", step_id)

    # --- Components ---

    async def get_all_components(
        self, type: str | None = None, exclude_types: list[str] | None = None
    ) -> list[dict[str, Any]]:
        filters = []
        if type:
            filters.append(Filter("type", "==", type))

        components = await self.driver.query("components", filters)

        if exclude_types:
            components = [c for c in components if c.get("type") not in exclude_types]

        return components

    async def get_component_by_id(self, component_id: str) -> dict[str, Any] | None:
        return await self.driver.get("components", component_id)

    async def get_component_by_name(self, name: str) -> dict[str, Any] | None:
        res = await self.driver.query("components", [Filter("name", "==", name)], limit=1)
        return res[0] if res else None

    async def update_component_metadata(self, component_id: str, module: str, component_class: str) -> bool:
        return await self.driver.update(
            "components",
            component_id,
            {"module": module, "class_name": component_class}
        )

    async def register_component(self, component_data: dict[str, Any]) -> str:
        doc_id = component_data["id"]
        return await self.driver.upsert("components", component_data, doc_id)

    # --- Banned Phrases ---

    async def get_banned_phrases(self) -> list[dict[str, Any]]:
        return await self.driver.query("banned_phrases")

    async def add_banned_phrase(self, phrase: str, language: str = "en") -> None:
        # Check duplicate
        existing = await self.driver.query("banned_phrases", [Filter("phrase", "==", phrase)], limit=1)
        if not existing:
            doc_id = str(uuid.uuid4())
            await self.driver.upsert(
                "banned_phrases",
                {"phrase": phrase, "language": language, "id": doc_id},
                doc_id
            )

    async def delete_banned_phrase(self, phrase: str) -> bool:
        existing = await self.driver.query("banned_phrases", [Filter("phrase", "==", phrase)], limit=1)
        if existing:
            return await self.driver.delete("banned_phrases", existing[0]["id"])
        return False

    # --- Metrics & Usage ---

    async def count_workflows(self) -> int:
        return await self.driver.count("workflows")

    async def get_prompt_template(self, template_id: str) -> dict[str, str] | None:
        # Check prompts table
        res = await self.driver.get("prompts", template_id)
        if res:
             return {"system": res.get("system_prompt", ""), "user": res.get("user_prompt", "")}

        # Fallback query by 'id' field if doc_id mismatch
        res_list = await self.driver.query("prompts", [Filter("id", "==", template_id)], limit=1)
        if res_list:
             res = res_list[0]
             return {"system": res.get("system_prompt", ""), "user": res.get("user_prompt", "")}

        return None

    async def get_knowledge_base_items(self) -> list[dict[str, Any]]:
        return await self.driver.query("knowledge_base")

    async def add_knowledge_base_item(self, item: dict[str, Any]) -> str:
        """Adds an item to the knowledge base collection."""
        doc_id = item["id"]
        return await self.driver.upsert("knowledge_base", item, doc_id)

    async def clear_knowledge_base(self) -> None:
        """Removes all items from the knowledge base collection."""
        items = await self.driver.query("knowledge_base")
        for item in items:
            await self.driver.delete("knowledge_base", item["id"])

    async def get_model_registry(self) -> dict[str, Any]:
        # Config stored in system_config/model_registry
        return await self.driver.get("system_config", "model_registry") or {}

    async def update_model_registry(self, registry_data: dict[str, Any]) -> bool:
        registry_data["id"] = "model_registry"
        await self.driver.upsert("system_config", registry_data, "model_registry")
        return True

    async def count_executions_by_matrix(self, matrix_id: str) -> int:
        # Filter on nested field? StorageDriver must support dot notation if backend does.
        # TinyDB supports it via Access. Firestore supports string paths.
        return await self.driver.count("executions", [Filter("settings.matrix_id", "==", matrix_id)])

    async def get_components_using_dimension(self, dimension_id: str) -> list[str]:
        # Complex logic: scan components in memory
        # Fetch Matrix types
        matrices = await self.get_all_components(type="evaluation_matrix")

        matches = []
        for m in matrices:
            content = m.get("content", {})
            if not isinstance(content, dict): continue
            criteria = content.get("criteria", [])
            if not isinstance(criteria, list): continue

            for crit in criteria:
                 if isinstance(crit, dict) and crit.get("dimension_id") == dimension_id:
                     matches.append(m["id"])
                     break
        return matches

    async def log_usage(self, record: Any) -> None:
        if hasattr(record, "model_dump"):
            data = record.model_dump()
        else:
            data = record

        doc_id = data.get("id") or str(uuid.uuid4())
        data["id"] = doc_id
        await self.driver.upsert("usage", data, doc_id)

    # --- Organizations ---

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

    async def delete_org_data(self, org_id: str) -> None:
        # Manual cascade delete - driver doesn't support batch delete by query yet
        # Phase 2 improvement: add delete_by_query to protocol?
        # For now, fetch and delete one by one or iterate

        # Users
        users = await self.list_users(org_id)
        for u in users:
            await self.driver.delete("users", u["id"])

        # Executions
        execs = await self.get_all_executions(organization_id=org_id)
        for e in execs:
            await self.driver.delete("executions", e["id"])

        # Workflows
        wfs = await self.get_all_workflows(organization_id=org_id)
        for w in wfs:
            await self.driver.delete("workflows", w["id"])

    async def get_org_usage_total(self, org_id: str, since: str | None = None) -> float:
        filters = [Filter("organization_id", "==", org_id)]
        if since:
            filters.append(Filter("created_at", ">=", since))

        # Fetch all matched executions
        execs = await self.driver.query("executions", filters)
        return sum(e.get("cost_estimate", 0.0) for e in execs)
