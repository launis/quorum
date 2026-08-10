import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.llm.client import LLMClient
from backend_v2.models.dtos.dag_models import CausalEdge, LinkedAtomGraph
from backend_v2.models.enums import ExecutionStatus
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.enriched_dag_executor import EnrichedDagExecutor


@pytest.fixture
def mock_llm_executor():
    """Mock for LLMTaskExecutor."""
    executor = MagicMock(spec=LLMTaskExecutor)
    executor.execute_structured_task = AsyncMock()
    return executor


@pytest.fixture
def mock_llm_client():
    """Mock for LLMClient."""
    return MagicMock(spec=LLMClient)


def create_mock_node(tda_id: str, depends_on: list[CausalEdge] | None = None) -> LinkedAtomGraph:
    """Helper to create strict Pydantic mock nodes for testing."""
    return LinkedAtomGraph.model_validate(
        {
            "atom": {
                "tda_id": tda_id,
                "reasoning": "mock reasoning",
                "resolved_claim": f"claim for {tda_id}",
                "source_quote": "mock quote",
                "source_id": "chunk_0",
                "source_sequence_index": 0,
            },
            "depends_on": depends_on or [],
        }
    )


@pytest.mark.asyncio
async def test_enriched_dag_happy_path(mock_llm_executor, mock_llm_client):
    """Test that all nodes pass when LLM evaluates claims as True."""
    mock_result = MagicMock()
    mock_result.is_true = True
    mock_llm_executor.execute_structured_task.return_value = (mock_result, None)

    executor = EnrichedDagExecutor(llm_executor=mock_llm_executor, llm_client=mock_llm_client)

    node1 = create_mock_node("tda_1111111111111111")
    node2 = create_mock_node(
        "tda_2222222222222222",
        depends_on=[
            CausalEdge.model_validate(
                {
                    "tda_id": "tda_1111111111111111",
                    "source_id": "chunk_0",
                    "edge_reasoning": "mock",
                    "expected_status": ExecutionStatus.PASSED,
                }
            )
        ],
    )

    result = await executor.execute_graph([node1, node2], "mock context")

    assert result["tda_1111111111111111"].status == ExecutionStatus.PASSED
    assert result["tda_2222222222222222"].status == ExecutionStatus.PASSED


@pytest.mark.asyncio
async def test_enriched_dag_short_circuit_cascade(mock_llm_executor, mock_llm_client):
    """Test that child is N_A when parent fails expectation."""
    mock_result = MagicMock()
    mock_result.is_true = False
    mock_llm_executor.execute_structured_task.return_value = (mock_result, None)

    executor = EnrichedDagExecutor(llm_executor=mock_llm_executor, llm_client=mock_llm_client)

    node1 = create_mock_node("tda_1111111111111111")
    node2 = create_mock_node(
        "tda_2222222222222222",
        depends_on=[
            CausalEdge.model_validate(
                {
                    "tda_id": "tda_1111111111111111",
                    "source_id": "chunk_0",
                    "edge_reasoning": "mock",
                    "expected_status": ExecutionStatus.PASSED,
                }
            )
        ],
    )

    result = await executor.execute_graph([node1, node2], "mock context")

    assert result["tda_1111111111111111"].status == ExecutionStatus.FAILED
    assert result["tda_2222222222222222"].status == ExecutionStatus.N_A
    assert "tda_1111111111111111" in result["tda_2222222222222222"].short_circuit_reason_tda_ids


@pytest.mark.asyncio
async def test_enriched_dag_blocked_cascade(mock_llm_executor, mock_llm_client):
    """Test that child is BLOCKED when parent hits SYSTEM_ERROR."""
    mock_llm_executor.execute_structured_task.side_effect = Exception("API Error")

    executor = EnrichedDagExecutor(llm_executor=mock_llm_executor, llm_client=mock_llm_client)

    node1 = create_mock_node("tda_1111111111111111")
    node2 = create_mock_node(
        "tda_2222222222222222",
        depends_on=[
            CausalEdge.model_validate(
                {
                    "tda_id": "tda_1111111111111111",
                    "source_id": "chunk_0",
                    "edge_reasoning": "mock",
                    "expected_status": ExecutionStatus.PASSED,
                }
            )
        ],
    )

    result = await executor.execute_graph([node1, node2], "mock context")

    assert result["tda_1111111111111111"].status == ExecutionStatus.SYSTEM_ERROR
    assert result["tda_2222222222222222"].status == ExecutionStatus.BLOCKED


@pytest.mark.asyncio
async def test_enriched_dag_deadlock_prevention(mock_llm_executor, mock_llm_client):
    """Test that exceptions do not deadlock the graph evaluation."""
    mock_llm_executor.execute_structured_task.side_effect = Exception("Timeout Simulation")

    executor = EnrichedDagExecutor(llm_executor=mock_llm_executor, llm_client=mock_llm_client)

    node1 = create_mock_node("tda_1111111111111111")
    node2 = create_mock_node(
        "tda_2222222222222222",
        depends_on=[
            CausalEdge.model_validate(
                {
                    "tda_id": "tda_1111111111111111",
                    "source_id": "chunk_0",
                    "edge_reasoning": "mock",
                    "expected_status": ExecutionStatus.PASSED,
                }
            )
        ],
    )

    # Wrap in wait_for to ensure the child doesn't hang indefinitely waiting for parent
    result = await asyncio.wait_for(executor.execute_graph([node1, node2], "mock context"), timeout=2.0)

    assert result["tda_1111111111111111"].status == ExecutionStatus.SYSTEM_ERROR
    assert result["tda_2222222222222222"].status == ExecutionStatus.BLOCKED
