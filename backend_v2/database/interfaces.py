"""Database Protocol Interfaces (ISP Refactoring).

These interfaces split the monolithic AbstractWorkflowRepository into
cohesive, role-based protocols according to the Interface Segregation Principle.
"""

from typing import Any, Protocol

from backend_v2.models.auth import Organization
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.v2_core import ExecutionRecord
from backend_v2.models.v2_core import Workflow as WorkflowDefinition


class IExecutionRepository(Protocol):
    async def get_execution(self, execution_id: str, hydrate: bool = True) -> ExecutionRecord | None:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def get_execution_status(self, execution_id: str) -> str | None:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def create_execution(self, execution_data: dict[str, Any]) -> str:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def update_execution(self, execution_id: str, updates: dict[str, Any]) -> bool:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def append_trace_event(self, execution_id: str, event_data: dict[str, Any]) -> bool:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def delete_execution(self, execution_id: str) -> bool:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def get_all_executions(
        self, organization_id: str | None = None, user_id: str | None = None
    ) -> list[ExecutionRecord]: ...
    async def get_recent_completed_executions(self, limit: int = 5) -> list[ExecutionRecord]:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def count_executions_by_matrix(self, matrix_id: str) -> int:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...


class IWorkflowRepository(Protocol):
    async def get_workflow_definition(self, workflow_id: str) -> WorkflowDefinition | None:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def get_workflow(self, workflow_id: str) -> WorkflowDefinition | None:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def get_all_workflows(
        self, organization_id: str | None = None, role: str | None = None
    ) -> list[dict[str, Any]]: ...
    async def get_workflow_by_id(self, workflow_id: str) -> dict[str, Any] | None:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def create_workflow(self, workflow_data: dict[str, Any]) -> str:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def update_workflow(self, workflow_id: str, updates: dict[str, Any]) -> str:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def update_workflow_definition(self, workflow_id: str, definition_data: dict[str, Any]) -> str:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def delete_workflow(self, workflow_id: str) -> bool:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def count_workflows(self) -> int:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def get_all_steps(self) -> list[dict[str, Any]]:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def get_step_by_id(self, step_id: str) -> dict[str, Any] | None:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def get_step(self, step_id: str) -> dict[str, Any] | None:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def create_step(self, step_data: dict[str, Any]) -> str:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def update_step(self, step_id: str, updates: dict[str, Any]) -> str:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def delete_step(self, step_id: str, force_delete: bool = False) -> bool:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...


class IIdentityRepository(Protocol):
    async def list_organizations(self) -> list[dict[str, Any]]:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def get_organization(self, org_id: str) -> dict[str, Any] | None:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def get_organization_model(self, org_id: str) -> Organization | None:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def create_organization(self, org_data: dict[str, Any]) -> str:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def update_organization(self, org_id: str, updates: dict[str, Any]) -> bool:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def delete_organization(self, org_id: str) -> bool:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def delete_org_data(self, org_id: str) -> None:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def get_org_usage_total(self, org_id: str, since: str | None = None) -> float:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def list_users(self, org_id: str | None = None) -> list[dict[str, Any]]:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def get_user(self, user_id: str) -> dict[str, Any] | None:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def create_user(self, user_data: dict[str, Any]) -> str:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def update_user(self, user_id: str, updates: dict[str, Any]) -> bool:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def delete_user(self, user_id: str) -> bool:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...


class IComponentRepository(Protocol):
    async def get_all_components(
        self, type: str | None = None, exclude_types: list[str] | None = None
    ) -> list[dict[str, Any]]: ...
    async def get_component_by_id(self, component_id: str) -> dict[str, Any] | None:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def get_component_by_name(self, name: str) -> dict[str, Any] | None:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def update_component_metadata(self, component_id: str, module: str, component_class: str) -> bool:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def register_component(self, component_data: dict[str, Any]) -> str:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def create_component(self, component_data: dict[str, Any]) -> str:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def update_component(self, component_id: str, updates: dict[str, Any]) -> str:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def delete_component(self, component_id: str) -> bool:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...


class IPromptBlockRepository(Protocol):
    async def get_prompt_block_by_id(self, block_id: str) -> dict[str, Any] | None:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def get_prompt_block(self, block_id: str) -> dict[str, Any] | None:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def get_all_prompt_blocks(self) -> list[dict[str, Any]]:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def create_prompt_block(self, block_data: dict[str, Any]) -> str:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def update_prompt_block(self, block_id: str, updates: dict[str, Any]) -> bool:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def delete_prompt_block(self, block_id: str, force_delete: bool = False) -> bool:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...


class IAgentRepository(Protocol):
    async def get_agent_by_id(self, agent_id: str) -> dict[str, Any] | None:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def get_all_agents(self) -> list[dict[str, Any]]:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def create_agent(self, agent_data: dict[str, Any]) -> str:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def update_agent(self, agent_id: str, updates: dict[str, Any]) -> bool:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def delete_agent(self, agent_id: str) -> bool:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...


