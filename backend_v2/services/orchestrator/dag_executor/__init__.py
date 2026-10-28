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

# Phase 4, Step 1: Explicit redundant re-exports for package facade and test patch compatibility
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
    """The central DAGOrchestrator architecture block."""

    _task_group_cls = asyncio.TaskGroup

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
        """Initialize the main DAG orchestration manager."""
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

    # Phase 4, Step 1: Delegate workflow bootstrap and topological wave execution
    async def execute_workflow(
        self,
        execution_id: str,
        workflow: Workflow,
        raw_inputs: WorkflowInputs,
        strictness_level: int | None = None,
        lexical_strictness_level: int | None = None,
        arq_pool: Any | None = None,
    ) -> ExecutionRecord:
        """Execute workflow by bootstrapping execution state and running topological waves."""
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
