from typing import Any, Dict
from backend.agents.base import BaseAgent
import json

class PanelAgent(BaseAgent):
    """
    Paneeli-agentti (Panel Agent).
    Executes multiple critical roles in a single LLM call to save tokens and time.
    """
    
    def construct_user_prompt(self, **kwargs) -> str:
        # Collect all relevant data for all potential critics
        relevant_keys = [
            'todistuskartta', 'argumentaatioanalyysi', 'data', 
            'metodologinen_loki', 'google_search_results',
            'history_text', 'product_text', 'reflection_text'
        ]
        input_data = {k: kwargs.get(k) for k in relevant_keys if k in kwargs}
        
        return f"""
        INPUT DATA FOR THE PANEL:
        ---
        {json.dumps(input_data, indent=2, ensure_ascii=False)}
        ---
        ULKOISEN FAKTANTARKISTUKSEN TULOKSET (jos saatavilla):
        {kwargs.get('google_search_results', 'Ei hakutuloksia.')}
        ---
        """

    def _process(self, **kwargs) -> Dict[str, Any]:
        user_content = self.construct_user_prompt(**kwargs)
        system_instruction = kwargs.get('system_instruction', "")
        
        # Append the Meta-Instruction for JSON formatting
        # We assume the system_instruction already contains the instructions for the sub-roles.
        # We just need to enforce the combined output structure.
        
        meta_instruction = """
        
        ### PANEL OUTPUT INSTRUCTION ###
        You are acting as a PANEL of critics. You have received instructions for multiple roles above.
        You must perform ALL these roles concurrently based on the same input data.
        
        REQUIRED OUTPUT FORMAT:
        Return a SINGLE JSON object where the top-level keys correspond to the output of each role.
        Based on the instructions provided, you should include keys such as:
        - "logiikka_auditointi" (for Logical Falsifier)
        - "kausaalinen_auditointi" (for Causal Analyst)
        - "performatiivisuus_auditointi" (for Performativity Detector)
        - "etiikka_ja_fakta" (for Factual Overseer)
        
        Example:
        {
            "logiikka_auditointi": { ... },
            "kausaalinen_auditointi": { ... },
            ...
        }
        
        Ensure each sub-object strictly follows the schema defined in its respective instruction.
        """
        
        full_system_instruction = system_instruction + meta_instruction
        
        # Call LLM
        response = self.get_json_response(
            prompt=user_content,
            system_instruction=full_system_instruction
        )
        
        # The response is already a dict.
        # We return it directly. The WorkflowEngine will merge this dict into the context.
        # So context['logiikka_auditointi'] will be populated.
        return response
