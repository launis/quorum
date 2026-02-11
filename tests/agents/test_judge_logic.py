import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from backend.agents.judge import JudgeAgent
from backend.exceptions import AgentExecutionError

@pytest.fixture
def mock_llm_factory():
    with patch("backend.agents.base.LLMFactory") as mock:
        mock.create_provider.return_value = MagicMock()
        yield mock

@pytest.mark.asyncio
async def test_judge_no_passiveness_cutter(mock_llm_factory):
    """Verify strictly high scores are preserved if no Level 1."""
    judge = JudgeAgent(model="mock-model", provider="openai")
    
    # Mock LLM Output: All 4.0
    mock_llm_result = {
        "matrix_id": "test_matrix",
        "total_score": 4.0,
        "dimensions": [
            {"dimension_id": "dim1", "score": 4.0, "dimension_label": "A"},
            {"dimension_id": "dim2", "score": 4.0, "dimension_label": "B"},
        ],
        "critical_findings": []
    }
    
    mock_repo = MagicMock()
    mock_repo.get_component_by_id = AsyncMock(return_value={
        "content": {
            "scale": {"min": 1, "max": 4},
            "criteria": [
                {"id": "dim1", "label": "A"},
                {"id": "dim2", "label": "B"}
            ]
        }
    })

    with patch("backend.agents.base.BaseAgent.execute", new_callable=AsyncMock) as mock_super:
        mock_super.return_value = mock_llm_result

        result = await judge.execute(
            input_data={},
            execution_context={"matrix_id": "test_matrix", "monitored_steps": {"step_analyst": "Analyst"}},
            system_instruction="mock",
            repository=mock_repo
        )

    assert result["total_score"] == 4.0
    assert len(result["critical_findings"]) == 0

@pytest.mark.asyncio
async def test_judge_passiveness_cutter_activated(mock_llm_factory):
    """Verify score is capped at 2.0 if ANY dimension is 1.0."""
    judge = JudgeAgent(model="mock-model", provider="openai")
    
    # Mock LLM Output: 4.0 total (hallucinated or average) but mixed dimensions
    mock_llm_result = {
        "matrix_id": "test_matrix",
        "total_score": 3.0, # Average of 5 and 1 is 3.
        "dimensions": [
            {"dimension_id": "dim1", "score": 5.0, "dimension_label": "Star"}, # Super high
            {"dimension_id": "dim2", "score": 1.0, "dimension_label": "Passenger"}, # The anchor
        ],
        "critical_findings": []
    }
    
    mock_repo = MagicMock()
    mock_repo.get_component_by_id = AsyncMock(return_value={
        "content": {
            "scale": {"min": 1, "max": 4},
            "criteria": [
                {"id": "dim1", "label": "Star"},
                {"id": "dim2", "label": "Passenger"}
            ]
        }
    })

    with patch("backend.agents.base.BaseAgent.execute", new_callable=AsyncMock) as mock_super:
        mock_super.return_value = mock_llm_result

        result = await judge.execute(
            input_data={},
            execution_context={"matrix_id": "test_matrix", "monitored_steps": {"step_analyst": "Analyst"}},
            system_instruction="mock",
            repository=mock_repo
        )

    # ASSERTIONS
    assert result["total_score"] == 2.0, "Total Score must be capped at 2.0"
    assert len(result["critical_findings"]) > 0
    assert "PASSIVENESS_CUTTER_ACTIVATED" in result["critical_findings"][0]

@pytest.mark.asyncio
async def test_judge_passiveness_cutter_nested_cards(mock_llm_factory):
    """Verify Passiveness Cutter works on nested score_cards."""
    judge = JudgeAgent(model="mock-model", provider="openai")
    
    mock_llm_result = {
        "matrix_id": "test_matrix",
        "total_score": 4.0,
        "dimensions": [],
        "score_cards": [
            {
                "id": "card1",
                "total_score": 4.0,
                "dimensions": [
                   {"dimension_id": "d1", "score": 4.0},
                   {"dimension_id": "d2", "score": 1.0} # TRIGGER
                ]
            }
        ]
    }
    
    mock_repo = MagicMock()
    mock_repo.get_component_by_id = AsyncMock(return_value={
        "content": {
            "scale": {"min": 1, "max": 4},
            "criteria": [
                {"id": "d1", "label": "Label1"},
                {"id": "d2", "label": "Label2"}
            ]
        }
    })

    with patch("backend.agents.base.BaseAgent.execute", new_callable=AsyncMock) as mock_super:
        mock_super.return_value = mock_llm_result

        result = await judge.execute(
            input_data={},
            execution_context={"matrix_id": "test_matrix", "monitored_steps": {"step_analyst": "Analyst"}},
            system_instruction="mock",
            repository=mock_repo
        )

    card = result["score_cards"][0]
    assert card["total_score"] == 2.0
    assert "critical_findings" in card
    assert "PASSIVENESS_CUTTER_ACTIVATED" in card["critical_findings"][0]

@pytest.mark.asyncio
async def test_judge_passiveness_cutter_dynamic_scale(mock_llm_factory):
    """Test PASSIVENESS_CUTTER with a 1-100 scale matrix."""
    
    # Setup Mock Repo with 1-100 Scale
    mock_repo = MagicMock()
    mock_repo.get_component_by_id = AsyncMock(return_value={
        "content": {
            "scale": {"min": 1, "max": 100},
            "criteria": [
                {"id": "dim1", "label": "Star"},
                {"id": "dim2", "label": "Passenger"}
            ]
        }
    })

    # Expected Cap: 1 + (99 / 3) = 34.0
    EXPECTED_CAP = 34.0
    PASSENGER_SCORE = 1.0

    # User has 90, 90, 1 (Passenger)
    mock_llm_result = {
        "matrix_id": "matrix_dynamic_100",
        "dimensions": [
            {"dimension_id": "dim1", "score": 90, "reasoning": "Excellent"},
            {"dimension_id": "dim1", "score": 90, "reasoning": "Excellent"},
            {"dimension_id": "dim2", "score": PASSENGER_SCORE, "reasoning": "Values match 'Passenger' anchor exactly."}
        ],
        "total_score": 60.33, # (90+90+1)/3 approx
        "final_verdict": "Mixed bag",
        "confidence_score": 0.9,
        "critical_findings": []
    }

    judge = JudgeAgent(model="mock-model", provider="openai")

    with patch("backend.agents.base.BaseAgent.execute", new_callable=AsyncMock) as mock_super:
        mock_super.return_value = mock_llm_result
        
        # Test Case: Passenger in one dimension -> Cap at 34.0
        result = await judge.execute(
            input_data={}, 
            execution_context={"matrix_id": "matrix_dynamic_100", "monitored_steps": {"step": "test"}},
            repository=mock_repo
        )
        
        assert result["scale_min"] == 1
        assert result["scale_max"] == 100
        assert result["total_score"] == EXPECTED_CAP, f"Total Score must be capped at {EXPECTED_CAP} for 1-100 scale. Got {result['total_score']}"
        assert f"capped at {EXPECTED_CAP}" in result["critical_findings"][0]
