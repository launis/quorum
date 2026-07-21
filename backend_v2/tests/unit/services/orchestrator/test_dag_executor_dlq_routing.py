import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.models.domain.blackboard import LLMDraftAtom, LLMDraftAtomList
from backend_v2.services.orchestrator.two_pass_atomizer import TwoPassAtomizer


@pytest.fixture
def mock_llm_executor() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_client() -> MagicMock:
    client = AsyncMock()
    client.provider_name = "mock_llm_99"
    client.model_name = "mock"
    return client


@pytest.mark.asyncio
async def test_two_pass_atomizer_dlq_routing(mock_llm_executor: MagicMock, mock_client: MagicMock) -> None:
    atomizer = TwoPassAtomizer(mock_llm_executor)

    atoms = [
        LLMDraftAtom(reasoning="1", resolved_claim="1", draft_id="a1", is_logical_deduction=True),
        LLMDraftAtom(
            reasoning="2", resolved_claim="2", draft_id="a2", is_logical_deduction=False, source_block_id=None
        ),
        LLMDraftAtom(
            reasoning="3", resolved_claim="3", draft_id="a3", is_logical_deduction=False, source_block_id="B99"
        ),
    ]

    mock_llm_executor.execute_structured_task = AsyncMock(return_value=(LLMDraftAtomList(atoms=atoms), None))

    from backend_v2.models.prompt import CompiledPrompt
    chunk = "[B99] This chunk has some text but not the fake quote."
    sem = asyncio.Semaphore(1)
    compiled_prompt = CompiledPrompt(static_messages=[], dynamic_messages=[])

    result = await atomizer._extract_drafts_from_chunk_with_retry(
        mock_client, compiled_prompt, "B0", "B99", ["B99"], 1, chunk, sem
    )

    assert len(result.atoms) == 2
    assert result.atoms[1].draft_id == "a3"
