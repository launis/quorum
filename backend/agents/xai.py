"""XAI Reporter Agent implementation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.models.domain import XAIReport

if TYPE_CHECKING:
    from backend.models.state import WorkflowState

logger = logging.getLogger(__name__)


class XAIReporterAgent(BaseAgent):
    """XAI-Raportoija-agentti (XAI Reporter Agent).

    Responsible for generating the final, explainable report.
    """

    state_field = "step_reporter"
    REQUIRES_KEYS = ["step_judge"]

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the expected output schema.

        Use the Domain Model directly to ensure strict validation.
        The dynamic generation was causing issues with Optional fields and Type mismatches.

        Returns:
            Optional[Type[BaseModel]]: XAIReport schema.

        """
        return XAIReport

    async def execute(
        self,
        state: WorkflowState | None = None,
        system_instruction: str | None = None,
        **kwargs,
    ) -> WorkflowState:
        """Executes the XAI Reporter Agent logic.

        Input State:
            - state.step_judge (Primary input for report).
            - state (Full context read for synthesis).

        Output State:
            - state.step_reporter (XAIReport): The final explanation/report.
            - (Post-Hook): Generates human-readable text via `generate_report`.

        Exceptions:
            - AgentExecutionError: If LLM fails.
        """
        return await super().execute(state, system_instruction, **kwargs)

    def post_process(self, state: WorkflowState) -> WorkflowState:
        """Lifecycle Hook: Post-Execution.

        Generates the final human-readable report by calling the reporting hook.

        Args:
            state (WorkflowState): Current workflow state.

        Returns:
            WorkflowState: Updated state with the generated report.

        """
        logger.info("[XAIReporterAgent] Running post_process hook...")
        from backend.hooks.reporting import generate_report

        return generate_report(state)
