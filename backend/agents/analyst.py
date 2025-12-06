from typing import Any, Optional, Type
from backend.agents.base import BaseAgent
from backend.state import WorkflowState
from backend.schemas import TodistusKartta
from pydantic import BaseModel

class AnalystAgent(BaseAgent):
    """
    Analyytikko-agentti (Analyst Agent).
    Responsible for:
    1. Evidence Anchoring (Todistepohjainen Ankkurointi)
    2. Creating an 'Evidence Map' (Todistuskartta)
    """

    def construct_user_prompt(self, state: WorkflowState) -> str:
        inputs = state.inputs
        
        # Get Example
        example_text = self.get_schema_example(TodistusKartta)

        # We need the full text for analysis
        return f"""
        TASK: Analyze the input data and create an Evidence Map.

        {example_text}

        INPUT DATA FOR ANALYSIS:
        ---
        KESKUSTELUHISTORIA:
        {inputs.history_text}
        
        LOPPUTUOTE:
        {inputs.product_text}
        
        REFLEKTIODOKUMENTTI:
        {inputs.reflection_text}
        ---
        """

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return TodistusKartta

    def get_system_instruction(self) -> str:
        return """
        You are the Analyst Agent. Your task is to analyze the input data and create an Evidence Map (Todistuskartta).
        
        1. Identify key claims or hypotheses about the student's work.
        2. Find concrete evidence (quotes) from the input texts to support or refute these claims.
        3. Assign a relevance score (1-10) to each piece of evidence.
        
        Output must be a valid JSON object matching the TodistusKartta schema.
        """

    def _update_state(self, state: WorkflowState, response_data: Any) -> WorkflowState:
        try:
            validated_data = TodistusKartta(**response_data)
            state.step_2_analyst = validated_data
        except Exception as e:
            print(f"[AnalystAgent] State update failed: {e}")
            raise e
        return state
