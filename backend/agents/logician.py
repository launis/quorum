from typing import Any, Optional, Type
from backend.agents.base import BaseAgent
from backend.models.state import WorkflowState
from backend.models.domain import ArgumentaatioAnalyysi
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class LogicianAgent(BaseAgent):
    """
    Loogikko-agentti (Logician Agent).

    Responsible for:
    1. Argument Construction (Argumentaation Rakentaminen)
    2. Applying Cognitive Assessment Matrix (Bloom/Toulmin)
    """

    state_field = "step_logician"
    PRODUCES_KEYS = ["step_logician"]

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        """
        Returns the expected output schema.

        Returns:
            Optional[Type[BaseModel]]: ArgumentaatioAnalyysi schema.
        """
        return ArgumentaatioAnalyysi
