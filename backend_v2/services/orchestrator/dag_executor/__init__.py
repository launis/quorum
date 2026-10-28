"""Asynchronous Directed Acyclic Graph (DAG) Executor package facade.

Strictly follows Event Sourcing, Fail-Fast principles (RFC 7807) and O(1) Concurrency.
Orchestrates workflow execution across causal_tda_fusion, execution_committer, node_executor,
workflow_bootstrap_stage, step_execution_stage, and wave_orchestrator_stage.
"""

from __future__ import annotations

import asyncio
from typing import Any

from backend_v2.core.hook_registry import hook_registry as hook_registry
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
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.step import Step as Step
from backend_v2.models.domain.workflow import Workflow
from backend_v2.services.orchestrator.causal_cohesion_evaluator import CausalCohesionEvaluator
from backend_v2.services.orchestrator.matrix_reducer import MatrixReducer as MatrixReducer
from backend_v2.services.orchestrator.rag_preflight_service import RAGPreflightService
from backend_v2.services.orchestrator.strategies.base import StrategyDependencies
from backend_v2.services.orchestrator.strategies.registry import (
    NodeStrategyFactory as NodeStrategyFactory,
)
from backend_v2.settings import get_settings as get_settings

# Explicit redundant re-exports preserve the public package facade and test patch targets.
from .causal_tda_fusion import (
    compute_causal_tda_fusion_result as compute_causal_tda_fusion_result,
)
from .causal_tda_fusion import transform_causal_nodes_to_atoms as transform_causal_nodes_to_atoms
from .execution_committer import ExecutionCommitter as ExecutionCommitter
from .execution_committer import ExecutionRecordUpdate as ExecutionRecordUpdate
from .execution_committer import FrozenContextUpdate as FrozenContextUpdate
from .execution_committer import StepOutputContentValue as StepOutputContentValue
from .node_executor import NodeExecutor as NodeExecutor
from .step_execution_stage import execute_dag_step_wrapper as execute_dag_step_wrapper
from .step_execution_stage import prepare_step_strategy_context as prepare_step_strategy_context
from .wave_orchestrator_stage import (
    execute_topological_waves_stage as execute_topological_waves_stage,
)
from .wave_orchestrator_stage import (
    finalize_step_output_and_commit as finalize_step_output_and_commit,
)
from .workflow_bootstrap_stage import WorkflowExecutionState as WorkflowExecutionState
from .workflow_bootstrap_stage import (
    bootstrap_workflow_execution_state as bootstrap_workflow_execution_state,
)
from .workflow_bootstrap_stage import dlq_fallback_step_exceptions as dlq_fallback_step_exceptions
from .workflow_bootstrap_stage import (
    dlq_handle_progress_commit_error as dlq_handle_progress_commit_error,
)
from .workflow_bootstrap_stage import dlq_record_step_failure as dlq_record_step_failure
from .workflow_bootstrap_stage import execute_rag_preflight_stage as execute_rag_preflight_stage
from .workflow_bootstrap_stage import safe_commit_execution_state as safe_commit_execution_state

__all__ = [
    "DAGExecutor",
    "ExecutionCommitter",
    "ExecutionRecordUpdate",
    "FrozenContextUpdate",
    "MatrixReducer",
    "NodeExecutor",
    "NodeStrategyFactory",
    "Step",
    "StepOutputContentValue",
    "WorkflowExecutionState",
    "bootstrap_workflow_execution_state",
    "compute_causal_tda_fusion_result",
    "dlq_fallback_step_exceptions",
    "dlq_handle_progress_commit_error",
    "dlq_record_step_failure",
    "execute_dag_step_wrapper",
    "execute_rag_preflight_stage",
    "execute_topological_waves_stage",
    "finalize_step_output_and_commit",
    "get_settings",
    "hook_registry",
    "prepare_step_strategy_context",
    "safe_commit_execution_state",
    "transform_causal_nodes_to_atoms",
]


