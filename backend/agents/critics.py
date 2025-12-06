from typing import Any, Optional, Type
import os
import json
from googleapiclient.discovery import build
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
        
        # Get Example
        example_text = self.get_schema_example(LogiikkaAuditointi)

        return f"""
        TASK: Stress-test the student's logic.

        {example_text}

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
        
        # Get Example
        example_text = self.get_schema_example(EtiikkaJaFakta)

        return f"""
        TASK: Verify facts and check for ethical issues.

        {example_text}

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

    def execute_google_search(self, state: WorkflowState) -> WorkflowState:
        """
        HOOK: execute_google_search
        Executes Google Search based on hypotheses.
        """
        print("[FactualOverseerAgent] Running execute_google_search...")
        
        api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        cx = os.getenv("GOOGLE_SEARCH_CX")
        
        if not api_key or not cx:
            print("   [Warning] Missing GOOGLE_SEARCH_API_KEY or GOOGLE_SEARCH_CX")
            state.aux_data['google_search_results'] = "Search disabled (Missing API Keys)"
            return state

        queries = []
        
        # Extract queries from Hypotheses (Step 2 Analyst)
        if state.step_2_analyst and state.step_2_analyst.hypoteesit:
            print(f"   [HOOK] Found {len(state.step_2_analyst.hypoteesit)} hypotheses.")
            for hyp in state.step_2_analyst.hypoteesit:
                if hyp.vaite_teksti:
                    q = hyp.vaite_teksti[:150]
                    queries.append(q)
        else:
             print("   [HOOK] No hypotheses found. Using fallback.")
             queries.append("Cognitive Quorum verification")

        all_results = []
        try:
            service = build("customsearch", "v1", developerKey=api_key)
            
            # Limit to top 3 queries
            for i, query in enumerate(queries[:3]): 
                print(f"   Query {i+1}: {query}")
                try:
                    res = service.cse().list(q=query, cx=cx, num=3).execute()
                    
                    for item in res.get('items', []):
                        all_results.append({
                            "query": query,
                            "title": item.get('title'),
                            "link": item.get('link'),
                            "snippet": item.get('snippet')
                        })
                except Exception as q_err:
                    print(f"   Query '{query}' failed: {q_err}")
                    
            state.aux_data['google_search_results'] = json.dumps(all_results, indent=2)
            
        except Exception as e:
            print(f"   Search failed: {e}")
            state.aux_data['google_search_results'] = f"Search failed: {str(e)}"

        return state


class CausalAnalystAgent(BaseAgent):
    """
    Kausaalinen Analyytikko-agentti (Causal Analyst).
    """
    def construct_user_prompt(self, state: WorkflowState) -> str:
        # Get Example
        example_text = self.get_schema_example(KausaalinenAuditointi)

        return f"""
        TASK: Verify the cause-and-effect relationship.

        {example_text}

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
        # Get Example
        example_text = self.get_schema_example(PerformatiivisuusAuditointi)

        return f"""
        TASK: Detect performativity or fake engagement.

        {example_text}

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

    def detect_performative_patterns(self, state: WorkflowState) -> WorkflowState:
        """
        HOOK: detect_performative_patterns
        Scans input for performative language patterns.
        """
        print("[PerformativityDetectorAgent] Running detect_performative_patterns...")
        
        suspect_patterns = [
            "delve into", "tapestry", "comprehensive overview", "rich history",
            "testament to", "underscore the importance", "pivotal role",
            "landscape of", "realm of", "foster a sense of"
        ]
        
        detected = []
        text_to_scan = (state.inputs.history_text or "") + (state.inputs.product_text or "")
        text_lower = text_to_scan.lower()
        
        for pattern in suspect_patterns:
            if pattern in text_lower:
                detected.append(pattern)
                
        if detected:
            print(f"   [HOOK] Detected patterns: {detected}")
            state.aux_data['performative_patterns_detected'] = json.dumps(detected)
        else:
            state.aux_data['performative_patterns_detected'] = "[]"
            
        return state
