from typing import Any
from backend.agents.base import BaseAgent

class LogicianAgent(BaseAgent):
    """
    Loogikko-agentti (Logician Agent).
    Responsible for:
    1. Argument Construction (Argumentaation Rakentaminen)
    2. Applying Cognitive Assessment Matrix (Bloom/Toulmin)
    """

    def _process(self, **kwargs) -> dict[str, Any]:
        """
        Processes the input using the Logician Agent's logic.
        """
        
        # We expect inputs from previous steps (Guard, Analyst) in kwargs.
        # Specifically, we need 2_todistuskartta.json (Analyst output) and 1_tainted_data.json (Guard output).
        
        import json
        
        # Filter context
        # We need 'hypoteesit', 'rag_todisteet' from Analyst
        # And 'data' from Guard (TaintedData)
        
        relevant_keys = ['hypoteesit', 'rag_todisteet', 'data', 'metodologinen_loki']
        input_data = {k: kwargs.get(k) for k in relevant_keys if k in kwargs}
        
        if not input_data:
             input_data = {k: v for k, v in kwargs.items() if k != 'system_instruction'}

        user_content = f"""
        INPUT DATA (TodistusKartta & TaintedData):
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
