"""Reporting hooks for generating XAI reports."""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from jinja2 import Environment, FileSystemLoader

from backend.exceptions import AppException, ErrorCodes
from backend.models.domain import (
    ReportContext,
    ReportResult,
    ScoringResult,
    ValidationResult,
)
from backend.models.domain.analyst import AnalystOutput
from backend.models.domain.judge import JudgeOutput
from backend.models.domain.overseer import OverseerOutput
from backend.models.domain.performativity import PerformativityOutput
from backend.models.domain.logician import LogicianOutput
from backend.models.domain.falsifier import FalsifierOutput
from backend.models.domain.causal import CausalOutput
from backend.models.domain.xai import XAIOutput
from backend.models.domain.profiler import ProfilerOutput
from backend.models.domain.archivist import ArchivistOutput
from backend.models.domain.coach import CoachingPlan, BibliographyResult
from backend.models.dtos.pdf_context import ReportContext
from backend.models.state import WorkflowState
from backend.models.domain.inputs import WorkflowInputs
from backend.services.localization import LocalizationService
from backend.utils.pydantic_utils import inflate
from backend.settings import get_settings

logger = logging.getLogger(__name__)


def generate_report(state: WorkflowState) -> WorkflowState:
    """HOOK: generate_report.

    Post-execution hook that aggregates results from all agents (Judge, Overseer, Reporter)
    and renders a human-readable Markdown report using a Jinja2 template.

    Outputs:
        Populates 'step_xai.xai_report_formatted' with the rendered Markdown.

    Args:
        state (WorkflowState): Current workflow state containing all agent outputs.

    Returns:
        WorkflowState: State updated with 'report_url' or 'report_status'.

    Raises:
        AppException: If template missing or generation fails.
    """
    logger.debug("[ReportingHook] Running generate_report...")

    # STRICT Enforce: State must be WorkflowState object
    if isinstance(state, dict):
        raise AppException(
            message="Reporting Hook received dict state. Strict Pydantic Enforcement Violation.",
            status_code=500,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA}
        )

    settings = get_settings()

    # 1. TEMPLATE VALIDATION (Fail Fast)
    template_dir = Path("backend/templates")
    # Adjust path relative to CWD
    if not template_dir.exists():
        template_dir = Path("c:/src/quorum/backend/templates") # Absolute fallback
    
    if not template_dir.exists():
         error_code = ErrorCodes.CONFIGURATION_ERROR
         msg = f"Template directory not found at {template_dir}."
         logger.error(f"[ReportingHook] {error_code.name}: {msg}")
         raise AppException(message=msg, status_code=500, details={"error_code": error_code})

    # 2. GATHER CONTEXT (Strict Inflation)
    context: Dict[str, Any] = {}

    # Inputs (Strict WorkflowInputs)
    input_data = state.context_variables.get("inputs")
    inputs = state.get_context("inputs", WorkflowInputs)
    
    if not inputs:
        # Distinguish Missing vs Invalid
        if input_data is None:
             error_code = ErrorCodes.EMPTY_INPUT
             msg = "Missing 'inputs' in context_variables."
             status_code = 400
        else:
             error_code = ErrorCodes.INVALID_OUTPUT_SCHEMA
             msg = f"Context 'inputs' is {type(input_data)}, expected WorkflowInputs."
             status_code = 500
        
        logger.error(f"[ReportingHook] {error_code.name}: {msg}")
        raise AppException(message=msg, status_code=status_code, details={"error_code": error_code})

    context["inputs"] = inputs
    context["generated_at"] = datetime.now().strftime("%d.%m.%Y %H:%M")
    context["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Helper to inflate safely
    def _get_agent_output(key: str, model_cls: Any) -> Any:
        data = state.context_variables.get(key)
        if data:
            return inflate(data, model_cls)
        return None

    # Inflate all potential agent outputs
    xai_out = _get_agent_output("step_xai", XAIOutput)
    judge_out = _get_agent_output("step_judge", JudgeOutput)
    overseer_out = _get_agent_output("step_overseer", OverseerOutput)
    logician_out = _get_agent_output("step_logician", LogicianOutput)
    performativity_out = _get_agent_output("step_detector", PerformativityOutput) # Check key name!
    
    # 3. MAP DATA TO REPORT CONTEXT
    
    # Summary (From XAI)
    if xai_out:
        context["summary"] = xai_out.executive_summary
    else:
        context["summary"] = "No Executive Summary available (XAI Agent did not run or failed)."

    # Critical Findings (From Judge)
    if judge_out and judge_out.critical_findings:
         context["critical_findings"] = judge_out.critical_findings
    else:
         context["critical_findings"] = []

    # Pre-Morten Signals (From Performativity/Detector)
    if performativity_out and performativity_out.performativity_analysis:
        context["pre_mortem_signals"] = performativity_out.performativity_analysis.pre_mortem_analysis.weak_signals
    else:
        context["pre_mortem_signals"] = []

    # Ethical Issues (From Overseer)
    ethical_issues_list = []
    if overseer_out and overseer_out.overseer_data:
        for issue in overseer_out.overseer_data.ethical_issues:
            # Convert model to dict for ReportContext
            ethical_issues_list.append(issue.model_dump())
    context["ethical_issues"] = ethical_issues_list

    # Audit Questions (From Logician)
    audit_questions_list = []
    if logician_out and logician_out.logician_data and logician_out.logician_data.walton_scheme:
        for q in logician_out.logician_data.walton_scheme.critical_questions:
             audit_questions_list.append({"question": q, "status": "Open"})
    context["audit_questions"] = audit_questions_list

    # Scores (From XAI Scorecards or Judge)
    scores_dict = {}
    total_score_sum = 0.0
    count = 0
    
    if xai_out and xai_out.score_cards:
        for card in xai_out.score_cards:
            total_score_sum += card.total_score
            count += 1
            # Add dimensions
            for dim in card.dimensions:
                scores_dict[dim.dimension_id] = {
                    "arvosana": dim.score,
                    "perustelu": dim.reasoning,
                    "label": dim.dimension_label
                }
    elif judge_out and judge_out.score_card:
        # Fallback if XAI didn't aggregate but Judge is present
        total_score_sum = judge_out.score_card.total_score
        count = 1
        for dim in judge_out.score_card.dimensions:
            scores_dict[dim.dimension_id] = {
                "arvosana": dim.score,
                "perustelu": dim.reasoning,
                "label": dim.dimension_label
            }

    context["scores"] = scores_dict
    context["average_score"] = (total_score_sum / count) if count > 0 else 0.0

    # Human In The Loop?
    context["hitl_required"] = context["average_score"] < 2.5 # Arbitrary threshold or from Override

    # Uncertainty
    context["uncertainty"] = {"status": "Not Assessed"} # Placeholder

    # Bibliography
    bib_data = state.context_variables.get("bibliography_result")
    if bib_data:
        # It might be a list or a BibliographyResult object
        if isinstance(bib_data, list):
             context["bibliography"] = bib_data
        else:
             # Try inflating
             bib_obj = inflate(bib_data, BibliographyResult)
             if bib_obj:
                 context["bibliography"] = bib_obj.references
             else:
                 context["bibliography"] = []
    else:
        context["bibliography"] = []


    # 4. PASS THROUGH SPECIALIST DATA (For Template deep dives)
    context["logician_data"] = logician_out.logician_data if logician_out else None
    context["overseer_data"] = overseer_out.overseer_data if overseer_out else None
    context["falsifier_data"] = None # Add Falsifier extraction if available
    context["causal_analysis"] = None # Add Causal extraction if available
    context["performativity_analysis"] = performativity_out.performativity_analysis if performativity_out else None
    
    # 5. ENRICHMENT (Metrics & Knowledge)
    profiler_out = _get_agent_output("step_profiler", ProfilerOutput)
    if profiler_out:
        # Assuming ProfilerOutput has metrics
        metrics = getattr(profiler_out, "metrics", None)
        if metrics:
            # metrics might be a dict (DTO) or object (Domain). Handle both.
            if isinstance(metrics, dict):
                 context["word_count"] = metrics.get("word_count", 0)
                 context["input_control_ratio"] = metrics.get("control_ratio", 0.0)
            else:
                 context["word_count"] = getattr(metrics, "word_count", 0)
                 context["input_control_ratio"] = getattr(metrics, "control_ratio", 0.0)
            
    analyst_out = _get_agent_output("step_analyst", AnalystOutput)
    if analyst_out:
        # Knowledge Items (Now extracted directly from analyst_out.rag_evidence if we want to show it, or left empty)
        # Search results and knowledge items were moved/removed in the Strict DTO refactor. 
        # For the report context, we provide empty lists or omit if not strictly required, 
        # or we could parse rag_evidence if necessary. For now, graceful degradation:
        context["google_search_results"] = []
        context["knowledge_items"] = []

    # Archivist
    archivist_out = _get_agent_output("step_archivist", ArchivistOutput)
    if archivist_out:
        context["archivist_precedents"] = archivist_out # Pass the whole object or specific field
    
    # Scoring Result (Hook)
    scoring_res = _get_agent_output("scoring_result", ScoringResult)
    if scoring_res:
        context["penalties_applied"] = scoring_res.penalties_applied
        context["score_summary"] = scoring_res.score_summary
    
    # Validation Result (Hook)
    validation_res = _get_agent_output("structure_validation", ValidationResult)
    if validation_res:
        context["structural_warnings"] = validation_res.warnings

    # Coaching Plan
    coach_out = _get_agent_output("step_coach", CoachingPlan)
    if coach_out:
         context["coaching_plan"] = coach_out.model_dump()

    
    # 5. RENDER / GENERATE (Strict Validation)
    try:
        # Validate that the gathered context matches ReportContext schema
        report_model = ReportContext(**context)
        # We dump it back to dict for the template
        validated_context = report_model.model_dump()
    except Exception as e:
        error_code = ErrorCodes.REPORT_GENERATION_FAILED
        msg = f"ReportContext Validation Failed: {e}"
        logger.error(f"[ReportingHook] {error_code.name}: {msg}")
        raise AppException(message=msg, status_code=500, details={"error_code": error_code}) from e

    # If this hook is just preparing data for separate generation step:
    new_context = state.context_variables.copy()
    new_context["report_context"] = validated_context 
    
    logger.info("[ReportingHook] Report context prepared and validated successfully.")
    return state.model_copy(update={"context_variables": new_context})
