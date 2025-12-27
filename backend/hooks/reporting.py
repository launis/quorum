import os
import logging
from datetime import datetime
from typing import Any, Dict, Optional
from jinja2 import Environment, FileSystemLoader
from backend.models.state import WorkflowState
from backend.models.domain import XAIReport

logger = logging.getLogger(__name__)

def generate_report(state: WorkflowState) -> WorkflowState:
    """
    HOOK: generate_report
    Post-execution hook that aggregates results from all agents (Judge, Overseer, Reporter)
    and renders a human-readable Markdown report using a Jinja2 template.

    Outputs:
        Populates 'step_reporter.xai_report_formatted' with the rendered Markdown.

    Args:
        state (WorkflowState): Current workflow state containing all agent outputs.

    Returns:
        WorkflowState: Updated state with the final report.
    """
    logger.info("[ReportingHook] Generating report...")
    
    try:
        # 1. Setup Jinja2 Environment
        # Resolve path relative to THIS file (backend/hooks/reporting.py)
        # Hooks dir: .../backend/hooks
        # Base dir (backend/): .../backend
        
        hooks_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(hooks_dir) 
        template_dir = os.path.join(backend_dir, 'templates')
        
        if not os.path.exists(template_dir):
            logger.error(f"[ReportingHook] Template directory not found: {template_dir}")
            return state

        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template('report_template.jinja2')
        
        # 2. Gather Data from State
        if not state.step_reporter:
            logger.warning("[ReportingHook] No XAI Report data available.")
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
            "scores": scores,
            "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M")
        }
        
        # Add Overseer Data if available
        if state.step_overseer:
                report_data["ethical_issues"] = get_list(state.step_overseer.eettiset_havainnot)
                report_data["audit_questions"] = get_list(state.step_overseer.faktantarkistus_rfi)

        # 3. Render
        disclaimer = "Tämä on automaattisesti generoitu raportti."
        output_text = template.render(
            report_content=report_data,
            final_verdict=xai_data.final_verdict or "KATSO PISTEYTYS",
            reliability_score=str(xai_data.confidence_score) if xai_data.confidence_score else "KORKEA",
            disclaimer=disclaimer
        )
        
        # 4. Save to State
        # Usage: XAIReport.xai_report_formatted
        if state.step_reporter:
             state.step_reporter.xai_report_formatted = output_text
             logger.info("[ReportingHook] Report generated and saved to step_reporter.xai_report_formatted")
        else:
             state.aux_data['final_report_markdown'] = output_text
        
    except Exception as e:
        logger.error(f"[ReportingHook] Report generation failed: {e}")
        
    return state
