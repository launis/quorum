"""Analyst Agent implementation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.models.domain import AnalystOutput
from backend.models.state import WorkflowState

if TYPE_CHECKING:
    pass

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
    OUTPUT_SCHEMA = AnalystOutput

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the Pydantic model for the agent's expected output.

        Returns:
            Optional[Type[BaseModel]]: The AnalystOutput schema.

        """
        return AnalystOutput

    async def execute(
        self,
        input_data: dict,
        execution_context: dict | None = None,
        system_instruction: str | None = None,
        **kwargs,
    ) -> dict:
        """Executes the analysis logic.

        Args:
            input_data (dict): Inputs.
            execution_context (dict): Context.
            system_instruction (str): Prompt.
            **kwargs: Args.

        Returns:
            dict: The generated evidence map.
        """
        return await super().execute(input_data, execution_context, system_instruction, **kwargs)

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

    def post_process(self, state: WorkflowState) -> WorkflowState:
        """Lifecycle Hook: Post-Execution.
        
        Enforces sequential IDs for Hypotheses (PYTHON AUTHORITY).
        """
        # Ensure we have the step output
        if not hasattr(state, self.state_field) or not state.step_analyst:
            return state

        result = state.step_analyst

        if result.hypoteesit:
            logger.info(f"[AnalystAgent] Enforcing Hypothesis IDs (Count: {len(result.hypoteesit)})")
            for idx, hyp in enumerate(result.hypoteesit, 1):
                new_id = f"HYP-{idx}"
                if hyp.id != new_id:
                    # logger.debug(f"Renaming Hypothesis: {hyp.id} -> {new_id}")
                    hyp.id = new_id

        return state
