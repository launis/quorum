from typing import Any, Optional, Type, List, Dict
from backend.agents.base import BaseAgent
from backend.models.state import WorkflowState
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

class ActionItem(BaseModel):
    otsikko: str
    kuvaus: str
    resurssit: List[str] = Field(default_factory=list, description="URLs or Book refs")

class CoachingPlan(BaseModel):
    """
    Schema for the Coach (Rehabilitation) Agent.
    Converts judgment into a learning path.
    """
    kannustava_palaute: str = Field(..., description="Positive reinforcement")
    kehityskohteet_konkreettisesti: List[ActionItem] = Field(..., description="Concrete steps to improve")
    oppimispolku_viikko: str = Field(..., description="A 1-week plan to fix the issues")

# STATIC RESOURCE LIBRARY (In a real app, this might be a JSON file or DB table)
RESOURCE_LIBRARY = {
    "Toulmin": "https://owl.purdue.edu/owl/general_writing/academic_writing/historical_perspectives_on_argumentation/toulmin_argument.html",
    "Bloom": "https://cft.vanderbilt.edu/guides-sub-pages/blooms-taxonomy/",
    "Bias": "https://yourbias.is/",
    "Fallacies": "https://yourlogicalfallacyis.com/",
    "Critical Thinking": "https://plato.stanford.edu/entries/critical-thinking/",
    "Argumentation": "https://en.wikipedia.org/wiki/Argumentation_theory"
}

class CoachAgent(BaseAgent):
    """
    Valmentaja (Coach) Agent.
    Step 10.5: Turns the verdict into a pedagogical plan.
    """

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return CoachingPlan

    def _update_state(self, state: WorkflowState, response_data: Any) -> WorkflowState:
        plan = CoachingPlan(**response_data)
        state.aux_data['step_coach'] = plan.model_dump()
        return state

    # --- PYTHON HOOKS ---

    def enrich_learning_plan(self, state: WorkflowState) -> WorkflowState:
        """
        POST-HOOK: Scans the generated ActionItems. If keywords match the Resource Library, 
        appends the official links to the 'resurssit' list.
        """
        logger.info("[CoachAgent] Running enrich_learning_plan hook...")
        
        # 1. Get the output from state using the temp storage we just wrote to
        if 'step_coach' not in state.aux_data:
            return state
            
        coach_data = state.aux_data['step_coach']
        items = coach_data.get('kehityskohteet_konkreettisesti', [])
        
        updated_items = []
        for item in items:
            # Basic keyword matching
            desc = item.get('kuvaus', '').lower() + " " + item.get('otsikko', '').lower()
            current_resources = item.get('resurssit', [])
            
            for key, url in RESOURCE_LIBRARY.items():
                if key.lower() in desc:
                    if url not in current_resources:
                        current_resources.append(f"[{key}]({url})")
                        logger.info(f"   [Coach] Enriched item '{item.get('otsikko')}' with resource {key}")
            
            item['resurssit'] = current_resources
            updated_items.append(item)
            
        # 2. Write back to state
        coach_data['kehityskohteet_konkreettisesti'] = updated_items
        state.aux_data['step_coach'] = coach_data
        
        return state
