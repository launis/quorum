"""LLM Node Strategy for DAG-based workflow execution.

Orchestrates AI/LLM step execution including dynamic schema compilation,
chunked map-reduce evaluation, DLQ graceful degradation, and anomaly retry logic.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, override

if TYPE_CHECKING:
    from backend_v2.services.orchestrator.engines.base import ExecutionEngine

from backend_v2.core.hook_registry import HookState
from backend_v2.llm.client import LLMClient as LLMClient
from backend_v2.models.domain.execution import FrozenContext
from backend_v2.models.domain.step import StepRule
from backend_v2.models.dtos.engine import EngineExecutionRequest as EngineExecutionRequest
from backend_v2.models.dtos.hook_delta import StepContextMetadataDTO
from backend_v2.models.state import StateProjector, TraceEvent
from backend_v2.services.mcp.mcp_tool_loop import execute_mcp_retrieval as execute_mcp_retrieval
from backend_v2.services.orchestrator.strategies.base import NodeStrategy, StrategyContext, StrategyDependencies
from backend_v2.services.orchestrator.strategies.llm_execution.context_builder import ContextBuilder as ContextBuilder
from backend_v2.services.orchestrator.strategies.llm_execution.prompt_factory import PromptFactory as PromptFactory
from backend_v2.services.orchestrator.strategies.llm_strategy.blueprint_and_metadata_stage import (
    _SCHEMA_BLOCK_EXTENSION as _SCHEMA_BLOCK_EXTENSION,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.blueprint_and_metadata_stage import (
    _SCHEMA_BLOCK_MATRIX as _SCHEMA_BLOCK_MATRIX,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.blueprint_and_metadata_stage import (
    _SCHEMA_BLOCK_SYSTEM as _SCHEMA_BLOCK_SYSTEM,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.blueprint_and_metadata_stage import (
    _SCHEMA_BLOCK_TEXT as _SCHEMA_BLOCK_TEXT,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.blueprint_and_metadata_stage import (
    BlueprintStageResult as BlueprintStageResult,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.blueprint_and_metadata_stage import (
    NodeStatePayload as NodeStatePayload,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.blueprint_and_metadata_stage import (
    dlq_handle_debug_log_error as dlq_handle_debug_log_error,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.blueprint_and_metadata_stage import (
    execute_blueprint_and_pre_hooks_stage as execute_blueprint_and_pre_hooks_stage,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.blueprint_and_metadata_stage import (
    extract_step_context_metadata as extract_step_context_metadata,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.engine_retry_stage import (
    EngineRetryStageResult as EngineRetryStageResult,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.engine_retry_stage import (
    execute_engine_retry_stage as execute_engine_retry_stage,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.prompt_and_schema_stage import (
    PromptAndSchemaStageResult as PromptAndSchemaStageResult,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.prompt_and_schema_stage import (
    execute_prompt_and_schema_stage as execute_prompt_and_schema_stage,
)
from backend_v2.services.orchestrator.strategies.llm_strategy.trace_event_stage import (
    build_llm_step_trace_events as build_llm_step_trace_events,
)
from backend_v2.settings import get_settings as get_settings

__all__ = [
    "BlueprintStageResult",
    "ContextBuilder",
    "EngineExecutionRequest",
    "EngineRetryStageResult",
    "LLMClient",
    "LLMNodeStrategy",
    "NodeStatePayload",
    "PromptAndSchemaStageResult",
    "PromptFactory",
    "_SCHEMA_BLOCK_EXTENSION",
    "_SCHEMA_BLOCK_MATRIX",
    "_SCHEMA_BLOCK_SYSTEM",
    "_SCHEMA_BLOCK_TEXT",
    "build_llm_step_trace_events",
    "dlq_handle_debug_log_error",
    "execute_blueprint_and_pre_hooks_stage",
    "execute_engine_retry_stage",
    "execute_mcp_retrieval",
    "execute_prompt_and_schema_stage",
    "extract_step_context_metadata",
    "get_settings",
]

logger = logging.getLogger(__name__)


class LLMNodeStrategy(NodeStrategy):
    """Executes an AI/LLM Step.

    Manages dynamic schema compilation, instruction aggregation, tracing optimization
    for token context explosion, and routes through either a standard structured prediction
    task or an autonomous MCP Tool Loop depending on step configuration.
    """

    def __init__(
        self,
        deps: StrategyDependencies,
        engine: ExecutionEngine | None = None,
    ) -> None:
        """Initialize the LLM strategy with StrategyDependencies and optional engine.

        Args:
            deps: Immutable container holding repositories, compiler, and pools.
            engine: Optional execution engine instance.
        """
        super().__init__(deps=deps)
        self._engine = engine

    @staticmethod
    def _dlq_handle_debug_log_error(exc: Exception) -> None:
        """Handle debug prompt logging failures in development gracefully.

        Args:
            exc: Exception encountered during debug prompt logging.
        """
        # Phase 1, Step 2: Delegate debug log error handler to blueprint_and_metadata_stage
        dlq_handle_debug_log_error(exc, step_logger=logger)

    def _extract_step_context_metadata(
        self,
        hook_state: HookState,
        context: StrategyContext | None = None,
    ) -> StepContextMetadataDTO:
        """Extract global vars, document aliases, and DAG input results from HookState.

        Args:
            hook_state: Ingress hook state holding inputs and context variables.
            context: Strategy configuration parameters holding context_variables.

        Returns:
            StepContextMetadataDTO containing gvars, doc_aliases, and dag_results.
        """
        # Phase 1, Step 2: Delegate step context metadata extraction to blueprint_and_metadata_stage
        return extract_step_context_metadata(hook_state, context)

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
        """Executes the node's workflow sequence matching system rules.

        Args:
            step: Rule defining the workflow execution block configuration.
            projector: Database representation of current structured historical trace.
            context: Strategy configuration parameters (model, metadata, strictness).
            frozen_ctx: Accumulator state matching prompt caches and MCP traces.
            trace: List of chronological events.
            progress_callback: Optional async callback reporting processed and total item progress.

        Returns:
            List containing the computed outputs packed into structured TraceEvents.

        Raises:
            AppException: With ErrorCodes.CONFIGURATION_ERROR, ErrorCodes.VALIDATION_FAILED,
                or ErrorCodes.RESOURCE_NOT_FOUND upon missing configuration, invalid models, or missing records.
            ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR upon missing mandatory step/profile blocks.
        """
        # Phase 1, Step 2: Delegate Stage 1 blueprint resolution and pre-hooks to blueprint_and_metadata_stage
        stage1 = await execute_blueprint_and_pre_hooks_stage(
            step=step,
            projector=projector,
            context=context,
            deps=self.deps,
            run_pre_hooks_fn=self.run_pre_hooks,
            step_logger=logger,
        )

        # Phase 2, Step 2: Delegate Stage 2 context building, prompt compilation, and dynamic schema resolution
        stage2 = await execute_prompt_and_schema_stage(
            stage1=stage1,
            step=step,
            context=context,
            deps=self.deps,
            frozen_ctx=frozen_ctx,
            engine=self._engine,
            settings_getter=get_settings,
            step_logger=logger,
        )

        # Phase 3, Step 2: Delegate Stage 3 LLMClient binding, MCP tool loop, and engine retry loop
        stage3 = await execute_engine_retry_stage(
            stage1=stage1,
            stage2=stage2,
            step=step,
            context=context,
            deps=self.deps,
            engine=self._engine,
            run_post_hooks_fn=self.run_post_hooks,
            progress_callback=progress_callback,
            request_cls=EngineExecutionRequest,
            mcp_retrieval_fn=execute_mcp_retrieval,
            extract_metadata_fn=self._extract_step_context_metadata,
            settings_getter=get_settings,
            step_logger=logger,
        )

        # Phase 3, Step 2: Delegate Stage 4 telemetry merging and TraceEvent assembly
        return build_llm_step_trace_events(
            stage1=stage1,
            stage2=stage2,
            stage3=stage3,
            step=step,
            engine=self._engine,
        )
