from typing import Optional, Type, List
from backend.agents.base import BaseAgent
from backend.models.state import WorkflowState
from backend.models.domain import InteractionAnalysis
from pydantic import BaseModel
import logging
import re

logger = logging.getLogger(__name__)

class InteractionAnalystAgent(BaseAgent):
    """
    InteractionAnalystAgent (Vuorovaikutusanalysaattori).
    
    Analyses the 'history_text' to evaluate Prompt Engineering competence.
    Hybrid logic:
    - AI: Qualitative analysis (Strategies, Driver Classification).
    - Python: Quantitative analysis (Input Control Ratio).
    """
    
    state_field = "step_interaction"
    REQUIRES_KEYS = ["history_text"]

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return InteractionAnalysis

    async def execute(self, state: WorkflowState, system_instruction: Optional[str] = None, **kwargs) -> WorkflowState:
        # Override but BaseAgent.execute uses generic prompt. 
        return await super().execute(state, system_instruction, **kwargs)

    def calculate_control_ratio(self, state: WorkflowState) -> WorkflowState:
        """
        Lifecycle Hook: Post-Execution.
        Calculates 'input_control_ratio' using Python regex on history_text.
        """
        logger.info("[InteractionAnalystAgent] Post-Processing: Calculating Input Control Ratio...")
        
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
            ratio = self._calculate_control_ratio(history)
            state.step_interaction.input_control_ratio = ratio
            logger.info(f"[InteractionAnalystAgent] Calculated Ratio: {ratio:.2f}")
        except Exception as e:
            logger.error(f"[InteractionAnalystAgent] Ratio calculation failed: {e}")
            state.step_interaction.input_control_ratio = 0.0

        return state

    def _calculate_control_ratio(self, text: str) -> float:
        """
        Calculates ratio of Human Tokens vs Total Tokens (approximation using chars).
        """
        if not text:
            return 0.0

        user_chars = 0
        ai_chars = 0
        
        # Normalize to lines
        lines = text.split('\n')
        current_speaker = None # 'user' or 'ai'
        
        user_headers = ['user:', 'human:', 'k:', 'käyttäjä:', 'me:', 'minä:']
        ai_headers = ['ai:', 'assistant:', 't:', 'tekoäly:', 'gpt:', 'bot:']
        
        for line in lines:
            lower_line = line.strip().lower()
            
            # Check for header switch
            started_new_block = False
            for h in user_headers:
                if lower_line.startswith(h):
                    current_speaker = 'user'
                    line_content = line[len(h):]
                    user_chars += len(line_content.strip())
                    started_new_block = True
                    break
            
            if not started_new_block:
                for h in ai_headers:
                    if lower_line.startswith(h):
                        current_speaker = 'ai'
                        line_content = line[len(h):]
                        ai_chars += len(line_content.strip())
                        started_new_block = True
                        break
            
            # If continuation of previous block
            if not started_new_block and current_speaker:
                clean_len = len(line.strip())
                if current_speaker == 'user':
                    user_chars += clean_len
                else:
                    ai_chars += clean_len
        
        total_chars = user_chars + ai_chars
        if total_chars == 0:
            return 0.0
            
        return round(user_chars / total_chars, 4)
