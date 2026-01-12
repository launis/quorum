"""Firestore Repository implementation."""

import logging
from typing import Any

from google.cloud.firestore import AsyncClient, FieldFilter, Query

from backend.database.repository import AbstractWorkflowRepository

logger = logging.getLogger(__name__)


class FirestoreWorkflowRepository(AbstractWorkflowRepository):
    """Firestore Implementation of the Workflow Repository.

    Native Async Implementation using google-cloud-firestore.
    Expects an injected AsyncClient.
    """

    def __init__(self, client: AsyncClient):
        """Initialize Firestore Repo with injected AsyncClient."""
        self.db = client

    # --- Core Helpers ---
    async def _get_doc(self, collection: str, doc_id: str) -> dict[str, Any] | None:
        """Get document helper."""
        doc = await self.db.collection(collection).document(str(doc_id)).get()
        if doc.exists:
            return doc.to_dict()
        return None

    async def _find_one_by_field(self, collection: str, field: str, value: Any) -> dict[str, Any] | None:
        """Find one document by field."""
        docs = self.db.collection(collection).where(filter=FieldFilter(field, "==", value)).limit(1).stream()
        async for doc in docs:
            return doc.to_dict()
        return None

    async def _get_all(self, collection: str) -> list[dict[str, Any]]:
        """Get all documents helper."""
        docs = self.db.collection(collection).stream()
        return [doc.to_dict() async for doc in docs]

    async def _delete_doc(self, collection: str, doc_key: str, doc_value: str):
        """Delete document helper."""
        docs = self.db.collection(collection).where(filter=FieldFilter(doc_key, "==", doc_value)).stream()
        async for doc in docs:
            await doc.reference.delete()

    async def _update_doc(self, collection: str, doc_key: str, doc_value: str, updates: dict[str, Any]):
        """Update document helper."""
        docs = self.db.collection(collection).where(filter=FieldFilter(doc_key, "==", doc_value)).stream()
        async for doc in docs:
            await doc.reference.update(updates)

    # --- Components ---
    async def get_component_by_id(self, component_id: str) -> dict[str, Any] | None:
        """Get component by ID."""
        # Strategy 1: Direct Lookup by Doc ID
        doc = await self._get_doc("components", component_id)
        if doc:
            doc["id"] = component_id  # Ensure ID is present
            return doc
        # Strategy 2: Search by field 'id' (legacy/imported data)
        return await self._find_one_by_field("components", "id", component_id)

    async def get_component_by_name(self, name: str) -> dict[str, Any] | None:
        """Get component by name."""
        return await self._find_one_by_field("components", "name", name)

    async def register_component(self, component_data: dict[str, Any]):
        """Register a new component."""
        doc_id = component_data.get("id", component_data.get("name"))
        if doc_id:
            await self.db.collection("components").document(doc_id).set(component_data)
        else:
            await self.db.collection("components").add(component_data)

    async def update_component_metadata(self, name: str, module: str, component_class: str):
        """Update component metadata."""
        await self._update_doc("components", "name", name, {"module": module, "class": component_class})

    async def get_all_components(self) -> list[dict[str, Any]]:
        """Get all components."""
        return await self._get_all("components")

    # --- Steps ---
    async def get_step_by_id(self, step_id: str) -> dict[str, Any] | None:
        """Get step by ID."""
        # Strategy 1: Direct Lookup by Doc ID
        doc = await self._get_doc("steps", step_id)
        if doc:
            doc["id"] = step_id
            return doc
        return await self._find_one_by_field("steps", "id", step_id)

    async def get_all_steps(self) -> list[dict[str, Any]]:
        """Get all steps."""
        return await self._get_all("steps")

    async def create_step(self, step_data: dict[str, Any]) -> str:
        """Create step."""
        s_id = step_data.get("id")
        if s_id:
            await self.db.collection("steps").document(str(s_id)).set(step_data)
            return s_id
        else:
            _, ref = await self.db.collection("steps").add(step_data)
            return ref.id

    async def update_step(self, step_id: str, updates: dict[str, Any]):
        """Update step."""
        await self._update_doc("steps", "id", step_id, updates)

    async def delete_step(self, step_id: str):
        """Delete step."""
        await self._delete_doc("steps", "id", step_id)

    # --- Workflows ---
    async def get_workflow_by_id(self, workflow_id: str) -> dict[str, Any] | None:
        """Get workflow by ID."""
        # Strategy 1: Direct Lookup by Doc ID
        doc = await self._get_doc("workflows", workflow_id)
        if doc:
            doc["id"] = workflow_id
            return doc
        return await self._find_one_by_field("workflows", "id", workflow_id)

    async def create_workflow(self, workflow_data: dict[str, Any]) -> int | str:
        """Create workflow."""
        wf_id = workflow_data.get("id")
        if wf_id:
            await self.db.collection("workflows").document(str(wf_id)).set(workflow_data)
            return wf_id
        else:
            _, doc_ref = await self.db.collection("workflows").add(workflow_data)
            return doc_ref.id

    async def get_all_workflows(
        self, organization_id: str | None = None, role: str | None = None
    ) -> list[dict[str, Any]]:
        """Get all workflows."""
        # Root View: See EVERYTHING
        if role == "ROOT":
            return await self._get_all("workflows")

        if organization_id:
            docs = (
                self.db.collection("workflows")
                .where(filter=FieldFilter("organization_id", "==", organization_id))
                .stream()
            )
            return [doc.to_dict() async for doc in docs]

        return await self._get_all("workflows")

    async def update_workflow(self, workflow_id: str, updates: dict[str, Any]):
        """Update workflow."""
        await self._update_doc("workflows", "id", workflow_id, updates)

    async def delete_workflow(self, workflow_id: str):
        """Delete workflow."""
        await self._delete_doc("workflows", "id", workflow_id)

    # --- Executions ---
    async def create_execution(self, execution_data: dict[str, Any]) -> int | str:
        """Create execution."""
        exec_id = execution_data.get("execution_id")
        if exec_id:
            await self.db.collection("executions").document(str(exec_id)).set(execution_data)
            return exec_id
        else:
            _, doc_ref = await self.db.collection("executions").add(execution_data)
            return doc_ref.id

    async def get_execution(self, execution_id: str) -> dict[str, Any] | None:
        """Get execution."""
        doc = await self.db.collection("executions").document(str(execution_id)).get()
        if doc.exists:
            return doc.to_dict()
        return await self._find_one_by_field("executions", "execution_id", execution_id)

    async def update_execution(self, execution_id: str, updates: dict[str, Any]):
        """Update execution."""
        doc_ref = self.db.collection("executions").document(str(execution_id))
        snp = await doc_ref.get()
        if snp.exists:
            await doc_ref.update(updates)
        else:
            await self._update_doc("executions", "execution_id", str(execution_id), updates)

    async def get_all_executions(
        self, organization_id: str | None = None, user_id: str | None = None
    ) -> list[dict[str, Any]]:
        """Get all executions."""
        query = self.db.collection("executions")

        if organization_id:
            query = query.where(filter=FieldFilter("organization_id", "==", organization_id))

        if user_id:
            query = query.where(filter=FieldFilter("user_id", "==", user_id))

        docs = query.stream()
        return [doc.to_dict() async for doc in docs]

    # --- Config ---
    async def get_model_registry(self) -> dict[str, Any] | None:
        """Get model registry."""
        return await self._find_one_by_field("system_config", "type", "model_registry")

    async def get_banned_phrases(self) -> list[dict[str, Any]]:
        """Get banned phrases."""
        return await self._get_all("banned_phrases")

    async def add_banned_phrase(self, phrase: str, **kwargs):
        """Add banned phrase."""
        existing = await self._find_one_by_field("banned_phrases", "phrase", phrase)
        if not existing:
            data = {"phrase": phrase}
            data.update(kwargs)
            await self.db.collection("banned_phrases").add(data)

    async def remove_banned_phrase(self, phrase: str):
        """Remove banned phrase."""
        await self._delete_doc("banned_phrases", "phrase", phrase)

    # --- Knowledge Base ---
    async def get_knowledge_base_items(self) -> list[dict[str, Any]]:
        """Get all KB items."""
        return await self._get_all("knowledge_base")

    async def add_knowledge_base_item(self, item_data: dict[str, Any]):
        """Add KB item."""
        await self.db.collection("knowledge_base").add(item_data)

    async def clear_knowledge_base(self):
        """Clear KB."""
        docs = self.db.collection("knowledge_base").limit(500).stream()
        async for doc in docs:
            await doc.reference.delete()

    # --- Organization Management ---
    async def create_organization(self, org_data: dict[str, Any]) -> str:
        """Create organization."""
        org_id = org_data.get("id")
        if org_id:
            await self.db.collection("organizations").document(str(org_id)).set(org_data)
            return org_id
        else:
            _, doc_ref = await self.db.collection("organizations").add(org_data)
            return doc_ref.id

    async def get_organization(self, org_id: str) -> dict[str, Any] | None:
        """Get organization."""
        return await self._get_doc("organizations", org_id)

    async def update_organization(self, org_id: str, updates: dict[str, Any]):
        """Update organization."""
        await self.db.collection("organizations").document(str(org_id)).update(updates)

    async def list_organizations(self) -> list[dict[str, Any]]:
        """List organizations."""
        return await self._get_all("organizations")

    async def delete_organization(self, org_id: str):
        """Delete organization."""
        await self._delete_doc("organizations", "id", org_id)

    async def delete_org_data(self, org_id: str):
        """Cascading delete for organization data (Workflows, Executions)."""
        # 1. Workflows
        await self._delete_doc("workflows", "organization_id", org_id)
        # 2. Executions
        await self._delete_doc("executions", "organization_id", org_id)

    async def log_usage(self, record: Any):
        """Log usage."""
        data = record.model_dump()
        await self.db.collection("usage_logs").add(data)

    async def get_org_usage_total(self, org_id: str, since: str | None = None) -> float:
        """Get total org usage."""
        coll = self.db.collection("usage_logs")
        query = coll.where(filter=FieldFilter("org_id", "==", org_id))
        if since:
            query = query.where(filter=FieldFilter("timestamp", ">=", since))

        docs = query.stream()
        total = 0.0
        async for doc in docs:
            d = doc.to_dict()
            total += float(d.get("cost_usd", 0.0))
        return total

    # --- System Settings ---
    async def get_system_settings(self) -> dict[str, Any]:
        """Retrieves global system settings singleton."""
        doc = await self.db.collection("system_config").document("global_settings").get()
        if doc.exists:
            return doc.to_dict()
        return {}

    async def update_system_settings(self, updates: dict[str, Any]):
        """Updates global system settings."""
        await self.db.collection("system_config").document("global_settings").set(updates, merge=True)

    # --- Audit Logs ---
    async def log_audit_event(self, entry: dict[str, Any]):
        """Persists a structured audit log entry."""
        await self.db.collection("audit_logs").add(entry)

    async def get_audit_logs(
        self,
        organization_id: str | None = None,
        actor_uid: str | None = None,
        action: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Retrieves audit logs with optional filtering."""
        query = self.db.collection("audit_logs")

        if organization_id:
            query = query.where(filter=FieldFilter("organization_id", "==", organization_id))
        if actor_uid:
            query = query.where(filter=FieldFilter("actor_uid", "==", actor_uid))
        if action:
            query = query.where(filter=FieldFilter("action", "==", action))

        # Order by timestamp desc
        query = query.order_by("timestamp", direction=Query.DESCENDING)
        query = query.limit(limit)

        docs = query.stream()
        return [doc.to_dict() async for doc in docs]

    # --- User Management ---
    async def get_user(self, uid: str) -> dict[str, Any] | None:
        """Get user by UID."""
        return await self._find_one_by_field("users", "uid", uid)

    async def list_users(self, organization_id: str | None = None) -> list[dict[str, Any]]:
        """List users."""
        if organization_id:
            docs = (
                self.db.collection("users").where(filter=FieldFilter("organization_id", "==", organization_id)).stream()
            )
            return [doc.to_dict() async for doc in docs]
        return await self._get_all("users")
