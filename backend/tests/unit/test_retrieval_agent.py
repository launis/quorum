from unittest.mock import AsyncMock, patch

import pytest

from backend.agents.retrieval import RetrievalAgent


@pytest.mark.asyncio
async def test_retrieval_agent_hybrid_execution():
    # Arrange
    mock_repo = AsyncMock()

    # 1. Mock Precedents (Legacy)
    from datetime import datetime, timezone
    from unittest.mock import MagicMock

    from backend.models.state import TraceEvent, WorkflowState

    # Needs to match ExecutionRecord strictly
    mock_execution = MagicMock()
    mock_execution.id = "exec-1"
    mock_execution.status = "completed"
    mock_execution.completed_at = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    from backend.models.domain.judge import JudgeOutput, JudgeScoreCard, DimensionResultItem

    judge_out = JudgeOutput(
        matrix_id="m",
        scale_min=1.0,
        scale_max=5.0,
        confidence_score=1.0,
        thought_process="tp",
        conclusion="c",
        critical_findings=[],
        score_card=JudgeScoreCard(
            total_score=8.3,
            verdict="Good job.",
            agent_name="x",
            max_score=10,
            scale_min=1,
            scale_max=10,
            dimensions=[DimensionResultItem(dimension_id="dim1", dimension_label="Dim1", score=8.0, reasoning="a")]
        ),
    )

    mock_trace_event = TraceEvent(
        event_type="output",
        step_name="step_judge",
        content=judge_out.model_dump(),
    )

    mock_state = WorkflowState(workflow_id="w-1", execution_trace=[mock_trace_event])
    mock_execution.results = mock_state

    mock_repo.get_all_executions.return_value = [mock_execution]

    # 2. Mock Knowledge Base Service (New)
    with (
        patch("backend.agents.retrieval.get_repository", new=AsyncMock(return_value=mock_repo)),
        patch("backend.agents.retrieval.get_settings"),
        patch("backend.agents.retrieval.get_db_client"),
        patch("backend.services.knowledge_base_service.KnowledgeBaseService") as MockKBService,
    ):
        mock_kb_instance = MockKBService.return_value
        # FIX: Return list of objects, not string
        from backend.models.domain.retrieval import KnowledgeItem

        mock_item = KnowledgeItem(id="1", type="concept", term="Test", definition="Passed", source="doc", score=1.0)
        mock_kb_instance.retrieve_context = AsyncMock(return_value=[mock_item])

        agent = RetrievalAgent()
        inputs = MagicMock()
        inputs.organization_id = "org-1"
        inputs.history_text = "Test"
        inputs.product_text = "dummy"
        inputs.reflection_text = "dummy"
        inputs.language = "fi"
        inputs.query = "Test"

        # Act
        result = await agent.execute(inputs)

        # Assert
        assert hasattr(result, "precedents")
        precedents_text = result.precedents

        # Verify Hybrid Content (Legacy Text)
        assert "=== ENNAKKOTAPAUKSET (PRECEDENTS) ===" in precedents_text
        assert "Case exec-1" in precedents_text
        assert "=== TIETOPANKKI (KNOWLEDGE BASE) - 1 matches ===" in precedents_text
        assert "[CONCEPT] Test: Passed" in precedents_text

        # Verify Structured Items
        assert hasattr(result, "knowledge_items")
        assert len(result.knowledge_items) == 1
        assert result.knowledge_items[0].term == "Test"

        # Verify Calls
        mock_repo.get_all_executions.assert_called_once()
        mock_kb_instance.retrieve_context.assert_called_with("Test")


@pytest.mark.asyncio
async def test_retrieval_agent_kb_failure_resilience():
    from unittest.mock import MagicMock

    # Arrange: KB Service fails, but Agent should return Precedents
    mock_repo = AsyncMock()
    mock_repo.get_all_executions.return_value = []

    with (
        patch("backend.agents.retrieval.get_repository", new=AsyncMock(return_value=mock_repo)),
        patch("backend.agents.retrieval.get_settings"),
        patch("backend.agents.retrieval.get_db_client"),
        patch("backend.services.knowledge_base_service.KnowledgeBaseService") as MockKBService,
    ):
        mock_kb_instance = MockKBService.return_value
        mock_kb_instance.retrieve_context.side_effect = Exception("KB Down")

        agent = RetrievalAgent()
        inputs = MagicMock()
        inputs.organization_id = "org-1"
        inputs.history_text = "Fallback query"
        inputs.product_text = "dummy"
        inputs.reflection_text = "dummy"
        inputs.language = "fi"
        inputs.query = "Fallback query"

        # Act
        from backend.exceptions import AppException

        with pytest.raises(AppException) as excinfo:
            await agent.execute(inputs)
        assert "Critical Failure in Knowledge Base Retrieval." in str(excinfo.value)
