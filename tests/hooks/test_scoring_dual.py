
import pytest
from backend.models.state import WorkflowState
from backend.hooks.scoring import enforce_passivity_penalty, apply_scoring_logic
from backend.models.domain.judge import JudgeOutput, JudgeScoreCard, DimensionResultItem
from backend.models.domain import ScoringResult

def test_dual_judge_passivity():
    print("Testing Dual Judge Passivity...")
    
    # Setup: 2 Judges. 
    # Standard: Pass (5.0)
    # Cognitive: Fail/Passive (1.0 on min scale 1.0)
    
    dim_ok = DimensionResultItem(dimension_id="d1", score=5.0, reasoning="perfect")
    dim_bad = DimensionResultItem(dimension_id="d2", score=1.0, reasoning="lazy") # trigger
    
    card_ok = JudgeScoreCard(agent_name="Standard", total_score=5.0, max_score=5, verdict="ok", dimensions=[dim_ok], scale_min=1.0, scale_max=5.0)
    card_bad = JudgeScoreCard(agent_name="Cognitive", total_score=4.0, max_score=5, verdict="lazy", dimensions=[dim_bad], scale_min=1.0, scale_max=5.0)
    
    judge_ok = JudgeOutput(thought_process="t", conclusion="c", confidence_score=1.0, score_card=card_ok, matrix_id="m1", scale_min=1.0, scale_max=5.0)
    judge_bad = JudgeOutput(thought_process="t", conclusion="c", confidence_score=1.0, score_card=card_bad, matrix_id="m1", scale_min=1.0, scale_max=5.0)
    
    mock_state = WorkflowState(workflow_id="test-dual", context_variables={
        "step_judge": judge_ok,
        "step_judge_cognitive": judge_bad
    })
    
    # 1. Test Passivity Enforcement
    new_state = enforce_passivity_penalty(mock_state)
    ctx = new_state.context_variables
    
    # Standard should be unset (unchanged implies original reference if not deep copied, but here we replace model)
    # Actually logic: if no change, it remains. 
    j1 = ctx["step_judge"]
    j2 = ctx["step_judge_cognitive"]
    
    # Verify Standard did NOT get penalty
    if j1.score_card.total_score != 5.0:
        print(f"FAIL: Standard score {j1.score_card.total_score} != 5.0")
        pytest.fail("Standard judge penalized incorrectly")
        
    # Verify Cognitive DID get penalty (Halved: 4.0 -> 2.0)
    if j2.score_card.total_score != 2.0:
        print(f"FAIL: Cognitive score {j2.score_card.total_score} != 2.0")
        pytest.fail("Cognitive judge NOT penalized")
        
    print("SUCCESS: Passivity applied correctly to partial set.")

def test_dual_judge_aggregation():
    print("Testing Dual Judge Aggregation...")
    
    dim_ok = DimensionResultItem(dimension_id="d1", score=5.0, reasoning="perfect")
    card1 = JudgeScoreCard(agent_name="Standard", total_score=5.0, max_score=5, verdict="ok", dimensions=[dim_ok], scale_min=1.0, scale_max=5.0)
    card2 = JudgeScoreCard(agent_name="Cognitive", total_score=3.0, max_score=5, verdict="ok", dimensions=[dim_ok], scale_min=1.0, scale_max=5.0)
    
    judge1 = JudgeOutput(thought_process="t", conclusion="c", confidence_score=1.0, score_card=card1, matrix_id="m1", scale_min=1.0, scale_max=5.0)
    judge2 = JudgeOutput(thought_process="t", conclusion="c", confidence_score=1.0, score_card=card2, matrix_id="m1", scale_min=1.0, scale_max=5.0)
    
    mock_state = WorkflowState(workflow_id="test-dual-agg", context_variables={
        "step_judge": judge1,
        "step_judge_cognitive": judge2
    })
    
    final_state = apply_scoring_logic(mock_state)
    result = final_state.context_variables.get("scoring_result")
    
    if not isinstance(result, ScoringResult):
        pytest.fail("No scoring result produced")
        
    # Average: (5.0 + 3.0) / 2 = 4.0
    if result.total_score != 4.0:
        print(f"FAIL: Expected 4.0, got {result.total_score}")
        pytest.fail(f"Aggregation failed. Got {result.total_score}")
        
    print("SUCCESS: Aggregation correct.")

if __name__ == "__main__":
    test_dual_judge_passivity()
    test_dual_judge_aggregation()
