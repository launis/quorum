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
    ISystemRepository,
    IWorkflowRepository,
)
from backend_v2.exceptions import AppException, ErrorCodes, WorkflowExecutionError
from backend_v2.models.enums import ScoringStrategy, SystemConcurrency
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
from backend_v2.services.orchestrator.context_router import ContextRouter
from backend_v2.services.orchestrator.dag_compiler import DAGCompilerService
from backend_v2.services.orchestrator.strategies.base import NodeStrategy, StrategyContext
from backend_v2.services.orchestrator.strategies.llm import LLMNodeStrategy
from backend_v2.services.orchestrator.strategies.logic import LogicNodeStrategy

logger = logging.getLogger(__name__)


class ExecutionCommitter:
    """Handles Checkpointing of the Event Sourced Trace."""

    def __init__(self, exec_repo: IExecutionRepository, execution_id: str):
        self.exec_repo = exec_repo
        self.execution_id = execution_id

    async def commit_trace(
        self,
        trace: list[TraceEvent],
        status: ExecutionStatus,
        step_states: dict[str, ExecutionStepState],
        error: str | None = None,
        frozen_context: Any | None = None,
    ) -> None:
        """Flushes the event array to persistent DB safely."""
        try:
            payload: dict[str, Any] = {
                "status": status.value,
                "execution_trace": [e.model_dump(mode="json") for e in trace],
                "step_states": {k: v.model_dump(mode="json") for k, v in step_states.items()},
            }
            if frozen_context:
                payload["frozen_context"] = frozen_context.model_dump(mode="json")

            if error:
                payload["error"] = error

            # The repository natively handles 100KB+ offloading to Blob storage via _offload_payloads()
            await self.exec_repo.update_execution(self.execution_id, payload)
        except Exception as e:
            msg = f"Failed to commit execution trace for {self.execution_id}"
            logger.error("[ExecutionCommitter] %s: %s", ErrorCodes.PROGRESS_UPDATE_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg, details={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED}, status_code=500
            ) from e


class NodeExecutor:
    """Executes a single step in pure isolation, emitting TraceEvents."""

    def __init__(
        self,
        exec_repo: IExecutionRepository,
        workflow_repo: IWorkflowRepository,
        comp_repo: IComponentRepository,
        identity_repo: IIdentityRepository,
        audit_repo: IAuditRepository,
        system_repo: ISystemRepository,
        prompt_compiler: Any,
    ):
        self.exec_repo = exec_repo
        self.workflow_repo = workflow_repo
        self.comp_repo = comp_repo
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
        strictness_level: int = 50,
        arq_pool: Any | None = None,
    ) -> list[TraceEvent]:
        try:
            blueprint_id = getattr(step, "task_blueprint", None)
            if not blueprint_id:
                raise AppException(
                    message=f"Step {step.id} has no task_blueprint configured.",
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
                )

            step_def_data = await self.workflow_repo.get_step_by_id(blueprint_id)
            if not step_def_data:
                raise AppException(
                    message=f"Configuration error: Step '{blueprint_id}' not found.",
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
                )

            step_def = Step.model_validate(step_def_data)

            # Rule 3: Fail-Fast variable resolution & Orphaned Step prevention
            normalized_mappings = {}
            for logical_name, path in step.input_mappings.items():
                normalized_path = ContextRouter.normalize_and_validate_variable(path, {"steps": projector.snapshot})
                normalized_mappings[logical_name] = normalized_path

            # Immutable freeze via model_copy
            step = step.model_copy(update={"input_mappings": normalized_mappings})

            context = StrategyContext(
                execution_id=execution_id,
                workflow_id=workflow_id,
                metadata=metadata,
                expected_inputs=expected_inputs,
                model_strategy=step_def.model_strategy,
                strictness_level=strictness_level,
            )

            strategy_impl: NodeStrategy
            if step_def.type == "logic":
                strategy_impl = LogicNodeStrategy(
                    self.exec_repo,
                    self.workflow_repo,
                    self.comp_repo,
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
                    self.identity_repo,
                    self.audit_repo,
                    self.system_repo,
                    self.compiler,
                    arq_pool=arq_pool,
                )

            # FinOps Circuit Breaker: Worker Cut-off Check (Graceful Exit Hatch)
            org_id = metadata["organization_id"] if "organization_id" in metadata else None
            await strategy_impl.assert_quota(org_id=org_id)

            emitted_events = await strategy_impl.execute(
                step=step,
                projector=projector,
                context=context,
                frozen_ctx=frozen_ctx,
                trace=trace,
                semaphore=semaphore,
            )
            return emitted_events

        except AppException as ae:
            # Rule 3: Fail-Fast -> Crash loudly, don't swallow into ErrorTraceEvent
            logger.error("[NodeExecutor] Fail-Fast Exception for step %s: %s", step.id, str(ae))
            raise
        except Exception as e:
            logger.error("[NodeExecutor] Dual-Reporting Exception for step %s: %s", step.id, str(e), exc_info=True)
            return [
                ErrorTraceEvent(
                    step_name=step.id, error_code="STEP_FAILED", error_message=str(e), content={"traceback": str(e)}
                )
            ]


