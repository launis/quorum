"""Unit tests for CausalDiscoveryEngine execution, validations, and cycle defense."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.step import StepRule
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.causal_discovery import CausalGraphPayloadDTO
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.dtos.dag_models import (
    CausalEdge,
    ExtractedAtom,
    GlobalOntologyMap,
    LinkedAtomGraph,
    OntologyEntity,
)
from backend_v2.models.dtos.engine import EngineExecutionRequest
from backend_v2.models.dtos.hook_state import GlobalContextVarsDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.services.orchestrator.engines.base import ExecutionEngine
from backend_v2.services.orchestrator.engines.causal_discovery_engine import (
    CausalDiscoveryEngine,
)
from backend_v2.services.orchestrator.strategies.base import StrategyContext


class DummySchema(BaseModel):
    """Placeholder schema for prompt compiler interface."""

    dummy: str = "test"


@pytest.fixture
def mock_client() -> MagicMock:
    """Mocked LLM client fixture."""
    client = MagicMock(spec=LLMClient)
    client.provider_name = "mock_provider"
    client.model_name = "mock_model"
    return client


@pytest.fixture
def mock_prompt_compiler() -> MagicMock:
    """Mocked prompt compiler fixture."""
    compiler = MagicMock()
    return compiler


def create_engine_request(
    source_text: str,
    client: MagicMock,
    compiler: MagicMock,
) -> EngineExecutionRequest:
    """Helper creating typed EngineExecutionRequest with zero raw dictionaries."""
    step = StepRule(
        id="stp_1111111111111111",
        task_blueprint="bp_1111111111111111",
    )
    context = StrategyContext(
        execution_id="exe_1111111111111111",
        workflow_id="wf_1111111111111111",
        output_profile_id="prof_1111111111111111",
        target_locale="en",
        metadata=ExecutionMetadata(),
        expected_inputs=[],
        strictness_level=0,
        global_context_vars=GlobalContextVarsDTO(),
        context_variables=ContextVariablesDTO(),
        prompt_blocks=[],
    )
    return EngineExecutionRequest(
        bound_client=client,
        compiled_schema=DummySchema,
        hydrated_messages=None,
        system_prompt="Test Causal Prompt",
        step=step,
        context=context,
        global_source_text=source_text,
        target_locale="en",
        progress_callback=None,
        trace_callback=None,
        prompt_compiler=compiler,
    )


def test_causal_discovery_telemetry_strategy_label(mock_prompt_compiler: MagicMock) -> None:
    """Verify CausalDiscoveryEngine implements ExecutionEngine protocol and exposes 'causal' label."""
    engine = CausalDiscoveryEngine(prompt_compiler=mock_prompt_compiler)
    assert isinstance(engine, ExecutionEngine)
    assert engine.telemetry_strategy_label == "causal"


@pytest.mark.asyncio
async def test_causal_discovery_empty_document_raises_app_exception(
    mock_client: MagicMock, mock_prompt_compiler: MagicMock
) -> None:
    """Verify empty or whitespace document text triggers CAUSAL_DISCOVERY_EMPTY_DOCUMENT."""
    engine = CausalDiscoveryEngine(prompt_compiler=mock_prompt_compiler)

    # Equivalence partition 1: completely empty string
    request_empty = create_engine_request("", mock_client, mock_prompt_compiler)
    with pytest.raises(AppException) as exc_info:
        await engine.execute(request_empty)

    assert exc_info.value.status_code == 422
    assert exc_info.value.details["error_code"] == ErrorCodes.CAUSAL_DISCOVERY_EMPTY_DOCUMENT.value

    # Equivalence partition 2: whitespace-only string
    request_whitespace = create_engine_request("   \n\n\t  ", mock_client, mock_prompt_compiler)
    with pytest.raises(AppException) as exc_info_ws:
        await engine.execute(request_whitespace)

    assert exc_info_ws.value.status_code == 422
    assert exc_info_ws.value.details["error_code"] == ErrorCodes.CAUSAL_DISCOVERY_EMPTY_DOCUMENT.value


@pytest.mark.asyncio
async def test_causal_discovery_data_starvation_raises_app_exception(
    mock_client: MagicMock, mock_prompt_compiler: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify non-empty text yielding 0 valid claims triggers CAUSAL_DISCOVERY_DATA_STARVATION."""
    engine = CausalDiscoveryEngine(prompt_compiler=mock_prompt_compiler)
    request = create_engine_request("This is a document about architecture.", mock_client, mock_prompt_compiler)

    mock_ontology = GlobalOntologyMap(entities=[], macro_rules=[])
    u0 = TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15)
    u1 = TokenUsage(prompt_tokens=20, completion_tokens=10, total_tokens=30)

    # TwoPassAtomizer returns empty list of extracted atoms
    mock_atomizer = MagicMock()
    mock_atomizer.execute_phase_0 = AsyncMock(return_value=(mock_ontology, u0))
    mock_atomizer.execute_phase_1 = AsyncMock(return_value=([], u1))

    monkeypatch.setattr(
        "backend_v2.services.orchestrator.engines.causal_discovery_engine.TwoPassAtomizer",
        lambda executor: mock_atomizer,
    )

    with pytest.raises(AppException) as exc_info:
        await engine.execute(request)

    assert exc_info.value.status_code == 422
    assert exc_info.value.details["error_code"] == ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION.value


