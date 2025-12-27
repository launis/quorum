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
        return TodistusKartta

    def verify_structure(self, state: WorkflowState) -> WorkflowState:
        """
        HOOK: verify_structure
        Pre-hook. Validates that inputs have sufficient content for analysis.
        """
        logger.info("[AnalystAgent] Running verify_structure (Pre-Hook)...")
        
        # Minimum char limits
        MIN_CHARS = 100 
        
        warnings = []
        
        for key in ["history_text", "product_text", "reflection_text"]:
            text = getattr(state.inputs, key, "")
            if not text or len(text) < MIN_CHARS:
                warnings.append(f"Input '{key}' is too short ({len(text) if text else 0} chars). Analysis quality may suffer.")
                
        if warnings:
            logger.warning(f"[AnalystAgent] Structural Warnings: {warnings}")
            # Inject into state so Analyst sees it?
            # Or just log it. If purely structural, we might want to fail fast, but for now just warn.
            state.aux_data['structural_warnings'] = warnings
            
        return state
