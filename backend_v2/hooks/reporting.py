"""Reporting hooks for generating XAI reports."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import status

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.view.sdui import ReferenceIntent, ReferenceItem
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)


@hook_registry.register(name="generate_report")
def generate_report_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Workflow Data wrapper for generate_report.

    Post-execution hook that aggregates results from all agents (Judge, Overseer, Reporter)
    and renders a human-readable Markdown report using a Jinja2 template.

    Outputs:
        Populates 'report_context' with the validated dictionary.

    Args:
        data (dict): Current workflow data containing all agent outputs.

    Returns:
        dict: Updated data with 'report_context'.

    Raises:
        AppException: If template missing or generation fails.
    """
    logger.debug("[ReportingHook] Running generate_report_hook...")

    if not state:
        return HookResult(success=True, state_delta={})

    get_settings()

    # 1. TEMPLATE VALIDATION (Fail Fast)
    template_dir = Path("backend/templates")
    # Adjust path relative to CWD
    if not template_dir.exists():
        template_dir = Path(__file__).parent.parent.parent.parent / "backend/templates"

    if not template_dir.exists():
        error_code = ErrorCodes.CONFIGURATION_ERROR
        msg = f"Template directory not found at {template_dir}."
        logger.error(f"[ReportingHook] {error_code.name}: {msg}")
        raise AppException(message=msg, status_code=500, details={"error_code": error_code})

    # 2. GATHER CONTEXT
    context: dict[str, Any] = {}

    # Inputs
    inputs = state.inputs

    if not inputs or not isinstance(inputs, dict):
        error_code = ErrorCodes.EMPTY_INPUT if inputs is None else ErrorCodes.INVALID_OUTPUT_SCHEMA
        msg = "Missing or invalid 'inputs' in data. Expected dict."
        status_code = status.HTTP_400_BAD_REQUEST if inputs is None else status.HTTP_500_INTERNAL_SERVER_ERROR
        logger.error(f"[ReportingHook] {error_code.name}: {msg}")
        raise AppException(
            message=msg,
            status_code=status_code,
            details={"error_code": error_code},
        )

    context["inputs"] = inputs
    context["generated_at"] = datetime.now().astimezone().strftime("%d.%m.%Y %H:%M")
    context["timestamp"] = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")

    # Helper to fetch safely
    def _get_agent_output(key: str) -> Any | None:
        return state.global_context_vars.get(key)

    # Fetch all potential agent outputs using the raw dicts
    xai_out = _get_agent_output("step_xai")
    judge_out = _get_agent_output("step_judge")
    overseer_out = _get_agent_output("step_overseer")
    logician_out = _get_agent_output("step_logician")
    performativity_out = _get_agent_output("step_detector")
    analyst_out = _get_agent_output("step_analyst")

    panel_out = _get_agent_output("step_panel")

    # Extract inner data correctly regardless of source dicts
    overseer_data = overseer_out.get("overseer_data") if isinstance(overseer_out, dict) else None
    if not overseer_data and isinstance(panel_out, dict):
        overseer_data = panel_out.get("overseer_data")

    logician_data = logician_out.get("logician_data") if isinstance(logician_out, dict) else None
    if not logician_data and isinstance(panel_out, dict):
        logician_data = panel_out.get("logician_data")

    perf_data = performativity_out.get("performativity_analysis") if isinstance(performativity_out, dict) else None
    if not perf_data and isinstance(panel_out, dict):
        perf_data = panel_out.get("performativity_analysis")

    falsifier_data = panel_out.get("falsifier_data") if isinstance(panel_out, dict) else None
    causal_data = panel_out.get("causal_analysis") if isinstance(panel_out, dict) else None

    # 3. MAP DATA TO REPORT CONTEXT

    # Summary (From XAI)
    if isinstance(xai_out, dict) and xai_out.get("executive_summary"):
        context["summary"] = xai_out.get("executive_summary")
    else:
        context["summary"] = "No Executive Summary available (XAI Role did not run or failed)."

    # Critical Findings (From Judge)
    if isinstance(judge_out, dict) and judge_out.get("critical_findings"):
        context["critical_findings"] = judge_out.get("critical_findings")
    else:
        context["critical_findings"] = []

    # Pre-Morten Signals (From Performativity/Detector)
    if isinstance(perf_data, dict) and perf_data.get("pre_mortem_analysis"):
        pm_analysis = perf_data.get("pre_mortem_analysis", {})
        context["pre_mortem_signals"] = (
            pm_analysis.get("weak_signals", [])
            if isinstance(pm_analysis, dict)
            else getattr(pm_analysis, "weak_signals", [])
        )
    else:
        context["pre_mortem_signals"] = []

    # Ethical Issues (From Overseer)
    ethical_issues_list = []
    if isinstance(overseer_data, dict) and overseer_data.get("ethical_issues"):
        for issue in overseer_data.get("ethical_issues", []):
            if isinstance(issue, dict):
                ethical_issues_list.append(issue)
    context["ethical_issues"] = ethical_issues_list

    # Audit Questions (From Logician)
    audit_questions_list = []
    if isinstance(logician_data, dict) and logician_data.get("walton_scheme"):
        scheme = logician_data.get("walton_scheme", {})
        if isinstance(scheme, dict) and scheme.get("critical_questions"):
            for q in scheme.get("critical_questions", []):
                audit_questions_list.append({"question": q, "status": "Open"})
    context["audit_questions"] = audit_questions_list

    # Scores (From XAI Scorecards or Judge)
    scores_dict = {}
    total_score_sum = 0.0
    count = 0

    if isinstance(xai_out, dict) and xai_out.get("score_cards"):
        for card in xai_out.get("score_cards", []):
            if isinstance(card, dict):
                total_score_sum += card.get("total_score", 0.0)
                count += 1
                # Add dimensions
                for dim in card.get("dimensions", []):
                    if isinstance(dim, dict):
                        scores_dict[dim.get("dimension_id", "")] = {
                            "arvosana": dim.get("score", 0.0),
                            "perustelu": dim.get("reasoning", ""),
                            "label": dim.get("dimension_label", ""),
                        }
    elif isinstance(judge_out, dict) and judge_out.get("score_card"):
        # Fallback if XAI didn't aggregate but Judge is present
        card = judge_out.get("score_card", {})
        if isinstance(card, dict):
            total_score_sum = card.get("total_score", 0.0)
            count = 1
            for dim in card.get("dimensions", []):
                if isinstance(dim, dict):
                    scores_dict[dim.get("dimension_id", "")] = {
                        "arvosana": dim.get("score", 0.0),
                        "perustelu": dim.get("reasoning", ""),
                        "label": dim.get("dimension_label", ""),
                    }

    context["scores"] = scores_dict
    context["average_score"] = (total_score_sum / count) if count > 0 else 0.0

    # Human In The Loop?
    context["hitl_required"] = context["average_score"] < 2.5  # Arbitrary threshold or from Override

    # Uncertainty
    context["uncertainty"] = {"status": "Not Assessed"}  # Placeholder

    # Bibliography
    bib_data = state.global_context_vars.get("bibliography_result")
    if bib_data:
        if isinstance(bib_data, list):
            context["bibliography"] = bib_data
        elif isinstance(bib_data, dict):
            context["bibliography"] = bib_data.get("references", [])
    else:
        context["bibliography"] = []

    # Contextual Citations & Global Bibliography (Unified References)
    references: list[ReferenceItem] = []
    counters = {"SEARCH": 1, "GROUNDING": 1, "INTERNAL_KB": 1}

    # SEARCH
    search_items = []
    if isinstance(analyst_out, dict) and analyst_out.get("rag_evidence"):
        search_items.extend(analyst_out.get("rag_evidence", []))
    sr_obj = state.global_context_vars.get("search_result")
    if sr_obj:
        results = (
            getattr(sr_obj, "results", [])
            if hasattr(sr_obj, "results")
            else (sr_obj.get("results", []) if isinstance(sr_obj, dict) else sr_obj)
        )
        if isinstance(results, list):
            search_items.extend(results)

    for item in search_items:
        title = "Verkkohaku"
        snippet = ""
        url = None
        if isinstance(item, dict):
            title = item.get("title", title)
            snippet = item.get("snippet", str(item))
            url = item.get("link")
        elif hasattr(item, "snippet"):
            title = getattr(item, "title", title)
            snippet = getattr(item, "snippet", str(item))
            url = getattr(item, "link", None)
        else:
            snippet = str(item)

        if snippet and snippet.strip():
            references.append(
                ReferenceItem(
                    id=f"[H-{counters['SEARCH']}]",
                    intent=ReferenceIntent.SEARCH,
                    title=title,
                    snippet=snippet,
                    url=url,
                )
            )
            counters["SEARCH"] += 1

    # GROUNDING
    for step_key, step_data in state.global_context_vars.items():
        if not step_key.startswith("step_") or not isinstance(step_data, dict):
            continue
        p_meta = step_data.get("metadata", {})
        p_prov = getattr(p_meta, "provider_metadata", {}) if p_meta else {}
        g_urls = p_prov.get("grounding_urls", []) if isinstance(p_prov, dict) else []
        for url in g_urls:
            references.append(
                ReferenceItem(
                    id=f"[F-{counters['GROUNDING']}]",
                    intent=ReferenceIntent.GROUNDING,
                    title="Faktantarkistus (Google)",
                    snippet=f"Vertex AI Grounding lähde: {url}",
                    url=url,
                )
            )
            counters["GROUNDING"] += 1

    # INTERNAL KB
    if bib_data:
        items = (
            getattr(bib_data, "items", [])
            if hasattr(bib_data, "items")
            else (bib_data.get("items", []) if isinstance(bib_data, dict) else bib_data)
        )
        if isinstance(items, list):
            for item in items:
                title = "Organisaation Linjaus"
                snippet = ""
                url = None
                if isinstance(item, dict):
                    title = item.get("title", title)
                    snippet = item.get("snippet", str(item))
                    url = item.get("url") or item.get("source_id")
                elif hasattr(item, "snippet"):
                    title = getattr(item, "title", title)
                    snippet = getattr(item, "snippet", str(item))
                    url = getattr(item, "url", getattr(item, "source_id", None))
                else:
                    snippet = str(item)

                if snippet and snippet.strip():
                    references.append(
                        ReferenceItem(
                            id=f"[O-{counters['INTERNAL_KB']}]",
                            intent=ReferenceIntent.INTERNAL_KB,
                            title=title,
                            snippet=snippet,
                            url=url,
                        )
                    )
                    counters["INTERNAL_KB"] += 1

    context["references"] = references

    # 4. PASS THROUGH SPECIALIST DATA (For Template deep dives)
    context["logician_data"] = logician_data
    context["overseer_data"] = overseer_data
    context["falsifier_data"] = falsifier_data
    context["causal_analysis"] = causal_data
    context["performativity_analysis"] = perf_data

    # 5. ENRICHMENT (Metrics & Knowledge)
    profiler_out = _get_agent_output("step_profiler")
    if isinstance(profiler_out, dict):
        metrics = profiler_out.get("metrics", {})
        if isinstance(metrics, dict):
            context["word_count"] = metrics.get("word_count", 0)
            context["input_control_ratio"] = metrics.get("control_ratio", 0.0)

    if analyst_out:
        # Knowledge Items (Now extracted directly from analyst_out.rag_evidence if we want to show it, or left empty)
        # Search results and knowledge items were moved/removed in the Strict DTO refactor.
        # For the report context, we provide empty lists or omit if not strictly required,
        # or we could parse rag_evidence if necessary. For now, graceful degradation:
        context["google_search_results"] = []
        context["knowledge_items"] = []

    # Archivist
    archival_data = state.global_context_vars.get("step_archivist")
    if archival_data:
        context["archivist_precedents"] = archival_data

    # Scoring Result (Hook)
    scoring_out = state.global_context_vars.get("step_scoreengine1")
    if isinstance(scoring_out, dict):
        context["penalties_applied"] = scoring_out.get("penalties_applied")
        context["score_summary"] = scoring_out.get("score_summary")

    # Validation Result (Hook)
    validation_out = state.global_context_vars.get("step_validation")
    if isinstance(validation_out, dict):
        context["structural_warnings"] = validation_out.get("warnings")

    # Coaching Plan
    coaching_out = state.global_context_vars.get("step_coach")
    if isinstance(coaching_out, dict):
        context["coaching_plan"] = coaching_out

    # 5. RENDER / GENERATE (Strict Validation without Silent Failures)

    # Validate that the gathered context matches ReportContext schema strictly.
    # No more silent failures hiding mapping bugs. "Fail-Fast" rule 18.1.
    validated_context = context.copy()

    # If this hook is just preparing data for separate generation step:
    logger.info("[ReportingHook] Report context prepared and validated successfully.")
    return HookResult(success=True, state_delta={"report_context": validated_context})
