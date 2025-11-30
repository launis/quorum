from typing import Any
from backend.agents.base import BaseAgent

class LogicianAgent(BaseAgent):
    """
    Loogikko-agentti (Logician Agent).
    Responsible for:
    1. Argument Construction (Argumentaation Rakentaminen)
    2. Applying Cognitive Assessment Matrix (Bloom/Toulmin)
    """

    def construct_user_prompt(self, **kwargs) -> str:
        import json
        
        relevant_keys = ['todistuskartta', 'metodologinen_loki']
        input_data = {k: kwargs.get(k) for k in relevant_keys if k in kwargs}
        
        if not input_data:
             # Fallback: Look for raw inputs if structured data missing
             fallback_keys = ['history_text', 'product_text', 'reflection_text']
             input_data = {k: kwargs.get(k) for k in fallback_keys if k in kwargs}
             if not input_data:
                 input_data = {"error": "No relevant input data found for LogicianAgent"}

        return f"""
        INPUT DATA:
        ---
        {json.dumps(input_data, indent=2, ensure_ascii=False)}
        ---
        """

    def _process(self, **kwargs) -> dict[str, Any]:
        """
        Processes the input using the Logician Agent's logic.
        """
        user_content = self.construct_user_prompt(**kwargs)
        
        system_instruction = kwargs.get('system_instruction')
        
        # Call LLM with Retry Logic
        return self.get_json_response(
            prompt=user_content,
            system_instruction=system_instruction
        )
