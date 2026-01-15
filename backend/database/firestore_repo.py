"""Firestore Repository Implementation."""

import json
import logging
import os
from typing import Any, Dict, List, Optional

from google.cloud import firestore  # type: ignore

from backend.database.repository import AbstractWorkflowRepository
from backend.models.workflow import WorkflowDefinition

logger = logging.getLogger(__name__)


class FirestoreWorkflowRepository(AbstractWorkflowRepository):
    """Firestore implementation of the AsyncRepository."""

    def __init__(self, client: firestore.AsyncClient):
        self.db = client

    async def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        doc_ref = self.db.collection("executions").document(execution_id)
        doc = await doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None

    async def create_execution(self, execution_data: Dict[str, Any]) -> str:
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

    async def update_execution(self, execution_id: str, updates: Dict[str, Any]) -> bool:
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
        self, organization_id: Optional[str] = None, user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = self.db.collection("executions")
        if organization_id:
            query = query.where("organization_id", "==", organization_id)
        if user_id:
            query = query.where("user_id", "==", user_id)
            
        docs = await query.stream()
        return [doc.to_dict() async for doc in docs] # Ensure async iteration for firestore AsyncClient

    async def log_audit_event(self, event_data: Dict[str, Any]) -> None:
        """Log an audit event to Firestore."""
        # Use a batch or direct write? Direct is fine for audit.
        # Collection: 'audit_logs'
        # document ID: event_data['id']
        await self.db.collection("audit_logs").document(event_data["id"]).set(event_data)

    async def get_audit_logs(
        self,
        organization_id: Optional[str] = None,
        actor_uid: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
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
        self, organization_id: Optional[str] = None, role: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = self.db.collection("workflows")
        if role != "ROOT":
             # Basic RBAC: filter by org if provided, otherwise assume user only sees own org unless specified handled by caller
             if organization_id:
                 query = query.where("organization_id", "in", [organization_id, "system"])
        
        docs = await query.stream()
        return [doc.to_dict() async for doc in docs]

    async def get_workflow_by_id(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        # Prefer DB
        doc_ref = self.db.collection("workflows").document(workflow_id)
        doc = await doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        
        # Fallback using get_workflow_definition logic?
        # For now, keep simple DB access.
        return None

    async def create_workflow(self, workflow_data: Dict[str, Any]) -> str:
        # workflow_data MUST have 'id'
        doc_id = workflow_data["id"]
        await self.db.collection("workflows").document(doc_id).set(workflow_data)
        return doc_id

    async def update_workflow(self, workflow_id: str, updates: Dict[str, Any]) -> bool:
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

    async def get_all_steps(self) -> List[Dict[str, Any]]:
        docs = await self.db.collection("steps").stream()
        return [doc.to_dict() async for doc in docs]

    async def get_step_by_id(self, step_id: str) -> Optional[Dict[str, Any]]:
        doc = await self.db.collection("steps").document(step_id).get()
        return doc.to_dict() if doc.exists else None

    async def create_step(self, step_data: Dict[str, Any]) -> str:
        doc_id = step_data.get("id")
        if not doc_id:
            raise ValueError("Step ID missing")
        await self.db.collection("steps").document(doc_id).set(step_data)
        return doc_id

    async def update_step(self, step_id: str, updates: Dict[str, Any]) -> bool:
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

    async def get_all_components(self) -> List[Dict[str, Any]]:
        docs = await self.db.collection("components").stream()
        return [doc.to_dict() async for doc in docs]

    async def get_component_by_id(self, component_id: str) -> Optional[Dict[str, Any]]:
        doc = await self.db.collection("components").document(component_id).get()
        return doc.to_dict() if doc.exists else None

    async def get_component_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        query = self.db.collection("components").where("name", "==", name).limit(1)
        docs = await query.stream()
        results = [doc.to_dict() async for doc in docs]
        return results[0] if results else None

    async def get_workflow_definition(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """
        Retrieves workflow definition.
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
                with open(file_path, "r", encoding="utf-8") as f:
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
            await self.db.collection("components").document(component_id).update({
                "module": module,
                "class_name": component_class
            })
            return True
        except Exception as e:
            logger.error(f"Failed to update component metadata {component_id}: {e}")
            return False

    async def get_banned_phrases(self) -> List[Dict[str, Any]]:
        """Retrieve all banned phrases."""
        docs = await self.db.collection("banned_phrases").stream()
        return [doc.to_dict() async for doc in docs]

    async def add_banned_phrase(self, phrase: str, language: str = "en") -> None:
        """Add a banned phrase if it doesn't exist."""
        # Query for existence first
        query = self.db.collection("banned_phrases").where("phrase", "==", phrase).limit(1)
        docs = await query.get() # .get() is efficient for small limit
        if not docs:
            await self.db.collection("banned_phrases").add({
                "phrase": phrase,
                "language": language,
                "timestamp": firestore.SERVER_TIMESTAMP
            })

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

    async def get_prompt_template(self, template_id: str) -> Optional[Dict[str, str]]:
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

    async def get_knowledge_base_items(self) -> List[Dict[str, Any]]:
        """Retrieve all knowledge base items."""
        docs = await self.db.collection("knowledge_base").stream()
        return [doc.to_dict() async for doc in docs]
