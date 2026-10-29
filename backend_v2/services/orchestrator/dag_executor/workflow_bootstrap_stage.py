"""Workflow bootstrap, DLQ helpers, safe commit, and Phase 0 RAG Pre-Flight stage."""

from __future__ import annotations

import asyncio
import dataclasses
import logging
import sys
import uuid
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, ValidationError

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDeltaDTO,
    HookDependencies,
    HookState,
    hook_registry,
)
from backend_v2.core.telemetry import inject_trace_context
from backend_v2.exceptions import AppException, ErrorCodes, WorkflowExecutionError
from backend_v2.models.auth import User
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord, ExecutionStep
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.prompt_blocks import AnyPromptBlock
from backend_v2.models.domain.step import Step, StepRule
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.node_execution import StepOutputContentDTO
from backend_v2.models.dtos.trace import ProgressTracePayloadDTO
from backend_v2.models.enums import ExecutionStatus, StepType, StrictnessAnchor
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import StateProjector, TraceEvent
from backend_v2.services.localization import set_language
from backend_v2.services.orchestrator.dag_compiler import DAGCompilerService
from backend_v2.services.orchestrator.dag_executor.execution_committer import ExecutionCommitter, StepOutputContentValue
from backend_v2.services.orchestrator.rag_preflight_service import RAGPreflightService
from backend_v2.services.orchestrator.strategies.base import StrategyDependencies

logger = logging.getLogger(__name__)
__all__ = [
    "WorkflowExecutionState",
    "bootstrap_workflow_execution_state",
    "dlq_fallback_step_exceptions",
    "dlq_handle_progress_commit_error",
    "dlq_record_step_failure",
    "execute_rag_preflight_stage",
    "safe_commit_execution_state",
]
_DAG_EXECUTOR_MODULE = "backend_v2.services.orchestrator.dag_executor"


@dataclasses.dataclass
class WorkflowExecutionState:
    """Execution-scoped state and Two-Lock synchronization primitives for a single workflow run."""

    execution_id: str
    workflow: Workflow
    exec_record: ExecutionRecord
    global_context_vars: GlobalContextVarsDTO
    projector: StateProjector
    step_definitions: dict[str, Step]
    steps_by_id: dict[str, StepRule] = dataclasses.field(default_factory=dict)
    blocks_by_id: dict[str, AnyPromptBlock] = dataclasses.field(default_factory=dict)
    strictness_level: int = StrictnessAnchor.STANDARD.value
    lexical_strictness_level: int = StrictnessAnchor.STANDARD.value
    step_exceptions: tuple[type[BaseException], ...] = ()
    update_lock: asyncio.Lock = dataclasses.field(default_factory=asyncio.Lock)
    commit_lock: asyncio.Lock = dataclasses.field(default_factory=asyncio.Lock)
    evaluated_causal_sources: set[str] = dataclasses.field(default_factory=set)

    @property
    def exec_id(self) -> str:
        """Return the execution ID alias for stage compatibility."""
        return self.execution_id


def dlq_record_step_failure(step_id: str, err_code: str, exc: BaseException) -> None:
    """Record dead-letter error log for a failed DAG step execution."""
    logger.error("[DAGExecutor] Step %s failed with error [%s]: %s", step_id, err_code, exc, exc_info=True)


def dlq_handle_progress_commit_error(step_id: str, commit_err: Exception) -> None:
    """Handle non-terminal progress commit error by logging a warning."""
    msg = "[DAGExecutor] %s: Non-terminal progress commit skipped for step %s: %s"
    logger.warning(msg, ErrorCodes.PROGRESS_UPDATE_FAILED.name, step_id, commit_err)


def dlq_fallback_step_exceptions() -> tuple[type[BaseException], ...]:
    """Return fallback step exceptions tuple when litellm is not imported."""
    t1 = (AppException, ValidationError, RuntimeError, ValueError, TypeError)
    return (*t1, KeyError, OSError, TimeoutError, ConnectionError, ExceptionGroup)


