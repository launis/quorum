from typing import Any, Optional, Type, List, Dict
from backend.agents.base import BaseAgent
from backend.models.state import WorkflowState
from pydantic import BaseModel, Field
from tinydb import Query
import logging
import json

logger = logging.getLogger(__name__)

from backend.models.domain import BaseJSON

class CaseLawContext(BaseJSON):
    """
    Schema for the Archivist (Clerk) Agent.
    Ensures consistency with previous rulings.
    """
    linjakkuus_analyysi: str = Field(..., description="Analysis of how this case compares to precedents")
    poikkeamat_linjasta: str = Field(..., description="Notable deviations from established consistency")
    suositus_tuomarille: str = Field(..., description="Recommendation to the Judge regarding severity/leniency")
    viitatut_ennakkotapaukset: List[str] = Field(..., description="IDs of cases referenced")

class ArchivistAgent(BaseAgent):
    """
    Arkistonhoitaja (Archivist) Agent.
    Step 8.5: Retrieves past cases to ensure consistency (Stare Decisis).
    """

    state_field = "step_archivist"

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return CaseLawContext

    # --- PYTHON HOOKS ---

    def retrieve_precedent(self, state: WorkflowState, repository: Any = None) -> WorkflowState:
        """
        PRE-HOOK: Retrieves the last N completed executions with a valid Judge score.
        Delegates to backend.hooks.archival.
        """
        logger.info("[ArchivistAgent] Delegating to Archival Hook...")
        from backend.hooks.archival import retrieve_precedent
        return retrieve_precedent(state, repository)
