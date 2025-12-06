from typing import Any, Optional, Type
from backend.agents.base import BaseAgent
from backend.state import WorkflowState
from backend.schemas import ArgumentaatioAnalyysi
from pydantic import BaseModel

class LogicianAgent(BaseAgent):
    """
    Loogikko-agentti (Logician Agent).
    Responsible for:
    1. Argument Construction (Argumentaation Rakentaminen)
    2. Applying Cognitive Assessment Matrix (Bloom/Toulmin)
    """

    def construct_user_prompt(self, state: WorkflowState) -> str:
        # Logician needs the Evidence Map from the previous step + Raw Data
        evidence_map = state.step_2_analyst.model_dump_json(indent=2) if state.step_2_analyst else "N/A"
        
        return f"""
        INPUT DATA:
        ---
        TODISTUSKARTTA (Edellisestä vaiheesta):
        {evidence_map}
        ---
        KESKUSTELUHISTORIA:
        {state.inputs.history_text}
        
        LOPPUTUOTE:
        {state.inputs.product_text}
        ---
        """

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return ArgumentaatioAnalyysi

    def get_system_instruction(self) -> str:
        return """
        You are the Logician Agent. Your task is to evaluate the logical structure of the student's argumentation.
        
        1. Apply the Toulmin Argumentation Model (Claim, Data, Warrant, Backing).
        2. Assess the Cognitive Level using Bloom's Taxonomy.
        3. Identify any Argumentation Schemes (Walton).
        
        Output must be a valid JSON object matching the ArgumentaatioAnalyysi schema.
        """

    def _update_state(self, state: WorkflowState, response_data: Any) -> WorkflowState:
        try:
            validated_data = ArgumentaatioAnalyysi(**response_data)
            state.step_3_logician = validated_data
        except Exception as e:
            print(f"[LogicianAgent] State update failed: {e}")
            raise e
        return state
