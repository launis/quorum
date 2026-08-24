"""Unit tests for the TDA Engine.

Tests the standalone TDA strategy engine extraction,
including progress routing, Exception ACL, and Fail-Fast validation.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.engine import EngineExecutionRequest, EngineExecutionResult, FlattenedAtom
from backend_v2.models.v2_core import StepRule
from backend_v2.services.orchestrator.engines.tda_engine import TDAEngine
from backend_v2.services.orchestrator.strategies.base import StrategyContext


@pytest.fixture
def mock_compiler() -> MagicMock:
    """Mock for the prompt compiler."""
    return MagicMock()


@pytest.fixture
def base_shuffled_atoms() -> list[FlattenedAtom]:
    """Default matrix atoms for testing."""
    return [
        FlattenedAtom(
            atom_id="tda_12345678",
            question="Test question",
            extraction_rule="rule",
            anchor_target="target",
            is_inverse=False,
        )
    ]


@pytest.fixture
def engine_request(mock_compiler: MagicMock, base_shuffled_atoms: list[FlattenedAtom]) -> EngineExecutionRequest:
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
        shuffled_atoms=base_shuffled_atoms,
    )


@pytest.mark.asyncio
@patch("backend_v2.services.orchestrator.engines.tda_engine.LLMTaskExecutor")
@patch("backend_v2.services.orchestrator.engines.tda_engine.TwoPassAtomizer")
@patch("backend_v2.services.orchestrator.engines.tda_engine.EnrichedDagExecutor")
@patch("backend_v2.services.orchestrator.engines.tda_engine.ResultProjector")
async def test_tda_engine_execute_success(
    mock_projector: MagicMock,
    mock_dag_executor: MagicMock,
    mock_atomizer: MagicMock,
    mock_task_executor: MagicMock,
    engine_request: EngineExecutionRequest,
    mock_compiler: MagicMock,
) -> None:
    """Test successful TDA engine matrix execution and progress callback routing."""
    mock_atomizer_instance = mock_atomizer.return_value
    mock_dag_executor_instance = mock_dag_executor.return_value

    async def mock_execute_phase_0(*args: object, **kwargs: object) -> tuple[str, TokenUsage]:
        progress_cb = kwargs.get("progress_callback")
        if callable(progress_cb):
            await progress_cb(1, 1)
        return "mock_ontology", TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15)

    mock_atomizer_instance.execute_phase_0.side_effect = mock_execute_phase_0

    async def mock_execute_graph(*args: object, **kwargs: object) -> tuple[dict[str, object], TokenUsage]:
        progress_cb = kwargs.get("progress_callback")
        if callable(progress_cb):
            await progress_cb(1, 1)
        return {"state": "done"}, TokenUsage(prompt_tokens=20, completion_tokens=10, total_tokens=30)

    mock_dag_executor_instance.execute_graph.side_effect = mock_execute_graph
    mock_projector.project.return_value = ([], {})

    engine = TDAEngine(prompt_compiler=mock_compiler)
    result = await engine.execute(engine_request)

    assert isinstance(result, EngineExecutionResult)
    assert result.results == []
    assert result.hydrated_references == {}
    assert result.usage is not None
    assert result.usage.total_tokens == (15 + 30)

    mock_atomizer_instance.execute_phase_0.assert_called_once()
    mock_dag_executor_instance.execute_graph.assert_called_once()
    mock_projector.project.assert_called_once()

    assert engine_request.progress_callback is not None
    assert engine_request.progress_callback.call_count == 2
    engine_request.progress_callback.assert_any_call(30, 100)
    engine_request.progress_callback.assert_any_call(100, 100)

    # Verify running event is set
    assert engine_request.running_event is not None
    assert engine_request.running_event.is_set()


@pytest.mark.asyncio
async def test_tda_engine_missing_shuffled_atoms_fails_fast(
    engine_request: EngineExecutionRequest,
    mock_compiler: MagicMock,
) -> None:
    """Test that invoking TDAEngine without shuffled_atoms raises Fail-Fast AppException."""
    req = engine_request.model_copy(update={"shuffled_atoms": None})

    engine = TDAEngine(prompt_compiler=mock_compiler)

    with pytest.raises(AppException) as exc_info:
        await engine.execute(req)

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == "MISSING_MATRIX_ASSERTIONS"
    assert "requires pre-compiled matrix assertions" in str(exc_info.value.message)


@pytest.mark.asyncio
@patch("backend_v2.services.orchestrator.engines.tda_engine.LLMTaskExecutor")
@patch("backend_v2.services.orchestrator.engines.tda_engine.TwoPassAtomizer")
async def test_tda_engine_execute_exception_acl(
    mock_atomizer: MagicMock,
    mock_task_executor: MagicMock,
    engine_request: EngineExecutionRequest,
    mock_compiler: MagicMock,
) -> None:
    """Test that third-party exceptions are wrapped in AppException."""
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
async def test_tda_engine_execute_app_exception_bypass(
    mock_atomizer: MagicMock,
    mock_task_executor: MagicMock,
    engine_request: EngineExecutionRequest,
    mock_compiler: MagicMock,
) -> None:
    """Test that existing AppExceptions are re-raised as-is without double wrapping."""
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


@pytest.mark.asyncio
@patch("backend_v2.services.orchestrator.engines.tda_engine.ResultProjector")
@patch("backend_v2.services.orchestrator.engines.tda_engine.TwoPassAtomizer")
async def test_tda_engine_data_starvation_circuit_breaker_with_shuffled_atoms(
    mock_atomizer: MagicMock,
    mock_projector: MagicMock,
    engine_request: EngineExecutionRequest,
    mock_compiler: MagicMock,
) -> None:
    """Test that data starvation short-circuits matrix evaluation immediately without LLM calls."""
    atom = FlattenedAtom(atom_id="tda_11112222", question="Test rubric question")
    req = engine_request.model_copy(
        update={
            "shuffled_atoms": [atom],
            "context": engine_request.context.model_copy(
                update={
                    "context_variables": {
                        "__GLOBAL_ATOM_BLACKBOARD__": {
                            "atoms_by_input": {},
                            "is_data_starved": True,
                        }
                    }
                }
            ),
        }
    )

    mock_projector.project.return_value = ([], {})

    engine = TDAEngine(prompt_compiler=mock_compiler)
    result = await engine.execute(req)

    assert isinstance(result, EngineExecutionResult)
    assert result.results == []
    assert result.hydrated_references == {}

    # Verify TwoPassAtomizer was NEVER called
    mock_atomizer.assert_not_called()

    # Verify ResultProjector was called with failed states
    mock_projector.project.assert_called_once()
    nodes_arg, states_arg = mock_projector.project.call_args[0][:2]
    assert len(nodes_arg) == 1
    assert nodes_arg[0].atom.tda_id == "tda_11112222"
    assert states_arg["tda_11112222"].status.value == "FAILED"
    assert "Data Starvation" in str(states_arg["tda_11112222"].evaluation_reasoning)
    assert req.progress_callback is not None
    req.progress_callback.assert_called_with(100, 100)
