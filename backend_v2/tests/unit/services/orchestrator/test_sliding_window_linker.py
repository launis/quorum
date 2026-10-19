from __future__ import annotations

import pytest

from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.dag_models import (
    CausalEdge,
    ExtractedAtom,
    GlobalOntologyMap,
    LinkedAtomGraph,
)
from backend_v2.models.enums import ExecutionStatus
from backend_v2.services.orchestrator.sliding_window_linker import (
    LinkerDependencyDTO,
    LinkerEdgeDTO,
    LinkerResponseDTO,
    SlidingWindowLinker,
    WindowCausalEdgesDTO,
)


class MockLinkerSettings:
    """Mock settings for sliding window linker tests."""

    linker_max_atoms_per_window: int = 20
    linker_max_global_root_axioms: int = 8
    linker_min_window_atoms_quota: int = 12
    max_concurrent_llm_steps: int = 3


def test_sliding_window_linker_get_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that the sliding window correctly batches atoms with overlap."""

    class MockSettings(MockLinkerSettings):
        pass

    monkeypatch.setattr("backend_v2.services.orchestrator.sliding_window_linker.get_settings", lambda: MockSettings())

    linker = SlidingWindowLinker(window_size=3, overlap=1)

    # Create dummy chunks (each list is one chunk containing atoms from a source)
    chunks = [
        [
            ExtractedAtom(
                tda_id="tda_0123456789abcdef",
                resolved_claim="claim 1",
                reasoning="reason 1",
                source_quotes=("quote 1",),
                source_sequence_index=0,
            )
        ],
        [
            ExtractedAtom(
                tda_id="tda_0123456789abcde0",
                resolved_claim="claim 2",
                reasoning="reason 2",
                source_quotes=("quote 2",),
                source_sequence_index=0,
            )
        ],
        [
            ExtractedAtom(
                tda_id="tda_0123456789abcde1",
                resolved_claim="claim 3",
                reasoning="reason 3",
                source_quotes=("quote 3",),
                source_sequence_index=0,
            )
        ],
        [
            ExtractedAtom(
                tda_id="tda_0123456789abcde2",
                resolved_claim="claim 4",
                reasoning="reason 4",
                source_quotes=("quote 4",),
                source_sequence_index=0,
            )
        ],
        [
            ExtractedAtom(
                tda_id="tda_0123456789abcde3",
                resolved_claim="claim 5",
                reasoning="reason 5",
                source_quotes=("quote 5",),
                source_sequence_index=0,
            )
        ],
    ]

    windows = linker._get_sliding_windows(chunks)

    # Expected:
    # window 1: chunks[0, 1, 2]
    # window 2: chunks[2, 3, 4]
    assert len(windows) == 2

    assert len(windows[0]) == 3
    assert windows[0][0][0].tda_id == "tda_0123456789abcdef"
    assert windows[0][1][0].tda_id == "tda_0123456789abcde0"
    assert windows[0][2][0].tda_id == "tda_0123456789abcde1"

    assert len(windows[1]) == 3
    assert windows[1][0][0].tda_id == "tda_0123456789abcde1"
    assert windows[1][1][0].tda_id == "tda_0123456789abcde2"
    assert windows[1][2][0].tda_id == "tda_0123456789abcde3"


def test_sliding_window_linker_get_windows_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test sliding window with empty chunks."""

    class MockSettings(MockLinkerSettings):
        pass

    monkeypatch.setattr("backend_v2.services.orchestrator.sliding_window_linker.get_settings", lambda: MockSettings())
    linker = SlidingWindowLinker(window_size=3, overlap=1)
    windows = linker._get_sliding_windows([])
    assert len(windows) == 0


