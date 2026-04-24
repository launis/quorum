"""Reporting hooks for generating XAI reports."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import status
from pydantic import ValidationError

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.report import ReportSynthesisDTO
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
        state: Current HookState.

    Returns:
        HookResult: Updated data with 'report_context'.

    Raises:
        AppException: If template missing or validation fails.
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
        logger.error("[ReportingHook] %s: %s", error_code.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": error_code})

    # 2. GATHER CONTEXT
    inputs = state.inputs

    if not inputs or not isinstance(inputs, dict):
        error_code = ErrorCodes.EMPTY_INPUT if inputs is None else ErrorCodes.INVALID_OUTPUT_SCHEMA
        msg = "Missing or invalid 'inputs' in data. Expected dict."
        status_code = status.HTTP_400_BAD_REQUEST if inputs is None else status.HTTP_500_INTERNAL_SERVER_ERROR
        logger.error("[ReportingHook] %s: %s", error_code.name, msg)
        raise AppException(
            message=msg,
            status_code=status_code,
            details={"error_code": error_code},
        )

    # 3. ENFORCE PARSING WITH DTO
    try:
        dto = ReportSynthesisDTO.model_validate({"inputs": inputs, "global_context_vars": state.global_context_vars})
    except ValidationError as e:
        logger.error("[ReportingHook] Validation failed: %s", e)
        raise AppException(
            message="Report Context Validation Failed.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.VALIDATION_FAILED, "errors": e.errors()},
        ) from e

    context: dict[str, Any] = {}
    context["inputs"] = dto.inputs
    context["generated_at"] = datetime.now().astimezone().strftime("%d.%m.%Y %H:%M")
    context["timestamp"] = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")

    gvars = dto.global_context_vars

    # Strictly read roles without fallbacks (Fail-Fast / Zero-Compromise)
    overseer_data = gvars.step_overseer.overseer_data if gvars.step_overseer else None
    logician_data = gvars.step_logician.logician_data if gvars.step_logician else None
    perf_data = gvars.step_detector.performativity_analysis if gvars.step_detector else None
    falsifier_data = gvars.step_panel.falsifier_data if gvars.step_panel else None
    causal_data = gvars.step_panel.causal_analysis if gvars.step_panel else None

    # Summary (From XAI)
    if gvars.step_xai and gvars.step_xai.executive_summary:
        context["summary"] = gvars.step_xai.executive_summary
    else:
        context["summary"] = "No Executive Summary available (XAI Role did not run or failed)."

    # Critical Findings (From Judge)
    if gvars.step_judge and gvars.step_judge.critical_findings:
        context["critical_findings"] = gvars.step_judge.critical_findings
    else:
        context["critical_findings"] = []

    # Pre-Morten Signals (From Performativity/Detector)
    if perf_data and perf_data.weak_signals:
        context["pre_mortem_signals"] = perf_data.weak_signals
    else:
        context["pre_mortem_signals"] = []

    # Ethical Issues (From Overseer)
    if overseer_data and overseer_data.ethical_issues:
        context["ethical_issues"] = overseer_data.ethical_issues
    else:
        context["ethical_issues"] = []

    # Audit Questions (From Logician)
    audit_questions_list = []
    if logician_data and logician_data.walton_scheme and logician_data.walton_scheme.critical_questions:
        for q in logician_data.walton_scheme.critical_questions:
            audit_questions_list.append({"question": q, "status": "Open"})
    context["audit_questions"] = audit_questions_list

    # Scores (From XAI Scorecards or Judge)
    scores_dict = {}
    total_score_sum = 0.0
    count = 0

    if gvars.step_xai and gvars.step_xai.score_cards:
        for card in gvars.step_xai.score_cards:
            total_score_sum += card.total_score
            count += 1
            for dim in card.dimensions:
                scores_dict[dim.dimension_id] = {
                    "score": dim.score,
                    "reasoning": dim.reasoning,
                    "label": dim.dimension_label,
                }
    elif gvars.step_judge and gvars.step_judge.score_card:
        card = gvars.step_judge.score_card
        total_score_sum = card.total_score
        count = 1
        for dim in card.dimensions:
            scores_dict[dim.dimension_id] = {
                "score": dim.score,
                "reasoning": dim.reasoning,
                "label": dim.dimension_label,
            }

    context["scores"] = scores_dict
    context["average_score"] = (total_score_sum / count) if count > 0 else 0.0

    # Human In The Loop?
    context["hitl_required"] = context["average_score"] < 2.5

    # Uncertainty
    context["uncertainty"] = {"status": "Not Assessed"}

    # Bibliography
    bib_data = gvars.bibliography_result
    extracted_bibliography = []
    if bib_data:
        if isinstance(bib_data, list):
            for res in bib_data:
                extracted_bibliography.extend(res.references)
        else:
            extracted_bibliography.extend(bib_data.references)

    context["bibliography"] = [ref.model_dump() for ref in extracted_bibliography]

    # Contextual Citations & Global Bibliography (Unified References)
    references: list[ReferenceItem] = []
    counters = {"SEARCH": 1, "INTERNAL_KB": 1}

    search_items: list[Any] = []
    if gvars.step_analyst and gvars.step_analyst.rag_evidence:
        search_items.extend(gvars.step_analyst.rag_evidence)

    sr_obj = gvars.search_result
    if sr_obj:
        if isinstance(sr_obj, list):
            for sr in sr_obj:
                search_items.extend(sr.results)
        else:
            search_items.extend(sr_obj.results)

    for item in search_items:
        title = "Web Search"
        snippet = ""
        url = None

        # item could be a dict if rag_evidence is raw strings, but SearchResult models have strict typing.
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

    # INTERNAL KB
    for bib_item in extracted_bibliography:
        title = bib_item.title or "Internal Knowledge Base"
        snippet = bib_item.snippet or ""
        url = bib_item.url or getattr(bib_item, "source_id", None)

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
    context["logician_data"] = logician_data.model_dump() if logician_data else None
    context["overseer_data"] = overseer_data.model_dump() if overseer_data else None
    context["falsifier_data"] = falsifier_data
    context["causal_analysis"] = causal_data
    context["performativity_analysis"] = perf_data.model_dump() if perf_data else None

    # 5. ENRICHMENT (Metrics & Knowledge)
    if gvars.step_profiler and gvars.step_profiler.metrics:
        context["word_count"] = gvars.step_profiler.metrics.word_count
        context["input_control_ratio"] = gvars.step_profiler.metrics.control_ratio

    if gvars.step_analyst:
        context["google_search_results"] = []
        context["knowledge_items"] = []

    # Archivist
    if gvars.step_archivist:
        context["archivist_precedents"] = gvars.step_archivist

    # Scoring Result (Hook)
    if gvars.step_scoreengine1:
        context["penalties_applied"] = gvars.step_scoreengine1.penalties_applied
        context["score_summary"] = gvars.step_scoreengine1.score_summary

    # Validation Result (Hook)
    if gvars.step_validation:
        context["structural_warnings"] = gvars.step_validation.warnings

    # Coaching Plan
    if gvars.step_coach:
        context["coaching_plan"] = gvars.step_coach

    logger.info("[ReportingHook] Report context prepared and validated successfully.")
    return HookResult(success=True, state_delta={"report_context": context})
