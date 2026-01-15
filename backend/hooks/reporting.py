"""Reporting hooks for generating XAI reports."""

import logging
import os
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

from backend.models.state import WorkflowState

logger = logging.getLogger(__name__)


def generate_report(state: WorkflowState) -> WorkflowState:
    """HOOK: generate_report.

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
        template_dir = os.path.join(backend_dir, "templates")

        if not os.path.exists(template_dir):
            logger.error(f"[ReportingHook] Template directory not found: {template_dir}")
            return state

        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template("report_template.jinja2")

        # 2. Gather Data from State
        if not state.step_reporter:
            logger.warning("[ReportingHook] No XAI Report data available.")
            return state

        xai_data = state.step_reporter  # This is a Pydantic Model (XAIReport) OR dict

        # --- DYNAMIC EVALUATION DISCOVERY ---
        eval_steps = []

        # 1. V1 Legacy Discovery (Attributes on State)
        for attr_name in dir(state):
            if attr_name.startswith("step_"):
                val = getattr(state, attr_name)
                pisteet = safe_get(val, "pisteet")
                if val and pisteet:
                    # Prevent duplicates if V2 system also populated this (unlikely but safe)
                    if attr_name not in state.audit_results:
                        eval_steps.append((attr_name, val))

        # 2. V2 Dynamic Discovery (audit_results dict)
        if state.audit_results:
            for step_id, res in state.audit_results.items():
                eval_steps.append((step_id, res))

        # Sort by step ID to ensure deterministic comparison
        eval_steps.sort(key=lambda x: x[0])

        comparison_data = None
        scores = {}

        # --- COMPARISON MATRIX LOGIC ---
        # If we have multiple judges, we build the comparison matrix
        if len(eval_steps) >= 2:
            left_id, left_data = eval_steps[0]
            right_id, right_data = eval_steps[1]

            # Helper to normalize data to Dict[dimension_key, {arvosana, perustelu}]
            def normalize_to_dict(data):
                # V2 EvaluationResult
                if hasattr(data, "dimensions") and isinstance(data.dimensions, list):
                    return {d.dimension_id: {"arvosana": d.score, "perustelu": d.reasoning} for d in data.dimensions}
                # V1 TuomioJaPisteet
                p = safe_get(data, "pisteet")
                if p:
                    p_dict = p.model_dump() if hasattr(p, "model_dump") else (p if isinstance(p, dict) else p.__dict__)
                    # Filter out None keys
                    return {k: v for k, v in p_dict.items() if v}
                return {}

            l_dict = normalize_to_dict(left_data)
            r_dict = normalize_to_dict(right_data)

            common_keys = sorted(list(set(l_dict.keys()) | set(r_dict.keys())))  # Union of keys

            rows = []
            for k in common_keys:
                # Helper to extract score/reasoning
                def get_details(d, key):
                    item = d.get(key)
                    if not item:
                        return None  # Distinct from 0
                    # Handle Pydantic object or dict
                    score = safe_get(item, "arvosana", 0)
                    reasoning = safe_get(item, "perustelu", "")
                    return {"score": score, "reasoning": reasoning}

                l_det = get_details(l_dict, k)
                r_det = get_details(r_dict, k)

                delta: float | None = 0
                if l_det and r_det:
                    try:
                        delta = float(r_det["score"]) - float(l_det["score"])
                    except (ValueError, TypeError):
                        pass
                elif l_det:
                    # Only Left exists
                    delta = None
                elif r_det:
                    # Only Right exists
                    delta = None

                rows.append(
                    {
                        "dimension": k,
                        "left": l_det,  # Can be None
                        "right": r_det,  # Can be None
                        "delta": delta,
                    }
                )

            comparison_data = {
                "mode": "dual",
                "left_label": left_id,  # Frontend can override with Metadata label if available
                "right_label": right_id,
                "rows": rows,
            }
            # Save to XAI Report Model
            # Handle assignment carefully if xai_data is dict
            if isinstance(xai_data, dict):
                xai_data["comparison_data"] = comparison_data
            else:
                # Use setattr for Pydantic model with extra='allow'
                try:
                    xai_data.comparison_data = comparison_data
                except Exception:
                    pass

        # Populate Standard Score Summary
        # We take the primary (latest) evaluation for the high-level summary.
        primary_eval = eval_steps[-1][1] if eval_steps else None
        judge_step = primary_eval  # Reference for critical findings logic

        if primary_eval:
            # Normalize again for scores dict
            def normalize_scores(data):
                # V2
                if hasattr(data, "dimensions") and isinstance(data.dimensions, list):
                    for d in data.dimensions:
                        # Map to Finnish keys for Frontend/Template compatibility
                        scores[d.dimension_id] = {
                            "arvosana": d.score, 
                            "perustelu": d.reasoning
                        }
                    return
                # V1
                p = safe_get(data, "pisteet")
                if p:
                    p_dict = p.model_dump() if hasattr(p, "model_dump") else (p if isinstance(p, dict) else p.__dict__)
                    for k, v in p_dict.items():
                        if v:
                            val = safe_get(v, "arvosana")
                            reason = safe_get(v, "perustelu")
                            if val is not None:
                                scores[k] = {"arvosana": val, "perustelu": reason or ""}

            try:
                normalize_scores(primary_eval)
            except Exception as e:
                logger.warning(f"[ReportingHook] Failed to normalize scores: {e}")

        # Calculate Average Score
        valid_scores = [
            float(v["arvosana"]) 
            for v in scores.values() 
            if isinstance(v, dict) and "arvosana" in v and v["arvosana"] is not None
        ]
        average_score = round(sum(valid_scores) / len(valid_scores), 2) if valid_scores else 0.0

        # Helper to safely get list or empty list
        def get_list(val):
            return val if isinstance(val, list) else []

        # Extract critical findings from Judge Step
        critical_findings = []
        findings = safe_get(judge_step, "kriittiset_havainnot_yhteenveto")
        if judge_step and findings:
            critical_findings = get_list(findings)
        elif judge_step and hasattr(judge_step, "critical_findings"):  # V2
            critical_findings = getattr(judge_step, "critical_findings", [])

        # Import ReportContext (Local import to avoid circular deps if any, though top-level is better)
        from backend.models.domain import ReportContext, ReportScore

        exec_summary = safe_get(xai_data, "executive_summary") or "Yhteenveto puuttuu."

        # Construct ReportContext
        # Note: 'scores' needs to be converted to ReportScore objects
        # Update ReportScore to accept Finnish keys if needed, OR we map back to english for the Typed Model
        # BUT wait: Domain model likely expects English keys if I didn't change it.
        # Let's check domain.py next. For now, I will pass the dicts as-is if ReportScore allows it,
        # OR I must update ReportScore definition.
        # Assuming ReportScore is strictly typed, I need to check it.
        # However, for the Template (Jinja), we are passing 'report_context' which is a Pydantic model.
        # So I *MUST* update domain.py to support 'arvosana'/'perustelu' in ReportScore.
        
        typed_scores = {}
        for k, v in scores.items():
            # Pass as raw dict if model allows, or update model
            typed_scores[k] = v 

        # Prepare arguments for ReportContext
        ctx_args = {
            "summary": exec_summary,
            "critical_findings": critical_findings,
            "pre_mortem_signals": (
                state.aux_data.get("performative_patterns_detected", [])
                if isinstance(state.aux_data, dict)
                else getattr(state.aux_data, "performative_patterns_detected", [])
            ),
            "hitl_required": False,
            "ethical_issues": [],
            "audit_questions": [],
            "uncertainty": {},
            "scores": typed_scores,
            "average_score": average_score, # New Field
            "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "coaching_plan": None,
            # Hook-injected data (Jan 2026)
            "penalties_applied": (
                state.aux_data.get("penalties_applied", [])
                if isinstance(state.aux_data, dict)
                else getattr(state.aux_data, "penalties_applied", [])
            ),
            "score_summary": (
                state.aux_data.get("score_summary")
                if isinstance(state.aux_data, dict)
                else getattr(state.aux_data, "score_summary", None)
            ),
            "input_control_ratio": (
                state.aux_data.get("input_control_ratio")
                if isinstance(state.aux_data, dict)
                else getattr(state.aux_data, "input_control_ratio", None)
            ),
            # Hook outputs (Jan 2026 - Expanded)
            "structural_warnings": (
                state.aux_data.get("structural_warnings", [])
                if isinstance(state.aux_data, dict)
                else getattr(state.aux_data, "structural_warnings", [])
            ),
            "archivist_precedents": (
                state.aux_data.get("archivist_precedents")
                if isinstance(state.aux_data, dict)
                else getattr(state.aux_data, "archivist_precedents", None)
            ),
            "google_search_results": (
                state.aux_data.get("google_search_results", [])
                if isinstance(state.aux_data, dict)
                else getattr(state.aux_data, "google_search_results", [])
            ),
        }

        # Add Overseer Data if available
        # Add Overseer Data if available
        if state.step_overseer:
            # Helper to serialize list of models
            def serialize_list(items):
                serialized = []
                for item in get_list(items):
                    if hasattr(item, "model_dump"):
                        serialized.append(item.model_dump())
                    elif isinstance(item, dict):
                        serialized.append(item)
                    else:
                        serialized.append(item.__dict__)
                return serialized

            ctx_args["ethical_issues"] = serialize_list(state.step_overseer.eettiset_havainnot)
            ctx_args["audit_questions"] = serialize_list(state.step_overseer.faktantarkistus_rfi)

        # Add Coaching Plan
        if state.step_coach:
             # V1 vs V2 check
             cp = safe_get(state.step_coach, "coaching_plan") or state.step_coach
             if hasattr(cp, "model_dump"):
                 ctx_args["coaching_plan"] = cp.model_dump()
             else:
                 ctx_args["coaching_plan"] = cp
        
        # Instantiate Model to validate
        report_context = ReportContext(**ctx_args)
        
        # 3. Render
        disclaimer = "Tämä on automaattisesti generoitu raportti."

        final_verdict = safe_get(xai_data, "final_verdict") or "KATSO PISTEYTYS"
        confidence_score = safe_get(xai_data, "confidence_score")

        output_text = template.render(
            report_content=report_context, # Pass Pydantic object directly
            final_verdict=final_verdict,
            reliability_score=str(confidence_score) if confidence_score else "KORKEA",
            disclaimer=disclaimer,
        )

        # 4. Save to State
        # Usage: XAIReport.xai_report_formatted AND WorkflowState.xai_report_formatted (Top-Level)
        if state.step_reporter:
            state.step_reporter.xai_report_formatted = output_text
            state.xai_report_formatted = output_text  # <--- CRITICAL FIX: Hoist to top-level for Frontend
            logger.info("[ReportingHook] Report generated and saved to state.xai_report_formatted")
        else:
            state.aux_data["final_report_markdown"] = output_text
            state.xai_report_formatted = output_text  # Fallback hoist

    except Exception as e:
        err_msg = f"⚠️ [ReportingHook] Report generation failed: {str(e)}"
        logger.error(err_msg, exc_info=True)
        if state.step_reporter:
            state.step_reporter.xai_report_formatted = (
                f"# Virhe Raportoinnissa\n\nJärjestelmä ei voinut generoida raporttia.\n\n**Tekninen syy:** `{str(e)}`"
            )
            # Optional: Mark comparison data as failed/empty to avoid UI guessing
            state.step_reporter.comparison_data = None

    return state
