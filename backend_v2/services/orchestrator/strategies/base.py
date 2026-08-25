import asyncio
import logging
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend_v2.core.hook_registry import HookDependencies, HookState, hook_registry
from backend_v2.database.interfaces import (
    IAuditRepository,
    IComponentRepository,
    IExecutionRepository,
    IIdentityRepository,
    IOutputProfileRepository,
    IPromptBlockRepository,
    ISystemRepository,
    IWorkflowRepository,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.prompt_blocks import PromptBlock
from backend_v2.models.enums import StrictnessAnchor
from backend_v2.models.state import StateProjector, TraceEvent
from backend_v2.models.v2_core import ExpectedInput, FrozenContext, StepRule
from backend_v2.models.v2_core import Step as V2Step
from backend_v2.services.usage_service import UsageService
from backend_v2.utils.dict_utils import deep_merge_dicts

logger = logging.getLogger(__name__)


class StrategyContext(BaseModel):
    """Immutable context wrapper enforcing strict typing and Single Responsibility for node execution.

    Follows the V2 Architecture Service Boundary Doctrine: Strict IN -> Strict OUT.

    Attributes:
        execution_id: ID of the parent execution.
        workflow_id: ID of the parent workflow.
        metadata: Execution metadata dictionary.
        expected_inputs: Optional expected inputs definition.
        model_strategy: Optional strategy profile.
        strictness_level: Int representing strictness level.
        global_context_vars: Global context variables.
        context_variables: Local context variables.
        prompt_blocks: Hydrated prompt blocks for execution.
    """

    execution_id: str
    workflow_id: str
    metadata: dict[str, Any]
    expected_inputs: list[ExpectedInput] | None = None
    model_strategy: str | None = None
    strictness_level: int = StrictnessAnchor.STANDARD.value
    global_context_vars: dict[str, Any] = Field(default_factory=dict)
    context_variables: dict[str, Any] = Field(default_factory=dict)
    prompt_blocks: list[PromptBlock] = Field(default_factory=list)

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True, extra="forbid")


@dataclass(frozen=True)
class StrategyDependencies:
    """Immutable dependency container injected into execution strategies."""

    exec_repo: IExecutionRepository
    workflow_repo: IWorkflowRepository
    comp_repo: IComponentRepository
    prompt_block_repo: IPromptBlockRepository
    output_profile_repo: IOutputProfileRepository
    identity_repo: IIdentityRepository
    audit_repo: IAuditRepository
    system_repo: ISystemRepository
    prompt_compiler: Any
    arq_pool: Any | None = None


