import asyncio
import uuid
from typing import Any
from datetime import datetime

from backend.agents.xai import XAIReporterAgent
from backend.models.domain.xai import XAIReporterInput, XAIOutput
from backend.models.domain.judge import JudgeScoreCard, DimensionResultItem

# Mock the BaseAgent.execute to avoid LLM calls
class MockXAIReporterAgent(XAIReporterAgent):
    async def execute(self, input_data: XAIReporterInput, execution_context: dict[str, Any] | None = None, **kwargs) -> XAIOutput:
        # 1. Simulate super().execute() returning a base result
        # We manually construct what the LLM would return
        base_result = XAIOutput(
            reasoning_trace={
                "thought_process": "Mock thinking...",
                "conclusion": "Mock conclusion.",
                "confidence_score": 0.95
            },
            executive_summary="Mock Summary",
            analysis_strengths="Mock Strengths",
            analysis_weaknesses="Mock Weaknesses",
            analysis_opportunities="Mock Opportunities",
            analysis_recommendations="Mock Recommendations",
            final_verdict="Approved",
            confidence_score=0.95
        )
        
        # 2. RUN THE REAL LOGIC FROM THE AGENT (Copy-Paste or Inheritance?)
        # Since I can't easily call "super().execute()" in a way that skips the REAL BaseAgent.execute but runs XAIReporterAgent.execute...
        # Wait, XAIReporterAgent.execute CALLS super().execute().
        # I need to mock methods on the instance, or monkeypatch BaseAgent.execute.
        
        # Better approach:
        # Use the REAL XAIReporterAgent, but mock the `super().execute` call.
        # But `super()` is special.
        
        # Let's just copy the logic I want to test into a helper, or REPLICATE the logic here to assert it works if I were to run it?
        # No, I want to test the code I just wrote.
        
        # Option C: Use proper mocking with unittest.mock.
        pass

import unittest
from unittest.mock import MagicMock, patch

class TestXAIFlatGeneration(unittest.TestCase):
    def setUp(self):
        self.agent = XAIReporterAgent()

    @patch("backend.agents.base.BaseAgent.execute")
    def test_flat_report_generation(self, mock_base_execute):
        # Setup Mock Return from BaseAgent (LLM part)
        mock_base_execute.return_value = XAIOutput(
            reasoning_trace={"thought_process": "x", "conclusion": "y", "confidence_score": 0.9},
            executive_summary="Summary",
            analysis_strengths="S",
            analysis_weaknesses="W",
            analysis_opportunities="O",
            analysis_recommendations="R",
            final_verdict="Approved",
            confidence_score=0.9,
            score_cards=[] # Initially empty
        )

        # Execution Context
        exec_id = uuid.uuid4()
        context = {"execution_id": str(exec_id)}

        # Input Data (with Judge Scores)
        step_judge_data = {
            "matrix_id": "standard_v1",
            "score_card": {
                "agent_name": "Judge",
                "total_score": 4.5,
                "max_score": 5,
                "verdict": "Approved",
                "scale_min": 0.0,
                "scale_max": 5.0,
                "dimensions": [
                    {"dimension_id": "clarity", "dimension_label": "Clarity", "score": 5.0, "reasoning": "Clear"},
                    {"dimension_id": "logic", "dimension_label": "Logic", "score": 4.0, "reasoning": "Good"}
                ]
            }
        }
        
        input_data = XAIReporterInput(step_judge_1=step_judge_data)

        # Run Agent
        # We need an event loop for async
        result = asyncio.run(self.agent.execute(input_data, context))

        # Assertions
        print("\n--- Test Results ---")
        print(f"Flat Report Present: {result.flat_report is not None}")
        
        if result.flat_report:
            print(f"Execution ID: {result.flat_report.execution_id}")
            print(f"Flattened Scores: {result.flat_report.flattened_scores}")
            
            self.assertEqual(result.flat_report.execution_id, exec_id)
            self.assertEqual(result.flat_report.score_total, 4.5)
            self.assertEqual(result.flat_report.flattened_scores["clarity"], 5.0)
            self.assertEqual(result.flat_report.flattened_scores["logic"], 4.0)
            self.assertEqual(result.flat_report.top_strength_id, "clarity") # 5.0 > 4.0
            
            print("SUCCESS: Flat report generated correctly.")
        else:
            self.fail("Flat report was None")

if __name__ == "__main__":
    unittest.main()
