"""Reporting hooks for generating XAI reports."""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from jinja2 import Environment, FileSystemLoader

from backend.exceptions import AppException
from backend.models.domain import (
    ReportContext,
    ReportResult,
)
from backend.services.localization import LocalizationService
from backend.models.state import WorkflowState

logger = logging.getLogger(__name__)


def _safe_get(obj: Any, attr: str, default: Any = None) -> Any:
    """Helper for safe access to Pydantic models or Dicts.
    
    Args:
        obj: The object or dictionary to access.
        attr: The attribute or key name.
        default: The value to return if not found.
        
    Returns:
        The value of the attribute/key or the default.
    """
    if isinstance(obj, dict):
        return obj.get(attr, default)
    return getattr(obj, attr, default)


def _normalize_scores(data: Any, scores_dict: Dict[str, Any]) -> None:
    """Normalizes scores from various agent outputs into a unified dictionary."""
    # V2 EvaluationResult (List[DimensionResultItem])
    if hasattr(data, "dimensions") and isinstance(data.dimensions, list):
        for d in data.dimensions:
            # Map to Finnish keys for Frontend/Template compatibility
            # We enforce Pydantic access
            scores_dict[d.dimension_id] = {"arvosana": d.score, "perustelu": d.reasoning}
        return
    
    # If data is a dict (from context_variables), check for dimensions key
    if isinstance(data, dict):
        dimensions = data.get("dimensions")
        if isinstance(dimensions, list):
             for d in dimensions:
                 # Handle dict items in list
                 d_id = d.get("dimension_id")
                 score = d.get("score")
                 reasoning = d.get("reasoning")
                 if d_id and score is not None:
                      scores_dict[d_id] = {"arvosana": score, "perustelu": reasoning}


