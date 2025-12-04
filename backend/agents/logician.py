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

    def _process(self, validation_schema: Any = None, **kwargs) -> dict[str, Any]:
        """
        Processes the input using the Logician Agent's logic.
        """
        user_content = self.construct_user_prompt(**kwargs)
        
        system_instruction = kwargs.get('system_instruction')
        
        # Call LLM with Retry Logic
        # Call LLM with Retry Logic
        # Pass validation_schema=None to allow manual validation after injection
        response = self.get_json_response(
            prompt=user_content,
            system_instruction=system_instruction,
            validation_schema=None
        )
        
        # --- AUTO-INJECT MISSING FIELDS ---
        if response:
            if 'toulmin_analyysi' not in response:
                print("[LogicianAgent] Warning: 'toulmin_analyysi' missing. Injecting empty list.")
                response['toulmin_analyysi'] = []
            
            if 'kognitiivinen_taso' not in response:
                print("[LogicianAgent] Warning: 'kognitiivinen_taso' missing. Injecting default.")
                response['kognitiivinen_taso'] = {
                    "bloom_taso": "Tuntematon",
                    "strateginen_syvyys": "Määrittelemätön"
                }
                
            if 'walton_skeema' not in response:
                print("[LogicianAgent] Warning: 'walton_skeema' missing. Injecting default.")
                response['walton_skeema'] = {
                    "tunnistettu_skeema": "Ei tunnistettu",
                    "kriittiset_kysymykset": []
                }

        # --- FINAL VALIDATION ---
        if validation_schema and response:
            try:
                print(f"[LogicianAgent] Validating against schema: {validation_schema.__name__}")
                validation_schema.model_validate(response)
                print("[LogicianAgent] Validation successful.")
            except Exception as e:
                print(f"[LogicianAgent] Validation failed after injection: {e}")
                pass

        return response
