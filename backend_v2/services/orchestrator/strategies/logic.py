import logging

from backend_v2.core.hook_registry import HookDependencies, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.state import StateProjector, TraceEvent
from backend_v2.models.v2_core import FrozenContext, StepRule
from backend_v2.models.v2_core import Step as V2Step
from backend_v2.services.orchestrator.strategies.base import NodeStrategy, StrategyContext
from backend_v2.utils.dict_utils import deep_merge_dicts

logger = logging.getLogger(__name__)


class LogicNodeStrategy(NodeStrategy):
    """Executes a Native/Logic Step, delegating CPU-bound work to the Hook Registry."""

    async def execute(
        self,
        step: StepRule,
        projector: StateProjector,
        context: StrategyContext,
        frozen_ctx: FrozenContext | None,
        trace: list[TraceEvent] | None,
    ) -> list[TraceEvent]:
        # 1. State Extraction
        current_state = dict(projector.snapshot)

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

        step_def = await self.repository.get_step_by_id(blueprint_id)
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

        hook_deps = HookDependencies(repository=self.repository)

        state_data = dict(current_state)
        hook_state = HookState(
            execution_id=context.execution_id,
            workflow_id=context.workflow_id,
            step_id=step.id,
            task_blueprint=blueprint_id,
            metadata=context.metadata,
            global_context_vars={},
            inputs=state_data,
        )

        # 2. Pre-Hooks
        hook_state = await self.run_pre_hooks(step_obj, step, hook_state, hook_deps)
        state_data = dict(hook_state.inputs)  # Refresh state after pre-hooks

        # 3. Main Logic Hook Execution
        # hook_registry.execute inherently handles sync/async routing.
        main_res = await hook_registry.execute(logic_hook, hook_state, hook_deps)

        if main_res.success and main_res.state_delta:
            state_data = deep_merge_dicts(state_data, main_res.state_delta)
            hook_state = hook_state.model_copy(update={"inputs": state_data})
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
        safe_context = {
            k: v.model_dump(mode="json") if hasattr(v, "model_dump") else v for k, v in dict(projector.snapshot).items()
        }

        post_hook_state = hook_state.model_copy(
            update={
                "global_context_vars": safe_context,
                "inputs": state_data,
            }
        )

        post_hook_state = await self.run_post_hooks(
            step_obj=step_obj,
            step=step,
            hook_state=post_hook_state,
            hook_deps=hook_deps,
        )
        final_outputs = dict(post_hook_state.inputs)

        # 5. Emit Immutable Event
        return [
            TraceEvent(
                step_name=step.id,
                event_type="output",
                content=final_outputs,
            )
        ]
