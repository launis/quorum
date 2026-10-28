"""NodeExecutor isolated step execution engine and OpenTelemetry span wrapper."""

from __future__ import annotations

import contextlib
import dataclasses
import logging
import sys
from collections.abc import Awaitable, Callable
from typing import Any

import opentelemetry.trace as otel_trace
from pydantic import ValidationError

from backend_v2.core.hook_registry import GlobalContextVarsDTO
from backend_v2.core.telemetry import get_tracer
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.execution import FrozenContext
from backend_v2.models.domain.prompt_blocks import PromptBlock
from backend_v2.models.domain.step import Step, StepRule
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.enums import CognitiveTier, StepType, StrictnessAnchor
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import ErrorTraceEvent, StateProjector, TraceEvent
from backend_v2.services.orchestrator.context_router import ContextRouter
from backend_v2.services.orchestrator.engines import ExecutionEngine, build_execution_engine
from backend_v2.services.orchestrator.strategies.base import StrategyContext, StrategyDependencies
from backend_v2.services.orchestrator.strategies.registry import NodeStrategyFactory

logger = logging.getLogger(__name__)
__all__ = ["NodeExecutor"]
_DAG_EXECUTOR_MODULE = "backend_v2.services.orchestrator.dag_executor"


def _hydrate_step_definition(step_candidate: Any) -> Step:
    """Hydrate a Step blueprint model using dag_executor.Step when loaded for patch compatibility."""
    step_cls: type[Step] = sys.modules[_DAG_EXECUTOR_MODULE].Step if _DAG_EXECUTOR_MODULE in sys.modules else Step
    return step_cls.model_validate(step_candidate)


