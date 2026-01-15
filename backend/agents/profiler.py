"""Profiler Agent implementation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.models.domain import ProfilerAnalysis, TextMetrics

if TYPE_CHECKING:
    from backend.models.state import WorkflowState

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
        state: WorkflowState | None = None,
        system_instruction: str | None = None,
        **kwargs,
    ) -> WorkflowState:
        """Executes the psychological profiling analysis.

        Input State:
            - state.inputs.history_text
            - state.inputs.product_text
            - state.aux_data.profiler_metrics (Calculated via pre-hook)

        Output State:
            - state.step_profiler (ProfilerAnalysis): Psychological profile and intent analysis.
            - state.aux_data.profiler_metrics: (Persisted)

        Exceptions:
            - AgentExecutionError: If LLM fails or schema validation fails.
        """
        return await super().execute(state, system_instruction, **kwargs)

    async def _update_state(
        self, state: WorkflowState, response_data: Any, output_key: str | None = None, **kwargs
    ) -> WorkflowState:
        """Updates the state with the response data.

        Injects metrics into the response if available in aux_data.

        Args:
            state (WorkflowState): Current workflow state.
            response_data (Any): Data returned by the LLM.
            output_key (Optional[str]): Override for output directory.
            **kwargs: Extra arguments propagated from execution context.

        Returns:
            WorkflowState: Updated state.

        """
        # Merge Python-calculated metrics if available (from pre-hook)
        if "profiler_metrics" in state.aux_data and isinstance(response_data, dict):
            # We inject it into the dict so BaseAgent validates it including the metrics
            response_data["teksti_metriikka"] = state.aux_data["profiler_metrics"]

        return await super()._update_state(state, response_data, output_key=output_key, **kwargs)

    # NOTE: The analyze_text_metrics hook has been removed (Jan 2026).
    # Hooks are now executed via centralized HOOK_MAPPING in runner.py.
    # The 'calculate_text_metrics' hook is called directly from seed_data.json config.

    def get_user_prompt_template(self) -> str:
        """Returns the user prompt template.

        Returns:
            str: The template string.

        """
        # Override to show we use metrics
        return "Analyze the text. Metrics: {{PROFILER_METRICS}}"
