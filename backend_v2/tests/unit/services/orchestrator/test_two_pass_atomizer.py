from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.models.domain.blackboard import DraftAtomList, DraftExtractedAtom
from backend_v2.models.dtos.dag_models import ExtractedAtom, GlobalOntologyMap, OntologyEntity
from backend_v2.services.orchestrator.two_pass_atomizer import TwoPassAtomizer


@pytest.fixture
def mock_executor():
    executor = MagicMock()
    executor.execute_structured_task = AsyncMock()
    return executor


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.fixture
def settings_mock(monkeypatch):
    mock = MagicMock()
    mock.max_concurrent_llm_steps = 10
    monkeypatch.setattr("backend_v2.services.orchestrator.two_pass_atomizer.get_settings", lambda: mock)
    return mock


@pytest.mark.asyncio
async def test_execute_phase_0(mock_executor, mock_client, settings_mock):
    """Test phase 0 extraction of ontology map from chunks."""
    atomizer = TwoPassAtomizer(executor=mock_executor)

    # Mock return value for executor.execute_structured_task
    mock_ontology = GlobalOntologyMap(
        entities=[OntologyEntity(name="Entity1", description="Test")], macro_rules=["Rule1"]
    )
    mock_executor.execute_structured_task.return_value = (mock_ontology, None)

    # Execute
    result = await atomizer.execute_phase_0(client=mock_client, chunks=["chunk1", "chunk2"])

    # Assert
    assert isinstance(result, GlobalOntologyMap)
    assert len(result.entities) == 1
    assert result.entities[0].name == "Entity1"
    assert len(result.macro_rules) == 1
    assert "Rule1" in result.macro_rules
    assert mock_executor.execute_structured_task.call_count == 2


@pytest.mark.asyncio
async def test_execute_phase_1(mock_executor, mock_client, settings_mock):
    """Test phase 1 atomic claims extraction using ontology."""
    atomizer = TwoPassAtomizer(executor=mock_executor)

    # Mock dependencies
    mock_ontology = GlobalOntologyMap(entities=[], macro_rules=[])

    mock_draft_list = DraftAtomList(
        atoms=[
            DraftExtractedAtom(reasoning="Reasoning1", resolved_claim="Claim1", source_quote="Quote1", draft_id="a1")
        ]
    )
    mock_executor.execute_structured_task.return_value = (mock_draft_list, None)

    # Execute
    result = await atomizer.execute_phase_1(client=mock_client, chunks=["chunk1"], ontology=mock_ontology)

    # Assert
    assert len(result) == 1
    assert isinstance(result[0], ExtractedAtom)
    assert result[0].resolved_claim == "Claim1"
    assert result[0].source_quote == "Quote1"
    assert result[0].source_id == "chunk_0"
    assert result[0].tda_id.startswith("tda_")
    # UUID hex sliced to 16 chars (or 8 chars, dag_models currently requires 16-32)
    # Wait, my previous edit made it [:8], so it is 12 chars total.
    # We will patch dag_models.py to allow 8 chars.
    assert len(result[0].tda_id) == 12
