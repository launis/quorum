"""Enriched DAG Executor.

Combines the TopologicalEvaluator with the ExtractiveSensorService to evaluate
a complete Enriched Atom Graph asynchronously.
"""

import asyncio
import logging

from backend_v2.llm.client import LLMClient
from backend_v2.llm.provider import _is_transient_llm_error
from backend_v2.models.dtos.dag_models import AtomExecutionState, LinkedAtomGraph
from backend_v2.models.enums import ExecutionStatus
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.extractive_sensor_service import ExtractiveSensorService
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
        self, nodes: list[LinkedAtomGraph], source_text: str, locale: str | None = None
    ) -> dict[str, AtomExecutionState]:
        """Executes the complete DAG of atoms.

        Args:
            nodes: The list of validated LinkedAtomGraphs.
            source_text: The original document text for contextual evaluation.
            locale: Optional target locale/language code.

        Returns:
            A dictionary mapping tda_id to its final AtomExecutionState.
        """

        async def process_chunk(
            chunk: list[LinkedAtomGraph],
        ) -> dict[str, tuple[ExecutionStatus, str | None, dict[str, str]]]:
            try:
                pre_flight_results, undecided_nodes = await ExtractiveSensorService.batch_pre_evaluate(
                    chunk, source_text, locale
                )

                if not undecided_nodes:
                    return pre_flight_results

                llm_results = await ExtractiveSensorService.evaluate_atom_boolean_batch(
                    nodes=undecided_nodes,
                    executor=self._llm_executor,
                    client=self._llm_client,
                    context_text=source_text,
                )
                return {**pre_flight_results, **llm_results}
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
                return {
                    node.atom.tda_id: (ExecutionStatus.SYSTEM_ERROR, f"EVALUATION_CRASH: {str(e)}", {})
                    for node in chunk
                }

        async def batch_evaluation_callback(
            wave_nodes: list[LinkedAtomGraph],
        ) -> dict[str, tuple[ExecutionStatus, str | None, dict[str, str]]]:
            """Callback injected into TopologicalEvaluator for wave-based evaluation.

            Slices the topological wave into batches of sensor_batch_size to
            avoid rate limits, evaluating them concurrently via a TaskGroup.

            Args:
                wave_nodes: A list of nodes from a single topological wave.

            Returns:
                A dictionary mapping tda_id to its evaluated ExecutionStatus, reasoning, and extensions.
            """
            settings = get_settings()
            batch_size = settings.sensor_batch_size
            chunks = [wave_nodes[i : i + batch_size] for i in range(0, len(wave_nodes), batch_size)]

            merged_results: dict[str, tuple[ExecutionStatus, str | None, dict[str, str]]] = {}

            async with asyncio.TaskGroup() as tg:
                tasks = [tg.create_task(process_chunk(chunk)) for chunk in chunks]

            for task in tasks:
                merged_results.update(task.result())

            return merged_results

        return await self._topological_evaluator.evaluate_graph(
            nodes=nodes,
            batch_evaluation_callback=batch_evaluation_callback,
        )
