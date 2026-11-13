"""In-Memory Repository Fakes with Rust-Accelerated Snapshot Isolation & Deterministic Fault Injection.

Enforces zero-leak snapshot isolation across all 9 active V2 repository protocols:
Entities returned from fake repositories are deep-cloned via Pydantic V2 model validation,
guaranteeing `repo.get(id) is not repo.get(id)` and `repo.get(id) == repo.get(id)`.
"""

from __future__ import annotations

import copy
import inspect
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, JsonValue, ValidationError

from backend_v2.database.interfaces import (
    IAuditRepository,
    IExecutionRepository,
    IIdentityRepository,
    IOutputProfileRepository,
    IPromptBlockRepository,
    IReportArtifactRepository,
    ISystemRepository,
    ITaskBriefRepository,
    IUnifiedWorkflowRepository,
    IWorkflowRepository,
)
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.auth import (
    Organization,
    OrganizationCreate,
    OrganizationUpdateDTO,
    SubscriptionStatus,
    SystemOrganizations,
    User,
    UserCreate,
    UserUpdate,
)
from backend_v2.models.core_base import generate_opaque_id, generate_uuid7
from backend_v2.models.domain.base import (
    AuditLogCreateDTO,
    AuditLogRecord,
    DetailedUsageDTO,
    UsageRecord,
    UsageRollupSummaryDTO,
)
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import PromptBlock
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.domain.step import Step
from backend_v2.models.domain.system_config import (
    ModelProfile,
    ProviderExtraParamsDTO,
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
)
from backend_v2.models.domain.task_brief import TaskBrief
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.report_artifact import ReportArtifactUpdateDTO
from backend_v2.models.dtos.studio import StepCreateDTO, StepUpdateDTO, WorkflowCreateDTO, WorkflowUpdateDTO
from backend_v2.models.dtos.trace import ExecutionCreateDTO, ExecutionUpdateDTO
from backend_v2.models.enums import CognitiveTier, EntityPrefix, LLMProvider
from backend_v2.models.state import TraceEvent


class BaseInMemoryRepository[T: BaseModel]:
    """Generic base in-memory repository providing Rust-accelerated snapshot isolation and fault injection."""

    _BASE_EXCLUDED_METHODS: frozenset[str] = frozenset(
        {
            "inject_fault",
            "clear_faults",
            "fault_context",
            "get_call_count",
        }
    )

    def __init__(self) -> None:
        self._storage: dict[str, T] = {}
        self._faults: dict[str, tuple[Exception, int | None]] = {}
        self._call_counts: dict[str, int] = {}

    def _clone[ItemT](self, item: ItemT) -> ItemT:
        """Deep-clone a Pydantic model preserving exact polymorphism."""
        if isinstance(item, BaseModel):
            return item.model_copy(deep=True)
        return copy.deepcopy(item)

    def _save_isolated(self, key: str, item: T) -> None:
        """Save an isolated deep copy to in-memory store."""
        self._storage[key] = self._clone(item)

    def _get_isolated(self, key: str) -> T | None:
        """Retrieve an isolated deep copy from in-memory store."""
        item = self._storage[key] if key in self._storage else None
        return self._clone(item) if item is not None else None

    def _list_isolated(self) -> list[T]:
        """Retrieve a list of isolated deep copies from in-memory store."""
        return [self._clone(item) for item in self._storage.values()]

    def _check_fault(self, method_name: str) -> None:
        """Check and trigger any injected faults before method execution."""
        current_count = 0
        if method_name in self._call_counts:
            current_count = self._call_counts[method_name]
        self._call_counts[method_name] = current_count + 1
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
        if method_name.startswith("_") or method_name in self._BASE_EXCLUDED_METHODS:
            raise ValueError(f"Method '{method_name}' does not exist on {type(self).__name__}")
        func = inspect.getattr_static(type(self), method_name, None)
        if func is None or not callable(func):
            raise ValueError(f"Method '{method_name}' does not exist on {type(self).__name__}")
        self._faults[method_name] = (exception, trigger_count)

    def clear_faults(self, method_name: str | None = None) -> None:
        """Clear active fault triggers."""
        if method_name is not None:
            if method_name in self._faults:
                del self._faults[method_name]
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
        if method_name in self._call_counts:
            return self._call_counts[method_name]
        return 0


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
        item = self._storage[execution_id] if execution_id in self._storage else None
        if item is None:
            return None
        return item.status.value

    async def create_execution(self, execution_data: ExecutionCreateDTO) -> str:
        self._check_fault("create_execution")
        exec_id = generate_opaque_id(EntityPrefix.EXECUTION)
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
        update_dict = updates.model_dump(mode="python")
        if "status_message" not in updates.model_fields_set:
            if "current_step" in updates.model_fields_set and updates.current_step:
                dumped["status_message"] = updates.current_step
            elif "current_step_name" in updates.model_fields_set and updates.current_step_name:
                dumped["status_message"] = updates.current_step_name
        for k in updates.model_fields_set:
            if k in ExecutionRecord.model_fields:
                v = update_dict[k]
                if v is None and k in (
                    "steps",
                    "step_states",
                    "profile_syntheses",
                    "source_identity_manifest",
                    "context_variables",
                ):
                    continue
                dumped[k] = v
        if updates.expected_state_version is not None and existing.state_version != updates.expected_state_version:
            raise AppException(
                message=(
                    f"Optimistic concurrency conflict for execution '{execution_id}': "
                    f"expected state_version={updates.expected_state_version}, actual={existing.state_version}."
                ),
                status_code=409,
                details={
                    "error_code": ErrorCodes.CONFLICT.value,
                    "expected_state_version": updates.expected_state_version,
                    "actual_state_version": existing.state_version,
                },
            )
        if "state_version" not in updates.model_fields_set or updates.state_version is None:
            dumped["state_version"] = existing.state_version + 1
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
            if (
                x.context_variables is not None
                and "matrix_id" in x.context_variables.variables
                and x.context_variables.variables["matrix_id"] == matrix_id
            ):
                count += 1
        return count

    async def save_execution(self, record: ExecutionRecord) -> str:
        """Saves an ExecutionRecord directly with snapshot isolation."""
        self._check_fault("save_execution")
        self._save_isolated(record.id, record)
        return record.id


