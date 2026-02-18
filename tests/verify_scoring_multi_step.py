
import logging
import uuid
import sys
import os

# Ensure backend matches path
sys.path.append(os.getcwd())

from datetime import datetime
from backend.hooks.scoring import apply_scoring_logic
from backend.models.state import WorkflowState
from backend.models.domain.evaluation import EvaluationResult, DimensionResultItem

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def create_mock_result(score: float, verdict: str) -> EvaluationResult:
    return EvaluationResult(
        matrix_id="test_matrix",
        timestamp=datetime.now(),
        total_score=score,
        final_verdict=verdict,
        dimensions=[
            DimensionResultItem(
                dimension_id="dim1",
                dimension_label="Test Dim",
                score=score,
                reasoning="Generic reasoning"
            )
        ],
        scale_min=1.0,
        scale_max=5.0,
        thought_process="Thinking...",
        conclusion="Conclusion...",
        confidence_score=0.9
    )

def test_scenario(name: str, context: dict):
    logger.info(f"--- TESTING SCENARIO: {name} ---")
    
    state = WorkflowState(
        execution_id=uuid.uuid4(),
        workflow_id="wf_test",
        context_variables=context
    )

    try:
        new_state = apply_scoring_logic(state)
        ctx = new_state.context_variables
        
        # Verify step_judge
        if "step_judge" in context:
            res = ctx.get("step_judge")
            val = res.total_score if isinstance(res, EvaluationResult) else res.get("total_score")
            logger.info(f"  step_judge score: {val} (Expected: {context['step_judge']['total_score']})")
            
        # Verify step_judge_cognitive
        if "step_judge_cognitive" in context:
            res = ctx.get("step_judge_cognitive")
            val = res.total_score if isinstance(res, EvaluationResult) else res.get("total_score")
            logger.info(f"  step_judge_cognitive score: {val} (Expected: {context['step_judge_cognitive']['total_score']})")
            
        logger.info(f"  [PASS] {name}")
        
    except Exception as e:
        logger.error(f"  [FAIL] {name}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 1. step_judge only
    r1 = create_mock_result(3.0, "Pass").model_dump()
    test_scenario("Step Judge Only", {"step_judge": r1})

    # 2. step_judge_cognitive only
    r2 = create_mock_result(4.0, "Excellent").model_dump()
    test_scenario("Cognitive Only", {"step_judge_cognitive": r2})

    # 3. Both
    test_scenario("Both Steps", {"step_judge": r1, "step_judge_cognitive": r2})