class ITaskBlueprintRepository(Protocol):
    async def get_task_blueprint_by_id(self, blueprint_id: str) -> dict[str, Any] | None:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def get_all_task_blueprints(self) -> list[dict[str, Any]]:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def create_task_blueprint(self, blueprint_data: dict[str, Any]) -> str:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def update_task_blueprint(self, blueprint_id: str, updates: dict[str, Any]) -> bool:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def delete_task_blueprint(self, blueprint_id: str) -> bool:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...


class IOutputProfileRepository(Protocol):
    async def get_all_output_profiles(self) -> list[dict[str, Any]]:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def get_all_output_profiles_models(self) -> list[OutputProfile]:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def get_output_profile_by_id(self, profile_id: str) -> dict[str, Any] | None:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def create_output_profile(self, profile_data: dict[str, Any]) -> str:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def update_output_profile(self, profile_id: str, updates: dict[str, Any]) -> bool:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def delete_output_profile(self, profile_id: str) -> bool:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...


class IKnowledgeRepository(Protocol):
    async def get_banned_phrases(self) -> list[dict[str, Any]]:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def add_banned_phrase(self, phrase: str, language: str = "en") -> None:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def delete_banned_phrase(self, phrase: str) -> bool:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def get_prompt_template(self, template_id: str) -> dict[str, str] | None:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def get_concepts(self) -> list[dict[str, Any]]:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def get_references(self) -> list[dict[str, Any]]:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def get_claims(self) -> list[dict[str, Any]]:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def add_concept(self, item: dict[str, Any]) -> str:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def add_reference(self, item: dict[str, Any]) -> str:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def add_claim(self, item: dict[str, Any]) -> str:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def clear_knowledge_base(self) -> None:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...


class ISystemRepository(Protocol):
    async def get_model_registry(self) -> dict[str, Any]:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def update_model_registry(self, registry_data: dict[str, Any]) -> bool:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def get_mcp_gateways(self) -> dict[str, Any]:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def update_mcp_gateways(self, gateways_data: dict[str, Any]) -> bool:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def get_system_settings(self) -> dict[str, Any] | None:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def update_system_settings(self, updates: dict[str, Any]) -> bool:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def get_system_config(self, config_id: str) -> dict[str, Any] | None:
        """Gets a system configuration document."""
        ...

    async def create_system_config(self, config_data: dict[str, Any]) -> str:
        """Creates a new system configuration document."""
        ...


class IAuditRepository(Protocol):
    async def log_audit_event(self, event_data: dict[str, Any]) -> None:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def get_audit_logs(
        self,
        organization_id: str | None = None,
        actor_id: str | None = None,
        action: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]: ...
    async def log_usage(self, record: Any) -> None:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def get_usage_records(
        self, scope: str, entity_id: str | None = None, since: str | None = None
    ) -> list[dict[str, Any]]: ...
    async def get_detailed_usage(
        self, scope: str, target_id: str | None = None, since: str | None = None
    ) -> dict[str, Any]: ...
    async def get_usage_aggregate(self, scope: str, entity_id: str | None, period: str) -> dict[str, Any] | None:
        """Protocol method definition.

        Args:
            *args: Protocol arguments.
            **kwargs: Protocol keyword arguments.

        Returns:
            The specified return type.

        Raises:
            AppException: If the operation fails.
        """
        ...

    async def upsert_usage_aggregate(
        self, scope: str, entity_id: str | None, period: str, update_data: dict[str, Any]
    ) -> None: ...


class IMatrixRepository(Protocol):
    async def get_all_matrices(self) -> list[dict[str, Any]]: ...
    async def get_matrix_by_id(self, matrix_id: str) -> dict[str, Any] | None: ...
    async def create_matrix(self, matrix_data: dict[str, Any]) -> str: ...
    async def update_matrix(self, matrix_id: str, updates: dict[str, Any]) -> str: ...
    async def delete_matrix(self, matrix_id: str) -> bool: ...
    async def get_matrices_using_dimension(self, dimension_id: str) -> list[str]: ...


class IRoleRepository(Protocol):
    async def get_all_roles(self) -> list[dict[str, Any]]: ...
    async def get_role_by_id(self, role_id: str) -> dict[str, Any] | None: ...
    async def create_role(self, role_data: dict[str, Any]) -> str: ...
    async def update_role(self, role_id: str, updates: dict[str, Any]) -> str: ...
    async def delete_role(self, role_id: str) -> bool: ...


class IExecutionPersonaRepository(Protocol):
    async def get_all_execution_personas(self) -> list[dict[str, Any]]: ...
    async def get_execution_persona_by_id(self, persona_id: str) -> dict[str, Any] | None: ...
    async def create_execution_persona(self, persona_data: dict[str, Any]) -> str: ...
    async def update_execution_persona(self, persona_id: str, updates: dict[str, Any]) -> str: ...
    async def delete_execution_persona(self, persona_id: str) -> bool: ...


class IExtractionProtocolRepository(Protocol):
    async def get_all_extraction_protocols(self) -> list[dict[str, Any]]: ...
    async def get_extraction_protocol_by_id(self, protocol_id: str) -> dict[str, Any] | None: ...
    async def create_extraction_protocol(self, protocol_data: dict[str, Any]) -> str: ...
    async def update_extraction_protocol(self, protocol_id: str, updates: dict[str, Any]) -> str: ...
    async def delete_extraction_protocol(self, protocol_id: str) -> bool: ...