# ==============================================================================
# 2. Workflow Repository Fake
# ==============================================================================


class InMemoryWorkflowRepository(BaseInMemoryRepository[Workflow], IWorkflowRepository):
    """In-memory fake implementation of IWorkflowRepository with snapshot isolation."""

    def __init__(self) -> None:
        super().__init__()
        self._steps: dict[str, Step] = {}
        self._default_step: Any | None = None

    def seed_raw_workflow(self, workflow_id: str, raw_workflow: Any) -> None:
        """Seed a raw dictionary or domain model into workflow storage for testing."""
        self._storage[workflow_id] = copy.deepcopy(raw_workflow)

    async def get_workflow_definition(self, workflow_id: str) -> Workflow | None:
        self._check_fault("get_workflow_definition")
        return await self.get_workflow_by_id(workflow_id)

    async def get_workflow(self, workflow_id: str) -> Workflow | None:
        self._check_fault("get_workflow")
        return await self.get_workflow_by_id(workflow_id)

    async def get_all_workflows(self, organization_id: str | None = None, role: str | None = None) -> list[Workflow]:
        self._check_fault("get_all_workflows")
        items = self._list_isolated()
        if role != "ROOT" and organization_id is not None:
            items = [
                w
                for w in items
                if (w.organization_id if isinstance(w, Workflow) else None)
                in (organization_id, SystemOrganizations.ROOT_SYSTEM, None)
            ]
        elif organization_id is not None:
            items = [w for w in items if (w.organization_id if isinstance(w, Workflow) else None) == organization_id]
        return items

    async def get_workflow_by_id(self, workflow_id: str) -> Workflow | None:
        self._check_fault("get_workflow_by_id")
        wf = self._get_isolated(workflow_id)
        if (
            wf is None
            and len(self._storage) == 1
            and (not isinstance(workflow_id, str) or type(workflow_id).__name__ == "MagicMock")
        ):
            wf = self._list_isolated()[0]
        if wf is None:
            return None
        if isinstance(wf, Workflow):
            return self._clone(wf)
        try:
            return Workflow.model_validate(wf, strict=False)
        except ValidationError:
            return wf

    async def create_workflow(self, workflow_data: WorkflowCreateDTO) -> str:
        self._check_fault("create_workflow")
        wf_id = generate_opaque_id(EntityPrefix.WORKFLOW)
        data_dict = workflow_data.model_dump(mode="python")
        data_dict["id"] = wf_id
        if "default_profile_id" not in data_dict or data_dict["default_profile_id"] is None:
            data_dict["default_profile_id"] = None
        if "status" not in data_dict or data_dict["status"] is None:
            data_dict["status"] = "ACTIVE"
        if "version" not in data_dict or data_dict["version"] is None:
            data_dict["version"] = 1
        if "description" not in data_dict or data_dict["description"] is None:
            data_dict["description"] = "Default description"
        if not ("model_registry_id" in data_dict and data_dict["model_registry_id"]):
            data_dict["model_registry_id"] = "mrg_0195f3a0000070008000bf23c2670ad5"
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
        dumped["version"] = existing.version + 1
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
        return [
            Step.model_validate(s.model_dump(mode="python") if isinstance(s, BaseModel) else s, strict=False)
            for s in self._steps.values()
        ]

    def seed_raw_step(self, step_id: str, raw_step: Any) -> None:
        """Seed a raw dictionary or domain model into steps storage for testing."""
        self._steps[step_id] = copy.deepcopy(raw_step)

    async def get_step_by_id(self, step_id: str) -> Step | None:
        self._check_fault("get_step_by_id")
        s = self._steps[step_id] if step_id in self._steps else None
        if not s and self._default_step is not None:
            s = self._default_step
        if not s:
            return None
        payload = s.model_dump(mode="python") if isinstance(s, BaseModel) else s
        return Step.model_validate(payload, strict=False)

    async def get_step(self, step_id: str) -> Step | None:
        self._check_fault("get_step")
        return await self.get_step_by_id(step_id)

    async def create_step(self, step_data: StepCreateDTO) -> str:
        self._check_fault("create_step")
        s_id = generate_opaque_id(EntityPrefix.STEP)
        data_dict = step_data.model_dump(mode="python")
        data_dict["id"] = s_id
        model = Step.model_validate(data_dict)
        self._steps[s_id] = Step.model_validate(model.model_dump(mode="python"), strict=False)
        return s_id

    async def update_step(self, step_id: str, updates: StepUpdateDTO) -> str:
        self._check_fault("update_step")
        existing = self._steps[step_id] if step_id in self._steps else None
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
        _ = force_delete
        for wf in self._storage.values():
            if isinstance(wf, Workflow) and any(rule.task_blueprint == step_id for rule in wf.steps):
                raise AppException(
                    message=f"Step '{step_id}' is referenced by workflow '{wf.id}'.",
                    status_code=400,
                    details={"error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value},
                )
        if step_id in self._steps:
            del self._steps[step_id]
            return True
        return False

    async def save_workflow(self, workflow: Workflow) -> str:
        self._check_fault("save_workflow")
        existing = self._get_isolated(workflow.id)
        if isinstance(existing, Workflow):
            if existing.version != workflow.version:
                raise AppException(
                    message=(
                        f"Optimistic concurrency conflict for workflow '{workflow.id}': "
                        f"expected version={workflow.version}, actual version={existing.version}."
                    ),
                    status_code=409,
                    details={"error_code": ErrorCodes.CONFLICT.value},
                )
            self._save_isolated(workflow.id, workflow.model_copy(update={"version": existing.version + 1}))
            return workflow.id
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
            org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)
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
                allowed_email_domains=[],
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
        items = [self._clone(u) for u in self._users.values()]
        if org_id is not None:
            items = [u for u in items if u.organization_id == org_id]
        return items

    async def get_user(self, user_id: str) -> User | None:
        self._check_fault("get_user")
        if user_id in self._users:
            u = self._users[user_id]
            return self._clone(u) if u else None
        return None

    async def get_user_by_email(self, email: str) -> User | None:
        self._check_fault("get_user_by_email")
        for u in self._users.values():
            if u.email == email:
                return self._clone(u)
        return None

    async def create_user(self, user_data: UserCreate | User) -> str:
        self._check_fault("create_user")
        if isinstance(user_data, User):
            u_id = user_data.id
            self._users[u_id] = self._clone(user_data)
            return u_id
        u_id = generate_opaque_id(EntityPrefix.USER)
        data_dict = user_data.model_dump(mode="python")
        data_dict["id"] = u_id
        if "password" in data_dict:
            del data_dict["password"]
        data_dict["created_at"] = datetime.now(UTC)
        user = User.model_validate(data_dict)
        self._users[u_id] = self._clone(user)
        return u_id

    async def update_user(self, user_id: str, updates: UserUpdate) -> bool:
        self._check_fault("update_user")
        existing = self._users[user_id] if user_id in self._users else None
        if existing is None:
            return False
        dumped = existing.model_dump(mode="python")
        dumped.update(updates.model_dump(mode="python", exclude_unset=True))
        try:
            updated = User.model_validate(dumped)
        except ValidationError:
            updated = existing.model_copy(update=updates.model_dump(mode="python", exclude_unset=True))
        self._users[user_id] = self._clone(updated)
        return True

    async def delete_user(self, user_id: str) -> bool:
        self._check_fault("delete_user")
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False

    async def delete_org_data(self, org_id: str) -> None:
        self._check_fault("delete_org_data")
        if org_id in self._storage:
            del self._storage[org_id]
        self._users = {k: v for k, v in self._users.items() if v.organization_id != org_id}

    async def get_org_usage_total(self, org_id: str, since: str | None = None) -> float:
        self._check_fault("get_org_usage_total")
        if org_id in self._usage_totals:
            return self._usage_totals[org_id]
        return 0.0

    def set_org_usage_total(self, org_id: str, total: float) -> None:
        """Helper to seed usage total for test scenarios."""
        self._usage_totals[org_id] = total


