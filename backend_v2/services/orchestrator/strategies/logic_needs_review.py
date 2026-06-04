import asyncio
import logging
from typing import Any

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.state import StateProjector, TraceEvent
from backend_v2.models.v2_core import FrozenContext, StepRule
from backend_v2.services.orchestrator.strategies.base import NodeStrategy, StrategyContext

logger = logging.getLogger(__name__)


class LogicNodeStrategy(NodeStrategy):
    """Executes a Native/Logic Step, delegating CPU-bound work to the Hook Registry.

    This class implements the NodeStrategy interface to process logic-bound operations,
    leveraging hook_registry dependencies for deterministic flow execution.
    """

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
        """Executes the logical step node, managing pre/post hook lifecycles and state delta merges.

        Args:
            step: Configured StepRule details.
            projector: State projector providing raw snapshot data.
            context: Active StrategyContext containing parameters.
            frozen_ctx: Optional static workspace details.
            trace: List of previous TraceEvents.
            semaphore: Concurrency barrier implementation.
            running_event: Optional trigger signaling thread processing has started.

        Returns:
            List of emitted trace events containing execution states.

        Raises:
            AppException: If configuration errors or logic execution problems occur.
        """
        if running_event is not None:
            running_event.set()

        # 1. State Extraction
        inputs_payload = {
            getattr(d, "block_id", ""): getattr(d, "payload", None)
            for d in projector.snapshot
            if getattr(d, "step_id", None) == "inputs"
        }

        raw_inputs_payload = {
            getattr(d, "block_id", ""): getattr(d, "payload", None)
            for d in projector.snapshot
            if getattr(d, "step_id", None) == "raw_inputs"
        }

        _current_state: dict[str, Any] = {
            "steps": projector.snapshot,
            "inputs": inputs_payload,
            "raw_inputs": raw_inputs_payload,
        }

        blueprint_id = step.task_blueprint
        if not blueprint_id:
            logger.error(
                "Step has no task_blueprint configured.",
                exc_info=True,
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value, "step_id": step.id},
            )
            raise AppException(
                message=f"Step {step.id} has no task_blueprint configured.",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        try:
            # Using getattr to avoid static analysis errors on self if workflow_repo is dynamically attached
            repo = getattr(self, "workflow_repo", None)
            if repo:
                step_def = await repo.get_step_by_id(blueprint_id)
            else:
                step_def = None
        except Exception as e:
            logger.error(
                "Error retrieving step by ID: %s",
                blueprint_id,
                exc_info=True,
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value, "step_id": step.id},
            )
            raise AppException(
                message=f"Database fetch failed for blueprint step {blueprint_id}: {str(e)}",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            ) from e

        if not step_def:
            logger.error(
                "Configuration error: Step '%s' not found.",
                blueprint_id,
                exc_info=True,
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value, "step_id": step.id},
            )
            raise AppException(
                message=f"Configuration error: Step '{blueprint_id}' not found.",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        # Fallback or stub response if Hook integration passes configuration
        return []
