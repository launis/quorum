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

    # Fallback to Panel if direct roles are missing
    overseer_data = gvars.step_overseer.overseer_data if gvars.step_overseer else None
    if not overseer_data and gvars.step_panel:
        overseer_data = gvars.step_panel.overseer_data

    logician_data = gvars.step_logician.logician_data if gvars.step_logician else None
    if not logician_data and gvars.step_panel:
        logician_data = gvars.step_panel.logician_data

    perf_data = gvars.step_detector.performativity_analysis if gvars.step_detector else None
    if not perf_data and gvars.step_panel:
        perf_data = gvars.step_panel.performativity_analysis

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
                    "arvosana": dim.score,
                    "perustelu": dim.reasoning,
                    "label": dim.dimension_label,
                }
    elif gvars.step_judge and gvars.step_judge.score_card:
        card = gvars.step_judge.score_card
        total_score_sum = card.total_score
        count = 1
        for dim in card.dimensions:
            scores_dict[dim.dimension_id] = {
                "arvosana": dim.score,
                "perustelu": dim.reasoning,
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

    search_items = []
    if gvars.step_analyst and gvars.step_analyst.rag_evidence:
        search_items.extend(gvars.step_analyst.rag_evidence)

    sr_obj = gvars.search_result
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

    # EPIC 6: Console Koostaja (XAI Extensions logging)
    all_grouped_ext: dict[str, list[str]] = {}
    for step_key, step_data in state.global_context_vars.items():
        if not step_key.startswith("step_") or not isinstance(step_data, dict):
            continue

        for k, v in step_data.items():
            if not isinstance(v, dict):
                continue

            eval_notes = v.get("evaluation_notes", "")
            raw_justification = str(v.get("step_3_logical_friction", eval_notes) or "")
            if raw_justification:
                all_grouped_ext.setdefault("justification", []).append(f"[{k}] {raw_justification[:100]}...")

            raw_falsification = v.get("extension_falsification", v.get("step_2_falsification"))
            if raw_falsification:
                all_grouped_ext.setdefault("falsification", []).append(f"[{k}] {str(raw_falsification)[:100]}...")

            raw_theory_link = v.get("extension_theory_link")
            if raw_theory_link:
                all_grouped_ext.setdefault("theory_link", []).append(f"[{k}] {str(raw_theory_link)[:100]}...")

            raw_risk_flag = v.get("extension_risk_flag")
            if raw_risk_flag is not None:
                all_grouped_ext.setdefault("risk_flag", []).append(f"[{k}] {raw_risk_flag}")

            coaching = v.get("extension_coaching")
            if coaching:
                all_grouped_ext.setdefault("coaching", []).append(f"[{k}] {str(coaching)[:100]}...")

            missing_context = v.get("extension_missing_context")
            if missing_context:
                all_grouped_ext.setdefault("missing_context", []).append(f"[{k}] {str(missing_context)[:100]}...")

            remediation_steps = v.get("extension_remediation_steps")
            if remediation_steps:
                all_grouped_ext.setdefault("remediation_steps", []).append(f"[{k}] {str(remediation_steps)[:100]}...")

            confidence = v.get("extension_confidence")
            if confidence is not None:
                all_grouped_ext.setdefault("confidence", []).append(f"[{k}] {confidence}")

    if all_grouped_ext:
        logger.info("\n" + "=" * 60)
        logger.info("  XAI OUTPUT EXTENSIONS (CONSOLE RENDER)")
        logger.info("=" * 60)
        for ext_key, items in all_grouped_ext.items():
            logger.info(f"[{ext_key.upper()}] ({len(items)} items)")
            for _i, itm in enumerate(items[:3]):
                logger.info(f"  - {itm}")
            if len(items) > 3:
                logger.info(f"  ... (+ {len(items) - 3} more)")
        logger.info("=" * 60 + "\n")

    logger.info("[ReportingHook] Report context prepared and validated successfully.")
    return HookResult(success=True, state_delta={"report_context": context})
