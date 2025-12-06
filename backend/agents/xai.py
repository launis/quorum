from typing import Any, Optional, Type
import re
from backend.agents.base import BaseAgent
from backend.state import WorkflowState
from backend.schemas import XAIReport
from pydantic import BaseModel

class XAIReporterAgent(BaseAgent):
    """
    XAI-Raportoija-agentti (XAI Reporter Agent).
    """
    def construct_user_prompt(self, state: WorkflowState) -> str:
        # Reporter needs the final verdict and scores
        judge_output = state.step_8_judge.model_dump_json(indent=2) if state.step_8_judge else "N/A"
        
        # Get Example
        example_text = self.get_schema_example(XAIReport)

        return f"""
        TASK: Generate a human-readable report.

        {example_text}

        INPUT DATA (TUOMIO JA PISTEET):
        ---
        {judge_output}
        ---
        """

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return XAIReport

    def get_system_instruction(self) -> str:
        return """
        You are the XAI Reporter Agent. Your task is to generate the content for a structured report based on the provided Audit and Scores.

        CRITICAL INSTRUCTIONS FOR JSON FIELDS:
        1. 'executive_summary': A concise text summary of the audit. Do NOT use structural headers.
        2. 'analysis_strengths': Detailed analysis of the strengths and what went well.
        3. 'analysis_weaknesses': Detailed analysis of weaknesses, limitations, and errors found.
        4. 'analysis_opportunities': Insights, "Supermegatrends", or future potential identified.
        5. 'analysis_recommendations': Concrete recommendations for improvement or next steps.
        6. 'final_verdict': A short concluding statement.
        7. 'confidence_score': Luottamustaso (0.0-1.0).

        Output must be a valid JSON object matching the XAIReport schema.
        """

    def _update_state(self, state: WorkflowState, response_data: Any) -> WorkflowState:
        try:
            state.step_9_reporter = XAIReport(**response_data)
        except Exception as e:
            print(f"[XAIReporterAgent] State update failed: {e}")
            raise e
        return state
