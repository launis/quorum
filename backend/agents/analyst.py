"""Analyst Agent implementation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pydantic import BaseModel

from backend.agents.base import BaseAgent
from backend.models.domain import TodistusKartta

if TYPE_CHECKING:
    from backend.models.state import WorkflowState

logger = logging.getLogger(__name__)


class AnalystAgent(BaseAgent):
    """Analyytikko-agentti (Analyst Agent).

    Responsible for:
    1. Evidence Anchoring (Todistepohjainen Ankkurointi)
    2. Creating an 'Evidence Map' (Todistuskartta)
    """

    state_field = "step_analyst"

    # Contracts
    REQUIRES_KEYS = ["history_text", "product_text", "reflection_text"]
    PRODUCES_KEYS = ["step_analyst"]
    OUTPUT_SCHEMA = TodistusKartta

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the Pydantic model for the agent's expected output.

        Returns:
            Optional[Type[BaseModel]]: The TodistusKartta schema.

        """
        return TodistusKartta

    async def execute(self, state: WorkflowState | None = None, system_instruction: str | None = None, **kwargs) -> WorkflowState:
        """Executes the analysis logic.

        Input State:
            - state.inputs.history_text
            - state.inputs.product_text
            - state.inputs.reflection_text

        Output State:
            - state.step_analyst (TodistusKartta): The generated evidence map.

        Exceptions:
            - AgentExecutionError: If LLM fails or schema validation fails.
        """
        return await super().execute(state, system_instruction, **kwargs)

    def verify_structure(self, state: WorkflowState) -> WorkflowState:
        """HOOK: verify_structure.

        Pre-hook that validates whether the inputs have sufficient content for analysis.
        Delegates the actual check to the 'backend.hooks.validation' module.

        Args:
            state (WorkflowState): The current workflow state.

        Returns:
            WorkflowState: The validated workflow state.

        """
        logger.info("[AnalystAgent] Delegating to Validation Hook...")
        from backend.hooks.validation import verify_structure

        return verify_structure(state)
