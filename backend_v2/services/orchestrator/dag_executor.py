"""Asynchronous Directed Acyclic Graph (DAG) Executor for V3 Workflows.

Strictly follows Event Sourcing, Fail-Fast principles (RFC 7807) and O(1) Concurrency.
God object refactored into: DAGOrchestrator, NodeExecutor, ExecutionCommitter.
"""

import asyncio
import dataclasses
import logging
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from pydantic import BaseModel, ValidationError
from tenacity import AsyncRetrying, before_sleep_log, retry_if_exception, stop_after_attempt, wait_exponential

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDeltaDTO,
    HookDependencies,
    HookState,
    hook_registry,
)
from backend_v2.database.interfaces import (
    IAuditRepository,
    IComponentRepository,
    IExecutionRepository,
    IIdentityRepository,
    IOutputProfileRepository,
    IPromptBlockRepository,
    ISystemRepository,
    IWorkflowRepository,
)
from backend_v2.exceptions import AppException, ErrorCodes, WorkflowExecutionError
from backend_v2.llm.provider import _is_transient_llm_error
from backend_v2.models.domain.prompt_blocks import PromptBlock
from backend_v2.models.dtos.trace import ExecutionUpdateDTO
from backend_v2.models.enums import ScoringStrategy, StepType, StrictnessAnchor
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import ErrorTraceEvent, StateProjector, TraceEvent
from backend_v2.models.v2_core import (
    ExecutionRecord,
    ExecutionStatus,
    ExecutionStepState,
    FrozenContext,
    I18nText,
    MCPAuditTrace,
    Step,
    StepRule,
    Workflow,
    WorkflowInputs,
)
from backend_v2.services.execution import create_execution_record
from backend_v2.services.localization import set_language
from backend_v2.services.orchestrator.context_router import ContextRouter
from backend_v2.services.orchestrator.dag_compiler import DAGCompilerService
from backend_v2.services.orchestrator.engines.base import ExecutionEngine
from backend_v2.services.orchestrator.matrix_reducer import MatrixReducer
from backend_v2.services.orchestrator.rag_preflight_service import RAGPreflightService
from backend_v2.services.orchestrator.strategies.base import StrategyContext, StrategyDependencies
from backend_v2.services.orchestrator.strategies.registry import NodeStrategyFactory
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

__all__ = ["DAGExecutor", "ExecutionCommitter", "NodeExecutor"]


class ExecutionCommitter:
    """Handles Checkpointing of the Event Sourced Trace conforming to Phase 9 directives."""

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
        frozen_context: Any | None = None,
        context_variables: dict[str, Any] | None = None,
    ) -> None:
        """Flushes the event array to persistent DB safely.

        Args:
            trace: Current sequence of workflow events.
            status: Target execution status boundary.
            step_states: Execution state dictionary mapping per-step states.
            error: Optional execution failure message to record.
            frozen_context: Serialized snapshot state if provided.
            context_variables: Execution level global variables.

        Raises:
            AppException: Triggered with PROGRESS_UPDATE_FAILED if db commit transaction fails.
        """
        try:
            update_dto = ExecutionUpdateDTO(
                status=status,
                execution_trace=trace,
                step_states=step_states,
                frozen_context=frozen_context,
                context_variables=context_variables,
                error=error,
            )
            await self.exec_repo.update_execution(self.execution_id, update_dto)
        except Exception as e:
            msg = f"Failed to commit execution trace for {self.execution_id}"
            logger.error("[ExecutionCommitter] %s: %s", ErrorCodes.PROGRESS_UPDATE_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                details={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED},
                status_code=500,
            ) from e


