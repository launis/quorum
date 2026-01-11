"""Logician Agent implementation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pydantic import BaseModel

from backend.agents.base import BaseAgent
from backend.models.domain import ArgumentaatioAnalyysi

if TYPE_CHECKING:
    from backend.models.state import WorkflowState

logger = logging.getLogger(__name__)


class LogicianAgent(BaseAgent):
    """Loogikko-agentti (Logician Agent).

    Responsible for:
    1. Argument Construction (Argumentaation Rakentaminen)
    2. Applying Cognitive Assessment Matrix (Bloom/Toulmin)
    """

    state_field = "step_logician"
    PRODUCES_KEYS = ["step_logician"]

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the expected output schema.

        Returns:
            Optional[Type[BaseModel]]: ArgumentaatioAnalyysi schema.

        """
        return ArgumentaatioAnalyysi

    async def execute(self, state: WorkflowState, system_instruction: str | None = None, **kwargs) -> WorkflowState:
        """Executes argument reconstruction and cognitive assessment.

        Input State:
            - state.inputs (History, Product, Reflection).

        Output State:
            - state.step_logician (ArgumentaatioAnalyysi): Argument map and scoring.

        Exceptions:
            - AgentExecutionError: If LLM fails.
        """
        return await super().execute(state, system_instruction, **kwargs)
