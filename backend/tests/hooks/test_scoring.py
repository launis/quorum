import pytest
import logging
from backend.models.state import WorkflowState
from backend.hooks.scoring import apply_scoring_logic, enforce_passivity_penalty
from backend.exceptions import AppException
from backend.models.domain.judge import JudgeOutput, JudgeScoreCard, DimensionResultItem

# Setup Logger
logger = logging.getLogger(__name__)

@pytest.fixture
def mock_state():
    return WorkflowState(workflow_id="test-wf")

def test_apply_scoring_missing_judge(mock_state):
    """Graceful Handling: Missing judge output should log warning but not crash."""
    # Should NOT raise exception
    new_state = apply_scoring_logic(mock_state)
    
    # Verify result context exists but score is 0
    # (Result is stored in 'scoring_result')
    assert "scoring_result" in new_state.context_variables
    res = new_state.context_variables["scoring_result"]
    assert res.total_score == 0.0

def test_passivity_invalid_dict_rejected(mock_state):
    """FAIL FAST: Invalid Dict (missing fields) should fail inflation and raise rejection."""
    # Use Functional Update
    state = mock_state.model_copy(update={
        "context_variables": {
            "step_judge": {
                "some_other_field": "val"
                # Missing 'score_card' etc -> Inflation fails
            }
        }
    })
    
    with pytest.raises(AppException) as exc:
        enforce_passivity_penalty(state)
    
    # New logic raises SCORING_LEGACY_DATA_REJECTED if inflation fails
    assert "SCORING_LEGACY_DATA_REJECTED" in str(exc.value.details)

def test_passivity_legacy_dict_accepted(mock_state):
    """GraphEngine Compatibility: Valid dictionaries must be inflated to Pydantic models."""
    # Construct a valid dict that mimics GraphEngine storage
    valid_judge_dict = {
        "matrix_id": "test_matrix",
        "scale_min": 1.0,
        "scale_max": 5.0,
        "thought_process": "thinking...",
        "conclusion": "concluded",
        "confidence_score": 0.9,
        "score_card": {
            "agent_name": "TestAgent",
            "total_score": 4.0,
            "max_score": 5.0,
            "verdict": "Pass",
            "scale_min": 1.0,
            "scale_max": 5.0,
            "dimensions": [
                {"dimension_id": "d1", "score": 1.0, "reasoning": "bad"} 
            ]
        }
    }
    
    state = mock_state.model_copy(update={
        "context_variables": {
            "step_judge": valid_judge_dict
        }
    })
    
    # Should NOT raise exception anymore
    new_state = enforce_passivity_penalty(state)
    
    # Verify inflation happens
    judge_out = new_state.context_variables["step_judge"]
    assert isinstance(judge_out, JudgeOutput)
    
    # Verify penalty applied (Dimensions[0].score is 1.0 == min)
    # Default multiplier is 1.0 in settings mock? 
    # We might need to check if penalty logic ran.
    # But primarily we are testing that it did NOT crash and DID inflate.
    assert judge_out.score_card.total_score == 4.0

def test_apply_scoring_invalid_dict_rejected(mock_state):
    """FAIL FAST: Apply Scoring Hook must reject invalid dictionaries."""
    state = mock_state.model_copy(update={
        "context_variables": {
            "step_judge": {"bad_key": "val"} # Invalid schema
        }
    })
    
    with pytest.raises(AppException) as exc:
        apply_scoring_logic(state)
        
    assert "SCORING_LEGACY_DATA_REJECTED" in str(exc.value.details)
