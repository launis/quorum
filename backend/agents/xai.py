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
        # DYNAMIC SCHEMA GENERATION
        # Reads 'STANDARD_REPORT_OUTPUT' from seed_data.json (Source of Truth)
        # to construct a Pydantic model that matches the DB config.
        try:
            import json
            from pydantic import create_model, Field
            from backend.config import SEED_DATA_PATH
            
            with open(SEED_DATA_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Find STANDARD_REPORT_OUTPUT
            output_config = next((c for c in data.get('components', []) if c['id'] == 'STANDARD_REPORT_OUTPUT'), None)
            
            if output_config:
                fields = {}
                for field_name in output_config.get('content', []):
                    # Simple handling: All dynamic fields are strings (or we could infer type)
                    # Use alias? No, simpler to just use the name.
                    # Handle dot notation? Pydantic fields can't have dots.
                    # We'll replace dots with underscores for the field name, 
                    # but we might need aliases if we want the JSON output to strictly match.
                    # For now, let's assume flat or sanitize.
                    safe_name = field_name.replace('.', '_')
                    fields[safe_name] = (Optional[str], Field(default=None, description=f"Dynamic field: {field_name}"))
                
                # Base it on XAIReport to keep existing logic/methods if any
                # But XAIReport has rigid fields. 
                # Better to create a fresh model or Extend XAIReport.
                # Let's EXTEND XAIReport so we keep the base fields and add new ones.
                
                DynamicReport = create_model(
                    'DynamicXAIReport',
                    __base__=XAIReport,
                    **fields
                )
                return DynamicReport
                
        except Exception as e:
            logger.error(f"[XAIReporterAgent] Failed to generate dynamic schema: {e}")
            # Fallback
            return XAIReport
            
        return XAIReport

    async def execute(self, state: WorkflowState, system_instruction: Optional[str] = None, **kwargs) -> WorkflowState:
        # Override to increase output token limit for large reports
        # Gemini 1.5 Pro/Flash supports up to 8k output natively usually, 
        # but let's try pushing it to 16k if the model supports it, 
        # or at least ensure we are requesting the max safe amount.
        return await super().execute(state, system_instruction, max_tokens=16384, **kwargs)

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
