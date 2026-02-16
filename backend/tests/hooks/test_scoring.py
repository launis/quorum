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
    """FAIL FAST: Missing judge output must raise AppException."""
    # State default context_variables is empty, so this is already valid for the test case
    # strict immutability check: ensure we don't try to mutate it if we needed to.
    
    with pytest.raises(AppException) as exc:
        apply_scoring_logic(mock_state)
    
    assert exc.value.status_code == 500
    assert "SCORING_MISSING_JUDGE_OUTPUT" in str(exc.value.details)

def test_apply_scoring_missing_scale_max(mock_state):
    """FAIL FAST: Pydantic model missing scale_max must raise exception."""
    # Create invalid card with scale_max=0.0 (simulating missing) or explicit None if allowed by model (it has default 5.0)
    # But we want to test the check.
    # JudgeScoreCard has default=5.0. So to trigger the error, we'd need to manually set it to 0.0 or something.
    # The code checks `if not score_card.scale_max`.
    
    dim = DimensionResultItem(dimension_id="d1", score=3.0, reasoning="ok")
    card = JudgeScoreCard(
        agent_name="Test", total_score=3.0, max_score=5, verdict="ok",
        dimensions=[dim], scale_min=1.0, scale_max=0.0 # Force 0.0 to trigger check
    )
    output = JudgeOutput(
        thought_process="think", conclusion="conc", confidence_score=1.0,
        score_card=card, scale_min=1.0, scale_max=0.0
    )
    
    # Use Functional Update
    state = mock_state.model_copy(update={"context_variables": {"step_judge": output}})
    
    with pytest.raises(AppException) as exc:
        apply_scoring_logic(state)
        
    assert "SCORING_MISSING_SCALE_MAX" in str(exc.value.details)

def test_passivity_missing_fields(mock_state):
    """FAIL FAST: Dict missing required fields should raise SCORING_MISSING_FIELD."""
    # Use Functional Update
    state = mock_state.model_copy(update={
        "context_variables": {
            "step_judge": {
                "some_other_field": "val"
            }
        }
    })
    
    with pytest.raises(AppException) as exc:
        enforce_passivity_penalty(state)
    
    assert "SCORING_MISSING_FIELD" in str(exc.value.details)

def test_passivity_legacy_dict_mutation_rejected(mock_state):
    """Strict Mode: Logic should reject mutating a legacy dict if penalty applies."""
    # Construct a dict that WOULD trigger penalty (score 1.0 matches scale_min 1.0)
    # But since it is a dict, and we removed mutation support, it should raise SCORING_LEGACY_DATA_REJECTED.
    
    # We need to provide all fields so it passes input validation
    # Use Functional Update
    state = mock_state.model_copy(update={
        "context_variables": {
            "step_judge": {
                "score_card": {
                     "scale_min": 1.0,
                     "scale_max": 5.0,
                     "total_score": 4.0,
                     "dimensions": [
                          {"score": 1.0, "reasoning": "bad"} # Level 1 triggers detection
                     ]
                }
            }
        }
    })
    
    with pytest.raises(AppException) as exc:
        enforce_passivity_penalty(state)
        
    # It should fail when trying to apply the penalty
    assert "SCORING_LEGACY_DATA_REJECTED" in str(exc.value.details)
    assert "SCORING_LEGACY_DATA_REJECTED" in str(exc.value.details)
