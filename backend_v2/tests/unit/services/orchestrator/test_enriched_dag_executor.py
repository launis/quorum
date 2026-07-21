"""Unit tests for EnrichedDagExecutor."""

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

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

    async def fake_evaluate_graph(
        self_obj: Any, nodes: list[LinkedAtomGraph], batch_evaluation_callback: Any
    ) -> dict[str, Any]:
        nonlocal captured_callback
        captured_callback = batch_evaluation_callback
        return dummy_result

    with patch.object(TopologicalEvaluator, "evaluate_graph", new=fake_evaluate_graph):
        result = await executor.execute_graph(nodes=[], source_text="test text")
        assert result == dummy_result

    assert captured_callback is not None

    from backend_v2.models.dtos.dag_models import ExtractedAtom

    mock_node = LinkedAtomGraph(
        atom=ExtractedAtom(
            tda_id="tda_11111111111111111111111111111111",
            reasoning="reason",
            resolved_claim="claim",
            source_quote="test text",
            source_id="src",
        ),
        depends_on=[],
    )

    with patch(
        "backend_v2.services.orchestrator.enriched_dag_executor.ExtractiveSensorService.evaluate_atom_boolean_batch",
        new_callable=AsyncMock,
    ) as mock_sensor, patch(
        "backend_v2.services.orchestrator.enriched_dag_executor.LLMCachingService.pre_cache_document",
        new_callable=AsyncMock,
    ), patch(
        "backend_v2.services.orchestrator.enriched_dag_executor.LLMCachingService.teardown_workflow_caches",
        new_callable=AsyncMock,
    ):
        mock_sensor.return_value = {"tda_11111111111111111111111111111111": (ExecutionStatus.PASSED, "OK", {})}
        status_dict = await captured_callback([mock_node])

        assert status_dict["tda_11111111111111111111111111111111"][0] == ExecutionStatus.PASSED
        mock_sensor.assert_called_once_with(
            nodes=[mock_node],
            executor=mock_llm_executor,
            client=mock_llm_client,
            context_text="test text",
        )


@pytest.mark.asyncio
async def test_execute_graph_callback_all_pre_flight_and_progress(
    mock_llm_executor: AsyncMock, mock_llm_client: AsyncMock
) -> None:
    """Test when all nodes are decided in pre-flight, and progress callback is used."""
    executor = EnrichedDagExecutor(llm_executor=mock_llm_executor, llm_client=mock_llm_client)

    captured_callback = None
    async def fake_evaluate_graph(
        self_obj: Any, nodes: list[LinkedAtomGraph], batch_evaluation_callback: Any
    ) -> dict[str, Any]:
        nonlocal captured_callback
        captured_callback = batch_evaluation_callback
        return {}

    from backend_v2.models.dtos.dag_models import ExtractedAtom
    mock_node = LinkedAtomGraph(
        atom=ExtractedAtom(
            tda_id="tda_11111111111111111111111111111111",
            reasoning="reason",
            resolved_claim="claim",
            source_quote="test text",
            source_id="src",
        ),
        depends_on=[],
    )

    with patch.object(TopologicalEvaluator, "evaluate_graph", new=fake_evaluate_graph):
        await executor.execute_graph(nodes=[mock_node], source_text="test text")

    assert captured_callback is not None

    progress_calls = []
    async def mock_progress(completed: int, total: int) -> None:
        progress_calls.append((completed, total))

    with patch(
        "backend_v2.services.orchestrator.enriched_dag_executor.ExtractiveSensorService.batch_pre_evaluate",
        new_callable=AsyncMock,
    ) as mock_pre_eval, patch(
        "backend_v2.services.orchestrator.enriched_dag_executor.LLMCachingService.pre_cache_document",
        new_callable=AsyncMock,
    ), patch(
        "backend_v2.services.orchestrator.enriched_dag_executor.LLMCachingService.teardown_workflow_caches",
        new_callable=AsyncMock,
    ):
        mock_pre_eval.return_value = ({"tda_11111111111111111111111111111111": (ExecutionStatus.PASSED, "OK", {})}, [])
        
        # We need to test the progress_callback, but the callback is provided to execute_graph.
        # So we have to re-invoke execute_graph, but patch evaluate_graph to actually run the callback.
        pass

    # Let's do it properly by patching evaluate_graph to run the callback
    async def fake_evaluate_graph_exec(
        self_obj: Any, nodes: list[LinkedAtomGraph], batch_evaluation_callback: Any
    ) -> dict[str, Any]:
        return await batch_evaluation_callback(nodes)

    with patch.object(TopologicalEvaluator, "evaluate_graph", new=fake_evaluate_graph_exec):
        with patch(
            "backend_v2.services.orchestrator.enriched_dag_executor.ExtractiveSensorService.batch_pre_evaluate",
            new_callable=AsyncMock,
        ) as mock_pre_eval, patch(
            "backend_v2.services.orchestrator.enriched_dag_executor.LLMCachingService.pre_cache_document",
            new_callable=AsyncMock,
        ), patch(
            "backend_v2.services.orchestrator.enriched_dag_executor.LLMCachingService.teardown_workflow_caches",
            new_callable=AsyncMock,
        ):
            mock_pre_eval.return_value = ({"tda_11111111111111111111111111111111": (ExecutionStatus.PASSED, "OK", {})}, [])
            result = await executor.execute_graph(
                nodes=[mock_node], source_text="test text", progress_callback=mock_progress
            )
            assert result["tda_11111111111111111111111111111111"][0] == ExecutionStatus.PASSED
            assert progress_calls == [(1, 1)]


