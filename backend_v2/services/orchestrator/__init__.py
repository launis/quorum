"""Orchestrator services package facade for compiling and executing workflows.

Exposes the core DAG compiler, DAG executor facade, context router, matrix reducer,
causal cohesion evaluator, prompt compiler, and execution engine registry.
"""

from backend_v2.services.orchestrator.causal_cohesion_evaluator import (
    CausalCohesionEvaluationDTO as CausalCohesionEvaluationDTO,
)
from backend_v2.services.orchestrator.causal_cohesion_evaluator import (
    CausalCohesionEvaluator as CausalCohesionEvaluator,
)
from backend_v2.services.orchestrator.context_router import ContextRouter as ContextRouter
from backend_v2.services.orchestrator.context_router import RoutingModeConfig as RoutingModeConfig
from backend_v2.services.orchestrator.dag_compiler import DAGCompilerService as DAGCompilerService
from backend_v2.services.orchestrator.dag_executor import DAGExecutor as DAGExecutor
from backend_v2.services.orchestrator.engines import ENGINE_REGISTRY as ENGINE_REGISTRY
from backend_v2.services.orchestrator.engines import ExecutionEngine as ExecutionEngine
from backend_v2.services.orchestrator.engines import build_execution_engine as build_execution_engine
from backend_v2.services.orchestrator.matrix_reducer import MatrixReducer as MatrixReducer
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler as PromptCompiler

__all__ = [
    "CausalCohesionEvaluationDTO",
    "CausalCohesionEvaluator",
    "ContextRouter",
    "DAGCompilerService",
    "DAGExecutor",
    "ENGINE_REGISTRY",
    "ExecutionEngine",
    "MatrixReducer",
    "PromptCompiler",
    "RoutingModeConfig",
    "build_execution_engine",
]
