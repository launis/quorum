"""Topological Data Analysis Engine.

Extracts the raw TDA pipeline into a standalone strategy engine.
"""

import logging
from typing import TYPE_CHECKING, Any

from backend_v2.exceptions import AppException
from backend_v2.models.dtos.engine import EngineExecutionRequest, EngineExecutionResult
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.engines.base import ExecutionEngine
from backend_v2.services.orchestrator.enriched_dag_executor import EnrichedDagExecutor
from backend_v2.services.orchestrator.result_projector import ResultProjector
from backend_v2.services.orchestrator.sliding_window_linker import SlidingWindowLinker
from backend_v2.services.orchestrator.two_pass_atomizer import TwoPassAtomizer
from backend_v2.settings import get_settings

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

_MATRIX_SOURCE_SENTINEL = "MATRIX_EVALUATION"


class TDAEngine(ExecutionEngine):
    """Execution engine for Topological Data Analysis.

    Executes the multi-pass atomizer, sliding window linker, and enriched
    DAG execution over the extracted ontology atoms.
    """

    def __init__(self, prompt_compiler: Any) -> None:
        """Initializes the TDA Engine.

        Args:
            prompt_compiler: The global PromptCompiler instance.
        """
        self._compiler = prompt_compiler

    async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:
        """Executes the TDA pipeline.

        Args:
            request: The EngineExecutionRequest containing runtime context.

        Returns:
            The EngineExecutionResult containing projected results and references.

        Raises:
            AppException: If engine execution fails catastrophically.
        """
        if request.running_event:
            request.running_event.set()

        try:
            llm_executor = LLMTaskExecutor(
                self._compiler,
                default_validation_context={
                    "execution_id": request.context.execution_id,
                    "step_id": request.step.id,
                },
            )
            atomizer = TwoPassAtomizer(llm_executor)
            linker = SlidingWindowLinker(
                window_size=get_settings().tda_linker_window_size,
                overlap=get_settings().tda_linker_overlap,
            )
            dag_executor = EnrichedDagExecutor(llm_executor, request.bound_client)

            global_source_text = request.global_source_text

            from backend_v2.models.dtos.dag_models import ExtractedAtom, LinkedAtomGraph
            from backend_v2.utils.alias_engine import AliasEngine

            alias_engine = AliasEngine()
            paragraphs = [p.strip() for p in global_source_text.split("\n\n") if p.strip()]
            numbered_lines = []
            for p in paragraphs:
                block_id = alias_engine.register(p, prefix="B")
                numbered_lines.append(f"[{block_id}] {p}")
            hydrated_text = "\n\n".join(numbered_lines)

            if request.shuffled_atoms:

                async def phase_0_progress_matrix(completed: int, total: int) -> None:
                    if request.progress_callback:
                        prog = int((completed / total) * 30)
                        await request.progress_callback(prog, 100)

                async def dag_progress_matrix(completed: int, total: int) -> None:
                    if request.progress_callback:
                        prog = 30 + int((completed / total) * 70)
                        await request.progress_callback(prog, 100)

                ontology = await atomizer.execute_phase_0(
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
                    nodes.append(LinkedAtomGraph(atom=extracted, depends_on=[]))

                states = await dag_executor.execute_graph(
                    nodes,
                    evaluation_context,
                    request.target_locale,
                    progress_callback=dag_progress_matrix,
                    semaphore=request.semaphore,
                    matrix_context=request.matrix_context,
                )
            else:

                async def phase_0_progress(completed: int, total: int) -> None:
                    if request.progress_callback:
                        prog = int((completed / total) * 15)
                        await request.progress_callback(prog, 100)

                async def phase_1_progress(completed: int, total: int) -> None:
                    if request.progress_callback:
                        prog = 15 + int((completed / total) * 20)
                        await request.progress_callback(prog, 100)

                async def linker_progress(completed: int, total: int) -> None:
                    if request.progress_callback:
                        prog = 35 + int((completed / total) * 25)
                        await request.progress_callback(prog, 100)

                async def dag_progress(completed: int, total: int) -> None:
                    if request.progress_callback:
                        prog = 60 + int((completed / total) * 40)
                        await request.progress_callback(prog, 100)

                ontology = await atomizer.execute_phase_0(
                    request.bound_client, hydrated_text, progress_callback=phase_0_progress, semaphore=request.semaphore
                )
                atoms = await atomizer.execute_phase_1(
                    request.bound_client,
                    hydrated_text,
                    ontology,
                    progress_callback=phase_1_progress,
                    semaphore=request.semaphore,
                )
                atoms.sort(key=lambda x: x.source_sequence_index)
                nodes = await linker.link_graph(
                    llm_executor,
                    request.bound_client,
                    atoms,
                    ontology,
                    progress_callback=linker_progress,
                    semaphore=request.semaphore,
                )
                states = await dag_executor.execute_graph(
                    nodes,
                    global_source_text,
                    request.target_locale,
                    progress_callback=dag_progress,
                    semaphore=request.semaphore,
                    matrix_context=request.matrix_context,
                )

            results_dto, hydrated_refs = ResultProjector.project(nodes, states, request.matrix_block_id)

            return EngineExecutionResult(
                results=results_dto,
                hydrated_references=hydrated_refs,
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
                extra={"error_code": "TDA_ENGINE_ERROR"},
            )
            raise AppException(
                message=str(eg),
                status_code=500,
                details={"error_code": "TDA_ENGINE_ERROR"},
            ) from eg
        except Exception as e:
            logger.error(
                "TDA Engine failed catastrophically during execution.",
                exc_info=True,
                extra={"error_code": "TDA_ENGINE_ERROR"},
            )
            raise AppException(
                message=str(e),
                status_code=500,
                details={"error_code": "TDA_ENGINE_ERROR"},
            ) from e
