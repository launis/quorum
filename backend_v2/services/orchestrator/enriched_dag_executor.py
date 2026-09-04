"""Enriched DAG Executor.

Combines the TopologicalEvaluator with the ExtractiveSensorService to evaluate
a complete Enriched Atom Graph asynchronously.
"""

import asyncio
import logging
from collections.abc import Awaitable, Callable

from backend_v2.exceptions import AppException
from backend_v2.llm.caching_service import LLMCachingService
from backend_v2.llm.client import LLMClient
from backend_v2.llm.provider import _is_transient_llm_error
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.dag_models import (
    AtomEvaluationResultDTO,
    AtomExecutionState,
    LinkedAtomGraph,
)
from backend_v2.models.dtos.engine import MatrixEvaluationContext
from backend_v2.models.enums import ExecutionStatus
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.extractive_sensor_service import ExtractiveSensorService
from backend_v2.services.orchestrator.prompts.matrix_sensor_prompt_builder import MatrixSensorPromptBuilder
from backend_v2.services.orchestrator.topological_evaluator import TopologicalEvaluator
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)


class EnrichedDagExecutor:
    """Orchestrates the execution of a Directed Acyclic Graph of atoms.

    Uses the TopologicalEvaluator to handle priority cascades, short-circuits,
    and dead-lock prevention, while injecting LLM-based boolean evaluation for the nodes.
    """

    def __init__(self, llm_executor: LLMTaskExecutor, llm_client: LLMClient) -> None:
        """Initializes the executor with the required LLM task executor.

        Args:
            llm_executor: The executor for running LLM structured tasks.
            llm_client: The initialized LLM client to execute the queries.
        """
        self._llm_executor = llm_executor
        self._llm_client = llm_client
        self._topological_evaluator = TopologicalEvaluator()

    async def execute_graph(
        self,
        nodes: list[LinkedAtomGraph],
        source_text: str,
        locale: str | None = None,
        progress_callback: Callable[[int, int], Awaitable[None]] | None = None,
        execution_id: str = "default_run",
        semaphore: asyncio.Semaphore | None = None,
        matrix_context: MatrixEvaluationContext | None = None,
    ) -> tuple[dict[str, AtomExecutionState], TokenUsage]:
        """Executes the complete DAG of atoms.

        Args:
            nodes: The list of validated LinkedAtomGraphs.
            source_text: The original document text for contextual evaluation.
            locale: Optional target locale/language code.
            progress_callback: Optional progress reporter callback function.
            execution_id: Execution identifier path.
            semaphore: Concurrency limiter semaphore.
            matrix_context: Optional Matrix evaluation context.

        Returns:
            A tuple of:
            - A dictionary mapping tda_id to its final AtomExecutionState.
            - Aggregated TokenUsage across all evaluated chunks.
        """
        total_atoms = len(nodes)
        completed_atoms = 0
        progress_lock = asyncio.Lock()
        accumulated_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)

        async def process_chunk(
            chunk: list[LinkedAtomGraph],
            current_states: dict[str, AtomExecutionState],
        ) -> dict[str, AtomEvaluationResultDTO]:
            nonlocal completed_atoms, accumulated_usage
            try:
                allow_override = matrix_context.allow_contextual_override if matrix_context else False
                pre_flight_results, undecided_nodes = await ExtractiveSensorService.batch_pre_evaluate(
                    chunk, source_text, locale, allow_contextual_override=allow_override
                )

                if not undecided_nodes:
                    if progress_callback:
                        async with progress_lock:
                            completed_atoms += len(chunk)
                            await progress_callback(completed_atoms, total_atoms)
                    return pre_flight_results

                sem = semaphore if semaphore is not None else asyncio.Semaphore(get_settings().max_concurrent_llm_steps)
                async with sem:
                    llm_results, chunk_usage = await ExtractiveSensorService.evaluate_atom_boolean_batch(
                        nodes=undecided_nodes,
                        executor=self._llm_executor,
                        client=self._llm_client,
                        context_text=source_text,
                        matrix_context=matrix_context,
                        current_states=current_states,
                    )
                accumulated_usage = accumulated_usage + chunk_usage
                res = {**pre_flight_results, **llm_results}
                if progress_callback:
                    async with progress_lock:
                        completed_atoms += len(chunk)
                        await progress_callback(completed_atoms, total_atoms)
                return res
            except Exception as e:
                cause = e.__cause__ or e
                if _is_transient_llm_error(cause):
                    # Bubble up transient network errors for Arq retry.
                    # This raises out of the TaskGroup, throwing an ExceptionGroup
                    # which bypasses TopologicalEvaluator's AppException handler.
                    logger.warning("Transient error detected in chunk, bubbling up: %s", str(cause))
                    raise e

                # Persistent schema extraction failure (ValidationError, etc.)
                # Mark all requested atoms in the batch as SYSTEM_ERROR.
                logger.error("Persistent error in chunk evaluation: %s", str(e))
                res = {
                    node.atom.tda_id: AtomEvaluationResultDTO(
                        status=ExecutionStatus.SYSTEM_ERROR,
                        reasoning=f"EVALUATION_CRASH: {str(e)}",
                        source_quote=None,
                        extensions={},
                    )
                    for node in chunk
                }
                if progress_callback:
                    async with progress_lock:
                        completed_atoms += len(chunk)
                        await progress_callback(completed_atoms, total_atoms)
                return res

        async def batch_evaluation_callback(
            wave_nodes: list[LinkedAtomGraph],
            current_states: dict[str, AtomExecutionState],
        ) -> dict[str, AtomEvaluationResultDTO]:
            """Callback injected into TopologicalEvaluator for wave-based evaluation.

            Slices the topological wave into batches of sensor_batch_size to
            avoid rate limits, evaluating them concurrently via a TaskGroup.

            Args:
                wave_nodes: A list of nodes from a single topological wave.
                current_states: Mapping of tda_id to its current AtomExecutionState.

            Returns:
                A dictionary mapping tda_id to its evaluated AtomEvaluationResultDTO.
            """
            settings = get_settings()
            batch_size = settings.sensor_batch_size
            chunks = [wave_nodes[i : i + batch_size] for i in range(0, len(wave_nodes), batch_size)]

            merged_results: dict[str, AtomEvaluationResultDTO] = {}

            compiled_prompt = MatrixSensorPromptBuilder.build_caching_prefix(source_text, matrix_context)

            provider_name = "vertex_ai"
            model_name = "gemini-1.5-pro"
            if self._llm_client._config is not None:
                provider_name = self._llm_client._config.provider
                model_name = str(self._llm_client._config.model_name)

            await LLMCachingService.pre_cache_document(
                provider_name=provider_name,
                compiled_prompt=compiled_prompt,
                model_name=model_name,
            )

            try:
                async with asyncio.TaskGroup() as tg:
                    tasks = [tg.create_task(process_chunk(chunk, current_states)) for chunk in chunks]

                for task in tasks:
                    merged_results.update(task.result())
            finally:
                try:
                    await LLMCachingService.teardown_workflow_caches(
                        provider_name=provider_name, workflow_run_id=execution_id
                    )
                except (OSError, AppException, ValueError) as teardown_err:
                    logger.error("Error during orchestrator cache teardown: %s", teardown_err)

            return merged_results

        states = await self._topological_evaluator.evaluate_graph(
            nodes=nodes,
            batch_evaluation_callback=batch_evaluation_callback,
        )
        return states, accumulated_usage
