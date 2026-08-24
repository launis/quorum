"""ISTQB Test Suite for Matrix Causal DAG Integration in TDAEngine.

Covers all 5 ISTQB Equivalence Partitions:
1. Happy Path - Clean Short-Circuit: Root fails -> Child short-circuited to N_A.
2. Negative - Phantom Edge Isolation: Missing parent -> Evaluator assigns SYSTEM_ERROR (UNRESOLVED_DEPENDENCY).
3. Negative - Cyclic Graph Isolation: Circular dependencies -> SYSTEM_ERROR (CYCLIC_DEPENDENCY_DETECTED).
4. Negative - Multi-Level Transitive Sampling Closure: Data Starvation retains depends_on edges.
5. Negative - Multi-Parent Conflicting Dependencies: 1 passed parent + 1 failed parent -> N_A.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.dag_models import AtomExecutionState, CausalEdge
from backend_v2.models.dtos.engine import EngineExecutionRequest, FlattenedAtom
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.v2_core import AtomResultDTO, ErrorDetailsDTO, StepRule
from backend_v2.services.orchestrator.engines.tda_engine import TDAEngine
from backend_v2.services.orchestrator.strategies.base import StrategyContext


@pytest.fixture
def mock_compiler() -> MagicMock:
    return MagicMock()


@pytest.fixture
def base_engine_request(mock_compiler: MagicMock) -> EngineExecutionRequest:
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
@patch("backend_v2.services.orchestrator.engines.tda_engine.EnrichedDagExecutor")
@patch("backend_v2.services.orchestrator.engines.tda_engine.ResultProjector")
@patch("backend_v2.services.orchestrator.engines.tda_engine.get_settings")
async def test_istqb_partition_1_happy_path_clean_short_circuit(
    mock_get_settings: MagicMock,
    mock_projector: MagicMock,
    mock_dag_executor: MagicMock,
    mock_atomizer: MagicMock,
    mock_task_executor: MagicMock,
    base_engine_request: EngineExecutionRequest,
    mock_compiler: MagicMock,
) -> None:
    """Partition 1: When Root A fails, dependent Child B short-circuits to N_A in the matrix DAG path."""
    parent_id = "tda_00000000000000000000000000000001"
    child_id = "tda_00000000000000000000000000000002"

    edge = CausalEdge(
        edge_reasoning="Parent must pass for child to be evaluated.",
        tda_id=parent_id,
        source_id="matrix_eval",
        expected_status=ExecutionStatus.PASSED,
    )

    atom_parent = FlattenedAtom(
        atom_id=parent_id,
        question="Root Criterion A",
        extraction_rule="Extract A",
        anchor_target="target_A",
        is_inverse=False,
        depends_on=(),
    )
    atom_child = FlattenedAtom(
        atom_id=child_id,
        question="Child Criterion B",
        extraction_rule="Extract B",
        anchor_target="target_B",
        is_inverse=False,
        depends_on=(edge,),
    )

    req = base_engine_request.model_copy(
        update={
            "shuffled_atoms": [atom_parent, atom_child],
            "matrix_block_id": "blk_0123456789abcdef0123456789abcdef",
        }
    )

    mock_atomizer_instance = mock_atomizer.return_value
    mock_dag_executor_instance = mock_dag_executor.return_value

    async def mock_execute_phase_0(*args: object, **kwargs: object) -> tuple[str, TokenUsage]:
        return "mock_ontology", TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15)

    mock_atomizer_instance.execute_phase_0.side_effect = mock_execute_phase_0

    async def mock_execute_graph(*args: object, **kwargs: object) -> tuple[dict[str, AtomExecutionState], TokenUsage]:
        return (
            {
                parent_id: AtomExecutionState(
                    tda_id=parent_id,
                    status=ExecutionStatus.FAILED,
                    evaluation_reasoning="Root criterion evidence not found in source text.",
                    extensions={},
                ),
                child_id: AtomExecutionState(
                    tda_id=child_id,
                    status=ExecutionStatus.N_A,
                    evaluation_reasoning=f"Dependency prerequisite not met for parent '{parent_id}'",
                    extensions={},
                ),
            },
            TokenUsage(prompt_tokens=20, completion_tokens=10, total_tokens=30),
        )

    mock_dag_executor_instance.execute_graph.side_effect = mock_execute_graph

    mock_projector.project.return_value = (
        [
            AtomResultDTO(
                tda_id=parent_id,
                status=ExecutionStatus.FAILED,
                evaluation_reasoning="Root criterion evidence not found in source text.",
                depends_on_tda_ids=[],
                short_circuit_reason_tda_ids=[],
            ),
            AtomResultDTO(
                tda_id=child_id,
                status=ExecutionStatus.N_A,
                evaluation_reasoning=f"Dependency prerequisite not met for parent '{parent_id}'",
                depends_on_tda_ids=[parent_id],
                short_circuit_reason_tda_ids=[parent_id],
            ),
        ],
        {},
    )

    engine = TDAEngine(prompt_compiler=mock_compiler)
    result = await engine.execute(req)

    # Verify LinkedAtomGraph nodes received the depends_on edge
    nodes_arg = mock_dag_executor_instance.execute_graph.call_args[0][0]
    assert len(nodes_arg) == 2
    assert nodes_arg[0].atom.tda_id == parent_id
    assert nodes_arg[0].depends_on == []
    assert nodes_arg[1].atom.tda_id == child_id
    assert len(nodes_arg[1].depends_on) == 1
    assert nodes_arg[1].depends_on[0].tda_id == parent_id

    assert len(result.results) == 2
    child_res = next(r for r in result.results if r.tda_id == child_id)
    assert child_res.status == ExecutionStatus.N_A
    assert child_res.short_circuit_reason_tda_ids == [parent_id]


@pytest.mark.asyncio
@patch("backend_v2.services.orchestrator.engines.tda_engine.LLMTaskExecutor")
@patch("backend_v2.services.orchestrator.engines.tda_engine.TwoPassAtomizer")
@patch("backend_v2.services.orchestrator.engines.tda_engine.EnrichedDagExecutor")
@patch("backend_v2.services.orchestrator.engines.tda_engine.ResultProjector")
@patch("backend_v2.services.orchestrator.engines.tda_engine.get_settings")
async def test_istqb_partition_2_phantom_edge_isolation(
    mock_get_settings: MagicMock,
    mock_projector: MagicMock,
    mock_dag_executor: MagicMock,
    mock_atomizer: MagicMock,
    mock_task_executor: MagicMock,
    base_engine_request: EngineExecutionRequest,
    mock_compiler: MagicMock,
) -> None:
    """Partition 2: Child B specifies dependency on missing/unsampled parent -> SYSTEM_ERROR."""
    child_id = "tda_00000000000000000000000000000002"
    missing_parent_id = "tda_99999999999999999999999999999999"

    edge = CausalEdge(
        edge_reasoning="Depends on phantom unsampled parent.",
        tda_id=missing_parent_id,
        source_id="matrix_eval",
        expected_status=ExecutionStatus.PASSED,
    )

    atom_child = FlattenedAtom(
        atom_id=child_id,
        question="Child Criterion with Missing Parent",
        extraction_rule="Extract B",
        anchor_target="target_B",
        is_inverse=False,
        depends_on=(edge,),
    )

    req = base_engine_request.model_copy(
        update={
            "shuffled_atoms": [atom_child],
            "matrix_block_id": "blk_0123456789abcdef0123456789abcdef",
        }
    )

    mock_atomizer_instance = mock_atomizer.return_value
    mock_dag_executor_instance = mock_dag_executor.return_value

    async def mock_execute_phase_0(*args: object, **kwargs: object) -> tuple[str, TokenUsage]:
        return "mock_ontology", TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15)

    mock_atomizer_instance.execute_phase_0.side_effect = mock_execute_phase_0

    async def mock_execute_graph(*args: object, **kwargs: object) -> tuple[dict[str, AtomExecutionState], TokenUsage]:
        return (
            {
                child_id: AtomExecutionState(
                    tda_id=child_id,
                    status=ExecutionStatus.SYSTEM_ERROR,
                    evaluation_reasoning=f"UNRESOLVED_DEPENDENCY: Parent '{missing_parent_id}' not found in graph.",
                    extensions={},
                ),
            },
            TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
        )

    mock_dag_executor_instance.execute_graph.side_effect = mock_execute_graph

    mock_projector.project.return_value = (
        [
            AtomResultDTO(
                tda_id=child_id,
                status=ExecutionStatus.SYSTEM_ERROR,
                evaluation_reasoning=f"UNRESOLVED_DEPENDENCY: Parent '{missing_parent_id}' not found in graph.",
                error_details=ErrorDetailsDTO(
                    error_code="UNRESOLVED_DEPENDENCY",
                    message=f"Parent '{missing_parent_id}' not found in graph.",
                ),
                depends_on_tda_ids=[missing_parent_id],
                short_circuit_reason_tda_ids=[],
            ),
        ],
        {},
    )

    engine = TDAEngine(prompt_compiler=mock_compiler)
    result = await engine.execute(req)

    nodes_arg = mock_dag_executor_instance.execute_graph.call_args[0][0]
    assert len(nodes_arg) == 1
    assert nodes_arg[0].depends_on[0].tda_id == missing_parent_id

    res = result.results[0]
    assert res.status == ExecutionStatus.SYSTEM_ERROR
    assert "UNRESOLVED_DEPENDENCY" in res.evaluation_reasoning


@pytest.mark.asyncio
@patch("backend_v2.services.orchestrator.engines.tda_engine.LLMTaskExecutor")
@patch("backend_v2.services.orchestrator.engines.tda_engine.TwoPassAtomizer")
@patch("backend_v2.services.orchestrator.engines.tda_engine.EnrichedDagExecutor")
@patch("backend_v2.services.orchestrator.engines.tda_engine.ResultProjector")
@patch("backend_v2.services.orchestrator.engines.tda_engine.get_settings")
async def test_istqb_partition_3_cyclic_graph_isolation(
    mock_get_settings: MagicMock,
    mock_projector: MagicMock,
    mock_dag_executor: MagicMock,
    mock_atomizer: MagicMock,
    mock_task_executor: MagicMock,
    base_engine_request: EngineExecutionRequest,
    mock_compiler: MagicMock,
) -> None:
    """Partition 3: Circular dependency A -> B -> A isolated as SYSTEM_ERROR while independent C evaluates normally."""
    id_a = "tda_0000000000000000000000000000000a"
    id_b = "tda_0000000000000000000000000000000b"
    id_c = "tda_0000000000000000000000000000000c"

    edge_b_to_a = CausalEdge(edge_reasoning="A depends on B", tda_id=id_b, source_id="src", expected_status=ExecutionStatus.PASSED)
    edge_a_to_b = CausalEdge(edge_reasoning="B depends on A", tda_id=id_a, source_id="src", expected_status=ExecutionStatus.PASSED)

    atom_a = FlattenedAtom(atom_id=id_a, question="A", extraction_rule="", anchor_target="", is_inverse=False, depends_on=(edge_b_to_a,))
    atom_b = FlattenedAtom(atom_id=id_b, question="B", extraction_rule="", anchor_target="", is_inverse=False, depends_on=(edge_a_to_b,))
    atom_c = FlattenedAtom(atom_id=id_c, question="Independent C", extraction_rule="", anchor_target="", is_inverse=False, depends_on=())

    req = base_engine_request.model_copy(
        update={
            "shuffled_atoms": [atom_a, atom_b, atom_c],
            "matrix_block_id": "blk_0123456789abcdef0123456789abcdef",
        }
    )

    mock_atomizer_instance = mock_atomizer.return_value
    mock_dag_executor_instance = mock_dag_executor.return_value

    async def mock_execute_phase_0(*args: object, **kwargs: object) -> tuple[str, TokenUsage]:
        return "mock_ontology", TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15)

    mock_atomizer_instance.execute_phase_0.side_effect = mock_execute_phase_0

    async def mock_execute_graph(*args: object, **kwargs: object) -> tuple[dict[str, AtomExecutionState], TokenUsage]:
        return (
            {
                id_a: AtomExecutionState(
                    tda_id=id_a,
                    status=ExecutionStatus.SYSTEM_ERROR,
                    evaluation_reasoning="CYCLIC_DEPENDENCY_DETECTED: Node is part of a circular loop.",
                    extensions={},
                ),
                id_b: AtomExecutionState(
                    tda_id=id_b,
                    status=ExecutionStatus.SYSTEM_ERROR,
                    evaluation_reasoning="CYCLIC_DEPENDENCY_DETECTED: Node is part of a circular loop.",
                    extensions={},
                ),
                id_c: AtomExecutionState(
                    tda_id=id_c,
                    status=ExecutionStatus.PASSED,
                    evaluation_reasoning="Independent node passed.",
                    extensions={},
                ),
            },
            TokenUsage(prompt_tokens=30, completion_tokens=15, total_tokens=45),
        )

    mock_dag_executor_instance.execute_graph.side_effect = mock_execute_graph

    mock_projector.project.return_value = (
        [
            AtomResultDTO(
                tda_id=id_a,
                status=ExecutionStatus.SYSTEM_ERROR,
                evaluation_reasoning="CYCLIC_DEPENDENCY_DETECTED: Node is part of a circular loop.",
                error_details=ErrorDetailsDTO(
                    error_code="CYCLIC_DEPENDENCY_DETECTED",
                    message="Node is part of a circular loop.",
                ),
                depends_on_tda_ids=[id_b],
                short_circuit_reason_tda_ids=[],
            ),
            AtomResultDTO(
                tda_id=id_b,
                status=ExecutionStatus.SYSTEM_ERROR,
                evaluation_reasoning="CYCLIC_DEPENDENCY_DETECTED: Node is part of a circular loop.",
                error_details=ErrorDetailsDTO(
                    error_code="CYCLIC_DEPENDENCY_DETECTED",
                    message="Node is part of a circular loop.",
                ),
                depends_on_tda_ids=[id_a],
                short_circuit_reason_tda_ids=[],
            ),
            AtomResultDTO(
                tda_id=id_c,
                status=ExecutionStatus.PASSED,
                source_quote="Direct factual observation verified in text.",
                evaluation_reasoning="Independent node passed.",
                depends_on_tda_ids=[],
                short_circuit_reason_tda_ids=[],
            ),
        ],
        {},
    )

    engine = TDAEngine(prompt_compiler=mock_compiler)
    result = await engine.execute(req)

    res_a = next(r for r in result.results if r.tda_id == id_a)
    res_b = next(r for r in result.results if r.tda_id == id_b)
    res_c = next(r for r in result.results if r.tda_id == id_c)

    assert res_a.status == ExecutionStatus.SYSTEM_ERROR
    assert "CYCLIC_DEPENDENCY_DETECTED" in res_a.evaluation_reasoning
    assert res_b.status == ExecutionStatus.SYSTEM_ERROR
    assert "CYCLIC_DEPENDENCY_DETECTED" in res_b.evaluation_reasoning
    assert res_c.status == ExecutionStatus.PASSED


@pytest.mark.asyncio
@patch("backend_v2.services.orchestrator.engines.tda_engine.ResultProjector")
@patch("backend_v2.services.orchestrator.engines.tda_engine.TwoPassAtomizer")
async def test_istqb_partition_4_data_starvation_propagates_depends_on(
    mock_atomizer: MagicMock,
    mock_projector: MagicMock,
    base_engine_request: EngineExecutionRequest,
    mock_compiler: MagicMock,
) -> None:
    """Partition 4: When Data Starvation triggers, LinkedAtomGraph nodes correctly retain depends_on."""
    parent_id = "tda_00000000000000000000000000000001"
    child_id = "tda_00000000000000000000000000000002"

    edge = CausalEdge(
        edge_reasoning="Parent prerequisite",
        tda_id=parent_id,
        source_id="src",
        expected_status=ExecutionStatus.PASSED,
    )

    atom_parent = FlattenedAtom(atom_id=parent_id, question="A", extraction_rule="", anchor_target="", is_inverse=False, depends_on=())
    atom_child = FlattenedAtom(atom_id=child_id, question="B", extraction_rule="", anchor_target="", is_inverse=False, depends_on=(edge,))

    req = base_engine_request.model_copy(
        update={
            "shuffled_atoms": [atom_parent, atom_child],
            "context": base_engine_request.context.model_copy(
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

    assert isinstance(result, object)
    mock_projector.project.assert_called_once()
    nodes_arg, states_arg = mock_projector.project.call_args[0][:2]
    assert len(nodes_arg) == 2
    assert nodes_arg[0].depends_on == []
    assert len(nodes_arg[1].depends_on) == 1
    assert nodes_arg[1].depends_on[0].tda_id == parent_id


@pytest.mark.asyncio
@patch("backend_v2.services.orchestrator.engines.tda_engine.LLMTaskExecutor")
@patch("backend_v2.services.orchestrator.engines.tda_engine.TwoPassAtomizer")
@patch("backend_v2.services.orchestrator.engines.tda_engine.EnrichedDagExecutor")
@patch("backend_v2.services.orchestrator.engines.tda_engine.ResultProjector")
@patch("backend_v2.services.orchestrator.engines.tda_engine.get_settings")
async def test_istqb_partition_5_multi_parent_conflicting_dependencies(
    mock_get_settings: MagicMock,
    mock_projector: MagicMock,
    mock_dag_executor: MagicMock,
    mock_atomizer: MagicMock,
    mock_task_executor: MagicMock,
    base_engine_request: EngineExecutionRequest,
    mock_compiler: MagicMock,
) -> None:
    """Partition 5: Child C depends on Parent A (PASSED) and Parent B (FAILED) -> Child C short-circuits to N_A with B attributed."""
    id_a = "tda_0000000000000000000000000000000a"
    id_b = "tda_0000000000000000000000000000000b"
    id_c = "tda_0000000000000000000000000000000c"

    edge_a = CausalEdge(edge_reasoning="A must pass", tda_id=id_a, source_id="src", expected_status=ExecutionStatus.PASSED)
    edge_b = CausalEdge(edge_reasoning="B must pass", tda_id=id_b, source_id="src", expected_status=ExecutionStatus.PASSED)

    atom_a = FlattenedAtom(atom_id=id_a, question="A", extraction_rule="", anchor_target="", is_inverse=False, depends_on=())
    atom_b = FlattenedAtom(atom_id=id_b, question="B", extraction_rule="", anchor_target="", is_inverse=False, depends_on=())
    atom_c = FlattenedAtom(atom_id=id_c, question="C", extraction_rule="", anchor_target="", is_inverse=False, depends_on=(edge_a, edge_b))

    req = base_engine_request.model_copy(
        update={
            "shuffled_atoms": [atom_a, atom_b, atom_c],
            "matrix_block_id": "blk_0123456789abcdef0123456789abcdef",
        }
    )

    mock_atomizer_instance = mock_atomizer.return_value
    mock_dag_executor_instance = mock_dag_executor.return_value

    async def mock_execute_phase_0(*args: object, **kwargs: object) -> tuple[str, TokenUsage]:
        return "mock_ontology", TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15)

    mock_atomizer_instance.execute_phase_0.side_effect = mock_execute_phase_0

    async def mock_execute_graph(*args: object, **kwargs: object) -> tuple[dict[str, AtomExecutionState], TokenUsage]:
        return (
            {
                id_a: AtomExecutionState(
                    tda_id=id_a,
                    status=ExecutionStatus.PASSED,
                    evaluation_reasoning="Passed.",
                    extensions={},
                ),
                id_b: AtomExecutionState(
                    tda_id=id_b,
                    status=ExecutionStatus.FAILED,
                    evaluation_reasoning="Failed.",
                    extensions={},
                ),
                id_c: AtomExecutionState(
                    tda_id=id_c,
                    status=ExecutionStatus.N_A,
                    evaluation_reasoning=f"Dependency prerequisite not met for parent '{id_b}'",
                    extensions={},
                ),
            },
            TokenUsage(prompt_tokens=30, completion_tokens=15, total_tokens=45),
        )

    mock_dag_executor_instance.execute_graph.side_effect = mock_execute_graph

    mock_projector.project.return_value = (
        [
            AtomResultDTO(
                tda_id=id_a,
                status=ExecutionStatus.PASSED,
                source_quote="Found explicit statement A.",
                evaluation_reasoning="Passed.",
                depends_on_tda_ids=[],
                short_circuit_reason_tda_ids=[],
            ),
            AtomResultDTO(
                tda_id=id_b,
                status=ExecutionStatus.FAILED,
                evaluation_reasoning="Failed.",
                depends_on_tda_ids=[],
                short_circuit_reason_tda_ids=[],
            ),
            AtomResultDTO(
                tda_id=id_c,
                status=ExecutionStatus.N_A,
                evaluation_reasoning=f"Dependency prerequisite not met for parent '{id_b}'",
                depends_on_tda_ids=[id_a, id_b],
                short_circuit_reason_tda_ids=[id_b],
            ),
        ],
        {},
    )

    engine = TDAEngine(prompt_compiler=mock_compiler)
    result = await engine.execute(req)

    nodes_arg = mock_dag_executor_instance.execute_graph.call_args[0][0]
    assert len(nodes_arg) == 3
    assert len(nodes_arg[2].depends_on) == 2

    res_c = next(r for r in result.results if r.tda_id == id_c)
    assert res_c.status == ExecutionStatus.N_A
    assert res_c.short_circuit_reason_tda_ids == [id_b]
