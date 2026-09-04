"""In-Memory Repository Fakes with Rust-Accelerated Snapshot Isolation & Deterministic Fault Injection.

Enforces zero-leak snapshot isolation across all 15 repository protocols:
Entities returned from fake repositories are deep-cloned via Pydantic V2 model validation,
guaranteeing `repo.get(id) is not repo.get(id)` and `repo.get(id) == repo.get(id)`.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel

from backend_v2.database.interfaces import (
    IAgentRepository,
    IAuditRepository,
    IComponentRepository,
    IExecutionPersonaRepository,
    IExecutionRepository,
    IExtractionProtocolRepository,
    IIdentityRepository,
    IKnowledgeRepository,
    IMatrixRepository,
    IOutputProfileRepository,
    IPromptBlockRepository,
    IRoleRepository,
    ISystemRepository,
    ITaskBlueprintRepository,
    IUnifiedWorkflowRepository,
    IWorkflowRepository,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import (
    Organization,
    OrganizationCreate,
    OrganizationUpdateDTO,
    SubscriptionStatus,
    User,
    UserCreate,
    UserUpdate,
)
from backend_v2.models.domain.base import (
    AuditLogCreateDTO,
    AuditLogEntry,
    DetailedUsageDTO,
    UsageAggregateDTO,
    UsageAggregateUpdateDTO,
    UsageRecord,
)
from backend_v2.models.domain.knowledge import (
    BannedPhrase,
    Claim,
    ClaimCreateDTO,
    Concept,
    ConceptCreateDTO,
    PromptTemplateDTO,
    Reference,
    ReferenceCreateDTO,
)
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, PromptBlock
from backend_v2.models.dtos.studio import StepCreateDTO, StepUpdateDTO, WorkflowCreateDTO, WorkflowUpdateDTO
from backend_v2.models.dtos.system import (
    AnySystemConfig,
    SystemConfigCreateDTO,
    SystemConfigUpdateDTO,
    SystemSettingsDTO,
)
from backend_v2.models.dtos.trace import ExecutionCreateDTO, ExecutionUpdateDTO
from backend_v2.models.state import TraceEvent
from backend_v2.models.v2_core import (
    ExecutionRecord,
    Role,
    Step,
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
    SystemConfigPerformativeLexicons,
    Workflow,
)


class BaseInMemoryRepository[T: BaseModel]:
    """Generic base in-memory repository providing Rust-accelerated snapshot isolation and fault injection."""

    def __init__(self) -> None:
        self._storage: dict[str, T] = {}
        self._faults: dict[str, tuple[Exception, int | None]] = {}
        self._call_counts: dict[str, int] = {}

    def _clone(self, item: T) -> T:
        """Deep-clone a Pydantic model using Rust-native validation/dumping."""
        return type(item).model_validate(item.model_dump(mode="python"), strict=False)

    def _save_isolated(self, key: str, item: T) -> None:
        """Save an isolated deep copy to in-memory store."""
        self._storage[key] = self._clone(item)

    def _get_isolated(self, key: str) -> T | None:
        """Retrieve an isolated deep copy from in-memory store."""
        item = self._storage.get(key)
        return self._clone(item) if item is not None else None

    def _list_isolated(self) -> list[T]:
        """Retrieve a list of isolated deep copies from in-memory store."""
        return [self._clone(item) for item in self._storage.values()]

    def _check_fault(self, method_name: str) -> None:
        """Check and trigger any injected faults before method execution."""
        self._call_counts[method_name] = (
            self._call_counts.get(method_name, 0) + 1  # noqa: QGR002 [REASON: Test fake call counter initialization]
        )
        if method_name in self._faults:
            exc, trigger_count = self._faults[method_name]
            if trigger_count is None:
                raise exc
            elif trigger_count > 0:
                self._faults[method_name] = (exc, trigger_count - 1)
                raise exc
            else:
                del self._faults[method_name]

    def inject_fault(self, method_name: str, exception: Exception, trigger_count: int | None = None) -> None:
        """Inject a deterministic fault into a repository method."""
        func = getattr(self, method_name, None)  # noqa: QGR001 [REASON: Test fake introspection to validate method existence for fault injection]
        if func is None or not callable(func):
            raise ValueError(f"Method '{method_name}' does not exist on {type(self).__name__}")
        self._faults[method_name] = (exception, trigger_count)

    def clear_faults(self, method_name: str | None = None) -> None:
        """Clear active fault triggers."""
        if method_name is not None:
            self._faults.pop(method_name, None)
        else:
            self._faults.clear()

    @asynccontextmanager
    async def fault_context(
        self, method_name: str, exception: Exception, trigger_count: int | None = 1
    ) -> AsyncIterator[None]:
        """Scoped async context manager for fault injection with guaranteed cleanup."""
        self.inject_fault(method_name, exception, trigger_count)
        try:
            yield
        finally:
            self.clear_faults(method_name)

    def get_call_count(self, method_name: str) -> int:
        """Get the number of times a method was invoked."""
        return self._call_counts.get(method_name, 0)  # noqa: QGR002 [REASON: Test fake call count query]


# ==============================================================================
# 1. Execution Repository Fake
# ==============================================================================


class InMemoryExecutionRepository(BaseInMemoryRepository[ExecutionRecord], IExecutionRepository):
    """In-memory fake implementation of IExecutionRepository with snapshot isolation."""

    async def get_execution(self, execution_id: str, hydrate: bool = True) -> ExecutionRecord | None:
        self._check_fault("get_execution")
        return self._get_isolated(execution_id)

    async def get_execution_status(self, execution_id: str) -> str | None:
        self._check_fault("get_execution_status")
        item = self._storage.get(execution_id)
        if item is None:
            return None
        return item.status.value if hasattr(item.status, "value") else str(item.status)  # noqa: QGR001 [REASON: Status enum or string resolution in fake]

    async def create_execution(self, execution_data: ExecutionCreateDTO) -> str:
        self._check_fault("create_execution")
        exec_id = execution_data.id or f"exe_{uuid.uuid4().hex[:16]}"
        data_dict = execution_data.model_dump(mode="python")
        data_dict["id"] = exec_id
        if "raw_inputs" not in data_dict or data_dict["raw_inputs"] is None:
            data_dict["raw_inputs"] = {}
        if "metadata" not in data_dict or data_dict["metadata"] is None:
            data_dict["metadata"] = {}
        record = ExecutionRecord.model_validate(data_dict)
        self._save_isolated(exec_id, record)
        return exec_id

    async def update_execution(self, execution_id: str, updates: ExecutionUpdateDTO) -> bool:
        self._check_fault("update_execution")
        existing = self._get_isolated(execution_id)
        if existing is None:
            return False
        dumped = existing.model_dump(mode="python")
        update_dict = updates.model_dump(mode="python", exclude_unset=True)
        dumped.update(update_dict)
        updated_record = ExecutionRecord.model_validate(dumped)
        self._save_isolated(execution_id, updated_record)
        return True

    async def append_trace_event(self, execution_id: str, event_data: TraceEvent) -> bool:
        self._check_fault("append_trace_event")
        existing = self._get_isolated(execution_id)
        if existing is None:
            return False
        cloned_event = type(event_data).model_validate(event_data.model_dump(mode="python"), strict=False)
        new_events = list(existing.execution_trace) + [cloned_event]
        updated_record = existing.model_copy(update={"execution_trace": new_events})
        self._save_isolated(execution_id, updated_record)
        return True

    async def delete_execution(self, execution_id: str) -> bool:
        self._check_fault("delete_execution")
        if execution_id in self._storage:
            del self._storage[execution_id]
            return True
        return False

    async def get_all_executions(
        self, organization_id: str | None = None, user_id: str | None = None
    ) -> list[ExecutionRecord]:
        self._check_fault("get_all_executions")
        items = self._list_isolated()
        if organization_id is not None:
            items = [x for x in items if x.organization_id == organization_id]
        if user_id is not None:
            items = [x for x in items if x.created_by == user_id]
        return items

    async def get_recent_completed_executions(self, limit: int = 5) -> list[ExecutionRecord]:
        self._check_fault("get_recent_completed_executions")
        return self._list_isolated()[:limit]

    async def count_executions_by_matrix(self, matrix_id: str) -> int:
        self._check_fault("count_executions_by_matrix")
        count = 0
        for x in self._storage.values():
            if isinstance(x.context_variables, dict) and x.context_variables.get("matrix_id") == matrix_id:  # noqa: QGR002, QGR012 [REASON: In-memory test fake filter simulation]
                count += 1
        return count


# ==============================================================================
# 2. Workflow Repository Fake
# ==============================================================================


class InMemoryWorkflowRepository(BaseInMemoryRepository[Workflow], IWorkflowRepository):
    """In-memory fake implementation of IWorkflowRepository with snapshot isolation."""

    def __init__(self) -> None:
        super().__init__()
        self._steps: dict[str, Step] = {}

    async def get_workflow_definition(self, workflow_id: str) -> Workflow | None:
        self._check_fault("get_workflow_definition")
        return self._get_isolated(workflow_id)

    async def get_workflow(self, workflow_id: str) -> Workflow | None:
        self._check_fault("get_workflow")
        return self._get_isolated(workflow_id)

    async def get_all_workflows(self, organization_id: str | None = None, role: str | None = None) -> list[Workflow]:
        self._check_fault("get_all_workflows")
        items = self._list_isolated()
        if role != "ROOT" and organization_id is not None:
            items = [w for w in items if w.organization_id in (organization_id, "root_system", None)]
        elif organization_id is not None:
            items = [w for w in items if w.organization_id == organization_id]
        return items

    async def get_workflow_by_id(self, workflow_id: str) -> Workflow | None:
        self._check_fault("get_workflow_by_id")
        return self._get_isolated(workflow_id)

    async def create_workflow(self, workflow_data: WorkflowCreateDTO) -> str:
        self._check_fault("create_workflow")
        wf_id = f"wf_{uuid.uuid4().hex[:16]}"
        data_dict = workflow_data.model_dump(mode="python")
        data_dict["id"] = wf_id
        if "default_profile_id" not in data_dict or data_dict["default_profile_id"] is None:
            data_dict["default_profile_id"] = "prof_default"
        if "status" not in data_dict or data_dict["status"] is None:
            data_dict["status"] = "ACTIVE"
        if "version" not in data_dict or data_dict["version"] is None:
            data_dict["version"] = 1
        if "description" not in data_dict or data_dict["description"] is None:
            data_dict["description"] = "Default description"
        model = Workflow.model_validate(data_dict)
        self._save_isolated(wf_id, model)
        return wf_id

    async def update_workflow(self, workflow_id: str, updates: WorkflowUpdateDTO) -> str:
        self._check_fault("update_workflow")
        existing = self._get_isolated(workflow_id)
        if existing is None:
            raise AppException(
                message=f"Workflow {workflow_id} not found",
                status_code=404,
                details={"error_code": ErrorCodes.WORKFLOW_NOT_FOUND.value},
            )
        dumped = existing.model_dump(mode="python")
        dumped.update(updates.model_dump(mode="python", exclude_unset=True))
        updated = Workflow.model_validate(dumped)
        self._save_isolated(workflow_id, updated)
        return workflow_id

    async def update_workflow_definition(self, workflow_id: str, definition_data: WorkflowUpdateDTO) -> str:
        self._check_fault("update_workflow_definition")
        return await self.update_workflow(workflow_id, definition_data)

    async def delete_workflow(self, workflow_id: str) -> bool:
        self._check_fault("delete_workflow")
        if workflow_id in self._storage:
            del self._storage[workflow_id]
            return True
        return False

    async def count_workflows(self) -> int:
        self._check_fault("count_workflows")
        return len(self._storage)

    async def get_all_steps(self) -> list[Step]:
        self._check_fault("get_all_steps")
        return [Step.model_validate(s.model_dump(mode="python"), strict=False) for s in self._steps.values()]

    async def get_step_by_id(self, step_id: str) -> Step | None:
        self._check_fault("get_step_by_id")
        s = self._steps.get(step_id)
        return Step.model_validate(s.model_dump(mode="python"), strict=False) if s else None

    async def get_step(self, step_id: str) -> Step | None:
        self._check_fault("get_step")
        return await self.get_step_by_id(step_id)

    async def create_step(self, step_data: StepCreateDTO) -> str:
        self._check_fault("create_step")
        s_id = f"stp_{uuid.uuid4().hex[:16]}"
        data_dict = step_data.model_dump(mode="python")
        data_dict["id"] = s_id
        model = Step.model_validate(data_dict)
        self._steps[s_id] = Step.model_validate(model.model_dump(mode="python"), strict=False)
        return s_id

    async def update_step(self, step_id: str, updates: StepUpdateDTO) -> str:
        self._check_fault("update_step")
        existing = self._steps.get(step_id)
        if existing is None:
            raise AppException(
                message=f"Step {step_id} not found",
                status_code=404,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )
        dumped = existing.model_dump(mode="python")
        dumped.update(updates.model_dump(mode="python", exclude_unset=True))
        updated = Step.model_validate(dumped)
        self._steps[step_id] = Step.model_validate(updated.model_dump(mode="python"), strict=False)
        return step_id

    async def delete_step(self, step_id: str, force_delete: bool = False) -> bool:
        self._check_fault("delete_step")
        if step_id in self._steps:
            del self._steps[step_id]
            return True
        return False

    async def save_workflow(self, workflow: Workflow) -> str:
        self._check_fault("save_workflow")
        self._save_isolated(workflow.id, workflow)
        return workflow.id

    async def save_step(self, step: Step) -> str:
        self._check_fault("save_step")
        self._steps[step.id] = Step.model_validate(step.model_dump(mode="python"), strict=False)
        return step.id


# ==============================================================================
# 3. Identity Repository Fake
# ==============================================================================


class InMemoryIdentityRepository(BaseInMemoryRepository[Organization], IIdentityRepository):
    """In-memory fake implementation of IIdentityRepository."""

    def __init__(self) -> None:
        super().__init__()
        self._users: dict[str, User] = {}
        self._usage_totals: dict[str, float] = {}

    async def list_organizations(self) -> list[Organization]:
        self._check_fault("list_organizations")
        return self._list_isolated()

    async def get_organization(self, org_id: str) -> Organization | None:
        self._check_fault("get_organization")
        return self._get_isolated(org_id)

    async def get_organization_model(self, org_id: str) -> Organization | None:
        self._check_fault("get_organization_model")
        return self._get_isolated(org_id)

    async def create_organization(self, org_data: OrganizationCreate | Organization) -> str:
        self._check_fault("create_organization")
        if isinstance(org_data, Organization):
            org = org_data
            org_id = org.id
        else:
            org_id = f"org_{uuid.uuid4().hex[:16]}"
            org = Organization(
                id=org_id,
                name=org_data.name,
                contact_email=org_data.admin_email,
                is_active=True,
                tier="free",
                subscription_status=SubscriptionStatus.ACTIVE,
                quota_limit=100.0,
                tpm_limit=org_data.tpm_limit,
                rpm_limit=org_data.rpm_limit,
            )
        self._save_isolated(org_id, org)
        return org_id

    async def update_organization(self, org_id: str, updates: OrganizationUpdateDTO) -> bool:
        self._check_fault("update_organization")
        existing = self._get_isolated(org_id)
        if existing is None:
            return False
        dumped = existing.model_dump(mode="python")
        dumped.update(updates.model_dump(mode="python", exclude_unset=True))
        updated = Organization.model_validate(dumped)
        self._save_isolated(org_id, updated)
        return True

    async def delete_organization(self, org_id: str) -> bool:
        self._check_fault("delete_organization")
        if org_id in self._storage:
            del self._storage[org_id]
            return True
        return False

    async def list_users(self, org_id: str | None = None) -> list[User]:
        self._check_fault("list_users")
        items = [User.model_validate(u.model_dump(mode="python"), strict=False) for u in self._users.values()]
        if org_id is not None:
            items = [u for u in items if u.organization_id == org_id]
        return items

    async def get_user(self, user_id: str) -> User | None:
        self._check_fault("get_user")
        u = self._users.get(user_id)
        return User.model_validate(u.model_dump(mode="python"), strict=False) if u else None

    async def get_user_by_email(self, email: str) -> User | None:
        self._check_fault("get_user_by_email")
        for u in self._users.values():
            if u.email == email:
                return User.model_validate(u.model_dump(mode="python"), strict=False)
        return None

    async def create_user(self, user_data: UserCreate | User) -> str:
        self._check_fault("create_user")
        if isinstance(user_data, User):
            u_id = user_data.id
            self._users[u_id] = User.model_validate(user_data.model_dump(mode="python"), strict=False)
            return u_id
        u_id = f"usr_{uuid.uuid4().hex[:16]}"
        data_dict = user_data.model_dump(mode="python")
        data_dict["id"] = u_id
        data_dict.pop("password", None)
        data_dict["created_at"] = datetime.now(timezone.utc)
        user = User.model_validate(data_dict)
        self._users[u_id] = User.model_validate(user.model_dump(mode="python"), strict=False)
        return u_id

    async def update_user(self, user_id: str, updates: UserUpdate) -> bool:
        self._check_fault("update_user")
        existing = self._users.get(user_id)
        if existing is None:
            return False
        dumped = existing.model_dump(mode="python")
        dumped.update(updates.model_dump(mode="python", exclude_unset=True))
        updated = User.model_validate(dumped)
        self._users[user_id] = User.model_validate(updated.model_dump(mode="python"), strict=False)
        return True

    async def delete_user(self, user_id: str) -> bool:
        self._check_fault("delete_user")
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False

    async def delete_org_data(self, org_id: str) -> None:
        self._check_fault("delete_org_data")
        self._storage.pop(org_id, None)
        self._users = {k: v for k, v in self._users.items() if v.organization_id != org_id}

    async def get_org_usage_total(self, org_id: str, since: str | None = None) -> float:
        self._check_fault("get_org_usage_total")
        return self._usage_totals.get(org_id, 0.0)  # noqa: QGR002 [REASON: Test fake usage total query with default 0.0]


# ==============================================================================
# 4. Component Repository Fake
# ==============================================================================


class InMemoryComponentRepository(BaseInMemoryRepository[PromptBlock], IComponentRepository):
    """In-memory fake implementation of IComponentRepository."""

    async def get_all_components(
        self, type: str | None = None, exclude_types: list[str] | None = None
    ) -> list[PromptBlock]:
        self._check_fault("get_all_components")
        items = self._list_isolated()
        if type is not None:
            items = [c for c in items if c.type == type or c.type.value == type]
        if exclude_types:
            items = [c for c in items if c.type not in exclude_types and c.type.value not in exclude_types]
        return items

    async def get_component_by_id(self, component_id: str) -> PromptBlock | None:
        self._check_fault("get_component_by_id")
        return self._get_isolated(component_id)

    async def get_component_by_name(self, name: str) -> PromptBlock | None:
        self._check_fault("get_component_by_name")
        for item in self._storage.values():
            if item.slug == name or any(v == name for v in item.label.translations.values()):
                return self._clone(item)
        return None

    async def update_component_metadata(self, component_id: str, module: str, component_class: str) -> bool:
        self._check_fault("update_component_metadata")
        existing = self._get_isolated(component_id)
        if existing is None:
            return False
        return True

    async def register_component(self, component_data: PromptBlock) -> str:
        self._check_fault("register_component")
        c_id = component_data.id
        self._save_isolated(c_id, component_data)
        return c_id

    async def create_component(self, component_data: PromptBlock) -> str:
        self._check_fault("create_component")
        return await self.register_component(component_data)

    async def update_component(self, component_id: str, updates: PromptBlock) -> str:
        self._check_fault("update_component")
        self._save_isolated(component_id, updates)
        return component_id

    async def delete_component(self, component_id: str) -> bool:
        self._check_fault("delete_component")
        if component_id in self._storage:
            del self._storage[component_id]
            return True
        return False

    async def get_components_using_dimension(self, dimension_id: str) -> list[str]:
        self._check_fault("get_components_using_dimension")
        matches: list[str] = []
        for c in self._storage.values():
            if isinstance(c, MatrixPromptBlock) and c.rows is not None:
                for row in c.rows:
                    if dimension_id in row.label.translations.values() or (
                        row.ai_description and dimension_id in row.ai_description
                    ):
                        matches.append(c.id)
                        break
        return matches


# ==============================================================================
# 5. Prompt Block Repository Fake
# ==============================================================================


class InMemoryPromptBlockRepository(BaseInMemoryRepository[PromptBlock], IPromptBlockRepository):
    """In-memory fake implementation of IPromptBlockRepository."""

    async def get_prompt_block_by_id(self, block_id: str) -> PromptBlock | None:
        self._check_fault("get_prompt_block_by_id")
        return self._get_isolated(block_id)

    async def get_prompt_block(self, block_id: str) -> PromptBlock | None:
        self._check_fault("get_prompt_block")
        return self._get_isolated(block_id)

    async def get_all_prompt_blocks(self) -> list[PromptBlock]:
        self._check_fault("get_all_prompt_blocks")
        return self._list_isolated()

    async def get_prompt_blocks_by_ids(self, block_ids: list[str], strict: bool = True) -> list[PromptBlock]:
        self._check_fault("get_prompt_blocks_by_ids")
        results: list[PromptBlock] = []
        for b_id in block_ids:
            block = self._get_isolated(b_id)
            if block is not None:
                results.append(block)
            elif strict:
                raise AppException(
                    message=f"Prompt block '{b_id}' not found.",
                    status_code=404,
                    details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
                )
        return results

    async def get_all_prompt_blocks_models(self) -> list[PromptBlock]:
        self._check_fault("get_all_prompt_blocks_models")
        return self._list_isolated()

    async def create_prompt_block(self, block_data: PromptBlock) -> str:
        self._check_fault("create_prompt_block")
        self._save_isolated(block_data.id, block_data)
        return block_data.id

    async def update_prompt_block(self, block_id: str, updates: PromptBlock) -> bool:
        self._check_fault("update_prompt_block")
        self._save_isolated(block_id, updates)
        return True

    async def delete_prompt_block(self, block_id: str, force_delete: bool = False) -> bool:
        self._check_fault("delete_prompt_block")
        if block_id in self._storage:
            del self._storage[block_id]
            return True
        return False


# ==============================================================================
# 6. Agent Repository Fake
# ==============================================================================


class InMemoryAgentRepository(BaseInMemoryRepository[PromptBlock], IAgentRepository):
    """In-memory fake implementation of IAgentRepository."""

    async def get_agent_by_id(self, agent_id: str) -> PromptBlock | None:
        self._check_fault("get_agent_by_id")
        return self._get_isolated(agent_id)

    async def get_all_agents(self) -> list[PromptBlock]:
        self._check_fault("get_all_agents")
        return self._list_isolated()

    async def create_agent(self, agent_data: PromptBlock) -> str:
        self._check_fault("create_agent")
        self._save_isolated(agent_data.id, agent_data)
        return agent_data.id

    async def update_agent(self, agent_id: str, updates: PromptBlock) -> bool:
        self._check_fault("update_agent")
        self._save_isolated(agent_id, updates)
        return True

    async def delete_agent(self, agent_id: str) -> bool:
        self._check_fault("delete_agent")
        if agent_id in self._storage:
            del self._storage[agent_id]
            return True
        return False


# ==============================================================================
# 7. Task Blueprint Repository Fake
# ==============================================================================


class InMemoryTaskBlueprintRepository(BaseInMemoryRepository[Step], ITaskBlueprintRepository):
    """In-memory fake implementation of ITaskBlueprintRepository."""

    async def get_task_blueprint_by_id(self, blueprint_id: str) -> Step | None:
        self._check_fault("get_task_blueprint_by_id")
        return self._get_isolated(blueprint_id)

    async def get_all_task_blueprints(self) -> list[Step]:
        self._check_fault("get_all_task_blueprints")
        return self._list_isolated()

    async def create_task_blueprint(self, blueprint_data: Step) -> str:
        self._check_fault("create_task_blueprint")
        self._save_isolated(blueprint_data.id, blueprint_data)
        return blueprint_data.id

    async def update_task_blueprint(self, blueprint_id: str, updates: StepUpdateDTO) -> bool:
        self._check_fault("update_task_blueprint")
        existing = self._get_isolated(blueprint_id)
        if existing is None:
            return False
        dumped = existing.model_dump(mode="python")
        dumped.update(updates.model_dump(mode="python", exclude_unset=True))
        updated = Step.model_validate(dumped)
        self._save_isolated(blueprint_id, updated)
        return True

    async def delete_task_blueprint(self, blueprint_id: str) -> bool:
        self._check_fault("delete_task_blueprint")
        if blueprint_id in self._storage:
            del self._storage[blueprint_id]
            return True
        return False


# ==============================================================================
# 8. Output Profile Repository Fake
# ==============================================================================


class InMemoryOutputProfileRepository(BaseInMemoryRepository[OutputProfile], IOutputProfileRepository):
    """In-memory fake implementation of IOutputProfileRepository."""

    async def get_all_output_profiles(self) -> list[OutputProfile]:
        self._check_fault("get_all_output_profiles")
        return self._list_isolated()

    async def get_all_output_profiles_models(self) -> list[OutputProfile]:
        self._check_fault("get_all_output_profiles_models")
        return self._list_isolated()

    async def get_output_profile_by_id(self, profile_id: str) -> OutputProfile | None:
        self._check_fault("get_output_profile_by_id")
        return self._get_isolated(profile_id)

    async def create_output_profile(self, profile_data: OutputProfile) -> str:
        self._check_fault("create_output_profile")
        self._save_isolated(profile_data.id, profile_data)
        return profile_data.id

    async def update_output_profile(self, profile_id: str, updates: OutputProfile) -> bool:
        self._check_fault("update_output_profile")
        self._save_isolated(profile_id, updates)
        return True

    async def delete_output_profile(self, profile_id: str) -> bool:
        self._check_fault("delete_output_profile")
        if profile_id in self._storage:
            del self._storage[profile_id]
            return True
        return False


# ==============================================================================
# 9. Knowledge Repository Fake
# ==============================================================================


class InMemoryKnowledgeRepository(BaseInMemoryRepository[Concept], IKnowledgeRepository):
    """In-memory fake implementation of IKnowledgeRepository."""

    def __init__(self) -> None:
        super().__init__()
        self._banned_phrases: dict[str, BannedPhrase] = {}
        self._prompt_templates: dict[str, PromptTemplateDTO] = {}
        self._concepts: dict[str, Concept] = {}
        self._references: dict[str, Reference] = {}
        self._claims: dict[str, Claim] = {}

    async def get_banned_phrases(self) -> list[BannedPhrase]:
        self._check_fault("get_banned_phrases")
        return [
            BannedPhrase.model_validate(b.model_dump(mode="python"), strict=False)
            for b in self._banned_phrases.values()
        ]

    async def add_banned_phrase(self, phrase: str, language: str = "en") -> None:
        self._check_fault("add_banned_phrase")
        bp_id = f"bp_{uuid.uuid4().hex[:16]}"
        self._banned_phrases[phrase] = BannedPhrase(id=bp_id, phrase=phrase, language=language)

    async def delete_banned_phrase(self, phrase: str) -> bool:
        self._check_fault("delete_banned_phrase")
        if phrase in self._banned_phrases:
            del self._banned_phrases[phrase]
            return True
        return False

    async def get_prompt_template(self, template_id: str) -> PromptTemplateDTO | None:
        self._check_fault("get_prompt_template")
        t = self._prompt_templates.get(template_id)
        return PromptTemplateDTO.model_validate(t.model_dump(mode="python"), strict=False) if t else None

    async def get_concepts(self) -> list[Concept]:
        self._check_fault("get_concepts")
        return [Concept.model_validate(c.model_dump(mode="python"), strict=False) for c in self._concepts.values()]

    async def get_references(self) -> list[Reference]:
        self._check_fault("get_references")
        return [Reference.model_validate(r.model_dump(mode="python"), strict=False) for r in self._references.values()]

    async def get_claims(self) -> list[Claim]:
        self._check_fault("get_claims")
        return [Claim.model_validate(c.model_dump(mode="python"), strict=False) for c in self._claims.values()]

    async def add_concept(self, item: ConceptCreateDTO) -> str:
        self._check_fault("add_concept")
        c_id = f"c_{uuid.uuid4().hex[:16]}"
        data_dict = item.model_dump(mode="python")
        data_dict["id"] = c_id
        model = Concept.model_validate(data_dict)
        self._concepts[c_id] = Concept.model_validate(model.model_dump(mode="python"), strict=False)
        return c_id

    async def add_reference(self, item: ReferenceCreateDTO) -> str:
        self._check_fault("add_reference")
        r_id = f"ref_{uuid.uuid4().hex[:16]}"
        data_dict = item.model_dump(mode="python")
        data_dict["id"] = r_id
        model = Reference.model_validate(data_dict)
        self._references[r_id] = Reference.model_validate(model.model_dump(mode="python"), strict=False)
        return r_id

    async def add_claim(self, item: ClaimCreateDTO) -> str:
        self._check_fault("add_claim")
        cl_id = f"cl_{uuid.uuid4().hex[:16]}"
        data_dict = item.model_dump(mode="python")
        data_dict["id"] = cl_id
        model = Claim.model_validate(data_dict)
        self._claims[cl_id] = Claim.model_validate(model.model_dump(mode="python"), strict=False)
        return cl_id

    async def clear_knowledge_base(self) -> None:
        self._check_fault("clear_knowledge_base")
        self._concepts.clear()
        self._references.clear()
        self._claims.clear()


# ==============================================================================
# 10. System Repository Fake
# ==============================================================================


class InMemorySystemRepository(BaseInMemoryRepository[AnySystemConfig], ISystemRepository):
    """In-memory fake implementation of ISystemRepository."""

    def __init__(self) -> None:
        super().__init__()
        self._model_registry = SystemConfigModelRegistry(id="sys_1234567890abcdef1234567890abcdef", models={})
        self._mcp_gateways = SystemConfigMCPGateways(id="sys_abcdef1234567890abcdef1234567890", tools=[])
        self._system_settings: SystemSettingsDTO | None = None

    async def get_model_registry(self) -> SystemConfigModelRegistry:
        self._check_fault("get_model_registry")
        return SystemConfigModelRegistry.model_validate(self._model_registry.model_dump(mode="python"), strict=False)

    async def update_model_registry(self, registry_data: SystemConfigModelRegistry) -> bool:
        self._check_fault("update_model_registry")
        self._model_registry = SystemConfigModelRegistry.model_validate(
            registry_data.model_dump(mode="python"), strict=False
        )
        return True

    async def get_mcp_gateways(self, id: str | None = None) -> SystemConfigMCPGateways:
        self._check_fault("get_mcp_gateways")
        return SystemConfigMCPGateways.model_validate(self._mcp_gateways.model_dump(mode="python"), strict=False)

    async def update_mcp_gateways(self, gateways_data: SystemConfigMCPGateways) -> bool:
        self._check_fault("update_mcp_gateways")
        self._mcp_gateways = SystemConfigMCPGateways.model_validate(
            gateways_data.model_dump(mode="python"), strict=False
        )
        return True

    async def get_system_settings(self) -> SystemSettingsDTO | None:
        self._check_fault("get_system_settings")
        if self._system_settings is None:
            return None
        return SystemSettingsDTO.model_validate(self._system_settings.model_dump(mode="python"), strict=False)

    async def update_system_settings(self, updates: SystemConfigUpdateDTO) -> bool:
        self._check_fault("update_system_settings")
        if updates.system_settings is not None:
            self._system_settings = SystemSettingsDTO.model_validate(
                updates.system_settings.model_dump(mode="python"), strict=False
            )
            return True
        return False

    async def get_system_config(self, config_id: str) -> AnySystemConfig | None:
        self._check_fault("get_system_config")
        return self._get_isolated(config_id)

    async def create_system_config(self, config_data: SystemConfigCreateDTO) -> str:
        self._check_fault("create_system_config")
        c_id = f"cfg_{config_data.type}"
        self._save_isolated(c_id, config_data.content)
        return c_id

    async def update_performative_lexicons(self, lexicons_data: SystemConfigPerformativeLexicons) -> bool:
        self._check_fault("update_performative_lexicons")
        self._save_isolated(lexicons_data.id, lexicons_data)
        return True


# ==============================================================================
# 11. Audit Repository Fake
# ==============================================================================


class InMemoryAuditRepository(BaseInMemoryRepository[AuditLogEntry], IAuditRepository):
    """In-memory fake implementation of IAuditRepository."""

    def __init__(self) -> None:
        super().__init__()
        self._audit_logs: list[AuditLogEntry] = []
        self._usage_records: list[UsageRecord] = []
        self._usage_aggregates: dict[str, UsageAggregateDTO] = {}

    async def log_audit_event(self, event_data: AuditLogCreateDTO) -> None:
        self._check_fault("log_audit_event")
        ts = event_data.timestamp or datetime.now(timezone.utc)
        ctx: dict[str, Any] = {
            "actor_id": event_data.actor_id,
            "action": event_data.action,
        }
        if event_data.organization_id is not None:
            ctx["organization_id"] = event_data.organization_id
        if event_data.details is not None:
            ctx["details"] = event_data.details
        entry = AuditLogEntry(
            timestamp=ts,
            level="INFO",
            message=f"{event_data.actor_id}: {event_data.action}",
            context=ctx,
        )
        self._audit_logs.append(entry)

    async def get_audit_logs(
        self,
        organization_id: str | None = None,
        actor_id: str | None = None,
        action: str | None = None,
        limit: int = 100,
    ) -> list[AuditLogEntry]:
        self._check_fault("get_audit_logs")
        logs = [AuditLogEntry.model_validate(e.model_dump(mode="python"), strict=False) for e in self._audit_logs]
        if organization_id is not None:
            logs = [
                entry
                for entry in logs
                if entry.context is not None and entry.context.get("organization_id") == organization_id
            ]
        if actor_id is not None:
            logs = [entry for entry in logs if entry.context is not None and entry.context.get("actor_id") == actor_id]
        if action is not None:
            logs = [entry for entry in logs if entry.context is not None and entry.context.get("action") == action]
        return logs[:limit]

    async def log_usage(self, record: UsageRecord) -> None:
        self._check_fault("log_usage")
        self._usage_records.append(UsageRecord.model_validate(record.model_dump(mode="python"), strict=False))

    async def get_usage_records(
        self, scope: str, entity_id: str | None = None, since: str | None = None
    ) -> list[UsageRecord]:
        self._check_fault("get_usage_records")
        return [UsageRecord.model_validate(r.model_dump(mode="python"), strict=False) for r in self._usage_records]

    async def get_usage_aggregate(self, scope: str, entity_id: str | None, period: str) -> UsageAggregateDTO | None:
        self._check_fault("get_usage_aggregate")
        key = f"{scope}:{entity_id}:{period}"
        agg = self._usage_aggregates.get(key)
        return UsageAggregateDTO.model_validate(agg.model_dump(mode="python"), strict=False) if agg else None

    async def upsert_usage_aggregate(
        self, scope: str, entity_id: str | None, period: str, update_data: UsageAggregateUpdateDTO
    ) -> None:
        self._check_fault("upsert_usage_aggregate")
        key = f"{scope}:{entity_id}:{period}"
        existing = self._usage_aggregates.get(key)
        org_id = entity_id or "system"
        if existing:
            self._usage_aggregates[key] = UsageAggregateDTO(
                organization_id=org_id,
                period=period,
                total_input_tokens=existing.total_input_tokens + update_data.input_tokens,
                total_output_tokens=existing.total_output_tokens + update_data.output_tokens,
                total_cached_tokens=existing.total_cached_tokens + update_data.cached_tokens,
                total_cost_usd=existing.total_cost_usd + update_data.cost_usd,
                execution_count=existing.execution_count + update_data.execution_count,
            )
        else:
            self._usage_aggregates[key] = UsageAggregateDTO(
                organization_id=org_id,
                period=period,
                total_input_tokens=update_data.input_tokens,
                total_output_tokens=update_data.output_tokens,
                total_cached_tokens=update_data.cached_tokens,
                total_cost_usd=update_data.cost_usd,
                execution_count=update_data.execution_count,
            )

    async def get_detailed_usage(
        self, scope: str, target_id: str | None = None, since: str | None = None
    ) -> DetailedUsageDTO:
        self._check_fault("get_detailed_usage")
        return DetailedUsageDTO(
            organization_id=target_id or "system",
            total_cost_usd=0.0,
            total_tokens=0,
            by_model={},
            by_workflow={},
        )


# ==============================================================================
# 12. Matrix Repository Fake
# ==============================================================================


class InMemoryMatrixRepository(BaseInMemoryRepository[PromptBlock], IMatrixRepository):
    """In-memory fake implementation of IMatrixRepository."""

    async def get_all_matrices(self) -> list[PromptBlock]:
        self._check_fault("get_all_matrices")
        return self._list_isolated()

    async def get_matrix_by_id(self, matrix_id: str) -> PromptBlock | None:
        self._check_fault("get_matrix_by_id")
        return self._get_isolated(matrix_id)

    async def create_matrix(self, matrix_data: PromptBlock) -> str:
        self._check_fault("create_matrix")
        self._save_isolated(matrix_data.id, matrix_data)
        return matrix_data.id

    async def update_matrix(self, matrix_id: str, updates: PromptBlock) -> str:
        self._check_fault("update_matrix")
        self._save_isolated(matrix_id, updates)
        return matrix_id

    async def delete_matrix(self, matrix_id: str) -> bool:
        self._check_fault("delete_matrix")
        if matrix_id in self._storage:
            del self._storage[matrix_id]
            return True
        return False

    async def get_matrices_using_dimension(self, dimension_id: str) -> list[str]:
        self._check_fault("get_matrices_using_dimension")
        matches: list[str] = []
        for c in self._storage.values():
            if isinstance(c, MatrixPromptBlock) and c.rows is not None:
                for row in c.rows:
                    if dimension_id in row.label.translations.values() or (
                        row.ai_description and dimension_id in row.ai_description
                    ):
                        matches.append(c.id)
                        break
        return matches


# ==============================================================================
# 13. Role Repository Fake
# ==============================================================================


class InMemoryRoleRepository(BaseInMemoryRepository[Role], IRoleRepository):
    """In-memory fake implementation of IRoleRepository."""

    async def get_all_roles(self) -> list[Role]:
        self._check_fault("get_all_roles")
        return self._list_isolated()

    async def get_role_by_id(self, role_id: str) -> Role | None:
        self._check_fault("get_role_by_id")
        return self._get_isolated(role_id)

    async def create_role(self, role_data: Role) -> str:
        self._check_fault("create_role")
        self._save_isolated(role_data.id, role_data)
        return role_data.id

    async def update_role(self, role_id: str, updates: Role) -> str:
        self._check_fault("update_role")
        self._save_isolated(role_id, updates)
        return role_id

    async def delete_role(self, role_id: str) -> bool:
        self._check_fault("delete_role")
        if role_id in self._storage:
            del self._storage[role_id]
            return True
        return False


# ==============================================================================
# 14. Execution Persona Repository Fake
# ==============================================================================


class InMemoryExecutionPersonaRepository(BaseInMemoryRepository[PromptBlock], IExecutionPersonaRepository):
    """In-memory fake implementation of IExecutionPersonaRepository."""

    async def get_all_execution_personas(self) -> list[PromptBlock]:
        self._check_fault("get_all_execution_personas")
        return self._list_isolated()

    async def get_execution_persona_by_id(self, persona_id: str) -> PromptBlock | None:
        self._check_fault("get_execution_persona_by_id")
        return self._get_isolated(persona_id)

    async def create_execution_persona(self, persona_data: PromptBlock) -> str:
        self._check_fault("create_execution_persona")
        self._save_isolated(persona_data.id, persona_data)
        return persona_data.id

    async def update_execution_persona(self, persona_id: str, updates: PromptBlock) -> str:
        self._check_fault("update_execution_persona")
        self._save_isolated(persona_id, updates)
        return persona_id

    async def delete_execution_persona(self, persona_id: str) -> bool:
        self._check_fault("delete_execution_persona")
        if persona_id in self._storage:
            del self._storage[persona_id]
            return True
        return False


# ==============================================================================
# 15. Extraction Protocol Repository Fake
# ==============================================================================


class InMemoryExtractionProtocolRepository(BaseInMemoryRepository[PromptBlock], IExtractionProtocolRepository):
    """In-memory fake implementation of IExtractionProtocolRepository."""

    async def get_all_extraction_protocols(self) -> list[PromptBlock]:
        self._check_fault("get_all_extraction_protocols")
        return self._list_isolated()

    async def get_extraction_protocol_by_id(self, protocol_id: str) -> PromptBlock | None:
        self._check_fault("get_extraction_protocol_by_id")
        return self._get_isolated(protocol_id)

    async def create_extraction_protocol(self, protocol_data: PromptBlock) -> str:
        self._check_fault("create_extraction_protocol")
        self._save_isolated(protocol_data.id, protocol_data)
        return protocol_data.id

    async def update_extraction_protocol(self, protocol_id: str, updates: PromptBlock) -> str:
        self._check_fault("update_extraction_protocol")
        self._save_isolated(protocol_id, updates)
        return protocol_id

    async def delete_extraction_protocol(self, protocol_id: str) -> bool:
        self._check_fault("delete_extraction_protocol")
        if protocol_id in self._storage:
            del self._storage[protocol_id]
            return True
        return False


# ==============================================================================
# 16. Unified Workflow Repository Composite Facade
# ==============================================================================


class InMemoryUnifiedWorkflowRepository(IUnifiedWorkflowRepository):
    """Composite in-memory facade satisfying IUnifiedWorkflowRepository."""

    def __init__(
        self,
        workflows: InMemoryWorkflowRepository | None = None,
        executions: InMemoryExecutionRepository | None = None,
        identities: InMemoryIdentityRepository | None = None,
        components: InMemoryComponentRepository | None = None,
        prompt_blocks: InMemoryPromptBlockRepository | None = None,
        agents: InMemoryAgentRepository | None = None,
        task_blueprints: InMemoryTaskBlueprintRepository | None = None,
        output_profiles: InMemoryOutputProfileRepository | None = None,
        knowledge: InMemoryKnowledgeRepository | None = None,
        system: InMemorySystemRepository | None = None,
        audit: InMemoryAuditRepository | None = None,
        matrices: InMemoryMatrixRepository | None = None,
        roles: InMemoryRoleRepository | None = None,
        execution_personas: InMemoryExecutionPersonaRepository | None = None,
        extraction_protocols: InMemoryExtractionProtocolRepository | None = None,
    ) -> None:
        self._workflows = workflows or InMemoryWorkflowRepository()
        self._executions = executions or InMemoryExecutionRepository()
        self._identities = identities or InMemoryIdentityRepository()
        self._components = components or InMemoryComponentRepository()
        self._prompt_blocks = prompt_blocks or InMemoryPromptBlockRepository()
        self._agents = agents or InMemoryAgentRepository()
        self._task_blueprints = task_blueprints or InMemoryTaskBlueprintRepository()
        self._output_profiles = output_profiles or InMemoryOutputProfileRepository()
        self._knowledge = knowledge or InMemoryKnowledgeRepository()
        self._system = system or InMemorySystemRepository()
        self._audit = audit or InMemoryAuditRepository()
        self._matrices = matrices or InMemoryMatrixRepository()
        self._roles = roles or InMemoryRoleRepository()
        self._execution_personas = execution_personas or InMemoryExecutionPersonaRepository()
        self._extraction_protocols = extraction_protocols or InMemoryExtractionProtocolRepository()

    # 1. Workflow
    async def get_workflow(self, workflow_id: str) -> Workflow | None:
        return await self._workflows.get_workflow(workflow_id)

    async def get_workflow_by_id(self, workflow_id: str) -> Workflow | None:
        return await self._workflows.get_workflow_by_id(workflow_id)

    async def get_workflow_definition(self, workflow_id: str) -> Workflow | None:
        return await self._workflows.get_workflow_definition(workflow_id)

    async def get_all_workflows(self, organization_id: str | None = None, role: str | None = None) -> list[Workflow]:
        return await self._workflows.get_all_workflows(organization_id, role)

    async def create_workflow(self, workflow_data: WorkflowCreateDTO) -> str:
        return await self._workflows.create_workflow(workflow_data)

    async def update_workflow(self, workflow_id: str, updates: WorkflowUpdateDTO) -> str:
        return await self._workflows.update_workflow(workflow_id, updates)

    async def update_workflow_definition(self, workflow_id: str, definition_data: WorkflowUpdateDTO) -> str:
        return await self._workflows.update_workflow_definition(workflow_id, definition_data)

    async def delete_workflow(self, workflow_id: str) -> bool:
        return await self._workflows.delete_workflow(workflow_id)

    async def count_workflows(self) -> int:
        return await self._workflows.count_workflows()

    async def get_step(self, step_id: str) -> Step | None:
        return await self._workflows.get_step(step_id)

    async def get_step_by_id(self, step_id: str) -> Step | None:
        return await self._workflows.get_step_by_id(step_id)

    async def get_all_steps(self) -> list[Step]:
        return await self._workflows.get_all_steps()

    async def create_step(self, step_data: StepCreateDTO) -> str:
        return await self._workflows.create_step(step_data)

    async def update_step(self, step_id: str, updates: StepUpdateDTO) -> str:
        return await self._workflows.update_step(step_id, updates)

    async def delete_step(self, step_id: str, force_delete: bool = False) -> bool:
        return await self._workflows.delete_step(step_id, force_delete)

    async def save_workflow(self, workflow: Workflow) -> str:
        return await self._workflows.save_workflow(workflow)

    async def save_step(self, step: Step) -> str:
        return await self._workflows.save_step(step)

    # 2. Execution
    async def create_execution(self, execution_data: ExecutionCreateDTO) -> str:
        return await self._executions.create_execution(execution_data)

    async def get_execution_status(self, execution_id: str) -> str | None:
        return await self._executions.get_execution_status(execution_id)

    async def update_execution(self, execution_id: str, updates: ExecutionUpdateDTO) -> bool:
        return await self._executions.update_execution(execution_id, updates)

    async def append_trace_event(self, execution_id: str, event_data: TraceEvent) -> bool:
        return await self._executions.append_trace_event(execution_id, event_data)

    async def get_execution(self, execution_id: str, hydrate: bool = True) -> ExecutionRecord | None:
        return await self._executions.get_execution(execution_id, hydrate)

    async def delete_execution(self, execution_id: str) -> bool:
        return await self._executions.delete_execution(execution_id)

    async def get_all_executions(
        self, organization_id: str | None = None, user_id: str | None = None
    ) -> list[ExecutionRecord]:
        return await self._executions.get_all_executions(organization_id, user_id)

    async def get_recent_completed_executions(self, limit: int = 5) -> list[ExecutionRecord]:
        return await self._executions.get_recent_completed_executions(limit)

    async def count_executions_by_matrix(self, matrix_id: str) -> int:
        return await self._executions.count_executions_by_matrix(matrix_id)

    # 3. Identity
    async def get_organization(self, org_id: str) -> Organization | None:
        return await self._identities.get_organization(org_id)

    async def get_organization_model(self, org_id: str) -> Organization | None:
        return await self._identities.get_organization_model(org_id)

    async def list_organizations(self) -> list[Organization]:
        return await self._identities.list_organizations()

    async def create_organization(self, org_data: OrganizationCreate | Organization) -> str:
        return await self._identities.create_organization(org_data)

    async def update_organization(self, org_id: str, updates: OrganizationUpdateDTO) -> bool:
        return await self._identities.update_organization(org_id, updates)

    async def delete_organization(self, org_id: str) -> bool:
        return await self._identities.delete_organization(org_id)

    async def get_user(self, user_id: str) -> User | None:
        return await self._identities.get_user(user_id)

    async def get_user_by_email(self, email: str) -> User | None:
        return await self._identities.get_user_by_email(email)

    async def list_users(self, org_id: str | None = None) -> list[User]:
        return await self._identities.list_users(org_id)

    async def create_user(self, user_data: UserCreate | User) -> str:
        return await self._identities.create_user(user_data)

    async def update_user(self, user_id: str, updates: UserUpdate) -> bool:
        return await self._identities.update_user(user_id, updates)

    async def delete_user(self, user_id: str) -> bool:
        return await self._identities.delete_user(user_id)

    async def delete_org_data(self, org_id: str) -> None:
        await self._identities.delete_org_data(org_id)

    async def get_org_usage_total(self, org_id: str, since: str | None = None) -> float:
        return await self._identities.get_org_usage_total(org_id, since)

    # 4. Component
    async def get_all_components(
        self, type: str | None = None, exclude_types: list[str] | None = None
    ) -> list[PromptBlock]:
        return await self._components.get_all_components(type, exclude_types)

    async def get_component_by_id(self, component_id: str) -> PromptBlock | None:
        return await self._components.get_component_by_id(component_id)

    async def get_component_by_name(self, name: str) -> PromptBlock | None:
        return await self._components.get_component_by_name(name)

    async def update_component_metadata(self, component_id: str, module: str, component_class: str) -> bool:
        return await self._components.update_component_metadata(component_id, module, component_class)

    async def register_component(self, component_data: PromptBlock) -> str:
        return await self._components.register_component(component_data)

    async def create_component(self, component_data: PromptBlock) -> str:
        return await self._components.create_component(component_data)

    async def update_component(self, component_id: str, updates: PromptBlock) -> str:
        return await self._components.update_component(component_id, updates)

    async def delete_component(self, component_id: str) -> bool:
        return await self._components.delete_component(component_id)

    async def get_components_using_dimension(self, dimension_id: str) -> list[str]:
        return await self._components.get_components_using_dimension(dimension_id)

    # 5. PromptBlock
    async def get_prompt_block(self, block_id: str) -> PromptBlock | None:
        return await self._prompt_blocks.get_prompt_block(block_id)

    async def get_prompt_block_by_id(self, block_id: str) -> PromptBlock | None:
        return await self._prompt_blocks.get_prompt_block_by_id(block_id)

    async def get_all_prompt_blocks(self) -> list[PromptBlock]:
        return await self._prompt_blocks.get_all_prompt_blocks()

    async def get_all_prompt_blocks_models(self) -> list[PromptBlock]:
        return await self._prompt_blocks.get_all_prompt_blocks_models()

    async def get_prompt_blocks_by_ids(self, block_ids: list[str], strict: bool = True) -> list[PromptBlock]:
        return await self._prompt_blocks.get_prompt_blocks_by_ids(block_ids, strict)

    async def create_prompt_block(self, block_data: PromptBlock) -> str:
        return await self._prompt_blocks.create_prompt_block(block_data)

    async def update_prompt_block(self, block_id: str, updates: PromptBlock) -> bool:
        return await self._prompt_blocks.update_prompt_block(block_id, updates)

    async def delete_prompt_block(self, block_id: str, force_delete: bool = False) -> bool:
        return await self._prompt_blocks.delete_prompt_block(block_id, force_delete)

    # 6. Agent
    async def get_all_agents(self) -> list[PromptBlock]:
        return await self._agents.get_all_agents()

    async def get_agent_by_id(self, agent_id: str) -> PromptBlock | None:
        return await self._agents.get_agent_by_id(agent_id)

    async def create_agent(self, agent_data: PromptBlock) -> str:
        return await self._agents.create_agent(agent_data)

    async def update_agent(self, agent_id: str, updates: PromptBlock) -> bool:
        return await self._agents.update_agent(agent_id, updates)

    async def delete_agent(self, agent_id: str) -> bool:
        return await self._agents.delete_agent(agent_id)

    # 7. TaskBlueprint
    async def get_all_task_blueprints(self) -> list[Step]:
        return await self._task_blueprints.get_all_task_blueprints()

    async def get_task_blueprint_by_id(self, blueprint_id: str) -> Step | None:
        return await self._task_blueprints.get_task_blueprint_by_id(blueprint_id)

    async def create_task_blueprint(self, blueprint_data: Step) -> str:
        return await self._task_blueprints.create_task_blueprint(blueprint_data)

    async def update_task_blueprint(self, blueprint_id: str, updates: StepUpdateDTO) -> bool:
        return await self._task_blueprints.update_task_blueprint(blueprint_id, updates)

    async def delete_task_blueprint(self, blueprint_id: str) -> bool:
        return await self._task_blueprints.delete_task_blueprint(blueprint_id)

    # 8. OutputProfile
    async def get_all_output_profiles(self) -> list[OutputProfile]:
        return await self._output_profiles.get_all_output_profiles()

    async def get_all_output_profiles_models(self) -> list[OutputProfile]:
        return await self._output_profiles.get_all_output_profiles_models()

    async def get_output_profile_by_id(self, profile_id: str) -> OutputProfile | None:
        return await self._output_profiles.get_output_profile_by_id(profile_id)

    async def create_output_profile(self, profile_data: OutputProfile) -> str:
        return await self._output_profiles.create_output_profile(profile_data)

    async def update_output_profile(self, profile_id: str, updates: OutputProfile) -> bool:
        return await self._output_profiles.update_output_profile(profile_id, updates)

    async def delete_output_profile(self, profile_id: str) -> bool:
        return await self._output_profiles.delete_output_profile(profile_id)

    # 9. Knowledge
    async def get_banned_phrases(self) -> list[BannedPhrase]:
        return await self._knowledge.get_banned_phrases()

    async def add_banned_phrase(self, phrase: str, language: str = "en") -> None:
        await self._knowledge.add_banned_phrase(phrase, language)

    async def delete_banned_phrase(self, phrase: str) -> bool:
        return await self._knowledge.delete_banned_phrase(phrase)

    async def get_prompt_template(self, template_id: str) -> PromptTemplateDTO | None:
        return await self._knowledge.get_prompt_template(template_id)

    async def get_concepts(self) -> list[Concept]:
        return await self._knowledge.get_concepts()

    async def add_concept(self, item: ConceptCreateDTO) -> str:
        return await self._knowledge.add_concept(item)

    async def get_references(self) -> list[Reference]:
        return await self._knowledge.get_references()

    async def add_reference(self, item: ReferenceCreateDTO) -> str:
        return await self._knowledge.add_reference(item)

    async def get_claims(self) -> list[Claim]:
        return await self._knowledge.get_claims()

    async def add_claim(self, item: ClaimCreateDTO) -> str:
        return await self._knowledge.add_claim(item)

    async def clear_knowledge_base(self) -> None:
        await self._knowledge.clear_knowledge_base()

    # 10. System
    async def get_model_registry(self) -> SystemConfigModelRegistry:
        return await self._system.get_model_registry()

    async def update_model_registry(self, registry_data: SystemConfigModelRegistry) -> bool:
        return await self._system.update_model_registry(registry_data)

    async def get_mcp_gateways(self, id: str | None = None) -> SystemConfigMCPGateways:
        return await self._system.get_mcp_gateways(id)

    async def update_mcp_gateways(self, gateways_data: SystemConfigMCPGateways) -> bool:
        return await self._system.update_mcp_gateways(gateways_data)

    async def get_system_settings(self) -> SystemSettingsDTO | None:
        return await self._system.get_system_settings()

    async def update_system_settings(self, updates: SystemConfigUpdateDTO) -> bool:
        return await self._system.update_system_settings(updates)

    async def get_system_config(self, config_id: str) -> AnySystemConfig | None:
        return await self._system.get_system_config(config_id)

    async def create_system_config(self, config_data: SystemConfigCreateDTO) -> str:
        return await self._system.create_system_config(config_data)

    async def update_performative_lexicons(self, lexicons_data: SystemConfigPerformativeLexicons) -> bool:
        return await self._system.update_performative_lexicons(lexicons_data)

    # 11. Audit
    async def log_audit_event(self, event_data: AuditLogCreateDTO) -> None:
        await self._audit.log_audit_event(event_data)

    async def get_audit_logs(
        self,
        organization_id: str | None = None,
        actor_id: str | None = None,
        action: str | None = None,
        limit: int = 100,
    ) -> list[AuditLogEntry]:
        return await self._audit.get_audit_logs(organization_id, actor_id, action, limit)

    async def log_usage(self, record: UsageRecord) -> None:
        await self._audit.log_usage(record)

    async def get_usage_records(
        self, scope: str, entity_id: str | None = None, since: str | None = None
    ) -> list[UsageRecord]:
        return await self._audit.get_usage_records(scope, entity_id, since)

    async def get_usage_aggregate(self, scope: str, entity_id: str | None, period: str) -> UsageAggregateDTO | None:
        return await self._audit.get_usage_aggregate(scope, entity_id, period)

    async def upsert_usage_aggregate(
        self, scope: str, entity_id: str | None, period: str, update_data: UsageAggregateUpdateDTO
    ) -> None:
        await self._audit.upsert_usage_aggregate(scope, entity_id, period, update_data)

    async def get_detailed_usage(
        self, scope: str, target_id: str | None = None, since: str | None = None
    ) -> DetailedUsageDTO:
        return await self._audit.get_detailed_usage(scope, target_id, since)

    # 12. Matrix
    async def get_all_matrices(self) -> list[PromptBlock]:
        return await self._matrices.get_all_matrices()

    async def get_matrix_by_id(self, matrix_id: str) -> PromptBlock | None:
        return await self._matrices.get_matrix_by_id(matrix_id)

    async def create_matrix(self, matrix_data: PromptBlock) -> str:
        return await self._matrices.create_matrix(matrix_data)

    async def update_matrix(self, matrix_id: str, updates: PromptBlock) -> str:
        return await self._matrices.update_matrix(matrix_id, updates)

    async def delete_matrix(self, matrix_id: str) -> bool:
        return await self._matrices.delete_matrix(matrix_id)

    async def get_matrices_using_dimension(self, dimension_id: str) -> list[str]:
        return await self._matrices.get_matrices_using_dimension(dimension_id)

    # 13. Role
    async def get_all_roles(self) -> list[Role]:
        return await self._roles.get_all_roles()

    async def get_role_by_id(self, role_id: str) -> Role | None:
        return await self._roles.get_role_by_id(role_id)

    async def create_role(self, role_data: Role) -> str:
        return await self._roles.create_role(role_data)

    async def update_role(self, role_id: str, updates: Role) -> str:
        return await self._roles.update_role(role_id, updates)

    async def delete_role(self, role_id: str) -> bool:
        return await self._roles.delete_role(role_id)

    # 14. Execution Persona
    async def get_all_execution_personas(self) -> list[PromptBlock]:
        return await self._execution_personas.get_all_execution_personas()

    async def get_execution_persona_by_id(self, persona_id: str) -> PromptBlock | None:
        return await self._execution_personas.get_execution_persona_by_id(persona_id)

    async def create_execution_persona(self, persona_data: PromptBlock) -> str:
        return await self._execution_personas.create_execution_persona(persona_data)

    async def update_execution_persona(self, persona_id: str, updates: PromptBlock) -> str:
        return await self._execution_personas.update_execution_persona(persona_id, updates)

    async def delete_execution_persona(self, persona_id: str) -> bool:
        return await self._execution_personas.delete_execution_persona(persona_id)

    # 15. Extraction Protocol
    async def get_all_extraction_protocols(self) -> list[PromptBlock]:
        return await self._extraction_protocols.get_all_extraction_protocols()

    async def get_extraction_protocol_by_id(self, protocol_id: str) -> PromptBlock | None:
        return await self._extraction_protocols.get_extraction_protocol_by_id(protocol_id)

    async def create_extraction_protocol(self, protocol_data: PromptBlock) -> str:
        return await self._extraction_protocols.create_extraction_protocol(protocol_data)

    async def update_extraction_protocol(self, protocol_id: str, updates: PromptBlock) -> str:
        return await self._extraction_protocols.update_extraction_protocol(protocol_id, updates)

    async def delete_extraction_protocol(self, protocol_id: str) -> bool:
        return await self._extraction_protocols.delete_extraction_protocol(protocol_id)
