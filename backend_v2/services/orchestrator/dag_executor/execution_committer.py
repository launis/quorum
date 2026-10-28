"""ExecutionCommitter and PEP 695 execution state update aliases for DAG orchestration.

Handles atomic checkpointing of Event Sourced TraceEvents and execution state snapshots
into persistent storage via IExecutionRepository.
"""

from __future__ import annotations

import logging

from pydantic import JsonValue

from backend_v2.database.interfaces import IExecutionRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.execution import ExecutionStep, ExecutionStepState, FrozenContext
from backend_v2.models.domain.inputs import DomainInputValue
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.dtos.node_execution import NodeExecutionUpdateDTO
from backend_v2.models.dtos.schema_manifest import GeneratedSchemaManifestDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import TraceEvent

logger = logging.getLogger(__name__)

__all__ = [
    "ExecutionCommitter",
    "ExecutionRecordUpdate",
    "FrozenContextUpdate",
    "StepOutputContentValue",
]

type FrozenContextUpdate = list[MCPAuditTrace] | GeneratedSchemaManifestDTO
type ExecutionRecordUpdate = (
    ContextVariablesDTO | FrozenContext | ExecutionMetadata | dict[str, ExecutionStepState] | list[ExecutionStep]
)
type StepOutputContentValue = DomainInputValue | JsonValue


class ExecutionCommitter:
    """Handles checkpointing of the Event Sourced trace into persistent storage.

    Attributes:
        exec_repo: Repository interface for execution state persistence.
        execution_id: Unique identifier for the active execution run.
    """

    def __init__(self, exec_repo: IExecutionRepository, execution_id: str) -> None:
        """Initialize the ExecutionCommitter with database access properties.

        Args:
            exec_repo: Repository interface for executions.
            execution_id: Unique identifier for current execution tracking.
        """
        self.exec_repo = exec_repo
        self.execution_id = execution_id

    async def commit_trace(
        self,
        trace: list[TraceEvent],
        status: ExecutionStatus,
        step_states: dict[str, ExecutionStepState],
        error: str | None = None,
        frozen_context: FrozenContext | None = None,
        context_variables: ContextVariablesDTO | None = None,
        steps: list[ExecutionStep] | None = None,
    ) -> None:
        """Flush the event array and execution state snapshot to persistent storage safely.

        Args:
            trace: Current sequence of workflow events.
            status: Target execution status boundary.
            step_states: Execution state dictionary mapping per-step states.
            error: Optional execution failure message to record.
            frozen_context: Frozen context snapshot state if provided.
            context_variables: Execution level global variables.
            steps: Optional list of ExecutionStep objects to persist.

        Returns:
            None.

        Raises:
            AppException: Triggered with PROGRESS_UPDATE_FAILED if db commit transaction or validation fails.
        """
        try:
            if not self.execution_id.strip():
                raise ValueError("Execution ID cannot be empty when committing trace.")
            update_node = NodeExecutionUpdateDTO(
                status=status,
                execution_trace=trace,
                step_states=step_states,
                frozen_context=frozen_context,
                context_variables=context_variables,
                error=error,
                steps=steps,
            )
            update_dto = update_node.to_execution_update_dto()
            await self.exec_repo.update_execution(self.execution_id, update_dto)
        except Exception as e:
            msg = f"Failed to commit execution trace for {self.execution_id}"
            logger.error("[ExecutionCommitter] %s: %s", ErrorCodes.PROGRESS_UPDATE_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                details={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED},
                status_code=500,
            ) from e