class DAGExecutor:
    """The central DAGOrchestrator."""

    def __init__(
        self,
        exec_repo: IExecutionRepository,
        workflow_repo: IWorkflowRepository,
        comp_repo: IComponentRepository,
        identity_repo: IIdentityRepository,
        audit_repo: IAuditRepository,
        system_repo: ISystemRepository,
        prompt_compiler: Any,
    ):
        self.exec_repo = exec_repo
        self.workflow_repo = workflow_repo
        self.comp_repo = comp_repo
        self.identity_repo = identity_repo
        self.audit_repo = audit_repo
        self.system_repo = system_repo
        self.compiler = prompt_compiler
        self.committer = ExecutionCommitter(exec_repo, "")
        self.node_executor = NodeExecutor(
            exec_repo, workflow_repo, comp_repo, identity_repo, audit_repo, system_repo, prompt_compiler
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
        """Main entrypoint for Workflow Execution."""
        # Fast Fail validation
        DAGCompilerService.validate_workflow(workflow)

        self.committer.execution_id = execution_id

        if strictness_level is None:
            strictness_level = workflow.default_strictness_level

        # 1. State Rehydration / Initialization
        existing_record_dict = await self.exec_repo.get_execution(execution_id)

        step_states = {
            step.id: ExecutionStepState(id=step.id, label=step.id, status=ExecutionStatus.PENDING.value)
            for step in workflow.steps
        }

        if existing_record_dict:
            exec_record = ExecutionRecord.model_validate(existing_record_dict)
            exec_record = exec_record.model_copy(update={"status": ExecutionStatus.RUNNING})
            if not getattr(exec_record, "step_states", None) or not exec_record.step_states:
                exec_record = exec_record.model_copy(update={"step_states": step_states})

            # Epic 47 Phase 2: Inject Virtual Step for Report Render Transparency
            v_step_id = f"sys_render_{exec_record.output_profile_id or workflow.default_profile_id}"
            if v_step_id not in exec_record.step_states:
                new_states = dict(exec_record.step_states)
                new_states[v_step_id] = ExecutionStepState(
                    id=v_step_id, label="system.virtual.rendering", status=ExecutionStatus.PENDING.value
                )
                exec_record = exec_record.model_copy(update={"step_states": new_states})
        else:
            exec_record = ExecutionRecord(
                id=execution_id,
                workflow_id=workflow.id,
                status=ExecutionStatus.RUNNING,
                raw_inputs=raw_inputs,
                execution_trace=[],
                step_states=step_states,
                frozen_context=FrozenContext(),
            )
            # Epic 47 Phase 2: Inject Virtual Step for Report Render Transparency
            v_step_id = f"sys_render_{workflow.default_profile_id}"
            if v_step_id not in exec_record.step_states:
                new_states = dict(exec_record.step_states)
                new_states[v_step_id] = ExecutionStepState(
                    id=v_step_id, label="system.virtual.rendering", status=ExecutionStatus.PENDING.value
                )
                exec_record = exec_record.model_copy(update={"step_states": new_states})

        # 2. Project Initial State
        projector = StateProjector()
        for evt in exec_record.execution_trace:
            projector.apply_delta(evt)

        # Initial Hydration Phase (if new execution)
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
                    identity_repo=self.identity_repo,
                    audit_repo=self.audit_repo,
                    system_repo=self.system_repo,
                )
                global_hook_state = HookState(
                    execution_id=execution_id,
                    workflow_id=workflow.id,
                    metadata=exec_record.metadata,
                    global_context_vars={},
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

        # 3. Topology Setup
        steps_by_id = {step.id: step for step in workflow.steps}
        step_events: dict[str, asyncio.Event] = {step.id: asyncio.Event() for step in workflow.steps}

        failed_previous_steps = []
        for step_id, s_state in exec_record.step_states.items():
            if s_state.status == ExecutionStatus.COMPLETED.value:
                step_events[step_id].set()
            elif s_state.status == ExecutionStatus.FAILED.value:
                failed_previous_steps.append(step_id)
                new_state = exec_record.step_states[step_id].model_copy(
                    update={"status": ExecutionStatus.PENDING.value}
                )
                new_states = {**exec_record.step_states, step_id: new_state}
                exec_record = exec_record.model_copy(update={"step_states": new_states})

        # Concurrency Limiter
        semaphore = asyncio.Semaphore(SystemConcurrency.MAX_CONCURRENT_LLM_STEPS.value)
        _update_lock = asyncio.Lock()

        async def run_step_wrapper(step_id: str) -> None:
            nonlocal exec_record
            step_obj = steps_by_id[step_id]

            # Skip if completed (Rehydration)
            if exec_record.step_states[step_id].status == ExecutionStatus.COMPLETED.value:
                return

            for dep in step_obj.depends_on:
                await step_events[dep].wait()

            try:
                async with _update_lock:
                    new_state = exec_record.step_states[step_id].model_copy(
                        update={"status": ExecutionStatus.RUNNING.value}
                    )
                    new_states = {**exec_record.step_states, step_id: new_state}
                    exec_record = exec_record.model_copy(update={"step_states": new_states})

                    # Proactive status push
                    await self.committer.commit_trace(
                        trace=exec_record.execution_trace,
                        status=exec_record.status,
                        step_states=exec_record.step_states,
                        frozen_context=exec_record.frozen_context,
                    )

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
                )

                for e in events:
                    exec_record.execution_trace.append(e)
                    projector.apply_delta(e)

                # Error Catching Boundary
                if any(isinstance(e, ErrorTraceEvent) for e in events):
                    async with _update_lock:
                        new_state = exec_record.step_states[step_id].model_copy(
                            update={"status": ExecutionStatus.FAILED.value}
                        )
                        new_states = {**exec_record.step_states, step_id: new_state}
                        exec_record = exec_record.model_copy(update={"step_states": new_states})
                    # Extract the error message from the event
                    msg = [e.error_message for e in events if isinstance(e, ErrorTraceEvent)][0]
                    raise AppException(
                        message=f"Step {step_id} emitted ErrorTraceEvent: {msg}",
                        status_code=500,
                        details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED},
                    )

                async with _update_lock:
                    new_state = exec_record.step_states[step_id].model_copy(
                        update={"status": ExecutionStatus.COMPLETED.value}
                    )
                    new_states = {**exec_record.step_states, step_id: new_state}
                    exec_record = exec_record.model_copy(update={"step_states": new_states})
                    await self.committer.commit_trace(
                        trace=exec_record.execution_trace,
                        status=exec_record.status,
                        step_states=exec_record.step_states,
                        frozen_context=exec_record.frozen_context,
                    )
                step_events[step_id].set()

            except Exception as e:
                async with _update_lock:
                    new_state = exec_record.step_states[step_id].model_copy(
                        update={"status": ExecutionStatus.FAILED.value}
                    )
                    new_states = {**exec_record.step_states, step_id: new_state}
                    exec_record = exec_record.model_copy(update={"step_states": new_states})
                    await self.committer.commit_trace(
                        trace=exec_record.execution_trace,
                        status=ExecutionStatus.FAILED,
                        step_states=exec_record.step_states,
                        error=str(e),
                        frozen_context=exec_record.frozen_context,
                    )
                raise WorkflowExecutionError(step_id=step_id, task_key=step_obj.task_blueprint, original_error=e) from e

        try:
            async with asyncio.TaskGroup() as tg:
                for step in workflow.steps:
                    tg.create_task(run_step_wrapper(step.id))

            # Epic 47 Phase 2: DO NOT transition to COMPLETED here.
            # We keep it as RUNNING so the Arq worker can safely enqueue the Render job.
            # The async Render job will handle the final status transition.
            await self.committer.commit_trace(
                trace=exec_record.execution_trace, status=exec_record.status, step_states=exec_record.step_states
            )
            return exec_record

        except ExceptionGroup as eg:
            # TaskGroup automatically cancels all other running tasks when one task fails.
            # We unwrap the primary exception to maintain the Fail-Fast (RFC 7807) boundary.
            primary_err = eg.exceptions[0]

            # Cleanup stuck 'running' states caused by CancelledError bypassing the standard exception handler
            new_states = dict(exec_record.step_states)
            for state_id, state in new_states.items():
                if state.status == ExecutionStatus.RUNNING.value:
                    new_states[state_id] = state.model_copy(update={"status": ExecutionStatus.FAILED.value})

            exec_record = exec_record.model_copy(
                update={"step_states": new_states, "status": ExecutionStatus.FAILED, "error": str(primary_err)}
            )

            # Strict save in loop death to guarantee XAI trace persistence
            await self.committer.commit_trace(
                trace=exec_record.execution_trace,
                status=exec_record.status,
                step_states=exec_record.step_states,
                error=exec_record.error,
            )

            if isinstance(primary_err, AppException):
                raise primary_err from eg

            raise AppException(
                message=f"Workflow failed: {primary_err}",
                details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED},
                status_code=500,
            ) from primary_err

        except Exception as unexpected_err:
            # Fallback for errors outside the TaskGroup scope
            exec_record = exec_record.model_copy(
                update={"status": ExecutionStatus.FAILED, "error": str(unexpected_err)}
            )

            await self.committer.commit_trace(
                trace=exec_record.execution_trace,
                status=exec_record.status,
                step_states=exec_record.step_states,
                error=exec_record.error,
            )

            if isinstance(unexpected_err, AppException):
                raise

            raise AppException(
                message=f"Workflow failed: {unexpected_err}",
                details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED},
                status_code=500,
            ) from unexpected_err
