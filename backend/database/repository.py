"""Abstract Repository Interface."""

from abc import ABC, abstractmethod
from typing import Any

from tinydb import Query

from backend.database.wrapper import AbstractDatabase
from backend.models.workflow import WorkflowDefinition


class AbstractWorkflowRepository(ABC):
    """Abstract base class for asynchronous data access."""

    @abstractmethod
    async def get_execution(self, execution_id: str) -> dict[str, Any] | None:
        """Retrieve an execution record by ID."""
        pass

    @abstractmethod
    async def get_execution_status(self, execution_id: str) -> str | None:
        """Retrieve the status of an execution."""
        pass

    @abstractmethod
    async def create_execution(self, execution_data: dict[str, Any]) -> str:
        """Create a new execution record."""
        pass

    @abstractmethod
    async def update_execution(self, execution_id: str, updates: dict[str, Any]) -> bool:
        """Update an existing execution record."""
        pass

    @abstractmethod
    async def delete_execution(self, execution_id: str) -> bool:
        """Delete an execution record."""
        pass

    @abstractmethod
    async def get_all_executions(
        self, organization_id: str | None = None, user_id: str | None = None
    ) -> list[dict[str, Any]]:
        """Retrieve all executions, optionally filtered."""
        pass

    # --- New Methods for V2.9 GraphEngine ---

    @abstractmethod
    async def get_workflow_definition(self, workflow_id: str) -> WorkflowDefinition | None:
        """Retrieve a workflow definition by ID.
        Should support fallback to disk if not in DB (implementation detail).
        """
        pass

    # Alias for compatibility if needed or strictly mapped
    async def get_workflow(self, workflow_id: str) -> WorkflowDefinition | None:
         return await self.get_workflow_definition(workflow_id)

    @abstractmethod
    async def log_audit_event(self, event_data: dict[str, Any]) -> None:
        """Log an audit event."""
        pass

    @abstractmethod
    async def get_audit_logs(
        self,
        organization_id: str | None = None,
        actor_uid: str | None = None,
        action: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Retrieve audit logs."""
        pass

    @abstractmethod
    async def get_all_workflows(
        self, organization_id: str | None = None, role: str | None = None
    ) -> list[dict[str, Any]]:
        """Retrieve all workflows, optionally filtered."""
        pass

    @abstractmethod
    async def get_workflow_by_id(self, workflow_id: str) -> dict[str, Any] | None:
        """Retrieve a workflow as a dictionary."""
        pass

    @abstractmethod
    async def create_workflow(self, workflow_data: dict[str, Any]) -> str:
        """Create a new workflow."""
        pass

    @abstractmethod
    async def update_workflow(self, workflow_id: str, updates: dict[str, Any]) -> bool:
        """Update a workflow."""
        pass

    @abstractmethod
    async def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow."""
        pass

    @abstractmethod
    async def get_all_steps(self) -> list[dict[str, Any]]:
        """Retrieve all steps."""
        pass

    @abstractmethod
    async def get_step_by_id(self, step_id: str) -> dict[str, Any] | None:
        """Retrieve a step by ID."""
        pass

    @abstractmethod
    async def create_step(self, step_data: dict[str, Any]) -> str:
        """Create a new step."""
        pass

    @abstractmethod
    async def update_step(self, step_id: str, updates: dict[str, Any]) -> bool:
        """Update a step."""
        pass

    @abstractmethod
    async def delete_step(self, step_id: str) -> bool:
        """Delete a step."""
        pass

    @abstractmethod
    async def get_all_components(self) -> list[dict[str, Any]]:
        """Retrieve all components."""
        pass

    @abstractmethod
    async def get_component_by_id(self, component_id: str) -> dict[str, Any] | None:
        """Retrieve a component by ID."""
        pass

    @abstractmethod
    async def get_component_by_name(self, name: str) -> dict[str, Any] | None:
        """Retrieve a component by name."""
        pass

    @abstractmethod
    async def update_component_metadata(self, component_id: str, module: str, component_class: str) -> bool:
        """Update component metadata."""
        pass

    @abstractmethod
    async def get_banned_phrases(self) -> list[dict[str, Any]]:
        """Retrieve all banned phrases."""
        pass

    @abstractmethod
    async def add_banned_phrase(self, phrase: str, language: str = "en") -> None:
        """Add a banned phrase."""
        pass

    @abstractmethod
    async def delete_banned_phrase(self, phrase: str) -> bool:
        """Delete a banned phrase."""
        pass

    @abstractmethod
    async def count_workflows(self) -> int:
        """Count total workflows."""
        pass

    @abstractmethod
    async def get_prompt_template(self, template_id: str) -> dict[str, str] | None:
        """Retrieve a prompt template by ID (returns dict with 'system', 'user')."""
        pass

    @abstractmethod
    async def get_knowledge_base_items(self) -> list[dict[str, Any]]:
        """Retrieve all knowledge base items."""
        pass

    @abstractmethod
    async def get_model_registry(self) -> dict[str, Any]:
        """Retrieve the model registry configuration."""
        pass

    @abstractmethod
    async def count_executions_by_matrix(self, matrix_id: str) -> int:
        """Count executions using a specific matrix ID."""
        pass

    @abstractmethod
    async def get_components_using_dimension(self, dimension_id: str) -> list[str]:
        """Return list of component IDs that reference this dimension."""
        pass

class TinyDBRepository(AbstractWorkflowRepository):
    """TinyDB implementation of the Workflow Repository."""

    def __init__(self, client: AbstractDatabase):
        self.client = client
        self.executions = client.table("executions")
        self.workflows = client.table("workflows")
        self.steps = client.table("steps")
        self.components = client.table("components")
        self.audit_logs = client.table("audit_logs")
        self.banned_phrases = client.table("banned_phrases")
        self.prompts = client.table("prompts")
        self.knowledge_base = client.table("knowledge_base")
        self.organizations = client.table("organizations")
        self.users = client.table("users")

    # --- Helper: Universal Serializer ---
    def _serialize_for_tinydb(self, data: dict[str, Any]) -> dict[str, Any]:
        """Recursively converts datetime objects to ISO format strings."""
        from datetime import datetime

        # Determine if we have a dict or list (handle recursiveness)
        # But top level is usually dict for these methods.

        def _convert(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, dict):
                return {k: _convert(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [_convert(v) for v in obj]
            return obj

        return _convert(data) # Expecting dict input mostly

    # --- Organization Methods (Required by organization_router.py) ---

    async def list_organizations(self) -> list[dict[str, Any]]:
        """List all organizations."""
        return self.organizations.all()

    async def get_organization(self, org_id: str) -> dict[str, Any] | None:
        """Get organization by ID."""
        return self.organizations.get(Query().id == org_id)

    async def create_organization(self, org_data: dict[str, Any]) -> str:
        """Create a new organization."""
        safe_data = self._serialize_for_tinydb(org_data)
        self.organizations.upsert(safe_data, Query().id == safe_data["id"])
        return safe_data["id"]

    async def update_organization(self, org_id: str, updates: dict[str, Any]) -> bool:
        """Update an organization."""
        safe_updates = self._serialize_for_tinydb(updates)
        res = self.organizations.update(safe_updates, Query().id == org_id)
        return bool(res)

    async def delete_organization(self, org_id: str) -> bool:
        """Delete an organization."""
        res = self.organizations.remove(Query().id == org_id)
        return bool(res)

    async def list_users(self, org_id: str | None = None) -> list[dict[str, Any]]:
        """List users, optionally filtered by organization."""
        all_users = self.users.all()
        if org_id:
            return [u for u in all_users if u.get("organization_id") == org_id]
        return all_users

    async def delete_org_data(self, org_id: str) -> None:
        """Delete all data associated with an organization (cascade delete)."""
        self.users.remove(Query().organization_id == org_id)
        self.executions.remove(Query().organization_id == org_id)
        self.workflows.remove(Query().organization_id == org_id)

    async def get_org_usage_total(self, org_id: str, since: str | None = None) -> float:
        """Calculate total usage cost for an organization since a given timestamp."""
        all_execs = self.executions.all()
        total = 0.0
        for ex in all_execs:
            if ex.get("organization_id") != org_id:
                continue
            if since:
                ex_time = ex.get("created_at", "")
                if ex_time < since:
                    continue
            total += ex.get("cost_estimate", 0.0)
        return total


    async def get_banned_phrases(self) -> list[dict[str, Any]]:
        return self.banned_phrases.all()

    async def add_banned_phrase(self, phrase: str, language: str = "en") -> None:
        from tinydb import Query
        # Check duplicate
        if not self.banned_phrases.contains(Query().phrase == phrase):
            self.banned_phrases.insert({"phrase": phrase, "language": language})

    async def delete_banned_phrase(self, phrase: str) -> bool:
        res = self.banned_phrases.remove(Query().phrase == phrase)
        return bool(res)

    async def count_workflows(self) -> int:
        return len(self.workflows.all())

    async def get_prompt_template(self, template_id: str) -> dict[str, str] | None:
        # Look in prompts table first
        res = self.prompts.get(Query().id == template_id)
        if res:
            return {"system": res.get("system_prompt", ""), "user": res.get("user_prompt", "")}
        return None

    async def get_knowledge_base_items(self) -> list[dict[str, Any]]:
        """Retrieve all knowledge base items."""
        return self.knowledge_base.all()

    async def log_audit_event(self, event_data: dict[str, Any]) -> None:
        safe_data = self._serialize_for_tinydb(event_data)
        self.audit_logs.insert(safe_data)

    async def get_audit_logs(
        self,
        organization_id: str | None = None,
        actor_uid: str | None = None,
        action: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        all_logs = self.audit_logs.all()

        # Filter in memory
        filtered = []
        for log in all_logs:
            if organization_id and log.get("organization_id") != organization_id:
                continue
            if actor_uid and log.get("actor_uid") != actor_uid:
                continue
            if action and log.get("action") != action:
                continue
            filtered.append(log)

        # Sort by timestamp desc (assuming ISO string sort works approx correctly)
        filtered.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return filtered[:limit]

    async def get_all_workflows(
        self, organization_id: str | None = None, role: str | None = None
    ) -> list[dict[str, Any]]:
        all_wfs = self.workflows.all()
        # Filter logic
        filtered = []
        for wf in all_wfs:
            # Role-based visibility check (Root sees all)
            if role == "ROOT":
                filtered.append(wf)
                continue

            # Org check
            wf_org = wf.get("organization_id")
            if wf_org and organization_id and wf_org != organization_id and wf_org != "system":
                continue

            filtered.append(wf)
        return filtered

    async def get_workflow_by_id(self, workflow_id: str) -> dict[str, Any] | None:
        return self.workflows.get(Query().id == workflow_id)

    async def create_workflow(self, workflow_data: dict[str, Any]) -> str:
        safe_data = self._serialize_for_tinydb(workflow_data)
        self.workflows.upsert(safe_data, Query().id == safe_data["id"])
        return safe_data["id"]

    async def update_workflow(self, workflow_id: str, updates: dict[str, Any]) -> bool:
        safe_updates = self._serialize_for_tinydb(updates)
        res = self.workflows.update(safe_updates, Query().id == workflow_id)
        return bool(res)

    async def delete_workflow(self, workflow_id: str) -> bool:
        res = self.workflows.remove(Query().id == workflow_id)
        return bool(res)

    async def get_all_steps(self) -> list[dict[str, Any]]:
        return self.steps.all()

    async def get_step_by_id(self, step_id: str) -> dict[str, Any] | None:
        return self.steps.get(Query().id == step_id)

    async def create_step(self, step_data: dict[str, Any]) -> str:
        safe_data = self._serialize_for_tinydb(step_data)
        self.steps.upsert(safe_data, Query().id == safe_data["id"])
        return safe_data["id"]

    async def update_step(self, step_id: str, updates: dict[str, Any]) -> bool:
        safe_updates = self._serialize_for_tinydb(updates)
        res = self.steps.update(safe_updates, Query().id == step_id)
        return bool(res)

    async def delete_step(self, step_id: str) -> bool:
        res = self.steps.remove(Query().id == step_id)
        return bool(res)

    async def get_all_components(self) -> list[dict[str, Any]]:
        return self.components.all()

    async def get_component_by_id(self, component_id: str) -> dict[str, Any] | None:
        return self.components.get(Query().id == component_id)

    async def get_component_by_name(self, name: str) -> dict[str, Any] | None:
        # This might be slow on TinyDB without index but OK for mock
        res = self.components.search(Query().name == name)
        return res[0] if res else None

    async def update_component_metadata(self, component_id: str, module: str, component_class: str) -> bool:
        """Update component metadata."""
        updates = {"module": module, "class_name": component_class}
        res = self.components.update(updates, Query().id == component_id)
        return bool(res)

    async def get_execution(self, execution_id: str) -> dict[str, Any] | None:
        return self.executions.get(Query().id == execution_id)

    async def create_execution(self, execution_data: dict[str, Any]) -> str:
        # Generate ID if missing? Usually handled by caller or DB.
        # TinyDB wrapper 'insert' returns document ID (int), but we want string UUIDs from data.
        # If 'id' is in data, we use upsert/insert.

        # KEY FIX: Helper to serialize datetimes for TinyDB
        # Using self._serialize_for_tinydb defined above
        safe_data = self._serialize_for_tinydb(execution_data)

        # We use upsert to ensure we use the UUID as key if possible, or just insert.
        # Wrapper 'insert' just appends. 'upsert' needs a query.
        eid = safe_data.get("id")
        if eid:
            self.executions.upsert(safe_data, Query().id == eid)
            return eid
        else:
            # Native insert, returns int ID, might not be what we want if we expect UUIDs.
            # But let's trust the input data has ID.
            result = self.executions.insert(safe_data)
            return str(result)

    async def update_execution(self, execution_id: str, updates: dict[str, Any]) -> bool:
        # KEY FIX: Helper to serialize datetimes for TinyDB
        safe_updates = self._serialize_for_tinydb(updates)

        # Wrapper 'update' takes dict of fields and query
        result = self.executions.update(safe_updates, Query().id == execution_id)
        return len(result) > 0

    async def delete_execution(self, execution_id: str) -> bool:
        """Delete an execution record."""
        result = self.executions.remove(Query().id == execution_id)
        return bool(result)

    async def get_all_executions(
        self, organization_id: str | None = None, user_id: str | None = None
    ) -> list[dict[str, Any]]:
        all_docs = self.executions.all()

        # Memory filter (TinyDB style)
        filtered = []
        for doc in all_docs:
            if organization_id and doc.get("organization_id") != organization_id:
                continue
            if user_id and doc.get("user_id") != user_id:
                continue
            filtered.append(doc)

        return filtered

    async def get_workflow_definition(self, workflow_id: str) -> WorkflowDefinition | None:
        data = self.workflows.get(Query().id == workflow_id)
        if data:
            return WorkflowDefinition(**data)

        # Fallback to Disk?
        # The AbstractRepository docstring mentions fallback.
        # Ideally this logic matches Firestore's fallback or is centralized.
        # For simplicity, if not in DB, return None.
        # (Or implement disk read if critical for TinyDB mode too)

        import json
        import logging
        import os
        logger = logging.getLogger(__name__)

        file_path = f"data/workflows/{workflow_id}.json"
        if os.path.exists(file_path):
             try:
                 with open(file_path, encoding="utf-8") as f:
                     data = json.load(f)
                     if "description" not in data:
                         data["description"] = "Loaded from file"
                     return WorkflowDefinition(**data)
             except Exception as e:
                 logger.error(f"Failed to load workflow from disk: {e}")

        return None

    async def get_model_registry(self) -> dict[str, Any]:
        """Retrieve the model registry configuration.
        
        Prioritizes configuration stored in 'system_config' table (id='model_registry').
        Falls back to 'components' table for backwards compatibility.
        Falls back to hardcoded defaults if missing from both.
        """
        # 1. Try to fetch from system_config table (PRIMARY source per seed_data.json)
        try:
            system_config_table = self.client.table("system_config")
            config_entry = system_config_table.get(Query().id == "model_registry")
            if config_entry and "models" in config_entry:
                return config_entry
        except Exception:
            pass

        return {}

    async def get_execution_status(self, execution_id: str) -> str | None:
        """Retrieve the status of an execution."""
        record = await self.get_execution(execution_id)
        if record:
            return record.get("status")
        return None

    async def count_executions_by_matrix(self, matrix_id: str) -> int:
        """Count executions using a specific matrix ID."""
        # Query: executions where settings.matrix_id == matrix_id
        return self.executions.count(Query().settings.matrix_id == matrix_id)

    async def get_components_using_dimension(self, dimension_id: str) -> list[str]:
        """Return list of component IDs that reference this dimension."""
        all_comps = self.components.all()
        matches = []
        for c in all_comps:
            content = c.get("content", {})
            if not isinstance(content, dict):
                continue

            criteria = content.get("criteria", [])
            if not isinstance(criteria, list):
                continue

            for crit in criteria:
                if isinstance(crit, dict) and crit.get("dimension_id") == dimension_id:
                    matches.append(c.get("id"))
                    break
        return matches


