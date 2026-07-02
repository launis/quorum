"""Reporting hooks for generating XAI reports.

This module defines the post-execution hooks that aggregate agent outputs and generate
a comprehensive, structured ReportContextDTO for the reporting phase.
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import status
from pydantic import ValidationError

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.xai import VarianceValidationExtension
from backend_v2.models.dtos.report import (
    AuditQuestionItem,
    GlobalContextVarsDTO,
    MatrixObservabilityDTO,
    ReportContextDTO,
    ReportSynthesisDTO,
    ScoreItem,
)
from backend_v2.models.view.sdui import ReferenceIntent, ReferenceItem
from backend_v2.utils.scoring.variance_engine import calculate_mechanical_cognitive_variance

logger = logging.getLogger(__name__)


@hook_registry.register(name="generate_report")
def generate_report_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Workflow Data wrapper for generate_report.

    Post-execution hook that aggregates results from all agents (Judge, Overseer, Reporter)
    and renders a human-readable Markdown report using a Jinja2 template.

    Args:
        state: Current HookState to query.
        deps: Standard injection dependencies for service access.

    Returns:
        Structured execution state delta carrying the validated report context.

    Raises:
        AppException: If template missing or validation fails under strict RFC 7807 rules.
    """
    logger.debug("[ReportingHook] Running generate_report_hook...")

    if not state:
        msg_ff = "Strict Fail-Fast Enforced: Missing HookState in generate_report_hook."
        logger.error("[ReportingHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg_ff)
        raise AppException(
            message=msg_ff,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    # 2. GATHER CONTEXT
    inputs = state.inputs

    error_code: ErrorCodes | None = None
    status_code: int | None = None
    msg: str | None = None

    if not inputs:
        error_code = ErrorCodes.EMPTY_INPUT
        status_code = status.HTTP_400_BAD_REQUEST
        msg = "Missing or empty 'inputs' in data."
    elif not isinstance(inputs, dict):
        error_code = ErrorCodes.INVALID_OUTPUT_SCHEMA
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        msg = "Invalid 'inputs' in data. Expected dict."

    if error_code is not None and msg is not None and status_code is not None:
        logger.error("[ReportingHook] %s: %s", error_code.name, msg)
        raise AppException(
            message=msg,
            status_code=status_code,
            details={"error_code": error_code.value},
        )

    # 3. ENFORCE PARSING WITH DTO
    try:
        observability_inputs = MatrixObservabilityDTO.model_validate(inputs)
    except ValidationError as e:
        error_code_val = ErrorCodes.INVALID_OUTPUT_SCHEMA
        msg_val = f"Failed to strictly validate reporting observability inputs: {e}"
        logger.error("[ReportingHook] %s: %s", error_code_val.name, msg_val, exc_info=True)
        raise AppException(
            message=msg_val,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code_val.value},
        ) from e

    filtered_gvars: dict[str, Any] = {}
    for k, v in state.global_context_vars.items():
        if k in GlobalContextVarsDTO.model_fields:
            filtered_gvars[k] = v

    try:
        # Applying PEP 736 short-hand variable notation
        dto = ReportSynthesisDTO.model_validate({"inputs": observability_inputs, "global_context_vars": filtered_gvars})
    except ValidationError as e:
        logger.error("[ReportingHook] Validation failed: %s", e, exc_info=True)
        raise AppException(
            message="Report Context Validation Failed.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        ) from e

    generated_at = datetime.now().astimezone().strftime("%d.%m.%Y %H:%M")
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")

    gvars = dto.global_context_vars

    # Strictly read roles without fallbacks (Fail-Fast / Zero-Compromise)
    overseer_data = gvars.step_overseer.overseer_data if gvars.step_overseer else None
    logician_data = gvars.step_logician.logician_data if gvars.step_logician else None
    perf_data = gvars.step_detector.performativity_analysis if gvars.step_detector else None
    falsifier_data = gvars.step_panel.falsifier_data if gvars.step_panel else None
    causal_data = gvars.step_panel.causal_analysis if gvars.step_panel else None

    # Summary (From XAI)
    summary = "UI_REPORT_SUMMARY_NOT_AVAILABLE"
    if gvars.step_xai and gvars.step_xai.executive_summary:
        summary = gvars.step_xai.executive_summary

    # Critical Findings (From Judge)
    critical_findings: list[Any] = []
    if gvars.step_judge and gvars.step_judge.critical_findings:
        critical_findings = gvars.step_judge.critical_findings

    # Pre-Morten Signals (From Performativity/Detector)
    pre_mortem_signals: list[Any] = []
    if perf_data and perf_data.weak_signals:
        pre_mortem_signals = perf_data.weak_signals

    # Ethical Issues (From Overseer)
    ethical_issues: list[Any] = []
    if overseer_data and overseer_data.ethical_issues:
        ethical_issues = overseer_data.ethical_issues

    # Audit Questions (From Logician)
    audit_questions_list: list[AuditQuestionItem] = []
    if logician_data and logician_data.walton_scheme and logician_data.walton_scheme.critical_questions:
        for q in logician_data.walton_scheme.critical_questions:
            audit_questions_list.append(AuditQuestionItem(question=q, status="OPEN"))

    # Scores (V2 Phase 9 Zero-Compromise: Matrices are extracted natively)
    scores_dict: dict[str, ScoreItem] = {}
    total_score_sum = 0.0
    count = 0

    # Use strictly validated DTO instead of raw inputs to prevent duct tape exceptions
    for k, matrix_obs in dto.inputs.matrices.items():
        scores_dict[k] = ScoreItem(
            score=matrix_obs.normalized_score,
            reasoning=matrix_obs.justification,
            label=k,
        )
        total_score_sum += matrix_obs.normalized_score
        count += 1

    # Use the precise centralized average from score_summary (Fail-Fast enforces its presence or default 0.0)
    average_score = 0.0
    if gvars.step_scoreengine1 and gvars.step_scoreengine1.score_summary:
        average_score = gvars.step_scoreengine1.score_summary.normalized_score

    # Human In The Loop?
    hitl_required = average_score < 2.5

    # Uncertainty
    uncertainty = {"status": "NOT_ASSESSED"}

    # Bibliography
    bib_data = gvars.bibliography_result
    extracted_bibliography: list[Any] = []
    if bib_data:
        if isinstance(bib_data, list):
            for res in bib_data:
                extracted_bibliography.extend(res.references)
        else:
            extracted_bibliography.extend(bib_data.references)

    bibliography = [ref.model_dump() for ref in extracted_bibliography]

    # Contextual Citations & Global Bibliography (Unified References)
    references: list[ReferenceItem] = []
    counters = {"SEARCH": 1, "INTERNAL_KB": 1}

    # 1. RAG Evidence (list of strict strings)
    if gvars.step_analyst and gvars.step_analyst.rag_evidence:
        for evidence in gvars.step_analyst.rag_evidence:
            snippet = str(evidence).strip()
            if snippet:
                references.append(
                    ReferenceItem(
                        id=f"[H-{counters['SEARCH']}]",
                        intent=ReferenceIntent.SEARCH,
                        title="UI_SEARCH_RESULT_FALLBACK",
                        snippet=snippet,
                        url=None,
                    )
                )
                counters["SEARCH"] += 1

    # 2. Search Result Objects (Strict SearchResult)
    sr_obj = gvars.search_result
    if sr_obj:
        sr_list = sr_obj if isinstance(sr_obj, list) else [sr_obj]
        for sr in sr_list:
            for result_item in sr.results:
                snippet = result_item.snippet.strip() if result_item.snippet else ""
                if snippet:
                    references.append(
                        ReferenceItem(
                            id=f"[H-{counters['SEARCH']}]",
                            intent=ReferenceIntent.SEARCH,
                            title=result_item.title or "UI_SEARCH_RESULT_FALLBACK",
                            snippet=snippet,
                            url=result_item.link,
                        )
                    )
                    counters["SEARCH"] += 1

    # INTERNAL KB
    for bib_item in extracted_bibliography:
        title = bib_item.title or "UI_KNOWLEDGE_BASE_FALLBACK"
        snippet = bib_item.snippet or ""
        url = bib_item.url

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

    prof_metrics = gvars.step_profiler.metrics if gvars.step_profiler and gvars.step_profiler.metrics else None

    # Calculate Mechanical-Cognitive Variance & Alignment Verdict
    authenticity_score = None
    if gvars.step_detector and gvars.step_detector.raw_score is not None:
        authenticity_score = gvars.step_detector.raw_score

    performative_phrases_count = None
    if gvars.step_linguistics and gvars.step_linguistics.performative_patterns is not None:
        performative_phrases_count = len(gvars.step_linguistics.performative_patterns)

    if authenticity_score is None or performative_phrases_count is None:
        msg = (
            "Strict Fail-Fast Enforced: 'variance_validation' generation failed because authenticity_score "
            f"({authenticity_score}) or performative_phrases_count ({performative_phrases_count}) is missing."
        )
        logger.error("[ReportingHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    variance_res = calculate_mechanical_cognitive_variance(
        llm_authenticity_score=authenticity_score,
        performative_phrases_count=performative_phrases_count,
    )
    variance_ext = VarianceValidationExtension(
        mechanical_metric_ref=str(variance_res["mechanical_metric_ref"]),
        cognitive_metric_ref=str(variance_res["cognitive_metric_ref"]),
        variance_score=float(variance_res["variance_score"]),
        alignment_verdict=str(variance_res["alignment_verdict"]),
    )

    # Assemble ReportContextDTO (No Naked Dicts!)
    report_context = ReportContextDTO(
        inputs=dto.inputs,
        generated_at=generated_at,
        timestamp=timestamp,
        summary=summary,
        critical_findings=critical_findings,
        pre_mortem_signals=pre_mortem_signals,
        ethical_issues=ethical_issues,
        audit_questions=audit_questions_list,
        scores=scores_dict,
        average_score=average_score,
        hitl_required=hitl_required,
        uncertainty=uncertainty,
        bibliography=bibliography,
        references=references,
        output_extensions=[variance_ext],
        logician_data=logician_data,
        overseer_data=overseer_data,
        falsifier_data=falsifier_data,
        causal_analysis=causal_data,
        performativity_analysis=perf_data,
        word_count=prof_metrics.word_count if prof_metrics else None,
        input_control_ratio=prof_metrics.control_ratio if prof_metrics else None,
        google_search_results=[],
        knowledge_items=[],
        archivist_precedents=gvars.step_archivist if gvars.step_archivist else None,
        penalties_applied=gvars.step_scoreengine1.penalties_applied if gvars.step_scoreengine1 else None,
        score_summary=gvars.step_scoreengine1.score_summary if gvars.step_scoreengine1 else None,
        structural_warnings=gvars.step_validation.warnings if gvars.step_validation else None,
        coaching_plan=gvars.step_coach if gvars.step_coach else None,
    )

    logger.info("[ReportingHook] Report context prepared and validated successfully.")
    return HookResult(
        success=True,
        state_delta={"report_context": report_context.model_dump(mode="json")},
    )
