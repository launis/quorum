"""Profiler Agent implementation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.models.domain import ProfilerAnalysis

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class ProfilerAgent(BaseAgent):
    """Profiloija (Psychologist) Agent.

    Step 2.5: Analyzes the 'human' side of the input: intent, biases, tone.
    """

    state_field = "step_profiler"
    REQUIRES_KEYS = ["history_text", "product_text", "reflection_text"]
    PRODUCES_KEYS = ["step_profiler"]

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the expected output schema.

        Returns:
            Optional[Type[BaseModel]]: ProfilerAnalysis schema.

        """
        return ProfilerAnalysis


    async def execute(
        self,
        input_data: dict,
        execution_context: dict | None = None,
        system_instruction: str | None = None,
        **kwargs,
    ) -> dict:
        """Executes the psychological profiling analysis.

        Args:
            input_data (dict): Inputs.
            execution_context (dict): Context.
            system_instruction (str): Prompt.
            **kwargs: Args.

        Returns:
            dict: ProfilerAnalysis.
        """
        # Inject metrics if available in pre-calculation
        try:
             logger.info(f"[ProfilerAgent] Input Context Keys: {list(input_data.keys())}")
             if "profiler_metrics" in input_data:
                 logger.info(f"[ProfilerAgent] Metrics found: {input_data['profiler_metrics']}")
             
             return await super().execute(input_data, execution_context, system_instruction, **kwargs)
        except Exception as e:
            logger.critical(f"[ProfilerAgent] CRASHED: {e}", exc_info=True)
            raise e

    # _update_state removed. Logic for metrics injection should be in a hook or pre-processing.
    # The 'profiler_metrics' are passed in input_data from the Engine if calculated.

    def post_process(self, response_data: Any) -> Any:
        # If we need to inject metrics into the response structure before returning:
        # Check execution_context or input_data?
        # Typically the LLM response is returned as is.
        # If 'teksti_metriikka' is missing, it might be added here if we had access to input_data context.
        return response_data

    # NOTE: The analyze_text_metrics hook has been removed (Jan 2026).
    # Hooks are now executed via centralized HOOK_MAPPING in runner.py.
    # The 'calculate_text_metrics' hook is called directly from seed_data.json config.

    def get_user_prompt_template(self) -> str:
        """Returns the user prompt template.

        Returns:
            str: The template string.

        """
        # Override to show we use metrics
        return "Analyze the text. Metrics: {{profiler_metrics}}"