class NodeExecutor:
    """Executes a single step in pure isolation, emitting TraceEvents."""

    def __init__(
        self,
        deps: StrategyDependencies,
    ) -> None:
        """Initialize NodeExecutor with typed StrategyDependencies container.

        Args:
            deps: Immutable container holding repositories, compiler, and pools.
        """
        self.deps = deps

    def _resolve_execution_engine(self, step_def: Step, prompt_blocks: list[PromptBlock]) -> ExecutionEngine:
        """Resolve ExecutionEngine orthogonally from model_strategy based on step prompt blocks."""
        from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock
        from backend_v2.models.enums import PromptBlockCategory
        from backend_v2.services.llm_task_executor import LLMTaskExecutor
        from backend_v2.services.orchestrator.engines.prompt_engine import PromptEngine
        from backend_v2.services.orchestrator.engines.synthesis_engine import SynthesisEngine
        from backend_v2.services.orchestrator.engines.tda_engine import TDAEngine

        criteria_blocks = [b for b in prompt_blocks if b.id in step_def.criteria_block_ids]

        if any(
            b.category_id == PromptBlockCategory.MATRIX or isinstance(b, MatrixPromptBlock) for b in criteria_blocks
        ):
            return TDAEngine(self.deps.prompt_compiler)

        if step_def.model_strategy == "synthesis":
            return SynthesisEngine(LLMTaskExecutor(self.deps.prompt_compiler))

        return PromptEngine(LLMTaskExecutor(self.deps.prompt_compiler))

    async def execute(
        self,
        step: StepRule,
        execution_id: str,
        workflow_id: str,
        metadata: ExecutionMetadata,
        projector: StateProjector,
        semaphore: asyncio.Semaphore,
        expected_inputs: list[Any] | None = None,
        frozen_ctx: FrozenContext | None = None,
        trace: list[TraceEvent] | None = None,
        strictness_level: int = StrictnessAnchor.STANDARD.value,
        arq_pool: Any | None = None,
        running_event: asyncio.Event | None = None,
        context_variables: dict[str, Any] | None = None,
        progress_callback: Callable[[int, int], Awaitable[None]] | None = None,
        step_def: Step | None = None,
        global_context_vars: dict[str, Any] | None = None,
    ) -> list[TraceEvent]:
        """Executes a pipeline node strategy with static parameters.

        Args:
            step: Step parameters and routing context constraints mappings.
            execution_id: Execution identifier path.
            workflow_id: Primary database record workflow key.
            metadata: Operational contexts such as organization identity maps.
            projector: Transient state snapshot delta computer context.
            semaphore: Concurrency barrier constraints control instance.
            expected_inputs: Type list schema limits.
            frozen_ctx: Snapshot of historical context fields.
            trace: Dynamic execution historical collection tracker.
            strictness_level: Tolerance boundary configuration limits.
            arq_pool: Worker delegation dispatcher parameters.
            running_event: Coordinator signal emitter.
            context_variables: Execution level global variables.
            progress_callback: Optional progress reporter callback function.
            step_def: Optional pre-loaded Step blueprint.
            global_context_vars: Optional global context variables.

        Returns:
            List of events generated during step evaluation.

        Raises:
            AppException: Triggered with CONFIGURATION_ERROR if step metadata or target templates are absent.
        """
        try:
            blueprint_id = step.task_blueprint
            if not blueprint_id:
                msg = f"Step {step.id} has no task_blueprint configured."
                logger.error("[NodeExecutor] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
                )

            if not step_def:
                step_def_data = await self.deps.workflow_repo.get_step_by_id(blueprint_id)
                if not step_def_data:
                    msg = f"Configuration error: Step '{blueprint_id}' not found."
                    logger.error("[NodeExecutor] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
                    )
                step_def = Step.model_validate(step_def_data)

            normalized_mappings = {}
            for logical_name, path in step.input_mappings.items():
                normalized_path = ContextRouter.normalize_and_validate_variable(path, {"steps": projector.snapshot})
                normalized_mappings[logical_name] = normalized_path

            step = step.model_copy(update={"input_mappings": normalized_mappings})

            criteria_ids: list[str] = list(step_def.criteria_block_ids)
            if step_def.role_block_id:
                criteria_ids.append(step_def.role_block_id)
            if step_def.extraction_protocol_block_id:
                criteria_ids.append(step_def.extraction_protocol_block_id)
            if step_def.execution_persona_block_id:
                criteria_ids.append(step_def.execution_persona_block_id)

            loaded_prompt_blocks = await self.deps.prompt_block_repo.get_prompt_blocks_by_ids(criteria_ids, strict=True)

            engine = (
                self._resolve_execution_engine(step_def, loaded_prompt_blocks)
                if step_def.type == StepType.LLM
                else None
            )

            effective_deps = dataclasses.replace(self.deps, arq_pool=arq_pool) if arq_pool else self.deps
            strategy_impl = NodeStrategyFactory.create_strategy(
                step_type=step_def.type,
                deps=effective_deps,
                engine=engine,
            )

            if global_context_vars is not None:
                resolved_global_vars = global_context_vars
            elif isinstance(metadata, ExecutionMetadata):
                resolved_global_vars = (
                    metadata.global_context_vars
                    if metadata.global_context_vars is not None
                    else {"language": metadata.target_locale}
                )
            elif not isinstance(metadata, (str, int, float, bool, list)) and metadata is not None:
                try:
                    resolved_global_vars = (
                        metadata["global_context_vars"]
                        if "global_context_vars" in metadata and metadata["global_context_vars"] is not None
                        else {"language": metadata["target_locale"] if "target_locale" in metadata else None}
                    )
                except KeyError, TypeError:
                    resolved_global_vars = {}
            else:
                resolved_global_vars = {}

            org_id = (
                metadata.organization_id
                if isinstance(metadata, ExecutionMetadata)
                else (
                    metadata["organization_id"]
                    if not isinstance(metadata, (str, int, float, bool, list))
                    and metadata is not None
                    and "organization_id" in metadata
                    else None
                )
            )

            context = StrategyContext(
                execution_id=execution_id,
                workflow_id=workflow_id,
                metadata=metadata,
                expected_inputs=expected_inputs,
                model_strategy=step_def.model_strategy,
                strictness_level=strictness_level,
                global_context_vars=resolved_global_vars,
                context_variables=context_variables or {},
                prompt_blocks=loaded_prompt_blocks,
            )

            await strategy_impl.assert_quota(org_id=org_id)

            return await strategy_impl.execute(
                step=step,
                projector=projector,
                context=context,
                frozen_ctx=frozen_ctx,
                trace=trace,
                semaphore=semaphore,
                running_event=running_event,
                progress_callback=progress_callback,
            )

        except AppException as ae:
            logger.error("[NodeExecutor] Fail-Fast Exception for step %s: %s", step.id, str(ae), exc_info=True)
            raise
        except (ValidationError, RuntimeError, ValueError, TypeError, KeyError, OSError, TimeoutError) as e:
            logger.error("[NodeExecutor] Dual-Reporting Exception for step %s: %s", step.id, str(e), exc_info=True)
            return [
                ErrorTraceEvent(
                    step_name=step.id, error_code="STEP_FAILED", error_message=str(e), content={"traceback": str(e)}
                )
            ]


