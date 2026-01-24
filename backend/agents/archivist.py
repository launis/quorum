"""Archivist Agent implementation."""

import logging
from typing import Any

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.models.domain import ArchivistOutput
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
        return ArchivistOutput

    async def execute(
        self,
        input_data: dict,
        execution_context: dict | None = None,
        system_instruction: str | None = None,
        **kwargs,
    ) -> dict:
        """Executes the archival retrieval and analysis.

        Args:
            input_data (dict): Inputs.
            execution_context (dict): Context.
            system_instruction (str): Prompt.
            **kwargs: Args.

        Returns:
            dict: Relevant past cases and consistency analysis.
        """
        # NOTE: Precedents are expected to be in input_data (injected via Engine/Hooks before execution)
        return await super().execute(input_data, execution_context, system_instruction, **kwargs)

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
