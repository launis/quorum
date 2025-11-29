from typing import Any
from backend.agents.base import BaseAgent

class AnalystAgent(BaseAgent):
    """
    Analyytikko-agentti (Analyst Agent).
    Responsible for:
    1. Evidence Anchoring (Todistepohjainen Ankkurointi)
    2. Creating an 'Evidence Map' (Todistuskartta)
    """

    def _process(self, **kwargs) -> dict[str, Any]:
        """
        Processes the input using the Analyst Agent's logic.
        """
        
        # The input 'safe_data' (or similar) comes from GuardAgent's output (TaintedData).
        # However, the engine passes 'current_inputs' which contains the accumulated context.
        # We expect 'data' (from TaintedData) or 'safe_data' to be available.
        # Actually, GuardAgent returns a dict which updates the context.
        # GuardAgent returned a dict which might be the TaintedData object itself or wrapped.
        # Let's assume the context has the relevant keys.
        
        # The prompt requires: 1_tainted_data.json (Step 1 Output).
        # We can pass the relevant parts of the context to the LLM.
        
        # Construct the user content
        # We dump the relevant context as JSON string for the LLM to analyze.
        import json
        
        # Filter context to avoid passing too much noise if possible, 
        # but for now let's pass the relevant keys if they exist.
        relevant_keys = ['data', 'security_check', 'metodologinen_loki']
        input_data = {k: kwargs.get(k) for k in relevant_keys if k in kwargs}
        
        # If input_data is empty, maybe the keys are different (e.g. from GuardAgent's return)
        if not input_data:
             # Fallback: pass all kwargs except system_instruction
             input_data = {k: v for k, v in kwargs.items() if k != 'system_instruction'}

        user_content = f"""
        INPUT DATA (TaintedData):
        ---
        {json.dumps(input_data, indent=2, ensure_ascii=False)}
        ---
        """
        
        system_instruction = kwargs.get('system_instruction')
        
        # Call LLM with Retry Logic
        return self.get_json_response(
            prompt=user_content,
            system_instruction=system_instruction
        )