@pytest.mark.asyncio
async def test_causal_discovery_exact_quote_anchoring_passes(
    mock_client: MagicMock, mock_prompt_compiler: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify claim with exact quote matching source paragraph is preserved and validated."""
    source_text = "The system uses Kahn's algorithm for topological sorting.\n\nDeadlocks are avoided."
    request = create_engine_request(source_text, mock_client, mock_prompt_compiler)
    engine = CausalDiscoveryEngine(prompt_compiler=mock_prompt_compiler)

    mock_ontology = GlobalOntologyMap(
        entities=[OntologyEntity(name="TopologicalSorter", description="Algorithm")],
        macro_rules=["Deadlocks are avoided."],
    )
    quote = "The system uses Kahn's algorithm for topological sorting."
    atom = ExtractedAtom(
        tda_id="tda_11111111",
        resolved_claim="The system orders nodes topologically.",
        reasoning="Direct statement in text.",
        source_quotes=(quote,),
        source_id="chunk_0",
        source_sequence_index=0,
    )

    u0 = TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15)
    u1 = TokenUsage(prompt_tokens=20, completion_tokens=10, total_tokens=30)
    u_link = TokenUsage(prompt_tokens=5, completion_tokens=5, total_tokens=10)

    mock_atomizer = MagicMock()
    mock_atomizer.execute_phase_0 = AsyncMock(return_value=(mock_ontology, u0))
    mock_atomizer.execute_phase_1 = AsyncMock(return_value=([atom], u1))
    monkeypatch.setattr(
        "backend_v2.services.orchestrator.engines.causal_discovery_engine.TwoPassAtomizer",
        lambda executor: mock_atomizer,
    )

    mock_linker = MagicMock()
    mock_linked_node = LinkedAtomGraph(atom=atom, depends_on=[])
    mock_linker.link_graph = AsyncMock(return_value=([mock_linked_node], u_link))
    monkeypatch.setattr(
        "backend_v2.services.orchestrator.engines.causal_discovery_engine.SlidingWindowLinker",
        lambda window_size, overlap: mock_linker,
    )

    result = await engine.execute(request)
    assert isinstance(result.synthesis_output, CausalGraphPayloadDTO)
    payload = result.synthesis_output
    assert len(payload.nodes) == 1
    assert payload.nodes[0].node_id == "tda_11111111"
    assert payload.nodes[0].source_quotes == (quote,)
    assert payload.nodes[0].status == ExecutionStatus.PASSED
    assert payload.cycle_detected is False


@pytest.mark.asyncio
async def test_causal_discovery_inexact_quote_fails_validation(
    mock_client: MagicMock, mock_prompt_compiler: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify hallucinated quote not present in source text is pruned, triggering starvation if 0 valid."""
    source_text = "Original authentic document text."
    request = create_engine_request(source_text, mock_client, mock_prompt_compiler)
    engine = CausalDiscoveryEngine(prompt_compiler=mock_prompt_compiler)

    mock_ontology = GlobalOntologyMap(entities=[], macro_rules=[])
    hallucinated_atom = ExtractedAtom(
        tda_id="tda_aaaaaaaa",
        resolved_claim="Completely fabricated assertion.",
        reasoning="Hallucinated evidence.",
        source_quotes=("This sentence never appeared in original text.",),
        source_id="chunk_0",
        source_sequence_index=0,
    )

    mock_atomizer = MagicMock()
    mock_atomizer.execute_phase_0 = AsyncMock(
        return_value=(mock_ontology, TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15))
    )
    mock_atomizer.execute_phase_1 = AsyncMock(
        return_value=([hallucinated_atom], TokenUsage(prompt_tokens=20, completion_tokens=10, total_tokens=30))
    )
    monkeypatch.setattr(
        "backend_v2.services.orchestrator.engines.causal_discovery_engine.TwoPassAtomizer",
        lambda executor: mock_atomizer,
    )

    # Inexact quote gets pruned by str.find, leaving 0 valid atoms -> CAUSAL_DISCOVERY_DATA_STARVATION
    with pytest.raises(AppException) as exc_info:
        await engine.execute(request)

    assert exc_info.value.status_code == 422
    assert exc_info.value.details["error_code"] == ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION.value


