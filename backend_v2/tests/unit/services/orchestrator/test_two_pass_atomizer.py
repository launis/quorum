import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.blackboard import (
    LLMDraftAtom,
    LLMDraftAtomList,
)
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.dag_models import ChunkPacketDTO, ExtractedAtom, GlobalOntologyMap, OntologyEntity
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.services.orchestrator.two_pass_atomizer import TwoPassAtomizer


@pytest.fixture
def mock_executor() -> MagicMock:
    executor = MagicMock()
    executor.execute_structured_task = AsyncMock()
    return executor


@pytest.fixture
def mock_client() -> MagicMock:
    client = MagicMock()
    client.provider_name = "mock_llm_99"
    client.model_name = "mock"
    return client


@pytest.fixture
def settings_mock(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    mock = MagicMock()
    mock.max_concurrent_llm_steps = 10
    mock.llm_max_retries = 2
    mock.llm_retry_multiplier = 0.1
    mock.llm_retry_min_seconds = 0.01
    mock.llm_retry_max_seconds = 0.05
    mock.two_pass_atomizer_packet_size = 50
    mock.max_citation_span_chars = 0
    monkeypatch.setattr("backend_v2.services.orchestrator.two_pass_atomizer.get_settings", lambda: mock)
    return mock


@pytest.mark.asyncio
async def test_execute_phase_0(
    mock_executor: MagicMock,
    mock_client: MagicMock,
    settings_mock: MagicMock,
) -> None:
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
async def test_execute_phase_1(
    mock_executor: MagicMock,
    mock_client: MagicMock,
    settings_mock: MagicMock,
) -> None:
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
    assert result[0].source_quotes == ("chunk1",)
    assert result[0].source_id == "chunk_0"
    assert result[0].tda_id.startswith("tda_")
    assert len(result[0].tda_id) == 36
    assert result[1].is_logical_deduction is True
    assert usage.total_tokens == 100


@pytest.mark.asyncio
async def test_execute_phase_1_drafts(
    mock_executor: MagicMock,
    mock_client: MagicMock,
    settings_mock: MagicMock,
) -> None:
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

    progress_calls: list[tuple[int, int]] = []

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
    assert result.atoms[1].source_quotes == ("Content of B0",)
    assert usage.total_tokens == 125
    assert len(progress_calls) == 1


@pytest.mark.asyncio
async def test_extract_drafts_from_chunk_dlq_fallback(
    mock_executor: MagicMock,
    mock_client: MagicMock,
    settings_mock: MagicMock,
) -> None:
    """Test DLQ fallback when extraction throws exception."""
    atomizer = TwoPassAtomizer(executor=mock_executor)
    mock_executor.execute_structured_task.side_effect = RuntimeError("Crash in LLM task")

    compiled_prompt = CompiledPrompt(static_messages=[], dynamic_messages=[])

    result, usage = await atomizer._extract_drafts_from_chunk(
        client=mock_client,
        compiled_prompt=compiled_prompt,
        start_b="B0",
        end_b="B0",
        packet_keys=["B0"],
        chunk_index=0,
        hydrated_text="[B0] text",
    )

    assert result.dlq_status == "FAILED/DLQ"
    assert len(result.atoms) == 0
    assert usage.total_tokens == 0


def test_calculate_packets_empty(mock_executor: MagicMock) -> None:
    """Test _calculate_packets with text without block IDs."""
    atomizer = TwoPassAtomizer(executor=mock_executor)
    packets = atomizer._calculate_packets("Simple text without any brackets")
    assert packets == []
    packets_blank = atomizer._calculate_packets("")
    assert packets_blank == []


def test_calculate_packets_dto_structure(mock_executor: MagicMock) -> None:
    """Test _calculate_packets returns ChunkPacketDTO instances with correct fields."""
    atomizer = TwoPassAtomizer(executor=mock_executor)
    text = "[B0] First block\n\n[B1] Second block\n\n[B2] Third block"
    packets = atomizer._calculate_packets(text, packet_size=2)
    assert len(packets) == 2
    assert isinstance(packets[0], ChunkPacketDTO)
    assert packets[0].start_block == "B0"
    assert packets[0].end_block == "B1"
    assert packets[0].packet_keys == ["B0", "B1"]
    assert isinstance(packets[1], ChunkPacketDTO)
    assert packets[1].start_block == "B2"
    assert packets[1].end_block == "B2"
    assert packets[1].packet_keys == ["B2"]


@pytest.mark.asyncio
async def test_empty_packets_zero_llm_calls_short_circuit(
    mock_executor: MagicMock,
    mock_client: MagicMock,
    settings_mock: MagicMock,
) -> None:
    """PROMISE: Zero LLM calls dispatched and empty models returned on text lacking block markers."""
    atomizer = TwoPassAtomizer(executor=mock_executor)
    ontology_empty = GlobalOntologyMap(entities=[], macro_rules=[])

    # Phase 0
    ont_res, ont_usage = await atomizer.execute_phase_0(client=mock_client, hydrated_text="Text without brackets")
    assert ont_res.entities == []
    assert ont_res.macro_rules == []
    assert ont_usage.total_tokens == 0
    assert mock_executor.execute_structured_task.call_count == 0

    # Phase 1
    atoms_res, atoms_usage = await atomizer.execute_phase_1(
        client=mock_client, hydrated_text="Text without brackets", ontology=ontology_empty
    )
    assert atoms_res == []
    assert atoms_usage.total_tokens == 0
    assert mock_executor.execute_structured_task.call_count == 0

    # Phase 1 drafts
    drafts_res, drafts_usage = await atomizer.execute_phase_1_drafts(
        client=mock_client, hydrated_text="Text without brackets", ontology=ontology_empty
    )
    assert drafts_res.atoms == []
    assert drafts_res.dlq_status is None
    assert drafts_usage.total_tokens == 0
    assert mock_executor.execute_structured_task.call_count == 0


@pytest.mark.asyncio
async def test_extract_atoms_from_chunk_outside_packet_raises(
    mock_executor: MagicMock,
    mock_client: MagicMock,
    settings_mock: MagicMock,
) -> None:
    """Negative boundary: Block ID outside packet bounds raises ValueError."""
    atomizer = TwoPassAtomizer(executor=mock_executor)
    mock_draft_list = LLMDraftAtomList(
        atoms=[
            LLMDraftAtom(
                reasoning="R",
                resolved_claim="C",
                source_block_id="B99",
                draft_id="a1",
                is_logical_deduction=False,
            ),
        ]
    )
    mock_executor.execute_structured_task.return_value = (
        mock_draft_list,
        TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
    )
    result, _ = await atomizer._extract_atoms_from_chunk(
        client=mock_client,
        compiled_prompt=CompiledPrompt(static_messages=[], dynamic_messages=[]),
        start_b="B0",
        end_b="B1",
        packet_keys=["B0", "B1"],
        chunk_index=0,
        hydrated_text="[B0] text\n\n[B1] text2",
    )
    assert len(result) == 0


@pytest.mark.asyncio
async def test_extract_atoms_from_chunk_alias_not_found(
    mock_executor: MagicMock,
    mock_client: MagicMock,
    settings_mock: MagicMock,
) -> None:
    """Verifies behavior when clean_id is not in alias map."""
    atomizer = TwoPassAtomizer(executor=mock_executor)
    mock_draft_list = LLMDraftAtomList(
        atoms=[
            LLMDraftAtom(
                reasoning="R",
                resolved_claim="C",
                source_block_id="B1",
                draft_id="a1",
                is_logical_deduction=False,
            ),
        ]
    )
    mock_executor.execute_structured_task.return_value = (
        mock_draft_list,
        TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
    )
    atoms, _ = await atomizer._extract_atoms_from_chunk(
        client=mock_client,
        compiled_prompt=CompiledPrompt(static_messages=[], dynamic_messages=[]),
        start_b="B0",
        end_b="B1",
        packet_keys=["B0", "B1"],
        chunk_index=0,
        hydrated_text="[B0] text",
    )
    assert len(atoms) == 0


@pytest.mark.asyncio
async def test_execute_phase_1_drafts_dlq_chunk_detected(
    mock_executor: MagicMock,
    mock_client: MagicMock,
    settings_mock: MagicMock,
) -> None:
    """Verifies execute_phase_1_drafts sets dlq_status when chunk fails."""
    atomizer = TwoPassAtomizer(executor=mock_executor)
    mock_executor.execute_structured_task.side_effect = RuntimeError("DLQ crash")
    ontology_empty = GlobalOntologyMap(entities=[], macro_rules=[])

    result, _ = await atomizer.execute_phase_1_drafts(
        client=mock_client, hydrated_text="[B0] text", ontology=ontology_empty
    )
    assert result.dlq_status == "FAILED/DLQ"
    assert result.atoms == []


@pytest.mark.asyncio
async def test_extract_drafts_corrupted_atom_dropped(
    mock_executor: MagicMock,
    mock_client: MagicMock,
    settings_mock: MagicMock,
) -> None:
    """Verifies that non-deductive atoms with block_id outside boundary or missing alias are dropped."""
    atomizer = TwoPassAtomizer(executor=mock_executor)
    mock_draft_list = LLMDraftAtomList(
        atoms=[
            LLMDraftAtom(
                reasoning="R1",
                resolved_claim="C1",
                source_block_id="B99",
                draft_id="a1",
                is_logical_deduction=False,
            ),
            LLMDraftAtom(
                reasoning="R2",
                resolved_claim="C2",
                source_block_id="B1",
                draft_id="a2",
                is_logical_deduction=False,
            ),
        ]
    )
    mock_executor.execute_structured_task.return_value = (
        mock_draft_list,
        TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
    )
    result, _ = await atomizer._extract_drafts_from_chunk(
        client=mock_client,
        compiled_prompt=CompiledPrompt(static_messages=[], dynamic_messages=[]),
        start_b="B0",
        end_b="B1",
        packet_keys=["B0", "B1"],
        chunk_index=0,
        hydrated_text="[B0] text",
    )
    assert len(result.atoms) == 0


@pytest.mark.asyncio
async def test_two_pass_atomizer_execute_phase_0_without_semaphore(
    mock_executor: MagicMock,
    mock_client: MagicMock,
    settings_mock: MagicMock,
) -> None:
    """Phase 3 Test Contract: execute_phase_0 without semaphore returns GlobalOntologyMap and TokenUsage."""
    atomizer = TwoPassAtomizer(executor=mock_executor)
    mock_ontology = GlobalOntologyMap(
        entities=[OntologyEntity(name="ContractEntity", description="Contract Desc")],
        macro_rules=["ContractRule"],
    )
    mock_executor.execute_structured_task.return_value = (
        mock_ontology,
        TokenUsage(prompt_tokens=40, completion_tokens=10, total_tokens=50),
    )

    result, usage = await atomizer.execute_phase_0(client=mock_client, hydrated_text="[B0] Contract text")
    assert isinstance(result, GlobalOntologyMap)
    assert len(result.entities) == 1
    assert result.entities[0].name == "ContractEntity"
    assert usage.total_tokens == 50


@pytest.mark.asyncio
async def test_two_pass_atomizer_execute_phase_1_without_semaphore(
    mock_executor: MagicMock,
    mock_client: MagicMock,
    settings_mock: MagicMock,
) -> None:
    """Phase 3 Test Contract: execute_phase_1 without semaphore returns list[ExtractedAtom] and TokenUsage."""
    atomizer = TwoPassAtomizer(executor=mock_executor)
    mock_ontology = GlobalOntologyMap(entities=[], macro_rules=[])
    mock_draft_list = LLMDraftAtomList(
        atoms=[
            LLMDraftAtom(
                reasoning="ContractReason",
                resolved_claim="ContractClaim",
                source_block_id="B0",
                draft_id="a1",
                is_logical_deduction=False,
            ),
        ]
    )
    mock_executor.execute_structured_task.return_value = (
        mock_draft_list,
        TokenUsage(prompt_tokens=60, completion_tokens=15, total_tokens=75),
    )

    result, usage = await atomizer.execute_phase_1(
        client=mock_client, hydrated_text="[B0] Contract chunk", ontology=mock_ontology
    )
    assert len(result) == 1
    assert isinstance(result[0], ExtractedAtom)
    assert result[0].resolved_claim == "ContractClaim"
    assert usage.total_tokens == 75


@pytest.mark.asyncio
async def test_two_pass_atomizer_helpers_reject_unexpected_semaphore_kwarg(
    mock_executor: MagicMock,
    mock_client: MagicMock,
    settings_mock: MagicMock,
) -> None:
    """Phase 3 Test Contract: verify helpers and phase methods reject unexpected sem / semaphore kwargs."""
    atomizer = TwoPassAtomizer(executor=mock_executor)
    compiled_prompt = CompiledPrompt(static_messages=[], dynamic_messages=[])
    dummy_sem = asyncio.Semaphore(1)
    sem_kwarg = {"sem": dummy_sem}
    semaphore_kwarg: dict[str, None] = {"semaphore": None}

    with pytest.raises(TypeError, match="unexpected keyword argument 'sem'"):
        await atomizer._extract_ontology_from_chunk(
            client=mock_client,
            compiled_prompt=compiled_prompt,
            start_b="B0",
            end_b="B1",
            **sem_kwarg,
        )

    with pytest.raises(TypeError, match="unexpected keyword argument 'sem'"):
        await atomizer._extract_atoms_from_chunk(
            client=mock_client,
            compiled_prompt=compiled_prompt,
            start_b="B0",
            end_b="B1",
            packet_keys=["B0", "B1"],
            chunk_index=0,
            hydrated_text="[B0] text",
            **sem_kwarg,
        )

    with pytest.raises(TypeError, match="unexpected keyword argument 'semaphore'"):
        await atomizer.execute_phase_0(
            client=mock_client,
            hydrated_text="[B0] text",
            **semaphore_kwarg,
        )


@pytest.mark.asyncio
async def test_extract_atoms_from_chunk_outside_packet_dropped_with_warning(
    mock_executor: MagicMock,
    mock_client: MagicMock,
    settings_mock: MagicMock,
) -> None:
    """Verify that an atom referencing a block outside the chunk's packet_keys is dropped with a warning, not crashing."""
    atomizer = TwoPassAtomizer(executor=mock_executor)
    compiled_prompt = CompiledPrompt(static_messages=[], dynamic_messages=[])

    mock_draft_list = LLMDraftAtomList(
        atoms=[
            LLMDraftAtom(
                reasoning="Valid atom",
                resolved_claim="Claim in packet",
                source_block_id="B0",
                draft_id="a0",
                is_logical_deduction=False,
            ),
            LLMDraftAtom(
                reasoning="Corrupted atom outside packet",
                resolved_claim="Claim out of bounds",
                source_block_id="B99",
                draft_id="a1",
                is_logical_deduction=False,
            ),
        ]
    )
    mock_executor.execute_structured_task.return_value = (
        mock_draft_list,
        TokenUsage(prompt_tokens=50, completion_tokens=10, total_tokens=60),
    )

    result, _ = await atomizer._extract_atoms_from_chunk(
        client=mock_client,
        compiled_prompt=compiled_prompt,
        start_b="B0",
        end_b="B1",
        packet_keys=["B0", "B1"],
        chunk_index=0,
        hydrated_text="[B0] valid text\n\n[B1] more text",
    )

    assert len(result) == 1
    assert result[0].resolved_claim == "Claim in packet"
    assert result[0].source_quotes == ("valid text",)


@pytest.mark.asyncio
async def test_extract_atoms_from_chunk_bounds_anchor_quote_over_1000_chars(
    mock_executor: MagicMock,
    mock_client: MagicMock,
    settings_mock: MagicMock,
) -> None:
    """Verify that TwoPassAtomizer bounds hydrated anchor quotes exceeding 1,000 chars to Gate 2 ceiling."""
    atomizer = TwoPassAtomizer(executor=mock_executor)
    compiled_prompt = CompiledPrompt(static_messages=[], dynamic_messages=[])

    mock_draft_list = LLMDraftAtomList(
        atoms=[
            LLMDraftAtom(
                reasoning="Extracted premise from massive block",
                resolved_claim="Claim from oversized block",
                source_block_id="B0",
                draft_id="a0",
                is_logical_deduction=False,
            ),
        ]
    )
    mock_executor.execute_structured_task.return_value = (
        mock_draft_list,
        TokenUsage(prompt_tokens=50, completion_tokens=10, total_tokens=60),
    )

    block_text_800 = "X" * 800
    # Default max_citation_span_chars = 0 preserves full 800 chars unbounded
    settings_mock.max_citation_span_chars = 0
    unbounded_result, _ = await atomizer._extract_atoms_from_chunk(
        client=mock_client,
        compiled_prompt=compiled_prompt,
        start_b="B0",
        end_b="B0",
        packet_keys=["B0"],
        chunk_index=0,
        hydrated_text=f"[B0] {block_text_800}",
    )
    assert len(unbounded_result) == 1
    assert unbounded_result[0].source_quotes is not None
    assert len(unbounded_result[0].source_quotes[0]) == 800

    oversized_block_text = "X" * 1250
    # Explicit positive max_citation_span_chars = 1000 slices to 1,000 chars
    settings_mock.max_citation_span_chars = 1000
    result, _ = await atomizer._extract_atoms_from_chunk(
        client=mock_client,
        compiled_prompt=compiled_prompt,
        start_b="B0",
        end_b="B0",
        packet_keys=["B0"],
        chunk_index=0,
        hydrated_text=f"[B0] {oversized_block_text}",
    )

    assert len(result) == 1
    assert result[0].source_quotes is not None
    assert len(result[0].source_quotes[0]) == 1000
    assert result[0].source_quotes[0] == "X" * 1000


@pytest.mark.asyncio
async def test_extract_atoms_from_chunk_unbounded_default_allows_anchor_quote_over_1000_chars(
    mock_executor: MagicMock,
    mock_client: MagicMock,
    settings_mock: MagicMock,
) -> None:
    """Verify that default unbounded max_citation_span_chars=0 preserves anchor quotes exceeding 1,000 chars."""
    atomizer = TwoPassAtomizer(executor=mock_executor)
    compiled_prompt = CompiledPrompt(static_messages=[], dynamic_messages=[])

    mock_draft_list = LLMDraftAtomList(
        atoms=[
            LLMDraftAtom(
                reasoning="Extracted premise from paragraph exceeding 1,000 chars",
                resolved_claim="Claim from full paragraph block",
                source_block_id="B0",
                draft_id="a0",
                is_logical_deduction=False,
            ),
        ]
    )
    mock_executor.execute_structured_task.return_value = (
        mock_draft_list,
        TokenUsage(prompt_tokens=50, completion_tokens=10, total_tokens=60),
    )

    oversized_block_text = "X" * 1250
    settings_mock.max_citation_span_chars = 0
    result, _ = await atomizer._extract_atoms_from_chunk(
        client=mock_client,
        compiled_prompt=compiled_prompt,
        start_b="B0",
        end_b="B0",
        packet_keys=["B0"],
        chunk_index=0,
        hydrated_text=f"[B0] {oversized_block_text}",
    )

    assert len(result) == 1
    assert result[0].source_quotes == (oversized_block_text,)

    draft_unbounded, _ = await atomizer._extract_drafts_from_chunk(
        client=mock_client,
        compiled_prompt=compiled_prompt,
        start_b="B0",
        end_b="B0",
        packet_keys=["B0"],
        chunk_index=0,
        hydrated_text=f"[B0] {oversized_block_text}",
    )
    assert len(draft_unbounded.atoms) == 1
    assert draft_unbounded.atoms[0].source_quotes == (oversized_block_text,)

    settings_mock.max_citation_span_chars = 1000
    draft_bounded, _ = await atomizer._extract_drafts_from_chunk(
        client=mock_client,
        compiled_prompt=compiled_prompt,
        start_b="B0",
        end_b="B0",
        packet_keys=["B0"],
        chunk_index=0,
        hydrated_text=f"[B0] {oversized_block_text}",
    )
    assert len(draft_bounded.atoms) == 1
    assert draft_bounded.atoms[0].source_quotes == ("X" * 1000,)


@pytest.mark.asyncio
async def test_phase_0_and_phase_1_progress_callbacks(
    mock_executor: MagicMock,
    mock_client: MagicMock,
    settings_mock: MagicMock,
) -> None:
    """Verify progress callbacks on execute_phase_0 and execute_phase_1."""
    atomizer = TwoPassAtomizer(executor=mock_executor)
    p0_progress: list[tuple[int, int]] = []
    p1_progress: list[tuple[int, int]] = []

    async def on_p0(completed: int, total: int) -> None:
        p0_progress.append((completed, total))

    async def on_p1(completed: int, total: int) -> None:
        p1_progress.append((completed, total))

    mock_ontology = GlobalOntologyMap(
        entities=[OntologyEntity(name="E1", description="D1")],
        macro_rules=["R1"],
    )
    mock_executor.execute_structured_task.return_value = (
        mock_ontology,
        TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
    )

    await atomizer.execute_phase_0(
        client=mock_client,
        hydrated_text="[B0] first block",
        progress_callback=on_p0,
    )
    assert p0_progress == [(1, 1)]

    mock_draft_list = LLMDraftAtomList(
        atoms=[
            LLMDraftAtom(
                reasoning="Extracted block",
                resolved_claim="Extracted claim",
                source_block_id="B0",
                draft_id="a1",
                is_logical_deduction=False,
            ),
        ]
    )
    mock_executor.execute_structured_task.return_value = (
        mock_draft_list,
        TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
    )

    atoms, _ = await atomizer.execute_phase_1(
        client=mock_client,
        hydrated_text="[B0] first block",
        ontology=mock_ontology,
        progress_callback=on_p1,
    )
    assert len(atoms) == 1
    assert p1_progress == [(1, 1)]
    assert (
        TwoPassAtomizer._resolve_bounded_quote(
            raw_block_id=None,
            packet_keys=["B0"],
            local_alias_map={"B0": "first block"},
            start_b="B0",
            end_b="B0",
        )
        is None
    )


@pytest.mark.asyncio
async def test_execute_phase_0_failure_propagates_app_exception(
    mock_executor: MagicMock,
    mock_client: MagicMock,
    settings_mock: MagicMock,
) -> None:
    """Negative test: execute_phase_0 propagates AppException when chunk task fails."""
    atomizer = TwoPassAtomizer(executor=mock_executor)
    mock_executor.execute_structured_task.side_effect = AppException(
        message="Simulated Phase 0 LLM failure",
        details={"error_code": ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED},
    )

    with pytest.raises(ExceptionGroup) as exc_info:
        await atomizer.execute_phase_0(
            client=mock_client,
            hydrated_text="[B0] first block",
        )
    assert any(isinstance(e, AppException) for e in exc_info.value.exceptions)


@pytest.mark.asyncio
async def test_extract_ontology_from_chunk_error_raises_app_exception(
    mock_executor: MagicMock,
    mock_client: MagicMock,
    settings_mock: MagicMock,
) -> None:
    """Negative test: _extract_ontology_from_chunk raises AppException on execution failure."""
    atomizer = TwoPassAtomizer(executor=mock_executor)
    mock_executor.execute_structured_task.side_effect = AppException(
        message="Simulated chunk ontology failure",
        details={"error_code": ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED},
    )
    compiled_prompt = CompiledPrompt(static_messages=[], dynamic_messages=[])

    with pytest.raises(AppException) as exc_info:
        await atomizer._extract_ontology_from_chunk(
            client=mock_client,
            compiled_prompt=compiled_prompt,
            start_b="B0",
            end_b="B0",
        )
    assert exc_info.value.error_code == ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED
