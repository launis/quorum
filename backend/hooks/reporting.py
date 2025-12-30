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
    
    # Helper for safe access (Pydantic or Dict)
    def safe_get(obj, attr, default=None):
        if isinstance(obj, dict):
            return obj.get(attr, default)
        return getattr(obj, attr, default)

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
            
        xai_data = state.step_reporter # This is a Pydantic Model (XAIReport) OR dict
        
        # --- DYNAMIC EVALUATION DISCOVERY ---
        eval_steps = []
        # Introspect state for any steps that look like EvaluationResult (have 'pisteet')
        for attr_name in dir(state):
            if attr_name.startswith('step_'):
                val = getattr(state, attr_name)
                # Check for Pydantic model with 'pisteet' field that is not None
                # Handle dict case:
                pisteet = safe_get(val, 'pisteet')
                if val and pisteet:
                    eval_steps.append((attr_name, val))
        
        # Sort by step ID to ensure deterministic comparison
        eval_steps.sort(key=lambda x: x[0])
        
        comparison_data = None
        scores = {}
        
        # If we have multiple judges, we build the comparison matrix
        if len(eval_steps) >= 2:
            left_id, left_data = eval_steps[0]
            right_id, right_data = eval_steps[1]
            
            # Extract common keys
            l_pisteet = safe_get(left_data, 'pisteet')
            r_pisteet = safe_get(right_data, 'pisteet')

            l_dict = l_pisteet.model_dump() if hasattr(l_pisteet, 'model_dump') else (l_pisteet if isinstance(l_pisteet, dict) else l_pisteet.__dict__)
            r_dict = r_pisteet.model_dump() if hasattr(r_pisteet, 'model_dump') else (r_pisteet if isinstance(r_pisteet, dict) else r_pisteet.__dict__)
            
            # Filter out None/Empty values
            l_dict = {k: v for k, v in l_dict.items() if v}
            r_dict = {k: v for k, v in r_dict.items() if v}
            
            common_keys = sorted(list(set(l_dict.keys()) | set(r_dict.keys()))) # Union of keys
            
            rows = []
            for k in common_keys:
                # Helper to extract score/reasoning
                def get_details(d, key):
                    item = d.get(key)
                    if not item: return {"score": 0, "reasoning": ""}
                    # Handle Pydantic object or dict
                    score = safe_get(item, 'arvosana', 0)
                    reasoning = safe_get(item, 'perustelu', "")
                    return {"score": score, "reasoning": reasoning}

                l_det = get_details(l_dict, k)
                r_det = get_details(r_dict, k)
                
                rows.append({
                    "dimension": k,
                    "left": l_det,
                    "right": r_det,
                    "delta": float(r_det['score']) - float(l_det['score'])
                })
                
            comparison_data = {
                "mode": "dual",
                "left_label": left_id, # Frontend can override with Metadata label if available
                "right_label": right_id,
                "rows": rows
            }
            # Save to XAI Report Model
            # Handle assignment carefully if xai_data is dict
            if isinstance(xai_data, dict):
                xai_data['comparison_data'] = comparison_data
            else:
                xai_data.comparison_data = comparison_data  # Removed field from schema but might exist dynamically? No, handled by extra='allow'

        # Populate Standard Score Summary
        # We take the primary (latest) evaluation for the high-level summary.
        primary_eval = eval_steps[-1][1] if eval_steps else None 
        judge_step = primary_eval # Reference for critical findings logic
        
        p = safe_get(primary_eval, 'pisteet')
        if primary_eval and p:
            # Generic loop for all attributes in Pisteet
            # This supports dynamic keys (analyysi, ethics, code_quality etc)
            p_dict = p.model_dump() if hasattr(p, 'model_dump') else (p if isinstance(p, dict) else p.__dict__)
            
            for k, v in p_dict.items():
                if v:
                    if isinstance(v, dict):
                        val = v.get('arvosana')
                        reason = v.get('perustelu')
                    else:
                        val = getattr(v, 'arvosana', None)
                        reason = getattr(v, 'perustelu', None)

                    if val is not None:
                         scores[k] = {"score": val, "reasoning": reason or ""}
        
        # Helper to safely get list or empty list
        def get_list(val): return val if isinstance(val, list) else []
        
        # Extract critical findings from Judge Step
        critical_findings = []
        findings = safe_get(judge_step, 'kriittiset_havainnot_yhteenveto')
        if judge_step and findings:
            critical_findings = get_list(findings)

        exec_summary = safe_get(xai_data, 'executive_summary') or "Yhteenveto puuttuu."
        
        report_data = {
            "summary": exec_summary,
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
        
        final_verdict = safe_get(xai_data, 'final_verdict') or "KATSO PISTEYTYS"
        confidence_score = safe_get(xai_data, 'confidence_score')
        
        output_text = template.render(
            report_content=report_data,
            final_verdict=final_verdict,
            reliability_score=str(confidence_score) if confidence_score else "KORKEA",
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
        err_msg = f"⚠️ [ReportingHook] Report generation failed: {str(e)}"
        logger.error(err_msg, exc_info=True)
        if state.step_reporter:
            state.step_reporter.xai_report_formatted = f"# Virhe Raportoinnissa\n\nJärjestelmä ei voinut generoida raporttia.\n\n**Tekninen syy:** `{str(e)}`"
            # Optional: Mark comparison data as failed/empty to avoid UI guessing
            state.step_reporter.comparison_data = None
            
    return state
