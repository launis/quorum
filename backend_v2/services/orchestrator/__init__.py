"""Orchestrator services package facade for compiling and executing workflows.

Exposes the core DAG compiler, context router, matrix reducer, causal cohesion
evaluator, prompt compiler, and prompt compiler adapter without pulling in
subpackages that depend on the LLM client layer.
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
from backend_v2.services.orchestrator.matrix_reducer import MatrixReducer as MatrixReducer
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler as PromptCompiler
from backend_v2.services.orchestrator.prompt_compiler_adapter import (
    PromptCompilerAdapter as PromptCompilerAdapter,
)

__all__ = [
    "CausalCohesionEvaluationDTO",
    "CausalCohesionEvaluator",
    "ContextRouter",
    "DAGCompilerService",
    "MatrixReducer",
    "PromptCompiler",
    "PromptCompilerAdapter",
    "RoutingModeConfig",
]
