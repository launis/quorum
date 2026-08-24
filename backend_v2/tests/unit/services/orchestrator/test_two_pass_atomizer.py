import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.models.domain.blackboard import (
    LLMDraftAtom,
    LLMDraftAtomList,
)
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.dag_models import ExtractedAtom, GlobalOntologyMap, OntologyEntity
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.services.orchestrator.two_pass_atomizer import TwoPassAtomizer


@pytest.fixture
def mock_executor():
    executor = MagicMock()
    executor.execute_structured_task = AsyncMock()
    return executor


@pytest.fixture
def mock_client():
    client = MagicMock()
    client.provider_name = "mock_llm_99"
    client.model_name = "mock"
    return client


@pytest.fixture
def settings_mock(monkeypatch):
    mock = MagicMock()
    mock.max_concurrent_llm_steps = 10
    mock.llm_max_retries = 2
    mock.llm_retry_multiplier = 0.1
    mock.llm_retry_min_seconds = 0.01
    mock.llm_retry_max_seconds = 0.05
    monkeypatch.setattr("backend_v2.services.orchestrator.two_pass_atomizer.get_settings", lambda: mock)
    return mock


@pytest.mark.asyncio
async def test_execute_phase_0(mock_executor, mock_client, settings_mock):
    """Test phase 0 extraction of ontology map from chunks."""
    atomizer = TwoPassAtomizer(executor=mock_executor)

    mock_ontology = GlobalOntologyMap(
        entities=[OntologyEntity(name="Entity1", description="Test")], macro_rules=["Rule1"]
    )
    mock_executor.execute_structured_task.return_value = (
        mock_ontology,
        TokenUsage(prompt_tokens=50, completion_tokens=10, total_tokens=60),
    )

    result, usage = await atomizer.execute_phase_0(client=mock_client, hydrated_text="[B0] chunk1\n\n[B1] chunk2")

    assert isinstance(result, GlobalOntologyMap)
    assert len(result.entities) == 1
    assert result.entities[0].name == "Entity1"
    assert len(result.macro_rules) == 1
    assert "Rule1" in result.macro_rules
    assert usage.total_tokens == 60
    assert mock_executor.execute_structured_task.call_count == 1


@pytest.mark.asyncio
async def test_execute_phase_1(mock_executor, mock_client, settings_mock):
    """Test phase 1 atomic claims extraction using ontology."""
    atomizer = TwoPassAtomizer(executor=mock_executor)

    mock_ontology = GlobalOntologyMap(entities=[], macro_rules=[])

    mock_draft_list = LLMDraftAtomList(
        atoms=[
            LLMDraftAtom(reasoning="Reasoning1", resolved_claim="Claim1", source_block_id="B0", draft_id="a1"),
            LLMDraftAtom(
                reasoning="ReasoningDeduce",
                resolved_claim="ClaimDeduce",
                source_block_id=None,
                is_logical_deduction=True,
                draft_id="a2",
            ),
        ]
    )
    mock_executor.execute_structured_task.return_value = (
        mock_draft_list,
        TokenUsage(prompt_tokens=80, completion_tokens=20, total_tokens=100),
    )

    result, usage = await atomizer.execute_phase_1(
        client=mock_client, hydrated_text="[B0] chunk1", ontology=mock_ontology
    )

    assert len(result) == 2
    assert isinstance(result[0], ExtractedAtom)
    assert result[0].resolved_claim == "Claim1"
    assert result[0].source_quote == "chunk1"
    assert result[0].source_id == "chunk_0"
    assert result[0].tda_id.startswith("tda_")
    assert len(result[0].tda_id) == 12
    assert result[1].is_logical_deduction is True
    assert usage.total_tokens == 100


@pytest.mark.asyncio
async def test_execute_phase_1_drafts(mock_executor, mock_client, settings_mock):
    """Test execute_phase_1_drafts extraction and token aggregation."""
    atomizer = TwoPassAtomizer(executor=mock_executor)

    mock_ontology = GlobalOntologyMap(entities=[], macro_rules=[])
    mock_draft_list = LLMDraftAtomList(
        atoms=[
            LLMDraftAtom(reasoning="Deduction", resolved_claim="ClaimD", draft_id="a1", is_logical_deduction=True),
            LLMDraftAtom(
                reasoning="Extracted",
                resolved_claim="ClaimE",
                source_block_id="B0",
                draft_id="a2",
                is_logical_deduction=False,
            ),
            LLMDraftAtom(
                reasoning="OutsidePacket",
                resolved_claim="ClaimO",
                source_block_id="B99",
                draft_id="a4",
                is_logical_deduction=False,
            ),
        ]
    )
    mock_executor.execute_structured_task.return_value = (
        mock_draft_list,
        TokenUsage(prompt_tokens=100, completion_tokens=25, total_tokens=125),
    )

    progress_calls = []

    async def mock_progress(completed: int, total: int) -> None:
        progress_calls.append((completed, total))

    result, usage = await atomizer.execute_phase_1_drafts(
        client=mock_client,
        hydrated_text="[B0] Content of B0",
        ontology=mock_ontology,
        progress_callback=mock_progress,
    )

    assert len(result.atoms) == 2
    assert result.atoms[0].is_logical_deduction is True
    assert result.atoms[1].source_quote == "Content of B0"
    assert usage.total_tokens == 125
    assert len(progress_calls) == 1


@pytest.mark.asyncio
async def test_extract_drafts_from_chunk_dlq_fallback(mock_executor, mock_client, settings_mock):
    """Test DLQ fallback when extraction throws exception."""
    atomizer = TwoPassAtomizer(executor=mock_executor)
    mock_executor.execute_structured_task.side_effect = RuntimeError("Crash in LLM task")

    compiled_prompt = CompiledPrompt(static_messages=[], dynamic_messages=[])
    sem = asyncio.Semaphore(1)

    result, usage = await atomizer._extract_drafts_from_chunk(
        client=mock_client,
        compiled_prompt=compiled_prompt,
        start_b="B0",
        end_b="B0",
        packet_keys=["B0"],
        chunk_index=0,
        hydrated_text="[B0] text",
        sem=sem,
    )

    assert result.dlq_status == "FAILED/DLQ"
    assert len(result.atoms) == 0
    assert usage.total_tokens == 0


def test_calculate_packets_empty(mock_executor):
    """Test _calculate_packets with text without block IDs."""
    atomizer = TwoPassAtomizer(executor=mock_executor)
    packets = atomizer._calculate_packets("Simple text without any brackets")
    assert len(packets) == 1
    assert packets[0] == ("[NO_BLOCK]", "[NO_BLOCK]", [])