@pytest.mark.asyncio
async def test_causal_discovery_single_atom_zero_edges(
    mock_client: MagicMock, mock_prompt_compiler: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify text yielding exactly 1 extracted claim produces graph with 1 node, 0 edges, and node in isolated."""
    source_text = "Solitary single proposition in document."
    request = create_engine_request(source_text, mock_client, mock_prompt_compiler)
    engine = CausalDiscoveryEngine(prompt_compiler=mock_prompt_compiler)

    mock_ontology = GlobalOntologyMap(entities=[], macro_rules=[])
    atom = ExtractedAtom(
        tda_id="tda_11111111",
        resolved_claim="Solitary single proposition in document.",
        reasoning="Solo statement.",
        source_quotes=("Solitary single proposition in document.",),
        source_id="chunk_0",
        source_sequence_index=0,
    )

    mock_atomizer = MagicMock()
    mock_atomizer.execute_phase_0 = AsyncMock(
        return_value=(mock_ontology, TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15))
    )
    mock_atomizer.execute_phase_1 = AsyncMock(
        return_value=([atom], TokenUsage(prompt_tokens=20, completion_tokens=10, total_tokens=30))
    )
    monkeypatch.setattr(
        "backend_v2.services.orchestrator.engines.causal_discovery_engine.TwoPassAtomizer",
        lambda executor: mock_atomizer,
    )

    mock_linker = MagicMock()
    mock_linked_node = LinkedAtomGraph(atom=atom, depends_on=[])
    mock_linker.link_graph = AsyncMock(
        return_value=([mock_linked_node], TokenUsage(prompt_tokens=5, completion_tokens=5, total_tokens=10))
    )
    monkeypatch.setattr(
        "backend_v2.services.orchestrator.engines.causal_discovery_engine.SlidingWindowLinker",
        lambda window_size, overlap: mock_linker,
    )

    result = await engine.execute(request)
    assert isinstance(result.synthesis_output, CausalGraphPayloadDTO)
    payload = result.synthesis_output
    assert len(payload.nodes) == 1
    assert len(payload.edges) == 0
    assert payload.cycle_detected is False
    assert payload.isolated_node_ids == ["tda_11111111"]


@pytest.mark.asyncio
async def test_causal_discovery_circular_graph_marks_system_error(
    mock_client: MagicMock, mock_prompt_compiler: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify directed circular argument loop (A -> B -> A) is detected and marked SYSTEM_ERROR."""
    source_text = "Claim A requires Claim B. Conversely, Claim B requires Claim A."
    request = create_engine_request(source_text, mock_client, mock_prompt_compiler)
    engine = CausalDiscoveryEngine(prompt_compiler=mock_prompt_compiler)

    mock_ontology = GlobalOntologyMap(entities=[], macro_rules=[])
    atom_a = ExtractedAtom(
        tda_id="tda_aaaaaaaa",
        resolved_claim="Claim A requires Claim B.",
        reasoning="Premise A.",
        source_quotes=("Claim A requires Claim B.",),
        source_id="chunk_0",
        source_sequence_index=0,
    )
    atom_b = ExtractedAtom(
        tda_id="tda_bbbbbbbb",
        resolved_claim="Conversely, Claim B requires Claim A.",
        reasoning="Premise B.",
        source_quotes=("Conversely, Claim B requires Claim A.",),
        source_id="chunk_0",
        source_sequence_index=1,
    )

    mock_atomizer = MagicMock()
    mock_atomizer.execute_phase_0 = AsyncMock(
        return_value=(mock_ontology, TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15))
    )
    mock_atomizer.execute_phase_1 = AsyncMock(
        return_value=([atom_a, atom_b], TokenUsage(prompt_tokens=20, completion_tokens=10, total_tokens=30))
    )
    monkeypatch.setattr(
        "backend_v2.services.orchestrator.engines.causal_discovery_engine.TwoPassAtomizer",
        lambda executor: mock_atomizer,
    )

    # Edge A -> B and Edge B -> A creates circular dependency
    edge_a_to_b = CausalEdge(
        tda_id="tda_bbbbbbbb",
        edge_reasoning="A depends on B",
        source_id="chunk_0",
        expected_status=ExecutionStatus.PASSED,
    )
    edge_b_to_a = CausalEdge(
        tda_id="tda_aaaaaaaa",
        edge_reasoning="B depends on A",
        source_id="chunk_0",
        expected_status=ExecutionStatus.PASSED,
    )

    linked_a = LinkedAtomGraph(atom=atom_a, depends_on=[edge_a_to_b])
    linked_b = LinkedAtomGraph(atom=atom_b, depends_on=[edge_b_to_a])

    mock_linker = MagicMock()
    mock_linker.link_graph = AsyncMock(
        return_value=([linked_a, linked_b], TokenUsage(prompt_tokens=10, completion_tokens=10, total_tokens=20))
    )
    monkeypatch.setattr(
        "backend_v2.services.orchestrator.engines.causal_discovery_engine.SlidingWindowLinker",
        lambda window_size, overlap: mock_linker,
    )

    result = await engine.execute(request)
    assert isinstance(result.synthesis_output, CausalGraphPayloadDTO)
    payload = result.synthesis_output

    assert payload.cycle_detected is True
    # Cyclic nodes should be marked SYSTEM_ERROR
    node_map = {n.node_id: n for n in payload.nodes}
    assert node_map["tda_aaaaaaaa"].status == ExecutionStatus.SYSTEM_ERROR
    assert node_map["tda_bbbbbbbb"].status == ExecutionStatus.SYSTEM_ERROR


