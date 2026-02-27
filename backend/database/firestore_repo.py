"""Firestore Repository Implementation."""

import json
import logging
import os
import uuid
from typing import Any

from google.cloud import firestore  # type: ignore

from backend.database.repository import AbstractWorkflowRepository
from backend.models.domain.execution import ExecutionRecord
from backend.models.workflow import WorkflowDefinition

logger = logging.getLogger(__name__)


class FirestoreWorkflowRepository(AbstractWorkflowRepository):
    """Firestore implementation of the AsyncRepository."""

    def __init__(self, client: firestore.AsyncClient):
        self.db = client

    # --- Helper: Universal Serializer (Parity with TinyDB) ---
    def _serialize_for_firestore(self, data: dict[str, Any] | list | Any) -> Any:
        """Recursively converts datetime, UUID, and Pydantic objects to JSON-safe types."""
        import uuid
        from datetime import datetime

        # Check for PyDantc model first
        if hasattr(data, "model_dump"):
            return self._serialize_for_firestore(data.model_dump())

        if isinstance(data, datetime):
            # Firestore can handle datetime, but for purity/parity we might want ISO string?
            # Actually Firestore native types are better for querying.
            # But prompt requested "Ensure WorkflowState is correctly serialized to JSON/Dict"
            # And "Ensure TraceEvent list is stored correctly."
            # If we serialize to JSON-dict (dict with only primitives), we are safe.
            return data.isoformat()

        if isinstance(data, uuid.UUID):
            return str(data)

        if isinstance(data, dict):
            return {k: self._serialize_for_firestore(v) for k, v in data.items()}

        if isinstance(data, list):
            return [self._serialize_for_firestore(v) for v in data]

        return data

    async def get_execution(self, execution_id: str) -> ExecutionRecord | None:
        doc_ref = self.db.collection("executions").document(execution_id)
        doc = await doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            return ExecutionRecord(**data)
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
        # Serializer for safety
        safe_data = self._serialize_for_firestore(execution_data)

        # If ID not provided, Firestore auto-generates, but we usually want to know it.
        # Ideally execution_data has 'execution_id' or we let firestore gen it.
        # Standard: use 'execution_id' key if present as doc ID.
        if "execution_id" in safe_data:
            doc_id = safe_data["execution_id"]
            await self.db.collection("executions").document(doc_id).set(safe_data)
            return doc_id
        else:
            _, doc_ref = await self.db.collection("executions").add(safe_data)
            return doc_ref.id

    async def update_execution(self, execution_id: str, updates: dict[str, Any]) -> bool:
        doc_ref = self.db.collection("executions").document(execution_id)

        safe_updates = self._serialize_for_firestore(updates)

        try:
            await doc_ref.update(safe_updates)
            return True
        except Exception as e:
            logger.error(f"Firestore update failed: {e}")
            return False

    async def delete_execution(self, execution_id: str) -> bool:
        """Delete an execution record."""
        try:
            await self.db.collection("executions").document(execution_id).delete()
            return True
        except Exception as e:
            logger.error(f"Firestore delete failed for execution {execution_id}: {e}")
            return False

    async def get_all_executions(
        self, organization_id: str | None = None, user_id: str | None = None
    ) -> list[ExecutionRecord]:
        query = self.db.collection("executions")
        if organization_id:
            query = query.where("organization_id", "==", organization_id)
        if user_id:
            query = query.where("user_id", "==", user_id)

        docs = await query.stream()
        results = []
        async for doc in docs:
            data = doc.to_dict()
            results.append(ExecutionRecord(**data))
        return results

    async def get_recent_completed_executions(self, limit: int = 5) -> list[ExecutionRecord]:
        query = self.db.collection("executions").where("status", "==", "completed")
        query = query.order_by("completed_at", direction=firestore.Query.DESCENDING).limit(limit)
        
        docs = await query.stream()
        results = []
        async for doc in docs:
            data = doc.to_dict()
            results.append(ExecutionRecord(**data))
        return results

    async def log_audit_event(self, event_data: dict[str, Any]) -> None:
        """Log an audit event to Firestore."""
        safe_data = self._serialize_for_firestore(event_data)
        await self.db.collection("audit_logs").document(safe_data["id"]).set(safe_data)

    async def get_audit_logs(
        self,
        organization_id: str | None = None,
        actor_id: str | None = None,
        action: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        query = self.db.collection("audit_logs")

        if organization_id:
            query = query.where("organization_id", "==", organization_id)
        if actor_id:
            query = query.where("actor_id", "==", actor_id)
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
        safe_data = self._serialize_for_firestore(workflow_data)
        doc_id = safe_data["id"]
        await self.db.collection("workflows").document(doc_id).set(safe_data)
        return doc_id

    async def update_workflow(self, workflow_id: str, updates: dict[str, Any]) -> bool:
        safe_updates = self._serialize_for_firestore(updates)
        try:
            await self.db.collection("workflows").document(workflow_id).update(safe_updates)
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
        safe_data = self._serialize_for_firestore(step_data)
        doc_id = safe_data.get("id")
        if not doc_id:
            raise ValueError("Step ID missing")
        await self.db.collection("steps").document(doc_id).set(safe_data)
        return doc_id

    async def update_step(self, step_id: str, updates: dict[str, Any]) -> bool:
        safe_updates = self._serialize_for_firestore(updates)
        try:
            await self.db.collection("steps").document(step_id).update(safe_updates)
            return True
        except Exception:
            return False

    async def delete_step(self, step_id: str) -> bool:
        try:
            await self.db.collection("steps").document(step_id).delete()
            return True
        except Exception:
            return False

    async def get_all_components(
        self, type: str | None = None, exclude_types: list[str] | None = None
    ) -> list[dict[str, Any]]:
        query = self.db.collection("components")
        if type:
            query = query.where("type", "==", type)

        docs = await query.stream()
        results = [doc.to_dict() async for doc in docs]

        if exclude_types:
            results = [c for c in results if c.get("type") not in exclude_types]

        return results

    async def get_component_by_id(self, component_id: str) -> dict[str, Any] | None:
        doc = await self.db.collection("components").document(component_id).get()
        return doc.to_dict() if doc.exists else None

    async def get_component_by_name(self, name: str) -> dict[str, Any] | None:
        query = self.db.collection("components").where("name", "==", name).limit(1)
        docs = await query.stream()
        results = [doc.to_dict() async for doc in docs]
        return results[0] if results else None

    async def get_matrix_by_id(self, matrix_id: str) -> dict[str, Any] | None:
        doc = await self.db.collection("matrices").document(matrix_id).get()
        return doc.to_dict() if doc.exists else None

    async def get_agent_by_id(self, agent_id: str) -> dict[str, Any] | None:
        doc = await self.db.collection("agents").document(agent_id).get()
        return doc.to_dict() if doc.exists else None

    async def get_dimension_by_id(self, dimension_id: str) -> dict[str, Any] | None:
        doc = await self.db.collection("dimensions").document(dimension_id).get()
        return doc.to_dict() if doc.exists else None

    async def get_output_config_by_id(self, config_id: str) -> dict[str, Any] | None:
        doc = await self.db.collection("output_configs").document(config_id).get()
        return doc.to_dict() if doc.exists else None

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

    async def register_component(self, component_data: dict[str, Any]) -> str:
        """Register a new component."""
        safe_data = self._serialize_for_firestore(component_data)
        doc_id = safe_data["id"]
        await self.db.collection("components").document(doc_id).set(safe_data)
        return doc_id

    async def create_component(self, component_data: dict[str, Any]) -> str:
        return await self.register_component(component_data)

    async def update_component(self, component_id: str, updates: dict[str, Any]) -> bool:
        """Update a component."""
        safe_updates = self._serialize_for_firestore(updates)
        try:
            await self.db.collection("components").document(component_id).update(safe_updates)
            return True
        except Exception as e:
            logger.error(f"Failed to update component {component_id}: {e}")
            return False

    async def delete_component(self, component_id: str) -> bool:
        """Delete a component."""
        try:
            await self.db.collection("components").document(component_id).delete()
            return True
        except Exception as e:
            logger.error(f"Failed to delete component {component_id}: {e}")
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
            # Serialized timestamp handled by Firestore SERVER_TIMESTAMP,
            # but we use safe_data in other places. Here manual is fine.
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

    async def clear_knowledge_base(self) -> None:
        """Delete all documents from concepts, references, and claims collections."""
        all_deleted = True
        for col in ["concepts", "references", "claims"]:
            docs = await self.db.collection(col).get()
            if not docs:
                continue  # No documents in this collection, move to next

            for doc in docs:
                try:
                    await doc.reference.delete()
                except Exception as e:
                    logger.error(f"Failed to delete document {doc.id} from collection {col}: {e}")
                    all_deleted = False  # Mark as false if any deletion fails
        return None

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

    async def get_concepts(self) -> list[dict[str, Any]]:
        c_docs = await self.db.collection("concepts").get()
        return [doc.to_dict() for doc in c_docs]

    async def get_references(self) -> list[dict[str, Any]]:
        r_docs = await self.db.collection("references").get()
        return [doc.to_dict() for doc in r_docs]

    async def get_claims(self) -> list[dict[str, Any]]:
        cl_docs = await self.db.collection("claims").get()
        return [doc.to_dict() for doc in cl_docs]

    async def add_concept(self, item: dict[str, Any]) -> str:
        doc_id = item.setdefault("id", str(uuid.uuid4()) if "uuid" in globals() else "gen_id")
        doc_ref = self.db.collection("concepts").document(doc_id)
        await doc_ref.set(item)
        return doc_id

    async def add_reference(self, item: dict[str, Any]) -> str:
        doc_id = item.setdefault("id", str(uuid.uuid4()) if "uuid" in globals() else "gen_id")
        doc_ref = self.db.collection("references").document(doc_id)
        await doc_ref.set(item)
        return doc_id

    async def add_claim(self, item: dict[str, Any]) -> str:
        doc_id = item.setdefault("id", str(uuid.uuid4()) if "uuid" in globals() else "gen_id")
        doc_ref = self.db.collection("claims").document(doc_id)
        await doc_ref.set(item)
        return doc_id

    async def get_model_registry(self) -> dict[str, Any]:
        """Retrieve the model registry configuration."""
        try:
            doc = await self.db.collection("system_config").document("model_registry").get()
            if doc.exists:
                return doc.to_dict()
        except Exception as e:
            logger.error(f"Firestore model registry check failed: {e}")
            from backend.exceptions import AppException, ErrorCodes, status
            raise AppException(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details={"error_code": ErrorCodes.DATABASE_ERROR}) from e
            
        logger.error("[FirestoreRepository] SYSTEM_CONFIG_NOT_FOUND: 'model_registry' document is missing from database.")
        from backend.exceptions import ResourceNotFoundError
        raise ResourceNotFoundError(resource_type="system_config", resource_id="model_registry")

    async def update_model_registry(self, registry_data: dict[str, Any]) -> bool:
        """Update the model registry configuration."""
        safe_data = self._serialize_for_firestore(registry_data)
        try:
            doc_id = safe_data.get("id", "model_registry")
            if doc_id != "model_registry" and "slug" not in safe_data:
                safe_data["slug"] = "model_registry"
            await self.db.collection("system_config").document(doc_id).set(safe_data)
            return True
        except Exception as e:
            logger.error(f"Firestore model registry update failed: {e}")
            return False

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
        safe_data = self._serialize_for_firestore(org_data)
        doc_id = safe_data["id"]
        await self.db.collection("organizations").document(doc_id).set(safe_data)
        return doc_id

    async def update_organization(self, org_id: str, updates: dict[str, Any]) -> bool:
        """Update an organization."""
        safe_updates = self._serialize_for_firestore(updates)
        try:
            await self.db.collection("organizations").document(org_id).update(safe_updates)
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

    async def get_detailed_usage(self, scope: str, target_id: str | None = None, since: str | None = None) -> dict[str, Any]:
        """Aggregate detailed usage metrics filtered by role scope."""
        query = self.db.collection("executions")
        
        if since:
            query = query.where("created_at", ">=", since)
            
        if scope == "user" and target_id:
            query = query.where("user_id", "==", target_id)
        elif scope == "org" and target_id:
            query = query.where("organization_id", "==", target_id)
            
        docs = await query.stream()
        
        total_cost = 0.0
        total_runs = 0
        total_time = 0
        models_used: dict[str, int] = {}
        workflows_used: dict[str, int] = {}
        
        async for doc in docs:
            data = doc.to_dict()
            total_runs += 1
            total_cost += data.get("cost_estimate", 0.0)
            total_time += data.get("duration_ms", 0)
            
            wid = data.get("workflow_id")
            if wid:
                workflows_used[wid] = workflows_used.get(wid, 0) + 1
                
            mu = data.get("models_used", {})
            if isinstance(mu, dict):
                for m, count in mu.items():
                    models_used[m] = models_used.get(m, 0) + count
                    
        return {
            "total_cost_usd": total_cost,
            "total_runs": total_runs,
            "total_processing_time_ms": total_time,
            "models_used": models_used,
            "workflows_used": workflows_used
        }

    async def count_executions_by_matrix(self, matrix_id: str) -> int:
        """Count executions using a specific matrix ID."""
        # Query: executions where settings.matrix_id == matrix_id
        # Note: Depending on collection size, count() aggregation is efficient.
        query = self.db.collection("executions").where("settings.matrix_id", "==", matrix_id).count()
        try:
            snapshots = await query.get()
            return int(snapshots[0][0].value)
        except Exception as e:
            logger.warning(f"Firestore matrix count extraction failed: {e}")
            return 0

    async def get_components_using_dimension(self, dimension_id: str) -> list[str]:
        """Return list of component IDs that reference this dimension."""
        # Firestore cannot easily query deep nested arrays of objects (content.criteria[].dimension_id).
        # Strategy: Fetch all matrices (filtered by type) and scan in memory.
        # This is acceptable as number of matrices is expected to be relatively small (<100).
        matches = []
        try:
            query = self.db.collection("components").where("type", "in", ["evaluation_matrix", "matrix"])
            docs = await query.stream()

            async for doc in docs:
                data = doc.to_dict()
                content = data.get("content", {})
                if not isinstance(content, dict):
                    continue

                criteria = content.get("criteria", [])
                if not isinstance(criteria, list):
                    continue

                # Check if any criterion uses this dimension
                for crit in criteria:
                    if isinstance(crit, dict) and crit.get("dimension_id") == dimension_id:
                        matches.append(data.get("id"))
                        break
        except Exception as e:
            logger.error(f"Failed to scan components for dimension usage: {e}")

        return matches

    async def log_usage(self, record: Any) -> None:
        """Log a usage record."""
        safe_data = self._serialize_for_firestore(record)
        # Use ID from record if available, otherwise auto-gen
        doc_id = safe_data.get("id")
        if doc_id:
            await self.db.collection("usage").document(doc_id).set(safe_data)
        else:
            await self.db.collection("usage").add(safe_data)
