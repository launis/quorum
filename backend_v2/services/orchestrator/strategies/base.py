import logging
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, ConfigDict

from backend_v2.core.hook_registry import HookDependencies, HookState, hook_registry
from backend_v2.database.repository import AbstractWorkflowRepository
from backend_v2.models.enums import ModelStrategy
from backend_v2.models.state import StateProjector, TraceEvent
from backend_v2.models.v2_core import FrozenContext, StepRule
from backend_v2.models.v2_core import Step as V2Step
from backend_v2.utils.dict_utils import deep_merge_dicts

logger = logging.getLogger(__name__)


class StrategyContext(BaseModel):
    """Immutable context wrapper enforcing strict typing and Single Responsibility for node execution.

    Follows the V2 Architecture Service Boundary Doctrine: Strict IN -> Strict OUT.
    """

    execution_id: str
    workflow_id: str
    metadata: dict[str, Any]
    expected_inputs: list[Any] | None = None
    model_strategy: ModelStrategy | str | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)


class NodeStrategy(ABC):
    """Abstract Base Class for executing a workflow node (Strategy Pattern).

    Subclasses must implement `execute` and adhere strictly to V3 Event Sourcing protocols
    by emitting immutable `TraceEvent` objects rather than mutating dictionaries in place.
    """

    def __init__(self, repository: AbstractWorkflowRepository, prompt_compiler: Any):
        self.repository = repository
        # Compiler is intentionally Any right now to avoid circular dependencies with heavy modules.
        # It's injected from the DAGExecutor.
        self.compiler = prompt_compiler

    @abstractmethod
    async def execute(
        self,
        step: StepRule,
        projector: StateProjector,
        context: StrategyContext,
        frozen_ctx: FrozenContext | None,
        trace: list[TraceEvent] | None,
    ) -> list[TraceEvent]:
        """Executes the specific strategy implementation cleanly.

        Args:
            step: The workflow StepRule containing execution instructions.
            projector: The V3 state projection representing the folded execution history.
            context: The immutable Pydantic wrapper for execution context limits.
            frozen_ctx: A context that stores MCP audit signatures and deterministic outputs securely.
            trace: Full historical log of TraceEvents (O(N) structure).

        Returns:
            An array of new TraceEvents representing the node's outputs or errors.
        """
        pass

    async def run_pre_hooks(
        self,
        step_obj: V2Step,
        step: StepRule,
        hook_state: HookState,
        hook_deps: HookDependencies,
        state_data: dict[str, Any],
    ) -> HookState:
        """Executes all pre-hooks associated with the step safely and deterministically.

        Extracts common pre-hook loops previously bundled inside the God Method execution branches.
        """
        current_data = dict(state_data)

        # SSOT Enforcement: Only the Blueprint (step_obj) owns pre_hooks
        if not step_obj.pre_hooks:
            return hook_state

        for pre_hook in step_obj.pre_hooks:
            res = await hook_registry.execute(pre_hook, hook_state, hook_deps)
            if res.success and res.state_delta:
                current_data = deep_merge_dicts(current_data, res.state_delta)
                hook_state = hook_state.model_copy(update={"inputs": current_data})

        return hook_state

    async def run_post_hooks(
        self,
        step_obj: V2Step,
        step: StepRule,
        hook_state: HookState,
        hook_deps: HookDependencies,
        final_dict: dict[str, Any],
        global_context_vars: dict[str, Any],
    ) -> dict[str, Any]:
        """Executes all post-hooks deterministically across both AI and synchronous domains.

        Safely injects global context variables so the post-hooks can act upon cross-boundary data.
        """
        post_hook_state = hook_state.model_copy(
            update={
                "global_context_vars": global_context_vars,
                "inputs": final_dict,
            }
        )

        # SSOT Enforcement: Only the Blueprint (step_obj) owns post_hooks.
        if not step_obj.post_hooks:
            return final_dict

        for post_hook in step_obj.post_hooks:
            ph_res = await hook_registry.execute(post_hook, post_hook_state, hook_deps)
            if ph_res.success and ph_res.state_delta:
                final_dict = deep_merge_dicts(final_dict, ph_res.state_delta)
                post_hook_state = post_hook_state.model_copy(update={"inputs": final_dict})

        return final_dict
