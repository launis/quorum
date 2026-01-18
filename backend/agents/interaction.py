"""Interaction Analyst Agent implementation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.models.domain import InteractionAnalysis

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class InteractionAnalystAgent(BaseAgent):
    """InteractionAnalystAgent (Vuorovaikutusanalysaattori).

    Analyses the 'history_text' to evaluate Prompt Engineering competence.
    Hybrid logic:
    - AI: Qualitative analysis (Strategies, Driver Classification).
    - Python: Quantitative analysis (Input Control Ratio).
    """

    state_field = "step_interaction"
    REQUIRES_KEYS = ["history_text"]

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the expected output schema.

        Returns:
            Optional[Type[BaseModel]]: InteractionAnalysis schema.

        """
        return InteractionAnalysis

    async def execute(
        self,
        input_data: dict,
        execution_context: dict | None = None,
        system_instruction: str | None = None,
        **kwargs,
    ) -> dict:
        """Executes interaction analysis (Driver/Passenger classification).

        Args:
            input_data (dict): Inputs including history_text.
            execution_context (dict): Context.
            system_instruction (str): Prompt.
            **kwargs: Args.

        Returns:
            dict: InteractionAnalysis.
        """
        # Note: Control ratio is now calculated via centralized HOOK_MAPPING (pre_hooks in seed_data.json)
        return await super().execute(input_data, execution_context, system_instruction, **kwargs)