def _extract_input_delta_dict(state_delta: Any) -> dict[str, StepOutputContentValue]:
    """Extract normalized input delta dictionary from HookResult.state_delta."""
    payload = state_delta.delta if isinstance(state_delta, HookDeltaDTO) else state_delta
    if payload is None:
        return {}
    if isinstance(payload, ExecutionInputsDTO):
        return {**dict(payload.raw_inputs), **dict(payload.dynamic_inputs)}
    if isinstance(payload, BaseModel):
        return payload.model_dump(mode="json")
    return {"value": payload} if isinstance(payload, (str, int, float, bool, list)) else dict(payload)


async def bootstrap_workflow_execution_state(
    execution_id: str,
    workflow: Workflow,
    raw_inputs: WorkflowInputs,
    deps: StrategyDependencies,
    strictness_level: int | None = None,
    lexical_strictness_level: int | None = None,
    dlq_fallback_fn: Callable[[], tuple[type[BaseException], ...]] = dlq_fallback_step_exceptions,
) -> WorkflowExecutionState:
    """Pre-fetch step blueprints via TaskGroup and initialize WorkflowExecutionState.

    Args:
        execution_id: Canonical Opaque Stripe ID for the execution record.
        workflow: Target Workflow domain model to validate and bootstrap.
        raw_inputs: Initial WorkflowInputs payload provided at ingress.
        deps: Immutable StrategyDependencies container holding repository ports.
        strictness_level: Optional override for mathematical scoring strictness.
        lexical_strictness_level: Optional override for lexical anchoring strictness.
        dlq_fallback_fn: Callable returning base step exception classes when litellm is absent.

    Returns:
        Initialized WorkflowExecutionState ready for topological wave execution.

    Raises:
        AppException: Triggered with CONFIGURATION_ERROR or VALIDATION_FAILED on failure.
    """
    DAGCompilerService.validate_workflow(workflow)
    blueprint_ids = {s.task_blueprint for s in workflow.steps if s.task_blueprint}
    step_definitions: dict[str, Step] = {}
    step_cls: type[Step] = sys.modules[_DAG_EXECUTOR_MODULE].Step if _DAG_EXECUTOR_MODULE in sys.modules else Step

    async def _fetch_and_validate(b_id: str) -> tuple[str, Step]:
        data = await deps.workflow_repo.get_step_by_id(b_id)
        if not data:
            msg = f"Configuration error: Step '{b_id}' not found."
            logger.error("[DAGExecutor] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True)
            raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR})
        return b_id, step_cls.model_validate(data)

    if blueprint_ids:
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(_fetch_and_validate(b_id)) for b_id in blueprint_ids]
        step_definitions = dict([t.result() for t in tasks])

    if not any(s.criteria_block_ids for s in step_definitions.values() if s and s.type != StepType.CAUSAL_DISCOVERY):
        for bp_id, s_def in step_definitions.items():
            if "apply_scoring_logic_hook" in s_def.post_hooks or "apply_scoring_logic" in s_def.post_hooks:
                posts = [h for h in s_def.post_hooks if h not in ("apply_scoring_logic_hook", "apply_scoring_logic")]
                step_definitions[bp_id] = s_def.model_copy(update={"post_hooks": posts})
    blocks_by_id: dict[str, AnyPromptBlock] = {}
    for s_def in step_definitions.values():
        for cb_id in s_def.criteria_block_ids if s_def.type == StepType.CAUSAL_DISCOVERY else ():
            if (blk := await deps.prompt_block_repo.get_prompt_block_by_id(cb_id)) is not None:
                blocks_by_id[cb_id] = blk

    s_lvl = workflow.default_strictness_level if strictness_level is None else strictness_level
    lex_def = workflow.default_lexical_strictness_level
    lex_lvl = lex_def if lexical_strictness_level is None else lexical_strictness_level
    raw_rec = await deps.exec_repo.get_execution(execution_id)
    existing_record = None if not isinstance(raw_rec, ExecutionRecord) else raw_rec
    if existing_record is None and raw_rec is not None:
        existing_record = ExecutionRecord.model_validate(raw_rec, strict=False)
    ex_loc = None if not existing_record else existing_record.target_locale
    in_loc = None if not raw_inputs else raw_inputs.language
    target_loc = ex_loc if ex_loc else ("en" if not in_loc else in_loc)

    steps: list[ExecutionStep] = []
    for step in workflow.steps:
        bp_def = None if step.task_blueprint not in step_definitions else step_definitions[step.task_blueprint]
        s_name = None if bp_def is None else bp_def.name
        raw_lbl = s_name if isinstance(s_name, str) and s_name.strip() else step.id
        step_label = s_name.resolve(target_loc) if isinstance(s_name, I18nText) else raw_lbl
        steps.append(ExecutionStep(id=step.id, label=step_label, status=ExecutionStatus.PENDING))

    step_states = {s.id: s for s in steps}
    default_meta = ExecutionMetadata(workflow_version=workflow.version, model_registry_id=workflow.model_registry_id)
    run_st = ExecutionStatus.RUNNING
    if existing_record:
        effective_meta = existing_record.metadata if existing_record.metadata is not None else default_meta
        if effective_meta.model_registry_id is None:
            effective_meta = effective_meta.model_copy(update={"model_registry_id": workflow.model_registry_id})
        base_steps = existing_record.steps if existing_record.steps else steps
        up_steps = [
            s.model_copy(update={"label": step_states[s.id].label if s.id in step_states else s.label})
            if (s.label == s.id or not s.label)
            else s
            for s in base_steps
        ]
        up_map = {s.id: s for s in up_steps}
        exec_record = existing_record.model_copy(
            update={"status": run_st, "metadata": effective_meta, "steps": up_steps, "step_states": up_map}
        )
    else:
        tel = default_meta.telemetry if default_meta.telemetry is not None else inject_trace_context()
        res_meta, def_prof = default_meta.model_copy(update={"telemetry": tel}), workflow.default_profile_id
        rec_base = ExecutionRecord(
            id=execution_id, workflow_id=workflow.id, target_locale="en", metadata=res_meta, raw_inputs=raw_inputs
        )
        exec_record = rec_base.model_copy(
            update={"status": run_st, "steps": steps, "step_states": step_states, "output_profile_id": def_prof}
        )

    if exec_record.target_locale:
        set_language(exec_record.target_locale)
    resolved_language: str | None = None
    user_id = exec_record.created_by if exec_record.created_by else exec_record.raw_inputs.user_id
    if user_id is not None:
        user_data = await deps.identity_repo.get_user(user_id)
        if isinstance(user_data, User) and user_data.language:
            resolved_language = str(user_data.language)
    if resolved_language is None:
        raw_lang = exec_record.raw_inputs.language
        resolved_language = raw_lang if raw_lang else exec_record.target_locale
    if exec_record.metadata and exec_record.metadata.global_context_vars is not None:
        egv = exec_record.metadata.global_context_vars
        g_lang = egv.language if egv.language else resolved_language
        g_loc = egv.target_locale if egv.target_locale else exec_record.target_locale
        g_prof = egv.profile_id if egv.profile_id else workflow.default_profile_id
        gvars = egv.model_copy(update={"language": g_lang, "target_locale": g_loc, "profile_id": g_prof})
    else:
        gvars = GlobalContextVarsDTO(
            language=resolved_language, target_locale=exec_record.target_locale, profile_id=workflow.default_profile_id
        )
        base_meta = exec_record.metadata if exec_record.metadata is not None else default_meta
        new_meta = base_meta.model_copy(update={"global_context_vars": gvars})
        exec_record = exec_record.model_copy(update={"metadata": new_meta})
    projector = StateProjector()
    for evt in exec_record.execution_trace:
        projector.apply_delta(evt)
    if not exec_record.execution_trace:
        input_event = TraceEvent(step_name="raw_inputs", event_type="input", content=exec_record.raw_inputs)
        exec_record.execution_trace.append(input_event)
        projector.apply_delta(input_event)
        try:
            r1 = (deps.exec_repo, deps.workflow_repo, deps.comp_repo, deps.prompt_block_repo)
            r2 = (deps.output_profile_repo, deps.identity_repo, deps.system_repo, deps.audit_repo)
            dyn_in = exec_record.raw_inputs.dynamic_inputs
            h_meta = exec_record.metadata if exec_record.metadata is not None else ExecutionMetadata()
            h_in, w_id = ExecutionInputsDTO(raw_inputs=dyn_in, dynamic_inputs=dyn_in), workflow.id
            h_state = HookState(
                execution_id=execution_id, workflow_id=w_id, inputs=h_in, metadata=h_meta, global_context_vars=gvars
            )
            dm = sys.modules
            reg: Any = dm[_DAG_EXECUTOR_MODULE].hook_registry if _DAG_EXECUTOR_MODULE in dm else hook_registry
            processed_result = await reg.execute("input_processing", h_state, HookDependencies(*r1, *r2))
            if processed_result.success and processed_result.state_delta is not None:
                delta_content = StepOutputContentDTO.model_validate(
                    {"data": _extract_input_delta_dict(processed_result.state_delta)}
                )
                proc_event = TraceEvent(step_name="inputs", event_type="input", content=delta_content)
                exec_record.execution_trace.append(proc_event)
                projector.apply_delta(proc_event)
        except Exception as e:
            msg = f"Pre-Hydration failed: {e}"
            logger.error("[DAGExecutor] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED}, status_code=400
            ) from e
    try:
        import litellm.exceptions as _le

        t1 = (_le.APIConnectionError, _le.APIError, _le.RateLimitError, _le.Timeout, _le.ServiceUnavailableError)
        t2 = (_le.InternalServerError, _le.BadGatewayError, _le.AuthenticationError, _le.PermissionDeniedError)
        t3 = (
            _le.NotFoundError,
            _le.UnprocessableEntityError,
            _le.ContextWindowExceededError,
            _le.ContentPolicyViolationError,
        )
        step_exceptions: tuple[type[BaseException], ...] = (*dlq_fallback_fn(), *t1, *t2, *t3)
    except ImportError:  # pragma: no cover
        step_exceptions = dlq_fallback_fn()
    for step_id, s_state in list(exec_record.step_states.items()):
        if s_state.status == ExecutionStatus.FAILED:
            exec_record = exec_record.transition_step(step_id=step_id, status=ExecutionStatus.PENDING)
    state = WorkflowExecutionState(execution_id, workflow, exec_record, gvars, projector, step_definitions)
    state.steps_by_id, state.blocks_by_id = {step.id: step for step in workflow.steps}, blocks_by_id
    state.strictness_level, state.lexical_strictness_level, state.step_exceptions = s_lvl, lex_lvl, step_exceptions
    return state


