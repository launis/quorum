"""Firestore Repository Implementation."""

import json
import logging
import os
from typing import Any

from google.cloud import firestore  # type: ignore

from backend.database.repository import AbstractWorkflowRepository
from backend.models.workflow import WorkflowDefinition

logger = logging.getLogger(__name__)


class FirestoreWorkflowRepository(AbstractWorkflowRepository):
    """Firestore implementation of the AsyncRepository."""

    def __init__(self, client: firestore.AsyncClient):
        self.db = client

    async def get_execution(self, execution_id: str) -> dict[str, Any] | None:
        doc_ref = self.db.collection("executions").document(execution_id)
        doc = await doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None

    async def get_execution_status(self, execution_id: str) -> str | None:
        """Retrieve the status of an execution."""
        doc_ref = self.db.collection("executions").document(execution_id)
        # Optimized fetch: only get the 'status' field
        doc = await doc_ref.get(field_paths=["status"])
        if doc.exists:
            return doc.to_dict().get("status")
        return None

    async def create_execution(self, execution_data: dict[str, Any]) -> str:
        # If ID not provided, Firestore auto-generates, but we usually want to know it.
        # Ideally execution_data has 'execution_id' or we let firestore gen it.
        # Standard: use 'execution_id' key if present as doc ID.
        if "execution_id" in execution_data:
            doc_id = execution_data["execution_id"]
            await self.db.collection("executions").document(doc_id).set(execution_data)
            return doc_id
        else:
            _, doc_ref = await self.db.collection("executions").add(execution_data)
            return doc_ref.id

    async def update_execution(self, execution_id: str, updates: dict[str, Any]) -> bool:
        doc_ref = self.db.collection("executions").document(execution_id)
        # Ensure generic state dicts are handled; Firestore accepts dicts natively.
        # If updates contains complex objects, they must be serialized before calling this.
        # But 'updates' usually comes from Engine which manages serialization if needed?
        # Engine stores Pydantic dumps typically.
        try:
            await doc_ref.update(updates)
            return True
        except Exception as e:
            logger.error(f"Firestore update failed: {e}")
            return False

    async def get_all_executions(
        self, organization_id: str | None = None, user_id: str | None = None
    ) -> list[dict[str, Any]]:
        query = self.db.collection("executions")
        if organization_id:
            query = query.where("organization_id", "==", organization_id)
        if user_id:
            query = query.where("user_id", "==", user_id)

        docs = await query.stream()
        return [doc.to_dict() async for doc in docs]  # Ensure async iteration for firestore AsyncClient

    async def log_audit_event(self, event_data: dict[str, Any]) -> None:
        """Log an audit event to Firestore."""
        # Use a batch or direct write? Direct is fine for audit.
        # Collection: 'audit_logs'
        # document ID: event_data['id']
        await self.db.collection("audit_logs").document(event_data["id"]).set(event_data)

    async def get_audit_logs(
        self,
        organization_id: str | None = None,
        actor_uid: str | None = None,
        action: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        query = self.db.collection("audit_logs")

        if organization_id:
            query = query.where("organization_id", "==", organization_id)
        if actor_uid:
            query = query.where("actor_uid", "==", actor_uid)
        if action:
            query = query.where("action", "==", action)

        # Order by timestamp desc
        query = query.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(limit)

        docs = await query.stream()
        return [doc.to_dict() async for doc in docs]

    # --- V2.9 Workflow Methods ---

    async def get_all_workflows(
        self, organization_id: str | None = None, role: str | None = None
    ) -> list[dict[str, Any]]:
        query = self.db.collection("workflows")
        if role != "ROOT":
            # Basic RBAC: filter by org if provided, otherwise assume user only sees own org unless specified handled by caller
            if organization_id:
                query = query.where("organization_id", "in", [organization_id, "system"])

        docs = await query.stream()
        return [doc.to_dict() async for doc in docs]

    async def get_workflow_by_id(self, workflow_id: str) -> dict[str, Any] | None:
        # Prefer DB
        doc_ref = self.db.collection("workflows").document(workflow_id)
        doc = await doc_ref.get()
        if doc.exists:
            return doc.to_dict()

        # Fallback using get_workflow_definition logic?
        # For now, keep simple DB access.
        return None

    async def create_workflow(self, workflow_data: dict[str, Any]) -> str:
        # workflow_data MUST have 'id'
        doc_id = workflow_data["id"]
        await self.db.collection("workflows").document(doc_id).set(workflow_data)
        return doc_id

    async def update_workflow(self, workflow_id: str, updates: dict[str, Any]) -> bool:
        try:
            await self.db.collection("workflows").document(workflow_id).update(updates)
            return True
        except Exception as e:
            logger.error(f"Failed to update workflow {workflow_id}: {e}")
            return False

    async def delete_workflow(self, workflow_id: str) -> bool:
        try:
            await self.db.collection("workflows").document(workflow_id).delete()
            return True
        except Exception:
            return False

    async def get_all_steps(self) -> list[dict[str, Any]]:
        docs = await self.db.collection("steps").stream()
        return [doc.to_dict() async for doc in docs]

    async def get_step_by_id(self, step_id: str) -> dict[str, Any] | None:
        doc = await self.db.collection("steps").document(step_id).get()
        return doc.to_dict() if doc.exists else None

    async def create_step(self, step_data: dict[str, Any]) -> str:
        doc_id = step_data.get("id")
        if not doc_id:
            raise ValueError("Step ID missing")
        await self.db.collection("steps").document(doc_id).set(step_data)
        return doc_id

    async def update_step(self, step_id: str, updates: dict[str, Any]) -> bool:
        try:
            await self.db.collection("steps").document(step_id).update(updates)
            return True
        except Exception:
            return False

    async def delete_step(self, step_id: str) -> bool:
        try:
            await self.db.collection("steps").document(step_id).delete()
            return True
        except Exception:
            return False

    async def get_all_components(self) -> list[dict[str, Any]]:
        docs = await self.db.collection("components").stream()
        return [doc.to_dict() async for doc in docs]

    async def get_component_by_id(self, component_id: str) -> dict[str, Any] | None:
        doc = await self.db.collection("components").document(component_id).get()
        return doc.to_dict() if doc.exists else None

    async def get_component_by_name(self, name: str) -> dict[str, Any] | None:
        query = self.db.collection("components").where("name", "==", name).limit(1)
        docs = await query.stream()
        results = [doc.to_dict() async for doc in docs]
        return results[0] if results else None

    async def get_workflow_definition(self, workflow_id: str) -> WorkflowDefinition | None:
        """Retrieves workflow definition.
        Strategy:
        1. Check 'workflows' collection in Firestore.
        2. Fallback to 'data/workflows/{id}.json' on disk (Crucial for Dev).
        """
        definition = None

        # 1. DB Lookup
        try:
            doc_ref = self.db.collection("workflows").document(workflow_id)
            doc = await doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                logger.info(f"Loaded workflow '{workflow_id}' from Firestore.")
                return WorkflowDefinition(**data)
        except Exception as e:
            logger.warning(f"Firestore workflow lookup failed for '{workflow_id}': {e}")

        # 2. Disk Fallback
        file_path = f"data/workflows/{workflow_id}.json"

        # normalize path relative to project root?
        # Assuming CWD is project root.
        if os.path.exists(file_path):
            try:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)
                    # Just in case description is missing in file but required
                    if "description" not in data:
                        data["description"] = "Loaded from disk"

                    definition = WorkflowDefinition(**data)
                    logger.info(f"Loaded workflow '{workflow_id}' from Disk Fallback.")
                    return definition
            except Exception as e:
                logger.error(f"Failed to load workflow from disk '{file_path}': {e}")

        logger.warning(f"Workflow definition '{workflow_id}' not found in DB or Disk.")
        return None

    # --- Missing Abstract Methods Implementation (Added Jan 2026 for Parity) ---

    async def update_component_metadata(self, component_id: str, module: str, component_class: str) -> bool:
        """Update component metadata in Firestore."""
        try:
            await (
                self.db.collection("components")
                .document(component_id)
                .update({"module": module, "class_name": component_class})
            )
            return True
        except Exception as e:
            logger.error(f"Failed to update component metadata {component_id}: {e}")
            return False

    async def get_banned_phrases(self) -> list[dict[str, Any]]:
        """Retrieve all banned phrases."""
        docs = await self.db.collection("banned_phrases").stream()
        return [doc.to_dict() async for doc in docs]

    async def add_banned_phrase(self, phrase: str, language: str = "en") -> None:
        """Add a banned phrase if it doesn't exist."""
        # Query for existence first
        query = self.db.collection("banned_phrases").where("phrase", "==", phrase).limit(1)
        docs = await query.get()  # .get() is efficient for small limit
        if not docs:
            await self.db.collection("banned_phrases").add(
                {"phrase": phrase, "language": language, "timestamp": firestore.SERVER_TIMESTAMP}
            )

    async def delete_banned_phrase(self, phrase: str) -> bool:
        """Delete a banned phrase."""
        query = self.db.collection("banned_phrases").where("phrase", "==", phrase).limit(1)
        docs = await query.get()
        deleted = False
        for doc in docs:
            await doc.reference.delete()
            deleted = True
        return deleted

    async def count_workflows(self) -> int:
        """Count total workflows."""
        try:
            # Standard aggregation in recent google-cloud-firestore
            col = self.db.collection("workflows")
            aggregate_query = col.count()
            snapshots = await aggregate_query.get()
            return int(snapshots[0][0].value)
        except Exception as e:
            logger.warning(f"Firestore count aggregation failed, falling back to len(): {e}")
            docs = await self.db.collection("workflows").select([]).get()
            return len(docs)

    async def get_prompt_template(self, template_id: str) -> dict[str, str] | None:
        """Retrieve a prompt template by ID."""
        doc_ref = self.db.collection("prompts").document(template_id)
        doc = await doc_ref.get()
        if doc.exists:
            res = doc.to_dict()
            return {"system": res.get("system_prompt", ""), "user": res.get("user_prompt", "")}

        # Fallback: Query by field 'id' if doc ID didn't match
        query = self.db.collection("prompts").where("id", "==", template_id).limit(1)
        docs = await query.get()
        if docs:
            res = docs[0].to_dict()
            return {"system": res.get("system_prompt", ""), "user": res.get("user_prompt", "")}

        return None

    async def get_knowledge_base_items(self) -> list[dict[str, Any]]:
        """Retrieve all knowledge base items."""
        docs = await self.db.collection("knowledge_base").stream()
        return [doc.to_dict() async for doc in docs]

    async def get_model_registry(self) -> dict[str, Any]:
        """Retrieve the model registry configuration."""
        try:
            doc = await self.db.collection("system_config").document("model_registry").get()
            if doc.exists:
                return doc.to_dict()
        except Exception as e:
            logger.error(f"Firestore model registry lookup failed: {e}")
        return {}

    # --- Organization Methods (Required by organization_router.py) ---

    async def list_organizations(self) -> list[dict[str, Any]]:
        """List all organizations."""
        docs = await self.db.collection("organizations").stream()
        return [doc.to_dict() async for doc in docs]

    async def get_organization(self, org_id: str) -> dict[str, Any] | None:
        """Get organization by ID."""
        doc = await self.db.collection("organizations").document(org_id).get()
        return doc.to_dict() if doc.exists else None

    async def create_organization(self, org_data: dict[str, Any]) -> str:
        """Create a new organization."""
        doc_id = org_data["id"]
        await self.db.collection("organizations").document(doc_id).set(org_data)
        return doc_id

    async def update_organization(self, org_id: str, updates: dict[str, Any]) -> bool:
        """Update an organization."""
        try:
            await self.db.collection("organizations").document(org_id).update(updates)
            return True
        except Exception as e:
            logger.error(f"Failed to update organization {org_id}: {e}")
            return False

    async def delete_organization(self, org_id: str) -> bool:
        """Delete an organization."""
        try:
            await self.db.collection("organizations").document(org_id).delete()
            return True
        except Exception:
            return False

    async def list_users(self, organization_id: str | None = None) -> list[dict[str, Any]]:
        """List users, optionally filtered by organization."""
        query = self.db.collection("users")
        if organization_id:
            query = query.where("organization_id", "==", organization_id)
        docs = await query.stream()
        return [doc.to_dict() async for doc in docs]

    async def delete_org_data(self, org_id: str) -> None:
        """Delete all data associated with an organization (cascade delete)."""
        # Delete users
        user_query = self.db.collection("users").where("organization_id", "==", org_id)
        user_docs = await user_query.stream()
        async for doc in user_docs:
            await doc.reference.delete()

        # Delete executions
        exec_query = self.db.collection("executions").where("organization_id", "==", org_id)
        exec_docs = await exec_query.stream()
        async for doc in exec_docs:
            await doc.reference.delete()

        # Delete workflows owned by org
        wf_query = self.db.collection("workflows").where("organization_id", "==", org_id)
        wf_docs = await wf_query.stream()
        async for doc in wf_docs:
            await doc.reference.delete()

    async def get_org_usage_total(self, org_id: str, since: str | None = None) -> float:
        """Calculate total usage cost for an organization since a given timestamp."""
        query = self.db.collection("executions").where("organization_id", "==", org_id)
        if since:
            query = query.where("created_at", ">=", since)
        
        docs = await query.stream()
        total = 0.0
        async for doc in docs:
            data = doc.to_dict()
            total += data.get("cost_estimate", 0.0)
        return total

