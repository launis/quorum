"""Logician Agent implementation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.models.domain import LogicianOutput

if TYPE_CHECKING:
    pass

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
            Optional[Type[BaseModel]]: LogicianOutput schema.

        """
        return LogicianOutput

    async def prepare_context(self, input_data: dict, execution_context: dict | None, **kwargs) -> str | None:
        """Lifecycle Hook: Pre-Execution.

        Injects the Evidence Map (AnalystOutput) from the Analyst step.

        Args:
            input_data (dict): Inputs.
            execution_context (dict): Context.
            **kwargs: execution arguments.

        Returns:
            Optional[str]: Formatted context.
        """
        # 1. Resolve Input (Prefer kwargs from wiring, then input_data)
        analyst_output = kwargs.get("step_analyst")
        if not analyst_output:
            analyst_output = input_data.get("step_analyst")

        # 2. Format Context
        if analyst_output:
            content = (
                analyst_output.model_dump_json(indent=2)
                if hasattr(analyst_output, "model_dump_json")
                else str(analyst_output)
            )
            return f"### TODISTUSKARTTA (EVIDENCE MAP):\n{content}"

        return None

    async def execute(
        self,
        input_data: dict,
        execution_context: dict | None = None,
        system_instruction: str | None = None,
        **kwargs,
    ) -> dict:
        """Executes argument reconstruction and cognitive assessment.

        Args:
            input_data (dict): Inputs.
            execution_context (dict): Context.
            system_instruction (str): Prompt.
            **kwargs: Args.

        Returns:
            dict: LogicianData.
        """
        return await super().execute(input_data, execution_context, system_instruction, **kwargs)
