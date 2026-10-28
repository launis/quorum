"""Asynchronous Directed Acyclic Graph (DAG) Executor for V3 Workflows.

Strictly follows Event Sourcing, Fail-Fast principles (RFC 7807) and O(1) Concurrency.
God object refactored into: DAGOrchestrator, NodeExecutor, ExecutionCommitter.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
from pathlib import Path
from typing import Any

import opentelemetry.trace as otel_trace
from pydantic import JsonValue, TypeAdapter, ValidationError
from tenacity import AsyncRetrying, before_sleep_log, retry_if_exception, stop_after_attempt, wait_exponential

from backend_v2.core.hook_registry import (
    GlobalContextVarsDTO,
)
from backend_v2.core.hook_registry import (
    hook_registry as hook_registry,
)
from backend_v2.core.telemetry import get_tracer
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
from backend_v2.models.domain.execution import ExecutionRecord, FrozenContext
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.step import Step as Step
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.dtos.causal_discovery import CausalGraphPayloadDTO
from backend_v2.models.dtos.node_execution import StepOutputContentDTO
from backend_v2.models.dtos.schema_manifest import GeneratedSchemaManifestDTO
from backend_v2.models.dtos.trace import TraceEventMetadataDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import ErrorTraceEvent, TraceEvent
from backend_v2.services.orchestrator.causal_cohesion_evaluator import CausalCohesionEvaluator
from backend_v2.services.orchestrator.dag_compiler import DAGCompilerService
from backend_v2.services.orchestrator.matrix_reducer import MatrixReducer
from backend_v2.services.orchestrator.rag_preflight_service import RAGPreflightService
from backend_v2.services.orchestrator.strategies.base import StrategyDependencies
from backend_v2.services.orchestrator.strategies.registry import (
    NodeStrategyFactory as NodeStrategyFactory,
)
from backend_v2.settings import get_settings as get_settings

logger = logging.getLogger(__name__)

# Phase 1 & Phase 2: Declare __path__ submodule bridging and explicit redundant re-exports
__path__: list[str] = [str(Path(__file__).resolve().with_suffix(""))]

from backend_v2.services.orchestrator.dag_executor.causal_tda_fusion import (
    compute_causal_tda_fusion_result as compute_causal_tda_fusion_result,
)
from backend_v2.services.orchestrator.dag_executor.causal_tda_fusion import (
    transform_causal_nodes_to_atoms as transform_causal_nodes_to_atoms,
)
from backend_v2.services.orchestrator.dag_executor.execution_committer import (
    ExecutionCommitter as ExecutionCommitter,
)
from backend_v2.services.orchestrator.dag_executor.execution_committer import (
    ExecutionRecordUpdate as ExecutionRecordUpdate,
)
from backend_v2.services.orchestrator.dag_executor.execution_committer import (
    FrozenContextUpdate as FrozenContextUpdate,
)
from backend_v2.services.orchestrator.dag_executor.execution_committer import (
    StepOutputContentValue as StepOutputContentValue,
)
from backend_v2.services.orchestrator.dag_executor.node_executor import (
    NodeExecutor as NodeExecutor,
)
from backend_v2.services.orchestrator.dag_executor.workflow_bootstrap_stage import (
    WorkflowExecutionState as WorkflowExecutionState,
)
from backend_v2.services.orchestrator.dag_executor.workflow_bootstrap_stage import (
    bootstrap_workflow_execution_state as bootstrap_workflow_execution_state,
)
from backend_v2.services.orchestrator.dag_executor.workflow_bootstrap_stage import (
    dlq_fallback_step_exceptions as dlq_fallback_step_exceptions,
)
from backend_v2.services.orchestrator.dag_executor.workflow_bootstrap_stage import (
    dlq_handle_progress_commit_error as dlq_handle_progress_commit_error,
)
from backend_v2.services.orchestrator.dag_executor.workflow_bootstrap_stage import (
    dlq_record_step_failure as dlq_record_step_failure,
)
from backend_v2.services.orchestrator.dag_executor.workflow_bootstrap_stage import (
    execute_rag_preflight_stage as execute_rag_preflight_stage,
)
from backend_v2.services.orchestrator.dag_executor.workflow_bootstrap_stage import (
    safe_commit_execution_state as safe_commit_execution_state,
)

__all__ = [
    "DAGExecutor",
    "ExecutionCommitter",
    "NodeExecutor",
    "WorkflowExecutionState",
    "bootstrap_workflow_execution_state",
    "compute_causal_tda_fusion_result",
    "dlq_fallback_step_exceptions",
    "dlq_handle_progress_commit_error",
    "dlq_record_step_failure",
    "execute_rag_preflight_stage",
    "safe_commit_execution_state",
    "transform_causal_nodes_to_atoms",
]


class DAGExecutor:
    """The central DAGOrchestrator architecture block."""

    @staticmethod
    def _dlq_record_step_failure(step_id: str, err_code: str, exc: BaseException) -> None:
        """Dead-letter error recording for failed DAG step execution."""
        dlq_record_step_failure(step_id, err_code, exc)

    @staticmethod
    def _dlq_handle_progress_commit_error(step_id: str, commit_err: Exception) -> None:
        """Handle non-terminal progress commit error."""
        dlq_handle_progress_commit_error(step_id, commit_err)

    @staticmethod
    def _dlq_fallback_step_exceptions() -> tuple[type[BaseException], ...]:
        """Fallback step exceptions tuple when litellm is not imported."""
        return dlq_fallback_step_exceptions()

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
        self._causal_cohesion_evaluator = CausalCohesionEvaluator()

    async def execute_workflow(
        self,
        execution_id: str,
        workflow: Workflow,
        raw_inputs: WorkflowInputs,
        strictness_level: int | None = None,
        lexical_strictness_level: int | None = None,
        arq_pool: Any | None = None,
    ) -> ExecutionRecord:
        """Main entrypoint for Workflow Execution.

        Args:
            execution_id: Unique record ID.
            workflow: Loaded configuration parameters.
            raw_inputs: Unprocessed raw input structures.
            strictness_level: User-override context threshold limits.
            lexical_strictness_level: User-override lexical strictness threshold limits.
            arq_pool: Target task queue backend integration.

        Returns:
            The finalized ExecutionRecord domain mapping.

        Raises:
            AppException: Triggered with VALIDATION_FAILED or WORKFLOW_EXECUTION_FAILED during step evaluations.
            WorkflowExecutionError: Instantiated inside execution branches if a step fails to complete gracefully.
        """
        self.committer.execution_id = execution_id
        state = await bootstrap_workflow_execution_state(
            execution_id=execution_id,
            workflow=workflow,
            raw_inputs=raw_inputs,
            deps=self.deps,
            strictness_level=strictness_level,
            lexical_strictness_level=lexical_strictness_level,
            dlq_fallback_fn=self._dlq_fallback_step_exceptions,
        )
        exec_record = state.exec_record
        global_context_vars = state.global_context_vars
        projector = state.projector
        step_definitions = state.step_definitions
        steps_by_id = state.steps_by_id
        strictness_level = state.strictness_level
        lexical_strictness_level = state.lexical_strictness_level
        step_exceptions = state.step_exceptions
        _update_lock = state.update_lock
        _evaluated_causal_sources = state.evaluated_causal_sources

        async def _safe_commit(
            status_override: ExecutionStatus | None = None, error_override: str | None = None
        ) -> None:
            state.exec_record = exec_record
            await safe_commit_execution_state(
                state=state,
                committer=self.committer,
                status_override=status_override,
                error_override=error_override,
            )

        async def run_step_wrapper(step_id: str) -> None:
            nonlocal exec_record, global_context_vars
            step_obj = steps_by_id[step_id]

            if exec_record.step_states[step_id].status == ExecutionStatus.PASSED:
                return

            node_stack = contextlib.ExitStack()
            node_span = node_stack.enter_context(tracer.start_as_current_span(f"dag.node.{step_id}"))
            node_span.set_attribute("node.id", step_id)
            if step_obj.task_blueprint is not None:
                node_span.set_attribute("node.blueprint", step_obj.task_blueprint)
            node_span.set_attribute("node.depends_on", list(step_obj.depends_on))

            try:
                for dep in step_obj.depends_on:
                    if dep in exec_record.step_states and exec_record.step_states[dep].status != ExecutionStatus.PASSED:
                        async with _update_lock:
                            exec_record = exec_record.transition_step(
                                step_id=step_id,
                                status=ExecutionStatus.BLOCKED,
                                last_error=f"Dependency {dep} did not pass",
                                has_warning=True,
                            )
                        await _safe_commit()
                        logger.warning(
                            "[DAGExecutor] Cascading failure: Step %s blocked because dependency %s did not pass.",
                            step_id,
                            dep,
                        )
                        return

                # --- Causal Discovery Upstream Resolution & Fusion Atom Injection ---
                upstream_graph: CausalGraphPayloadDTO | None = None
                if step_obj.causal_source_step_id is not None:
                    if step_obj.causal_source_step_id not in steps_by_id:
                        msg = (
                            f"Step '{step_id}' references causal_source_step_id "
                            f"'{step_obj.causal_source_step_id}' which does not exist in workflow."
                        )
                        logger.error("[DAGExecutor] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                        raise AppException(
                            message=msg,
                            status_code=400,
                            details={"error_code": ErrorCodes.VALIDATION_FAILED},
                        )

                    source_state = None
                    if step_obj.causal_source_step_id in exec_record.step_states:
                        source_state = exec_record.step_states[step_obj.causal_source_step_id]
                    if source_state is None or source_state.status != ExecutionStatus.PASSED:
                        logger.error(
                            "[DAGExecutor] %s: Upstream causal step '%s' did not complete successfully.",
                            ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION.name,
                            step_obj.causal_source_step_id,
                        )
                        raise AppException(
                            message=(
                                "Upstream causal discovery step produced 0 valid proposition nodes for "
                                "downstream evaluation."
                            ),
                            status_code=500,
                            details={"error_code": ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION},
                        )

                    for evt in reversed(exec_record.execution_trace):
                        if evt.step_name == step_obj.causal_source_step_id and evt.event_type == "output":
                            match evt.content:
                                case CausalGraphPayloadDTO() as direct_graph:
                                    upstream_graph = direct_graph
                                    break
                                case raw_evt_content:
                                    try:
                                        evt_map = (
                                            raw_evt_content.data
                                            if isinstance(raw_evt_content, StepOutputContentDTO)
                                            else raw_evt_content
                                        )
                                        out_payload = (
                                            evt_map["graph"]
                                            if type(evt_map) is dict and "graph" in evt_map
                                            else evt_map
                                        )
                                        if isinstance(out_payload, CausalGraphPayloadDTO):
                                            upstream_graph = out_payload
                                        else:
                                            upstream_graph = TypeAdapter(CausalGraphPayloadDTO).validate_python(
                                                out_payload,
                                                strict=False,
                                            )
                                        break
                                    except ValidationError as err:
                                        logger.error(
                                            "[DAGExecutor] %s: Failed to parse upstream causal graph "
                                            "from step output: %s",
                                            ErrorCodes.VALIDATION_FAILED.name,
                                            err,
                                        )
                                        raise AppException(
                                            message=f"Failed to parse upstream causal graph: {err}",
                                            status_code=500,
                                            details={"error_code": ErrorCodes.VALIDATION_FAILED},
                                        ) from err

                    if upstream_graph is None:
                        for snap_dto in projector.snapshot:
                            if snap_dto.step_id == step_obj.causal_source_step_id:
                                match snap_dto.payload:
                                    case CausalGraphPayloadDTO() as snap_graph:
                                        upstream_graph = snap_graph
                                        break
                                    case raw_snap_content:
                                        try:
                                            snap_map = (
                                                raw_snap_content.data
                                                if isinstance(raw_snap_content, StepOutputContentDTO)
                                                else raw_snap_content
                                            )
                                            snap_payload = (
                                                snap_map["graph"]
                                                if type(snap_map) is dict and "graph" in snap_map
                                                else snap_map
                                            )
                                            if isinstance(snap_payload, CausalGraphPayloadDTO):
                                                upstream_graph = snap_payload
                                            else:
                                                upstream_graph = TypeAdapter(CausalGraphPayloadDTO).validate_python(
                                                    snap_payload,
                                                    strict=False,
                                                )
                                            break
                                        except ValidationError as err:
                                            logger.error(
                                                "[DAGExecutor] %s: Failed to parse upstream causal graph "
                                                "from snapshot payload: %s",
                                                ErrorCodes.VALIDATION_FAILED.name,
                                                err,
                                            )
                                            raise AppException(
                                                message=(
                                                    "Failed to parse upstream causal graph from snapshot payload: "
                                                    f"{err}"
                                                ),
                                                status_code=500,
                                                details={"error_code": ErrorCodes.VALIDATION_FAILED},
                                            ) from err

                    if upstream_graph is None or not upstream_graph.nodes:
                        msg = (
                            "Upstream causal discovery step produced 0 valid proposition nodes for "
                            "downstream evaluation."
                        )
                        logger.error("[DAGExecutor] %s: %s", ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION.name, msg)
                        raise AppException(
                            message=msg,
                            status_code=500,
                            details={"error_code": ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION},
                        )

                    fusion_atoms = transform_causal_nodes_to_atoms(upstream_graph.nodes)
                    async with _update_lock:
                        global_context_vars = global_context_vars.model_copy(update={"shuffled_atoms": fusion_atoms})
                        base_meta = exec_record.metadata or ExecutionMetadata(
                            workflow_version=workflow.version,
                            model_registry_id=workflow.model_registry_id,
                        )
                        exec_record = exec_record.model_copy(
                            update={
                                "metadata": base_meta.model_copy(update={"global_context_vars": global_context_vars})
                            }
                        )

                # --- Pre-Synthesis Matrix Reducer Lifecycle Event ---
                step_def = None
                if step_obj.task_blueprint is not None and step_obj.task_blueprint in step_definitions:
                    step_def = step_definitions[step_obj.task_blueprint]
                if step_def and (
                    "atom_flattening_hook" in step_def.pre_hooks or "synthesis_distiller_hook" in step_def.pre_hooks
                ):
                    has_evaluated_atoms = any(exec_record.step_states.values()) or any(
                        evt.event_type == "output" and evt.step_name != "matrix_reducer"
                        for evt in exec_record.execution_trace
                    )
                    if has_evaluated_atoms:
                        try:
                            lightweight_matrix = MatrixReducer.reduce_matrix(exec_record)

                            reduce_event = TraceEvent(
                                step_name="matrix_reducer", event_type="output", content=lightweight_matrix
                            )

                            async with _update_lock:
                                exec_record.execution_trace.append(reduce_event)
                                projector.apply_delta(reduce_event)

                                new_cv = exec_record.context_variables.with_update(
                                    __MATRIX_REDUCER_OUTPUT__=lightweight_matrix
                                )
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
                    exec_record = exec_record.transition_step(
                        step_id=step_id,
                        status=ExecutionStatus.RUNNING,
                    )

                await _safe_commit()

                async def progress_callback(completed: int, total: int) -> None:
                    nonlocal exec_record

                    if total == 100:
                        prog = completed
                        label = f"Processing... {prog}%"
                    else:
                        prog = 0
                        if total > 0:
                            prog = int((completed / total) * 100)
                        label = f"Evaluating batch {completed}/{total}..."

                    async with _update_lock:
                        exec_record = exec_record.transition_step(
                            step_id=step_id,
                            status=exec_record.step_states[step_id].status,
                            progress=prog,
                            label=label,
                        )
                        exec_record = exec_record.model_copy(
                            update={
                                "progress": prog,
                                "status_message": label,
                            }
                        )
                    try:
                        await _safe_commit()
                        logger.info("Progress updated for step %s: %s", step_id, label)
                    except (OSError, AppException, TimeoutError, ConnectionError) as commit_err:
                        self._dlq_handle_progress_commit_error(step_id, commit_err)

                node_step_def: Step | None = None
                if step_obj.task_blueprint is not None and step_obj.task_blueprint in step_definitions:
                    node_step_def = step_definitions[step_obj.task_blueprint]

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
                            metadata=exec_record.metadata
                            or ExecutionMetadata(
                                workflow_version=workflow.version, model_registry_id=workflow.model_registry_id
                            ),
                            target_locale=exec_record.target_locale,
                            output_profile_id=exec_record.output_profile_id,
                            organization_id=exec_record.organization_id,
                            projector=projector,
                            expected_inputs=workflow.expected_inputs,
                            frozen_ctx=exec_record.frozen_context,
                            trace=exec_record.execution_trace,
                            strictness_level=strictness_level,
                            lexical_strictness_level=lexical_strictness_level,
                            context_variables=exec_record.context_variables,
                            progress_callback=progress_callback,
                            step_def=node_step_def,
                            global_context_vars=global_context_vars,
                        )

                if step_obj.causal_source_step_id is not None and upstream_graph is not None:
                    evaluated_atoms: list[AtomResultDTO] = []
                    atom_adapter = TypeAdapter(AtomResultDTO)
                    for evt in events:
                        match evt.content:
                            case AtomResultDTO() as single_atom:
                                evaluated_atoms.append(single_atom)
                            case StepOutputContentDTO() as step_out:
                                if "results" in step_out.data:
                                    raw_results = step_out.data["results"]
                                    if isinstance(raw_results, list):
                                        for item in raw_results:
                                            match item:
                                                case AtomResultDTO() as item_atom:
                                                    evaluated_atoms.append(item_atom)
                                                case _:
                                                    evaluated_atoms.append(atom_adapter.validate_python(item))
                            case _:
                                if type(evt.content) is dict and "results" in evt.content:
                                    raw_results = evt.content["results"]
                                    if isinstance(raw_results, list):
                                        for item in raw_results:
                                            match item:
                                                case AtomResultDTO() as item_atom:
                                                    evaluated_atoms.append(item_atom)
                                                case _:
                                                    evaluated_atoms.append(atom_adapter.validate_python(item))
                    atoms_arg: list[AtomResultDTO] | None = None
                    if evaluated_atoms:
                        atoms_arg = evaluated_atoms
                    fusion_res = compute_causal_tda_fusion_result(
                        graph=upstream_graph,
                        evaluative_matrices=global_context_vars.evaluative_matrices,
                        evaluated_atoms=atoms_arg,
                        dampening_factor=settings.causal_secondary_fault_dampening,
                        expected_inputs=workflow.expected_inputs,
                    )
                    events.append(
                        TraceEvent(
                            step_name=step_id,
                            event_type="output",
                            content={"fusion": fusion_res},
                        )
                    )

                    if step_obj.causal_source_step_id not in _evaluated_causal_sources:
                        _evaluated_causal_sources.add(step_obj.causal_source_step_id)
                        eval_dto = self._causal_cohesion_evaluator.evaluate_causal_cohesion(
                            audit=fusion_res.anti_fluff_audit,
                            total_nodes=fusion_res.total_deliverable_nodes,
                            strictness_level=workflow.default_strictness_level,
                            matrix_block_id=settings.causal_cohesion_matrix_block_id,
                        )
                        events.append(
                            TraceEvent(
                                step_name=step_obj.causal_source_step_id,
                                event_type="output",
                                content={
                                    "results": eval_dto.atom_results,
                                    "hydrated_references": eval_dto.hydrated_references,
                                    eval_dto.matrix_block_id: eval_dto.matrix_output.model_dump(mode="json"),
                                },
                            )
                        )
                        events.append(
                            TraceEvent(
                                step_name=step_obj.causal_source_step_id,
                                event_type="decision",
                                metadata=TraceEventMetadataDTO(is_context_update=True),
                                content=GlobalContextVarsDTO(
                                    evaluative_matrices={eval_dto.matrix_block_id: eval_dto.score_result.score}
                                ),
                            )
                        )

                has_error_evt = any(isinstance(evt, ErrorTraceEvent) for evt in events)
                async with _update_lock:
                    step_mcp_traces: list[MCPAuditTrace] = []
                    step_generated_schemas: dict[str, JsonValue] = {}
                    new_cv = exec_record.context_variables
                    has_cv_updates = False
                    has_gvar_updates = False
                    for evt in events:
                        exec_record.execution_trace.append(evt)
                        projector.apply_delta(evt)
                        if (
                            evt.event_type == "decision"
                            and evt.metadata
                            and evt.metadata.is_context_update
                            and not isinstance(evt.content, (str, int, float, bool, list))
                            and evt.content is not None
                        ):
                            content_dict = dict(evt.content)
                            new_cv = new_cv.with_update(**content_dict)
                            has_cv_updates = True
                            gvar_data = {
                                k: v for k, v in content_dict.items() if k in GlobalContextVarsDTO.model_fields
                            }
                            if gvar_data:
                                parsed_gvars = GlobalContextVarsDTO.model_validate(gvar_data)
                                if parsed_gvars.evaluative_matrices is not None:
                                    if global_context_vars.evaluative_matrices:
                                        merged_eval = {
                                            **global_context_vars.evaluative_matrices,
                                            **parsed_gvars.evaluative_matrices,
                                        }
                                    else:
                                        merged_eval = parsed_gvars.evaluative_matrices
                                    global_context_vars = global_context_vars.model_copy(
                                        update={"evaluative_matrices": merged_eval}
                                    )
                                    has_gvar_updates = True
                                if parsed_gvars.passivity_detected is not None:
                                    global_context_vars = global_context_vars.model_copy(
                                        update={"passivity_detected": parsed_gvars.passivity_detected}
                                    )
                                    has_gvar_updates = True
                        match evt:
                            case TraceEvent() if evt.mcp_audit_traces:
                                step_mcp_traces.extend(evt.mcp_audit_traces)
                            case TraceEvent() if evt.metadata and evt.metadata.generated_schema is not None:
                                step_generated_schemas[evt.step_name] = evt.metadata.generated_schema

                    schema_manifest = GeneratedSchemaManifestDTO(schemas=step_generated_schemas)
                    updates: dict[str, ExecutionRecordUpdate] = {}
                    if has_cv_updates:
                        updates["context_variables"] = new_cv

                    if has_gvar_updates:
                        base_meta = exec_record.metadata or ExecutionMetadata(
                            workflow_version=workflow.version,
                            model_registry_id=workflow.model_registry_id,
                        )
                        updates["metadata"] = base_meta.model_copy(update={"global_context_vars": global_context_vars})

                    fc_updates: dict[str, FrozenContextUpdate] = {}
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

                    if schema_manifest.schemas:
                        merged_schemas = {**base_fc.generated_schemas.schemas, **schema_manifest.schemas}
                        fc_updates["generated_schemas"] = GeneratedSchemaManifestDTO(schemas=merged_schemas)

                    if fc_updates:
                        new_fc = base_fc.model_copy(update=fc_updates)
                        updates["frozen_context"] = new_fc

                    step_status = ExecutionStatus.FAILED if has_error_evt else ExecutionStatus.PASSED
                    step_prog = 100 if step_status == ExecutionStatus.PASSED else None
                    if updates:
                        exec_record = exec_record.model_copy(update=updates)
                    exec_record = exec_record.transition_step(
                        step_id=step_id,
                        status=step_status,
                        progress=step_prog,
                    )

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
                node_span.record_exception(e)
                node_span.set_status(otel_trace.StatusCode.ERROR, str(e))
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
                    exec_record = exec_record.transition_step(
                        step_id=step_id,
                        status=ExecutionStatus.FAILED,
                        last_error=str(e),
                        has_warning=True,
                    )
                    error_evt = ErrorTraceEvent(
                        step_name=step_id,
                        error_code=err_code,
                        error_message=str(e),
                        content={"error_code": err_code, "message": str(e)},
                    )
                    exec_record.execution_trace.append(error_evt)
                    projector.apply_delta(error_evt)
                await _safe_commit(status_override=ExecutionStatus.FAILED, error_override=str(e))
                self._dlq_record_step_failure(step_id, err_code, e)
                raise
            except Exception as e:
                node_span.record_exception(e)
                node_span.set_status(otel_trace.StatusCode.ERROR, str(e))
                async with _update_lock:
                    exec_record = exec_record.transition_step(
                        step_id=step_id,
                        status=ExecutionStatus.FAILED,
                        last_error=str(e),
                        has_warning=True,
                    )
                await _safe_commit(status_override=ExecutionStatus.FAILED, error_override=str(e))
                self._dlq_record_step_failure(step_id, "UNEXPECTED_STEP_EXCEPTION", e)
                raise
            finally:
                node_stack.close()

        tracer = get_tracer(__name__)
        orch_stack = contextlib.ExitStack()
        orch_span = orch_stack.enter_context(tracer.start_as_current_span("dag.orchestration"))
        orch_span.set_attribute("execution.id", execution_id)
        orch_span.set_attribute("workflow.id", workflow.id)
        orch_span.set_attribute("workflow.node_count", len(workflow.steps))
        try:
            state.exec_record = exec_record
            try:
                await execute_rag_preflight_stage(
                    state=state,
                    rag_preflight=self.rag_preflight,
                    committer=self.committer,
                    dlq_on_progress_commit_error=self._dlq_handle_progress_commit_error,
                )
            finally:
                exec_record = state.exec_record

            waves = DAGCompilerService.compute_topological_waves(workflow.steps)
            for wave_idx, wave in enumerate(waves):
                steps_to_run = [s for s in wave if exec_record.step_states[s.id].status != ExecutionStatus.PASSED]
                if not steps_to_run:
                    continue

                try:
                    async with asyncio.TaskGroup() as tg:
                        for step_rule in steps_to_run:
                            tg.create_task(run_step_wrapper(step_rule.id))
                except* BaseException as eg:
                    primary_err = eg.exceptions[0]
                    logger.error("[DAGExecutor] Wave %d execution failed: %s", wave_idx, eg, exc_info=True)

                    async with _update_lock:
                        for step_rule in wave:
                            curr_st = exec_record.step_states[step_rule.id]
                            if curr_st.status in (ExecutionStatus.RUNNING, ExecutionStatus.PENDING):
                                exec_record = exec_record.transition_step(
                                    step_id=step_rule.id,
                                    status=ExecutionStatus.FAILED,
                                    last_error=str(primary_err),
                                    has_warning=True,
                                )
                                self._dlq_record_step_failure(step_rule.id, "WAVE_TASKGROUP_CANCELLED", primary_err)

                        for remaining_wave in waves[wave_idx + 1 :]:
                            for downstream_step in remaining_wave:
                                if exec_record.step_states[downstream_step.id].status == ExecutionStatus.PENDING:
                                    exec_record = exec_record.transition_step(
                                        step_id=downstream_step.id,
                                        status=ExecutionStatus.BLOCKED,
                                        last_error=f"Blocked due to wave {wave_idx} failure: {primary_err}",
                                        has_warning=True,
                                    )
                                    self._dlq_record_step_failure(
                                        downstream_step.id,
                                        "DOWNSTREAM_WAVE_BLOCKED",
                                        primary_err,
                                    )

                        exec_record = exec_record.model_copy(
                            update={
                                "status": ExecutionStatus.FAILED,
                                "error": str(primary_err),
                            }
                        )

                    await self.committer.commit_trace(
                        trace=exec_record.execution_trace,
                        status=exec_record.status,
                        step_states=exec_record.step_states,
                        error=exec_record.error,
                        context_variables=exec_record.context_variables,
                        steps=exec_record.steps,
                    )

                    if isinstance(primary_err, AppException):
                        orch_span.record_exception(primary_err)
                        orch_span.set_status(otel_trace.StatusCode.ERROR, str(primary_err))
                        raise primary_err from eg

                    msg = f"Workflow failed: {primary_err}"
                    logger.error("[DAGExecutor] %s: %s", ErrorCodes.WORKFLOW_EXECUTION_FAILED.name, msg)
                    orch_span.record_exception(primary_err)
                    orch_span.set_status(otel_trace.StatusCode.ERROR, str(primary_err))
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED},
                    ) from eg

            if any(
                state.status in (ExecutionStatus.FAILED, ExecutionStatus.BLOCKED)
                for state in exec_record.step_states.values()
            ):
                exec_record = exec_record.model_copy(update={"status": ExecutionStatus.FAILED})
                await self.committer.commit_trace(
                    trace=exec_record.execution_trace,
                    status=exec_record.status,
                    step_states=exec_record.step_states,
                    context_variables=exec_record.context_variables,
                    steps=exec_record.steps,
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
                steps=exec_record.steps,
            )

            return exec_record

        except Exception as unexpected_err:
            async with _update_lock:
                for s in exec_record.steps:
                    if s.status == ExecutionStatus.RUNNING:
                        exec_record = exec_record.transition_step(
                            step_id=s.id,
                            status=ExecutionStatus.FAILED,
                            last_error=str(unexpected_err),
                            has_warning=True,
                        )
                exec_record = exec_record.model_copy(
                    update={
                        "status": ExecutionStatus.FAILED,
                        "error": str(unexpected_err),
                    }
                )

            await self.committer.commit_trace(
                trace=exec_record.execution_trace,
                status=exec_record.status,
                step_states=exec_record.step_states,
                error=exec_record.error,
                context_variables=exec_record.context_variables,
                steps=exec_record.steps,
            )

            orch_span.record_exception(unexpected_err)
            orch_span.set_status(otel_trace.StatusCode.ERROR, str(unexpected_err))

            if isinstance(unexpected_err, AppException):
                raise

            msg = f"Workflow failed: {unexpected_err}"
            logger.error("[DAGExecutor] %s: %s", ErrorCodes.WORKFLOW_EXECUTION_FAILED.name, msg)
            raise AppException(
                message=msg,
                details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED},
                status_code=500,
            ) from unexpected_err
        finally:
            orch_stack.close()