@pytest.mark.asyncio
async def test_causal_discovery_token_usage_aggregated(
    mock_client: MagicMock, mock_prompt_compiler: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify engine execution result usage matches exact sum of Phase 0, Phase 1, and Linking token usages."""
    source_text = "Proposition for token tracking."
    request = create_engine_request(source_text, mock_client, mock_prompt_compiler)
    engine = CausalDiscoveryEngine(prompt_compiler=mock_prompt_compiler)

    mock_ontology = GlobalOntologyMap(entities=[], macro_rules=[])
    atom = ExtractedAtom(
        tda_id="tda_11111111",
        resolved_claim="Proposition for token tracking.",
        reasoning="Token claim.",
        source_quotes=("Proposition for token tracking.",),
        source_id="chunk_0",
        source_sequence_index=0,
    )

    usage_0 = TokenUsage(prompt_tokens=100, completion_tokens=20, total_tokens=120)
    usage_1 = TokenUsage(prompt_tokens=200, completion_tokens=50, total_tokens=250)
    usage_link = TokenUsage(prompt_tokens=50, completion_tokens=30, total_tokens=80)

    mock_atomizer = MagicMock()
    mock_atomizer.execute_phase_0 = AsyncMock(return_value=(mock_ontology, usage_0))
    mock_atomizer.execute_phase_1 = AsyncMock(return_value=([atom], usage_1))
    monkeypatch.setattr(
        "backend_v2.services.orchestrator.engines.causal_discovery_engine.TwoPassAtomizer",
        lambda executor: mock_atomizer,
    )

    mock_linker = MagicMock()
    mock_linked_node = LinkedAtomGraph(atom=atom, depends_on=[])
    mock_linker.link_graph = AsyncMock(return_value=([mock_linked_node], usage_link))
    monkeypatch.setattr(
        "backend_v2.services.orchestrator.engines.causal_discovery_engine.SlidingWindowLinker",
        lambda window_size, overlap: mock_linker,
    )

    result = await engine.execute(request)
    assert result.usage is not None
    assert result.usage.prompt_tokens == 100 + 200 + 50
    assert result.usage.completion_tokens == 20 + 50 + 30
    assert result.usage.total_tokens == 120 + 250 + 80


@pytest.mark.asyncio
async def test_causal_discovery_phantom_edges_filtered(
    mock_client: MagicMock, mock_prompt_compiler: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify linker producing edge with target or source not in extracted nodes is pruned."""
    source_text = "Real valid proposition."
    request = create_engine_request(source_text, mock_client, mock_prompt_compiler)
    engine = CausalDiscoveryEngine(prompt_compiler=mock_prompt_compiler)

    mock_ontology = GlobalOntologyMap(entities=[], macro_rules=[])
    atom = ExtractedAtom(
        tda_id="tda_11111111",
        resolved_claim="Real valid proposition.",
        reasoning="Fact.",
        source_quotes=("Real valid proposition.",),
        source_id="chunk_0",
        source_sequence_index=0,
    )

    mock_atomizer = MagicMock()
    mock_atomizer.execute_phase_0 = AsyncMock(
        return_value=(mock_ontology, TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15))
    )
    mock_atomizer.execute_phase_1 = AsyncMock(
        return_value=([atom], TokenUsage(prompt_tokens=20, completion_tokens=10, total_tokens=30))
    )
    monkeypatch.setattr(
        "backend_v2.services.orchestrator.engines.causal_discovery_engine.TwoPassAtomizer",
        lambda executor: mock_atomizer,
    )

    # Linker hallucinated parent dependency pointing to non-existent 'tda_99999999'
    phantom_edge = CausalEdge(
        tda_id="tda_99999999",
        edge_reasoning="Hallucinated dependency on ghost node",
        source_id="chunk_0",
        expected_status=ExecutionStatus.PASSED,
    )
    mock_linked_node = LinkedAtomGraph(atom=atom, depends_on=[phantom_edge])

    mock_linker = MagicMock()
    mock_linker.link_graph = AsyncMock(
        return_value=([mock_linked_node], TokenUsage(prompt_tokens=5, completion_tokens=5, total_tokens=10))
    )
    monkeypatch.setattr(
        "backend_v2.services.orchestrator.engines.causal_discovery_engine.SlidingWindowLinker",
        lambda window_size, overlap: mock_linker,
    )

    # Should execute successfully without ValueError from CausalGraphPayloadDTO validator
    result = await engine.execute(request)
    assert isinstance(result.synthesis_output, CausalGraphPayloadDTO)
    payload = result.synthesis_output

    assert len(payload.nodes) == 1
    assert len(payload.edges) == 0  # Phantom edge pruned
    assert payload.nodes[0].node_id == "tda_11111111"


