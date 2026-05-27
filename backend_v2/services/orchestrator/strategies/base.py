import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, ConfigDict

from backend_v2.core.hook_registry import HookDependencies, HookState, hook_registry
from backend_v2.database.interfaces import (
    IAuditRepository,
    IComponentRepository,
    IExecutionRepository,
    IIdentityRepository,
    ISystemRepository,
    IWorkflowRepository,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.state import StateProjector, TraceEvent
from backend_v2.models.v2_core import ExpectedInput, FrozenContext, StepRule
from backend_v2.models.v2_core import Step as V2Step
from backend_v2.services.usage_service import UsageService
from backend_v2.utils.dict_utils import deep_merge_dicts

logger = logging.getLogger(__name__)


class StrategyContext(BaseModel):
    """Immutable context wrapper enforcing strict typing and Single Responsibility for node execution.

    Follows the V2 Architecture Service Boundary Doctrine: Strict IN -> Strict OUT.
    """

    execution_id: str
    workflow_id: str
    metadata: dict[str, Any]
    expected_inputs: list[ExpectedInput] | None = None
    model_strategy: str | None = None
    strictness_level: int = 50

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True, extra="forbid")


class NodeStrategy(ABC):
    """Abstract Base Class for executing a workflow node (Strategy Pattern).

    Subclasses must implement `execute` and adhere strictly to V3 Event Sourcing protocols
    by emitting immutable `TraceEvent` objects rather than mutating dictionaries in place.
    """

    def __init__(
        self,
        exec_repo: IExecutionRepository,
        workflow_repo: IWorkflowRepository,
        comp_repo: IComponentRepository,
        identity_repo: IIdentityRepository,
        audit_repo: IAuditRepository,
        system_repo: ISystemRepository,
        prompt_compiler: Any,
        arq_pool: Any | None = None,
    ):
        self.exec_repo = exec_repo
        self.workflow_repo = workflow_repo
        self.comp_repo = comp_repo
        self.identity_repo = identity_repo
        self.audit_repo = audit_repo
        self.system_repo = system_repo
        # Compiler is intentionally Any right now to avoid circular dependencies with heavy modules.
        # It's injected from the DAGExecutor.
        self.compiler = prompt_compiler
        self.arq_pool = arq_pool

    @abstractmethod
    async def execute(
        self,
        step: StepRule,
        projector: StateProjector,
        context: StrategyContext,
        frozen_ctx: FrozenContext | None,
        trace: list[TraceEvent] | None,
        semaphore: asyncio.Semaphore,
        running_event: asyncio.Event | None = None,
    ) -> list[TraceEvent]:
        """Executes the specific strategy implementation cleanly.

        Args:
            step: The workflow StepRule containing execution instructions.
            projector: The V3 state projection representing the folded execution history.
            context: The immutable Pydantic wrapper for execution context limits.

        Returns:
            An array of new TraceEvents representing the node's outputs or errors.
        """
        pass

    async def assert_quota(self, org_id: str | None) -> None:
        """Enforces a 'Denial of Wallet' FinOps circuit breaker during long DAG executions.

        If the organization's token expenditure limit is exceeded mid-air, this throws
        an AppException which bubble-cancels the TaskGroup gracefully.
        """
        if not org_id:
            # Free tier or unbound system org
            return

        usage_service = UsageService(self.identity_repo, self.audit_repo)
        is_quota_safe = await usage_service.check_quota(org_id)
        if not is_quota_safe:
            msg = f"Organization '{org_id}' ran out of quota mid-execution."
            logger.warning("[Worker Cut-off] Circuit Breaker Tripped: %s", msg)
            raise AppException(
                message=msg,
                status_code=402,
                details={"error_code": ErrorCodes.RATE_LIMIT_EXCEEDED.value},
            )

    async def run_pre_hooks(
        self,
        step_obj: V2Step,
        step: StepRule,
        hook_state: HookState,
        hook_deps: HookDependencies,
    ) -> HookState:
        """Executes all pre-hooks associated with the step safely and deterministically.

        Extracts common pre-hook loops previously bundled inside the God Method execution branches.
        """
        # SSOT Enforcement: Only the Blueprint (step_obj) owns pre_hooks
        if not step_obj.pre_hooks:
            return hook_state

        for pre_hook in step_obj.pre_hooks:
            res = await hook_registry.execute(pre_hook, hook_state, hook_deps)
            if res.success and res.state_delta:
                current_data = deep_merge_dicts(hook_state.inputs, res.state_delta)
                hook_state = hook_state.model_copy(update={"inputs": current_data})
            elif not res.success:
                # RFC 7807: Hook signaled non-success — log explicitly so the audit trail captures it.
                logger.warning(
                    "[NodeStrategy] Pre-hook '%s' returned success=False for step '%s'.",
                    pre_hook,
                    step_obj.slug,
                )

        return hook_state

    async def run_post_hooks(
        self,
        step_obj: V2Step,
        step: StepRule,
        hook_state: HookState,
        hook_deps: HookDependencies,
    ) -> HookState:
        """Executes all post-hooks deterministically across both AI and synchronous domains.

        Safely relies on the strictly typed HookState which must be populated before calling this.
        """
        # SSOT Enforcement: Only the Blueprint (step_obj) owns post_hooks.
        if not step_obj.post_hooks:
            return hook_state

        for post_hook in step_obj.post_hooks:
            ph_res = await hook_registry.execute(post_hook, hook_state, hook_deps)
            if ph_res.success and ph_res.state_delta:
                final_data = deep_merge_dicts(hook_state.inputs, ph_res.state_delta)
                hook_state = hook_state.model_copy(update={"inputs": final_data})
            elif not ph_res.success:
                # RFC 7807: Post-hook signaled non-success — log explicitly so the audit trail captures it.
                logger.warning(
                    "[NodeStrategy] Post-hook '%s' returned success=False for step '%s'.",
                    post_hook,
                    step_obj.slug,
                )

        return hook_state
