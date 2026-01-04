import logging
from typing import Optional, Type

from pydantic import BaseModel

from backend.agents.base import BaseAgent
from backend.models.domain import XAIReport
from backend.models.state import WorkflowState

logger = logging.getLogger(__name__)


class XAIReporterAgent(BaseAgent):
    """
    XAI-Raportoija-agentti (XAI Reporter Agent).

    Responsible for generating the final, explainable report.
    """

    state_field = "step_reporter"
    REQUIRES_KEYS = ["step_judge"]

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        """
        Returns the expected output schema.

        Use the Domain Model directly to ensure strict validation.
        The dynamic generation was causing issues with Optional fields and Type mismatches.

        Returns:
            Optional[Type[BaseModel]]: XAIReport schema.
        """
        return XAIReport

    async def execute(self, state: WorkflowState, system_instruction: Optional[str] = None, **kwargs) -> WorkflowState:
        """
        Executes the XAI Reporter Agent logic.

        Strictly forwards kwargs without injecting local defaults, as configuration
        must come from the WorkflowEngine/Config.

        Args:
            state (WorkflowState): Current workflow state.
            system_instruction (Optional[str]): System prompt.
            **kwargs: Extra arguments.

        Returns:
            WorkflowState: Updated workflow state.
        """
        return await super().execute(state, system_instruction, **kwargs)

    def post_process(self, state: WorkflowState) -> WorkflowState:
        """
        Lifecycle Hook: Post-Execution.

        Generates the final human-readable report by calling the reporting hook.

        Args:
            state (WorkflowState): Current workflow state.

        Returns:
            WorkflowState: Updated state with the generated report.
        """
        logger.info("[XAIReporterAgent] Running post_process hook...")
        from backend.hooks.reporting import generate_report

        return generate_report(state)