def generate_report(state: WorkflowState) -> WorkflowState:
    """HOOK: generate_report.

    Post-execution hook that aggregates results from all agents (Judge, Overseer, Reporter)
    and renders a human-readable Markdown report using a Jinja2 template.

    Outputs:
        Populates 'step_xai.xai_report_formatted' with the rendered Markdown.

    Args:
        state (WorkflowState): Current workflow state containing all agent outputs.

    Returns:
        WorkflowState: Updated state with the final report.

    Raises:
        AppException: If report generation fails (Fail Fast).
    """
    logger.debug("[ReportingHook] Generating report (Strict V2 Common Output).")

    try:
        # 1. Setup Jinja2 Environment
        hooks_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(hooks_dir)
        template_dir = os.path.join(backend_dir, "templates")

        if not os.path.exists(template_dir):
            error_code = "REPORT_TEMPLATE_DIR_MISSING"
            logger.error(f"[ReportingHook] {error_code}: {template_dir}")
            raise AppException(
                message=f"Template directory not found: {template_dir}",
                status_code=500,
                details={"error_code": error_code}
            )

        env = Environment(loader=FileSystemLoader(template_dir))
        try:
            template = env.get_template("report_template.jinja2")
        except Exception as e:
            error_code = "REPORT_TEMPLATE_LOAD_FAILED"
            raise AppException(
                 message=f"Failed to load report template: {e}",
                 status_code=500,
                 details={"error_code": error_code}
            ) from e

        # 2. Gather Data from State (Event Sourcing / Context Variables ONLY)
        xai_data = state.context_variables.get("step_xai")

        if not xai_data:
            logger.warning("[ReportingHook] No XAI Report data available in context_variables. Skipping.")
            return state

        # --- DYNAMIC EVALUATION DISCOVERY ---
        eval_steps = []

        # 1. Discovery from strict context_variables
        if state.context_variables:
            for key, val in state.context_variables.items():
                if key.startswith("step_") and val:
                    # Check if it looks like an evaluation (V2 Structure)
                    # We look for 'dimensions' list primarily, or 'total_score'
                    dimensions = _safe_get(val, "dimensions")
                    total_score = _safe_get(val, "total_score")

                    if (dimensions and isinstance(dimensions, list)) or total_score is not None:
                         # De-duplicate if in audit_results
                         if hasattr(state, "audit_results") and key in state.audit_results:
                             continue
                         eval_steps.append((key, val))

        # 2. Discovery from audit_results (Prioritized)
        if hasattr(state, "audit_results") and state.audit_results:
            for step_id, res in state.audit_results.items():
                eval_steps.append((step_id, res))

        # Sort by step ID
        eval_steps.sort(key=lambda x: x[0])

        comparison_data = None
        scores: Dict[str, Any] = {}

        # --- COMPARISON MATRIX LOGIC ---
        if len(eval_steps) >= 2:
            left_id, left_data = eval_steps[0]
            right_id, right_data = eval_steps[1]

            # Helper to normalize data to Dict[dimension_key, {arvosana, perustelu}]
            def normalize_to_dict(data):
                # V2 EvaluationResult Only
                dims = _safe_get(data, "dimensions")
                if dims and isinstance(dims, list):
                    result = {}
                    for d in dims:
                         # Handle Pydantic or Dict
                         d_id = _safe_get(d, "dimension_id")
                         score = _safe_get(d, "score")
                         reason = _safe_get(d, "reasoning")
                         if d_id:
                             result[d_id] = {"arvosana": score, "perustelu": reason}
                    return result
                return {}

            l_dict = normalize_to_dict(left_data)
            r_dict = normalize_to_dict(right_data)

            common_keys = sorted(list(set(l_dict.keys()) | set(r_dict.keys())))

            rows = []
            for k in common_keys:
                # Helper to extract score/reasoning
                def get_details(d, key):
                    item = d.get(key)
                    if not item:
                        return None
                    return {"score": item["arvosana"], "reasoning": item["perustelu"]}

                l_det = get_details(l_dict, k)
                r_det = get_details(r_dict, k)

                delta: float | None = 0
                if l_det and r_det:
                    try:
                        delta = float(r_det["score"]) - float(l_det["score"])
                    except (ValueError, TypeError):
                        pass
                elif l_det:
                    delta = None
                elif r_det:
                    delta = None

                rows.append(
                    {
                        "dimension": k,
                        "left": l_det,
                        "right": r_det,
                        "delta": delta,
                    }
                )

            comparison_data = {
                "mode": "dual",
                "left_label": left_id,
                "right_label": right_id,
                "rows": rows,
            }
            
            # Save to XAI Report Model
            if isinstance(xai_data, dict):
                xai_data["comparison_data"] = comparison_data
            else:
                try:
                    setattr(xai_data, "comparison_data", comparison_data)
                except Exception:
                    pass

        # Populate Standard Score Summary
        primary_eval = eval_steps[-1][1] if eval_steps else None
        judge_step = primary_eval

        if primary_eval:
            try:
                _normalize_scores(primary_eval, scores)
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
        def _get_list(val: Any) -> List[Any]:
            return val if isinstance(val, list) else []

        # Extract critical findings (V2 Only)
        critical_findings = []
        if judge_step:
            crit = _safe_get(judge_step, "critical_findings")
            # If strictly V2, we expect a list of strings or objects
            if crit:
                critical_findings = _get_list(crit)

        exec_summary = _safe_get(xai_data, "executive_summary")

        typed_scores = {}
        for k, v in scores.items():
            typed_scores[k] = v

        # Prepare arguments for ReportContext
        def _get_aux(key: str, default: Any = None) -> Any:
             aux = getattr(state, "aux_data", {})
             if isinstance(aux, dict):
                 return aux.get(key, default)
             return getattr(aux, key, default)

        ctx_args = {
            "summary": exec_summary,
            "critical_findings": critical_findings,
            "pre_mortem_signals": _get_aux("performative_patterns_detected", []),
            "hitl_required": False,
            "ethical_issues": [],
            "audit_questions": [],
            "uncertainty": {},
            "scores": typed_scores,
            "average_score": average_score,
            "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "coaching_plan": None,
            # Hook-injected data
            "penalties_applied": _get_aux("penalties_applied", []),
            "score_summary": _get_aux("score_summary"),
            "input_control_ratio": _get_aux("input_control_ratio"),
            "structural_warnings": _get_aux("structural_warnings", []),
            "archivist_precedents": _get_aux("archivist_precedents"),
            "google_search_results": _get_aux("google_search_results", []),
            "word_count": _get_aux("word_count"),
            "knowledge_items": [],
            "bibliography": [],
        }

        # Add Bibliography
        bib_result = state.context_variables.get("bibliography_result")
        if bib_result:
            if hasattr(bib_result, "references"):
                ctx_args["bibliography"] = bib_result.references
            elif isinstance(bib_result, dict):
                 ctx_args["bibliography"] = bib_result.get("references", [])

        # Add Retrieval Data
        step_retrieval = state.context_variables.get("step_retrieval")
        if step_retrieval:
             k_items = _safe_get(step_retrieval, "knowledge_items")
             if k_items:
                 ctx_args["knowledge_items"] = _get_list(k_items)

        # Add Overseer Data
        step_overseer = state.context_variables.get("step_overseer")
        if step_overseer:
            def _serialize_list(items):
                serialized = []
                for item in _get_list(items):
                    if hasattr(item, "model_dump"):
                        serialized.append(item.model_dump())
                    elif isinstance(item, dict):
                        serialized.append(item)
                    else:
                        serialized.append(item.__dict__)
                return serialized

            ctx_args["ethical_issues"] = _serialize_list(_safe_get(step_overseer, "eettiset_havainnot"))
            ctx_args["audit_questions"] = _serialize_list(_safe_get(step_overseer, "faktantarkistus_rfi"))

        # Add Coaching Plan
        step_coach = state.context_variables.get("step_coach")
        if step_coach:
            cp = _safe_get(step_coach, "coaching_plan") or step_coach
            if hasattr(cp, "model_dump"):
                ctx_args["coaching_plan"] = cp.model_dump()
            else:
                ctx_args["coaching_plan"] = cp

        # Add Specialist Agents
        def _extract_specialist_data(step_name, data_attr):
             step_data = state.context_variables.get(step_name)
             if not step_data:
                 return None

             val = _safe_get(step_data, data_attr)
             return val

        ctx_args["logician_data"] = _extract_specialist_data("step_logician", "logician_data")
        ctx_args["falsifier_data"] = _extract_specialist_data("step_falsifier", "falsifier_data")
        ctx_args["causal_analysis"] = _extract_specialist_data("step_causal", "causal_analysis")
        ctx_args["performativity_analysis"] = _extract_specialist_data("step_detector", "performativity_analysis")
        ctx_args["overseer_data"] = _extract_specialist_data("step_overseer", "overseer_data")

        # Instantiate Model
        try:
            report_context = ReportContext(**ctx_args)
        except Exception as e:
             error_code = "REPORT_CONTEXT_VALIDATION_FAILED"
             logger.error(f"[ReportingHook] {error_code}: {e}")
             raise AppException(
                 message=f"Report Context validation failed: {e}",
                 status_code=500,
                 details={"error_code": error_code, "original_error": str(e)}
             ) from e

        # 3. Render
        loc = LocalizationService()
        disclaimer = loc.get("Report.Disclaimer")
        final_verdict = _safe_get(xai_data, "final_verdict")
        confidence_score = _safe_get(xai_data, "confidence_score")

        try:
            output_text = template.render(
                report_content=report_context,
                final_verdict=final_verdict,
                reliability_score=str(confidence_score) if confidence_score else None,
                disclaimer=disclaimer,
            )
        except Exception as e:
            error_code = "REPORT_TEMPLATE_RENDER_FAILED"
            raise AppException(
                message=f"Template rendering failed: {e}",
                status_code=500,
                details={"error_code": error_code}
            ) from e

        # 4. Save to State
        report_result = ReportResult(
            report_content=output_text,
            format="markdown",
            data=report_context
        )

        new_context = state.context_variables.copy()
        new_context["report_result"] = report_result
        new_context["xai_report_formatted"] = output_text
        new_context["final_report_markdown"] = output_text

        if xai_data and isinstance(xai_data, dict):
             xai_data["xai_report_formatted"] = output_text
             new_context["step_xai"] = xai_data

        logger.debug("[ReportingHook] Report generated (strict mode).")

        return state.model_copy(update={"context_variables": new_context})

    except AppException:
        raise
    except Exception as e:
        error_code = "REPORT_GENERATION_FAILED"
        logger.error(f"⚠️ [ReportingHook] {error_code}: {str(e)}", exc_info=True)
        raise AppException(
            message=f"Report generation failed: {str(e)}",
            status_code=500,
            details={"error_code": error_code, "cause": str(e)}
        ) from e