def test_sliding_window_linker_get_windows_small(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test sliding window with chunks less than window size."""

    class MockSettings(MockLinkerSettings):
        pass

    monkeypatch.setattr("backend_v2.services.orchestrator.sliding_window_linker.get_settings", lambda: MockSettings())
    linker = SlidingWindowLinker(window_size=3, overlap=1)
    chunks = [
        [
            ExtractedAtom(
                tda_id="tda_0123456789abcdef",
                resolved_claim="claim 1",
                reasoning="reason 1",
                source_quotes=("quote 1",),
                source_sequence_index=0,
            )
        ],
        [
            ExtractedAtom(
                tda_id="tda_0123456789abcde0",
                resolved_claim="claim 2",
                reasoning="reason 2",
                source_quotes=("quote 2",),
                source_sequence_index=0,
            )
        ],
    ]
    windows = linker._get_sliding_windows(chunks)
    assert len(windows) == 1
    assert len(windows[0]) == 2


def test_sliding_window_linker_subdivides_oversized_chunks(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that chunks exceeding max_atoms are subdivided."""

    class MockSettings(MockLinkerSettings):
        linker_max_atoms_per_window = 2

    monkeypatch.setattr("backend_v2.services.orchestrator.sliding_window_linker.get_settings", lambda: MockSettings())

    linker = SlidingWindowLinker(window_size=3, overlap=1)
    chunk = [
        ExtractedAtom(
            tda_id=f"tda_0000000{i}",
            resolved_claim=f"claim {i}",
            reasoning=f"reason {i}",
            source_quotes=(f"quote {i}",),
            source_sequence_index=0,
        )
        for i in range(5)
    ]

    windows = linker._get_sliding_windows([chunk])

    assert len(windows) == 3
    assert len(windows[0]) == 1
    assert len(windows[0][0]) == 2
    assert windows[0][0][0].tda_id == "tda_00000000"

    assert len(windows[1]) == 1
    assert len(windows[1][0]) == 2
    assert windows[1][0][0].tda_id == "tda_00000002"

    assert len(windows[2]) == 1
    assert len(windows[2][0]) == 1
    assert windows[2][0][0].tda_id == "tda_00000004"


def test_linker_response_dto_schema_no_dicts() -> None:
    payload = {
        "dependencies": [
            {
                "child_alias": "a1",
                "parent_dependencies": [
                    {
                        "edge_reasoning": "Logical dependency",
                        "tda_id": "a0",
                        "expected_status": ExecutionStatus.PASSED,
                    }
                ],
            }
        ]
    }

    model = LinkerResponseDTO.model_validate(payload)

    assert len(model.dependencies) == 1
    assert model.dependencies[0].child_alias == "a1"
    assert len(model.dependencies[0].parent_dependencies) == 1
    assert model.dependencies[0].parent_dependencies[0].tda_id == "a0"

    schema = LinkerResponseDTO.model_json_schema()
    assert schema["properties"]["dependencies"]["type"] == "array"


@pytest.mark.asyncio
async def test_link_graph_ignores_hallucinated_aliases(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that a hallucinated alias from the LLM is gracefully dropped without crashing."""
    from unittest.mock import AsyncMock

    from backend_v2.services.orchestrator.sliding_window_linker import LinkerDependencyDTO, LinkerEdgeDTO

    class MockSettings(MockLinkerSettings):
        pass

    monkeypatch.setattr("backend_v2.services.orchestrator.sliding_window_linker.get_settings", lambda: MockSettings())

    linker = SlidingWindowLinker(window_size=3, overlap=1)

    # Two valid atoms
    atoms = [
        ExtractedAtom(
            tda_id="tda_00000000",
            resolved_claim="claim 0",
            reasoning="r0",
            source_quotes=("q0",),
            source_id="chunk_0",
            source_sequence_index=0,
        ),
        ExtractedAtom(
            tda_id="tda_11111111",
            resolved_claim="claim 1",
            reasoning="r1",
            source_quotes=("q1",),
            source_id="chunk_0",
            source_sequence_index=0,
        ),
    ]

    ontology = GlobalOntologyMap(entities=[], macro_rules=[])

    # The LLM hallucinates an 'a99' parent alias, and an 'a98' child alias
    mock_response = LinkerResponseDTO(
        dependencies=[
            LinkerDependencyDTO(
                child_alias="a1",  # Maps to tda_11111111
                parent_dependencies=[
                    LinkerEdgeDTO(
                        edge_reasoning="Valid edge", tda_id="a0", expected_status=ExecutionStatus.PASSED
                    ),  # Valid
                    LinkerEdgeDTO(
                        edge_reasoning="Hallucinated parent", tda_id="a99", expected_status=ExecutionStatus.PASSED
                    ),  # Hallucinated Parent
                ],
            ),
            LinkerDependencyDTO(
                child_alias="a98",  # Hallucinated Child
                parent_dependencies=[
                    LinkerEdgeDTO(
                        edge_reasoning="Edge for hallucinated child",
                        tda_id="a0",
                        expected_status=ExecutionStatus.PASSED,
                    ),
                ],
            ),
        ]
    )

    mock_executor = AsyncMock()
    mock_executor.execute_structured_task.return_value = (
        mock_response,
        TokenUsage(prompt_tokens=50, completion_tokens=10, total_tokens=60),
    )
    mock_client = AsyncMock()

    results, usage = await linker.link_graph(
        executor=mock_executor, client=mock_client, atoms=atoms, ontology_map=ontology
    )

    assert len(results) == 2
    assert usage.total_tokens == 60
    # Verify tda_00000000 has no dependencies
    node0 = next(n for n in results if n.atom.tda_id == "tda_00000000")
    assert len(node0.depends_on) == 0

    # Verify tda_11111111 has exactly 1 dependency (the valid a0 one), and the hallucinated a99 was dropped
    node1 = next(n for n in results if n.atom.tda_id == "tda_11111111")
    assert len(node1.depends_on) == 1
    assert node1.depends_on[0].tda_id == "tda_00000000"


@pytest.mark.asyncio
async def test_link_graph_empty_atoms() -> None:
    """Test that link_graph with empty atoms returns immediately with 0 usage."""
    from unittest.mock import AsyncMock

    linker = SlidingWindowLinker()
    mock_executor = AsyncMock()
    mock_client = AsyncMock()
    ontology = GlobalOntologyMap(entities=[], macro_rules=[])

    results, usage = await linker.link_graph(
        executor=mock_executor, client=mock_client, atoms=[], ontology_map=ontology
    )
    assert results == []
    assert usage.total_tokens == 0


@pytest.mark.asyncio
async def test_link_graph_llm_failure_raises_app_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that LLM task failure triggers AppException with AGENT_EXECUTION_CRITICAL."""
    from unittest.mock import AsyncMock

    from backend_v2.exceptions import AppException, ErrorCodes

    class MockSettings(MockLinkerSettings):
        pass

    monkeypatch.setattr("backend_v2.services.orchestrator.sliding_window_linker.get_settings", lambda: MockSettings())

    linker = SlidingWindowLinker(window_size=3, overlap=1)
    atoms = [
        ExtractedAtom(
            tda_id="tda_00000000",
            resolved_claim="claim 0",
            reasoning="r0",
            source_quotes=("q0",),
            source_sequence_index=0,
        )
    ]
    ontology = GlobalOntologyMap(entities=[], macro_rules=[])

    mock_executor = AsyncMock()
    mock_executor.execute_structured_task.side_effect = RuntimeError("LLM connection timeout")
    mock_client = AsyncMock()

    with pytest.raises(AppException) as exc_info:
        await linker.link_graph(executor=mock_executor, client=mock_client, atoms=atoms, ontology_map=ontology)

    assert exc_info.value.details is not None
    assert exc_info.value.details["error_code"] == ErrorCodes.AGENT_EXECUTION_CRITICAL.value


def test_sliding_window_linker_dtos_extra_fields_forbidden() -> None:
    """Test that all sliding window linker DTOs strictly forbid extra fields."""
    from pydantic import ValidationError

    from backend_v2.services.orchestrator.sliding_window_linker import (
        LinkerDependencyDTO,
        LinkerEdgeDTO,
        LinkerResponseDTO,
        WindowCausalEdgesDTO,
    )

    with pytest.raises(ValidationError):
        LinkerEdgeDTO.model_validate({"edge_reasoning": "reason", "tda_id": "a0", "extra_field": "bad"})

    with pytest.raises(ValidationError):
        LinkerDependencyDTO.model_validate({"child_alias": "a1", "extra_field": "bad"})

    with pytest.raises(ValidationError):
        LinkerResponseDTO.model_validate({"extra_field": "bad"})

    with pytest.raises(ValidationError):
        WindowCausalEdgesDTO.model_validate({"extra_field": "bad"})


@pytest.mark.asyncio
async def test_sliding_window_linker_link_graph_without_semaphore() -> None:
    """Test that link_graph executes successfully without semaphore arguments."""
    from unittest.mock import AsyncMock

    from backend_v2.services.orchestrator.sliding_window_linker import LinkerResponseDTO

    linker = SlidingWindowLinker(window_size=2, overlap=1)
    atoms = [
        ExtractedAtom(
            tda_id="tda_00000000",
            resolved_claim="claim 0",
            reasoning="r0",
            source_quotes=("q0",),
            source_sequence_index=0,
        )
    ]
    ontology = GlobalOntologyMap(entities=[], macro_rules=[])

    mock_executor = AsyncMock()
    mock_executor.execute_structured_task.return_value = (
        LinkerResponseDTO(dependencies=[]),
        TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
    )
    mock_client = AsyncMock()

    results, usage = await linker.link_graph(
        executor=mock_executor,
        client=mock_client,
        atoms=atoms,
        ontology_map=ontology,
    )

    assert len(results) == 1
    assert isinstance(results[0], LinkedAtomGraph)
    assert usage.total_tokens == 15


@pytest.mark.asyncio
async def test_sliding_window_linker_link_graph_rejects_unexpected_semaphore_kwarg() -> None:
    """Test that link_graph rejects deprecated semaphore keyword argument fail-fast."""
    import asyncio
    from unittest.mock import AsyncMock

    linker = SlidingWindowLinker()
    mock_executor = AsyncMock()
    mock_client = AsyncMock()
    ontology = GlobalOntologyMap(entities=[], macro_rules=[])
    unexpected_kwargs = {"semaphore": asyncio.Semaphore(1)}

    with pytest.raises(TypeError, match="unexpected keyword argument 'semaphore'"):
        await linker.link_graph(
            executor=mock_executor,
            client=mock_client,
            atoms=[],
            ontology_map=ontology,
            **unexpected_kwargs,
        )


def test_sliding_window_linker_root_axiom_header_quota(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify 8 root axioms are injected when window has 10 current atoms and 12 eligible root axioms.

    Tests budget guard: 10 current + 8 injected = 18 <= 20.
    Candidates must be sorted by OutDegree desc and sequence index asc.
    """
    settings = MockLinkerSettings()
    monkeypatch.setattr("backend_v2.services.orchestrator.sliding_window_linker.get_settings", lambda: settings)
    linker = SlidingWindowLinker()

    processed_atoms: dict[str, ExtractedAtom] = {}
    for i in range(12):
        tda_id = f"tda_{i:08x}"
        processed_atoms[tda_id] = ExtractedAtom(
            tda_id=tda_id,
            resolved_claim=f"Axiom claim {i}",
            reasoning=f"Reason {i}",
            source_quotes=(f"Quote {i}",),
            source_sequence_index=i,
        )

    # Master deps: Give axiom 5 and axiom 2 highest out-degree (3 children each), axiom 1 out-degree 1
    master_deps: dict[str, WindowCausalEdgesDTO] = {
        "tda_c0000001": WindowCausalEdgesDTO(
            edges={
                "tda_00000005": CausalEdge(
                    edge_reasoning="r",
                    tda_id="tda_00000005",
                    source_id="c1",
                ),
                "tda_00000002": CausalEdge(
                    edge_reasoning="r",
                    tda_id="tda_00000002",
                    source_id="c1",
                ),
            }
        ),
        "tda_c0000002": WindowCausalEdgesDTO(
            edges={
                "tda_00000005": CausalEdge(
                    edge_reasoning="r",
                    tda_id="tda_00000005",
                    source_id="c2",
                ),
                "tda_00000002": CausalEdge(
                    edge_reasoning="r",
                    tda_id="tda_00000002",
                    source_id="c2",
                ),
            }
        ),
        "tda_c0000003": WindowCausalEdgesDTO(
            edges={
                "tda_00000005": CausalEdge(
                    edge_reasoning="r",
                    tda_id="tda_00000005",
                    source_id="c3",
                ),
                "tda_00000002": CausalEdge(
                    edge_reasoning="r",
                    tda_id="tda_00000002",
                    source_id="c3",
                ),
                "tda_00000001": CausalEdge(
                    edge_reasoning="r",
                    tda_id="tda_00000001",
                    source_id="c3",
                ),
            }
        ),
    }

    current_window_ids = {f"tda_d000{j:04x}" for j in range(10)}
    selected = linker._select_root_axioms(
        processed_atoms=processed_atoms,
        current_window_ids=current_window_ids,
        master_deps=master_deps,
        current_window_size=10,
    )

    # Must select exactly 8 root axioms (K_eff = min(8, 20 - 10) = 8)
    assert len(selected) == 8
    # Top 2 by out-degree (both have out_degree=3, so sorted by sequence_index asc: 2 before 5)
    assert selected[0].tda_id == "tda_00000002"
    assert selected[1].tda_id == "tda_00000005"
    # Third has out_degree=1
    assert selected[2].tda_id == "tda_00000001"


def test_sliding_window_linker_budget_guard_exceeded(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify at most 4 root axioms injected when window has 16 atoms so total <= 20."""
    settings = MockLinkerSettings()
    monkeypatch.setattr("backend_v2.services.orchestrator.sliding_window_linker.get_settings", lambda: settings)
    linker = SlidingWindowLinker()

    processed_atoms: dict[str, ExtractedAtom] = {}
    for i in range(10):
        tda_id = f"tda_{i:08x}"
        processed_atoms[tda_id] = ExtractedAtom(
            tda_id=tda_id,
            resolved_claim=f"Axiom claim {i}",
            reasoning=f"Reason {i}",
            source_quotes=(f"Quote {i}",),
            source_sequence_index=i,
        )

    current_window_ids = {f"tda_d000{j:04x}" for j in range(16)}
    selected = linker._select_root_axioms(
        processed_atoms=processed_atoms,
        current_window_ids=current_window_ids,
        master_deps={},
        current_window_size=16,
    )

    # K_eff = min(8, max(0, 20 - 16)) = 4
    assert len(selected) == 4
    assert 16 + len(selected) <= 20


def test_sliding_window_linker_zero_root_axioms(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify 0 root axioms injected when 0 eligible root axioms exist."""
    settings = MockLinkerSettings()
    monkeypatch.setattr("backend_v2.services.orchestrator.sliding_window_linker.get_settings", lambda: settings)
    linker = SlidingWindowLinker()

    current_window_ids = {f"tda_d000{j:04x}" for j in range(12)}
    selected = linker._select_root_axioms(
        processed_atoms={},
        current_window_ids=current_window_ids,
        master_deps={},
        current_window_size=12,
    )

    assert len(selected) == 0


def test_sliding_window_linker_full_capacity_window(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify 0 root axioms injected when window is already at full capacity (20 atoms)."""
    settings = MockLinkerSettings()
    monkeypatch.setattr("backend_v2.services.orchestrator.sliding_window_linker.get_settings", lambda: settings)
    linker = SlidingWindowLinker()

    processed_atoms: dict[str, ExtractedAtom] = {}
    for i in range(15):
        tda_id = f"tda_{i:08x}"
        processed_atoms[tda_id] = ExtractedAtom(
            tda_id=tda_id,
            resolved_claim=f"Axiom claim {i}",
            reasoning=f"Reason {i}",
            source_quotes=(f"Quote {i}",),
            source_sequence_index=i,
        )

    current_window_ids = {f"tda_d000{j:04x}" for j in range(20)}
    selected = linker._select_root_axioms(
        processed_atoms=processed_atoms,
        current_window_ids=current_window_ids,
        master_deps={},
        current_window_size=20,
    )

    # K_eff = min(8, max(0, 20 - 20)) = 0
    assert len(selected) == 0


@pytest.mark.asyncio
async def test_sliding_window_linker_warrant_quotes_transit(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify structured LLM response with warrant_quotes transits cleanly into CausalEdge.warrant_quotes."""
    from unittest.mock import AsyncMock

    settings = MockLinkerSettings()
    monkeypatch.setattr("backend_v2.services.orchestrator.sliding_window_linker.get_settings", lambda: settings)
    linker = SlidingWindowLinker()

    atoms = [
        ExtractedAtom(
            tda_id="tda_00000001",
            resolved_claim="Parent premise",
            reasoning="Reason 1",
            source_quotes=("Premise Quote",),
            source_sequence_index=0,
        ),
        ExtractedAtom(
            tda_id="tda_00000002",
            resolved_claim="Child conclusion",
            reasoning="Reason 2",
            source_quotes=("Conclusion Quote",),
            source_sequence_index=1,
        ),
    ]
    ontology = GlobalOntologyMap(entities=[], macro_rules=[])

    mock_executor = AsyncMock()
    mock_executor.execute_structured_task.return_value = (
        LinkerResponseDTO(
            dependencies=[
                LinkerDependencyDTO(
                    child_alias="a1",
                    parent_dependencies=[
                        LinkerEdgeDTO(
                            edge_reasoning="Toulmin warrant grounding connection",
                            tda_id="a0",
                            expected_status=ExecutionStatus.PASSED,
                            warrant_quotes=("Warrant segment 1", "Warrant segment 2"),
                        )
                    ],
                )
            ]
        ),
        TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
    )
    mock_client = AsyncMock()

    results, _ = await linker.link_graph(
        executor=mock_executor,
        client=mock_client,
        atoms=atoms,
        ontology_map=ontology,
    )

    assert len(results) == 2
    child_graph = next(g for g in results if g.atom.tda_id == "tda_00000002")
    assert len(child_graph.depends_on) == 1
    edge = child_graph.depends_on[0]
    assert edge.tda_id == "tda_00000001"
    assert edge.warrant_quotes == ("Warrant segment 1", "Warrant segment 2")
    assert isinstance(edge.warrant_quotes, tuple)
