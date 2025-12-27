from typing import Any, Optional, Type, List, Dict
import re
from backend.agents.base import BaseAgent
from backend.models.state import WorkflowState

import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

from backend.models.domain import CoachingPlan
from backend.services.reference_manager import ReferenceManager

class CoachAgent(BaseAgent):
    state_field = "step_coach"
    REQUIRES_KEYS = ["step_judge"]

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return CoachingPlan



    # ...

    # ...

    async def prepare_context(self, state: WorkflowState, **kwargs) -> str:
        """
        PRE-HOOK: Loads Domain Knowledge from the Repository (Database) into the Agent instance.
        This ensures the CoachAgent uses the same Unified DB as the Ingestion Service.
        """
        repository = kwargs.get('repository')
        if repository:
            # Load items from DB
            items = repository.get_knowledge_base_items()
            
            # Transform to expected structure
            concepts = {}
            references = []
            
            for item in items:
                i_type = item.get('type')
                if i_type == 'concept':
                    term = item.get('term')
                    defn = item.get('definition')
                    if term and defn:
                        concepts[term] = defn
                elif i_type == 'reference':
                    # Support both old string format and new dict format
                    # enrich_learning_plan expects list of strings OR list of dicts.
                    # Let's populate list of dicts for better data.
                    ref_obj = {
                        "citation": item.get('definition'), # Full citation stored in definition
                        "short_citation": item.get('term'), # Short citation stored in term (e.g. "Smith 2020...")
                        "doi": item.get('doi_link')
                    }
                    references.append(ref_obj)
            
            # Populate self.knowledge_base
            # Populate self.knowledge_base
            self.knowledge_base = {
                "concepts": concepts,
                "references": references # List of dicts
            }
            logger.info(f"[CoachAgent] Loaded {len(concepts)} concepts and {len(references)} references from Unified Database.")
            
            # Formulate the Context String for the Prompt
            context_output = "\nEXTERNAL SOURCES (KNOWLEDGE BASE):\n"
            for ref in references:
                citation = ref.get('citation', '')
                if citation:
                     context_output += f"- {citation}\n"
            
            return context_output
            
        else:
            logger.warning("[CoachAgent] No Repository provided in kwargs. Knowledge Base not loaded from DB.")
            self.knowledge_base = {}
            return ""

    # Legacy code removed

    def post_process(self, state: WorkflowState) -> WorkflowState:
        """
        Lifecycle Hook: Post-Execution.
        Triggers bibliography validation and enrichment.
        """
        return self.enrich_learning_plan(state)

    def enrich_learning_plan(self, state: WorkflowState) -> WorkflowState:
        """
        POST-HOOK: Scans the ENTIRE Workflow State.
        Populates bibliography using backend.hooks.references.generate_bibliography.
        """
        logger.info("[CoachAgent] Running enrich_learning_plan hook...")
        
        if not hasattr(self, 'knowledge_base') or not self.knowledge_base:
            return state

        coach_plan_data = getattr(state, self.state_field, None)
        if not coach_plan_data:
            return state

        # Prepare Scan Data (Global)
        try:
            full_state_dict = state.to_flat_dict()
            text_dump = str(full_state_dict)
        except Exception:
            text_dump = str(state.dict())

        # Delegate to Hook
        from backend.hooks.references import generate_bibliography
        formatted_list = generate_bibliography(text_dump, self.knowledge_base)

        if hasattr(coach_plan_data, 'lahdeluettelo'):
             coach_plan_data.lahdeluettelo = formatted_list
        
        logger.info(f"[CoachAgent] Populated bibliography with {len(formatted_list)} references found in global state.")

        return state