# Phase 2, Step 1: Relocate NodeExecutor into dedicated sub-module
class NodeExecutor:
    """Executes a single step in pure isolation, emitting TraceEvents."""

    def __init__(self, deps: StrategyDependencies) -> None:
        """Initialize NodeExecutor with typed StrategyDependencies container."""
        self.deps = deps

    @staticmethod
    def _dlq_record_node_error(step_id: str, exc: Exception) -> list[TraceEvent]:
        """Dead-letter error recording for failed step execution returning error trace."""
        logger.error("[NodeExecutor] Dual-Reporting Exception for step %s: %s", step_id, str(exc), exc_info=True)
        return [
            ErrorTraceEvent(
                step_name=step_id, error_code="STEP_FAILED", error_message=str(exc), content={"traceback": str(exc)}
            )
        ]

    def _resolve_execution_engine(
        self, step_def: Step, prompt_blocks: list[PromptBlock] | None = None
    ) -> ExecutionEngine:
        """Resolve ExecutionEngine orthogonally from model_strategy based on step engine_type."""
        _ = prompt_blocks
        return build_execution_engine(step_def.engine_type, self.deps.prompt_compiler)

    async def execute(
        self,
        step: StepRule,
        execution_id: str,
        workflow_id: str,
        metadata: ExecutionMetadata,
        projector: StateProjector,
        expected_inputs: list[Any] | None = None,
        frozen_ctx: FrozenContext | None = None,
        trace: list[TraceEvent] | None = None,
        strictness_level: int = StrictnessAnchor.STANDARD.value,
        lexical_strictness_level: int = StrictnessAnchor.STANDARD.value,
        arq_pool: Any | None = None,
        context_variables: ContextVariablesDTO | None = None,
        progress_callback: Callable[[int, int], Awaitable[None]] | None = None,
        step_def: Step | None = None,
        global_context_vars: GlobalContextVarsDTO | None = None,
        target_locale: str = "en",
        output_profile_id: str | None = None,
        organization_id: str | None = None,
    ) -> list[TraceEvent]:
        """Execute a pipeline node strategy with static parameters and OpenTelemetry span wrapping.

        Raises:
            AppException: Triggered with CONFIGURATION_ERROR if node configuration or blueprint is missing.
        """
        tracer = get_tracer(__name__)
        current_span = otel_trace.get_current_span()
        span_cm = (
            contextlib.nullcontext(current_span)
            if current_span.is_recording()
            else tracer.start_as_current_span(f"dag.node.{step.id}")
        )
        with span_cm as node_span:
            node_span.set_attribute("node.id", step.id)
            if step.task_blueprint is not None:
                node_span.set_attribute("node.blueprint", step.task_blueprint)
            node_span.set_attribute("node.depends_on", list(step.depends_on))
            try:
                blueprint_id = step.task_blueprint
                if not blueprint_id:
                    msg = f"Step {step.id} has no task_blueprint configured."
                    logger.error("[NodeExecutor] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                    raise AppException(
                        message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR}
                    )

                if not step_def:
                    step_def_data = await self.deps.workflow_repo.get_step_by_id(blueprint_id)
                    if not step_def_data:
                        msg = f"Step definition not found: {blueprint_id}"
                        logger.error("[NodeExecutor] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                        raise AppException(
                            message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR}
                        )
                    step_def = _hydrate_step_definition(step_def_data)

                if "apply_scoring_logic_hook" in step_def.post_hooks or "apply_scoring_logic" in step_def.post_hooks:
                    has_step_matrices = bool(step_def.criteria_block_ids)
                    has_eval_matrices = bool(global_context_vars and global_context_vars.evaluative_matrices)
                    if not has_step_matrices and not has_eval_matrices:
                        filtered_posts = [
                            h
                            for h in step_def.post_hooks
                            if h not in ("apply_scoring_logic_hook", "apply_scoring_logic")
                        ]
                        step_def = step_def.model_copy(update={"post_hooks": filtered_posts})

                normalized_mappings = {
                    logical_name: ContextRouter.normalize_and_validate_variable(path, projector.snapshot)
                    for logical_name, path in step.input_mappings.items()
                }
                step = step.model_copy(update={"input_mappings": normalized_mappings})

                optional_blocks = (
                    step_def.role_block_id,
                    step_def.extraction_protocol_block_id,
                    step_def.execution_persona_block_id,
                )
                criteria_ids: list[str] = [*step_def.criteria_block_ids, *(b for b in optional_blocks if b)]
                loaded_prompt_blocks = await self.deps.prompt_block_repo.get_prompt_blocks_by_ids(
                    criteria_ids, strict=True
                )

                engine: ExecutionEngine | None = None
                if step_def.type in (StepType.LLM, StepType.CAUSAL_DISCOVERY):
                    engine = self._resolve_execution_engine(step_def, loaded_prompt_blocks)

                effective_deps = (
                    dataclasses.replace(self.deps, arq_pool=arq_pool) if arq_pool is not None else self.deps
                )
                strategy_factory: type[NodeStrategyFactory] = (
                    sys.modules[_DAG_EXECUTOR_MODULE].NodeStrategyFactory
                    if _DAG_EXECUTOR_MODULE in sys.modules
                    else NodeStrategyFactory
                )
                strategy_impl = strategy_factory.create_strategy(
                    step_type=step_def.type, deps=effective_deps, engine=engine
                )

                resolved_global_vars = (
                    global_context_vars
                    if isinstance(global_context_vars, GlobalContextVarsDTO)
                    else GlobalContextVarsDTO()
                )
                if (
                    isinstance(metadata, ExecutionMetadata)
                    and isinstance(metadata.global_context_vars, GlobalContextVarsDTO)
                    and not resolved_global_vars.model_dump(exclude_defaults=True)
                ):
                    resolved_global_vars = metadata.global_context_vars

                resolved_model_registry_id = (
                    None if not isinstance(metadata, ExecutionMetadata) else metadata.model_registry_id
                )
                resolved_context_vars = (
                    context_variables if isinstance(context_variables, ContextVariablesDTO) else ContextVariablesDTO()
                )
                resolved_cognitive_tier = (
                    step_def.cognitive_tier if step_def.cognitive_tier is not None else CognitiveTier.FAST
                )

                context = StrategyContext(
                    execution_id=execution_id,
                    workflow_id=workflow_id,
                    target_locale=target_locale,
                    output_profile_id=output_profile_id,
                    metadata=metadata,
                    expected_inputs=expected_inputs,
                    cognitive_tier=resolved_cognitive_tier,
                    strictness_level=strictness_level,
                    lexical_strictness_level=lexical_strictness_level,
                    global_context_vars=resolved_global_vars,
                    context_variables=resolved_context_vars,
                    prompt_blocks=loaded_prompt_blocks,
                    model_registry_id=resolved_model_registry_id,
                )

                await strategy_impl.assert_quota(org_id=organization_id)
                return await strategy_impl.execute(
                    step=step,
                    projector=projector,
                    context=context,
                    frozen_ctx=frozen_ctx,
                    trace=trace,
                    progress_callback=progress_callback,
                )

            except AppException as ae:
                node_span.record_exception(ae)
                node_span.set_status(otel_trace.StatusCode.ERROR, str(ae))
                logger.error("[NodeExecutor] Fail-Fast Exception for step %s: %s", step.id, str(ae), exc_info=True)
                raise
            except (ValidationError, RuntimeError, ValueError, TypeError, KeyError, OSError, TimeoutError) as e:
                node_span.record_exception(e)
                node_span.set_status(otel_trace.StatusCode.ERROR, str(e))
                return self._dlq_record_node_error(step.id, e)
            except Exception as e:
                node_span.record_exception(e)
                node_span.set_status(otel_trace.StatusCode.ERROR, str(e))
                raise