class DAGExecutor:
    """The central DAGOrchestrator architecture block."""

    def __init__(
        self,
        exec_repo: IExecutionRepository,
        workflow_repo: IWorkflowRepository,
        comp_repo: IComponentRepository,
        prompt_block_repo: IPromptBlockRepository,
        output_profile_repo: IOutputProfileRepository,
        identity_repo: IIdentityRepository,
        audit_repo: IAuditRepository,
        system_repo: ISystemRepository,
        prompt_compiler: Any,
        rag_preflight: RAGPreflightService,
    ) -> None:
        """Initialize the main DAG orchestration manager.

        Args:
            exec_repo: Primary database context for tracking runs.
            workflow_repo: Access parameters for templates definitions.
            comp_repo: UI configurations parameters.
            prompt_block_repo: Prompt block repository instance.
            output_profile_repo: Output profile repository instance.
            identity_repo: Access keys boundary metadata mappings.
            audit_repo: Compliance parameters interface.
            system_repo: Orchestrator environment constants limits.
            prompt_compiler: Standard evaluation environment for templates compilers.
            rag_preflight: RAG preflight service instance.
        """
        self.exec_repo = exec_repo
        self.workflow_repo = workflow_repo
        self.comp_repo = comp_repo
        self.prompt_block_repo = prompt_block_repo
        self.output_profile_repo = output_profile_repo
        self.identity_repo = identity_repo
        self.audit_repo = audit_repo
        self.system_repo = system_repo
        self.compiler = prompt_compiler
        self.rag_preflight = rag_preflight
        self.committer = ExecutionCommitter(exec_repo, "")
        self.deps = StrategyDependencies(
            exec_repo=exec_repo,
            workflow_repo=workflow_repo,
            comp_repo=comp_repo,
            prompt_block_repo=prompt_block_repo,
            output_profile_repo=output_profile_repo,
            identity_repo=identity_repo,
            audit_repo=audit_repo,
            system_repo=system_repo,
            prompt_compiler=self.compiler,
        )
        self.node_executor = NodeExecutor(deps=self.deps)

    async def execute_workflow(
        self,
        execution_id: str,
        workflow: Workflow,
        raw_inputs: WorkflowInputs,
        strictness_level: int | None = None,
        scoring_strategy: ScoringStrategy = ScoringStrategy.WATERFALL,
        arq_pool: Any | None = None,
    ) -> ExecutionRecord:
        """Main entrypoint for Workflow Execution.

        Args:
            execution_id: Unique record ID.
            workflow: Loaded configuration parameters.
            raw_inputs: Unprocessed raw input structures.
            strictness_level: User-override context threshold limits.
            scoring_strategy: Mathematical aggregation model selection.
            arq_pool: Target task queue backend integration.

        Returns:
            The finalized ExecutionRecord domain mapping.

        Raises:
            AppException: Triggered with VALIDATION_FAILED or WORKFLOW_EXECUTION_FAILED during step evaluations.
            WorkflowExecutionError: Instantiated inside execution branches if a step fails to complete gracefully.
        """
        DAGCompilerService.validate_workflow(workflow)

        self.committer.execution_id = execution_id

        # 1. Pre-fetch and validate all Step definitions upfront (Fail-Fast & N+1 fix)
        blueprint_ids = {s.task_blueprint for s in workflow.steps if s.task_blueprint}
        step_definitions: dict[str, Step] = {}

        async def _fetch_and_validate(b_id: str) -> tuple[str, Step]:
            data = await self.workflow_repo.get_step_by_id(b_id)
            if not data:
                msg = f"Configuration error: Step '{b_id}' not found."
                logger.error("[DAGExecutor] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
                )
            return b_id, Step.model_validate(data)

        if blueprint_ids:
            async with asyncio.TaskGroup() as tg:
                tasks = [tg.create_task(_fetch_and_validate(b_id)) for b_id in blueprint_ids]
            results = [t.result() for t in tasks]
            step_definitions = dict(results)

        if strictness_level is None:
            strictness_level = workflow.default_strictness_level

        raw_rec = await self.exec_repo.get_execution(execution_id)
        existing_record: ExecutionRecord | None = (
            raw_rec
            if isinstance(raw_rec, ExecutionRecord)
            else (ExecutionRecord.model_validate(raw_rec, strict=False) if raw_rec is not None else None)
        )

        target_loc = (
            existing_record.target_locale
            if existing_record and existing_record.target_locale
            else (raw_inputs.language if raw_inputs and raw_inputs.language else "en")
        )

        step_states = {}
        for step in workflow.steps:
            step_def = step_definitions.get(step.task_blueprint) if step.task_blueprint else None
            if step_def and isinstance(step_def.name, I18nText):
                step_label = step_def.name.resolve(target_loc)
            elif step_def and isinstance(step_def.name, str) and step_def.name.strip():
                step_label = step_def.name
            else:
                step_label = step.id
            step_states[step.id] = ExecutionStepState(
                id=step.id,
                label=step_label,
                status=ExecutionStatus.PENDING,
            )

        if existing_record:
            exec_record = existing_record.model_copy(update={"status": ExecutionStatus.RUNNING})
            if not exec_record.step_states:
                exec_record = exec_record.model_copy(update={"step_states": step_states})
            else:
                updated_states = {}
                for s_id, s_state in exec_record.step_states.items():
                    if s_id in step_states and (s_state.label == s_id or not s_state.label):
                        updated_states[s_id] = s_state.model_copy(update={"label": step_states[s_id].label})
                    else:
                        updated_states[s_id] = s_state
                exec_record = exec_record.model_copy(update={"step_states": updated_states})

            v_step_id = f"sys_render_{exec_record.output_profile_id}"
            if v_step_id not in exec_record.step_states:
                new_states = dict(exec_record.step_states)
                new_states[v_step_id] = ExecutionStepState(
                    id=v_step_id, label="system.virtual.rendering", status=ExecutionStatus.PENDING
                )
                exec_record = exec_record.model_copy(update={"step_states": new_states})
        else:
            exec_record = create_execution_record(
                execution_id=execution_id,
                workflow_id=workflow.id,
                raw_inputs=raw_inputs,
                frozen_context=FrozenContext(),
                source_identity_manifest={},
                status=ExecutionStatus.RUNNING,
                step_states=step_states,
                output_profile_id=workflow.default_profile_id,
            )
            v_step_id = f"sys_render_{workflow.default_profile_id}"
            if v_step_id not in exec_record.step_states:
                new_states = dict(exec_record.step_states)
                new_states[v_step_id] = ExecutionStepState(
                    id=v_step_id, label="system.virtual.rendering", status=ExecutionStatus.PENDING
                )
                exec_record = exec_record.model_copy(update={"step_states": new_states})

        if exec_record.target_locale:
            set_language(exec_record.target_locale)

        global_vars: dict[str, Any] = {}
        user_id = exec_record.metadata.user_id or exec_record.raw_inputs.user_id
        if user_id:
            user_data = await self.identity_repo.get_user(user_id)
            if user_data:
                user_lang = (
                    user_data.language
                    if isinstance(user_data, BaseModel)
                    else (
                        user_data.get("language")
                        if not isinstance(user_data, (str, int, float, bool, list)) and user_data is not None
                        else None
                    )
                )
                if user_lang:
                    global_vars["language"] = user_lang

        if "language" not in global_vars and exec_record.raw_inputs.language:
            global_vars["language"] = exec_record.raw_inputs.language

        if "language" not in global_vars and exec_record.target_locale:
            global_vars["language"] = exec_record.target_locale

        projector = StateProjector()
        for evt in exec_record.execution_trace:
            projector.apply_delta(evt)

        if not exec_record.execution_trace:
            inputs_dict = exec_record.raw_inputs.model_dump(mode="json")
            input_event = TraceEvent(step_name="raw_inputs", event_type="input", content=inputs_dict)
            exec_record.execution_trace.append(input_event)
            projector.apply_delta(input_event)

            try:
                global_hook_deps = HookDependencies(
                    exec_repo=self.exec_repo,
                    workflow_repo=self.workflow_repo,
                    comp_repo=self.comp_repo,
                    prompt_block_repo=self.prompt_block_repo,
                    output_profile_repo=self.output_profile_repo,
                    identity_repo=self.identity_repo,
                    audit_repo=self.audit_repo,
                    system_repo=self.system_repo,
                )
                global_hook_state = HookState(
                    execution_id=execution_id,
                    workflow_id=workflow.id,
                    metadata=exec_record.metadata,
                    global_context_vars=GlobalContextVarsDTO(vars=global_vars),
                    inputs=ExecutionInputsDTO(
                        raw_inputs=inputs_dict, dynamic_inputs=exec_record.raw_inputs.dynamic_inputs
                    ),
                )
                processed_result = await hook_registry.execute("input_processing", global_hook_state, global_hook_deps)
                if processed_result.success and processed_result.state_delta:
                    delta_content = (
                        processed_result.state_delta.delta
                        if isinstance(processed_result.state_delta, HookDeltaDTO)
                        else (
                            dict(processed_result.state_delta)
                            if not isinstance(processed_result.state_delta, (str, int, float, bool, list))
                            and processed_result.state_delta is not None
                            else {}
                        )
                    )
                    proc_event = TraceEvent(step_name="inputs", event_type="input", content=delta_content)
                    exec_record.execution_trace.append(proc_event)
                    projector.apply_delta(proc_event)
            except Exception as e:
                msg = f"Pre-Hydration failed: {e}"
                logger.error(msg, exc_info=True)
                raise AppException(
                    message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED}, status_code=400
                ) from e

        steps_by_id = {step.id: step for step in workflow.steps}
        step_events: dict[str, asyncio.Event] = {step.id: asyncio.Event() for step in workflow.steps}

        try:
            import litellm.exceptions as _litellm_exc

            step_exceptions: tuple[type[BaseException], ...] = (
                AppException,
                ValidationError,
                RuntimeError,
                ValueError,
                TypeError,
                KeyError,
                OSError,
                TimeoutError,
                ConnectionError,
                ExceptionGroup,
                _litellm_exc.APIConnectionError,
                _litellm_exc.APIError,
                _litellm_exc.RateLimitError,
                _litellm_exc.Timeout,
                _litellm_exc.ServiceUnavailableError,
                _litellm_exc.InternalServerError,
                _litellm_exc.BadGatewayError,
                _litellm_exc.AuthenticationError,
                _litellm_exc.PermissionDeniedError,
                _litellm_exc.NotFoundError,
                _litellm_exc.UnprocessableEntityError,
                _litellm_exc.ContextWindowExceededError,
                _litellm_exc.ContentPolicyViolationError,
            )
        except ImportError:
            step_exceptions = (
                AppException,
                ValidationError,
                RuntimeError,
                ValueError,
                TypeError,
                KeyError,
                OSError,
                TimeoutError,
                ConnectionError,
                ExceptionGroup,
            )

        failed_previous_steps = []
        for step_id, s_state in exec_record.step_states.items():
            if s_state.status == ExecutionStatus.PASSED:
                step_events[step_id].set()
            elif s_state.status == ExecutionStatus.FAILED:
                failed_previous_steps.append(step_id)
                new_state = exec_record.step_states[step_id].model_copy(update={"status": ExecutionStatus.PENDING})
                new_states = {**exec_record.step_states, step_id: new_state}
                exec_record = exec_record.model_copy(update={"step_states": new_states})

        semaphore = asyncio.Semaphore(get_settings().max_concurrent_llm_steps)
        _update_lock = asyncio.Lock()
        _commit_lock = asyncio.Lock()

        async def _safe_commit(
            status_override: ExecutionStatus | None = None, error_override: str | None = None
        ) -> None:
            async with _commit_lock:
                current = exec_record
                await self.committer.commit_trace(
                    trace=current.execution_trace,
                    status=status_override if status_override is not None else current.status,
                    step_states=current.step_states,
                    error=error_override if error_override is not None else current.error,
                    frozen_context=current.frozen_context,
                    context_variables=current.context_variables,
                )

        async def run_step_wrapper(step_id: str) -> None:
            nonlocal exec_record
            step_obj = steps_by_id[step_id]

            if exec_record.step_states[step_id].status == ExecutionStatus.PASSED:
                return

            try:
                for dep in step_obj.depends_on:
                    await step_events[dep].wait()
                    if exec_record.step_states[dep].status == ExecutionStatus.FAILED:
                        async with _update_lock:
                            new_state = exec_record.step_states[step_id].model_copy(
                                update={"status": ExecutionStatus.FAILED}
                            )
                            new_states = {**exec_record.step_states, step_id: new_state}
                            exec_record = exec_record.model_copy(update={"step_states": new_states})
                        await _safe_commit()
                        logger.warning(
                            "[DAGExecutor] Cascading failure: Step %s failed because dependency %s failed.",
                            step_id,
                            dep,
                        )
                        return

                # --- Epic 93 Phase 3: Pre-Synthesis Matrix Reducer Lifecycle Event ---
                step_def = step_definitions.get(step_obj.task_blueprint) if step_obj.task_blueprint else None
                if step_def and step_def.model_strategy == "synthesis":
                    try:
                        lightweight_matrix = MatrixReducer.reduce_matrix(exec_record)

                        reduce_event = TraceEvent(
                            step_name="matrix_reducer", event_type="output", content=lightweight_matrix.model_dump()
                        )

                        async with _update_lock:
                            exec_record.execution_trace.append(reduce_event)
                            projector.apply_delta(reduce_event)

                            new_cv = dict(exec_record.context_variables)
                            new_cv["__MATRIX_REDUCER_OUTPUT__"] = lightweight_matrix.model_dump()
                            exec_record = exec_record.model_copy(update={"context_variables": new_cv})
                        logger.info("[DAGExecutor] Successfully applied MatrixReducer pre-synthesis.")
                    except Exception as e:
                        logger.error(
                            "[DAGExecutor] Failed to project and reduce matrix pre-synthesis: %s", e, exc_info=True
                        )
                        raise WorkflowExecutionError(
                            step_id=step_id, task_key=step_obj.task_blueprint, original_error=e
                        ) from e

                async with _update_lock:
                    new_state = exec_record.step_states[step_id].model_copy(update={"status": ExecutionStatus.QUEUED})
                    new_states = {**exec_record.step_states, step_id: new_state}
                    exec_record = exec_record.model_copy(update={"step_states": new_states})

                await _safe_commit()

                running_event = asyncio.Event()

                async def watch_running() -> None:
                    nonlocal exec_record
                    await running_event.wait()
                    needs_commit = False
                    async with _update_lock:
                        if exec_record.step_states[step_id].status == ExecutionStatus.QUEUED:
                            new_state = exec_record.step_states[step_id].model_copy(
                                update={"status": ExecutionStatus.RUNNING}
                            )
                            new_states = {**exec_record.step_states, step_id: new_state}
                            exec_record = exec_record.model_copy(update={"step_states": new_states})
                            needs_commit = True

                    if needs_commit:
                        await _safe_commit()

                watcher_task = asyncio.create_task(watch_running())

                async def progress_callback(completed: int, total: int) -> None:
                    nonlocal exec_record

                    if total == 100:
                        prog = completed
                        label = f"Processing... {prog}%"
                    else:
                        prog = int((completed / total) * 100) if total > 0 else 0
                        label = f"Evaluating batch {completed}/{total}..."

                    async with _update_lock:
                        new_state = exec_record.step_states[step_id].model_copy(update={"label": label})
                        new_states = {**exec_record.step_states, step_id: new_state}
                        exec_record = exec_record.model_copy(
                            update={"step_states": new_states, "progress": prog, "status_message": label}
                        )
                    await _safe_commit()
                    logger.info("Progress updated for step %s: %s", step_id, label)

                try:
                    settings = get_settings()
                    async for attempt in AsyncRetrying(
                        stop=stop_after_attempt(settings.llm_max_transient_retries),
                        wait=wait_exponential(
                            multiplier=settings.llm_retry_multiplier,
                            min=settings.llm_retry_min_seconds,
                            max=settings.llm_retry_max_seconds,
                        ),
                        retry=retry_if_exception(_is_transient_llm_error),
                        reraise=True,
                        before_sleep=before_sleep_log(logger, logging.WARNING),
                    ):
                        with attempt:
                            events = await self.node_executor.execute(
                                step=step_obj,
                                execution_id=execution_id,
                                workflow_id=workflow.id,
                                metadata=exec_record.metadata,
                                projector=projector,
                                expected_inputs=workflow.expected_inputs,
                                frozen_ctx=exec_record.frozen_context,
                                trace=exec_record.execution_trace,
                                strictness_level=strictness_level,
                                semaphore=semaphore,
                                running_event=running_event,
                                context_variables=exec_record.context_variables,
                                progress_callback=progress_callback,
                                step_def=step_definitions.get(step_obj.task_blueprint)
                                if step_obj.task_blueprint
                                else None,
                                global_context_vars=global_vars,
                            )
                finally:
                    watcher_task.cancel()

                has_error_evt = any(isinstance(evt, ErrorTraceEvent) for evt in events)
                async with _update_lock:
                    step_mcp_traces: list[MCPAuditTrace] = []
                    step_generated_schemas: dict[str, Any] = {}
                    new_cv = dict(exec_record.context_variables)
                    has_cv_updates = False
                    for evt in events:
                        exec_record.execution_trace.append(evt)
                        projector.apply_delta(evt)
                        if (
                            evt.event_type == "decision"
                            and evt.metadata
                            and "is_context_update" in evt.metadata
                            and evt.metadata["is_context_update"]
                        ):
                            new_cv.update(evt.content)
                            has_cv_updates = True
                        match evt:
                            case TraceEvent() if evt.mcp_audit_traces:
                                step_mcp_traces.extend(evt.mcp_audit_traces)
                            case TraceEvent() if (
                                evt.event_type == "decision"
                                and evt.metadata
                                and "mcp_audit_traces" in evt.metadata
                                and evt.metadata["mcp_audit_traces"]
                            ):
                                for raw in evt.metadata["mcp_audit_traces"]:
                                    try:
                                        trace = MCPAuditTrace.model_validate(raw)
                                        step_mcp_traces.append(trace)
                                    except Exception as e:
                                        logger.error(
                                            "[DAGExecutor] %s: Invalid MCPAuditTrace payload in decision event: %s",
                                            ErrorCodes.VALIDATION_FAILED.name,
                                            e,
                                            exc_info=True,
                                        )
                                        raise AppException(
                                            message=f"Invalid MCPAuditTrace in pre-hook decision event: {e}",
                                            status_code=500,
                                            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                                        ) from e
                            case TraceEvent() if evt.metadata and "generated_schema" in evt.metadata:
                                step_generated_schemas[evt.step_name] = evt.metadata["generated_schema"]

                    updates: dict[str, Any] = {}
                    if has_cv_updates:
                        updates["context_variables"] = new_cv

                    fc_updates: dict[str, Any] = {}
                    base_fc = exec_record.frozen_context or FrozenContext()
                    if step_mcp_traces:
                        current_traces: list[MCPAuditTrace] = list(base_fc.mcp_tool_audit)
                        seen_ids: set[str] = {t.id for t in current_traces if t.id}
                        new_unique_traces: list[MCPAuditTrace] = []
                        for t in step_mcp_traces:
                            if t.id is None or t.id not in seen_ids:
                                new_unique_traces.append(t)
                                if t.id:
                                    seen_ids.add(t.id)
                        if new_unique_traces:
                            fc_updates["mcp_tool_audit"] = current_traces + new_unique_traces

                    if step_generated_schemas:
                        merged_schemas = {**base_fc.generated_schemas, **step_generated_schemas}
                        fc_updates["generated_schemas"] = merged_schemas

                    if fc_updates:
                        new_fc = base_fc.model_copy(update=fc_updates)
                        updates["frozen_context"] = new_fc

                    step_status = ExecutionStatus.FAILED if has_error_evt else ExecutionStatus.PASSED
                    new_state = exec_record.step_states[step_id].model_copy(update={"status": step_status})
                    updates["step_states"] = {**exec_record.step_states, step_id: new_state}

                    exec_record = exec_record.model_copy(update=updates)

                if has_error_evt:
                    err_msg = [evt.error_message for evt in events if isinstance(evt, ErrorTraceEvent)][0]
                    msg = f"Step {step_id} emitted ErrorTraceEvent: {err_msg}"
                    logger.error("[DAGExecutor] %s: %s", ErrorCodes.WORKFLOW_EXECUTION_FAILED.name, msg)
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED.value},
                    )

                await _safe_commit()

            except step_exceptions as e:
                err_code = "UNKNOWN_ERROR"
                if isinstance(e, AppException):
                    if isinstance(e.error_code, ErrorCodes):
                        err_code = e.error_code.name
                    elif (
                        not isinstance(e.details, (str, int, float, bool, list))
                        and e.details is not None
                        and "error_code" in e.details
                    ):
                        code_val = e.details["error_code"]
                        if isinstance(code_val, ErrorCodes):
                            err_code = code_val.name
                        elif isinstance(code_val, str):
                            err_code = code_val

                async with _update_lock:
                    new_state = exec_record.step_states[step_id].model_copy(update={"status": ExecutionStatus.FAILED})
                    new_states = {**exec_record.step_states, step_id: new_state}
                    error_evt = TraceEvent(
                        step_name=step_id,
                        event_type="error",
                        content={"error_code": err_code, "message": str(e)},
                    )
                    exec_record.execution_trace.append(error_evt)
                    projector.apply_delta(error_evt)
                    exec_record = exec_record.model_copy(update={"step_states": new_states})
                await _safe_commit(status_override=ExecutionStatus.FAILED, error_override=str(e))
                logger.error("[DAGExecutor] Step %s failed with error: %s", step_id, str(e), exc_info=True)
            finally:
                step_events[step_id].set()

        try:
            # Epic 101 Phase 1B: RAG Pre-Flight Pipeline Injection
            has_prehydrated = False
            preflight_target_step = None
            for step in workflow.steps:
                if step.task_blueprint and step.task_blueprint in step_definitions:
                    if step_definitions[step.task_blueprint].model_strategy == "synthesis":
                        has_prehydrated = True
                        preflight_target_step = step
                        break

            if has_prehydrated and preflight_target_step:
                virtual_step_id = f"stp_{uuid.uuid4().hex[:16]}"

                async with _update_lock:
                    new_state = ExecutionStepState(
                        id=virtual_step_id, label="system.rag.preflight", status=ExecutionStatus.RUNNING
                    )
                    new_states = {**exec_record.step_states, virtual_step_id: new_state}
                    exec_record = exec_record.model_copy(update={"step_states": new_states})

                await _safe_commit()

                async def _emit_preflight_progress(message: str, pct: int) -> None:
                    nonlocal exec_record
                    evt = TraceEvent(
                        step_name=virtual_step_id,
                        event_type="progress",
                        content={"message": message, "progress_pct": pct},
                    )
                    async with _update_lock:
                        exec_record.execution_trace.append(evt)
                        projector.apply_delta(evt)
                    await _safe_commit()

                try:
                    blackboard_payload = await self.rag_preflight.execute(
                        target_step=preflight_target_step,
                        step_def=step_definitions[preflight_target_step.task_blueprint],
                        exec_record=exec_record,
                        emit_progress=_emit_preflight_progress,
                    )

                    async with _update_lock:
                        pass_state = exec_record.step_states[virtual_step_id].model_copy(
                            update={"status": ExecutionStatus.PASSED}
                        )
                        new_states = {**exec_record.step_states, virtual_step_id: pass_state}
                        new_cv = dict(exec_record.context_variables)
                        new_cv["__GLOBAL_ATOM_BLACKBOARD__"] = blackboard_payload
                        exec_record = exec_record.model_copy(
                            update={"step_states": new_states, "context_variables": new_cv}
                        )
                    await _safe_commit()
                except Exception as e:
                    async with _update_lock:
                        fail_state = exec_record.step_states[virtual_step_id].model_copy(
                            update={"status": ExecutionStatus.FAILED}
                        )
                        new_states = {**exec_record.step_states, virtual_step_id: fail_state}
                        exec_record = exec_record.model_copy(update={"step_states": new_states})
                    await _safe_commit(status_override=ExecutionStatus.FAILED, error_override=str(e))
                    raise WorkflowExecutionError(
                        step_id=virtual_step_id, task_key="system.rag.preflight", original_error=e
                    ) from e

            async with asyncio.TaskGroup() as tg:
                for step in workflow.steps:
                    tg.create_task(run_step_wrapper(step.id))

            if any(state.status == ExecutionStatus.FAILED for state in exec_record.step_states.values()):
                exec_record = exec_record.model_copy(update={"status": ExecutionStatus.FAILED})
                await self.committer.commit_trace(
                    trace=exec_record.execution_trace,
                    status=exec_record.status,
                    step_states=exec_record.step_states,
                    context_variables=exec_record.context_variables,
                )
                msg = "Workflow completed with failed steps"
                logger.error("[DAGExecutor] %s: %s", ErrorCodes.WORKFLOW_EXECUTION_FAILED.name, msg)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED},
                )

            await self.committer.commit_trace(
                trace=exec_record.execution_trace,
                status=exec_record.status,
                step_states=exec_record.step_states,
                context_variables=exec_record.context_variables,
            )

            return exec_record

        except ExceptionGroup as eg:
            primary_err = eg.exceptions[0]

            new_states = dict(exec_record.step_states)
            for state_id, state in new_states.items():
                if state.status == ExecutionStatus.RUNNING:
                    new_states[state_id] = state.model_copy(update={"status": ExecutionStatus.FAILED})

            exec_record = exec_record.model_copy(
                update={"step_states": new_states, "status": ExecutionStatus.FAILED, "error": str(primary_err)}
            )

            await self.committer.commit_trace(
                trace=exec_record.execution_trace,
                status=exec_record.status,
                step_states=exec_record.step_states,
                error=exec_record.error,
                context_variables=exec_record.context_variables,
            )

            if isinstance(primary_err, AppException):
                raise primary_err from eg

            msg = f"Workflow failed: {primary_err}"
            logger.error("[DAGExecutor] %s: %s", ErrorCodes.WORKFLOW_EXECUTION_FAILED.name, msg)
            raise AppException(
                message=msg,
                details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED},
                status_code=500,
            ) from primary_err

        except Exception as unexpected_err:
            exec_record = exec_record.model_copy(
                update={"status": ExecutionStatus.FAILED, "error": str(unexpected_err)}
            )

            await self.committer.commit_trace(
                trace=exec_record.execution_trace,
                status=exec_record.status,
                step_states=exec_record.step_states,
                error=exec_record.error,
                context_variables=exec_record.context_variables,
            )

            if isinstance(unexpected_err, AppException):
                raise

            msg = f"Workflow failed: {unexpected_err}"
            logger.error("[DAGExecutor] %s: %s", ErrorCodes.WORKFLOW_EXECUTION_FAILED.name, msg)
            raise AppException(
                message=msg,
                details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED},
                status_code=500,
            ) from unexpected_err
