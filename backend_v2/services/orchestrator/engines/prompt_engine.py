"""Prompt Execution Engine.

Implements the ExecutionEngine protocol for structured non-matrix LLM prompt tasks.
"""

import logging

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.engine import EngineExecutionRequest, EngineExecutionResult
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.engines.base import ExecutionEngine

logger = logging.getLogger(__name__)

__all__ = ["PromptEngine"]


class PromptEngine(ExecutionEngine):
    """Engine executing structured non-matrix LLM prompt tasks."""

    def __init__(self, task_executor: LLMTaskExecutor) -> None:
        """Initialize the PromptEngine with injected LLMTaskExecutor.

        Args:
            task_executor: Service for executing structured LLM tasks.
        """
        self.task_executor = task_executor

    async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:
        """Execute structured LLM prompt task with Fail-Fast validations.

        Args:
            request: The EngineExecutionRequest containing compiled schemas and context.

        Returns:
            EngineExecutionResult containing validated structured output model and token usage.

        Raises:
            AppException: If compiled_schema or hydrated_messages are missing, or LLM execution fails.
        """
        if request.compiled_schema is None:
            msg = f"PromptEngine requires compiled_schema on Step '{request.step.id}'."
            logger.error("[PromptEngine] %s: %s", ErrorCodes.PROMPT_ENGINE_ERROR.name, msg)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.PROMPT_ENGINE_ERROR.value, "step_id": request.step.id},
            )

        if not request.hydrated_messages:
            msg = f"PromptEngine received empty hydrated_messages on Step '{request.step.id}'."
            logger.error("[PromptEngine] %s: %s", ErrorCodes.PROMPT_ENGINE_ERROR.name, msg)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.PROMPT_ENGINE_ERROR.value, "step_id": request.step.id},
            )

        if request.running_event:
            request.running_event.set()

        async with request.semaphore_cm:
            synthesis_output, usage = await self.task_executor.execute_structured_task(
                client=request.bound_client,
                messages=request.hydrated_messages,
                response_model=request.compiled_schema,
            )

        return EngineExecutionResult(
            results=[],
            hydrated_references={},
            synthesis_output=synthesis_output,
            usage=usage,
        )