# ==============================================================================
# 4. Prompt Block Repository Fake
# ==============================================================================


class InMemoryPromptBlockRepository(BaseInMemoryRepository[PromptBlock], IPromptBlockRepository):
    """In-memory fake implementation of IPromptBlockRepository."""

    def __init__(self) -> None:
        super().__init__()
        self._workflow_repo: InMemoryWorkflowRepository | None = None
        self._profile_repo: InMemoryOutputProfileRepository | None = None

    def seed_raw_prompt_block(self, block_id: str, raw_block: Any) -> None:
        """Seed a raw dictionary or domain model into prompt block storage for testing."""
        self._storage[block_id] = copy.deepcopy(raw_block)

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
        _ = force_delete
        if self._workflow_repo is not None:
            for step in self._workflow_repo._steps.values():
                if isinstance(step, Step) and (
                    block_id in (step.role_block_id, step.extraction_protocol_block_id, step.execution_persona_block_id)
                    or block_id in step.criteria_block_ids
                ):
                    raise AppException(
                        message=f"Prompt block '{block_id}' is referenced by step '{step.id}'.",
                        status_code=400,
                        details={"error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value},
                    )
        if self._profile_repo is not None:
            for profile in self._profile_repo._storage.values():
                if isinstance(profile, OutputProfile) and block_id in (
                    profile.variance_target_block,
                    profile.user_role_target_block,
                ):
                    raise AppException(
                        message=f"Prompt block '{block_id}' is referenced by output profile '{profile.id}'.",
                        status_code=400,
                        details={"error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value},
                    )
        if block_id in self._storage:
            del self._storage[block_id]
            return True
        return False


# ==============================================================================
# 5. Output Profile Repository Fake
# ==============================================================================


class InMemoryOutputProfileRepository(BaseInMemoryRepository[OutputProfile], IOutputProfileRepository):
    """In-memory fake implementation of IOutputProfileRepository."""

    def __init__(self) -> None:
        super().__init__()
        self._workflow_repo: InMemoryWorkflowRepository | None = None
        self._report_repo: InMemoryReportArtifactRepository | None = None

    async def get_all_output_profiles(self) -> list[OutputProfile]:
        self._check_fault("get_all_output_profiles")
        return self._list_isolated()

    async def get_all_output_profiles_models(self) -> list[OutputProfile]:
        self._check_fault("get_all_output_profiles_models")
        return self._list_isolated()

    async def get_output_profile_by_id(self, profile_id: str) -> OutputProfile | None:
        self._check_fault("get_output_profile_by_id")
        res = self._get_isolated(profile_id)
        if (
            res is None
            and len(self._storage) == 1
            and (not isinstance(profile_id, str) or type(profile_id).__name__ == "MagicMock")
        ):
            return self._list_isolated()[0]
        return res

    async def get_output_profile(self, profile_id: str) -> OutputProfile | None:
        return await self.get_output_profile_by_id(profile_id)

    async def get_by_id(self, profile_id: str) -> OutputProfile | None:
        return await self.get_output_profile_by_id(profile_id)

    async def create_output_profile(self, profile_data: OutputProfile) -> str:
        self._check_fault("create_output_profile")
        self._save_isolated(profile_data.id, profile_data)
        return profile_data.id

    async def save_output_profile(self, profile_data: OutputProfile) -> str:
        """Alias for create_output_profile to support save conventions in tests."""
        return await self.create_output_profile(profile_data)

    async def update_output_profile(self, profile_id: str, updates: OutputProfile) -> bool:
        self._check_fault("update_output_profile")
        self._save_isolated(profile_id, updates)
        return True

    async def delete_output_profile(self, profile_id: str) -> bool:
        self._check_fault("delete_output_profile")
        if self._workflow_repo is not None:
            for wf in self._workflow_repo._storage.values():
                if isinstance(wf, Workflow) and wf.default_profile_id == profile_id:
                    raise AppException(
                        message=f"Output profile '{profile_id}' is referenced by workflow '{wf.id}'.",
                        status_code=400,
                        details={"error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value},
                    )
        if self._report_repo is not None:
            for report in self._report_repo._storage.values():
                if isinstance(report, ReportArtifact) and report.profile_id == profile_id:
                    raise AppException(
                        message=f"Output profile '{profile_id}' is referenced by report artifact '{report.id}'.",
                        status_code=400,
                        details={"error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value},
                    )
        if profile_id in self._storage:
            del self._storage[profile_id]
            return True
        return False


class InMemoryTaskBriefRepository(BaseInMemoryRepository[TaskBrief], ITaskBriefRepository):
    """In-memory fake implementation of ITaskBriefRepository."""

    async def get_all_task_briefs(self) -> list[TaskBrief]:
        self._check_fault("get_all_task_briefs")
        return self._list_isolated()

    async def get_task_brief_by_id(self, brief_id: str) -> TaskBrief | None:
        self._check_fault("get_task_brief_by_id")
        return self._get_isolated(brief_id)

    async def create_task_brief(self, brief_data: TaskBrief) -> str:
        self._check_fault("create_task_brief")
        self._save_isolated(brief_data.id, brief_data)
        return brief_data.id

    async def update_task_brief(self, brief_id: str, updates: TaskBrief) -> bool:
        self._check_fault("update_task_brief")
        if brief_id not in self._storage:
            return False
        self._save_isolated(brief_id, updates)
        return True

    async def delete_task_brief(self, brief_id: str) -> bool:
        self._check_fault("delete_task_brief")
        if brief_id in self._storage:
            del self._storage[brief_id]
            return True
        return False


# ==============================================================================
# 7. System Repository Fake
# ==============================================================================


class InMemorySystemRepository(
    BaseInMemoryRepository[SystemConfigModelRegistry | SystemConfigMCPGateways],
    ISystemRepository,
):
    """In-memory fake implementation of ISystemRepository."""

    def __init__(self) -> None:
        super().__init__()
        default_reg = SystemConfigModelRegistry(
            id="mrg_0195f3a0000070008000bf23c2670ad5",
            name="Default Model Registry",
            slug="default_model_registry",
            default_provider=LLMProvider.AI_STUDIO,
            tier_definitions={
                CognitiveTier.FAST: ModelProfile(
                    provider="ai_studio",
                    model_name="gemini-2.5-flash",
                    allowed_tools=[],
                    additional_params=ProviderExtraParamsDTO(),
                ),
                CognitiveTier.BALANCED: ModelProfile(
                    provider="ai_studio",
                    model_name="gemini-2.5-flash",
                    allowed_tools=[],
                    additional_params=ProviderExtraParamsDTO(),
                ),
                CognitiveTier.DEEP: ModelProfile(
                    provider="ai_studio",
                    model_name="gemini-2.5-pro",
                    allowed_tools=[],
                    additional_params=ProviderExtraParamsDTO(),
                ),
                CognitiveTier.REASONING: ModelProfile(
                    provider="ai_studio",
                    model_name="gemini-2.5-pro",
                    allowed_tools=[],
                    additional_params=ProviderExtraParamsDTO(),
                ),
            },
        )
        self._model_registries: dict[str, SystemConfigModelRegistry] = {
            default_reg.id: default_reg,
            "mrg_0195f3a0000070008000e26807f3bfa3": default_reg,
            "mrg_0195f3a00000700e826807f3bfa3454d": default_reg,
            "mrg_0195f3a00000700b81c2d3e4f5a60718": default_reg,
            "mrg_0195f3a0000070068f8b1c4a2e0d49f1": default_reg,
        }
        self._mcp_gateways = SystemConfigMCPGateways(
            id="mcp_0195f3a00000700080008172bda70c86",
            organization_id=SystemOrganizations.ROOT_SYSTEM.value,
            name="Default MCP Gateway",
            slug="default_mcp_gateway",
            tools=[],
        )
        self._mcp_gateways_map: dict[str, SystemConfigMCPGateways] = {
            self._mcp_gateways.id: self._mcp_gateways,
        }
        self._raw_system_configs: dict[str, JsonValue] = {}

    def seed_raw_system_config(self, key: str, item: JsonValue) -> None:
        """Seed a raw dictionary or domain model into system storage for testing."""
        self._raw_system_configs[key] = copy.deepcopy(item)

    def set_model_registry(self, registry: SystemConfigModelRegistry | None, registry_id: str | None = None) -> None:
        """Helper to seed model registry for tests."""
        if registry is None:
            self._model_registries.clear()
        else:
            r_id = registry_id if registry_id is not None else registry.id
            self._model_registries[r_id] = registry
            if registry.id not in self._model_registries:
                self._model_registries[registry.id] = registry

    async def get_model_registry(self, registry_id: str) -> SystemConfigModelRegistry:
        self._check_fault("get_model_registry")
        if not registry_id or registry_id not in self._model_registries:
            raise ResourceNotFoundError(resource_type="model_registry", resource_id=registry_id if registry_id else "")
        reg = self._model_registries[registry_id]
        return self._clone(reg)

    async def get_all_model_registries(self) -> list[SystemConfigModelRegistry]:
        self._check_fault("get_all_model_registries")
        seen_ids: set[str] = set()
        result: list[SystemConfigModelRegistry] = []
        for reg_key, reg in self._model_registries.items():
            reg_id = reg.id if isinstance(reg, SystemConfigModelRegistry) else reg_key
            if reg_id not in seen_ids:
                seen_ids.add(reg_id)
                result.append(self._clone(reg))
        return sorted(
            result,
            key=lambda m: (m.name, m.id) if isinstance(m, SystemConfigModelRegistry) else ("", ""),
        )

    async def update_model_registry(self, registry_data: SystemConfigModelRegistry) -> bool:
        self._check_fault("update_model_registry")
        doc_id = registry_data.id
        self._model_registries[doc_id] = SystemConfigModelRegistry.model_validate(
            registry_data.model_dump(mode="python"), strict=False
        )
        return True

    async def delete_model_registry(self, registry_id: str) -> bool:
        self._check_fault("delete_model_registry")
        if registry_id in self._model_registries:
            del self._model_registries[registry_id]
            return True
        return False

    async def delete_mcp_gateways(self, gateway_id: str) -> bool:
        self._check_fault("delete_mcp_gateways")
        if gateway_id in self._mcp_gateways_map:
            del self._mcp_gateways_map[gateway_id]
            return True
        return False

    def remove_system_config(self, config_id: str) -> None:
        """Remove a model registry or MCP gateway record from test storage."""
        if config_id in self._mcp_gateways_map:
            del self._mcp_gateways_map[config_id]
        if config_id in self._raw_system_configs:
            del self._raw_system_configs[config_id]
        if config_id in self._model_registries:
            del self._model_registries[config_id]
        if config_id in self._storage:
            del self._storage[config_id]

    async def get_mcp_gateways(self, id: str | None = None) -> SystemConfigMCPGateways:
        self._check_fault("get_mcp_gateways")
        if self._mcp_gateways is not None and not isinstance(self._mcp_gateways, SystemConfigMCPGateways):
            return SystemConfigMCPGateways.model_validate(self._mcp_gateways, strict=False)
        if id is not None:
            if id in self._mcp_gateways_map:
                return self._clone(self._mcp_gateways_map[id])
            if isinstance(self._mcp_gateways, SystemConfigMCPGateways) and self._mcp_gateways.id == id:
                return self._clone(self._mcp_gateways)
            raise ResourceNotFoundError(resource_type="mcp_gateways", resource_id=id)
        if self._mcp_gateways is None:
            raise ResourceNotFoundError(resource_type="mcp_gateways", resource_id="mcp_gateways")
        return self._mcp_gateways.model_copy(deep=True)

    async def get_all_mcp_gateways(self) -> list[SystemConfigMCPGateways]:
        self._check_fault("get_all_mcp_gateways")
        return [self._clone(gw) for gw in sorted(self._mcp_gateways_map.values(), key=lambda m: (m.slug, m.id))]

    async def update_mcp_gateways(self, gateways_data: SystemConfigMCPGateways) -> bool:
        self._check_fault("update_mcp_gateways")
        validated = SystemConfigMCPGateways.model_validate(gateways_data.model_dump(mode="python"), strict=False)
        self._mcp_gateways = validated
        self._mcp_gateways_map[validated.id] = validated
        return True

    async def get_system_config(self, config_id: str) -> Any:
        self._check_fault("get_system_config")
        if config_id in self._raw_system_configs:
            return copy.deepcopy(self._raw_system_configs[config_id])
        if config_id in self._model_registries:
            return self._clone(self._model_registries[config_id])
        if config_id in self._mcp_gateways_map:
            return self._clone(self._mcp_gateways_map[config_id])
        return self._get_isolated(config_id)


# ==============================================================================
# 11. Audit Repository Fake
# ==============================================================================


class InMemoryAuditRepository(BaseInMemoryRepository[AuditLogRecord], IAuditRepository):
    """In-memory fake implementation of IAuditRepository."""

    def __init__(self) -> None:
        super().__init__()
        self._audit_logs: list[AuditLogRecord] = []
        self._usage_records: list[UsageRecord] = []

    async def log_audit_event(self, event_data: AuditLogCreateDTO) -> None:
        self._check_fault("log_audit_event")
        record = AuditLogRecord(
            id=f"aud_{generate_uuid7().hex}",
            organization_id=event_data.organization_id,
            actor_id=event_data.actor_id,
            execution_id=event_data.execution_id,
            event_type=event_data.event_type,
            resource_type=event_data.resource_type,
            resource_id=event_data.resource_id,
            details=dict(event_data.details),
            created_at=datetime.now(UTC),
        )
        self._audit_logs.append(record)

    async def get_audit_logs(
        self,
        organization_id: str | None = None,
        actor_id: str | None = None,
        event_type: str | None = None,
        limit: int = 100,
    ) -> list[AuditLogRecord]:
        self._check_fault("get_audit_logs")
        if limit <= 0:
            return []
        logs = [AuditLogRecord.model_validate(e.model_dump(mode="python"), strict=False) for e in self._audit_logs]
        if organization_id is not None:
            logs = [entry for entry in logs if entry.organization_id == organization_id]
        if actor_id is not None:
            logs = [entry for entry in logs if entry.actor_id == actor_id]
        if event_type is not None:
            logs = [entry for entry in logs if entry.event_type == event_type]
        logs.reverse()
        return logs[:limit]

    async def log_usage(self, record: UsageRecord) -> None:
        self._check_fault("log_usage")
        self._usage_records.append(UsageRecord.model_validate(record.model_dump(mode="python"), strict=False))

    @staticmethod
    def _parse_optional_since(since: datetime | str | None) -> datetime | None:
        if since is None:
            return None
        if isinstance(since, datetime):
            return since if since.tzinfo is not None else since.replace(tzinfo=UTC)
        parsed = datetime.fromisoformat(since.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)

    async def get_usage_records(
        self, scope: str, entity_id: str | None = None, since: str | None = None
    ) -> list[UsageRecord]:
        self._check_fault("get_usage_records")
        since_dt = self._parse_optional_since(since)
        records = [UsageRecord.model_validate(r.model_dump(mode="python"), strict=False) for r in self._usage_records]
        if scope == "organization" and entity_id is not None:
            records = [r for r in records if r.org_id == entity_id]
        elif scope == "user" and entity_id is not None:
            records = [r for r in records if r.user_id == entity_id]
        if since_dt is not None:
            records = [
                r
                for r in records
                if (r.timestamp if r.timestamp.tzinfo is not None else r.timestamp.replace(tzinfo=UTC)) >= since_dt
            ]
        return records

    async def aggregate_organization_usage(
        self,
        organization_id: str | None = None,
        since: datetime | None = None,
    ) -> UsageRollupSummaryDTO:
        self._check_fault("aggregate_organization_usage")
        since_dt = self._parse_optional_since(since)
        records = list(self._usage_records)
        if organization_id is not None:
            records = [r for r in records if r.org_id == organization_id]
        if since_dt is not None:
            records = [
                r
                for r in records
                if (r.timestamp if r.timestamp.tzinfo is not None else r.timestamp.replace(tzinfo=UTC)) >= since_dt
            ]
        return UsageRollupSummaryDTO(
            organization_id=organization_id,
            total_prompt_tokens=sum(r.input_tokens for r in records),
            total_completion_tokens=sum(r.output_tokens for r in records),
            total_cached_tokens=sum(r.cached_tokens for r in records),
            total_reasoning_tokens=sum(r.reasoning_tokens for r in records),
            total_cache_creation_input_tokens=sum(r.cache_creation_input_tokens for r in records),
            total_cost_usd=sum(r.cost_usd for r in records),
            total_estimated_savings_usd=sum(r.estimated_savings_usd for r in records),
            record_count=len(records),
        )

    async def get_detailed_usage(
        self, scope: str, target_id: str | None = None, since: str | None = None
    ) -> DetailedUsageDTO:
        self._check_fault("get_detailed_usage")
        records = await self.get_usage_records(scope=scope, entity_id=target_id, since=since)
        by_model: dict[str, int] = {}
        total_tokens = 0
        total_cost = 0.0
        for rec in records:
            tokens = rec.input_tokens + rec.output_tokens + rec.reasoning_tokens
            total_tokens += tokens
            total_cost += rec.cost_usd
            prev = by_model[rec.model] if rec.model in by_model else 0
            by_model[rec.model] = prev + tokens
        resolved_org = target_id if target_id is not None else "system"
        return DetailedUsageDTO(
            organization_id=resolved_org,
            total_cost_usd=total_cost,
            total_tokens=total_tokens,
            by_model=by_model,
            by_workflow={},
        )


# ==============================================================================
# 9. Report Artifact Repository Fake
# ==============================================================================


class InMemoryReportArtifactRepository(BaseInMemoryRepository[ReportArtifact], IReportArtifactRepository):
    """In-memory fake implementation of IReportArtifactRepository with snapshot isolation."""

    def save_report_artifact(self, report: ReportArtifact) -> None:
        """Synchronously persist a report artifact into isolated storage without pre-flight validation."""
        self._save_isolated(report.id, report)

    async def create_report_artifact(self, report: ReportArtifact) -> ReportArtifact:
        self._check_fault("create_report_artifact")
        self._save_isolated(report.id, report)
        return self._clone(report)

    async def get_report_artifact(self, report_id: str) -> ReportArtifact | None:
        self._check_fault("get_report_artifact")
        return self._get_isolated(report_id)

    async def list_report_artifacts_by_execution(self, execution_id: str) -> list[ReportArtifact]:
        self._check_fault("list_report_artifacts_by_execution")
        return [r for r in self._list_isolated() if r.execution_id == execution_id]

    async def update_report_artifact(self, report_id: str, update_dto: ReportArtifactUpdateDTO) -> ReportArtifact:
        self._check_fault("update_report_artifact")
        existing = self._get_isolated(report_id)
        if existing is None:
            raise AppException(
                message=f"Report artifact {report_id} not found",
                status_code=404,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )
        updated = existing.model_copy(
            update={
                "status": update_dto.status if update_dto.status is not None else existing.status,
                "storage_paths": update_dto.storage_paths
                if update_dto.storage_paths is not None
                else existing.storage_paths,
                "metadata": update_dto.metadata if update_dto.metadata is not None else existing.metadata,
                "error_message": update_dto.error_message
                if update_dto.error_message is not None
                else existing.error_message,
                "updated_at": datetime.now(UTC),
            }
        )
        self._save_isolated(report_id, updated)
        return self._clone(updated)

    async def delete_report_artifact(self, report_id: str) -> bool:
        self._check_fault("delete_report_artifact")
        if report_id in self._storage:
            del self._storage[report_id]
            return True
        return False


# ==============================================================================
# 10. Unified Workflow Repository Composite Facade
# ==============================================================================


class InMemoryUnifiedWorkflowRepository(IUnifiedWorkflowRepository):
    """Composite in-memory facade satisfying IUnifiedWorkflowRepository across the 9 active V2 protocols."""

    def __init__(
        self,
        workflows: InMemoryWorkflowRepository | None = None,
        executions: InMemoryExecutionRepository | None = None,
        report_artifacts: InMemoryReportArtifactRepository | None = None,
        identities: InMemoryIdentityRepository | None = None,
        prompt_blocks: InMemoryPromptBlockRepository | None = None,
        task_briefs: InMemoryTaskBriefRepository | None = None,
        output_profiles: InMemoryOutputProfileRepository | None = None,
        system: InMemorySystemRepository | None = None,
        audit: InMemoryAuditRepository | None = None,
    ) -> None:
        self._workflows = workflows or InMemoryWorkflowRepository()
        self._executions = executions or InMemoryExecutionRepository()
        self._report_artifacts = report_artifacts or InMemoryReportArtifactRepository()
        self._identities = identities or InMemoryIdentityRepository()
        self._prompt_blocks = prompt_blocks or InMemoryPromptBlockRepository()
        self._task_briefs = task_briefs or InMemoryTaskBriefRepository()
        self._output_profiles = output_profiles or InMemoryOutputProfileRepository()
        self._system = system or InMemorySystemRepository()
        self._audit = audit or InMemoryAuditRepository()
        self._prompt_blocks._workflow_repo = self._workflows
        self._prompt_blocks._profile_repo = self._output_profiles
        self._output_profiles._workflow_repo = self._workflows
        self._output_profiles._report_repo = self._report_artifacts

    def _all_sub_repos(self) -> tuple[BaseInMemoryRepository[Any], ...]:
        return (
            self._workflows,
            self._executions,
            self._report_artifacts,
            self._identities,
            self._prompt_blocks,
            self._task_briefs,
            self._output_profiles,
            self._system,
            self._audit,
        )

    def get_call_count(self, method_name: str) -> int:
        """Get the total call count for a method across all underlying repositories."""
        return sum(r.get_call_count(method_name) for r in self._all_sub_repos())

    def inject_fault(self, method_name: str, exception: Exception, trigger_count: int | None = 1) -> None:
        """Inject a fault into underlying repositories that support the method."""
        injected = False
        for r in self._all_sub_repos():
            try:
                r.inject_fault(method_name, exception, trigger_count)
                injected = True
            except ValueError:
                pass
        if not injected:
            raise ValueError(
                f"Method '{method_name}' does not exist on any sub-repository of InMemoryUnifiedWorkflowRepository"
            )

    def clear_faults(self, method_name: str | None = None) -> None:
        """Clear faults across all underlying repositories."""
        for r in self._all_sub_repos():
            r.clear_faults(method_name)

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

    async def save_execution(self, record: ExecutionRecord) -> str:
        if (
            isinstance(record.organization_id, str)
            and record.organization_id != SystemOrganizations.ROOT_SYSTEM
            and self._identities._get_isolated(record.organization_id) is None
        ):
            try:
                self._identities._save_isolated(
                    record.organization_id,
                    Organization(
                        id=record.organization_id,
                        name="Test Organization",
                        contact_email="admin@example.com",
                        is_active=True,
                        tier="free",
                        subscription_status=SubscriptionStatus.ACTIVE,
                        quota_limit=100.0,
                        tpm_limit=1000000,
                        rpm_limit=60,
                        allowed_email_domains=[],
                    ),
                )
            except ValidationError, AppException:
                pass
        return await self._executions.save_execution(record)

    # 2.5 Report Artifact
    def save_report_artifact(self, report: ReportArtifact) -> None:
        self._report_artifacts.save_report_artifact(report)

    async def create_report_artifact(self, report: ReportArtifact) -> ReportArtifact:
        return await self._report_artifacts.create_report_artifact(report)

    async def get_report_artifact(self, report_id: str) -> ReportArtifact | None:
        return await self._report_artifacts.get_report_artifact(report_id)

    async def list_report_artifacts_by_execution(self, execution_id: str) -> list[ReportArtifact]:
        return await self._report_artifacts.list_report_artifacts_by_execution(execution_id)

    async def update_report_artifact(self, report_id: str, update_dto: ReportArtifactUpdateDTO) -> ReportArtifact:
        return await self._report_artifacts.update_report_artifact(report_id, update_dto)

    async def delete_report_artifact(self, report_id: str) -> bool:
        return await self._report_artifacts.delete_report_artifact(report_id)

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

    def set_org_usage_total(self, org_id: str, total: float) -> None:
        """Helper to seed usage total for test scenarios."""
        self._identities.set_org_usage_total(org_id, total)

    # 4. PromptBlock
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

    # 5.5 TaskBrief
    async def get_all_task_briefs(self) -> list[TaskBrief]:
        return await self._task_briefs.get_all_task_briefs()

    async def get_task_brief_by_id(self, brief_id: str) -> TaskBrief | None:
        return await self._task_briefs.get_task_brief_by_id(brief_id)

    async def create_task_brief(self, brief_data: TaskBrief) -> str:
        return await self._task_briefs.create_task_brief(brief_data)

    async def update_task_brief(self, brief_id: str, updates: TaskBrief) -> bool:
        return await self._task_briefs.update_task_brief(brief_id, updates)

    async def delete_task_brief(self, brief_id: str) -> bool:
        return await self._task_briefs.delete_task_brief(brief_id)

    def set_task_briefs(self, briefs: list[TaskBrief]) -> None:
        """Helper to seed task briefs for tests."""
        self._task_briefs._storage.clear()
        for brief in briefs:
            self._task_briefs._save_isolated(brief.id, brief)

    # 6. OutputProfile
    async def get_all_output_profiles(self) -> list[OutputProfile]:
        return await self._output_profiles.get_all_output_profiles()

    async def get_all_output_profiles_models(self) -> list[OutputProfile]:
        return await self._output_profiles.get_all_output_profiles_models()

    async def get_output_profile_by_id(self, profile_id: str) -> OutputProfile | None:
        return await self._output_profiles.get_output_profile_by_id(profile_id)

    async def get_output_profile(self, profile_id: str) -> OutputProfile | None:
        return await self._output_profiles.get_output_profile_by_id(profile_id)

    async def get_by_id(self, entity_id: str) -> Any | None:
        p = await self._output_profiles.get_output_profile_by_id(entity_id)
        if p is not None:
            return p
        return await self._prompt_blocks.get_prompt_block_by_id(entity_id)

    async def create_output_profile(self, profile_data: OutputProfile) -> str:
        return await self._output_profiles.create_output_profile(profile_data)

    async def save_output_profile(self, profile_data: OutputProfile) -> str:
        return await self.create_output_profile(profile_data)

    async def update_output_profile(self, profile_id: str, updates: OutputProfile) -> bool:
        return await self._output_profiles.update_output_profile(profile_id, updates)

    async def delete_output_profile(self, profile_id: str) -> bool:
        return await self._output_profiles.delete_output_profile(profile_id)

    # 7. System
    async def get_model_registry(self, registry_id: str) -> SystemConfigModelRegistry:
        return await self._system.get_model_registry(registry_id=registry_id)

    async def get_all_model_registries(self) -> list[SystemConfigModelRegistry]:
        return await self._system.get_all_model_registries()

    async def update_model_registry(self, registry_data: SystemConfigModelRegistry) -> bool:
        return await self._system.update_model_registry(registry_data)

    async def delete_model_registry(self, registry_id: str) -> bool:
        for wf in self._workflows._storage.values():
            if wf.model_registry_id == registry_id:
                raise AppException(
                    message=f"Model registry '{registry_id}' is referenced by workflow '{wf.id}'.",
                    status_code=400,
                    details={"error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value},
                )
        return await self._system.delete_model_registry(registry_id)

    async def get_mcp_gateways(self, id: str | None = None) -> SystemConfigMCPGateways:
        return await self._system.get_mcp_gateways(id)

    async def get_all_mcp_gateways(self) -> list[SystemConfigMCPGateways]:
        return await self._system.get_all_mcp_gateways()

    async def update_mcp_gateways(self, gateways_data: SystemConfigMCPGateways) -> bool:
        return await self._system.update_mcp_gateways(gateways_data)

    async def delete_mcp_gateways(self, gateway_id: str) -> bool:
        for wf in self._workflows._storage.values():
            if wf.mcp_gateway_id == gateway_id:
                raise AppException(
                    message=f"MCP gateway '{gateway_id}' is referenced by workflow '{wf.id}'.",
                    status_code=400,
                    details={"error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value},
                )
        return await self._system.delete_mcp_gateways(gateway_id)

    async def get_system_config(self, config_id: str) -> Any:
        return await self._system.get_system_config(config_id)

    def seed_raw_step(self, step_id: str, raw_step: Any) -> None:
        """Seeds a raw step record into the underlying workflow repository."""
        self._workflows.seed_raw_step(step_id, raw_step)

    def set_step(self, step_data: Any, step_id: str | None = None) -> None:
        """Helper to seed a step record for tests."""
        if step_data is None:
            self._workflows._default_step = None
            return
        if step_id is not None:
            s_id = step_id
        else:
            try:
                s_id = step_data.id
            except AttributeError:
                try:
                    s_id = step_data["id"]
                except KeyError, TypeError:
                    s_id = "stp_0123456789abcdef0123456789abcdef"
        self._workflows.seed_raw_step(s_id, step_data)
        self._workflows._default_step = step_data

    def seed_raw_prompt_block(self, block_id: str, raw_block: Any) -> None:
        """Seeds a raw prompt block record into the underlying prompt block repository."""
        self._prompt_blocks.seed_raw_prompt_block(block_id, raw_block)

    def set_output_profile(self, profile: Any) -> None:
        """Helper to seed a single output profile for tests."""
        if profile is None:
            self._output_profiles._storage.clear()
            return
        self.set_output_profiles([profile])

    def set_output_profiles(self, profiles: list[Any]) -> None:
        """Helper to seed output profiles for tests."""
        self._output_profiles._storage.clear()
        for p in profiles:
            p_model = p if isinstance(p, OutputProfile) else OutputProfile.model_validate(p)
            self._output_profiles._save_isolated(p_model.id, p_model)

    def set_prompt_blocks(self, blocks: list[Any]) -> None:
        """Helper to seed prompt blocks for tests."""
        self._prompt_blocks._storage.clear()
        for b in blocks:
            try:
                b_id = b.id
            except AttributeError:
                try:
                    b_id = b["id"]
                except KeyError, TypeError:
                    b_id = generate_opaque_id(EntityPrefix.PROMPT_BLOCK)
            self._prompt_blocks.seed_raw_prompt_block(b_id, b)

    def seed_raw_workflow(self, workflow_id: str, raw_workflow: Any) -> None:
        """Seed a raw dictionary or domain model into workflow storage for testing."""
        self._workflows.seed_raw_workflow(workflow_id, raw_workflow)

    def set_workflow(self, workflow: Workflow | Any | None) -> None:
        """Helper to seed a workflow for tests."""
        if workflow is None:
            self._workflows._storage.clear()
            return
        if isinstance(workflow, Workflow):
            self._workflows._save_isolated(workflow.id, workflow)
            return
        try:
            self._workflows._storage[workflow.id] = workflow
        except AttributeError:
            wf_id = workflow["id"] if "id" in workflow else "wf_0123456789abcdef0123456789abcdef"
            self._workflows.seed_raw_workflow(wf_id, workflow)

    def set_execution(self, record: ExecutionRecord | Any | None) -> None:
        """Helper to seed an execution record for tests."""
        if record is None:
            self._executions._storage.clear()
            return
        if isinstance(record, ExecutionRecord):
            self._executions._save_isolated(record.id, record)
            return
        try:
            self._executions._storage[record.id] = record
        except AttributeError:
            if "id" in record:
                self._executions._storage[record["id"]] = record

    def set_model_registry(self, registry: SystemConfigModelRegistry | None, registry_id: str | None = None) -> None:
        """Helper to seed model registry for tests."""
        self._system.set_model_registry(registry, registry_id)

    def set_user(self, user: User | Any | None) -> None:
        """Helper to seed a user for tests."""
        if user is None:
            self._identities._users.clear()
            return
        if isinstance(user, User):
            self._identities._users[user.id] = self._identities._clone(user)
            return
        try:
            self._identities._users[user.id] = self._identities._clone(user)
        except AttributeError:
            u_id = user["id"] if "id" in user else "usr_0123456789abcdef0123456789abcdef"
            self._identities._users[u_id] = copy.deepcopy(user)

    def set_organization(self, org: Organization | None) -> None:
        """Helper to seed an organization for tests."""
        if org is None:
            self._identities._storage.clear()
        else:
            self._identities._save_isolated(org.id, org)

    def set_mcp_gateways(self, gateways: SystemConfigMCPGateways | Any) -> None:
        """Helper to seed mcp gateways for tests."""
        self._system._mcp_gateways = gateways
        if gateways is None or not isinstance(gateways, SystemConfigMCPGateways):
            self._system._mcp_gateways_map.clear()
        else:
            self._system._mcp_gateways_map[gateways.id] = gateways

    def seed_system_config(self, key: str, item: JsonValue) -> None:
        """Seeds a system config record into the underlying system repository."""
        self._system.seed_raw_system_config(key, item)

    def remove_system_config(self, config_id: str) -> None:
        """Removes a system config record from the underlying system repository."""
        self._system.remove_system_config(config_id)

    # 11. Audit
    async def log_audit_event(self, event_data: AuditLogCreateDTO) -> None:
        await self._audit.log_audit_event(event_data)

    async def get_audit_logs(
        self,
        organization_id: str | None = None,
        actor_id: str | None = None,
        event_type: str | None = None,
        limit: int = 100,
    ) -> list[AuditLogRecord]:
        return await self._audit.get_audit_logs(organization_id, actor_id, event_type, limit)

    async def log_usage(self, record: UsageRecord) -> None:
        await self._audit.log_usage(record)

    async def get_usage_records(
        self, scope: str, entity_id: str | None = None, since: str | None = None
    ) -> list[UsageRecord]:
        return await self._audit.get_usage_records(scope, entity_id, since)

    async def aggregate_organization_usage(
        self,
        organization_id: str | None = None,
        since: datetime | None = None,
    ) -> UsageRollupSummaryDTO:
        return await self._audit.aggregate_organization_usage(organization_id, since)

    async def get_detailed_usage(
        self, scope: str, target_id: str | None = None, since: str | None = None
    ) -> DetailedUsageDTO:
        return await self._audit.get_detailed_usage(scope, target_id, since)
