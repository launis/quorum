"""Archivist Agent implementation."""

import logging
from typing import Any

from pydantic import BaseModel

from backend.agents.base import BaseAgent
from backend.models.domain import CaseLawContext
from backend.models.state import WorkflowState

logger = logging.getLogger(__name__)


class ArchivistAgent(BaseAgent):
    """Arkistonhoitaja (Archivist) Agent.

    Retrieves past cases to ensure consistency (Stare Decisis).
    """

    state_field = "step_archivist"

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the expected response schema for the Archivist agent.

        Returns:
            Optional[Type[BaseModel]]: The CaseLawContext schema.

        """
        return CaseLawContext

    async def execute(
        self,
        state: WorkflowState | None = None,
        system_instruction: str | None = None,
        **kwargs,
    ) -> WorkflowState:
        """Executes the archival retrieval and analysis.

        Input State:
            - state.inputs (History, Product) via hooks.
            - Precedents retrieved via `retrieve_precedent` hook.

        Output State:
            - state.step_archivist (CaseLawContext): Relevant past cases and consistency analysis.

        Exceptions:
            - AgentExecutionError: If LLM fails or schema validation fails.
        """
        return await super().execute(state, system_instruction, **kwargs)

    # --- PYTHON HOOKS ---

    async def retrieve_precedent(self, state: WorkflowState, repository: Any = None) -> WorkflowState:
        """PRE-HOOK: retrieve_precedent.

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
