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
    state_field = "step_reporter"

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        # Use the Domain Model directly to ensure strict validation.
        # The dynamic generation was causing issues with Optional fields and Type mismatches.
        return XAIReport

    async def execute(self, state: WorkflowState, system_instruction: Optional[str] = None, **kwargs) -> WorkflowState:
        # Override to increase output token limit for large reports
        # Gemini 1.5 Pro/Flash supports up to 8k output natively usually, 
        # but let's try pushing it to 16k if the model supports it, 
        # or at least ensure we are requesting the max safe amount.
        return await super().execute(state, system_instruction, max_tokens=16384, **kwargs)

    def generate_jinja2_report(self, state: WorkflowState) -> WorkflowState:
        """
        HOOK: generate_jinja2_report
        Post-Hook. Generates the final human-readable report using Jinja2 templates.
        Migrated from backend.services.hooks.
        """
        logger.info("[XAIReporterAgent] Running generate_jinja2_report...")
        
        import os
        from jinja2 import Environment, FileSystemLoader
        
        try:
            # 1. Setup Jinja2 Environment
            # Traverse up from backend/agents/xai.py -> backend/agents -> backend -> [root] -> backend/templates ?
            # Current file: .../backend/agents/xai.py
            # Base dir (backend/): os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # Correct path resolution to 'backend/templates'
            agents_dir = os.path.dirname(os.path.abspath(__file__))
            backend_dir = os.path.dirname(agents_dir) 
            template_dir = os.path.join(backend_dir, 'templates')
            
            if not os.path.exists(template_dir):
                logger.error(f"[XAIReporterAgent] Template directory not found: {template_dir}")
                return state

            env = Environment(loader=FileSystemLoader(template_dir))
            template = env.get_template('report_template.jinja2')
            
            # 2. Gather Data from State
            if not state.step_reporter:
                logger.warning("[XAIReporterAgent] No XAI Report data available.")
                return state
                
            xai_data = state.step_reporter # This is a Pydantic Model (XAIReport)
            
            # Extract scores (Preferably from Judge Step 8, fallback to XAI data)
            scores = {}
            if state.step_judge and state.step_judge.pisteet:
                p = state.step_judge.pisteet
                scores = {
                    "analysis": {"score": p.analyysi.arvosana if p.analyysi else 'N/A', "reasoning": p.analyysi.perustelu if p.analyysi else ''},
                    "evaluation": {"score": p.arviointi.arvosana if p.arviointi else 'N/A', "reasoning": p.arviointi.perustelu if p.arviointi else ''},
                    "synthesis": {"score": p.synteesi.arvosana if p.synteesi else 'N/A', "reasoning": p.synteesi.perustelu if p.synteesi else ''}
                }
            else:
                # Fallback to extracting from XAI text if needed, but Step 8 is safer
                pass
            
            # Helper to safely get list or empty list
            def get_list(val): return val if isinstance(val, list) else []
            
            # Extract critical findings from Judge Step 8
            critical_findings = []
            if state.step_judge and state.step_judge.kriittiset_havainnot_yhteenveto:
                critical_findings = get_list(state.step_judge.kriittiset_havainnot_yhteenveto)

            report_data = {
                "summary": xai_data.executive_summary or "Yhteenveto puuttuu.",
                "critical_findings": critical_findings,
                "pre_mortem_signals": state.aux_data.get('performative_patterns_detected', []), # Or similar
                "hitl_required": False, # Could check logic
                "ethical_issues": [], # Could fetch from Overseer Step 5
                "audit_questions": [], # Could fetch from Overseer Step 5
                "uncertainty": {},
                "scores": scores
            }
            
            # Add Overseer Data if available
            if state.step_overseer:
                 report_data["ethical_issues"] = get_list(state.step_overseer.eettiset_havainnot)
                 report_data["audit_questions"] = get_list(state.step_overseer.faktantarkistus_rfi)

            # Render
            disclaimer = "Tämä on automaattisesti generoitu raportti."
            rendered_report = template.render(
                report_content=report_data,
                final_verdict=xai_data.final_verdict or "KATSO PISTEYTYS",
                reliability_score=str(xai_data.confidence_score) if xai_data.confidence_score else "KORKEA",
                disclaimer=disclaimer
            )
            
            # Store formatted report in state
            # Now saving to the persistent schema field so it gets projected to the result.
            state.step_reporter.xai_report_formatted = rendered_report
            logger.info("[XAIReporterAgent] Report generated and saved to step_reporter.xai_report_formatted")
            
        except Exception as e:
            logger.error(f"[XAIReporterAgent] Report generation failed: {e}", exc_info=True)
            
        return state

    # --- Private Helpers for JSON Resilience (If needed for raw parsing, though Pydantic handles most) ---
    # Kept here if we ever need to parse raw strings inside the agent logic.
    
    def _repair_json_string(self, text: str) -> str:
        import re
        text = re.sub(r'\\u(?![0-9a-fA-F]{4})', r'\\\\u', text)
        text = re.sub(r'\\(?![/\"\\bfnrtu])', r'\\\\', text)
        return text
