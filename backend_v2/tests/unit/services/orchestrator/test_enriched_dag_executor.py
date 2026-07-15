"""Unit tests for EnrichedDagExecutor."""

import pytest
from typing import Any
from unittest.mock import AsyncMock, patch

from backend_v2.models.dtos.dag_models import LinkedAtomGraph
from backend_v2.models.enums import ExecutionStatus
from backend_v2.services.orchestrator.enriched_dag_executor import EnrichedDagExecutor
from backend_v2.services.orchestrator.topological_evaluator import TopologicalEvaluator


@pytest.fixture
def mock_llm_executor() -> AsyncMock:
    """Fixture for LLMTaskExecutor."""
    return AsyncMock()


@pytest.fixture
def mock_llm_client() -> AsyncMock:
    """Fixture for LLMClient."""
    return AsyncMock()


@pytest.mark.asyncio
async def test_execute_graph_callback(mock_llm_executor: AsyncMock, mock_llm_client: AsyncMock) -> None:
    """Test execute_graph correctly forwards to TopologicalEvaluator and callback works."""
    executor = EnrichedDagExecutor(llm_executor=mock_llm_executor, llm_client=mock_llm_client)

    dummy_result: dict[str, Any] = {}
    captured_callback = None

    async def fake_evaluate_graph(self_obj: Any, nodes: list[LinkedAtomGraph], evaluation_callback: Any) -> dict[str, Any]:
        nonlocal captured_callback
        captured_callback = evaluation_callback
        return dummy_result

    with patch.object(TopologicalEvaluator, "evaluate_graph", new=fake_evaluate_graph):
        result = await executor.execute_graph(nodes=[], source_text="test text")
        assert result == dummy_result

    assert captured_callback is not None

    mock_node = AsyncMock(spec=LinkedAtomGraph)
    with patch(
        "backend_v2.services.orchestrator.enriched_dag_executor.ExtractiveSensorService.evaluate_atom_boolean",
        new_callable=AsyncMock,
    ) as mock_sensor:
        mock_sensor.return_value = ExecutionStatus.PASSED
        status = await captured_callback(mock_node)
        assert status == ExecutionStatus.PASSED
        mock_sensor.assert_called_once_with(
            node=mock_node,
            executor=mock_llm_executor,
            client=mock_llm_client,
            context_text="test text",
        )
