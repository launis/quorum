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

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return TuomioJaPisteet

    def _update_state(self, state: WorkflowState, response_data: Any) -> WorkflowState:
        try:
            state.step_8_judge = TuomioJaPisteet(**response_data)
        except Exception as e:
            logger.error(f"[JudgeAgent] State update failed: {e}")
            raise e
        return state

    def calculate_final_scores(self, state: WorkflowState) -> WorkflowState:
        """
        HOOK: calculate_final_scores
        Calculates averages and summary of the scores.
        """
        logger.info("[JudgeAgent] Running calculate_final_scores...")
        
        if not state.step_8_judge or not state.step_8_judge.pisteet:
            logger.warning("   [JudgeAgent] No scores to calculate.")
            return state
            
        try:
            p = state.step_8_judge.pisteet
            
            # Helper to safely get score
            def get_val(s): return s.arvosana if s else 0
            
            total = 0
            count = 0
            
            # Check each component dynamically
            for comp in [p.analyysi, p.arviointi, p.synteesi]:
                if comp and comp.arvosana is not None:
                    total += comp.arvosana
                    count += 1
            
            # Calculate average
            average = (total / count) if count > 0 else 0.0
            
            summary = f"Total Score: {total}/{count*4} (Avg: {average:.2f})"
            logger.info(f"   {summary}")
            
            # We can store this in aux_data for reference, or update the model if schema allows.
            # The schema TuomioJaPisteet might not have 'calculated_avg'.
            # We'll store in aux_data to be safe.
            state.aux_data['score_summary'] = summary
            state.aux_data['calculated_average'] = average
            
        except Exception as e:
            logger.error(f"[JudgeAgent] Calculation failed: {e}")
            
        return state
