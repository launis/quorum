"""Topological Directed Atom (TDA) Engine.

Strategy engine executing Kahn-based causal wave graphs over propositional assertion DAGs.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, override

from backend_v2.core.telemetry import get_tracer
from backend_v2.core.template_processor import TemplateProcessor
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.dag_models import AtomExecutionState, ExtractedAtom, LinkedAtomGraph
from backend_v2.models.dtos.engine import EngineExecutionRequest, EngineExecutionResult
from backend_v2.models.enums import ExecutionStatus
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.engines.base import ExecutionEngine
from backend_v2.services.orchestrator.enriched_dag_executor import EnrichedDagExecutor
from backend_v2.services.orchestrator.result_projector import ResultProjector
from backend_v2.services.orchestrator.two_pass_atomizer import TwoPassAtomizer
from backend_v2.utils.alias_engine import AliasEngine

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

_MATRIX_SOURCE_SENTINEL = "MATRIX_EVALUATION"

__all__ = ["TDAEngine"]


class TDAEngine(ExecutionEngine):
    """Execution engine for Topological Directed Atom (TDA) evaluation.

    Executes ontology extraction and enriched DAG execution over pre-compiled matrix
    assertions (shuffled_atoms) using Kahn-based topological wave evaluation, enforcing
    the Local Causal Markov Condition over causal dependency graphs.
    """

    def __init__(self, prompt_compiler: Any) -> None:
        """Initializes the TDA Engine.

        Args:
            prompt_compiler: The global PromptCompiler instance.
        """
        self._compiler = prompt_compiler

    @override
    async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:
        """Executes the TDA pipeline for matrix evaluations.

        Args:
            request: The EngineExecutionRequest containing runtime context.

        Returns:
            The EngineExecutionResult containing projected results and references.

        Raises:
            AppException: If matrix assertions are missing or context blackboard is corrupted
                (ErrorCodes.VALIDATION_FAILED), or if execution fails catastrophically
                (ErrorCodes.AGENT_EXECUTION_CRITICAL).
        """
        # Fail-Fast: Zero-Fallback mandate. TDAEngine strictly requires pre-compiled matrix assertions.
        if not request.shuffled_atoms:
            logger.error(
                "[TDAEngine] Step '%s' invoked without mandatory matrix assertions ('shuffled_atoms'). Fail-Fast.",
                request.step.id,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
            )
            raise AppException(
                message=(
                    f"Step '{request.step.id}' requires pre-compiled matrix assertions "
                    "('shuffled_atoms'). Free-form extraction fallback is prohibited."
                ),
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        # Circuit Breaker: If preflight determined analytical data is starved, short-circuit immediately.
        blackboard = request.context.context_variables.global_atom_blackboard
        is_starved = blackboard is not None and (blackboard.is_data_starved or not blackboard.atoms_by_input)

        if is_starved:
            logger.info(
                "[TDAEngine] Data starvation circuit breaker active for step %s. Short-circuiting LLM execution.",
                request.step.id,
            )
            nodes = []
            states = {}
            for i, atom in enumerate(request.shuffled_atoms):
                extracted = ExtractedAtom(
                    reasoning="Insufficient input data (Data Starvation).",
                    resolved_claim=atom.question,
                    is_logical_deduction=True,
                    source_quote=None,
                    tda_id=atom.atom_id,
                    source_id=_MATRIX_SOURCE_SENTINEL,
                    source_sequence_index=i,
                )
                nodes.append(LinkedAtomGraph(atom=extracted, depends_on=list(atom.depends_on)))
                states[atom.atom_id] = AtomExecutionState(
                    tda_id=atom.atom_id,
                    status=ExecutionStatus.FAILED,
                    evaluation_reasoning="Insufficient input data (Data Starvation).",
                    short_circuit_reason_tda_ids=[],
                    extensions={},
                )

            projected = ResultProjector.project(nodes, states, matrix_id=request.matrix_block_id)
            if request.progress_callback:
                await request.progress_callback(100, 100)
            return EngineExecutionResult(
                results=projected.results,
                hydrated_references=projected.hydrated_references,
                usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
            )

        try:
            llm_executor = LLMTaskExecutor(
                self._compiler,
                default_validation_context={
                    "execution_id": request.context.execution_id,
                    "step_id": request.step.id,
                },
            )
            atomizer = TwoPassAtomizer(llm_executor)
            dag_executor = EnrichedDagExecutor(llm_executor, request.bound_client)

            global_source_text = request.global_source_text

            alias_engine = AliasEngine()
            paragraphs = [p.strip() for p in global_source_text.split("\n\n") if p.strip()]
            numbered_lines = []
            for p in paragraphs:
                block_id = alias_engine.register(p, prefix="B")
                numbered_lines.append(f"[{block_id}] {p}")
            hydrated_text = "\n\n".join(numbered_lines)

            async def phase_0_progress_matrix(completed: int, total: int) -> None:
                if request.progress_callback:
                    prog = int((completed / total) * 30)
                    await request.progress_callback(prog, 100)

            async def dag_progress_matrix(completed: int, total: int) -> None:
                if request.progress_callback:
                    prog = 30 + int((completed / total) * 70)
                    await request.progress_callback(prog, 100)

            tracer = get_tracer(__name__)
            with tracer.start_as_current_span("tda.atomization") as atom_span:
                atom_span.set_attribute("execution.id", request.context.execution_id)
                atom_span.set_attribute("step.id", request.step.id)
                ontology, usage_p0 = await atomizer.execute_phase_0(
                    request.bound_client,
                    hydrated_text,
                    progress_callback=phase_0_progress_matrix,
                )

            evaluation_context = TemplateProcessor.render_prompt(
                t"{hydrated_text}\n\n<ontology>\n{ontology}\n</ontology>"
            )

            nodes = []
            for i, atom in enumerate(request.shuffled_atoms):
                extracted = ExtractedAtom(
                    reasoning="Matrix assertion provided by orchestrator.",
                    resolved_claim=atom.question,
                    is_logical_deduction=True,
                    source_quote=None,
                    tda_id=atom.atom_id,
                    source_id=_MATRIX_SOURCE_SENTINEL,
                    source_sequence_index=i,
                )
                nodes.append(LinkedAtomGraph(atom=extracted, depends_on=list(atom.depends_on)))

            matrix_context = None
            if request.matrix_context is not None:
                matrix_context = request.matrix_context.model_copy(update={"matrix_assertions": request.shuffled_atoms})

            with tracer.start_as_current_span("tda.topological_evaluation") as topo_span:
                topo_span.set_attribute("execution.id", request.context.execution_id)
                topo_span.set_attribute("step.id", request.step.id)
                topo_span.set_attribute("tda.node_count", len(nodes))
                states, usage_dag = await dag_executor.execute_graph(
                    nodes,
                    evaluation_context,
                    request.target_locale,
                    progress_callback=dag_progress_matrix,
                    execution_id=request.context.execution_id,
                    step_id=request.step.id,
                    matrix_context=matrix_context,
                )
            total_usage = usage_p0 + usage_dag

            projected = ResultProjector.project(nodes, states, request.matrix_block_id)

            return EngineExecutionResult(
                results=projected.results,
                hydrated_references=projected.hydrated_references,
                usage=total_usage,
            )
        except AppException:
            # Re-raise AppException directly to avoid double-wrapping
            raise
        except ExceptionGroup as eg:
            # Unwrap ExceptionGroup if it contains AppException
            for exc in eg.exceptions:
                if isinstance(exc, AppException):
                    raise exc from eg

            logger.error(
                "TDA Engine failed catastrophically during execution.",
                exc_info=True,
                extra={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.name},
            )
            raise AppException(
                message=str(eg),
                status_code=500,
                details={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.value},
            ) from eg
        except Exception as e:
            logger.error(
                "TDA Engine failed catastrophically during execution.",
                exc_info=True,
                extra={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.name},
            )
            raise AppException(
                message=str(e),
                status_code=500,
                details={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.value},
            ) from e