async def safe_commit_execution_state(
    state: WorkflowExecutionState,
    committer: ExecutionCommitter,
    status_override: ExecutionStatus | None = None,
    error_override: str | None = None,
) -> ExecutionRecord:
    """Persist current ExecutionRecord state under state.commit_lock via ExecutionCommitter.

    Args:
        state: Active WorkflowExecutionState holding the execution record and commit_lock.
        committer: ExecutionCommitter bound to the target execution repository.
        status_override: Optional execution status override to persist.
        error_override: Optional execution error message override to persist.

    Returns:
        Current ExecutionRecord snapshot after commit completion.

    Raises:
        AppException: Triggered with PROGRESS_UPDATE_FAILED if ExecutionCommitter fails to persist.
    """
    async with state.commit_lock:
        cur = state.exec_record
        st = status_override if status_override is not None else cur.status
        err = error_override if error_override is not None else cur.error
        await committer.commit_trace(
            cur.execution_trace, st, cur.step_states, err, cur.frozen_context, cur.context_variables, cur.steps
        )
        return cur


async def execute_rag_preflight_stage(
    state: WorkflowExecutionState,
    rag_preflight: RAGPreflightService,
    committer: ExecutionCommitter,
    dlq_on_progress_commit_error: Callable[[str, Exception], None] = dlq_handle_progress_commit_error,
) -> None:
    """Execute Phase 0 RAG Pre-Flight atomization when pre-hydration hooks are present.

    Args:
        state: Active WorkflowExecutionState containing workflow steps and synchronization locks.
        rag_preflight: Injected RAGPreflightService executing document atomization.
        committer: ExecutionCommitter persisting pre-flight progress and blackboard state.
        dlq_on_progress_commit_error: Callback invoked when non-terminal progress commits fail.

    Raises:
        WorkflowExecutionError: Triggered with WORKFLOW_EXECUTION_FAILED when RAG preflight fails.
    """
    target_step: StepRule | None = None
    for s in state.workflow.steps:
        bp_def = None if s.task_blueprint not in state.step_definitions else state.step_definitions[s.task_blueprint]
        if bp_def and ("atom_flattening_hook" in bp_def.pre_hooks or "synthesis_distiller_hook" in bp_def.pre_hooks):
            target_step = s
            break
    if target_step is None or target_step.task_blueprint is None:
        return
    vid, _update_lock, run_st = f"sys_rag_{uuid.uuid4().hex[:16]}", state.update_lock, ExecutionStatus.RUNNING
    async with _update_lock:
        state.exec_record = state.exec_record.transition_step(vid, run_st, 0, "system.rag.preflight", has_warning=False)
    await safe_commit_execution_state(state, committer)

    async def _emit_preflight_progress(message: str, pct: int) -> None:
        prog_dto = ProgressTracePayloadDTO(message=message, progress_pct=pct)
        evt = TraceEvent(step_name=vid, event_type="progress", content=prog_dto)
        async with _update_lock:
            state.exec_record.execution_trace.append(evt)
            state.projector.apply_delta(evt)
            lbl, status_msg = f"system.rag.preflight: {message}", f"Preflight: {message}"
            state.exec_record = state.exec_record.transition_step(vid, run_st, pct, lbl)
            state.exec_record = state.exec_record.model_copy(update={"progress": pct, "status_message": status_msg})
        try:
            await safe_commit_execution_state(state, committer)
        except (OSError, AppException, TimeoutError, ConnectionError) as commit_err:
            dlq_on_progress_commit_error(vid, commit_err)

    try:
        bp_def = state.step_definitions[target_step.task_blueprint]
        bb_payload = await rag_preflight.execute(target_step, bp_def, state.exec_record, _emit_preflight_progress)
        async with _update_lock:
            state.exec_record = state.exec_record.transition_step(vid, ExecutionStatus.PASSED, progress=100)
            new_cv = state.exec_record.context_variables.with_update(__GLOBAL_ATOM_BLACKBOARD__=bb_payload)
            state.exec_record = state.exec_record.model_copy(update={"context_variables": new_cv})
        await safe_commit_execution_state(state, committer)
    except Exception as e:
        fail_st = ExecutionStatus.FAILED
        async with _update_lock:
            state.exec_record = state.exec_record.transition_step(vid, fail_st, last_error=str(e), has_warning=True)
        await safe_commit_execution_state(state, committer, status_override=fail_st, error_override=str(e))
        msg = "[DAGExecutor] %s: RAG preflight failed for step %s: %s"
        logger.error(msg, ErrorCodes.WORKFLOW_EXECUTION_FAILED.name, vid, e, exc_info=True)
        raise WorkflowExecutionError(step_id=vid, task_key="system.rag.preflight", original_error=e) from e
