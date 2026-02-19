
import pytest
from unittest.mock import MagicMock, AsyncMock
from backend.agents.judge import JudgeAgent
from backend.models.domain.judge import JudgeInput, JudgeOutput, JudgeDTO, JudgeScoreCard, DimensionResultItem
from backend.exceptions import AgentExecutionError, ErrorCodes

@pytest.fixture
def mock_context():
    return {
        "matrix_id": "test_matrix",
        "scoring_logic": "standard",
        "monitored_steps": {"step_analyst": "Analyst Output"}
    }

@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.get_component_by_id = AsyncMock(return_value={
        "id": "test_matrix",
        "content": {
            "scale": {"min": 1.0, "max": 5.0},
            "criteria": [{"id": "dim1", "label": "Dimension 1"}]
        }
    })
    return repo

@pytest.fixture
def judge_agent():
    return JudgeAgent()

@pytest.mark.asyncio
async def test_judge_deterministic_scoring(judge_agent, mock_repo):
    """Verify that JudgeAgent recalculates total_score based on dimensions in execute()."""
    
    # Mock LLM response (hallucinated score)
    llm_output = JudgeDTO(
        matrix_id="test_matrix",
        thought_process="Thinking...",
        conclusion="Verdict reached.",
        confidence_score=0.8,
        scale_min=1.0, 
        scale_max=5.0,
        score_card=JudgeScoreCard(
            agent_name="TestJudge",
            total_score=1.0, # WRONG (Should be 4.0)
            max_score=5,
            verdict="Bad",
            scale_min=1.0,
            scale_max=5.0,
            dimensions=[
                DimensionResultItem(dimension_id="dim1", dimension_label="D1", score=5.0, reasoning="Good"),
                DimensionResultItem(dimension_id="dim2", dimension_label="D2", score=3.0, reasoning="Okay")
            ]
        )
    )
    
    # Mock get_model_response to return our DTO
    judge_agent.get_model_response = AsyncMock(return_value=llm_output)
    
    # Input data
    input_data = JudgeInput(
        history_text="Context",
        product_text="Product",
        step_analyst=None
    )
    
    context = {"matrix_id": "test_matrix", "scoring_logic": "standard", "monitored_steps": {"step_analyst": "Analyst"}}
    
    # Execute
    result = await judge_agent.execute(input_data, execution_context=context, repository=mock_repo)
    
    # Assert: Score should be recalculated (Authority)
    # (5+3)/2 = 4.0
    assert result.score_card.total_score == 4.0, f"Expected 4.0, got {result.score_card.total_score}"

@pytest.mark.asyncio
async def test_judge_fail_fast_empty_dimensions(judge_agent, mock_repo):
    """Verify JudgeAgent fails fast if dimensions are empty in execute()."""
    
    llm_output = JudgeDTO(
        matrix_id="test_matrix",
        thought_process="Thinking...",
        conclusion="Empty verdict.",
        confidence_score=0.0,
        scale_min=1.0, 
        scale_max=5.0,
        score_card=JudgeScoreCard(
            agent_name="TestJudge",
            total_score=0.0,
            max_score=5,
            verdict="Empty",
            scale_min=1.0,
            scale_max=5.0,
            dimensions=[] # EMPTY
        )
    )
    
    judge_agent.get_model_response = AsyncMock(return_value=llm_output)
    
    input_data = JudgeInput(history_text="C", product_text="P")
    context = {"matrix_id": "test_matrix", "scoring_logic": "standard", "monitored_steps": {"step_analyst": "Analyst"}}
    
    with pytest.raises(AgentExecutionError) as exc:
        await judge_agent.execute(input_data, execution_context=context, repository=mock_repo)
    
    assert exc.value.details["error_code"] == ErrorCodes.INVALID_OUTPUT_SCHEMA.value

@pytest.mark.asyncio
async def test_judge_fail_fast_score_out_of_bounds(judge_agent, mock_repo):
    """Verify JudgeAgent fails fast if score is out of DB bounds (Strict Authority)."""
    
    llm_output = JudgeDTO(
        matrix_id="test_matrix",
        thought_process="Thinking...",
        conclusion="Invalid score.",
        confidence_score=1.0,
        scale_min=1.0,
        scale_max=5.0,
        score_card=JudgeScoreCard(
            agent_name="TestJudge",
            total_score=5.0,
            max_score=5,
            verdict="Overflow",
            scale_min=1.0,
            scale_max=5.0,
            dimensions=[
                DimensionResultItem(dimension_id="dim1", dimension_label="D1", score=100.0, reasoning="Overflow")
            ]
        )
    )
    
    judge_agent.get_model_response = AsyncMock(return_value=llm_output)
    
    input_data = JudgeInput(history_text="C", product_text="P")
    context = {"matrix_id": "test_matrix", "scoring_logic": "standard", "monitored_steps": {"step_analyst": "Analyst"}}

    with pytest.raises(AgentExecutionError) as exc:
        await judge_agent.execute(input_data, execution_context=context, repository=mock_repo)
        
    assert exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
