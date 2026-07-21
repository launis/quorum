import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from backend_v2.models.domain.blackboard import LLMDraftAtomList, LLMDraftAtom
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.services.orchestrator.two_pass_atomizer import TwoPassAtomizer


@pytest.mark.asyncio
async def test_extract_drafts_from_chunk_out_of_bounds_block_id_dropped():
    """Verify that an atom with a block_id outside the packet boundary is dropped cleanly without crashing."""
    mock_executor = MagicMock()
    
    # Return two atoms: one with out-of-bounds block ID B148, one with valid B149
    mock_draft_list = LLMDraftAtomList(
        atoms=[
            LLMDraftAtom(
                draft_id="draft_1",
                reasoning="Atom from previous packet",
                resolved_claim="Out of bounds claim",
                source_block_id="B148",
                is_logical_deduction=False,
            ),
            LLMDraftAtom(
                draft_id="draft_2",
                reasoning="Valid atom in packet",
                resolved_claim="Valid claim",
                source_block_id="B149",
                is_logical_deduction=False,
            ),
        ]
    )
    mock_executor.execute_structured_task = AsyncMock(return_value=(mock_draft_list, MagicMock()))
    
    atomizer = TwoPassAtomizer(executor=mock_executor)
    
    compiled_prompt = CompiledPrompt(
        static_messages=[{"role": "system", "content": "test"}],
        dynamic_messages=[],
    )
    
    packet_keys = ["B149", "B150"]
    hydrated_text = "[B149] Some block 149 text\n\n[B150] Some block 150 text"
    sem = asyncio.Semaphore(1)
    
    # Execute extraction
    result = await atomizer._extract_drafts_from_chunk_with_retry(
        client=MagicMock(),
        compiled_prompt=compiled_prompt,
        start_b="B149",
        end_b="B150",
        packet_keys=packet_keys,
        chunk_index=0,
        hydrated_text=hydrated_text,
        sem=sem,
    )
    
    # Should drop B148 and retain draft_2 (B149)
    assert len(result.atoms) == 1
    assert result.atoms[0].draft_id == "draft_2"
    assert result.atoms[0].source_quote == "Some block 149 text"