@pytest.mark.asyncio
async def test_causal_discovery_with_progress_callback_and_deductions(
    mock_client: MagicMock, mock_prompt_compiler: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify progress callback is invoked at all milestones and logical deduction atoms are preserved."""
    source_text = "Proposition with progress and deduction."
    base_req = create_engine_request(source_text, mock_client, mock_prompt_compiler)
    progress_mock = AsyncMock()
    request = base_req.model_copy(update={"progress_callback": progress_mock})

    engine = CausalDiscoveryEngine(prompt_compiler=mock_prompt_compiler)

    mock_ontology = GlobalOntologyMap(entities=[], macro_rules=[])
    atom_deductive = ExtractedAtom(
        tda_id="tda_aaaaaaaa",
        resolved_claim="Logical deduction without quote.",
        reasoning="Inferred logically.",
        is_logical_deduction=True,
        source_quotes=None,
        source_id="chunk_0",
        source_sequence_index=0,
    )
    atom_grounded = ExtractedAtom(
        tda_id="tda_bbbbbbbb",
        resolved_claim="Proposition with progress and deduction.",
        reasoning="Grounded claim.",
        source_quotes=("Proposition with progress and deduction.",),
        source_id="chunk_0",
        source_sequence_index=1,
    )

    mock_atomizer = MagicMock()

    async def fake_p0(
        client: Any, text: str, progress_callback: Callable[[int, int], Awaitable[None]] | None = None
    ) -> tuple[GlobalOntologyMap, TokenUsage]:
        if progress_callback:
            await progress_callback(1, 1)
        return mock_ontology, TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15)

    async def fake_p1(
        client: Any,
        text: str,
        ontology: GlobalOntologyMap,
        progress_callback: Callable[[int, int], Awaitable[None]] | None = None,
    ) -> tuple[list[ExtractedAtom], TokenUsage]:
        if progress_callback:
            await progress_callback(1, 1)
        return [atom_deductive, atom_grounded], TokenUsage(prompt_tokens=20, completion_tokens=10, total_tokens=30)

    mock_atomizer.execute_phase_0 = fake_p0
    mock_atomizer.execute_phase_1 = fake_p1
    monkeypatch.setattr(
        "backend_v2.services.orchestrator.engines.causal_discovery_engine.TwoPassAtomizer",
        lambda executor: mock_atomizer,
    )

    async def fake_link(
        executor: Any,
        client: Any,
        atoms: list[ExtractedAtom],
        ontology_map: GlobalOntologyMap,
        progress_callback: Callable[[int, int], Awaitable[None]] | None = None,
    ) -> tuple[list[LinkedAtomGraph], TokenUsage]:
        if progress_callback:
            await progress_callback(1, 1)
        nodes = [
            LinkedAtomGraph(atom=atom_deductive, depends_on=[]),
            LinkedAtomGraph(atom=atom_grounded, depends_on=[]),
        ]
        return nodes, TokenUsage(prompt_tokens=5, completion_tokens=5, total_tokens=10)

    mock_linker = MagicMock()
    mock_linker.link_graph = fake_link
    monkeypatch.setattr(
        "backend_v2.services.orchestrator.engines.causal_discovery_engine.SlidingWindowLinker",
        lambda window_size, overlap: mock_linker,
    )

    result = await engine.execute(request)
    assert isinstance(result.synthesis_output, CausalGraphPayloadDTO)
    payload = result.synthesis_output
    assert len(payload.nodes) == 2
    assert progress_mock.call_count >= 4


@pytest.mark.asyncio
async def test_causal_discovery_multi_hop_blame_propagation(
    mock_client: MagicMock, mock_prompt_compiler: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify multi-hop blame propagation with diamond dependency and visited set deduplication."""
    source_text = "Node 1 causes Node 2 and Node 3. Both cause Node 4."
    request = create_engine_request(source_text, mock_client, mock_prompt_compiler)
    engine = CausalDiscoveryEngine(prompt_compiler=mock_prompt_compiler)

    mock_ontology = GlobalOntologyMap(entities=[], macro_rules=[])
    a1 = ExtractedAtom(
        tda_id="tda_11111111",
        resolved_claim="Claim 1",
        reasoning="R1",
        source_quotes=("Node 1 causes Node 2 and Node 3.",),
        source_id="chunk_0",
        source_sequence_index=0,
    )
    a2 = ExtractedAtom(
        tda_id="tda_22222222",
        resolved_claim="Claim 2",
        reasoning="R2",
        source_quotes=("Node 1 causes Node 2 and Node 3.",),
        source_id="chunk_0",
        source_sequence_index=1,
    )
    a3 = ExtractedAtom(
        tda_id="tda_33333333",
        resolved_claim="Claim 3",
        reasoning="R3",
        source_quotes=("Node 1 causes Node 2 and Node 3.",),
        source_id="chunk_0",
        source_sequence_index=2,
    )
    a4 = ExtractedAtom(
        tda_id="tda_44444444",
        resolved_claim="Claim 4",
        reasoning="R4",
        source_quotes=("Both cause Node 4.",),
        source_id="chunk_0",
        source_sequence_index=3,
    )

    mock_atomizer = MagicMock()
    mock_atomizer.execute_phase_0 = AsyncMock(
        return_value=(mock_ontology, TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15))
    )
    mock_atomizer.execute_phase_1 = AsyncMock(
        return_value=([a1, a2, a3, a4], TokenUsage(prompt_tokens=20, completion_tokens=10, total_tokens=30))
    )
    monkeypatch.setattr(
        "backend_v2.services.orchestrator.engines.causal_discovery_engine.TwoPassAtomizer",
        lambda executor: mock_atomizer,
    )

    # a1 (failed) -> a2, a3 -> a4 (diamond dependency)
    e1_to_2 = CausalEdge(
        tda_id="tda_11111111", edge_reasoning="1->2", source_id="chunk_0", expected_status=ExecutionStatus.PASSED
    )
    e1_to_3 = CausalEdge(
        tda_id="tda_11111111", edge_reasoning="1->3", source_id="chunk_0", expected_status=ExecutionStatus.PASSED
    )
    e2_to_4 = CausalEdge(
        tda_id="tda_22222222", edge_reasoning="2->4", source_id="chunk_0", expected_status=ExecutionStatus.PASSED
    )
    e3_to_4 = CausalEdge(
        tda_id="tda_33333333", edge_reasoning="3->4", source_id="chunk_0", expected_status=ExecutionStatus.PASSED
    )

    nodes = [
        LinkedAtomGraph(atom=a1, depends_on=[]),
        LinkedAtomGraph(atom=a2, depends_on=[e1_to_2]),
        LinkedAtomGraph(atom=a3, depends_on=[e1_to_3]),
        LinkedAtomGraph(atom=a4, depends_on=[e2_to_4, e3_to_4]),
    ]

    mock_linker = MagicMock()
    mock_linker.link_graph = AsyncMock(
        return_value=(nodes, TokenUsage(prompt_tokens=10, completion_tokens=10, total_tokens=20))
    )
    monkeypatch.setattr(
        "backend_v2.services.orchestrator.engines.causal_discovery_engine.SlidingWindowLinker",
        lambda window_size, overlap: mock_linker,
    )

    # Custom evaluator callback that fails a1, causing a2, a3, and a4 to block
    mock_evaluator = MagicMock()
    from backend_v2.models.dtos.dag_models import AtomExecutionState

    mock_states = {
        "tda_11111111": AtomExecutionState(
            tda_id="tda_11111111",
            status=ExecutionStatus.SYSTEM_ERROR,
            evaluation_reasoning="Root failure",
            short_circuit_reason_tda_ids=[],
            extensions={},
        ),
        "tda_22222222": AtomExecutionState(
            tda_id="tda_22222222",
            status=ExecutionStatus.BLOCKED,
            evaluation_reasoning="Blocked by 1",
            short_circuit_reason_tda_ids=["tda_11111111"],
            extensions={},
        ),
        "tda_33333333": AtomExecutionState(
            tda_id="tda_33333333",
            status=ExecutionStatus.BLOCKED,
            evaluation_reasoning="Blocked by 1",
            short_circuit_reason_tda_ids=["tda_11111111"],
            extensions={},
        ),
        "tda_44444444": AtomExecutionState(
            tda_id="tda_44444444",
            status=ExecutionStatus.BLOCKED,
            evaluation_reasoning="Blocked by 2 and 3",
            short_circuit_reason_tda_ids=["tda_22222222", "tda_33333333"],
            extensions={},
        ),
    }
    mock_evaluator.evaluate_graph = AsyncMock(return_value=mock_states)
    monkeypatch.setattr(
        "backend_v2.services.orchestrator.engines.causal_discovery_engine.TopologicalEvaluator",
        lambda: mock_evaluator,
    )

    result = await engine.execute(request)
    assert isinstance(result.synthesis_output, CausalGraphPayloadDTO)
    payload = result.synthesis_output

    assert payload.root_cause_node_ids == ["tda_11111111"]
    node_map = {n.node_id: n for n in payload.nodes}
    # a4 should have blamed upstream parents traversed through the diamond
    assert "tda_11111111" in node_map["tda_44444444"].blame_parent_ids
    assert "tda_22222222" in node_map["tda_44444444"].blame_parent_ids
    assert "tda_33333333" in node_map["tda_44444444"].blame_parent_ids


