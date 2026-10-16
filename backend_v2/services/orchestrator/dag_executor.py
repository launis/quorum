"""Asynchronous Directed Acyclic Graph (DAG) Executor for V3 Workflows.

Strictly follows Event Sourcing, Fail-Fast principles (RFC 7807) and O(1) Concurrency.
God object refactored into: DAGOrchestrator, NodeExecutor, ExecutionCommitter.
"""

from __future__ import annotations

import asyncio
import contextlib
import dataclasses
import logging
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

import opentelemetry.trace as otel_trace
from pydantic import BaseModel, JsonValue, TypeAdapter, ValidationError
from tenacity import AsyncRetrying, before_sleep_log, retry_if_exception, stop_after_attempt, wait_exponential

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDeltaDTO,
    HookDependencies,
    HookState,
    hook_registry,
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
from backend_v2.models.auth import User
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord, ExecutionStep, ExecutionStepState, FrozenContext
from backend_v2.models.domain.inputs import DomainInputValue, WorkflowInputs
from backend_v2.models.domain.matrix import FlattenedAtom
from backend_v2.models.domain.prompt_blocks import PromptBlock
from backend_v2.models.domain.step import Step, StepRule
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.dtos.causal_discovery import (
    AntiFluffAuditDTO,
    CausalGraphPayloadDTO,
    CausalNodeDTO,
    CausalRootCauseDiagnosisDTO,
    CausalTdaFusionResultDTO,
    FairScoringBreakdownDTO,
    PrescriptiveRemediationDTO,
)
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.dtos.node_execution import NodeExecutionUpdateDTO, StepOutputContentDTO
from backend_v2.models.dtos.schema_manifest import GeneratedSchemaManifestDTO
from backend_v2.models.dtos.trace import ProgressTracePayloadDTO, TraceEventMetadataDTO
from backend_v2.models.enums import CognitiveTier, ExecutionStatus, StepType, StrictnessAnchor
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import ErrorTraceEvent, StateProjector, TraceEvent
from backend_v2.services.execution import create_execution_record
from backend_v2.services.localization import set_language
from backend_v2.services.orchestrator.causal_cohesion_evaluator import CausalCohesionEvaluator
from backend_v2.services.orchestrator.context_router import ContextRouter
from backend_v2.services.orchestrator.dag_compiler import DAGCompilerService
from backend_v2.services.orchestrator.engines import ExecutionEngine, build_execution_engine
from backend_v2.services.orchestrator.matrix_reducer import MatrixReducer
from backend_v2.services.orchestrator.rag_preflight_service import RAGPreflightService
from backend_v2.services.orchestrator.strategies.base import StrategyContext, StrategyDependencies
from backend_v2.services.orchestrator.strategies.registry import NodeStrategyFactory
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

__all__ = [
    "DAGExecutor",
    "ExecutionCommitter",
    "NodeExecutor",
    "compute_causal_tda_fusion_result",
    "transform_causal_nodes_to_atoms",
]

type FrozenContextUpdate = list[MCPAuditTrace] | GeneratedSchemaManifestDTO
type ExecutionRecordUpdate = (
    ContextVariablesDTO | FrozenContext | ExecutionMetadata | dict[str, ExecutionStepState] | list[ExecutionStep]
)
type StepOutputContentValue = DomainInputValue | JsonValue


def transform_causal_nodes_to_atoms(nodes: list[CausalNodeDTO]) -> list[FlattenedAtom]:
    """Transform causal discovery proposition nodes into immutable FlattenedAtom instances.

    Args:
        nodes: List of CausalNodeDTO instances from upstream causal discovery.

    Returns:
        List of strictly typed FlattenedAtom instances for TDA evaluation.
    """
    atoms: list[FlattenedAtom] = []
    for node in nodes:
        anchor_target = ""
        if node.paragraph_ref is not None:
            anchor_target = node.paragraph_ref
        extraction_rule = ""
        if node.source_quote is not None:
            extraction_rule = node.source_quote
        atoms.append(
            FlattenedAtom(
                atom_id=node.node_id,
                question=node.claim,
                anchor_target=anchor_target,
                extraction_rule=extraction_rule,
                depends_on=(),
                acceptance_criteria=(),
                anti_patterns=(),
                syntactic_anchors=(),
            )
        )
    return atoms


