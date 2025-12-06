from typing import Any, Optional, Type
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
        
        return f"""
        INPUT DATA (TUOMIO JA PISTEET):
        ---
        {judge_output}
        ---
        """

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return XAIReport

    def get_system_instruction(self) -> str:
        return """
        You are the XAI Reporter Agent. Your task is to generate a human-readable report for the student/teacher.
        
        1. Create an Executive Summary.
        2. Provide Detailed Analysis sections based on the scores.
        3. Give a Final Verdict and Confidence Score.
        
        Output must be a valid JSON object matching the XAIReport schema.
        """

    def _update_state(self, state: WorkflowState, response_data: Any) -> WorkflowState:
        try:
            state.step_9_reporter = XAIReport(**response_data)
        except Exception as e:
            print(f"[XAIReporterAgent] State update failed: {e}")
            raise e
        return state
