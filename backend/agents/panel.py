from typing import Any, Dict, Optional
from backend.agents.base import BaseAgent
from backend.models.state import WorkflowState
from backend.models.domain import (
    LogiikkaAuditointi,
    KausaalinenAuditointi,
    PerformatiivisuusAuditointi,
    EtiikkaJaFakta
)
import json
import logging

logger = logging.getLogger(__name__)

class PanelAgent(BaseAgent):
    """
    Paneeli-agentti (Panel Agent).
    Executes multiple critical roles in a single LLM call to save tokens and time.
    """
    
    def construct_user_prompt(self, state: WorkflowState) -> str:
        # Collect all relevant data for all potential critics from the state
        # Utilizing previous steps' outputs if available
        input_data = {
            "inputs": {
                "history_text": state.inputs.history_text,
                "product_text": state.inputs.product_text,
                "reflection_text": state.inputs.reflection_text
            }
        }

        # Add available intermediate results
        if state.step_analyst:
            input_data["todistuskartta"] = state.step_analyst.model_dump(mode='json')
        if state.step_logician:
            input_data["argumentaatioanalyysi"] = state.step_logician.model_dump(mode='json')
            
        # Add aux data if relevant (like search results)
        google_search_results = state.aux_data.get('google_search_results', 'Ei hakutuloksia.')
        
        return f"""
        INPUT DATA FOR THE PANEL:
        ---
        {json.dumps(input_data, indent=2, ensure_ascii=False)}
        ---
        ULKOISEN FAKTANTARKISTUKSEN TULOKSET (jos saatavilla):
        {google_search_results}
        ---
        """

    async def execute(self, state: WorkflowState, system_instruction: Optional[str] = None, **kwargs) -> WorkflowState:
        # 1. Construct User Prompt
        user_content = self.construct_user_prompt(state)
        
        # 2. Append the Meta-Instruction for JSON formatting
        meta_instruction = """
        
        ### PANEL OUTPUT INSTRUCTION ###
        You are acting as a PANEL of critics. You have received instructions for multiple roles above.
        You must perform ALL these roles concurrently based on the same input data.
        
        REQUIRED OUTPUT FORMAT:
        Return a SINGLE JSON object where the top-level keys correspond to the output of each role.
        Based on the instructions provided, you should include keys such as:
        - "logiikka_auditointi" (for Logical Falsifier)
        - "etiikka_ja_fakta" (for Factual Overseer)
        - "kausaalinen_auditointi" (for Causal Analyst)
        - "performatiivisuus_auditointi" (for Performativity Detector)
        
        Example:
        {
            "logiikka_auditointi": { ... },
            "etiikka_ja_fakta": { ... },
            "kausaalinen_auditointi": { ... },
            "performatiivisuus_auditointi": { ... }
        }
        
        Ensure each sub-object strictly follows the schema defined in its respective instruction.
        """
        
        full_system_instruction = (system_instruction or "") + meta_instruction
        
        # 3. Call LLM
        # We do NOT pass a specific response_schema because the output is a composite dict 
        # of multiple schemas. We rely on the prompt to enforce structure (or we could define a super-model).
        # We pass **kwargs (like temperature, max_tokens) to the provider
        response = await self.llm_provider.generate(
            prompt=user_content,
            system_instruction=full_system_instruction,
            response_schema=None,
            mock_identity="PanelAgent",
            **kwargs
        )
        
        # 4. Parse JSON
        parsed_data = {}
        if isinstance(response, str):
            try:
                # Basic cleanup for markdown code blocks
                clean_txt = response.strip()
                if clean_txt.startswith("```"):
                     clean_txt = clean_txt.split("\n", 1)[1]
                     if clean_txt.endswith("```"):
                         clean_txt = clean_txt.rsplit("\n", 1)[0]
                parsed_data = json.loads(clean_txt)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                # Return state without updates if parsing fails
                return state
        elif isinstance(response, dict):
            parsed_data = response

        # 5. Instantiate Pydantic models and update State
        try:
            if "logiikka_auditointi" in parsed_data:
                state.step_falsifier = LogiikkaAuditointi(**parsed_data["logiikka_auditointi"])
                logger.info("[PanelAgent] Updated step_falsifier")
                
            if "etiikka_ja_fakta" in parsed_data:
                state.step_overseer = EtiikkaJaFakta(**parsed_data["etiikka_ja_fakta"])
                logger.info("[PanelAgent] Updated step_overseer")
                
            if "kausaalinen_auditointi" in parsed_data:
                state.step_causal = KausaalinenAuditointi(**parsed_data["kausaalinen_auditointi"])
                logger.info("[PanelAgent] Updated step_causal")
                
            if "performatiivisuus_auditointi" in parsed_data:
                state.step_detector = PerformatiivisuusAuditointi(**parsed_data["performatiivisuus_auditointi"])
                logger.info("[PanelAgent] Updated step_detector")
                
        except Exception as e:
             logger.error(f"[PanelAgent] Failed to instantiate Pydantic models from output: {e}")
             
        return state
