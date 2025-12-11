from typing import Any, Optional, Type
from backend.agents.base import BaseAgent
from backend.models.state import WorkflowState
from backend.models.domain import TodistusKartta
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class AnalystAgent(BaseAgent):
    """
    Analyytikko-agentti (Analyst Agent).
    Responsible for:
    1. Evidence Anchoring (Todistepohjainen Ankkurointi)
    2. Creating an 'Evidence Map' (Todistuskartta)
    """

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return TodistusKartta

    def _update_state(self, state: WorkflowState, response_data: Any) -> WorkflowState:
        try:
            validated_data = TodistusKartta(**response_data)
            state.step_2_analyst = validated_data
        except Exception as e:
            logger.error(f"[AnalystAgent] State update failed: {e}")
            raise e
        return state