class DAGExecutor:
    """Central DAG orchestrator coordinating workflow bootstrap and topological wave execution.

    Attributes:
        exec_repo: Repository port for persisting and querying execution records.
        workflow_repo: Repository port for fetching workflow and step definitions.
        comp_repo: Repository port for component definitions.
        prompt_block_repo: Repository port for prompt blocks and scoring criteria.
        output_profile_repo: Repository port for output profile configurations.
        identity_repo: Repository port for user and organization identity records.
        audit_repo: Repository port for audit trail persistence.
        system_repo: Repository port for system-wide model registry and settings.
        compiler: Prompt compiler instance injected into execution strategies.
        rag_preflight: Pre-flight RAG service executed prior to topological waves.
        committer: ExecutionCommitter managing atomic trace and state persistence.
        deps: Immutable StrategyDependencies container shared across node strategies.
        node_executor: NodeExecutor dispatching individual DAG steps to strategies.
    """

    _task_group_cls = asyncio.TaskGroup

    @staticmethod
    def _dlq_record_step_failure(step_id: str, err_code: str, exc: BaseException) -> None:
        """Record dead-letter error telemetry for a failed DAG step execution.

        Args:
            step_id: Canonical Opaque Stripe ID of the failed step.
            err_code: Standardized error code string classifying the failure.
            exc: BaseException instance caught during step execution.
        """
        dlq_record_step_failure(step_id, err_code, exc)

    @staticmethod
    def _dlq_handle_progress_commit_error(step_id: str, commit_err: Exception) -> None:
        """Log and handle a non-terminal progress commit error.

        Args:
            step_id: Canonical Opaque Stripe ID of the step reporting progress.
            commit_err: Exception raised while persisting intermediate progress state.
        """
        dlq_handle_progress_commit_error(step_id, commit_err)

    @staticmethod
    def _dlq_fallback_step_exceptions() -> tuple[type[BaseException], ...]:
        """Return fallback step exception types when LiteLLM is not imported.

        Returns:
            Tuple of base exception classes trapped at the step execution boundary.
        """
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
        """Initialize the DAG orchestration facade and wire strategy dependencies.

        Args:
            exec_repo: Execution persistence repository port.
            workflow_repo: Workflow and step blueprint repository port.
            comp_repo: Component repository port.
            prompt_block_repo: Prompt block repository port.
            output_profile_repo: Output profile repository port.
            identity_repo: User and organization identity repository port.
            audit_repo: Audit log repository port.
            system_repo: System configuration repository port.
            prompt_compiler: Prompt compiler instance for LLM node strategies.
            rag_preflight: RAG pre-flight service executed before wave dispatch.
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

    # Delegate workflow bootstrap and topological wave execution to isolated stage modules.
    async def execute_workflow(
        self,
        execution_id: str,
        workflow: Workflow,
        raw_inputs: WorkflowInputs,
        strictness_level: int | None = None,
        lexical_strictness_level: int | None = None,
        arq_pool: Any | None = None,
    ) -> ExecutionRecord:
        """Execute a workflow by bootstrapping state and running topological waves.

        Args:
            execution_id: Canonical Opaque Stripe ID for the active execution run.
            workflow: Validated Workflow domain model defining the DAG steps.
            raw_inputs: Initial WorkflowInputs payload provided at ingress.
            strictness_level: Optional override for mathematical scoring strictness.
            lexical_strictness_level: Optional override for lexical citation strictness.
            arq_pool: Optional background worker connection pool reference.

        Returns:
            Updated ExecutionRecord snapshot after all topological waves complete.

        Raises:
            AppException: Triggered with CONFIGURATION_ERROR if a step blueprint is missing
                or DAG topology is invalid, VALIDATION_FAILED if input pre-hydration fails,
                WORKFLOW_EXECUTION_FAILED if a topological wave or step fails, or
                PROGRESS_UPDATE_FAILED if state persistence fails.
            ExceptionGroup: Raised by asyncio.TaskGroup when parallel blueprint pre-fetching
                encounters a CONFIGURATION_ERROR.
        """
        _ = arq_pool
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
        return await execute_topological_waves_stage(
            state=state,
            node_executor=self.node_executor,
            committer=self.committer,
            rag_preflight=self.rag_preflight,
            causal_cohesion_evaluator=self._causal_cohesion_evaluator,
            dlq_on_step_failure=self._dlq_record_step_failure,
            dlq_on_progress_commit_error=self._dlq_handle_progress_commit_error,
        )
