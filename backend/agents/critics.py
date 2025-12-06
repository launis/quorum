from typing import Any, Optional, Type
from backend.agents.base import BaseAgent
from backend.state import WorkflowState
from backend.schemas import (
    LogiikkaAuditointi, 
    EtiikkaJaFakta, 
    KausaalinenAuditointi, 
    PerformatiivisuusAuditointi
)
from pydantic import BaseModel

class LogicalFalsifierAgent(BaseAgent):
    """
    Looginen Falsifioija-agentti (Logical Falsifier).
    """
    def construct_user_prompt(self, state: WorkflowState) -> str:
        # Needs Logician's output + Raw Data
        logician_output = state.step_3_logician.model_dump_json(indent=2) if state.step_3_logician else "N/A"
        
        return f"""
        INPUT DATA:
        ---
        ARGUMENTAATIOANALYYSI (Edellisestä vaiheesta):
        {logician_output}
        ---
        KESKUSTELUHISTORIA:
        {state.inputs.history_text}
        
        LOPPUTUOTE:
        {state.inputs.product_text}
        ---
        """

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return LogiikkaAuditointi

    def get_system_instruction(self) -> str:
        return """
        You are the Logical Falsifier Agent. Your task is to stress-test the student's logic.
        
        1. Perform a 'Walton Stress Test': Ask critical questions to challenge the arguments.
        2. Check for 'Post-Hoc Rationalization': Did the student invent reasons after the fact?
        
        Output must be a valid JSON object matching the LogiikkaAuditointi schema.
        """

    def _update_state(self, state: WorkflowState, response_data: Any) -> WorkflowState:
        try:
            state.step_4_falsifier = LogiikkaAuditointi(**response_data)
        except Exception as e:
            print(f"[LogicalFalsifierAgent] State update failed: {e}")
            raise e
        return state


class FactualOverseerAgent(BaseAgent):
    """
    Faktuaalinen ja Eettinen Valvoja-agentti (Factual & Ethical Overseer).
    """
    def construct_user_prompt(self, state: WorkflowState) -> str:
        # Needs Analyst's output + Search Results (if any)
        analyst_output = state.step_2_analyst.model_dump_json(indent=2) if state.step_2_analyst else "N/A"
        search_results = state.aux_data.get('google_search_results', 'Ei hakutuloksia.')
        
        return f"""
        INPUT DATA:
        ---
        TODISTUSKARTTA:
        {analyst_output}
        ---
        ULKOISEN FAKTANTARKISTUKSEN TULOKSET:
        {search_results}
        ---
        LOPPUTUOTE:
        {state.inputs.product_text}
        ---
        """

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return EtiikkaJaFakta

    def get_system_instruction(self) -> str:
        return """
        You are the Factual & Ethical Overseer. Your task is to verify facts and check for ethical issues.
        
        1. Verify claims against external search results (if provided) or general knowledge.
        2. Check for ethical violations (plagiarism, bias, harmful content).
        
        Output must be a valid JSON object matching the EtiikkaJaFakta schema.
        """

    def _update_state(self, state: WorkflowState, response_data: Any) -> WorkflowState:
        try:
            state.step_5_overseer = EtiikkaJaFakta(**response_data)
        except Exception as e:
            print(f"[FactualOverseerAgent] State update failed: {e}")
            raise e
        return state


class CausalAnalystAgent(BaseAgent):
    """
    Kausaalinen Analyytikko-agentti (Causal Analyst).
    """
    def construct_user_prompt(self, state: WorkflowState) -> str:
        return f"""
        INPUT DATA:
        ---
        KESKUSTELUHISTORIA:
        {state.inputs.history_text}
        
        REFLEKTIODOKUMENTTI:
        {state.inputs.reflection_text}
        ---
        """

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return KausaalinenAuditointi

    def get_system_instruction(self) -> str:
        return """
        You are the Causal Analyst. Your task is to verify the cause-and-effect relationship between the process and the product.
        
        1. Check if the timeline of events in the history matches the reflection.
        2. Perform a Counterfactual Test: "If X hadn't happened, would Y exist?"
        
        Output must be a valid JSON object matching the KausaalinenAuditointi schema.
        """

    def _update_state(self, state: WorkflowState, response_data: Any) -> WorkflowState:
        try:
            state.step_6_causal = KausaalinenAuditointi(**response_data)
        except Exception as e:
            print(f"[CausalAnalystAgent] State update failed: {e}")
            raise e
        return state


class PerformativityDetectorAgent(BaseAgent):
    """
    Performatiivisuuden Tunnistaja-agentti (Performativity Detector).
    """
    def construct_user_prompt(self, state: WorkflowState) -> str:
        return f"""
        INPUT DATA:
        ---
        KESKUSTELUHISTORIA:
        {state.inputs.history_text}
        
        REFLEKTIODOKUMENTTI:
        {state.inputs.reflection_text}
        ---
        """

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return PerformatiivisuusAuditointi

    def get_system_instruction(self) -> str:
        return """
        You are the Performativity Detector. Your task is to detect "theater" or fake engagement.
        
        1. Look for heuristics of performativity (e.g., overly formal language, lack of struggle).
        2. Perform a Pre-Mortem Analysis.
        3. Give an overall verdict: Organic vs. Performative.
        
        Output must be a valid JSON object matching the PerformatiivisuusAuditointi schema.
        """

    def _update_state(self, state: WorkflowState, response_data: Any) -> WorkflowState:
        try:
            state.step_7_detector = PerformatiivisuusAuditointi(**response_data)
        except Exception as e:
            print(f"[PerformativityDetectorAgent] State update failed: {e}")
            raise e
        return state
