import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend_v2.models.domain.blackboard import DraftExtractedAtom, DraftAtomList
from backend_v2.models.dtos.dag_models import GlobalOntologyMap
from backend_v2.services.orchestrator.two_pass_atomizer import TwoPassAtomizer
import asyncio

@pytest.fixture
def mock_llm_executor() -> MagicMock:
    return MagicMock()

@pytest.fixture
def mock_client() -> MagicMock:
    return AsyncMock()

@pytest.mark.asyncio
async def test_two_pass_atomizer_dlq_routing(mock_llm_executor: MagicMock, mock_client: MagicMock) -> None:
    atomizer = TwoPassAtomizer(mock_llm_executor)
    
    atoms = [
        DraftExtractedAtom(reasoning="1", resolved_claim="1", draft_id="a1", is_logical_deduction=True),
        DraftExtractedAtom(reasoning="2", resolved_claim="2", draft_id="a2", is_logical_deduction=False, source_quote=None),
        DraftExtractedAtom(reasoning="3", resolved_claim="3", draft_id="a3", is_logical_deduction=False, source_quote="does not exist"),
    ]
    
    mock_llm_executor.execute_structured_task = AsyncMock(return_value=(DraftAtomList(atoms=atoms), None))
    
    ontology = GlobalOntologyMap(entities=[], macro_rules=[])
    chunk = "This chunk has some text but not the fake quote."
    sem = asyncio.Semaphore(1)
    
    result = await atomizer._extract_drafts_from_chunk_with_retry(mock_client, chunk, 1, "{}", sem)
    
    assert len(result.atoms) == 1
    assert result.atoms[0].draft_id == "a1"
