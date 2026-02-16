"""Agent implementations for the Cognitive Quorum backend."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.exceptions import AgentExecutionError, ErrorCodes
from backend.models.domain import (
    AnalystOutput,
    ContextData,
    PanelOutput,
    PanelOutputDTO,
    ProfilerAnalysis,
)

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
    DTO_SCHEMA = PanelOutputDTO
    OUTPUT_SCHEMA = PanelOutput

    def __init__(self, model: str | None = None, provider: str | None = None, **kwargs: Any):
        """Initializes PanelAgent with strict configuration (Zero-Fallback)."""
        # ZERO-FALLBACK RULE: Fail fast if configuration is missing
        if not model:
            # We allow None during init if it's injected later via Registry,
            # but we do NOT provide a hardcoded default string here.
            # The Registry/Factory logic must ensure 'model' is passed.
            pass

        super().__init__(model=model, provider=provider)

    def _hydrate_inputs(self, input_data: dict[str, Any]) -> tuple[AnalystOutput, ProfilerAnalysis, ContextData | None]:
        """Hydrates raw dictionary inputs into strict Pydantic models.

        Args:
            input_data (dict[str, Any]): Raw input dictionary.

        Returns:
            tuple[AnalystOutput, ProfilerAnalysis, ContextData | None]: Hydrated models.
        
        Raises:
            AgentExecutionError: If mandatory inputs are missing or invalid.
        """
        # 1. Analyst Output (Mandatory)
        analyst_raw = input_data.get("step_analyst")
        if not analyst_raw:
             raise AgentExecutionError(
                 detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                 original_error=ValueError("PanelAgent: Missing dependency 'step_analyst'."),
                 agent_name="PanelAgent"
             )

        try:
            if isinstance(analyst_raw, dict):
                analyst_data = AnalystOutput(**analyst_raw)
            elif isinstance(analyst_raw, AnalystOutput):
                analyst_data = analyst_raw
            else:
                 raise ValueError(f"Invalid type for step_analyst: {type(analyst_raw)}")
        except Exception as e:
            raise AgentExecutionError(
                detail=ErrorCodes.INVALID_JSON_PAYLOAD,
                original_error=e,
                agent_name="PanelAgent"
            ) from e

        # 2. Profiler Analysis (Mandatory)
        profiler_raw = input_data.get("step_profiler")
        if not profiler_raw:
             raise AgentExecutionError(
                 detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                 original_error=ValueError("PanelAgent: Missing dependency 'step_profiler'."),
                 agent_name="PanelAgent"
             )

        try:
            if isinstance(profiler_raw, dict):
                profiler_data = ProfilerAnalysis(**profiler_raw)
            elif isinstance(profiler_raw, ProfilerAnalysis):
                profiler_data = profiler_raw
            else:
                 raise ValueError(f"Invalid type for step_profiler: {type(profiler_raw)}")
        except Exception as e:
            raise AgentExecutionError(
                detail=ErrorCodes.INVALID_JSON_PAYLOAD,
                original_error=e,
                agent_name="PanelAgent"
            ) from e

        # 3. Context Data (Optional)
        context_data = None
        context_raw = input_data.get("step_context")
        if context_raw:
            try:
                if isinstance(context_raw, dict):
                    context_data = ContextData(**context_raw)
                elif isinstance(context_raw, ContextData):
                    context_data = context_raw
                # If it's a string (legacy/error), we might skip or fail.
            except Exception as e:
                logger.warning(f"PanelAgent: Context hydration failed ignored: {e}")

        return analyst_data, profiler_data, context_data

    def construct_user_prompt(self, input_data: dict[str, Any], auxiliary_data: dict[str, Any] | None = None) -> str:
        """Constructs the user prompt for the Panel Agent by aggregating input data and prior step results.

        Args:
            input_data (dict[str, Any]): Flattended input data with prior steps.
            auxiliary_data (dict[str, Any] | None, optional): Aux data (searches etc).

        Returns:
            str: The constructed user prompt string.
        """
        # HYDRATION STEP: Convert inputs to Pydantic models
        analyst_data, profiler_data, context_data = self._hydrate_inputs(input_data)

        # Collect all relevant data for all potential critics from inputs
        # Maps keys if they exist in input_data

        # Strict Validation Helper (Fail-Safe)
        def strict_get(key: str) -> Any:
             val = input_data.get(key)
             if not val:
                 raise AgentExecutionError(
                     detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                     original_error=ValueError(f"PanelAgent: Mandatory input '{key}' missing."),
                     agent_name="PanelAgent"
                 )
             return val

        prompt_input_data = {
            "inputs": {
                "history_text": strict_get("history_text"),
                "product_text": strict_get("product_text"),
                "reflection_text": input_data.get("reflection_text"), # Optional, no default text
            }
        }

        # 3. Context Data (Knowledge Base & Precedents)
        if context_data:
             # Use model_dump to serialize back to dict for generic prompting
             prompt_input_data["step_context"] = context_data.model_dump()

        prompt_input_data["step_analyst"] = analyst_data.model_dump()
        prompt_input_data["step_profiler"] = profiler_data.model_dump()

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

        # Context Section (Knowledge Base)
        context_section = ""
        if context_data:
             # Use typed access! Only `precedents` (which is a string summary) is guaranteed by ContextData model.
             # But ContextData also has knowledge_items.
             # We use the text summary field `precedents` which usually contains everything in the current RetrievalAgent impl.
             context_section = f"\nJÄRJESTELMÄN KONTEKSTI (TIETOPANKKI & ENNAKKOTAPAUKSET):\n{context_data.precedents}\n---"

        from backend.utils.json_utils import flexible_json_dump

        return f"""
        INPUT DATA FOR THE PANEL:
        ---
        {flexible_json_dump(prompt_input_data)}
        ---
        {context_section}
        {search_section}
        """

    async def execute(
        self,
        input_data: dict[str, Any],
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> PanelOutput:
        """Executes the Panel Agent logic.

        Args:
            input_data (dict[str, Any]): Inputs.
            execution_context (dict[str, Any] | None, optional): Config.
            system_instruction (str | None, optional): Prompt.
            **kwargs: Args.

        Returns:
             PanelOutput: The composite PanelOutput result.
        """
        # 1. Construct User Prompt
        try:
            user_content = self.construct_user_prompt(input_data, auxiliary_data=input_data) # Assuming input_data contains merged aux

            # 2. Call LLM with strict PanelOutputDTO schema (Content Only)
            if not self.llm_provider:
                raise AgentExecutionError(
                    detail=ErrorCodes.AGENT_NOT_CONFIGURED,
                    original_error=ValueError("PanelAgent requires a configured LLM Provider."),
                    agent_name="PanelAgent"
                )

            # ENFORCEMENT: Model must be configured
            if not self.model:
                raise AgentExecutionError(
                    detail=ErrorCodes.AGENT_NOT_CONFIGURED,
                    original_error=ValueError("PanelAgent requires a configured Model string (Zero-Fallback Violation)."),
                    agent_name="PanelAgent"
                )

            response = await self.llm_provider.generate(
                prompt=user_content,
                system_instruction=system_instruction,
                response_schema=self.DTO_SCHEMA, # Request DTO
                mock_identity="PanelAgent",
                **kwargs,
            )

            # 3. Process Response (Structured Output)
            panel_dto = None

            # OPTIMIZATION: Use pre-parsed content if available (Instructor Pattern)
            if response.parsed_content is not None:
                if isinstance(response.parsed_content, PanelOutputDTO):
                    panel_dto = response.parsed_content
                elif isinstance(response.parsed_content, PanelOutput): # Should not happen if schema requested is DTO
                    # But if provider does weird things or fallback
                    panel_dto = response.parsed_content
                elif isinstance(response.parsed_content, dict):
                    panel_dto = PanelOutputDTO(**response.parsed_content)
                else:
                    logger.warning(
                        f"[PanelAgent] parsed_content was {type(response.parsed_content)}, "
                        "expected Dict or PanelOutputDTO. Trying legacy parsing."
                    )

            # Fallback (Legacy) - Only used if Provider didn't parse
            if not panel_dto:
                raw_content = response.content if hasattr(response, "content") else response
                if isinstance(raw_content, str):
                    try:
                        clean_content = raw_content.replace("```json", "").replace("```", "").strip()
                        raw_dict = json.loads(clean_content)
                        panel_dto = PanelOutputDTO(**raw_dict)
                    except json.JSONDecodeError as e:
                        error_code = ErrorCodes.AGENT_EXECUTION_CRITICAL
                        logger.error(f"{error_code}: Could not parse JSON string - {e}")
                        raise AgentExecutionError(detail=error_code, original_error=e) from e

            if panel_dto:
                # 4. Promotion to Domain Model (Inject Metadata)
                panel_domain = self._apply_python_authority(panel_dto)
                
                logger.info("[PanelAgent] Successfully generated PanelOutput (Domain Model).")
                return panel_domain

            else:
                raise AgentExecutionError(detail=ErrorCodes.AGENT_EXECUTION_CRITICAL, original_error=ValueError("No data returned"))

        except Exception as e:
            # ECHO PROTOCOL: Safety Net
            error_code = ErrorCodes.AGENT_EXECUTION_CRITICAL
            logger.error(f"{error_code}: Unexpected failure - {e}", exc_info=True)
            raise AgentExecutionError(detail=error_code, original_error=e) from e
