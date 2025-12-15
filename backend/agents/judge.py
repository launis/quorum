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

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return TuomioJaPisteet

    def calculate_final_scores(self, state: WorkflowState) -> WorkflowState:
        """
        HOOK: calculate_final_scores
        Calculates averages and summary of the scores.
        Applies DETERMINISTIC penalties based on earlier steps.
        """
        logger.info("[JudgeAgent] Running calculate_final_scores...")
        
        if not state.step_judge or not state.step_judge.pisteet:
            logger.warning("   [JudgeAgent] No scores to calculate.")
            return state
            
        try:
            p = state.step_judge.pisteet
            
            # --- DETERMINISTIC RULE ENFORCEMENT ---
            penalties_applied = []
            
            # Rule 1: Security Threat (Guard) -> Auto Fail (1/4)
            if state.step_guard and state.step_guard.security_check and state.step_guard.security_check.uhka_havaittu:
                logger.warning("[JudgeAgent] Security Threat detected by Guard! Capping scores to 1.")
                for comp in [p.analyysi, p.arviointi, p.synteesi]:
                    if comp: 
                        comp.arvosana = 1
                        comp.perustelu += " [AUTOMATIC PENALTY: Security Threat Detected]"
                penalties_applied.append("Security Threat (Score capped at 1)")

            # Rule 2: Logical Failures (Falsifier) -> Max Score 2/4
            # We assume Falsifier has run and populated 'step_falsifier'
            # Check if there are critical logical errors (needs inspection of Falsifier schema/output)
            # For now, let's look for "post_hoc_rationalisointi" if it's a boolean in the model
            elif state.step_falsifier:
                 # Check for critical flags (Example logic)
                 # Adjust based on actua Falsifier model structure
                 if hasattr(state.step_falsifier, 'onko_post_hoc_rationalisointia') and state.step_falsifier.onko_post_hoc_rationalisointia:
                    logger.warning("[JudgeAgent] Post-Hoc Rationalization detected! Capping scores to 2.")
                    for comp in [p.analyysi, p.arviointi, p.synteesi]:
                        if comp and comp.arvosana > 2:
                            comp.arvosana = 2
                            comp.perustelu += " [AUTOMATIC PENALTY: Logical Fallacies Detected]"
                    penalties_applied.append("Logical Fallacies (Score capped at 2)")
            
            # --- End Rules ---

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
            if penalties_applied:
                summary += f" | Penalties: {', '.join(penalties_applied)}"
                
            logger.info(f"   {summary}")
            
            # We can store this in aux_data for reference, or update the model if schema allows.
            # The schema TuomioJaPisteet might not have 'calculated_avg'.
            # We'll store in aux_data to be safe.
            state.aux_data['score_summary'] = summary
            state.aux_data['calculated_average'] = average
            state.aux_data['penalties_applied'] = penalties_applied
            
        except Exception as e:
            logger.error(f"[JudgeAgent] Calculation failed: {e}")
            
        return state
