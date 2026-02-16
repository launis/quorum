from unittest.mock import AsyncMock, patch

import pytest

from backend.agents.retrieval import RetrievalAgent


@pytest.mark.asyncio
async def test_retrieval_agent_hybrid_execution():
    # Arrange
    mock_repo = AsyncMock()

    # 1. Mock Precedents (Legacy)
    mock_execution = {
        "execution_id": "exec-1",
        "end_time": "2026-01-01T12:00:00",
        "status": "completed",
        "trace": {
            "step_judge": {
                "pisteet": {
                    "analyysi": {"arvosana": 8},
                    "arviointi": {"arvosana": 9},
                    "synteesi": {"arvosana": 8}
                },
                "kriittiset_havainnot_yhteenveto": "Good job."
            }
        }
    }
    mock_repo.get_all_executions.return_value = [mock_execution]

    # 2. Mock Knowledge Base Service (New)
    with patch("backend.agents.retrieval.get_repository", new=AsyncMock(return_value=mock_repo)), \
         patch("backend.agents.retrieval.get_settings"), \
         patch("backend.agents.retrieval.get_db_client"), \
         patch("backend.services.knowledge_base_service.KnowledgeBaseService") as MockKBService:

        mock_kb_instance = MockKBService.return_value
        # FIX: Return list of objects, not string
        from backend.models.domain.retrieval import KnowledgeItem
        mock_item = KnowledgeItem(id="1", type="concept", term="Test", definition="Passed", source="doc")
        mock_kb_instance.retrieve_context = AsyncMock(return_value=[mock_item])

        agent = RetrievalAgent()
        inputs = {"organization_id": "org-1", "query": "Test"}

        # Act
        result = await agent.execute(inputs)

        # Assert
        assert isinstance(result, dict)
        precedents_text = result["precedents"]

        # Verify Hybrid Content (Legacy Text)
        assert "=== ENNAKKOTAPAUKSET (PRECEDENTS) ===" in precedents_text
        assert "Case exec-1" in precedents_text
        assert "=== TIETOPANKKI (KNOWLEDGE BASE) - 1 matches ===" in precedents_text
        assert "[CONCEPT] Test: Passed" in precedents_text

        # Verify Structured Items
        assert "knowledge_items" in result
        assert len(result["knowledge_items"]) == 1
        assert result["knowledge_items"][0]["term"] == "Test"

        # Verify Calls
        mock_repo.get_all_executions.assert_called_once()
        mock_kb_instance.retrieve_context.assert_called_with("Test")


@pytest.mark.asyncio
async def test_retrieval_agent_kb_failure_resilience():
    # Arrange: KB Service fails, but Agent should return Precedents
    mock_repo = AsyncMock()
    mock_repo.get_all_executions.return_value = []

    with patch("backend.agents.retrieval.get_repository", new=AsyncMock(return_value=mock_repo)), \
         patch("backend.agents.retrieval.get_settings"), \
         patch("backend.agents.retrieval.get_db_client"), \
         patch("backend.services.knowledge_base_service.KnowledgeBaseService") as MockKBService:

        mock_kb_instance = MockKBService.return_value
        mock_kb_instance.retrieve_context.side_effect = Exception("KB Down")

        agent = RetrievalAgent()
        inputs = {"organization_id": "org-1"}

        # Act
        result = await agent.execute(inputs)

        # Assert
        precedents_text = result["precedents"]
        assert "Knowledge Base retrieval error." in precedents_text
        assert "Ei aiempia tapauksia tiedostossa." in precedents_text