@pytest.mark.asyncio
async def test_execute_graph_callback_persistent_error(
    mock_llm_executor: AsyncMock, mock_llm_client: AsyncMock
) -> None:
    """Test when process_chunk raises a persistent error, it's caught and returns SYSTEM_ERROR."""
    executor = EnrichedDagExecutor(llm_executor=mock_llm_executor, llm_client=mock_llm_client)

    async def fake_evaluate_graph_exec(
        self_obj: Any, nodes: list[LinkedAtomGraph], batch_evaluation_callback: Any
    ) -> dict[str, Any]:
        return await batch_evaluation_callback(nodes)

    from backend_v2.models.dtos.dag_models import ExtractedAtom
    mock_node = LinkedAtomGraph(
        atom=ExtractedAtom(
            tda_id="tda_11111111111111111111111111111111",
            reasoning="reason",
            resolved_claim="claim",
            source_quote="test text",
            source_id="src",
        ),
        depends_on=[],
    )

    progress_calls = []
    async def mock_progress(completed: int, total: int) -> None:
        progress_calls.append((completed, total))

    with patch.object(TopologicalEvaluator, "evaluate_graph", new=fake_evaluate_graph_exec):
        with patch(
            "backend_v2.services.orchestrator.enriched_dag_executor.ExtractiveSensorService.batch_pre_evaluate",
            new_callable=AsyncMock,
        ) as mock_pre_eval, patch(
            "backend_v2.services.orchestrator.enriched_dag_executor.LLMCachingService.pre_cache_document",
            new_callable=AsyncMock,
        ), patch(
            "backend_v2.services.orchestrator.enriched_dag_executor.LLMCachingService.teardown_workflow_caches",
            new_callable=AsyncMock,
        ):
            mock_pre_eval.side_effect = ValueError("Some persistent validation error")
            result = await executor.execute_graph(
                nodes=[mock_node], source_text="test text", progress_callback=mock_progress
            )
            assert result["tda_11111111111111111111111111111111"][0] == ExecutionStatus.SYSTEM_ERROR
            assert "Some persistent validation error" in result["tda_11111111111111111111111111111111"][1]
            assert progress_calls == [(1, 1)]


@pytest.mark.asyncio
async def test_execute_graph_callback_transient_error(
    mock_llm_executor: AsyncMock, mock_llm_client: AsyncMock
) -> None:
    """Test when process_chunk raises a transient error, it bubbles up."""
    executor = EnrichedDagExecutor(llm_executor=mock_llm_executor, llm_client=mock_llm_client)

    async def fake_evaluate_graph_exec(
        self_obj: Any, nodes: list[LinkedAtomGraph], batch_evaluation_callback: Any
    ) -> dict[str, Any]:
        return await batch_evaluation_callback(nodes)

    from backend_v2.models.dtos.dag_models import ExtractedAtom
    mock_node = LinkedAtomGraph(
        atom=ExtractedAtom(
            tda_id="tda_11111111111111111111111111111111",
            reasoning="reason",
            resolved_claim="claim",
            source_quote="test text",
            source_id="src",
        ),
        depends_on=[],
    )

    with patch.object(TopologicalEvaluator, "evaluate_graph", new=fake_evaluate_graph_exec):
        with patch(
            "backend_v2.services.orchestrator.enriched_dag_executor.ExtractiveSensorService.batch_pre_evaluate",
            new_callable=AsyncMock,
        ) as mock_pre_eval, patch(
            "backend_v2.services.orchestrator.enriched_dag_executor._is_transient_llm_error",
            return_value=True,
        ), patch(
            "backend_v2.services.orchestrator.enriched_dag_executor.LLMCachingService.pre_cache_document",
            new_callable=AsyncMock,
        ), patch(
            "backend_v2.services.orchestrator.enriched_dag_executor.LLMCachingService.teardown_workflow_caches",
            new_callable=AsyncMock,
        ) as mock_teardown:
            mock_pre_eval.side_effect = ValueError("Transient network error")
            mock_teardown.side_effect = ValueError("Teardown error") # Also cover the finally block exception handling
            
            with pytest.raises(ExceptionGroup) as exc_info:
                await executor.execute_graph(nodes=[mock_node], source_text="test text")
            
            assert len(exc_info.value.exceptions) == 1
            assert str(exc_info.value.exceptions[0]) == "Transient network error"
