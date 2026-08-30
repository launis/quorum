"""Topological Data Analysis Engine.

Extracts the raw TDA pipeline into a standalone strategy engine.
"""

import logging
from typing import TYPE_CHECKING, Any

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


class TDAEngine(ExecutionEngine):
    """Execution engine for Topological Data Analysis.

    Executes ontology extraction and enriched DAG execution over
    the pre-compiled matrix assertions (shuffled_atoms).
    """

    def __init__(self, prompt_compiler: Any) -> None:
        """Initializes the TDA Engine.

        Args:
            prompt_compiler: The global PromptCompiler instance.
        """
        self._compiler = prompt_compiler

    async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:
        """Executes the TDA pipeline for matrix evaluations.

        Args:
            request: The EngineExecutionRequest containing runtime context.

        Returns:
            The EngineExecutionResult containing projected results and references.

        Raises:
            AppException: If matrix assertions are missing or execution fails catastrophically.
        """
        if request.running_event:
            request.running_event.set()

        # Fail-Fast: Zero-Fallback mandate. TDAEngine strictly requires pre-compiled matrix assertions.
        if not request.shuffled_atoms:
            logger.error(
                "[TDAEngine] Step '%s' invoked without mandatory matrix assertions ('shuffled_atoms'). Fail-Fast.",
                request.step.id,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
            )
            raise AppException(
                message=f"Step '{request.step.id}' requires pre-compiled matrix assertions ('shuffled_atoms'). Free-form extraction fallback is prohibited.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        # Circuit Breaker: If preflight determined analytical data is starved, short-circuit immediately.
        raw_blackboard = (
            request.context.context_variables["__GLOBAL_ATOM_BLACKBOARD__"]
            if "__GLOBAL_ATOM_BLACKBOARD__" in request.context.context_variables
            else None
        )
        is_starved = False
        if raw_blackboard and isinstance(raw_blackboard, dict):  # noqa: QGR012 [REASON: Polymorphic DAG payload validation]
            is_starved_flag = raw_blackboard["is_data_starved"] if "is_data_starved" in raw_blackboard else False
            atoms_map = raw_blackboard["atoms_by_input"] if "atoms_by_input" in raw_blackboard else None
            if is_starved_flag or not atoms_map:
                is_starved = True

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
                    extensions={},
                )

            results, hydrated_references = ResultProjector.project(nodes, states, matrix_id=request.matrix_block_id)
            if request.progress_callback:
                await request.progress_callback(100, 100)
            return EngineExecutionResult(
                results=results,
                hydrated_references=hydrated_references,
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

            ontology, usage_p0 = await atomizer.execute_phase_0(
                request.bound_client,
                hydrated_text,
                progress_callback=phase_0_progress_matrix,
                semaphore=request.semaphore,
            )

            evaluation_context = f"{hydrated_text}\n\n<ontology>\n{ontology}\n</ontology>"

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

            matrix_context = (
                request.matrix_context.model_copy(update={"matrix_assertions": request.shuffled_atoms})
                if request.matrix_context
                else None
            )

            states, usage_dag = await dag_executor.execute_graph(
                nodes,
                evaluation_context,
                request.target_locale,
                progress_callback=dag_progress_matrix,
                semaphore=request.semaphore,
                matrix_context=matrix_context,
            )
            total_usage = usage_p0 + usage_dag

            results_dto, hydrated_refs = ResultProjector.project(nodes, states, request.matrix_block_id)

            return EngineExecutionResult(
                results=results_dto,
                hydrated_references=hydrated_refs,
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
