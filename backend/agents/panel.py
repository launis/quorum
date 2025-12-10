from typing import Any, Dict
from backend.agents.base import BaseAgent
import json
import logging

logger = logging.getLogger(__name__)

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

    async def execute(self, system_instruction: str = None, **kwargs) -> Dict[str, Any]:
        user_content = self.construct_user_prompt(**kwargs)
        
        # Append the Meta-Instruction for JSON formatting
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
        
        full_system_instruction = (system_instruction or "") + meta_instruction
        
        # Call LLM
        response = await self.llm_provider.generate(
            prompt=user_content,
            system_instruction=full_system_instruction,
            response_schema=None
        )
        
        # Parse JSON if response is a string
        if isinstance(response, str):
            try:
                # Basic cleanup for markdown code blocks
                clean_txt = response.strip()
                if clean_txt.startswith("```"):
                     clean_txt = clean_txt.split("\n", 1)[1]
                     if clean_txt.endswith("```"):
                         clean_txt = clean_txt.rsplit("\n", 1)[0]
                return json.loads(clean_txt)
            except json.JSONDecodeError as e:
                # If parsing fails, return as error or raw text wrapped
                logger.error(f"Failed to parse JSON response: {e}")
                return {"error": "Failed to parse JSON", "raw_response": response}
        
        return response
