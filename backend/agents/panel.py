from typing import Any, Dict, Optional
from backend.agents.base import BaseAgent
from backend.models.state import WorkflowState
from backend.models.domain import (
    PanelAudit
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
        if state.step_profiler:
            input_data["profiili"] = state.step_profiler.model_dump(mode='json')
            
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
        
        # 2. Call LLM with strict PanelAudit schema
        response = await self.llm_provider.generate(
            prompt=user_content,
            system_instruction=system_instruction,
            response_schema=PanelAudit,
            mock_identity="PanelAgent",
            **kwargs
        )
        
        # 3. Process Response
        if isinstance(response, PanelAudit) or (isinstance(response, dict) and "logiikka_auditointi" in response):
            # Verify and parse if it's a raw dict
            panel_data = response if isinstance(response, PanelAudit) else PanelAudit(**response)

            # 4. Fan-Out: Populate individual state fields for compatibility with Judge/Coach
            state.step_logician = panel_data.logiikka_auditointi
            state.step_falsifier = panel_data.falsifiointi_auditointi
            state.step_causal = panel_data.kausaalinen_auditointi
            state.step_detector = panel_data.performatiivisuus_auditointi
            state.step_overseer = panel_data.etiikka_ja_fakta
            
            # 5. Populate the panel step itself (optional, but good for tracking)
            state.step_panel = panel_data
            
            logger.info("[PanelAgent] Successfully fanned out PanelAudit to 5 distinct state steps.")

        else:
            logger.error(f"[PanelAgent] unexpected response type: {type(response)}")

        return state
