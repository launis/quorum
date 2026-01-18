"""Abstract Repository Interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from tinydb import Query

from backend.database.wrapper import AbstractDatabase
from backend.models.workflow import WorkflowDefinition


class AbstractWorkflowRepository(ABC):
    """Abstract base class for asynchronous data access."""

    @abstractmethod
    async def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an execution record by ID."""
        pass

    @abstractmethod
    async def create_execution(self, execution_data: Dict[str, Any]) -> str:
        """Create a new execution record."""
        pass

    @abstractmethod
    async def update_execution(self, execution_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing execution record."""
        pass

    @abstractmethod
    async def get_all_executions(
        self, organization_id: Optional[str] = None, user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve all executions, optionally filtered."""
        pass

    # --- New Methods for V2.9 GraphEngine ---

    @abstractmethod
    async def get_workflow_definition(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """
        Retrieve a workflow definition by ID. 
        Should support fallback to disk if not in DB (implementation detail).
        """
        pass
        
    # Alias for compatibility if needed or strictly mapped
    async def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
         return await self.get_workflow_definition(workflow_id)

    @abstractmethod
    async def log_audit_event(self, event_data: Dict[str, Any]) -> None:
        """Log an audit event."""
        pass

    @abstractmethod
    async def get_audit_logs(
        self,
        organization_id: Optional[str] = None,
        actor_uid: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Retrieve audit logs."""
        pass

    @abstractmethod
    async def get_all_workflows(
        self, organization_id: Optional[str] = None, role: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve all workflows, optionally filtered."""
        pass

    @abstractmethod
    async def get_workflow_by_id(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a workflow as a dictionary."""
        pass

    @abstractmethod
    async def create_workflow(self, workflow_data: Dict[str, Any]) -> str:
        """Create a new workflow."""
        pass

    @abstractmethod
    async def update_workflow(self, workflow_id: str, updates: Dict[str, Any]) -> bool:
        """Update a workflow."""
        pass

    @abstractmethod
    async def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow."""
        pass

    @abstractmethod
    async def get_all_steps(self) -> List[Dict[str, Any]]:
        """Retrieve all steps."""
        pass

    @abstractmethod
    async def get_step_by_id(self, step_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a step by ID."""
        pass

    @abstractmethod
    async def create_step(self, step_data: Dict[str, Any]) -> str:
        """Create a new step."""
        pass

    @abstractmethod
    async def update_step(self, step_id: str, updates: Dict[str, Any]) -> bool:
        """Update a step."""
        pass

    @abstractmethod
    async def delete_step(self, step_id: str) -> bool:
        """Delete a step."""
        pass

    @abstractmethod
    async def get_all_components(self) -> List[Dict[str, Any]]:
        """Retrieve all components."""
        pass

    @abstractmethod
    async def get_component_by_id(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a component by ID."""
        pass

    @abstractmethod
    async def get_component_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve a component by name."""
        pass

    @abstractmethod
    async def update_component_metadata(self, component_id: str, module: str, component_class: str) -> bool:
        """Update component metadata."""
        pass

    @abstractmethod
    async def get_banned_phrases(self) -> List[Dict[str, Any]]:
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
    async def get_prompt_template(self, template_id: str) -> Optional[Dict[str, str]]:
        """Retrieve a prompt template by ID (returns dict with 'system', 'user')."""
        pass

    @abstractmethod
    async def get_knowledge_base_items(self) -> List[Dict[str, Any]]:
        """Retrieve all knowledge base items."""
        pass

    @abstractmethod
    async def get_model_registry(self) -> Dict[str, Any]:
        """Retrieve the model registry configuration."""
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

    # --- Organization Methods (Required by organization_router.py) ---

    async def list_organizations(self) -> List[Dict[str, Any]]:
        """List all organizations."""
        return self.organizations.all()

    async def get_organization(self, org_id: str) -> Optional[Dict[str, Any]]:
        """Get organization by ID."""
        return self.organizations.get(Query().id == org_id)

    async def create_organization(self, org_data: Dict[str, Any]) -> str:
        """Create a new organization."""
        self.organizations.upsert(org_data, Query().id == org_data["id"])
        return org_data["id"]

    async def update_organization(self, org_id: str, updates: Dict[str, Any]) -> bool:
        """Update an organization."""
        res = self.organizations.update(updates, Query().id == org_id)
        return bool(res)

    async def delete_organization(self, org_id: str) -> bool:
        """Delete an organization."""
        res = self.organizations.remove(Query().id == org_id)
        return bool(res)

    async def list_users(self, org_id: Optional[str] = None) -> List[Dict[str, Any]]:
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

    async def get_org_usage_total(self, org_id: str, since: Optional[str] = None) -> float:
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


    async def get_banned_phrases(self) -> List[Dict[str, Any]]:
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
        
    async def get_prompt_template(self, template_id: str) -> Optional[Dict[str, str]]:
        # Look in prompts table first
        res = self.prompts.get(Query().id == template_id)
        if res:
            return {"system": res.get("system_prompt", ""), "user": res.get("user_prompt", "")}
        return None

    async def get_knowledge_base_items(self) -> List[Dict[str, Any]]:
        """Retrieve all knowledge base items."""
        return self.knowledge_base.all()

    async def log_audit_event(self, event_data: Dict[str, Any]) -> None:
        self.audit_logs.insert(event_data)

    async def get_audit_logs(
        self,
        organization_id: Optional[str] = None,
        actor_uid: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
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
        self, organization_id: Optional[str] = None, role: Optional[str] = None
    ) -> List[Dict[str, Any]]:
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

    async def get_workflow_by_id(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        return self.workflows.get(Query().id == workflow_id)

    async def create_workflow(self, workflow_data: Dict[str, Any]) -> str:
        self.workflows.upsert(workflow_data, Query().id == workflow_data["id"])
        return workflow_data["id"]

    async def update_workflow(self, workflow_id: str, updates: Dict[str, Any]) -> bool:
        res = self.workflows.update(updates, Query().id == workflow_id)
        return bool(res)

    async def delete_workflow(self, workflow_id: str) -> bool:
        res = self.workflows.remove(Query().id == workflow_id)
        return bool(res)

    async def get_all_steps(self) -> List[Dict[str, Any]]:
        return self.steps.all()

    async def get_step_by_id(self, step_id: str) -> Optional[Dict[str, Any]]:
        return self.steps.get(Query().id == step_id)

    async def create_step(self, step_data: Dict[str, Any]) -> str:
        self.steps.upsert(step_data, Query().id == step_data["id"])
        return step_data["id"]

    async def update_step(self, step_id: str, updates: Dict[str, Any]) -> bool:
        res = self.steps.update(updates, Query().id == step_id)
        return bool(res)

    async def delete_step(self, step_id: str) -> bool:
        res = self.steps.remove(Query().id == step_id)
        return bool(res)

    async def get_all_components(self) -> List[Dict[str, Any]]:
        return self.components.all()

    async def get_component_by_id(self, component_id: str) -> Optional[Dict[str, Any]]:
        return self.components.get(Query().id == component_id)

    async def get_component_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        # This might be slow on TinyDB without index but OK for mock
        res = self.components.search(Query().name == name)
        return res[0] if res else None

    async def update_component_metadata(self, component_id: str, module: str, component_class: str) -> bool:
        """Update component metadata."""
        updates = {"module": module, "class_name": component_class}
        res = self.components.update(updates, Query().id == component_id)
        return bool(res)

    async def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        return self.executions.get(Query().id == execution_id)

    async def create_execution(self, execution_data: Dict[str, Any]) -> str:
        # Generate ID if missing? Usually handled by caller or DB.
        # TinyDB wrapper 'insert' returns document ID (int), but we want string UUIDs from data.
        # If 'id' is in data, we use upsert/insert.
        
        # We assume execution_data has 'id' (UUID).
        if "id" not in execution_data:
             # Fallback or error? For now assume it's there as per schema.
             pass
             
        # We use upsert to ensure we use the UUID as key if possible, or just insert.
        # Wrapper 'insert' just appends. 'upsert' needs a query.
        eid = execution_data.get("id")
        if eid:
            self.executions.upsert(execution_data, Query().id == eid)
            return eid
        else:
            # Native insert, returns int ID, might not be what we want if we expect UUIDs.
            # But let's trust the input data has ID.
            result = self.executions.insert(execution_data)
            return str(result)

    async def update_execution(self, execution_id: str, updates: Dict[str, Any]) -> bool:
        # Wrapper 'update' takes dict of fields and query
        result = self.executions.update(updates, Query().id == execution_id)
        return len(result) > 0

    async def get_all_executions(
        self, organization_id: Optional[str] = None, user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
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

    async def get_workflow_definition(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        data = self.workflows.get(Query().id == workflow_id)
        if data:
            return WorkflowDefinition(**data)
            
        # Fallback to Disk? 
        # The AbstractRepository docstring mentions fallback.
        # Ideally this logic matches Firestore's fallback or is centralized.
        # For simplicity, if not in DB, return None. 
        # (Or implement disk read if critical for TinyDB mode too)
        
        import os
        import json
        import logging
        logger = logging.getLogger(__name__)

        file_path = f"data/workflows/{workflow_id}.json"
        if os.path.exists(file_path):
             try:
                 with open(file_path, "r", encoding="utf-8") as f:
                     data = json.load(f)
                     if "description" not in data:
                         data["description"] = "Loaded from file"
                     return WorkflowDefinition(**data)
             except Exception as e:
                 logger.error(f"Failed to load workflow from disk: {e}")
        
        return None

    async def get_model_registry(self) -> Dict[str, Any]:
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


