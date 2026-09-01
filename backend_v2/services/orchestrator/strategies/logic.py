"""Logic node strategy module."""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookState,
    hook_registry,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.state import StateProjector, TraceEvent
from backend_v2.models.v2_core import FrozenContext, StepRule
from backend_v2.models.v2_core import Step as V2Step
from backend_v2.services.orchestrator.state_reducer import merge_dynamic_inputs
from backend_v2.services.orchestrator.strategies.base import NodeStrategy, StrategyContext, StrategyDependencies

logger = logging.getLogger(__name__)


class LogicNodeStrategy(NodeStrategy):
    """Executes a Native/Logic Step, delegating CPU-bound work to the Hook Registry."""

    def __init__(self, deps: StrategyDependencies) -> None:
        """Initialize LogicNodeStrategy with StrategyDependencies container.

        Args:
            deps: Immutable dependency container.
        """
        super().__init__(deps=deps)

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
        """Executes a Native/Logic Step, delegating CPU-bound work to the Hook Registry.

        Args:
            step: The workflow StepRule containing execution instructions.
            projector: The V3 state projection representing the folded execution history.
            context: The immutable Pydantic wrapper for execution context limits.
            frozen_ctx: Read-only context containing parsed external inputs.
            trace: Optional current execution trace lineage.
            semaphore: Asyncio semaphore for concurrency limits.
            running_event: Optional event to track if the execution is still running.
            progress_callback: Optional async callback reporting execution progress.

        Returns:
            An array of new TraceEvents representing the node's outputs or errors.

        Raises:
            AppException: If configuration is invalid or logic hook execution fails.
        """
        if running_event is not None:
            running_event.set()
        # 1. State Extraction
        # Epic 43 Phase 2 Fail-Fast Parity: Re-inject 'inputs' and 'raw_inputs' DTO payloads into the root state
        # so legacy dot-notation mappings resolve properly without Naked Dict violations.
        inputs_payload = {d.block_id: d.payload for d in projector.snapshot if d.step_id == "inputs"}

        raw_inputs_payload = {d.block_id: d.payload for d in projector.snapshot if d.step_id == "raw_inputs"}

        current_state: dict[str, Any] = {
            "steps": projector.snapshot,
            "inputs": inputs_payload,
            "raw_inputs": raw_inputs_payload,
        }

        blueprint_id = step.task_blueprint
        if not blueprint_id:
            logger.error(
                "Step has no task_blueprint configured.",
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "step_id": step.id},
            )
            raise AppException(
                message=f"Step {step.id} has no task_blueprint configured.",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        step_def = await self.workflow_repo.get_step_by_id(blueprint_id)
        if not step_def:
            logger.error(
                "Configuration error: Step '%s' not found.",
                blueprint_id,
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "step_id": step.id},
            )
            raise AppException(
                message=f"Configuration error: Step '{blueprint_id}' not found.",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        step_obj = V2Step.model_validate(step_def)

        logic_hook = step_obj.hook
        if not logic_hook:
            logger.error(
                "Logic step '%s' has no native hook defined.",
                blueprint_id,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "step_id": step.id},
            )
            raise AppException(
                message=f"Logic step '{blueprint_id}' has no native hook defined.",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        hook_deps = HookDependencies(
            exec_repo=self.exec_repo,
            workflow_repo=self.workflow_repo,
            comp_repo=self.comp_repo,
            prompt_block_repo=self.prompt_block_repo,
            output_profile_repo=self.output_profile_repo,
            identity_repo=self.identity_repo,
            audit_repo=self.audit_repo,
            system_repo=self.system_repo,
        )

        state_data = dict(current_state)
        hook_state = HookState(
            execution_id=context.execution_id,
            workflow_id=context.workflow_id,
            step_id=step.id,
            task_blueprint=blueprint_id,
            metadata=context.metadata,
            global_context_vars=GlobalContextVarsDTO(vars=context.global_context_vars),
            inputs=ExecutionInputsDTO(dynamic_inputs=state_data),
        )

        # 2. Pre-Hooks
        hook_state, pre_events = await self.run_pre_hooks(step_obj, step, hook_state, hook_deps)
        state_data = dict(hook_state.inputs.dynamic_inputs)  # Refresh state after pre-hooks

        # 3. Main Logic Hook Execution
        # hook_registry.execute inherently handles sync/async routing.
        main_res = await hook_registry.execute(logic_hook, hook_state, hook_deps)

        if main_res.success and main_res.state_delta:
            delta_dict = main_res.state_delta.delta
            state_data = merge_dynamic_inputs(state_data, delta_dict)
            hook_state = hook_state.model_copy(update={"inputs": ExecutionInputsDTO(dynamic_inputs=state_data)})
        elif not main_res.success:
            # Fail-Fast: The primary logic hook returning success=False is a hard execution error.
            msg = f"Logic hook '{logic_hook}' for step '{step.id}' returned success=False."
            logger.error("[LogicStrategy] %s: %s", ErrorCodes.AGENT_EXECUTION_CRITICAL.name, msg)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.value},
            )
        # 4. Post-Hooks
        safe_context: dict[str, Any] = {**hook_state.global_context_vars.vars, "steps": projector.snapshot}

        post_hook_state = hook_state.model_copy(
            update={
                "global_context_vars": GlobalContextVarsDTO(vars=safe_context),
                "inputs": ExecutionInputsDTO(
                    dynamic_inputs=state_data,
                    raw_inputs=state_data,
                    target_locale=hook_state.inputs.target_locale
                    if isinstance(hook_state.inputs, ExecutionInputsDTO)
                    else None,
                    user_role=hook_state.inputs.user_role
                    if isinstance(hook_state.inputs, ExecutionInputsDTO)
                    else None,
                ),
            }
        )

        post_hook_state, post_events = await self.run_post_hooks(
            step_obj=step_obj,
            step=step,
            hook_state=post_hook_state,
            hook_deps=hook_deps,
        )
        final_outputs = dict(main_res.state_delta.delta) if main_res.state_delta else {}
        meta = final_outputs.setdefault("_step_metadata", {})
        meta["task_blueprint"] = blueprint_id

        # 5. Emit Immutable Event
        return (
            pre_events
            + post_events
            + [
                TraceEvent(
                    step_name=step.id,
                    event_type="output",
                    content=final_outputs,
                )
            ]
        )
