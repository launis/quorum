from backend_v2.settings import get_settings

"""Asynchronous Directed Acyclic Graph (DAG) Executor for V3 Workflows.

Strictly follows Event Sourcing, Fail-Fast principles (RFC 7807) and O(1) Concurrency.
God object refactored into: DAGOrchestrator, NodeExecutor, ExecutionCommitter.
"""

import asyncio
import logging
from typing import Any

from backend_v2.core.hook_registry import HookDependencies, HookState, hook_registry
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
from backend_v2.models.enums import ScoringStrategy, StrictnessAnchor
from backend_v2.models.state import ErrorTraceEvent, StateProjector, TraceEvent
from backend_v2.models.v2_core import (
    ExecutionRecord,
    ExecutionStatus,
    ExecutionStepState,
    FrozenContext,
    Step,
    StepRule,
    Workflow,
    WorkflowInputs,
)
from backend_v2.services.execution import create_execution_record
from backend_v2.services.orchestrator.context_router import ContextRouter
from backend_v2.services.orchestrator.dag_compiler import DAGCompilerService
from backend_v2.services.orchestrator.strategies.base import NodeStrategy, StrategyContext
from backend_v2.services.orchestrator.strategies.llm import LLMNodeStrategy
from backend_v2.services.orchestrator.strategies.logic import LogicNodeStrategy

