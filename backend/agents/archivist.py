"""Archivist Agent implementation."""

import logging
from typing import Any

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent
from backend.exceptions import AgentExecutionError, ErrorCodes

# 3. Local Imports
# 3. Local Imports
from backend.models.domain import ArchivistOutput, ArchivistOutputDTO
from backend.models.state import WorkflowState

logger = logging.getLogger(__name__)


class ArchivistAgent(BaseAgent):
    """Arkistonhoitaja (Archivist) Agent.

    Retrieves past cases to ensure consistency (Stare Decisis).
    """

    state_field = "step_archivist"
    DTO_SCHEMA = ArchivistOutputDTO
    OUTPUT_SCHEMA = ArchivistOutput

    async def execute(
        self,
        input_data: dict[str, Any],
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> ArchivistOutput:
        """Executes the archival retrieval and analysis.

        Args:
            input_data (dict[str, Any]): Inputs.
            execution_context (dict[str, Any] | None, optional): Context.
            system_instruction (str | None, optional): Prompt.
            **kwargs: Args.

        Returns:
            ArchivistOutput: Relevant past cases and consistency analysis.

        Raises:
            ValueError: If precedents are missing (Fail Fast).
        """
        # FAIL FAST: Precedents must be injected via Hooks.
        # Check input_data for 'archivist_precedents' OR 'aux_data.archivist_precedents' if merged.
        # usually aux_data is separate.
        # But BaseAgent.execute takes input_data.

        # NOTE: If we enforce this, we MUST ensure the hook is running.
        # Since we found it's likely NOT running, this will break execution until config is fixed.
        # BUT this is "Fail Fast". Better to crash than hallucinate.

        # IMPORTANT: If the input isn't mapped, the Agent CANNOT see it unless it's in 'execution_context'.
        # BaseAgent.execute signature has execution_context.
        # Let's check execution_context['aux_data'] if available.

        precedents = None
        if input_data.get("archivist_precedents"):
            precedents = input_data["archivist_precedents"]
        elif execution_context and execution_context.get("aux_data", {}).get("archivist_precedents"):
            precedents = execution_context["aux_data"]["archivist_precedents"]

        if not precedents:
             # If completely missing, we have a problem.
             # Warn effectively, or Fail Fast if it's critical.
             # For now, let's Fail Fast to signal the misconfiguration found in audit.
             error_code = ErrorCodes.SERVICE_DEPENDENCY_MISSING
             error_msg = "[ArchivistAgent] Missing 'archivist_precedents'. Archival Hook not configured or failed."
             logger.error(f"{error_code}: {error_msg}")

             # Raising ValueError might block the user from using the app if config is bad.
             # Given this is "Auditing", failing fast is the goal.
             # Given this is "Auditing", failing fast is the goal.
             raise AgentExecutionError(
                 detail=error_code,
                 original_error=ValueError(error_msg),
                 agent_name="ArchivistAgent"
             )

        result_obj = await super().execute(input_data, execution_context, system_instruction, **kwargs)

        if isinstance(result_obj, ArchivistOutput):
            return result_obj
        elif isinstance(result_obj, dict):
            return ArchivistOutput(**result_obj)
        else:
             raise AgentExecutionError(
                 detail=ErrorCodes.INVALID_JSON_PAYLOAD,
                 original_error=TypeError(f"ArchivistAgent returned {type(result_obj)} instead of ArchivistOutput"),
                 agent_name="ArchivistAgent"
             )

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
