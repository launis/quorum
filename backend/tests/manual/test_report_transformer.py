import sys
import os
import unittest
import traceback
from typing import Any

# Ensure cwd is in path
sys.path.append(os.getcwd())

from backend.models.state import WorkflowState
# from backend.models.domain.inputs import WorkflowInputs # Not needed if not used
from backend.models.domain.xai import XAIOutput
from backend.models.domain.judge import JudgeOutput, JudgeScoreCard, DimensionResultItem
from backend.models.view.report_view import ExecutionReportView
from backend.api.transformers.report_transformer import ReportTransformer

class TestReportTransformer(unittest.TestCase):
    def test_transform_success(self):
        print("\n--- Testing Report Transformer Success ---")
        try:
            # 1. Setup State
            state = WorkflowState(workflow_id="test_transformer")

            # 2. Inject Mock Agent Outputs
            xai_out = XAIOutput(
                thought_process="Thinking",
                conclusion="Done",
                confidence_score=0.95,
                executive_summary="Excellent work.",
                analysis_strengths="Strength",
                analysis_weaknesses="None",
                analysis_opportunities="None",
                analysis_recommendations="Keep it up",
                final_verdict="Approved",
                score_cards=[
                     JudgeScoreCard(
                        agent_name="Judge 1",
                        total_score=4.8,
                        max_score=5,
                        verdict="Approved",
                        scale_min=0.0,
                        scale_max=5.0,
                        dimensions=[
                            DimensionResultItem(dimension_id="d1", dimension_label="Clarity", score=5.0, reasoning="Very clear"),
                            DimensionResultItem(dimension_id="d2", dimension_label="Logic", score=4.6, reasoning="Good logic")
                        ]
                     )
                ]
            )
            state.context_variables["step_xai"] = xai_out.model_dump()
            
            # 3. Transform
            view = ReportTransformer.transform(state)
            
            # 4. Assertions
            print("View generated successfully.")
            
            self.assertEqual(view.execution_id, "test_transformer")
            self.assertEqual(view.summary_section.content, "Excellent work.")
            self.assertEqual(view.score_section.average, 4.8)
            
            print("Success Test Passed")
        except Exception:
            traceback.print_exc()
            self.fail("Success test raised exception")

    def test_transform_fail_fast(self):
        print("\n--- Testing Fail Fast (Missing XAI) ---")
        try:
            state = WorkflowState(workflow_id="fail_test")
            
            with self.assertRaises(Exception) as cm:
                ReportTransformer.transform(state)
            
            print(f"Caught expected exception: {cm.exception}")
            self.assertIn("Report generation pending or failed", str(cm.exception))
            print("Fail Fast Test Passed")
        except Exception:
            traceback.print_exc()
            self.fail("Fail Fast test failed with unexpected exception")

if __name__ == "__main__":
    unittest.main()
