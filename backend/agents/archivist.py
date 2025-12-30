from typing import Any, Optional, Type, List, Dict, Annotated
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
    linjakkuus_analyysi: Annotated[str, Field(description="Analysis of how this case compares to precedents")]
    poikkeamat_linjasta: Annotated[str, Field(description="Notable deviations from established consistency")]
    suositus_tuomarille: Annotated[str, Field(description="Recommendation to the Judge regarding severity/leniency")]
    viitatut_ennakkotapaukset: Annotated[List[str], Field(description="IDs of cases referenced")]

class ArchivistAgent(BaseAgent):
    """
    Arkistonhoitaja (Archivist) Agent.
    
    Step 8.5: Retrieves past cases to ensure consistency (Stare Decisis).
    """

    state_field = "step_archivist"

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        """
        Returns the expected response schema for the Archivist agent.

        Returns:
            Optional[Type[BaseModel]]: The CaseLawContext schema.
        """
        return CaseLawContext

    # --- PYTHON HOOKS ---

    async def retrieve_precedent(self, state: WorkflowState, repository: Any = None) -> WorkflowState:
        """
        PRE-HOOK: retrieve_precedent.
        
        Retrieves the last N completed executions with a valid Judge score to ensure consistency (Stare Decisis).
        Delegates to backend.hooks.archival.

        Args:
            state (WorkflowState): Current workflow state.
            repository (Any): The repository instance for DB access.

        Returns:
            WorkflowState: Updated state with retrieved precedents.
        """
        logger.info("[ArchivistAgent] Delegating to Archival Hook...")
        from backend.hooks.archival import retrieve_precedent
        return await retrieve_precedent(state, repository)
