from typing import Any, Optional, Type
from backend.agents.base import BaseAgent
from backend.models.state import WorkflowState
from backend.models.domain import TodistusKartta
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class AnalystAgent(BaseAgent):
    """
    Analyytikko-agentti (Analyst Agent).

    Responsible for:
    1. Evidence Anchoring (Todistepohjainen Ankkurointi)
    2. Creating an 'Evidence Map' (Todistuskartta)
    """

    state_field = "step_analyst"
    
    # Contracts
    REQUIRES_KEYS = ["history_text", "product_text"] 
    PRODUCES_KEYS = ["step_analyst"]
    OUTPUT_SCHEMA = TodistusKartta

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        """
        Returns the Pydantic model for the agent's expected output.

        Returns:
            Optional[Type[BaseModel]]: The TodistusKartta schema.
        """
        return TodistusKartta

    def verify_structure(self, state: WorkflowState) -> WorkflowState:
        """
        HOOK: verify_structure.
        
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