@pytest.mark.asyncio
async def test_causal_discovery_duplicate_paragraphs_must_have_unique_block_ids(
    mock_client: MagicMock, mock_prompt_compiler: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that identical paragraphs in source document receive strictly unique block IDs."""
    engine = CausalDiscoveryEngine(prompt_compiler=mock_prompt_compiler)
    source_text = "Unique paragraph one.\n\nDuplicate header.\n\nUnique paragraph two.\n\nDuplicate header."
    request = create_engine_request(source_text, mock_client, mock_prompt_compiler)

    captured_hydrated_text: list[str] = []
    mock_ontology = GlobalOntologyMap(entities=[], macro_rules=[])
    u0 = TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15)
    u1 = TokenUsage(prompt_tokens=20, completion_tokens=10, total_tokens=30)

    class SpyTwoPassAtomizer:
        def __init__(self, executor: Any) -> None:
            self.executor = executor

        async def execute_phase_0(
            self, client: Any, hydrated_text: str, progress_callback: Any = None
        ) -> tuple[GlobalOntologyMap, TokenUsage]:
            captured_hydrated_text.append(hydrated_text)
            return mock_ontology, u0

        async def execute_phase_1(
            self, client: Any, hydrated_text: str, ontology: Any, progress_callback: Any = None
        ) -> tuple[list[ExtractedAtom], TokenUsage]:
            atom = ExtractedAtom(
                reasoning="R",
                resolved_claim="C",
                is_logical_deduction=True,
                source_quotes=None,
                tda_id="tda_11111111",
                source_id="chunk_0",
                source_sequence_index=0,
            )
            return [atom], u1

    monkeypatch.setattr(
        "backend_v2.services.orchestrator.engines.causal_discovery_engine.TwoPassAtomizer",
        SpyTwoPassAtomizer,
    )

    mock_linker = MagicMock()
    mock_linked_node = LinkedAtomGraph(
        atom=ExtractedAtom(
            reasoning="R",
            resolved_claim="C",
            is_logical_deduction=True,
            source_quotes=None,
            tda_id="tda_11111111",
            source_id="chunk_0",
            source_sequence_index=0,
        ),
        depends_on=[],
    )
    u_link = TokenUsage(prompt_tokens=5, completion_tokens=5, total_tokens=10)
    mock_linker.link_graph = AsyncMock(return_value=([mock_linked_node], u_link))
    monkeypatch.setattr(
        "backend_v2.services.orchestrator.engines.causal_discovery_engine.SlidingWindowLinker",
        lambda window_size, overlap: mock_linker,
    )

    await engine.execute(request)

    assert len(captured_hydrated_text) == 1
    hydrated = captured_hydrated_text[0]
    import re

    block_ids = re.findall(r"\[(B\d+)\]", hydrated)
    assert len(block_ids) == 4
    # All 4 paragraphs must have unique, monotonically increasing IDs: B0, B1, B2, B3
    assert len(set(block_ids)) == 4, f"Duplicate block IDs detected: {block_ids}"
    assert block_ids == ["B0", "B1", "B2", "B3"]


@pytest.mark.asyncio
async def test_causal_discovery_empty_document_raises_422(
    mock_client: MagicMock, mock_prompt_compiler: MagicMock
) -> None:
    """Verify that empty or whitespace-only documents trigger fail-fast HTTP 422."""
    engine = CausalDiscoveryEngine(prompt_compiler=mock_prompt_compiler)
    request = create_engine_request("   \n\n   \n\n   ", mock_client, mock_prompt_compiler)

    with pytest.raises(AppException) as exc_info:
        await engine.execute(request)

    assert exc_info.value.status_code == 422
    assert exc_info.value.details["error_code"] == ErrorCodes.CAUSAL_DISCOVERY_EMPTY_DOCUMENT.value


@pytest.mark.asyncio
async def test_causal_discovery_dynamic_directive_provenance_and_tag_stripping(
    mock_client: MagicMock,
    mock_prompt_compiler: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify that <ai_context_directive document="..."> tags are parsed, stripped, and propagated."""
    engine = CausalDiscoveryEngine(prompt_compiler=mock_prompt_compiler)

    multi_doc_text = (
        '<ai_context_directive document="dialogue_history">\n'
        "Speaker context directive.\n"
        "</ai_context_directive>\n\n"
        "Customer: We need higher throughput.\n\n"
        "Agent: We can scale horizontally.\n\n"
        '<ai_context_directive document="deliverable_report">\n'
        "Deliverable analysis directive.\n"
        "</ai_context_directive>\n\n"
        "System architecture will leverage Kubernetes clusters to meet throughput goals.\n\n"
        "Therefore horizontally scaled pods will sustain peak load demands."
    )

    request = create_engine_request(multi_doc_text, mock_client, mock_prompt_compiler)

    captured_hydrated_text: list[str] = []
    mock_ontology = GlobalOntologyMap(entities=[], macro_rules=[])
    u0 = TokenUsage(prompt_tokens=5, completion_tokens=5, total_tokens=10)
    u1 = TokenUsage(prompt_tokens=10, completion_tokens=10, total_tokens=20)

    class SpyTwoPassAtomizer:
        def __init__(self, executor: Any) -> None:
            self.executor = executor

        async def execute_phase_0(
            self, client: Any, hydrated_text: str, progress_callback: Any = None
        ) -> tuple[GlobalOntologyMap, TokenUsage]:
            captured_hydrated_text.append(hydrated_text)
            return mock_ontology, u0

        async def execute_phase_1(
            self, client: Any, hydrated_text: str, ontology: Any, progress_callback: Any = None
        ) -> tuple[list[ExtractedAtom], TokenUsage]:
            atoms = [
                ExtractedAtom(
                    reasoning="Throughput need",
                    resolved_claim="Customer needs higher throughput.",
                    is_logical_deduction=True,
                    source_quotes=None,
                    tda_id="tda_11111111",
                    source_id="B0",
                    source_sequence_index=0,
                ),
                ExtractedAtom(
                    reasoning="Architecture scaling",
                    resolved_claim="Architecture leverages Kubernetes clusters.",
                    is_logical_deduction=True,
                    source_quotes=None,
                    tda_id="tda_22222222",
                    source_id="B2",
                    source_sequence_index=1,
                ),
            ]
            return atoms, u1

    monkeypatch.setattr(
        "backend_v2.services.orchestrator.engines.causal_discovery_engine.TwoPassAtomizer",
        SpyTwoPassAtomizer,
    )

    mock_linker = MagicMock()
    mock_linked_nodes = [
        LinkedAtomGraph(
            atom=ExtractedAtom(
                reasoning="Throughput need",
                resolved_claim="Customer needs higher throughput.",
                is_logical_deduction=True,
                source_quotes=None,
                tda_id="tda_11111111",
                source_id="B0",
                source_sequence_index=0,
            ),
            depends_on=[],
        ),
        LinkedAtomGraph(
            atom=ExtractedAtom(
                reasoning="Architecture scaling",
                resolved_claim="Architecture leverages Kubernetes clusters.",
                is_logical_deduction=True,
                source_quotes=None,
                tda_id="tda_22222222",
                source_id="B2",
                source_sequence_index=1,
            ),
            depends_on=[
                CausalEdge(
                    edge_reasoning="Throughput dependency",
                    tda_id="tda_11111111",
                    source_id="B2",
                )
            ],
        ),
    ]
    u_link = TokenUsage(prompt_tokens=5, completion_tokens=5, total_tokens=10)
    mock_linker.link_graph = AsyncMock(return_value=(mock_linked_nodes, u_link))
    monkeypatch.setattr(
        "backend_v2.services.orchestrator.engines.causal_discovery_engine.SlidingWindowLinker",
        lambda window_size, overlap: mock_linker,
    )

    output = await engine.execute(request)

    assert isinstance(output.synthesis_output, CausalGraphPayloadDTO)
    payload: CausalGraphPayloadDTO = output.synthesis_output

    # 1. Verify stripped tags in emitted text
    assert len(captured_hydrated_text) == 1
    hydrated = captured_hydrated_text[0]
    assert "<ai_context_directive" not in hydrated
    assert "</ai_context_directive>" not in hydrated
    assert "[B0]" in hydrated
    assert "[B1]" in hydrated
    assert "[B2]" in hydrated
    assert "[B3]" in hydrated

    # 2. Verify source_input_key assigned on nodes
    node_b0 = next((n for n in payload.nodes if n.node_id == "tda_11111111"), None)
    node_b2 = next((n for n in payload.nodes if n.node_id == "tda_22222222"), None)
    assert node_b0 is not None
    assert node_b0.source_input_key == "dialogue_history"
    assert node_b2 is not None
    assert node_b2.source_input_key == "deliverable_report"

    # 3. Verify partition_node_ids mapping
    assert "dialogue_history" in payload.partition_node_ids
    assert "deliverable_report" in payload.partition_node_ids
    assert "tda_11111111" in payload.partition_node_ids["dialogue_history"]
    assert "tda_22222222" in payload.partition_node_ids["deliverable_report"]

    # 4. Verify edge created and edge_root_causes initialized
    assert len(payload.edges) == 1
    assert payload.edges[0].source_id == "tda_11111111"
    assert payload.edges[0].target_id == "tda_22222222"
    assert isinstance(payload.edge_root_causes, list)
