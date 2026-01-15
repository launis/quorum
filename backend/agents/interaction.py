"""Interaction Analyst Agent implementation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.models.domain import InteractionAnalysis

if TYPE_CHECKING:
    from backend.models.state import WorkflowState

logger = logging.getLogger(__name__)


class InteractionAnalystAgent(BaseAgent):
    """InteractionAnalystAgent (Vuorovaikutusanalysaattori).

    Analyses the 'history_text' to evaluate Prompt Engineering competence.
    Hybrid logic:
    - AI: Qualitative analysis (Strategies, Driver Classification).
    - Python: Quantitative analysis (Input Control Ratio).
    """

    state_field = "step_interaction"
    REQUIRES_KEYS = ["history_text"]

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the expected output schema.

        Returns:
            Optional[Type[BaseModel]]: InteractionAnalysis schema.

        """
        return InteractionAnalysis

    async def execute(
        self,
        state: WorkflowState | None = None,
        system_instruction: str | None = None,
        **kwargs,
    ) -> WorkflowState:
        """Executes interaction analysis (Driver/Passenger classification).

        Input State:
            - state.inputs.history_text (Primary analysis target).

        Output State:
            - state.step_interaction (InteractionAnalysis): Qualitative analysis, including 'imperative_command_count'.
            - input_control_ratio is auto-calculated by the Schema.

        Exceptions:
            - AgentExecutionError: If LLM fails.
        """
        # Note: Control ratio is now calculated via centralized HOOK_MAPPING (pre_hooks in seed_data.json)
        return await super().execute(state, system_instruction, **kwargs)
