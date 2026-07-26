"""Unit tests for the TDA Engine.

Tests the standalone TDA strategy engine extraction,
including progress routing and the Exception Anti-Corruption Layer (ACL).
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.dtos.engine import EngineExecutionRequest, EngineExecutionResult
from backend_v2.models.v2_core import StepRule
from backend_v2.services.orchestrator.engines.tda_engine import TDAEngine
from backend_v2.services.orchestrator.strategies.base import StrategyContext


@pytest.fixture
def mock_compiler():
    """Mock for the prompt compiler."""
    return MagicMock()


@pytest.fixture
def engine_request(mock_compiler):
    """Mock EngineExecutionRequest for tests."""
    from backend_v2.llm.client import LLMClient

    return EngineExecutionRequest(
        bound_client=MagicMock(spec=LLMClient),
        compiled_schema=None,
        hydrated_messages=None,
        system_prompt="Test System Prompt",
        step=StepRule(id="step_a1b2c3d4e5f6a7b8", task_blueprint="task_123", depends_on=[], input_mappings={}),
        context=StrategyContext(
            execution_id="exe_abc12345",
            workflow_id="wor_xyz12345",
            metadata={},
        ),
        global_source_text="Test source text",
        target_locale="fi",
        semaphore=asyncio.Semaphore(1),
        running_event=asyncio.Event(),
        progress_callback=AsyncMock(),
        trace_callback=AsyncMock(),
        prompt_compiler=mock_compiler,
    )


@pytest.mark.asyncio
@patch("backend_v2.services.orchestrator.engines.tda_engine.LLMTaskExecutor")
@patch("backend_v2.services.orchestrator.engines.tda_engine.TwoPassAtomizer")
@patch("backend_v2.services.orchestrator.engines.tda_engine.SlidingWindowLinker")
@patch("backend_v2.services.orchestrator.engines.tda_engine.EnrichedDagExecutor")
@patch("backend_v2.services.orchestrator.engines.tda_engine.ResultProjector")
@patch("backend_v2.services.orchestrator.engines.tda_engine.get_settings")
async def test_tda_engine_execute_success(
    mock_get_settings,
    mock_projector,
    mock_dag_executor,
    mock_linker,
    mock_atomizer,
    mock_task_executor,
    engine_request,
    mock_compiler,
):
    """Test successful TDA engine execution and progress callback routing."""
    settings = mock_get_settings.return_value
    settings.tda_linker_window_size = 4
    settings.tda_linker_overlap = 2
    settings.rag_preflight_chunk_size = 1000

    mock_atomizer_instance = mock_atomizer.return_value
    mock_linker_instance = mock_linker.return_value
    mock_dag_executor_instance = mock_dag_executor.return_value

    async def mock_execute_phase_0(*args, **kwargs):
        progress_cb = kwargs.get("progress_callback")
        if progress_cb:
            await progress_cb(1, 1)
        return {"ontology": "mock"}

    mock_atomizer_instance.execute_phase_0.side_effect = mock_execute_phase_0

    async def mock_execute_phase_1(*args, **kwargs):
        progress_cb = kwargs.get("progress_callback")
        if progress_cb:
            await progress_cb(1, 1)
        atom = MagicMock()
        atom.source_sequence_index = 0
        return [atom]

    mock_atomizer_instance.execute_phase_1.side_effect = mock_execute_phase_1

    async def mock_link_graph(*args, **kwargs):
        progress_cb = kwargs.get("progress_callback")
        if progress_cb:
            await progress_cb(1, 1)
        return ["node1"]

    mock_linker_instance.link_graph.side_effect = mock_link_graph

    async def mock_execute_graph(*args, **kwargs):
        progress_cb = kwargs.get("progress_callback")
        if progress_cb:
            await progress_cb(1, 1)
        return {"state": "done"}

    mock_dag_executor_instance.execute_graph.side_effect = mock_execute_graph

    mock_projector.project.return_value = ([], {})

    engine = TDAEngine(prompt_compiler=mock_compiler)
    result = await engine.execute(engine_request)

    assert isinstance(result, EngineExecutionResult)
    assert result.results == []
    assert result.hydrated_references == {}

    mock_atomizer_instance.execute_phase_0.assert_called_once()
    mock_atomizer_instance.execute_phase_1.assert_called_once()
    mock_linker_instance.link_graph.assert_called_once()
    mock_dag_executor_instance.execute_graph.assert_called_once()
    mock_projector.project.assert_called_once()

    assert engine_request.progress_callback.call_count == 4
    engine_request.progress_callback.assert_any_call(15, 100)
    engine_request.progress_callback.assert_any_call(35, 100)
    engine_request.progress_callback.assert_any_call(60, 100)
    engine_request.progress_callback.assert_any_call(100, 100)

    # Verify running event is set
    assert engine_request.running_event.is_set()


@pytest.mark.asyncio
@patch("backend_v2.services.orchestrator.engines.tda_engine.LLMTaskExecutor")
@patch("backend_v2.services.orchestrator.engines.tda_engine.TwoPassAtomizer")
@patch("backend_v2.services.orchestrator.engines.tda_engine.EnrichedDagExecutor")
@patch("backend_v2.services.orchestrator.engines.tda_engine.ResultProjector")
@patch("backend_v2.services.orchestrator.engines.tda_engine.get_settings")
async def test_tda_engine_matrix_path(
    mock_get_settings,
    mock_projector,
    mock_dag_executor,
    mock_atomizer,
    mock_task_executor,
    engine_request,
    mock_compiler,
):
    """Test successful TDA engine matrix execution path."""
    from backend_v2.models.dtos.engine import FlattenedAtom

    engine_request = engine_request.model_copy(update={
        "shuffled_atoms": [
            FlattenedAtom(
                atom_id="tda_12345678",
                question="Test question",
                extraction_rule="rule",
                anchor_target="target",
                is_inverse=False,
            )
        ]
    })

    mock_atomizer_instance = mock_atomizer.return_value
    mock_dag_executor_instance = mock_dag_executor.return_value

    async def mock_execute_phase_0(*args, **kwargs):
        progress_cb = kwargs.get("progress_callback")
        if progress_cb:
            await progress_cb(1, 1)
        return "mock_ontology"

    mock_atomizer_instance.execute_phase_0.side_effect = mock_execute_phase_0

    async def mock_execute_graph(*args, **kwargs):
        progress_cb = kwargs.get("progress_callback")
        if progress_cb:
            await progress_cb(1, 1)
        return {"state": "done"}

    mock_dag_executor_instance.execute_graph.side_effect = mock_execute_graph

    mock_projector.project.return_value = ([], {})

    engine = TDAEngine(prompt_compiler=mock_compiler)
    result = await engine.execute(engine_request)

    assert isinstance(result, EngineExecutionResult)
    mock_atomizer_instance.execute_phase_0.assert_called_once()
    # Phase 1 and Linker must be skipped for matrix
    assert not mock_atomizer_instance.execute_phase_1.called
    mock_dag_executor_instance.execute_graph.assert_called_once()
    
    nodes_arg = mock_dag_executor_instance.execute_graph.call_args[0][0]
    assert len(nodes_arg) == 1
    assert nodes_arg[0].atom.tda_id == "tda_12345678"
    assert nodes_arg[0].atom.is_logical_deduction is True
    assert nodes_arg[0].depends_on == []
    
    assert engine_request.progress_callback.call_count == 2
    engine_request.progress_callback.assert_any_call(30, 100)
    engine_request.progress_callback.assert_any_call(100, 100)



@pytest.mark.asyncio
@patch("backend_v2.services.orchestrator.engines.tda_engine.LLMTaskExecutor")
@patch("backend_v2.services.orchestrator.engines.tda_engine.TwoPassAtomizer")
@patch("backend_v2.services.orchestrator.engines.tda_engine.get_settings")
async def test_tda_engine_execute_exception_acl(
    mock_get_settings,
    mock_atomizer,
    mock_task_executor,
    engine_request,
    mock_compiler,
):
    """Test that third-party exceptions are wrapped in AppException."""
    settings = mock_get_settings.return_value
    settings.tda_linker_window_size = 4
    settings.tda_linker_overlap = 2
    settings.rag_preflight_chunk_size = 1000

    mock_atomizer_instance = mock_atomizer.return_value
    mock_atomizer_instance.execute_phase_0.side_effect = Exception("Third-party crash")

    engine = TDAEngine(prompt_compiler=mock_compiler)

    with pytest.raises(AppException) as exc_info:
        await engine.execute(engine_request)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == "TDA_ENGINE_ERROR"
    assert str(exc_info.value.message) == "Third-party crash"


@pytest.mark.asyncio
@patch("backend_v2.services.orchestrator.engines.tda_engine.LLMTaskExecutor")
@patch("backend_v2.services.orchestrator.engines.tda_engine.TwoPassAtomizer")
@patch("backend_v2.services.orchestrator.engines.tda_engine.get_settings")
async def test_tda_engine_execute_app_exception_bypass(
    mock_get_settings,
    mock_atomizer,
    mock_task_executor,
    engine_request,
    mock_compiler,
):
    """Test that existing AppExceptions are re-raised as-is without double wrapping."""
    settings = mock_get_settings.return_value
    settings.tda_linker_window_size = 4
    settings.tda_linker_overlap = 2
    settings.rag_preflight_chunk_size = 1000

    mock_atomizer_instance = mock_atomizer.return_value
    mock_atomizer_instance.execute_phase_0.side_effect = AppException(
        message="Native crash", status_code=400, details={"error_code": "NATIVE_ERROR"}
    )

    engine = TDAEngine(prompt_compiler=mock_compiler)

    with pytest.raises(AppException) as exc_info:
        await engine.execute(engine_request)

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == "NATIVE_ERROR"
    assert str(exc_info.value.message) == "Native crash"
