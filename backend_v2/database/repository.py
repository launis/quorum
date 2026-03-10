"""Unified Repository Implementation.

This module implements the 'Storage Driver Pattern' (V2.9/V2026).
Business logic is written ONCE in UnifiedWorkflowRepository and delegates
I/O to the injected StorageDriver.
"""

import logging
import uuid
from abc import ABC, abstractmethod
from typing import Any

from backend_v2.database.driver import Filter, StorageDriver
from backend_v2.models.v2_core import ExecutionRecord
from backend_v2.models.v2_core import Workflow as WorkflowDefinition

logger = logging.getLogger(__name__)


class AbstractWorkflowRepository(ABC):
    """Abstract base class for asynchronous data access.

    Kept for dependency injection compatibility.
    """

    @abstractmethod
    async def get_execution(self, execution_id: str) -> ExecutionRecord | None:
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
    ) -> list[ExecutionRecord]:
        pass

    @abstractmethod
    async def get_recent_completed_executions(self, limit: int = 5) -> list[ExecutionRecord]:
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
        actor_id: str | None = None,
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
        """Create a new append-only workflow."""
        pass

    @abstractmethod
    async def update_workflow(self, workflow_id: str, updates: dict[str, Any]) -> str:
        """Append-only update. Creates a new version and returns the new ID.
        Sets is_latest to False on the old version.
        """
        pass

    @abstractmethod
    async def update_workflow_definition(self, workflow_id: str, definition_data: dict[str, Any]) -> str:
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

    # --- Generic Data Access ---

    @abstractmethod
    async def get_all(self, collection: str) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def get(self, collection: str, doc_id: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    async def create_raw(self, collection: str, data: dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def delete(self, collection: str, doc_id: str) -> bool:
        pass



    @abstractmethod
    async def create_step(self, step_data: dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def update_step(self, step_id: str, updates: dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def delete_step(self, step_id: str, force_delete: bool = False) -> bool:
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
    async def get_component_by_slug(self, slug: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    async def update_component_metadata(self, component_id: str, module: str, component_class: str) -> bool:
        pass

    @abstractmethod
    async def register_component(self, component_data: dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def create_component(self, component_data: dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def get_prompt_block_by_id(self, block_id: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    async def get_all_prompt_blocks(self) -> list[dict[str, Any]]:
        """Fetch all V2 prompt_blocks."""
        pass

    @abstractmethod
    async def create_prompt_block(self, block_data: dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def update_prompt_block(self, block_id: str, updates: dict[str, Any]) -> bool:
        pass

    @abstractmethod
    async def delete_prompt_block(self, block_id: str, force_delete: bool = False) -> bool:
        pass

    @abstractmethod
    async def get_agent_by_id(self, agent_id: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    async def get_all_agents(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def create_agent(self, agent_data: dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def update_agent(self, agent_id: str, updates: dict[str, Any]) -> bool:
        pass

    @abstractmethod
    async def delete_agent(self, agent_id: str) -> bool:
        pass

    @abstractmethod
    async def get_dimension_by_id(self, dimension_id: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    async def get_all_dimensions(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def create_dimension(self, dimension_data: dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def update_dimension(self, dimension_id: str, updates: dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def delete_dimension(self, dimension_id: str) -> bool:
        pass

    @abstractmethod
    async def get_output_config_by_id(self, config_id: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    async def get_all_output_configs(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def create_output_config(self, config_data: dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def update_output_config(self, config_id: str, updates: dict[str, Any]) -> bool:
        pass

    @abstractmethod
    async def delete_output_config(self, config_id: str) -> bool:
        pass

    @abstractmethod
    async def update_component(self, component_id: str, updates: dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def delete_component(self, component_id: str) -> bool:
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
    async def get_concepts(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def get_references(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def get_claims(self) -> list[dict[str, Any]]:
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
    async def get_usage_records(
        self, scope: str, entity_id: str | None = None, since: str | None = None
    ) -> list[dict[str, Any]]:
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
    async def get_user(self, user_id: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    async def create_user(self, user_data: dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def update_user(self, user_id: str, updates: dict[str, Any]) -> bool:
        pass

    @abstractmethod
    async def delete_user(self, user_id: str) -> bool:
        pass

    @abstractmethod
    async def delete_org_data(self, org_id: str) -> None:
        pass

    @abstractmethod
    async def get_org_usage_total(self, org_id: str, since: str | None = None) -> float:
        pass

    @abstractmethod
    async def add_concept(self, item: dict[str, Any]) -> str:
        """Adds an item to the concepts collection."""
        pass

    @abstractmethod
    async def add_reference(self, item: dict[str, Any]) -> str:
        """Adds an item to the references collection."""
        pass

    @abstractmethod
    async def add_claim(self, item: dict[str, Any]) -> str:
        """Adds an item to the claims collection."""
        pass

    @abstractmethod
    async def get_system_settings(self) -> dict[str, Any] | None:
        pass

    @abstractmethod
    async def update_system_settings(self, updates: dict[str, Any]) -> bool:
        pass


class UnifiedWorkflowRepository(AbstractWorkflowRepository):
    """Unified implementation using the StorageDriver pattern.

    This replaces both TinyDBRepository and FirestoreWorkflowRepository.
    """

    def __init__(self, driver: StorageDriver):
        self.driver = driver

    # --- Generic Data Access ---

    async def get_all(self, collection: str) -> list[dict[str, Any]]:
        return await self.driver.query(collection)

    async def get(self, collection: str, doc_id: str) -> dict[str, Any] | None:
        return await self.driver.get(collection, doc_id)

    async def create_raw(self, collection: str, data: dict[str, Any]) -> str:
        doc_id = data.get("id")
        if not doc_id:
             doc_id = str(uuid.uuid4())
        return await self.driver.upsert(collection, data, doc_id)

    async def delete(self, collection: str, doc_id: str) -> bool:
        return await self.driver.delete(collection, doc_id)

    # --- Executions ---

    async def get_execution(self, execution_id: str) -> ExecutionRecord | None:
        data = await self.driver.get("executions", execution_id)
        return ExecutionRecord(**data) if data else None

    async def get_execution_status(self, execution_id: str) -> str | None:
        exec_record = await self.get_execution(execution_id)
        return exec_record.status if exec_record else None

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
    ) -> list[ExecutionRecord]:
        filters = []
        if organization_id:
            filters.append(Filter("organization_id", "==", organization_id))
        if user_id:
            filters.append(Filter("user_id", "==", user_id))

        results = await self.driver.query("executions", filters)
        return [ExecutionRecord(**r) for r in results]

    async def get_recent_completed_executions(self, limit: int = 5) -> list[ExecutionRecord]:
        filters = [Filter("status", "==", "completed")]
        results = await self.driver.query(
            "executions",
            filters=filters,
            limit=limit,
            order_by="completed_at",
            descending=True
        )
        return [ExecutionRecord(**r) for r in results]

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

        # Note: Hydration is strictly handled at the execution (engine.py)
        # or presentation (_expand_workflow) layer according to Strict SSOT API.

        return WorkflowDefinition(**data)

    async def log_audit_event(self, event_data: dict[str, Any]) -> None:
        doc_id = event_data.get("id") or str(uuid.uuid4())
        event_data["id"] = doc_id
        await self.driver.upsert("audit_logs", event_data, doc_id)

    async def get_audit_logs(
        self,
        organization_id: str | None = None,
        actor_id: str | None = None,
        action: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        filters = []
        if organization_id:
            filters.append(Filter("organization_id", "==", organization_id))
        if actor_id:
            filters.append(Filter("actor_id", "==", actor_id))
        if action:
            filters.append(Filter("action", "==", action))

        return await self.driver.query(
            "audit_logs", filters=filters, limit=limit, order_by="timestamp", descending=True
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

    async def update_workflow(self, workflow_id: str, updates: dict[str, Any]) -> str:
        """Unified Driver update. Must be overridden for Append-Only logic."""
        await self.driver.update("workflows", workflow_id, updates)
        return workflow_id

    async def update_workflow_definition(self, workflow_id: str, definition_data: dict[str, Any]) -> str:
        """Alias for update_workflow in V2 to satisfy AbstractWorkflowRepository."""
        return await self.update_workflow(workflow_id, definition_data)

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
                    if isinstance(s, dict) and (s.get("id") == step_id or s.get("slug") == step_id):
                        from backend_v2.exceptions import AppException, ErrorCodes
                        raise AppException(
                            message=f"Tuhoaminen estetty: Step '{step_id}' on sidottu Workflowhun '{wf.get('id', 'unknown')}'.",
                            details={"error_code": str(ErrorCodes.DELETE_BLOCKED_BY_USAGE.value)},
                            status_code=400
                        )
                    elif isinstance(s, str) and s == step_id:
                        from backend_v2.exceptions import AppException, ErrorCodes
                        raise AppException(
                            message=f"Tuhoaminen estetty: Step '{step_id}' on sidottu Workflowhun '{wf.get('id', 'unknown')}'.",
                            details={"error_code": str(ErrorCodes.DELETE_BLOCKED_BY_USAGE.value)},
                            status_code=400
                        )

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

    async def get_component_by_slug(self, slug: str) -> dict[str, Any] | None:
        res = await self.driver.query("components", [Filter("slug", "==", slug)], limit=1)
        return res[0] if res else None

    async def get_prompt_block_by_id(self, block_id: str) -> dict[str, Any] | None:
        return await self.driver.get("prompt_blocks", block_id)

    async def get_all_prompt_blocks(self) -> list[dict[str, Any]]:
        return await self.driver.query("prompt_blocks")

    async def create_prompt_block(self, block_data: dict[str, Any]) -> str:
        doc_id = block_data["id"]
        return await self.driver.upsert("prompt_blocks", block_data, doc_id)

    async def update_prompt_block(self, block_id: str, updates: dict[str, Any]) -> bool:
        block = await self.get_prompt_block_by_id(block_id)
        if not block:
            return False
        return await self.driver.update("prompt_blocks", block_id, updates)

    async def delete_prompt_block(self, block_id: str, force_delete: bool = False) -> bool:
        block = await self.get_prompt_block_by_id(block_id)
        if not block:
            return False
            
        if not force_delete:
            # Relational Check: Fail-Fast if used in any Step
            steps = await self.get_all_steps()
            for s in steps:
                if block_id in s.get("prompt_blocks", []):
                    from backend_v2.exceptions import AppException, ErrorCodes
                    error_msg = f"Tuhoaminen estetty: PromptBlock '{block_id}' on sidottu Askeleeseen'{str(s.get('id', 'unknown'))}'."
                    raise AppException(
                        message=str(error_msg),
                        details={"error_code": str(ErrorCodes.DELETE_BLOCKED_BY_USAGE.value)},
                        status_code=400
                    )

        return await self.driver.delete("prompt_blocks", block_id)

    async def get_agent_by_id(self, agent_id: str) -> dict[str, Any] | None:
        return await self.driver.get("agents", agent_id)

    async def get_task_blueprint_by_id(self, blueprint_id: str) -> dict[str, Any] | None:
        return await self.driver.get("task_blueprints", blueprint_id)

    async def get_all_task_blueprints(self) -> list[dict[str, Any]]:
        return await self.driver.query("task_blueprints")

    async def create_task_blueprint(self, blueprint_data: dict[str, Any]) -> str:
        doc_id = blueprint_data["id"]
        return await self.driver.upsert("task_blueprints", blueprint_data, doc_id)

    async def update_task_blueprint(self, blueprint_id: str, updates: dict[str, Any]) -> bool:
        blueprint = await self.get_task_blueprint_by_id(blueprint_id)
        if not blueprint:
            return False
        return await self.driver.update("task_blueprints", blueprint_id, updates)

    async def delete_task_blueprint(self, blueprint_id: str) -> bool:
        blueprint = await self.get_task_blueprint_by_id(blueprint_id)
        if not blueprint:
            return False
        return await self.driver.delete("task_blueprints", blueprint_id)

    async def get_all_agents(self) -> list[dict[str, Any]]:
        return await self.driver.query("agents")

    async def create_agent(self, agent_data: dict[str, Any]) -> str:
        doc_id = agent_data["id"]
        return await self.driver.upsert("agents", agent_data, doc_id)

    async def update_agent(self, agent_id: str, updates: dict[str, Any]) -> bool:
        agent = await self.get_agent_by_id(agent_id)
        if not agent:
            return False
        return await self.driver.update("agents", agent_id, updates)

    async def delete_agent(self, agent_id: str) -> bool:
        agent = await self.get_agent_by_id(agent_id)
        if not agent:
            return False
        return await self.driver.delete("agents", agent_id)

    async def get_dimension_by_id(self, dimension_id: str) -> dict[str, Any] | None:
        return await self.driver.get("dimensions", dimension_id)

    async def get_all_dimensions(self) -> list[dict[str, Any]]:
        return await self.driver.query("dimensions")

    async def create_dimension(self, dimension_data: dict[str, Any]) -> str:
        doc_id = dimension_data["id"]
        return await self.driver.upsert("dimensions", dimension_data, doc_id)

    async def update_dimension(self, dimension_id: str, updates: dict[str, Any]) -> str:
        dimension = await self.get_dimension_by_id(dimension_id)
        if not dimension:
            raise ValueError(f"Observation {dimension_id} not found")
        await self.driver.update("dimensions", dimension_id, updates)
        return dimension_id

    async def delete_dimension(self, dimension_id: str) -> bool:
        dimension = await self.get_dimension_by_id(dimension_id)
        if not dimension:
            return False
        return await self.driver.delete("dimensions", dimension_id)

    async def get_output_config_by_id(self, config_id: str) -> dict[str, Any] | None:
        return await self.driver.get("output_configs", config_id)

    async def get_all_output_configs(self) -> list[dict[str, Any]]:
        return await self.driver.query("output_configs")

    async def create_output_config(self, config_data: dict[str, Any]) -> str:
        doc_id = config_data["id"]
        return await self.driver.upsert("output_configs", config_data, doc_id)

    async def update_output_config(self, config_id: str, updates: dict[str, Any]) -> bool:
        config = await self.get_output_config_by_id(config_id)
        if not config:
            return False
        return await self.driver.update("output_configs", config_id, updates)

    async def delete_output_config(self, config_id: str) -> bool:
        config = await self.get_output_config_by_id(config_id)
        if not config:
            return False
        return await self.driver.delete("output_configs", config_id)

    async def update_component_metadata(self, component_id: str, module: str, component_class: str) -> bool:
        comp = await self.get_component_by_id(component_id)
        if not comp:
            return False
        return await self.driver.update("components", component_id, {"module": module, "class_name": component_class})

    async def register_component(self, component_data: dict[str, Any]) -> str:
        doc_id = component_data["id"]
        return await self.driver.upsert("components", component_data, doc_id)

    async def create_component(self, component_data: dict[str, Any]) -> str:
        return await self.register_component(component_data)

    async def update_component(self, component_id: str, updates: dict[str, Any]) -> str:
        comp = await self.get_component_by_id(component_id)
        if not comp:
            raise ValueError(f"LegacyPromptBlock {component_id} not found")
        await self.driver.update("components", component_id, updates)
        return component_id

    async def delete_component(self, component_id: str) -> bool:
        comp = await self.get_component_by_id(component_id)
        if not comp:
            return False
        return await self.driver.delete("components", component_id)

    # --- Banned Phrases ---

    async def get_banned_phrases(self) -> list[dict[str, Any]]:
        return await self.driver.query("banned_phrases")

    async def add_banned_phrase(self, phrase: str, language: str = "en") -> None:
        # Check duplicate
        existing = await self.driver.query("banned_phrases", [Filter("phrase", "==", phrase)], limit=1)
        if not existing:
            doc_id = str(uuid.uuid4())
            await self.driver.upsert("banned_phrases", {"phrase": phrase, "language": language, "id": doc_id}, doc_id)

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

    async def get_concepts(self) -> list[dict[str, Any]]:
        return await self.driver.query("concepts")

    async def get_references(self) -> list[dict[str, Any]]:
        return await self.driver.query("references")

    async def get_claims(self) -> list[dict[str, Any]]:
        return await self.driver.query("claims")

    async def add_concept(self, item: dict[str, Any]) -> str:
        doc_id = item["id"]
        return await self.driver.upsert("concepts", item, doc_id)

    async def add_reference(self, item: dict[str, Any]) -> str:
        doc_id = item["id"]
        return await self.driver.upsert("references", item, doc_id)

    async def add_claim(self, item: dict[str, Any]) -> str:
        doc_id = item["id"]
        return await self.driver.upsert("claims", item, doc_id)

    async def clear_knowledge_base(self) -> None:
        """Removes all items from the separated knowledge base collections."""
        await self.driver.clear("concepts")
        await self.driver.clear("references")
        await self.driver.clear("claims")

    async def get_model_registry(self) -> dict[str, Any]:
        res = await self.driver.get("system_config", "model_registry")
        if not res:
            logger.error(
                "[MockRepository] SYSTEM_CONFIG_NOT_FOUND: "
                "'model_registry' document is missing from database."
            )
            from backend_v2.exceptions import ResourceNotFoundError
            raise ResourceNotFoundError(resource_type="system_config", resource_id="model_registry")
        return res

    async def update_model_registry(self, registry_data: dict[str, Any]) -> bool:
        doc_id = registry_data.get("id", "model_registry")
        if doc_id != "model_registry" and "slug" not in registry_data:
            registry_data["slug"] = "model_registry"
        await self.driver.upsert("system_config", registry_data, doc_id)
        return True

    async def get_system_settings(self) -> dict[str, Any] | None:
        res = await self.driver.get("system_config", "global_settings")
        if not res:
            logger.error(
                "[MockRepository] SYSTEM_CONFIG_NOT_FOUND: "
                "'global_settings' document is missing from database."
            )
            from backend_v2.exceptions import ResourceNotFoundError
            raise ResourceNotFoundError(resource_type="system_config", resource_id="global_settings")
        return res

    async def update_system_settings(self, updates: dict[str, Any]) -> bool:
        doc_id = updates.get("id", "global_settings")
        if doc_id != "global_settings" and "slug" not in updates:
            updates["slug"] = "global_settings"
        await self.driver.upsert("system_config", updates, doc_id)
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
            if not isinstance(content, dict):
                continue
            criteria = content.get("criteria", [])
            if not isinstance(criteria, list):
                continue

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

    async def get_usage_aggregate(self, scope: str, entity_id: str | None, period: str) -> dict[str, Any] | None:
        agg_id = f"{scope}_{entity_id or 'system'}_{period}"
        return await self.driver.get("usage_aggregates", agg_id)

    async def upsert_usage_aggregate(
        self, scope: str, entity_id: str | None, period: str, update_data: dict[str, Any]
    ) -> None:
        agg_id = f"{scope}_{entity_id or 'system'}_{period}"
        update_data["id"] = agg_id
        update_data["scope"] = scope
        if entity_id:
            update_data["entity_id"] = entity_id
        update_data["period"] = period

        existing = await self.get_usage_aggregate(scope, entity_id, period)
        if existing:
            import copy
            merged = copy.deepcopy(existing)
            merged["total_executions"] = existing.get("total_executions", 0) + update_data.get("total_executions", 0)

            ex_usage = existing.get("usage", {})
            up_usage = update_data.get("usage", {})
            merged["usage"] = {
                "prompt_tokens": ex_usage.get("prompt_tokens", 0) + up_usage.get("prompt_tokens", 0),
                "completion_tokens": ex_usage.get("completion_tokens", 0) + up_usage.get("completion_tokens", 0),
                "total_tokens": ex_usage.get("total_tokens", 0) + up_usage.get("total_tokens", 0),
                "cached_tokens": ex_usage.get("cached_tokens", 0) + up_usage.get("cached_tokens", 0),
                "reasoning_tokens": ex_usage.get("reasoning_tokens", 0) + up_usage.get("reasoning_tokens", 0),
                "cost_usd": ex_usage.get("cost_usd", 0.0) + up_usage.get("cost_usd", 0.0)
            }
            await self.driver.upsert("usage_aggregates", merged, agg_id)
        else:
            if "usage" not in update_data:
                update_data["usage"] = {}
            for k in ["prompt_tokens", "completion_tokens", "total_tokens", "cached_tokens", "reasoning_tokens"]:
                if k not in update_data["usage"]:
                    update_data["usage"][k] = update_data.get(k, 0)
            if "cost_usd" not in update_data["usage"]:
                update_data["usage"]["cost_usd"] = update_data.get("cost_usd", 0.0)

            await self.driver.upsert("usage_aggregates", update_data, agg_id)

    async def get_usage_records(
        self, scope: str, entity_id: str | None = None, since: str | None = None
    ) -> list[dict[str, Any]]:
        filters = []
        if scope == "organization" and entity_id:
            filters.append(Filter("org_id", "==", entity_id))
        elif scope == "user" and entity_id:
            filters.append(Filter("user_id", "==", entity_id))

        if since:
            filters.append(Filter("timestamp", ">=", since))

        return await self.driver.query("usage", filters)

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
            await self.driver.delete("executions", e.id)

        # Workflows
        wfs = await self.get_all_workflows(organization_id=org_id)
        for w in wfs:
            await self.driver.delete("workflows", w["id"])

    async def get_org_usage_total(self, org_id: str, since: str | None = None) -> float:
        filters = [Filter("organization_id", "==", org_id)]
        if since:
            filters.append(Filter("completed_at", ">=", since))

        # Fetch all matched executions
        execs = await self.driver.query("executions", filters)
        return float(sum(e.get("cost_estimate", 0.0) for e in execs))

    async def get_detailed_usage(
        self, scope: str, target_id: str | None = None, since: str | None = None
    ) -> dict[str, Any]:
        filters = []
        if since:
            filters.append(Filter("completed_at", ">=", since))

        if scope == "user" and target_id:
            filters.append(Filter("user_id", "==", target_id))
        elif scope == "org" and target_id:
            filters.append(Filter("organization_id", "==", target_id))
        # if scope == "system", no id filter

        execs = await self.driver.query("executions", filters)

        total_cost = 0.0
        total_runs = len(execs)
        total_time = 0
        models_used: dict[str, int] = {}
        workflows_used: dict[str, int] = {}

        for e in execs:
            total_cost += e.get("cost_estimate", 0.0)

            # Duration (if available)
            total_time += e.get("duration_ms", 0)

            # Workflows
            wid = e.get("workflow_id")
            if wid:
                workflows_used[wid] = workflows_used.get(wid, 0) + 1

            # Models
            mu = e.get("models_used", {})
            if isinstance(mu, dict):
                for m, count in mu.items():
                    models_used[m] = models_used.get(m, 0) + count

        # Map workflow IDs to human-readable names
        if workflows_used:
            try:
                # get_all_workflows is an abstract method implemented by driver wrappers
                all_workflows = await self.get_all_workflows(organization_id=target_id if scope == "org" else None)
                wf_names = {w["id"]: w.get("name", w["id"]) for w in all_workflows}

                named_workflows_used: dict[str, int] = {}
                for wid, count in workflows_used.items():
                    name = wf_names.get(wid, wid)
                    name_str = str(name)
                    named_workflows_used[name_str] = named_workflows_used.get(name_str, 0) + count
                workflows_used = named_workflows_used
            except Exception as ex:
                logger.warning(f"Could not map workflow names: {ex}")

        # Gather token analytics from UsageAggregates
        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0
        cached_tokens = 0
        reasoning_tokens = 0

        # Determine period for aggregate lookup
        period = "all-time"
        if since:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
                period = dt.strftime("%Y-%m")
            except Exception as e:
                logger.warning(f"Virheellinen päivämäärämuoto '{since}', palataan all-time -näkymään: {e}")

        mapped_scope = "organization" if scope == "org" else scope
        agg = await self.get_usage_aggregate(mapped_scope, target_id, period)
        if agg:
            usage_data = agg.get("usage", {})
            prompt_tokens = usage_data.get("prompt_tokens", 0)
            completion_tokens = usage_data.get("completion_tokens", 0)
            total_tokens = usage_data.get("total_tokens", 0)
            cached_tokens = usage_data.get("cached_tokens", 0)
            reasoning_tokens = usage_data.get("reasoning_tokens", 0)

        return {
            "total_cost_usd": total_cost,
            "total_runs": total_runs,
            "total_processing_time_ms": total_time,
            "models_used": models_used,
            "workflows_used": workflows_used,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "cached_tokens": cached_tokens,
            "reasoning_tokens": reasoning_tokens
        }

class AppendOnlyRepository(UnifiedWorkflowRepository):
    """V2 Append-Only Repository.
    Overrides update methods to enforce snapshotting of the old version (is_latest=False)
    and creating a new versionized document.
    """

    def _increment_version(self, id_str: str) -> tuple[str, str, int]:
        """Parses an ID into (slug, full_new_id, version)."""
        if "_v" in id_str:
            slug, v_str = id_str.rsplit("_v", 1)
            try:
                version = int(v_str) + 1
            except ValueError:
                version = 2
        else:
            slug = id_str
            version = 2

        new_id = f"{slug}_v{version}"
        return slug, new_id, version

    async def update_workflow(self, workflow_id: str, updates: dict[str, Any]) -> str:
        """Append-only update for workflow."""
        old_doc = await self.get_workflow_by_id(workflow_id)
        if not old_doc:
            raise ValueError(f"Workflow {workflow_id} not found")

        # Set old document is_latest to False
        await self.driver.update("workflows", workflow_id, {"is_latest": False})

        # Insert new version
        slug, new_id, ver = self._increment_version(workflow_id)

        new_doc = dict(old_doc)
        new_doc.update(updates)
        new_doc["id"] = new_id
        new_doc["is_latest"] = True
        new_doc["version"] = ver
        new_doc["slug"] = slug

        await self.driver.upsert("workflows", new_doc, new_id)
        return new_id

    async def update_agent(self, agent_id: str, updates: dict[str, Any]) -> bool:
        """Append-only update for agent."""
        old_doc = await self.get_agent_by_id(agent_id)
        if not old_doc:
            return False

        await self.driver.update("agents", agent_id, {"is_latest": False})

        slug, new_id, ver = self._increment_version(agent_id)

        new_doc = dict(old_doc)
        new_doc.update(updates)
        new_doc["id"] = new_id
        new_doc["is_latest"] = True
        new_doc["version"] = ver
        new_doc["slug"] = slug

        await self.driver.upsert("agents", new_doc, new_id)
        return True

    async def update_prompt_block(self, prompt_block_id: str, updates: dict[str, Any]) -> bool:
        """Append-only update for prompt block."""
        old_doc = await self.get_prompt_block_by_id(prompt_block_id)
        if not old_doc:
            return False

        await self.driver.update("prompt_blocks", prompt_block_id, {"is_latest": False})

        slug, new_id, ver = self._increment_version(prompt_block_id)

        new_doc = dict(old_doc)
        new_doc.update(updates)
        new_doc["id"] = new_id
        new_doc["is_latest"] = True
        new_doc["version"] = ver
        new_doc["slug"] = slug

        await self.driver.upsert("prompt_blocks", new_doc, new_id)
        return True

    async def update_task_blueprint(self, blueprint_id: str, updates: dict[str, Any]) -> bool:
        """Append-only update for task blueprint."""
        old_doc = await self.get_task_blueprint_by_id(blueprint_id)
        if not old_doc:
            return False

        await self.driver.update("task_blueprints", blueprint_id, {"is_latest": False})

        slug, new_id, ver = self._increment_version(blueprint_id)

        new_doc = dict(old_doc)
        new_doc.update(updates)
        new_doc["id"] = new_id
        new_doc["is_latest"] = True
        new_doc["version"] = ver
        new_doc["slug"] = slug

        await self.driver.upsert("task_blueprints", new_doc, new_id)
        return True

