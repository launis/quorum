"""Logic node strategy module."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any, override

from pydantic import BaseModel

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    HookDeltaDTO,
    HookDependencies,
    HookState,
    hook_registry,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import generate_uuid7
from backend_v2.models.domain.execution import FrozenContext
from backend_v2.models.domain.inputs import DomainInputValue
from backend_v2.models.domain.step import Step as V2Step
from backend_v2.models.domain.step import StepRule
from backend_v2.models.dtos.node_execution import (
    LogicEvaluationContextDTO,
    LogicNodeStateDTO,
    StepOutputContentValue,
)
from backend_v2.models.dtos.trace import ProgressTracePayloadDTO, TraceEventMetadataDTO, TraceScoringPayloadDTO
from backend_v2.models.enums import VirtualSystemStepID
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

    async def _resolve_step_blueprint(self, step: StepRule) -> V2Step:
        """Validate step rule blueprint configuration and fetch the V2Step definition.

        Args:
            step: The workflow StepRule containing execution instructions.

        Returns:
            Hydrated V2Step definition with a verified native hook identifier.

        Raises:
            AppException: With CONFIGURATION_ERROR if the step has no blueprint or definition is not found.
            AppException: With VALIDATION_FAILED if the step definition has no native hook configured.
        """
        blueprint_id = step.task_blueprint
        if not blueprint_id:
            logger.error(
                "Step has no task_blueprint configured.",
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "step_id": step.id},
                exc_info=True,
            )
            raise AppException(
                message=f"Step {step.id} has no task_blueprint configured.",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        step_obj: V2Step | None = await self.workflow_repo.get_step_by_id(blueprint_id)
        if not step_obj:
            logger.error(
                "Configuration error: Step '%s' not found.",
                blueprint_id,
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "step_id": step.id},
                exc_info=True,
            )
            raise AppException(
                message=f"Configuration error: Step '{blueprint_id}' not found.",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        if not step_obj.hook:
            logger.error(
                "Logic step '%s' has no native hook defined.",
                blueprint_id,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "step_id": step.id},
                exc_info=True,
            )
            raise AppException(
                message=f"Logic step '{blueprint_id}' has no native hook defined.",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        return step_obj

    @staticmethod
    def _extract_inputs_payload(current_steps: list[Any]) -> dict[str, DomainInputValue]:
        """Extract domain input values from projected step outputs.

        Args:
            current_steps: Projected step output items from the StateProjector snapshot.

        Returns:
            Dictionary mapping input block identifiers to domain input values.
        """
        inputs_payload: dict[str, DomainInputValue] = {
            d.block_id: d.payload
            for d in current_steps
            if isinstance(d, StepOutputDTO)
            and d.step_id == "inputs"
            and d.block_id
            and not isinstance(d.payload, ProgressTracePayloadDTO)
        }
        if not inputs_payload:
            for d in current_steps:
                if isinstance(d, StepOutputDTO) and d.step_id == "raw_inputs" and d.block_id:
                    if d.block_id == "dynamic_inputs":
                        if not isinstance(d.payload, (str, int, float, bool, list)) and d.payload is not None:
                            for k, v in dict(d.payload).items():
                                inputs_payload[str(k)] = v
                    elif d.block_id not in (
                        "simulation_mode",
                        "language",
                        "organization_id",
                        "user_id",
                    ) and not isinstance(d.payload, ProgressTracePayloadDTO):
                        inputs_payload[d.block_id] = d.payload
        return inputs_payload

    @staticmethod
    def _build_final_outputs(
        blueprint_id: str,
        state_delta: HookDeltaDTO | None,
    ) -> dict[str, StepOutputContentValue]:
        """Serialize hook state delta into trace event output content with exclude_none parity.

        Args:
            blueprint_id: Canonical step blueprint identifier recorded in step metadata.
            state_delta: Optional typed state delta emitted by the primary logic hook.

        Returns:
            Serialized step output dictionary ready for TraceEvent emission.
        """
        final_outputs: dict[str, StepOutputContentValue] = {}
        if state_delta and state_delta.delta:
            delta_val = state_delta.delta
            if isinstance(delta_val, TraceScoringPayloadDTO):
                dumped_scoring = delta_val.model_dump(mode="json", exclude_none=True)
                final_outputs[VirtualSystemStepID.SCORING_RESULT.value] = dumped_scoring
                final_outputs.update(dumped_scoring)
            elif isinstance(delta_val, BaseModel):
                final_outputs.update(delta_val.model_dump(mode="json", exclude_none=True))
        final_outputs["_step_metadata"] = {"task_blueprint": blueprint_id}
        return final_outputs

    @override
    async def execute(
        self,
        step: StepRule,
        projector: StateProjector,
        context: StrategyContext,
        frozen_ctx: FrozenContext | None = None,
        trace: list[TraceEvent] | None = None,
        progress_callback: Callable[[int, int], Awaitable[None]] | None = None,
    ) -> list[TraceEvent]:
        """Executes a Native/Logic Step, delegating CPU-bound work to the Hook Registry.

        Args:
            step: The workflow StepRule containing execution instructions.
            projector: The V3 state projection representing the folded execution history.
            context: The immutable Pydantic wrapper for execution context limits.
            frozen_ctx: Read-only context containing parsed external inputs.
            trace: Optional current execution trace lineage.
            progress_callback: Optional async callback reporting execution progress.

        Returns:
            An array of new TraceEvents representing the node's outputs or errors.

        Raises:
            AppException: With CONFIGURATION_ERROR if the step has no blueprint or definition is not found.
            AppException: With VALIDATION_FAILED if the step definition has no native hook configured.
            AppException: With AGENT_EXECUTION_CRITICAL if hook execution returns failure.
        """
        snapshot_data = projector.snapshot
        current_steps: list[Any] = []
        if isinstance(snapshot_data, list):
            current_steps = list(snapshot_data)
        current_state = LogicNodeStateDTO(steps=current_steps, dynamic_inputs={})

        step_obj = await self._resolve_step_blueprint(step)
        blueprint_id = step.task_blueprint
        logic_hook = str(step_obj.hook)

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

        inputs_payload = self._extract_inputs_payload(current_steps)
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

        hook_state, pre_events = await self.run_pre_hooks(step_obj, step, hook_state, hook_deps)
        main_res = await hook_registry.execute(logic_hook, hook_state, hook_deps)

        if main_res.success and main_res.state_delta:
            hook_state, main_events = reduce_hook_delta(hook_state, main_res.state_delta, step.id)
            pre_events.extend(main_events)
        elif not main_res.success:
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
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.value},
            )

        _, post_events = await self.run_post_hooks(
            step_obj=step_obj,
            step=step,
            hook_state=hook_state,
            hook_deps=hook_deps,
        )
        final_outputs = self._build_final_outputs(blueprint_id, main_res.state_delta)

        return (
            pre_events
            + post_events
            + [
                TraceEvent(
                    event_id=generate_uuid7(),
                    timestamp=datetime.now(UTC),
                    step_name=step.id,
                    event_type="output",
                    content=final_outputs,
                    metadata=TraceEventMetadataDTO(mcp_audit_traces=[]),
                    mcp_audit_traces=[],
                )
            ]
        )
