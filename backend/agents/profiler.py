from typing import Any, Optional, Type, Dict
from backend.agents.base import BaseAgent
from backend.models.state import WorkflowState
from pydantic import BaseModel, Field
import logging
import re


from backend.models.domain import ProfilerAnalysis, TextMetrics
logger = logging.getLogger(__name__)

# TextMetrics moved to backend.models.domain


# StructuredBias and ProfilerAnalysis removed (using domain.py)

class ProfilerAgent(BaseAgent):
    """
    Profiloija (Psychologist) Agent.
    Step 2.5: Analyzes the 'human' side of the input: intent, biases, tone.
    """

    state_field = "step_profiler"
    REQUIRES_KEYS = ["history_text", "product_text"]

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return ProfilerAnalysis
        


    def _update_state(self, state: WorkflowState, response_data: Any) -> WorkflowState:
        # Merge Python-calculated metrics if available (from pre-hook)
        if 'profiler_metrics' in state.aux_data and isinstance(response_data, dict):
            # We inject it into the dict so BaseAgent validates it including the metrics
            response_data['teksti_metriikka'] = state.aux_data['profiler_metrics']
            
        return super()._update_state(state, response_data)

    # --- PYTHON HOOKS ---

    def analyze_text_metrics(self, state: WorkflowState) -> WorkflowState:
        """
        PRE-HOOK: Calculates objective text metrics from the input history/product.
        Delegates to backend.hooks.metrics.
        """
        logger.info("[ProfilerAgent] Delegating to Metrics Hook...")
        
        # 1. Get Text to Analyze
        text = (state.inputs.history_text or "") + "\n" + (state.inputs.product_text or "")
        if not text.strip():
            logger.warning("[ProfilerAgent] No text to analyze.")
            return state

        # 2. Calculate Metrics using Hook
        from backend.hooks.metrics import calculate_text_metrics
        raw_metrics = calculate_text_metrics(text)
        
        from backend.models.domain import TextMetrics
        metrics = TextMetrics(**raw_metrics)
        
        logger.info(f"[ProfilerAgent] Metrics calculated: {metrics}")
        
        # 3. Inject into State (aux_data)
        state.aux_data['profiler_metrics'] = metrics.model_dump()
        
        return state
        
    def get_user_prompt_template(self) -> str:
        # Override to show we use metrics
        return "Analyze the text. Metrics: {{PROFILER_METRICS}}"
