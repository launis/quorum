from typing import Any, Optional, Type
from backend.agents.base import BaseAgent
from backend.models.state import WorkflowState
from backend.models.domain import TuomioJaPisteet
from pydantic import BaseModel
import logging
import json

logger = logging.getLogger(__name__)

class JudgeAgent(BaseAgent):
    """
    Tuomari-agentti (Judge Agent).
    """

    state_field = "step_judge"
    
    # Contracts: Depends on Guard for penalties, and Panel for logic checks
    REQUIRES_KEYS = ["step_guard", "step_falsifier", "step_logician"] 
    PRODUCES_KEYS = ["step_judge"]
    OUTPUT_SCHEMA = TuomioJaPisteet

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return TuomioJaPisteet

    def post_process(self, state: WorkflowState) -> WorkflowState:
        """
        Lifecycle Hook: Post-Execution.
        Calculates final scores and applying penalties.
        """
        return self.calculate_final_scores(state)

    def calculate_final_scores(self, state: WorkflowState) -> WorkflowState:
        """
        HOOK: calculate_final_scores
        Calculates averages and summary of the scores.
        Delegates to backend.hooks.scoring.
        """
        logger.info("[JudgeAgent] Running calculate_final_scores...")
        from backend.hooks.scoring import apply_scoring_logic
        
        return apply_scoring_logic(state)
