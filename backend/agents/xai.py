from typing import Any, Optional, Type
from backend.agents.base import BaseAgent
from backend.models.state import WorkflowState
from backend.models.domain import XAIReport
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class XAIReporterAgent(BaseAgent):
    """
    XAI-Raportoija-agentti (XAI Reporter Agent).
    """
    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return XAIReport

    def _update_state(self, state: WorkflowState, response_data: Any) -> WorkflowState:
        try:
            state.step_9_reporter = XAIReport(**response_data)
        except Exception as e:
            logger.error(f"[XAIReporterAgent] State update failed: {e}")
            raise e
        return state

    def generate_jinja2_report(self, state: WorkflowState) -> WorkflowState:
        """
        HOOK: generate_jinja2_report
        Post-Hook. Generates the final human-readable report using Jinja2 templates (if implemented).
        """
        logger.info("[XAIReporterAgent] Running generate_jinja2_report...")
        # Placeholder logic
        if state.step_9_reporter:
            # Maybe flatten or format something for UI?
            pass
        return state
