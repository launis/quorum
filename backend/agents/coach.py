from typing import Any, Optional, Type, List, Dict
from backend.agents.base import BaseAgent
from backend.models.state import WorkflowState
from pydantic import BaseModel, Field
import logging
import os
import json

logger = logging.getLogger(__name__)

from backend.models.domain import CoachingPlan, ActionItem

class CoachAgent(BaseAgent):
    """
    Coach Agent (Valmentaja).
    Transformative feedback based on Judge's verdict.
    """
    state_field = "step_coach"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.knowledge_base = self._load_knowledge_base()

    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Loads the extended knowledge base from JSON."""
        path = os.path.join("data", "coach_resources.json")
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"[CoachAgent] Loaded knowledge base from {path}")
                    return data
            except Exception as e:
                logger.error(f"[CoachAgent] Failed to load knowledge base: {e}")
        return {}

    def _build_prompt(self, state: WorkflowState) -> str:
        """
        Overrides BaseAgent._build_prompt to inject Knowledge Base context.
        """
        # 1. Get base prompt from DB/config
        base_prompt = super()._build_prompt(state)
        
        # 2. Enrich with Knowledge Base
        if self.knowledge_base and "concepts" in self.knowledge_base:
            context_str = "\n\n### REFERENCE MATERIAL (from 'Holistinen Mestaruus')\n"
            context_str += "Use these definitions to explain *why* specific feedback is given:\n\n"
            
            for concept, definition in self.knowledge_base["concepts"].items():
                def_short = definition[:800] + "..." if len(definition) > 800 else definition
                context_str += f"#### {concept}\n{def_short}\n\n"
            
            return context_str + base_prompt
            
        return base_prompt

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return CoachingPlan

    def enrich_learning_plan(self, state: WorkflowState) -> WorkflowState:
        """
        POST-HOOK: Scans the generated ActionItems. 
        Searches the JSON Knowledge Base bibliography for relevant citations and appends them.
        """
        logger.info("[CoachAgent] Running enrich_learning_plan hook...")
        
        # 1. Get the output from state using the state_field
        coach_plan_data = getattr(state, self.state_field, None)
        if not coach_plan_data:
            return state
            
        # Ensure it's a model instance or dict, Pydantic should handle it?
        # In V2 state, it's usually the Pydantic object if validated.
        
        # Check if we need to access items. 
        # Note: 'coach_plan_data' might be a Dict if deserialized from JSON without model validation in some paths,
        # OR it is the CoachingPlan object. 
        # BaseAgent.execute usually sets the Pydantic model.
        
        # To be safe, if it's an object, get attribute; if dict, get key.
        def get_attr(obj, attr):
            return getattr(obj, attr) if hasattr(obj, attr) else obj.get(attr)

        items = get_attr(coach_plan_data, 'kehityskohteet_konkreettisesti')
        if not items:
            return state

        updated_count = 0
        for item in items:
            # item is ActionItem object or dict
            otsikko = get_attr(item, 'otsikko') or ""
            kuvaus = get_attr(item, 'kuvaus') or ""
            desc = (kuvaus + " " + otsikko).lower()
            
            current_resources = get_attr(item, 'resurssit')
            if current_resources is None:
                current_resources = []
            
            # Search bibliography based on specific keywords found in the item
            if self.knowledge_base and "concepts" in self.knowledge_base:
                for concept in self.knowledge_base["concepts"]:
                    if concept.lower() in desc and concept != "Bibliography":
                        if self.knowledge_base.get("references") and "bibliography" in self.knowledge_base["references"]:
                            for ref in self.knowledge_base["references"]["bibliography"]:
                                # Simple match
                                if concept.lower() in ref.lower() or (concept == "Hybrid Rubric" and "hybridirubriikki" in ref.lower()):
                                    if not any(ref[:20] in r for r in current_resources):
                                        current_resources.append(f"📚 {ref}")
                                        logger.info(f"   [Coach] Enriched item '{otsikko}' with biblio ref.")
                                        updated_count += 1
            
            # Update item
            if hasattr(item, 'resurssit'):
                item.resurssit = current_resources
            else:
                item['resurssit'] = current_resources
            
        return state
