"""Logic node strategy module."""

import asyncio
import logging
from collections.abc import Awaitable, Callable, Mapping
from typing import Any

from pydantic import BaseModel, JsonValue

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    HookDependencies,
    HookState,
    hook_registry,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.execution import FrozenContext
from backend_v2.models.domain.inputs import DomainInputValue
from backend_v2.models.domain.step import Step as V2Step
from backend_v2.models.domain.step import StepRule
from backend_v2.models.dtos.node_execution import LogicEvaluationContextDTO, LogicNodeStateDTO
from backend_v2.models.state import StateProjector, StepOutputDTO, TraceEvent
from backend_v2.services.orchestrator.state_reducer import reduce_hook_delta
from backend_v2.services.orchestrator.strategies.base import NodeStrategy, StrategyContext, StrategyDependencies

logger = logging.getLogger(__name__)

__all__ = ["LogicNodeStrategy"]


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
            AppException: With CONFIGURATION_ERROR if the step has no blueprint or definition is not found.
            AppException: With VALIDATION_FAILED if the step definition has no native hook configured.
            AppException: With AGENT_EXECUTION_CRITICAL if hook execution returns failure.
        """
        if running_event is not None:
            running_event.set()
        # 1. State Extraction
        snapshot_data = projector.snapshot
        current_steps: list[Any] = []
        if isinstance(snapshot_data, list):
            current_steps = list(snapshot_data)
        current_state = LogicNodeStateDTO(steps=current_steps)

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

        inputs_payload: dict[str, DomainInputValue] = {
            d.block_id: d.payload  # type: ignore[misc]
            for d in current_steps
            if isinstance(d, StepOutputDTO) and d.step_id == "inputs" and d.block_id
        }
        if not inputs_payload:
            for d in current_steps:
                if isinstance(d, StepOutputDTO) and d.step_id == "raw_inputs" and d.block_id:
                    if d.block_id == "dynamic_inputs" and isinstance(d.payload, Mapping):
                        for k, v in d.payload.items():
                            inputs_payload[str(k)] = v
                    elif d.block_id not in ("simulation_mode", "language", "organization_id", "user_id"):
                        inputs_payload[d.block_id] = d.payload  # type: ignore[assignment]

        safe_context = LogicEvaluationContextDTO(
            execution_id=context.execution_id,
            workflow_id=context.workflow_id,
            step_id=step.id,
            task_blueprint=blueprint_id,
            metadata=context.metadata,
            global_context_vars=context.global_context_vars,
            inputs=ExecutionInputsDTO(
                dynamic_inputs={"steps": current_state.steps},
                raw_inputs=inputs_payload,
            ),
            target_locale=context.target_locale,
        )
        hook_state = HookState(
            execution_id=safe_context.execution_id,
            workflow_id=safe_context.workflow_id,
            step_id=safe_context.step_id,
            task_blueprint=safe_context.task_blueprint,
            metadata=safe_context.metadata,
            global_context_vars=safe_context.global_context_vars,
            inputs=safe_context.inputs,
        )

        # 2. Pre-Hooks
        hook_state, pre_events = await self.run_pre_hooks(step_obj, step, hook_state, hook_deps)

        # 3. Main Logic Hook Execution

        # hook_registry.execute inherently handles sync/async routing.
        main_res = await hook_registry.execute(logic_hook, hook_state, hook_deps)

        if main_res.success and main_res.state_delta:
            hook_state, main_events = reduce_hook_delta(hook_state, main_res.state_delta, step.id)
            pre_events.extend(main_events)
        elif not main_res.success:
            # Fail-Fast: The primary logic hook returning success=False is a hard execution error.
            msg = f"Logic hook '{logic_hook}' for step '{step.id}' returned success=False."
            logger.error(
                "Logic hook '%s' for step '%s' returned success=False.",
                logic_hook,
                step.id,
                extra={
                    "error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.name,
                    "step_id": step.id,
                    "hook": logic_hook,
                },
            )
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.value},
            )
        # 4. Post-Hooks
        post_hook_state, post_events = await self.run_post_hooks(
            step_obj=step_obj,
            step=step,
            hook_state=hook_state,
            hook_deps=hook_deps,
        )
        final_outputs: dict[str, JsonValue] = {}
        if main_res.state_delta and main_res.state_delta.delta:
            delta_val = main_res.state_delta.delta
            if isinstance(delta_val, BaseModel):
                final_outputs.update(delta_val.model_dump(mode="json"))
        final_outputs["_step_metadata"] = {"task_blueprint": blueprint_id}

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
