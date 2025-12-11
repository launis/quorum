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

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return ArgumentaatioAnalyysi

    def _update_state(self, state: WorkflowState, response_data: Any) -> WorkflowState:
        try:
            validated_data = ArgumentaatioAnalyysi(**response_data)
            state.step_3_logician = validated_data
        except Exception as e:
            logger.error(f"[LogicianAgent] State update failed: {e}")
            raise e
        return state