def compute_causal_tda_fusion_result(
    graph: CausalGraphPayloadDTO,
    evaluative_matrices: dict[str, float] | None = None,
    evaluated_atoms: list[AtomResultDTO] | None = None,
    dampening_factor: float | None = None,
) -> CausalTdaFusionResultDTO:
    """Computes composite fusion result executing five stakeholder benefit pipelines.

    Executes:
    1. Root Cause Attribution: Diagnoses cascading failures via blame_parent_ids.
    2. Anti-Fluff Shield: Quantifies isolated concepts, unsupported claims, and logical cohesion.
    3. Prescriptive Remediation: Identifies unlock paths for root cause failure nodes.
    4. Visual XAI Data Projection: Overlays evaluated statuses and scores on graph nodes.
    5. Fair Scoring Deduplication: Deduplicates cascading penalties with power-curve dampening.

    Args:
        graph: Causal graph payload discovered from source propositions.
        evaluative_matrices: Optional mapping of matrix IDs to evaluated scores.
        evaluated_atoms: Optional list of evaluated AtomResultDTO instances.
        dampening_factor: Optional penalty dampening factor (defaults to settings value).

    Returns:
        CausalTdaFusionResultDTO combining graph and all five analytical facets.
    """
    # 1. Visual XAI Data Projection: Overlay evaluated statuses/scores
    updated_nodes: list[CausalNodeDTO] = []
    atom_by_id: dict[str, AtomResultDTO] = {}
    if evaluated_atoms is not None:
        for atom in evaluated_atoms:
            atom_by_id[atom.tda_id] = atom

    for node in graph.nodes:
        if node.node_id in atom_by_id:
            atom = atom_by_id[node.node_id]
            node_status = ExecutionStatus.FAILED
            if atom.status == ExecutionStatus.PASSED:
                node_status = ExecutionStatus.PASSED
            score_val = node.tda_score
            if evaluative_matrices and atom.matrix_id and atom.matrix_id in evaluative_matrices:
                score_val = evaluative_matrices[atom.matrix_id]
            elif atom.extracted_data and isinstance(atom.extracted_data.value, (int, float)):
                score_val = float(atom.extracted_data.value)

            updated_nodes.append(
                node.model_copy(
                    update={
                        "status": node_status,
                        "tda_score": score_val,
                    }
                )
            )
        else:
            updated_nodes.append(node)

    projected_graph = graph.model_copy(update={"nodes": updated_nodes})

    # 2. Root Cause Attribution
    root_cause_diagnoses: list[CausalRootCauseDiagnosisDTO] = []
    for node in projected_graph.nodes:
        if node.blame_parent_ids:
            paragraph_ref = ""
            if node.paragraph_ref is not None:
                paragraph_ref = node.paragraph_ref
            for parent_id in node.blame_parent_ids:
                root_cause_diagnoses.append(
                    CausalRootCauseDiagnosisDTO(
                        failing_node_id=node.node_id,
                        root_cause_parent_id=parent_id,
                        paragraph_ref=paragraph_ref,
                        explanation=f"Cascading failure caused by root issue in parent '{parent_id}'.",
                        penalty_points=1.0,
                    )
                )

    # 3. Anti-Fluff Shield
    isolated_count = len(projected_graph.isolated_node_ids)
    cycle = projected_graph.cycle_detected
    unsupported_count = sum(1 for n in projected_graph.nodes if not n.source_quote)
    total_nodes = len(projected_graph.nodes)
    if total_nodes == 0:
        cohesion = 1.0
    else:
        connected_ratio = max(0.0, 1.0 - (isolated_count / total_nodes))
        if cycle:
            connected_ratio *= 0.5
        cohesion = round(connected_ratio, 4)

    anti_fluff_audit = AntiFluffAuditDTO(
        isolated_concept_count=isolated_count,
        cycle_detected=cycle,
        unsupported_claims_count=unsupported_count,
        logical_cohesion_score=cohesion,
        detected_hollow_terms=[],
    )

    # 4. Prescriptive Remediation
    prescriptive_remediations: list[PrescriptiveRemediationDTO] = []
    node_by_id = {n.node_id: n for n in projected_graph.nodes}
    for root_id in projected_graph.root_cause_node_ids:
        root_node = None
        if root_id in node_by_id:
            root_node = node_by_id[root_id]
        dependent_children: set[str] = set()
        if root_node is not None:
            dependent_children = set(root_node.dependent_child_ids)
        blaming_nodes = {n.node_id for n in projected_graph.nodes if root_id in n.blame_parent_ids}
        unlocked = sorted(list((dependent_children | blaming_nodes) - {root_id}))
        if unlocked:
            prescriptive_remediations.append(
                PrescriptiveRemediationDTO(
                    target_node_id=root_id,
                    required_action=f"Remediate foundational claim in node '{root_id}' to restore downstream validity.",
                    unlocks_node_ids=unlocked,
                    potential_score_impact=float(len(unlocked) + 1),
                )
            )

    # 5. Fair Scoring Deduplication
    effective_dampening = get_settings().causal_secondary_fault_dampening
    if dampening_factor is not None:
        effective_dampening = dampening_factor

    failing_nodes = [
        n
        for n in projected_graph.nodes
        if n.status in (ExecutionStatus.FAILED, ExecutionStatus.SYSTEM_ERROR, ExecutionStatus.BLOCKED)
    ]
    if not failing_nodes and (projected_graph.root_cause_node_ids or root_cause_diagnoses):
        cascading_fault_count = len({d.failing_node_id for d in root_cause_diagnoses})
        independent_error_count = len(projected_graph.root_cause_node_ids)
    else:
        cascading_fault_count = sum(1 for n in failing_nodes if n.blame_parent_ids)
        independent_error_count = sum(1 for n in failing_nodes if not n.blame_parent_ids)

    raw_penalty = float(independent_error_count + cascading_fault_count) * 1.0
    dampened_savings = round(float(cascading_fault_count) * 1.0 * effective_dampening, 4)
    deduplicated_penalty = round(raw_penalty - dampened_savings, 4)

    fair_scoring = FairScoringBreakdownDTO(
        independent_error_count=independent_error_count,
        cascading_fault_count=cascading_fault_count,
        raw_penalty_points=raw_penalty,
        deduplicated_penalty_points=deduplicated_penalty,
        dampened_savings_points=dampened_savings,
    )

    return CausalTdaFusionResultDTO(
        graph=projected_graph,
        root_cause_diagnoses=root_cause_diagnoses,
        anti_fluff_audit=anti_fluff_audit,
        prescriptive_remediations=prescriptive_remediations,
        fair_scoring=fair_scoring,
    )


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
        context_variables: ContextVariablesDTO | None = None,
        steps: list[ExecutionStep] | None = None,
    ) -> None:
        """Flushes the event array to persistent DB safely.

        Args:
            trace: Current sequence of workflow events.
            status: Target execution status boundary.
            step_states: Execution state dictionary mapping per-step states.
            error: Optional execution failure message to record.
            frozen_context: Serialized snapshot state if provided.
            context_variables: Execution level global variables.
            steps: Optional list of ExecutionStep objects to persist.

        Raises:
            AppException: Triggered with PROGRESS_UPDATE_FAILED if db commit transaction fails.
        """
        try:
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
        """Resolve ExecutionEngine orthogonally from model_strategy based on step engine_type.

        Args:
            step_def: Step domain blueprint model.
            prompt_blocks: Optional pre-loaded list of prompt blocks (retained for signature parity).

        Returns:
            Instantiated ExecutionEngine strategy instance.
        """
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
        arq_pool: Any | None = None,
        context_variables: ContextVariablesDTO | None = None,
        progress_callback: Callable[[int, int], Awaitable[None]] | None = None,
        step_def: Step | None = None,
        global_context_vars: GlobalContextVarsDTO | None = None,
        target_locale: str = "en",
        output_profile_id: str | None = None,
        organization_id: str | None = None,
    ) -> list[TraceEvent]:
        """Executes a pipeline node strategy with static parameters.

        Args:
            step: Step parameters and routing context constraints mappings.
            execution_id: Execution identifier path.
            workflow_id: Primary database record workflow key.
            metadata: Operational contexts such as organization identity maps.
            projector: Transient state snapshot delta computer context.
            expected_inputs: Type list schema limits.
            frozen_ctx: Frozen context snapshot.
            trace: Trace events history.
            strictness_level: Strictness level numeric value.
            arq_pool: Async Arq pool context.
            context_variables: Global state context dictionary or DTO.
            progress_callback: Progress observer async invocation handler.
            step_def: Underlying definition specification if eager loaded.
            global_context_vars: Global context variables state envelope.
            target_locale: ISO language tag.
            output_profile_id: Presentation output profile identifier.
            organization_id: Organization context identifier.

        Returns:
            List of emitted trace events.

        Raises:
            AppException: Fail-fast error if node configuration or blueprint is missing.
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
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
                    )

                if not step_def:
                    step_def_data = await self.deps.workflow_repo.get_step_by_id(blueprint_id)
                    if not step_def_data:
                        msg = f"Step definition not found: {blueprint_id}"
                        logger.error("[NodeExecutor] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                        raise AppException(
                            message=msg,
                            status_code=500,
                            details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
                        )
                    step_def = Step.model_validate(step_def_data)

                # Scoring Hook Separation Contract: Standalone causal steps or steps with zero criteria matrices
                # and no evaluative matrices omit apply_scoring_logic_hook.
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

                normalized_mappings = {}
                for logical_name, path in step.input_mappings.items():
                    normalized_path = ContextRouter.normalize_and_validate_variable(path, projector.snapshot)
                    normalized_mappings[logical_name] = normalized_path

                step = step.model_copy(update={"input_mappings": normalized_mappings})

                criteria_ids: list[str] = list(step_def.criteria_block_ids)
                if step_def.role_block_id:
                    criteria_ids.append(step_def.role_block_id)
                if step_def.extraction_protocol_block_id:
                    criteria_ids.append(step_def.extraction_protocol_block_id)
                if step_def.execution_persona_block_id:
                    criteria_ids.append(step_def.execution_persona_block_id)

                loaded_prompt_blocks = await self.deps.prompt_block_repo.get_prompt_blocks_by_ids(
                    criteria_ids, strict=True
                )

                engine: ExecutionEngine | None = None
                if step_def.type in (StepType.LLM, StepType.CAUSAL_DISCOVERY):
                    engine = self._resolve_execution_engine(step_def, loaded_prompt_blocks)

                effective_deps = self.deps
                if arq_pool is not None:
                    effective_deps = dataclasses.replace(self.deps, arq_pool=arq_pool)

                strategy_impl = NodeStrategyFactory.create_strategy(
                    step_type=step_def.type,
                    deps=effective_deps,
                    engine=engine,
                )

                resolved_global_vars: GlobalContextVarsDTO
                if isinstance(global_context_vars, GlobalContextVarsDTO):
                    resolved_global_vars = global_context_vars
                else:
                    resolved_global_vars = GlobalContextVarsDTO()

                if (
                    isinstance(metadata, ExecutionMetadata)
                    and metadata.global_context_vars is not None
                    and not resolved_global_vars.model_dump(exclude_defaults=True)
                    and isinstance(metadata.global_context_vars, GlobalContextVarsDTO)
                ):
                    resolved_global_vars = metadata.global_context_vars

                resolved_model_registry_id: str | None = None
                if isinstance(metadata, ExecutionMetadata) and metadata.model_registry_id is not None:
                    resolved_model_registry_id = metadata.model_registry_id

                resolved_context_vars: ContextVariablesDTO
                if isinstance(context_variables, ContextVariablesDTO):
                    resolved_context_vars = context_variables
                else:
                    resolved_context_vars = ContextVariablesDTO()

                resolved_cognitive_tier = CognitiveTier.FAST
                if step_def.cognitive_tier is not None:
                    resolved_cognitive_tier = step_def.cognitive_tier

                context = StrategyContext(
                    execution_id=execution_id,
                    workflow_id=workflow_id,
                    target_locale=target_locale,
                    output_profile_id=output_profile_id,
                    metadata=metadata,
                    expected_inputs=expected_inputs,
                    cognitive_tier=resolved_cognitive_tier,
                    strictness_level=strictness_level,
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


class DAGExecutor:
    """The central DAGOrchestrator architecture block."""

    @staticmethod
    def _dlq_record_step_failure(step_id: str, err_code: str, exc: BaseException) -> None:
        """Dead-letter error recording for failed DAG step execution."""
        logger.error("[DAGExecutor] Step %s failed with error [%s]: %s", step_id, err_code, exc, exc_info=True)

    @staticmethod
    def _dlq_handle_progress_commit_error(step_id: str, commit_err: Exception) -> None:
        """Handle non-terminal progress commit error."""
        logger.warning(
            "[DAGExecutor] %s: Non-terminal progress commit skipped for step %s: %s",
            ErrorCodes.PROGRESS_UPDATE_FAILED.name,
            step_id,
            commit_err,
        )

    @staticmethod
    def _dlq_fallback_step_exceptions() -> tuple[type[BaseException], ...]:
        """Fallback step exceptions tuple when litellm is not imported."""
        return (
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
        arq_pool: Any | None = None,
    ) -> ExecutionRecord:
        """Main entrypoint for Workflow Execution.

        Args:
            execution_id: Unique record ID.
            workflow: Loaded configuration parameters.
            raw_inputs: Unprocessed raw input structures.
            strictness_level: User-override context threshold limits.
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

        # Scoring Hook Separation Contract:
        # In standalone non-matrix workflows (zero criteria matrix blocks), omit apply_scoring_logic_hook
        # to prevent false-positive fail-fast crashes on empty evaluative matrices.
        has_criteria_matrices = any(
            bool(s_def.criteria_block_ids) for s_def in step_definitions.values() if s_def is not None
        )
        if not has_criteria_matrices:
            for bp_id, s_def in step_definitions.items():
                if "apply_scoring_logic_hook" in s_def.post_hooks or "apply_scoring_logic" in s_def.post_hooks:
                    filtered_posts = [
                        h for h in s_def.post_hooks if h not in ("apply_scoring_logic_hook", "apply_scoring_logic")
                    ]
                    step_definitions[bp_id] = s_def.model_copy(update={"post_hooks": filtered_posts})

        if strictness_level is None:
            strictness_level = workflow.default_strictness_level

        raw_rec = await self.exec_repo.get_execution(execution_id)
        existing_record: ExecutionRecord | None = None
        if isinstance(raw_rec, ExecutionRecord):
            existing_record = raw_rec
        elif raw_rec is not None:
            existing_record = ExecutionRecord.model_validate(raw_rec, strict=False)

        target_loc = "en"
        if existing_record is not None and existing_record.target_locale:
            target_loc = existing_record.target_locale
        elif raw_inputs is not None and raw_inputs.language:
            target_loc = raw_inputs.language

        steps: list[ExecutionStep] = []
        step_states: dict[str, ExecutionStep] = {}
        for step in workflow.steps:
            step_def = None
            if step.task_blueprint is not None and step.task_blueprint in step_definitions:
                step_def = step_definitions[step.task_blueprint]
            if step_def is not None and isinstance(step_def.name, I18nText):
                step_label = step_def.name.resolve(target_loc)
            elif step_def is not None and isinstance(step_def.name, str) and step_def.name.strip():
                step_label = step_def.name
            else:
                step_label = step.id
            st = ExecutionStep(
                id=step.id,
                label=step_label,
                status=ExecutionStatus.PENDING,
            )
            steps.append(st)
            step_states[step.id] = st

        if existing_record:
            effective_meta = existing_record.metadata
            if effective_meta is None:
                effective_meta = ExecutionMetadata(
                    workflow_version=workflow.version,
                    model_registry_id=workflow.model_registry_id,
                )
            elif effective_meta.model_registry_id is None:
                effective_meta = effective_meta.model_copy(update={"model_registry_id": workflow.model_registry_id})
            exec_record = existing_record.model_copy(
                update={"status": ExecutionStatus.RUNNING, "metadata": effective_meta}
            )
            if not exec_record.steps:
                exec_record = exec_record.model_copy(update={"steps": steps, "step_states": step_states})
            else:
                updated_steps = []
                updated_states = {}
                for s in exec_record.steps:
                    matching_label = step_states[s.id].label if s.id in step_states else s.label
                    new_s = s.model_copy(update={"label": matching_label}) if (s.label == s.id or not s.label) else s
                    updated_steps.append(new_s)
                    updated_states[new_s.id] = new_s
                exec_record = exec_record.model_copy(update={"steps": updated_steps, "step_states": updated_states})

        else:
            exec_record = create_execution_record(
                execution_id=execution_id,
                workflow_id=workflow.id,
                raw_inputs=raw_inputs,
                frozen_context=FrozenContext(),
                source_identity_manifest={},
                status=ExecutionStatus.RUNNING,
                steps=steps,
                step_states=step_states,
                output_profile_id=workflow.default_profile_id,
                metadata=ExecutionMetadata(
                    workflow_version=workflow.version,
                    model_registry_id=workflow.model_registry_id,
                ),
            )

        if exec_record.target_locale:
            set_language(exec_record.target_locale)

        resolved_language: str | None = None
        user_id = exec_record.created_by
        if user_id is None and exec_record.raw_inputs is not None:
            user_id = exec_record.raw_inputs.user_id
        if user_id is not None:
            user_data = await self.identity_repo.get_user(user_id)
            if user_data is not None and isinstance(user_data, User):
                if user_data.language:
                    resolved_language = str(user_data.language)

        if resolved_language is None and exec_record.raw_inputs.language:
            resolved_language = exec_record.raw_inputs.language

        if resolved_language is None and exec_record.target_locale:
            resolved_language = exec_record.target_locale

        if exec_record.metadata and exec_record.metadata.global_context_vars is not None:
            existing_gvars = exec_record.metadata.global_context_vars
            new_lang = resolved_language if not existing_gvars.language else existing_gvars.language
            new_locale = exec_record.target_locale if not existing_gvars.target_locale else existing_gvars.target_locale
            new_profile = workflow.default_profile_id if not existing_gvars.profile_id else existing_gvars.profile_id
            global_context_vars = existing_gvars.model_copy(
                update={"language": new_lang, "target_locale": new_locale, "profile_id": new_profile}
            )
        else:
            global_context_vars = GlobalContextVarsDTO(
                language=resolved_language,
                target_locale=exec_record.target_locale,
                profile_id=workflow.default_profile_id,
            )
            base_meta = exec_record.metadata or ExecutionMetadata(
                workflow_version=workflow.version,
                model_registry_id=workflow.model_registry_id,
            )
            exec_record = exec_record.model_copy(
                update={"metadata": base_meta.model_copy(update={"global_context_vars": global_context_vars})}
            )

        projector = StateProjector()
        for evt in exec_record.execution_trace:
            projector.apply_delta(evt)

        if not exec_record.execution_trace:
            input_event = TraceEvent(step_name="raw_inputs", event_type="input", content=exec_record.raw_inputs)
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
                    metadata=exec_record.metadata or ExecutionMetadata(),
                    global_context_vars=global_context_vars,
                    inputs=ExecutionInputsDTO(
                        raw_inputs=exec_record.raw_inputs.dynamic_inputs,
                        dynamic_inputs=exec_record.raw_inputs.dynamic_inputs,
                    ),
                )
                processed_result = await hook_registry.execute("input_processing", global_hook_state, global_hook_deps)
                if processed_result.success and processed_result.state_delta is not None:
                    delta_content_dict: dict[str, StepOutputContentValue] = {}
                    if isinstance(processed_result.state_delta, HookDeltaDTO):
                        delta_payload = processed_result.state_delta.delta
                        if delta_payload is None:
                            delta_content_dict = {}
                        elif isinstance(delta_payload, ExecutionInputsDTO):
                            delta_content_dict = {
                                **dict(delta_payload.raw_inputs),
                                **dict(delta_payload.dynamic_inputs),
                            }
                        elif isinstance(delta_payload, BaseModel):
                            delta_content_dict = delta_payload.model_dump(mode="json")
                        elif isinstance(delta_payload, (str, int, float, bool, list)):
                            delta_content_dict = {"value": delta_payload}
                        elif not isinstance(delta_payload, (str, int, float, bool, list)) and delta_payload is not None:
                            delta_content_dict = dict(delta_payload)
                    elif isinstance(processed_result.state_delta, ExecutionInputsDTO):
                        delta_content_dict = {
                            **dict(processed_result.state_delta.raw_inputs),
                            **dict(processed_result.state_delta.dynamic_inputs),
                        }
                    elif isinstance(processed_result.state_delta, BaseModel):
                        delta_content_dict = processed_result.state_delta.model_dump(mode="json")
                    elif isinstance(processed_result.state_delta, (str, int, float, bool, list)):
                        delta_content_dict = {"value": processed_result.state_delta}
                    elif (
                        not isinstance(processed_result.state_delta, (str, int, float, bool, list))
                        and processed_result.state_delta is not None
                    ):
                        delta_content_dict = dict(processed_result.state_delta)
                    delta_content = StepOutputContentDTO.model_validate({"data": delta_content_dict})
                    proc_event = TraceEvent(step_name="inputs", event_type="input", content=delta_content)
                    exec_record.execution_trace.append(proc_event)
                    projector.apply_delta(proc_event)
            except Exception as e:
                msg = f"Pre-Hydration failed: {e}"
                logger.error(msg, exc_info=True)
                raise AppException(
                    message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED}, status_code=400
                ) from e

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
            step_exceptions = self._dlq_fallback_step_exceptions()

        failed_previous_steps = []
        for step_id, s_state in exec_record.step_states.items():
            if s_state.status == ExecutionStatus.FAILED:
                failed_previous_steps.append(step_id)
                exec_record = exec_record.transition_step(
                    step_id=step_id,
                    status=ExecutionStatus.PENDING,
                )

        steps_by_id = {step.id: step for step in workflow.steps}
        _update_lock = asyncio.Lock()
        _commit_lock = asyncio.Lock()
        _evaluated_causal_sources: set[str] = set()

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
                    steps=current.steps,
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
                                case StepOutputContentDTO() as step_out:
                                    try:
                                        out_payload = (
                                            step_out.data["graph"] if "graph" in step_out.data else step_out.data
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
                                case _:
                                    try:
                                        evt_payload = (
                                            evt.content["graph"]
                                            if type(evt.content) is dict and "graph" in evt.content
                                            else evt.content
                                        )
                                        if isinstance(evt_payload, CausalGraphPayloadDTO):
                                            upstream_graph = evt_payload
                                        else:
                                            upstream_graph = TypeAdapter(CausalGraphPayloadDTO).validate_python(
                                                evt_payload,
                                                strict=False,
                                            )
                                        break
                                    except ValidationError as err:
                                        logger.error(
                                            "[DAGExecutor] %s: Failed to parse upstream causal graph "
                                            "from trace event: %s",
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
                                    case StepOutputContentDTO() as snap_step_out:
                                        try:
                                            snap_out_payload = (
                                                snap_step_out.data["graph"]
                                                if "graph" in snap_step_out.data
                                                else snap_step_out.data
                                            )
                                            if isinstance(snap_out_payload, CausalGraphPayloadDTO):
                                                upstream_graph = snap_out_payload
                                            else:
                                                upstream_graph = TypeAdapter(CausalGraphPayloadDTO).validate_python(
                                                    snap_out_payload,
                                                    strict=False,
                                                )
                                            break
                                        except ValidationError as err:
                                            logger.error(
                                                "[DAGExecutor] %s: Failed to parse upstream causal graph "
                                                "from snapshot: %s",
                                                ErrorCodes.VALIDATION_FAILED.name,
                                                err,
                                            )
                                            raise AppException(
                                                message=f"Failed to parse upstream causal graph from snapshot: {err}",
                                                status_code=500,
                                                details={"error_code": ErrorCodes.VALIDATION_FAILED},
                                            ) from err
                                    case _:
                                        try:
                                            snap_payload = (
                                                snap_dto.payload["graph"]
                                                if type(snap_dto.payload) is dict and "graph" in snap_dto.payload
                                                else snap_dto.payload
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
                            context_variables=exec_record.context_variables,
                            progress_callback=progress_callback,
                            step_def=node_step_def,
                            global_context_vars=global_context_vars,
                        )

                if step_obj.causal_source_step_id is not None and upstream_graph is not None:
                    evaluated_atoms: list[AtomResultDTO] = []
                    for evt in events:
                        match evt.content:
                            case AtomResultDTO() as single_atom:
                                evaluated_atoms.append(single_atom)
                            case _:
                                if type(evt.content) is dict and "results" in evt.content:
                                    raw_results = evt.content["results"]
                                    if type(raw_results) is list:
                                        for item in raw_results:
                                            match item:
                                                case AtomResultDTO() as item_atom:
                                                    evaluated_atoms.append(item_atom)
                                                case _:
                                                    if type(item) is dict:
                                                        evaluated_atoms.append(
                                                            AtomResultDTO.model_validate(item, strict=False)
                                                        )
                    atoms_arg: list[AtomResultDTO] | None = None
                    if evaluated_atoms:
                        atoms_arg = evaluated_atoms
                    fusion_res = compute_causal_tda_fusion_result(
                        graph=upstream_graph,
                        evaluative_matrices=global_context_vars.evaluative_matrices,
                        evaluated_atoms=atoms_arg,
                        dampening_factor=settings.causal_secondary_fault_dampening,
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
                            total_nodes=len(upstream_graph.nodes),
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
            # RAG Pre-Flight Pipeline Injection
            has_prehydrated = False
            preflight_target_step = None
            for step in workflow.steps:
                if step.task_blueprint and step.task_blueprint in step_definitions:
                    step_b = step_definitions[step.task_blueprint]
                    if "atom_flattening_hook" in step_b.pre_hooks or "synthesis_distiller_hook" in step_b.pre_hooks:
                        has_prehydrated = True
                        preflight_target_step = step
                        break

            if has_prehydrated and preflight_target_step:
                virtual_step_id = f"sys_rag_{uuid.uuid4().hex[:16]}"

                async with _update_lock:
                    exec_record = exec_record.transition_step(
                        step_id=virtual_step_id,
                        status=ExecutionStatus.RUNNING,
                        progress=0,
                        label="system.rag.preflight",
                        has_warning=False,
                    )

                await _safe_commit()

                async def _emit_preflight_progress(message: str, pct: int) -> None:
                    nonlocal exec_record
                    evt = TraceEvent(
                        step_name=virtual_step_id,
                        event_type="progress",
                        content=ProgressTracePayloadDTO(message=message, progress_pct=pct),
                    )
                    async with _update_lock:
                        exec_record.execution_trace.append(evt)
                        projector.apply_delta(evt)
                        exec_record = exec_record.transition_step(
                            step_id=virtual_step_id,
                            status=ExecutionStatus.RUNNING,
                            progress=pct,
                            label=f"system.rag.preflight: {message}",
                        )
                        exec_record = exec_record.model_copy(
                            update={
                                "progress": pct,
                                "status_message": f"Preflight: {message}",
                            }
                        )
                    try:
                        await _safe_commit()
                    except (OSError, AppException, TimeoutError, ConnectionError) as commit_err:
                        self._dlq_handle_progress_commit_error(virtual_step_id, commit_err)

                try:
                    blackboard_payload = await self.rag_preflight.execute(
                        target_step=preflight_target_step,
                        step_def=step_definitions[preflight_target_step.task_blueprint],
                        exec_record=exec_record,
                        emit_progress=_emit_preflight_progress,
                    )

                    async with _update_lock:
                        exec_record = exec_record.transition_step(
                            step_id=virtual_step_id,
                            status=ExecutionStatus.PASSED,
                            progress=100,
                        )
                        new_cv = exec_record.context_variables.with_update(
                            __GLOBAL_ATOM_BLACKBOARD__=blackboard_payload
                        )
                        exec_record = exec_record.model_copy(
                            update={
                                "context_variables": new_cv,
                            }
                        )
                    await _safe_commit()
                except Exception as e:
                    async with _update_lock:
                        exec_record = exec_record.transition_step(
                            step_id=virtual_step_id,
                            status=ExecutionStatus.FAILED,
                            last_error=str(e),
                            has_warning=True,
                        )
                    await _safe_commit(status_override=ExecutionStatus.FAILED, error_override=str(e))
                    raise WorkflowExecutionError(
                        step_id=virtual_step_id, task_key="system.rag.preflight", original_error=e
                    ) from e

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
