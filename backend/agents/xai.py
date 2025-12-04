from typing import Any
import json
from backend.agents.base import BaseAgent

class XAIReportAgent(BaseAgent):
    """
    XAI Reporter Agent (Step 9).
    Generates the final Explainable AI report based on all previous steps.
    """

    def construct_user_prompt(self, **kwargs) -> str:
        """
        Constructs the prompt for the XAI Reporter.
        It needs access to the outputs of all previous agents.
        """
        # Filter out very large raw texts to save tokens, as the agent relies on the structured analysis from previous steps.
        # However, we keep 'product_text' if it's not too huge, or rely on the analyses.
        
        # We want to pass the structured JSON outputs from previous steps.
        # These are usually passed as kwargs matching their keys in the context.
        
        relevant_keys = [
            '1_tainted_data.json',
            '2_todistuskartta.json',
            '3_argumentaatioanalyysi.json',
            '4_logiikka_auditointi.json',
            '5_kausaalinen_auditointi.json',
            '6_performatiivisuus_auditointi.json',
            '7_falsifiointi_ja_etiikka.json',
            '8_tuomio_ja_pisteet.json'
        ]
        
        input_data = {}
        for k in relevant_keys:
            if k in kwargs:
                input_data[k] = kwargs[k]
            elif k.split('.')[0] in kwargs: # Handle cases where extension is dropped or key is different
                 input_data[k] = kwargs[k.split('.')[0]]
        
        # Also include metadata if available
        if 'metadata' in kwargs:
            input_data['metadata'] = kwargs['metadata']

        return f"""
INPUT DATA (Previous Analysis Steps):
---
{json.dumps(input_data, indent=2, ensure_ascii=False, default=str)}
---
"""

    def _process(self, validation_schema: Any = None, **kwargs) -> dict[str, Any]:
        # Construct prompt
        user_prompt = self.construct_user_prompt(**kwargs)
        
        # Get system instruction (usually passed in kwargs or fetched from DB by engine)
        system_instruction = kwargs.get('system_instruction')
        
        # Call LLM
        # We use a higher retry count here as this is the final step
        response = self.get_json_response(
            user_prompt, 
            system_instruction, 
            max_retries=3,
            validation_schema=validation_schema
        )
        
        return response
