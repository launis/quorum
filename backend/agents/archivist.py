"""Archivist Agent implementation."""

import logging
from typing import Any

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent
from backend.exceptions import AgentExecutionError, ErrorCodes

# 3. Local Imports
from backend.models.domain import ArchivistInput, ArchivistOutput, ArchivistOutputDTO
from backend.models.state import WorkflowState

logger = logging.getLogger(__name__)


class ArchivistAgent(BaseAgent[ArchivistInput, ArchivistOutput]):
    """Arkistonhoitaja (Archivist) Agent.

    Retrieves past cases to ensure consistency (Stare Decisis).
    """

    state_field = "step_archivist"
    DTO_SCHEMA = ArchivistOutputDTO
    INPUT_SCHEMA = ArchivistInput
    OUTPUT_SCHEMA = ArchivistOutput

    async def execute(
        self,
        input_data: ArchivistInput,
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> ArchivistOutput:
        """Executes the archival retrieval and analysis.

        Args:
            input_data (ArchivistInput): Inputs.
            execution_context (dict[str, Any] | None, optional): Context.
            system_instruction (str | None, optional): Prompt.
            **kwargs: Args.

        Returns:
            ArchivistOutput: Relevant past cases and consistency analysis.

        Raises:
            ValueError: If precedents are missing (Fail Fast).
        """
        # FAIL FAST: Precedents must be injected via Hooks.
        # Check validity of injected precedents.
        precedents = input_data.archivist_precedents

        if precedents is None:
             # If strictly None, dependency injection failed
             error_code = ErrorCodes.SERVICE_DEPENDENCY_MISSING
             error_msg = "[ArchivistAgent] Missing 'archivist_precedents'. Archival Hook not configured or failed."
             logger.error(f"{error_code}: {error_msg}")

             raise AgentExecutionError(
                 detail=error_code,
                 original_error=ValueError(error_msg),
                 agent_name="ArchivistAgent"
             )
        
        if not precedents:
             logger.info("[ArchivistAgent] No precedents found (List is empty). Proceeding without historical context.")

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

    async def prepare_context(
        self,
        input_data: ArchivistInput,
        execution_context: dict[str, Any] | None,
        **kwargs: Any
    ) -> str | None:
        """Lifecycle Hook: Pre-Execution.

        Formats the structured precedents into a text block for the LLM.

        Args:
            input_data (ArchivistInput): Inputs.
            execution_context (dict[str, Any] | None): Config.
            **kwargs: Args.

        Returns:
            str | None: Context string.
        """
        precedents = input_data.archivist_precedents
        
        summary_text = "=== ENNAKKOTAPAUKSET (PRECEDENTS) ===\n"
        if not precedents:
            summary_text += "Ei aiempia tapauksia tiedostossa."
        else:
            for p in precedents:
                # p is dict[str, Any]
                p_id = p.get("id", "Unknown")
                p_date = p.get("date", "Unknown")
                p_scores = p.get("scores", "N/A")
                p_verdict = p.get("verdict", "N/A")
                
                summary_text += (
                    f"- Case {p_id} ({p_date}): {p_scores}. Verdict: {p_verdict}\n"
                )
        summary_text += "====================================="
        
        return summary_text

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