logger = logging.getLogger(__name__)


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

        Raises:
            AppException: Triggered with PROGRESS_UPDATE_FAILED if db commit transaction fails.
        """
        try:
            payload: dict[str, Any] = {
                "status": status.value,
                "execution_trace": [e.model_dump(mode="json") for e in trace],
                "step_states": {k: v.model_dump(mode="json") for k, v in step_states.items()},
            }
            if frozen_context:
                payload["frozen_context"] = frozen_context.model_dump(mode="json")

            if context_variables is not None:
                payload["context_variables"] = context_variables

            if error:
                payload["error"] = error

            await self.exec_repo.update_execution(self.execution_id, payload)
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
        exec_repo: IExecutionRepository,
        workflow_repo: IWorkflowRepository,
        comp_repo: IComponentRepository,
        prompt_block_repo: IPromptBlockRepository,
        output_profile_repo: IOutputProfileRepository,
        identity_repo: IIdentityRepository,
        audit_repo: IAuditRepository,
        system_repo: ISystemRepository,
        prompt_compiler: Any,
    ) -> None:
        """Initialize NodeExecutor with required underlying storage abstractions.

        Args:
            exec_repo: Database access boundary for state checkpointing.
            workflow_repo: Source for static workflows configuration definitions.
            comp_repo: UI Hints / Component configurations repository reference.
            identity_repo: Authorization constraints database context.
            audit_repo: Global tamper-proof log repository integration mapping.
            system_repo: Configurations registry interface mapping.
            prompt_compiler: Compiler engine dynamic handler.
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

    async def execute(
        self,
        step: StepRule,
        execution_id: str,
        workflow_id: str,
        metadata: dict[str, Any],
        projector: StateProjector,
        semaphore: asyncio.Semaphore,
        expected_inputs: list[Any] | None = None,
        frozen_ctx: FrozenContext | None = None,
        trace: list[TraceEvent] | None = None,
        strictness_level: int = StrictnessAnchor.STANDARD.value,
        arq_pool: Any | None = None,
        running_event: asyncio.Event | None = None,
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

        Returns:
            List of events generated during step evaluation.

        Raises:
            AppException: Triggered with CONFIGURATION_ERROR if step metadata or target templates are absent.
        """
        try:
            blueprint_id = getattr(step, "task_blueprint", None)
            if not blueprint_id:
                msg = f"Step {step.id} has no task_blueprint configured."
                logger.error("[NodeExecutor] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
                )

            step_def_data = await self.workflow_repo.get_step_by_id(blueprint_id)
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

            context = StrategyContext(
                execution_id=execution_id,
                workflow_id=workflow_id,
                metadata=metadata,
                expected_inputs=expected_inputs,
                model_strategy=step_def.model_strategy,
                strictness_level=strictness_level,
                global_context_vars=metadata["global_context_vars"] if "global_context_vars" in metadata else {},
            )

            strategy_impl: NodeStrategy
            if step_def.type == "logic":
                strategy_impl = LogicNodeStrategy(
                    self.exec_repo,
                    self.workflow_repo,
                    self.comp_repo,
                    self.prompt_block_repo,
                    self.output_profile_repo,
                    self.identity_repo,
                    self.audit_repo,
                    self.system_repo,
                    self.compiler,
                    arq_pool=arq_pool,
                )
            else:
                strategy_impl = LLMNodeStrategy(
                    self.exec_repo,
                    self.workflow_repo,
                    self.comp_repo,
                    self.prompt_block_repo,
                    self.output_profile_repo,
                    self.identity_repo,
                    self.audit_repo,
                    self.system_repo,
                    self.compiler,
                    arq_pool=arq_pool,
                )

            org_id = metadata["organization_id"] if "organization_id" in metadata else None
            await strategy_impl.assert_quota(org_id=org_id)

            emitted_events = await strategy_impl.execute(
                step=step,
                projector=projector,
                context=context,
                frozen_ctx=frozen_ctx,
                trace=trace,
                semaphore=semaphore,
                running_event=running_event,
            )
            return emitted_events

        except AppException as ae:
            logger.error("[NodeExecutor] Fail-Fast Exception for step %s: %s", step.id, str(ae), exc_info=True)
            raise
        except Exception as e:
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
    ) -> None:
        """Initialize the main DAG orchestration manager.

        Args:
            exec_repo: Primary database context for tracking runs.
            workflow_repo: Access parameters for templates definitions.
            comp_repo: UI configurations parameters.
            identity_repo: Access keys boundary metadata mappings.
            audit_repo: Compliance parameters interface.
            system_repo: Orchestrator environment constants limits.
            prompt_compiler: Standard evaluation environment for templates compilers.
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
        self.committer = ExecutionCommitter(exec_repo, "")
        self.node_executor = NodeExecutor(
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

        if strictness_level is None:
            strictness_level = workflow.default_strictness_level

        existing_record_dict = await self.exec_repo.get_execution(execution_id)

        step_states = {
            step.id: ExecutionStepState(id=step.id, label=step.id, status=ExecutionStatus.PENDING)
            for step in workflow.steps
        }

        if existing_record_dict:
            exec_record = ExecutionRecord.model_validate(existing_record_dict)
            exec_record = exec_record.model_copy(update={"status": ExecutionStatus.RUNNING})
            if not getattr(exec_record, "step_states", None) or not exec_record.step_states:
                exec_record = exec_record.model_copy(update={"step_states": step_states})

            v_step_id = f"sys_render_{exec_record.output_profile_id or workflow.default_profile_id}"
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
            )
            v_step_id = f"sys_render_{workflow.default_profile_id}"
            if v_step_id not in exec_record.step_states:
                new_states = dict(exec_record.step_states)
                new_states[v_step_id] = ExecutionStepState(
                    id=v_step_id, label="system.virtual.rendering", status=ExecutionStatus.PENDING
                )
                exec_record = exec_record.model_copy(update={"step_states": new_states})

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
                global_vars: dict[str, Any] = {}
                user_id = (
                    exec_record.metadata["user_id"]
                    if "user_id" in exec_record.metadata
                    else exec_record.raw_inputs.user_id
                )
                if user_id:
                    user_data = await self.identity_repo.get_user(user_id)
                    if user_data and "language" in user_data:
                        global_vars["language"] = user_data["language"]

                if "language" not in global_vars and exec_record.raw_inputs.language:
                    global_vars["language"] = exec_record.raw_inputs.language

                exec_record.metadata["global_context_vars"] = global_vars

                global_hook_state = HookState(
                    execution_id=execution_id,
                    workflow_id=workflow.id,
                    metadata=exec_record.metadata,
                    global_context_vars=global_vars,
                    inputs=inputs_dict,
                )
                processed_result = await hook_registry.execute("input_processing", global_hook_state, global_hook_deps)
                if processed_result.success and isinstance(processed_result.state_delta, dict):
                    proc_event = TraceEvent(
                        step_name="inputs", event_type="input", content=processed_result.state_delta
                    )
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
                    error=error_override if error_override is not None else getattr(current, "error", None),
                    frozen_context=current.frozen_context,
                    context_variables=current.context_variables,
                )

        async def run_step_wrapper(step_id: str) -> None:
            nonlocal exec_record
            step_obj = steps_by_id[step_id]

            if exec_record.step_states[step_id].status == ExecutionStatus.PASSED:
                return

            for dep in step_obj.depends_on:
                await step_events[dep].wait()

            # --- Epic 93 Phase 3: Pre-Synthesis Matrix Reducer Lifecycle Event ---
            if step_obj.task_blueprint == "sp_7a8b9c0d1e2f3a4b":
                from backend_v2.services.orchestrator.matrix_reducer import MatrixReducer

                try:
                    lightweight_matrix = MatrixReducer.reduce_matrix(exec_record)

                    reduce_event = TraceEvent(
                        step_name="matrix_reducer", event_type="output", content=lightweight_matrix.model_dump()
                    )

                    async with _update_lock:
                        exec_record.execution_trace.append(reduce_event)
                        projector.apply_delta(reduce_event)
                    logger.info("[DAGExecutor] Successfully applied MatrixReducer pre-synthesis.")
                except Exception as e:
                    logger.error(
                        "[DAGExecutor] Failed to project and reduce matrix pre-synthesis: %s", e, exc_info=True
                    )
                    raise WorkflowExecutionError(
                        step_id=step_id, task_key=step_obj.task_blueprint, original_error=e
                    ) from e

            try:
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

                try:
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
                    )
                finally:
                    watcher_task.cancel()

                new_cv = dict(exec_record.context_variables)
                has_cv_updates = False
                for evt in events:
                    exec_record.execution_trace.append(evt)
                    projector.apply_delta(evt)
                    if evt.event_type == "decision" and evt.metadata and evt.metadata.get("is_context_update"):
                        new_cv.update(evt.content)
                        has_cv_updates = True

                if has_cv_updates:
                    async with _update_lock:
                        exec_record = exec_record.model_copy(update={"context_variables": new_cv})

                if any(isinstance(evt, ErrorTraceEvent) for evt in events):
                    async with _update_lock:
                        new_state = exec_record.step_states[step_id].model_copy(
                            update={"status": ExecutionStatus.FAILED}
                        )
                        new_states = {**exec_record.step_states, step_id: new_state}
                        exec_record = exec_record.model_copy(update={"step_states": new_states})
                    err_msg = [evt.error_message for evt in events if isinstance(evt, ErrorTraceEvent)][0]
                    msg = f"Step {step_id} emitted ErrorTraceEvent: {err_msg}"
                    logger.error("[DAGExecutor] %s: %s", ErrorCodes.WORKFLOW_EXECUTION_FAILED.name, msg)
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED},
                    )

                async with _update_lock:
                    new_state = exec_record.step_states[step_id].model_copy(update={"status": ExecutionStatus.PASSED})
                    new_states = {**exec_record.step_states, step_id: new_state}
                    exec_record = exec_record.model_copy(update={"step_states": new_states})
                step_events[step_id].set()
                await _safe_commit()

            except Exception as e:
                async with _update_lock:
                    new_state = exec_record.step_states[step_id].model_copy(update={"status": ExecutionStatus.FAILED})
                    new_states = {**exec_record.step_states, step_id: new_state}
                    exec_record = exec_record.model_copy(update={"step_states": new_states})
                await _safe_commit(status_override=ExecutionStatus.FAILED, error_override=str(e))
                raise WorkflowExecutionError(step_id=step_id, task_key=step_obj.task_blueprint, original_error=e) from e

        try:
            async with asyncio.TaskGroup() as tg:
                for step in workflow.steps:
                    tg.create_task(run_step_wrapper(step.id))

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