class NodeStrategy(ABC):
    """Abstract Base Class for executing a workflow node (Strategy Pattern).

    Subclasses must implement `execute` and adhere strictly to V3 Event Sourcing protocols
    by emitting immutable `TraceEvent` objects rather than mutating dictionaries in place.
    """

    def __init__(self, deps: StrategyDependencies) -> None:
        """Initialize the NodeStrategy with the typed StrategyDependencies container.

        Args:
            deps: Immutable container holding repositories, compiler, and pools.
        """
        self.deps = deps

    @property
    def exec_repo(self) -> IExecutionRepository:
        return self.deps.exec_repo

    @property
    def workflow_repo(self) -> IWorkflowRepository:
        return self.deps.workflow_repo

    @property
    def comp_repo(self) -> IComponentRepository:
        return self.deps.comp_repo

    @property
    def prompt_block_repo(self) -> IPromptBlockRepository:
        return self.deps.prompt_block_repo

    @property
    def output_profile_repo(self) -> IOutputProfileRepository:
        return self.deps.output_profile_repo

    @property
    def identity_repo(self) -> IIdentityRepository:
        return self.deps.identity_repo

    @property
    def audit_repo(self) -> IAuditRepository:
        return self.deps.audit_repo

    @property
    def system_repo(self) -> ISystemRepository:
        return self.deps.system_repo

    @property
    def compiler(self) -> Any:
        return self.deps.prompt_compiler

    @property
    def arq_pool(self) -> Any | None:
        return self.deps.arq_pool

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
        progress_callback: Callable[[int, int], Awaitable[None]] | None = None,
    ) -> list[TraceEvent]:
        """Executes the specific strategy implementation cleanly.

        Args:
            step: The workflow StepRule containing execution instructions.
            projector: The V3 state projection representing the folded execution history.
            context: The immutable Pydantic wrapper for execution context limits.
            frozen_ctx: Read-only context containing parsed external inputs.
            trace: Optional current execution trace lineage.
            semaphore: Asyncio semaphore for concurrency limits.
            running_event: Optional event to track if the execution is still running.

        Returns:
            An array of new TraceEvents representing the node's outputs or errors.
        """
        pass

    async def assert_quota(self, org_id: str | None) -> None:
        """Enforces a 'Denial of Wallet' FinOps circuit breaker during long DAG executions.

        If the organization's token expenditure limit is exceeded mid-air, this throws
        an AppException which bubble-cancels the TaskGroup gracefully.

        Args:
            org_id: Optional organization ID to check quota for.

        Raises:
            AppException: If the token limit is exceeded (ErrorCodes.RATE_LIMIT_EXCEEDED).
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
    ) -> tuple[HookState, list[TraceEvent]]:
        """Executes all pre-hooks associated with the step safely and deterministically.

        Extracts common pre-hook loops previously bundled inside the God Method execution branches.

        Args:
            step_obj: The V2Step definition containing the hooks.
            step: The node step rule from the DAG.
            hook_state: The current state of the execution hook.
            hook_deps: Dependencies injected into the hook.

        Returns:
            A tuple containing the mutated HookState and a list of TraceEvents.
        """
        emitted_events: list[TraceEvent] = []
        # SSOT Enforcement: Only the Blueprint (step_obj) owns pre_hooks
        if not step_obj.pre_hooks:
            return hook_state, emitted_events

        for pre_hook in step_obj.pre_hooks:
            res = await hook_registry.execute(pre_hook, hook_state, hook_deps)
            if res.success and res.state_delta:
                delta = dict(res.state_delta)
                metadata_updates = delta.pop("metadata", None)
                if metadata_updates:
                    new_metadata = dict(hook_state.metadata)
                    new_metadata.update(metadata_updates)
                    hook_state = hook_state.model_copy(update={"metadata": new_metadata})

                gvars_updates = delta.pop("global_context_vars", None)
                if gvars_updates:
                    new_gvars = dict(hook_state.global_context_vars)
                    new_gvars.update(gvars_updates)
                    hook_state = hook_state.model_copy(update={"global_context_vars": new_gvars})

                    # V2 Mandate: Emit an explicit event sourcing trace for context updates
                    # Use existing allowed Literal 'decision' to preserve cross-language enum parity with Flutter
                    emitted_events.append(
                        TraceEvent(
                            step_name=step.id,
                            event_type="decision",
                            content=gvars_updates,
                            metadata={"is_context_update": True},
                        )
                    )

                current_data = deep_merge_dicts(hook_state.inputs, delta)
                hook_state = hook_state.model_copy(update={"inputs": current_data})
            elif not res.success:
                # RFC 7807: Hook signaled non-success — log explicitly so the audit trail captures it.
                logger.warning(
                    "[NodeStrategy] Pre-hook '%s' returned success=False for step '%s'.",
                    pre_hook,
                    step_obj.id,
                )

        return hook_state, emitted_events

    async def run_post_hooks(
        self,
        step_obj: V2Step,
        step: StepRule,
        hook_state: HookState,
        hook_deps: HookDependencies,
    ) -> tuple[HookState, list[TraceEvent]]:
        """Executes all post-hooks deterministically across both AI and synchronous domains.

        Safely relies on the strictly typed HookState which must be populated before calling this.

        Args:
            step_obj: The V2Step definition containing the hooks.
            step: The node step rule from the DAG.
            hook_state: The current state of the execution hook.
            hook_deps: Dependencies injected into the hook.

        Returns:
            A tuple containing the mutated HookState and a list of TraceEvents.
        """
        emitted_events: list[TraceEvent] = []
        # SSOT Enforcement: Only the Blueprint (step_obj) owns post_hooks.
        if not step_obj.post_hooks:
            return hook_state, emitted_events

        for post_hook in step_obj.post_hooks:
            ph_res = await hook_registry.execute(post_hook, hook_state, hook_deps)
            if ph_res.success and ph_res.state_delta:
                delta = dict(ph_res.state_delta)
                metadata_updates = delta.pop("metadata", None)
                if metadata_updates:
                    new_metadata = dict(hook_state.metadata)
                    new_metadata.update(metadata_updates)
                    hook_state = hook_state.model_copy(update={"metadata": new_metadata})

                gvars_updates = delta.pop("global_context_vars", None)
                if gvars_updates:
                    new_gvars = dict(hook_state.global_context_vars)
                    new_gvars.update(gvars_updates)
                    hook_state = hook_state.model_copy(update={"global_context_vars": new_gvars})

                    # V2 Mandate: Emit an explicit event sourcing trace for context updates
                    # Use existing allowed Literal 'decision' to preserve cross-language enum parity with Flutter
                    emitted_events.append(
                        TraceEvent(
                            step_name=step.id,
                            event_type="decision",
                            content=gvars_updates,
                            metadata={"is_context_update": True},
                        )
                    )

                final_data = deep_merge_dicts(hook_state.inputs, delta)
                hook_state = hook_state.model_copy(update={"inputs": final_data})
            elif not ph_res.success:
                # RFC 7807: Post-hook signaled non-success — log explicitly so the audit trail captures it.
                logger.warning(
                    "[NodeStrategy] Post-hook '%s' returned success=False for step '%s'.",
                    post_hook,
                    step_obj.id,
                )

        return hook_state, emitted_events
