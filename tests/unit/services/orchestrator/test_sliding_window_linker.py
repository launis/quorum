from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.models.dtos.dag_models import ExtractedAtom, GlobalOntologyMap
from backend_v2.services.orchestrator.sliding_window_linker import (
    LinkerEdgeDTO,
    LinkerResponseDTO,
    SlidingWindowLinker,
)


@pytest.fixture
def dummy_atoms():
    return [
        ExtractedAtom(
            reasoning="R1",
            resolved_claim="Claim 1",
            source_quote="Q1",
            tda_id="tda_1111111111111111",
            source_id="chunk_0",
        ),
        ExtractedAtom(
            reasoning="R2",
            resolved_claim="Claim 2",
            source_quote="Q2",
            tda_id="tda_2222222222222222",
            source_id="chunk_1",
        ),
        ExtractedAtom(
            reasoning="R3",
            resolved_claim="Claim 3",
            source_quote="Q3",
            tda_id="tda_3333333333333333",
            source_id="chunk_2",
        ),
    ]


@pytest.fixture
def mock_executor():
    executor = MagicMock()
    executor.execute_structured_task = AsyncMock()
    return executor


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.mark.asyncio
async def test_sliding_window_linker_basic(dummy_atoms, mock_executor, mock_client):
    linker = SlidingWindowLinker(window_size=2, overlap=1)

    # Mock LLM to return dependencies using Alias IDs.
    # Window 1: tda_1 -> a0, tda_2 -> a1. tda_2 depends on tda_1.
    # Window 2: tda_2 -> a0, tda_3 -> a1. tda_3 depends on tda_2.
    async def mock_execute(*args, **kwargs):
        messages = kwargs.get("messages")
        prompt_content = messages.static_messages[1]["content"]
        if "Claim 3" in prompt_content:
            return LinkerResponseDTO(dependencies={"a1": [LinkerEdgeDTO(edge_reasoning="R", tda_id="a0")]}), None
        else:
            return LinkerResponseDTO(dependencies={"a1": [LinkerEdgeDTO(edge_reasoning="R", tda_id="a0")]}), None

    mock_executor.execute_structured_task.side_effect = mock_execute

    ontology_map = GlobalOntologyMap(entities=[], macro_rules=[])

    results = await linker.link_graph(mock_executor, mock_client, dummy_atoms, ontology_map)

    assert len(results) == 3

    # Atom 1 has no deps
    assert len(results[0].depends_on) == 0

    # Atom 2 depends on Atom 1
    assert len(results[1].depends_on) == 1
    assert results[1].depends_on[0].tda_id == "tda_1111111111111111"

    # Atom 3 depends on Atom 2
    assert len(results[2].depends_on) == 1
    assert results[2].depends_on[0].tda_id == "tda_2222222222222222"


@pytest.mark.asyncio
async def test_sliding_window_deduplication(dummy_atoms, mock_executor, mock_client):
    # If the overlap window yields the same edge again, it should be deduplicated
    linker = SlidingWindowLinker(window_size=3, overlap=2)

    async def mock_execute(*args, **kwargs):
        # Always output tda_2 (a1) depends on tda_1 (a0)
        return LinkerResponseDTO(dependencies={"a1": [LinkerEdgeDTO(edge_reasoning="R", tda_id="a0")]}), None

    mock_executor.execute_structured_task.side_effect = mock_execute

    ontology_map = GlobalOntologyMap(entities=[], macro_rules=[])

    results = await linker.link_graph(mock_executor, mock_client, dummy_atoms, ontology_map)

    # The duplicate edges should be handled by the dict-based master_deps
    assert len(results[1].depends_on) == 1
    assert results[1].depends_on[0].tda_id == "tda_1111111111111111"
