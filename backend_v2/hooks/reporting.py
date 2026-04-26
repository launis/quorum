"""Reporting hooks for generating XAI reports."""

import logging
from datetime import datetime
from pathlib import Path

from fastapi import status
from pydantic import ValidationError

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.dtos.report import (
    AuditQuestionItem,
    ReportContextDTO,
    ReportSynthesisDTO,
    ScoreItem,
)
from backend_v2.models.view.sdui import ReferenceIntent, ReferenceItem

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
        msg = "Strict Fail-Fast Enforced: Missing HookState in generate_report_hook."
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

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
    summary = "No Executive Summary available (XAI Role did not run or failed)."
    if gvars.step_xai and gvars.step_xai.executive_summary:
        summary = gvars.step_xai.executive_summary

    # Critical Findings (From Judge)
    critical_findings = []
    if gvars.step_judge and gvars.step_judge.critical_findings:
        critical_findings = gvars.step_judge.critical_findings

    # Pre-Morten Signals (From Performativity/Detector)
    pre_mortem_signals = []
    if perf_data and perf_data.weak_signals:
        pre_mortem_signals = perf_data.weak_signals

    # Ethical Issues (From Overseer)
    ethical_issues = []
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

    # We iterate the raw inputs because ReportSynthesisDTO securely drops matrix keys to prevent token explosion.
    for k, v in inputs.items():
        if isinstance(v, dict) and "normalized_score" in v and "justification" in v:
            try:
                matrix_dto = LightweightMatrixOutput.model_validate(v)
                scores_dict[k] = ScoreItem(
                    score=matrix_dto.normalized_score,
                    reasoning=matrix_dto.justification,
                    label=k,  # UI Localization handles dimension resolving
                )
                total_score_sum += matrix_dto.normalized_score
                count += 1
            except ValidationError:
                continue

    # Use the precise centralized average from score_summary if available
    if gvars.step_scoreengine1 and gvars.step_scoreengine1.score_summary:
        average_score = gvars.step_scoreengine1.score_summary.normalized_score
    else:
        average_score = (total_score_sum / count) if count > 0 else 0.0

    # Human In The Loop?
    hitl_required = average_score < 2.5

    # Uncertainty
    uncertainty = {"status": "NOT_ASSESSED"}

    # Bibliography
    bib_data = gvars.bibliography_result
    extracted_bibliography = []
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
                        title="SEARCH_RESULT_FALLBACK",
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
                            title=result_item.title or "SEARCH_RESULT_FALLBACK",
                            snippet=snippet,
                            url=result_item.link,
                        )
                    )
                    counters["SEARCH"] += 1

    # INTERNAL KB
    for bib_item in extracted_bibliography:
        title = bib_item.title or "KNOWLEDGE_BASE_FALLBACK"
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
        logician_data=logician_data.model_dump() if logician_data else None,
        overseer_data=overseer_data.model_dump() if overseer_data else None,
        falsifier_data=falsifier_data,
        causal_analysis=causal_data,
        performativity_analysis=perf_data.model_dump() if perf_data else None,
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
    return HookResult(success=True, state_delta={"report_context": report_context.model_dump(mode="json")})
