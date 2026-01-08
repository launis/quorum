"""Interaction Analyst Agent implementation."""
from __future__ import annotations
import logging
from typing import TYPE_CHECKING

from pydantic import BaseModel

from backend.agents.base import BaseAgent
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

    async def execute(self, state: WorkflowState, system_instruction: str | None = None, **kwargs) -> WorkflowState:
        """Executes interaction analysis (Driver/Passenger classification).

        Input State:
            - state.inputs.history_text (Primary analysis target).

        Output State:
            - state.step_interaction (InteractionAnalysis): Qualitative analysis.
            - state.step_interaction.input_control_ratio (Updated via post-hook).

        Exceptions:
            - AgentExecutionError: If LLM fails.
        """
        return await super().execute(state, system_instruction, **kwargs)

    def calculate_control_ratio(self, state: WorkflowState) -> WorkflowState:
        """Lifecycle Hook: Post-Execution.

        Calculates 'input_control_ratio' using Python regex on history_text.
        Delegates underlying logic to 'backend.hooks.metrics.calculate_control_ratio'.

        Args:
            state (WorkflowState): Current workflow state.

        Returns:
            WorkflowState: Updated state with calculated metrics.

        """
        logger.info("[InteractionAnalystAgent] Post-Processing: Calculating Input Control Ratio via Hook...")

        if not state.step_interaction:
            return state

        # 1. Get History Text
        history = state.inputs.history_text
        if not history:
            logger.warning("[InteractionAnalystAgent] No history_text found for ratio calculation.")
            state.step_interaction.input_control_ratio = 0.0
            return state

        # 2. Calculate Ratio
        try:
            from backend.hooks.metrics import calculate_control_ratio

            ratio = calculate_control_ratio(history)

            state.step_interaction.input_control_ratio = ratio
            logger.info(f"[InteractionAnalystAgent] Calculated Ratio: {ratio:.2f}")
        except Exception as e:
            logger.error(f"[InteractionAnalystAgent] Ratio calculation failed: {e}")
            state.step_interaction.input_control_ratio = 0.0

        return state
