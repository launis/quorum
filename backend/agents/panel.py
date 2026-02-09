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
    pass

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

    def construct_user_prompt(self, input_data: dict, auxiliary_data: dict | None = None) -> str:
        """Constructs the user prompt for the Panel Agent by aggregating input data and prior step results.

        Args:
            input_data (dict): Flattended input data with prior steps.
            auxiliary_data (dict): Aux data (searches etc).

        Returns:
            str: The constructed user prompt string.
        """
        # Collect all relevant data for all potential critics from inputs
        # Maps keys if they exist in input_data

        # Strict Validation Helper (Fail-Safe)
        def strict_get(key):
             val = input_data.get(key)
             if not val:
                 raise ValueError(f"PanelAgent: Mandatory input '{key}' missing.")
             return val

        prompt_input_data = {
            "inputs": {
                "history_text": strict_get("history_text"),
                "product_text": strict_get("product_text"),
                "reflection_text": input_data.get("reflection_text"), # Optional, no default text
            }
        }

        # Add available intermediate results
        if "step_analyst" in input_data:
            # Assume it's already dict or model dumped by Engine
            prompt_input_data["todistuskartta"] = input_data["step_analyst"]
        if "step_profiler" in input_data:
            prompt_input_data["profiili"] = input_data["step_profiler"]

        # Add aux data if relevant (like search results)
        # REMOVED default value "Ei hakutuloksia" per strict requirements.
        google_search_results = None
        if auxiliary_data and "google_search_results" in auxiliary_data:
             google_search_results = auxiliary_data["google_search_results"]
        # Also check input_data just in case
        elif "google_search_results" in input_data:
             google_search_results = input_data["google_search_results"]

        search_section = ""
        if google_search_results:
             search_section = f"\nULKOISEN FAKTANTARKISTUKSEN TULOKSET:\n{google_search_results}\n---"

        return f"""
        INPUT DATA FOR THE PANEL:
        ---
        {json.dumps(prompt_input_data, indent=2, ensure_ascii=False)}
        ---
        {search_section}
        """

    async def execute(
        self,
        input_data: dict,
        execution_context: dict | None = None,
        system_instruction: str | None = None,
        **kwargs,
    ) -> dict:
        """Executes the Panel Agent logic.

        Args:
            input_data (dict): Inputs.
            execution_context (dict): Config.
            system_instruction (str): Prompt.
            **kwargs: Args.

        Returns:
             dict: The composite PanelAudit result.
        """
        # 1. Construct User Prompt
        try:
            user_content = self.construct_user_prompt(input_data, auxiliary_data=input_data) # Assuming input_data contains merged aux

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
                    logger.warning(
                        f"[PanelAgent] parsed_content was {type(response.parsed_content)}, "
                        "expected Dict or PanelAudit. Trying legacy parsing."
                    )

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
                # 4. Result Construction
                # We return the PanelAudit object (or dict).
                # NOTE: The "Fan-Out" to logging/falsifier/etc fields is no longer done by modifying 'state' here.
                # It must be done by the Engine using mapping_expressions or result_mapping logic if needed.
                # OR we return a dict with those keys if Engine supports flattening.

                # For compatibility with new Engine, we return the PanelAudit.
                # If we need to fan out, we might return a dict like:
                # {
                #   "step_panel": panel_data,
                #   "step_logician": panel_data.logiikka_auditointi, ...
                # }
                # But BaseAgent usually returns one result.
                # Let's assume Engine takes the result for this step ID.

                logger.info("[PanelAgent] Successfully generated PanelAudit.")

                # To support fan-out in the new architecture, we might explicitly return the sub-models
                # But typically the step result is just "step_panel".
                # Downstream steps will look up "step_panel.logiikka_auditointi".

                if isinstance(panel_data, PanelAudit):
                   return panel_data.model_dump()
                return panel_data

            else:
                raise AgentExecutionError(detail="PANEL_RESPONSE_EMPTY", original_error=ValueError("No data returned"))

        except Exception as e:
            # ECHO PROTOCOL: Safety Net
            error_code = "PANEL_EXECUTION_CRITICAL"
            logger.error(f"{error_code}: Unexpected failure - {e}", exc_info=True)
            raise AgentExecutionError(detail=error_code, original_error=e) from e

        except Exception as e:
            # ECHO PROTOCOL: Safety Net
            error_code = "PANEL_EXECUTION_CRITICAL"
            logger.error(f"{error_code}: Unexpected failure - {e}", exc_info=True)
            raise AgentExecutionError(detail=error_code, original_error=e) from e
