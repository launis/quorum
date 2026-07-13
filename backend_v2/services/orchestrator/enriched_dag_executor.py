"""Enriched DAG Executor.

Combines the TopologicalEvaluator with the ExtractiveSensorService to evaluate
a complete Enriched Atom Graph asynchronously.
"""

from backend_v2.llm.client import LLMClient
from backend_v2.models.dtos.dag_models import AtomExecutionState, LinkedAtomGraph
from backend_v2.models.enums import ExecutionStatus
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.extractive_sensor_service import ExtractiveSensorService
from backend_v2.services.orchestrator.topological_evaluator import TopologicalEvaluator


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

    async def execute_graph(self, nodes: list[LinkedAtomGraph], source_text: str) -> dict[str, AtomExecutionState]:
        """Executes the complete DAG of atoms.

        Args:
            nodes: The list of validated LinkedAtomGraphs.
            source_text: The original document text for contextual evaluation.

        Returns:
            A dictionary mapping tda_id to its final AtomExecutionState.
        """

        async def evaluation_callback(node: LinkedAtomGraph) -> ExecutionStatus:
            """Callback injected into TopologicalEvaluator for node evaluation."""
            return await ExtractiveSensorService.evaluate_atom_boolean(
                node=node,
                executor=self._llm_executor,
                client=self._llm_client,
                context_text=source_text,
            )

        return await self._topological_evaluator.evaluate_graph(
            nodes=nodes,
            evaluation_callback=evaluation_callback,
        )
