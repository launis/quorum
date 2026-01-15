"""Agent implementations for the Cognitive Quorum backend."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.exceptions import AgentExecutionError
from backend.models.domain import PanelAudit

if TYPE_CHECKING:
    from backend.models.state import WorkflowState

logger = logging.getLogger(__name__)


class PanelAgent(BaseAgent):
    """Paneeli-agentti (Panel Agent).

    Executes multiple critical roles in a single LLM call to save tokens and time.
    Acts as a composite agent that performs fan-out of results to individual state fields.
    """

    state_field = "step_panel"
    REQUIRES_KEYS = ["step_analyst", "step_profiler"]
    PRODUCES_KEYS = ["step_panel", "step_logician", "step_falsifier", "step_causal", "step_detector", "step_overseer"]

    def __init__(self, model: str | None = None, provider: str | None = None, **kwargs):
        """Initializes PanelAgent with strict configuration (Zero-Fallback)."""
        # ZERO-FALLBACK RULE: Fail fast if configuration is missing
        if not model:
            # We allow None during init if it's injected later via Registry, 
            # but we do NOT provide a hardcoded default string here.
            # The Registry/Factory logic must ensure 'model' is passed.
            pass
        
        super().__init__(model=model, provider=provider)


    def construct_user_prompt(self, state: WorkflowState) -> str:
        """Constructs the user prompt for the Panel Agent by aggregating input data and prior step results.
        
        Args:
            state (WorkflowState): The current workflow state.
            
        Returns:
            str: The constructed user prompt string.
        """
        # Collect all relevant data for all potential critics from the state
        # Utilizing previous steps' outputs if available
        input_data = {
            "inputs": {
                "history_text": state.inputs.history_text,
                "product_text": state.inputs.product_text,
                "reflection_text": state.inputs.reflection_text,
            }
        }

        # Add available intermediate results
        if state.step_analyst:
            input_data["todistuskartta"] = state.step_analyst.model_dump(mode="json")
        if state.step_profiler:
            input_data["profiili"] = state.step_profiler.model_dump(mode="json")

        # Add aux data if relevant (like search results)
        google_search_results = state.aux_data.get("google_search_results", "Ei hakutuloksia.")

        return f"""
        INPUT DATA FOR THE PANEL:
        ---
        {json.dumps(input_data, indent=2, ensure_ascii=False)}
        ---
        ULKOISEN FAKTANTARKISTUKSEN TULOKSET (jos saatavilla):
        {google_search_results}
        ---
        """

    async def execute(
        self,
        state: WorkflowState | None = None,
        system_instruction: str | None = None,
        **kwargs,
    ) -> WorkflowState:
        """Executes the Panel Agent logic.

        1. Constructs the user prompt.
        2. Calls the LLM provider with the PanelAudit schema.
        3. Fans out the results to specific state fields (logician, falsifier, etc.).

        Input State:
            - state.inputs (History, Product, Reflection).
            - state.step_analyst (Evidence Map) [Optional].
            - state.step_profiler (Psychological Profile) [Optional].

        Output State:
            - state.step_panel (PanelAudit): The composite audit.
            - state.step_logician (Populated from PanelAudit).
            - state.step_falsifier (Populated from PanelAudit).
            - state.step_causal (Populated from PanelAudit).
            - state.step_detector (Populated from PanelAudit).
            - state.step_overseer (Populated from PanelAudit).

        Exceptions:
            - AgentExecutionError: If LLM fails or schema validation fails.
        """
        # 1. Construct User Prompt
        if state is None:
            raise ValueError("PanelAgent requires a valid WorkflowState.")

        try:
            user_content = self.construct_user_prompt(state)

            # 2. Call LLM with strict PanelAudit schema
            if not self.llm_provider:
                raise ValueError("PanelAgent requires a configured LLM Provider.")

            # ENFORCEMENT: Model must be configured
            if not self.model:
                 raise ValueError("PanelAgent requires a configured Model string (Zero-Fallback Violation).")

            response = await self.llm_provider.generate(
                prompt=user_content,
                system_instruction=system_instruction,
                response_schema=PanelAudit,
                mock_identity="PanelAgent",
                **kwargs,
            )

            # 3. Process Response (Structured Output)
            panel_data = None
            
            # OPTIMIZATION: Use pre-parsed content if available (Instructor Pattern)
            if response.parsed_content is not None:
                if isinstance(response.parsed_content, PanelAudit):
                    panel_data = response.parsed_content
                elif isinstance(response.parsed_content, dict):
                    panel_data = PanelAudit(**response.parsed_content)
                else:
                    logger.warning(f"[PanelAgent] parsed_content was {type(response.parsed_content)}, expected Dict or PanelAudit. Trying legacy parsing.")
            
            # Fallback (Legacy) - Only used if Provider didn't parse
            if not panel_data:
                raw_content = response.content if hasattr(response, "content") else response
                if isinstance(raw_content, str):
                    try:
                        clean_content = raw_content.replace("```json", "").replace("```", "").strip()
                        raw_dict = json.loads(clean_content)
                        panel_data = PanelAudit(**raw_dict)
                    except json.JSONDecodeError as e:
                         error_code = "PANEL_RESPONSE_MALFORMED"
                         logger.error(f"{error_code}: Could not parse JSON string - {e}")
                         raise AgentExecutionError(detail=error_code, original_error=e) from e

            if panel_data:
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
                 raise AgentExecutionError(detail="PANEL_RESPONSE_EMPTY", original_error=ValueError("No data returned"))

            return state

        except Exception as e:
            # ECHO PROTOCOL: Safety Net
            error_code = "PANEL_EXECUTION_CRITICAL"
            logger.error(f"{error_code}: Unexpected failure - {e}", exc_info=True)
            raise AgentExecutionError(detail=error_code, original_error=e) from e
