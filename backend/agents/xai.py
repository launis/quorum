from typing import Any, Optional, Type
from backend.agents.base import BaseAgent
from backend.models.state import WorkflowState
from backend.models.domain import XAIReport
from pydantic import BaseModel
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class XAIReporterAgent(BaseAgent):
    """
    XAI-Raportoija-agentti (XAI Reporter Agent).
    """
    state_field = "step_reporter"
    REQUIRES_KEYS = ["step_judge"]

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        # Use the Domain Model directly to ensure strict validation.
        # The dynamic generation was causing issues with Optional fields and Type mismatches.
        return XAIReport

    async def execute(self, state: WorkflowState, system_instruction: Optional[str] = None, **kwargs) -> WorkflowState:
        # Configuration (max_tokens, etc.) must come from the WorkflowEngine/Config.
        # We strictly forward kwargs without injecting local defaults.
        return await super().execute(state, system_instruction, **kwargs)

    def post_process(self, state: WorkflowState) -> WorkflowState:
        """
        Lifecycle Hook: Post-Execution.
        Generates the final human-readable report using backend.hooks.reporting.
        """
        logger.info("[XAIReporterAgent] Running post_process hook...")
        from backend.hooks.reporting import generate_report
        return generate_report(state)

