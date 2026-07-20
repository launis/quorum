"""Execution Engine Base Protocol.

Provides the structural protocol for polymorphic TDA pipeline execution.
"""

from typing import Protocol, runtime_checkable

from backend_v2.models.dtos.engine import EngineExecutionRequest, EngineExecutionResult


@runtime_checkable
class ExecutionEngine(Protocol):
    """Protocol for execution engines.

    Engines are fundamentally stateless across execute() calls.
    All context, state, limits, and callbacks must be passed in the request payload.
    """

    async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:
        """Executes the pipeline over the given request.

        Args:
            request: The EngineExecutionRequest containing all required context and callbacks.

        Returns:
            The EngineExecutionResult with projected atoms and references.

        Raises:
            AppException: If engine execution fails catastrophically or concurrency bounds are exceeded.
        """
        ...
