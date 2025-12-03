from typing import Any
from backend.agents.base import BaseAgent

class AnalystAgent(BaseAgent):
    """
    Analyytikko-agentti (Analyst Agent).
    Responsible for:
    1. Evidence Anchoring (Todistepohjainen Ankkurointi)
    2. Creating an 'Evidence Map' (Todistuskartta)
    """

    def construct_user_prompt(self, **kwargs) -> str:
        import json
        
        # Prioritize safe_data if available, otherwise look for data
        relevant_keys = ['safe_data', 'data', 'security_check', 'metodologinen_loki', 'metadata']
        input_data = {k: kwargs.get(k) for k in relevant_keys if k in kwargs}
        
        # DEBUG: Verify data content
        if 'data' in input_data:
            print(f"[AnalystAgent] 'data' keys: {list(input_data['data'].keys())}")
            for k, v in input_data['data'].items():
                print(f"[AnalystAgent] 'data[{k}]' length: {len(str(v))}")
        
        if not input_data:
             # Fallback: Try to find 'history_text' etc directly if no structured data found
             # But DO NOT dump everything.
             fallback_keys = ['history_text', 'product_text', 'reflection_text']
             input_data = {k: kwargs.get(k) for k in fallback_keys if k in kwargs}
             if not input_data:
                 input_data = {"error": "No relevant input data found for AnalystAgent"}

        return f"""
        INPUT DATA:
        ---
        {json.dumps(input_data, indent=2, ensure_ascii=False)}
        ---
        """

    def _process(self, validation_schema: Any = None, **kwargs) -> dict[str, Any]:
        """
        Processes the input using the Analyst Agent's logic.
        """
        user_content = self.construct_user_prompt(**kwargs)
        
        system_instruction = kwargs.get('system_instruction')
        
        # Call LLM with Retry Logic
        return self.get_json_response(
            prompt=user_content,
            system_instruction=system_instruction,
            validation_schema=validation_schema
        )
