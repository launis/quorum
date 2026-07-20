"""Unit tests for the TDA Engine.

Verifies the integration of the Topological Data Analysis pipeline
components and proper Exception ACL wrapping.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.dtos.dag_models import GlobalOntologyMap
from backend_v2.models.dtos.engine import EngineExecutionRequest
from backend_v2.services.orchestrator.engines.tda_engine import TDAEngine


@pytest.fixture
def mock_compiler() -> MagicMock:
    """Provides a mock PromptCompiler."""
    return MagicMock()


@pytest.fixture
def mock_request() -> MagicMock:
    """Provides a mock EngineExecutionRequest."""
    req = MagicMock(spec=EngineExecutionRequest)
    req.bound_client = MagicMock()
    req.context = MagicMock()
    req.context.execution_id = "test_exec_id"
    req.step = MagicMock()
    req.step.id = "test_step_id"
    req.global_source_text = "test " * 1000
    req.target_locale = "fi"
    req.semaphore = asyncio.Semaphore(1)
    req.running_event = asyncio.Event()
    req.progress_callback = AsyncMock()
    return req


@pytest.mark.asyncio
@patch("backend_v2.services.orchestrator.engines.tda_engine.TwoPassAtomizer")
@patch("backend_v2.services.orchestrator.engines.tda_engine.SlidingWindowLinker")
@patch("backend_v2.services.orchestrator.engines.tda_engine.EnrichedDagExecutor")
@patch("backend_v2.services.orchestrator.engines.tda_engine.ResultProjector")
@patch("backend_v2.services.orchestrator.engines.tda_engine.get_settings")
async def test_tda_engine_success(
    mock_get_settings: MagicMock,
    mock_result_projector: MagicMock,
    mock_dag_executor_cls: MagicMock,
    mock_linker_cls: MagicMock,
    mock_atomizer_cls: MagicMock,
    mock_compiler: MagicMock,
    mock_request: MagicMock,
) -> None:
    """Test successful TDA pipeline execution."""
    settings = MagicMock()
    settings.rag_preflight_chunk_size = 100
    settings.tda_linker_window_size = 4
    settings.tda_linker_overlap = 2
    mock_get_settings.return_value = settings

    atomizer_mock = MagicMock()
    atomizer_mock.execute_phase_0 = AsyncMock(return_value=GlobalOntologyMap(entities=[], macro_rules=[]))
    atomizer_mock.execute_phase_1 = AsyncMock(return_value=[])
    mock_atomizer_cls.return_value = atomizer_mock

    linker_mock = MagicMock()
    linker_mock.link_graph = AsyncMock(return_value=[])
    mock_linker_cls.return_value = linker_mock

    dag_executor_mock = MagicMock()
    dag_executor_mock.execute_graph = AsyncMock(return_value={})
    mock_dag_executor_cls.return_value = dag_executor_mock

    mock_result_projector.project.return_value = ([], {})

    engine = TDAEngine(mock_compiler)
    result = await engine.execute(mock_request)

    assert result is not None
    assert result.results == []
    assert result.hydrated_references == {}

    # Verify all stages were called
    atomizer_mock.execute_phase_0.assert_called_once()
    atomizer_mock.execute_phase_1.assert_called_once()
    linker_mock.link_graph.assert_called_once()
    dag_executor_mock.execute_graph.assert_called_once()


@pytest.mark.asyncio
@patch("backend_v2.services.orchestrator.engines.tda_engine.TwoPassAtomizer")
@patch("backend_v2.services.orchestrator.engines.tda_engine.get_settings")
async def test_tda_engine_app_exception_re_raised(
    mock_get_settings: MagicMock,
    mock_atomizer_cls: MagicMock,
    mock_compiler: MagicMock,
    mock_request: MagicMock,
) -> None:
    """Test that AppException is re-raised without double wrapping."""
    settings = MagicMock()
    settings.rag_preflight_chunk_size = 100
    mock_get_settings.return_value = settings

    atomizer_mock = MagicMock()
    atomizer_mock.execute_phase_0 = AsyncMock(side_effect=AppException(message="Phase 0 error", status_code=400, details={"error_code": "TEST"}))
    mock_atomizer_cls.return_value = atomizer_mock

    engine = TDAEngine(mock_compiler)

    with pytest.raises(AppException) as exc_info:
        await engine.execute(mock_request)

    assert exc_info.value.message == "Phase 0 error"
    assert exc_info.value.details["error_code"] == "TEST"


@pytest.mark.asyncio
@patch("backend_v2.services.orchestrator.engines.tda_engine.TwoPassAtomizer")
@patch("backend_v2.services.orchestrator.engines.tda_engine.get_settings")
async def test_tda_engine_general_exception_wrapped(
    mock_get_settings: MagicMock,
    mock_atomizer_cls: MagicMock,
    mock_compiler: MagicMock,
    mock_request: MagicMock,
) -> None:
    """Test that general Exception is wrapped into AppException."""
    settings = MagicMock()
    settings.rag_preflight_chunk_size = 100
    mock_get_settings.return_value = settings

    atomizer_mock = MagicMock()
    atomizer_mock.execute_phase_0 = AsyncMock(side_effect=ValueError("Native error"))
    mock_atomizer_cls.return_value = atomizer_mock

    engine = TDAEngine(mock_compiler)

    with pytest.raises(AppException) as exc_info:
        await engine.execute(mock_request)

    assert exc_info.value.message == "Native error"
    assert exc_info.value.details["error_code"] == "TDA_ENGINE_ERROR"
