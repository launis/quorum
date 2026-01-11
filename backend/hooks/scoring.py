"""Scoring hooks for applying penalties and calculating averages."""

import logging

from backend.models.state import WorkflowState

logger = logging.getLogger(__name__)


def apply_scoring_logic(state: WorkflowState) -> WorkflowState:
    """HOOK: apply_scoring_logic.

    Applies deterministic penalties based on Guard (Security) and Falsifier (Logical) findings,
    then calculates final score averages.

    Rules:
    1. Security Threat -> All scores capped at 1.
    2. Post-Hoc Rationalization -> All scores capped at 2.

    Args:
        state (WorkflowState): Current state containing Judge, Guard, and Falsifier outputs.

    Returns:
        WorkflowState: State with penalty-adjusted scores and calculated averages in 'aux_data'.

    """
    target_steps = []
    if state.step_judge and state.step_judge.pisteet:
        target_steps.append(state.step_judge)

    if state.step_judge_cognitive and state.step_judge_cognitive.pisteet:
        target_steps.append(state.step_judge_cognitive)

    if not target_steps:
        logger.warning("   [ScoringHook] No scores to calculate (checked step_judge and step_judge_cognitive).")
        return state

    try:
        total_global = 0
        count_global = 0
        penalties_applied = []

        # --- DETERMINISTIC RULE ENFORCEMENT & CALC ---
        # Rule 1: Security Threat (Guard) -> Auto Fail (1/4)
        security_threat = False
        if state.step_guard and state.step_guard.security_check and state.step_guard.security_check.uhka_havaittu:
            security_threat = True
            penalties_applied.append("Security Threat (Score capped at 1)")

        # Rule 2: Logical Failures (Falsifier) -> Max Score 2/4
        logical_failure = False
        if not security_threat and state.step_falsifier:
            audit = getattr(state.step_falsifier, "paattelyketjun_uskollisuus_auditointi", None)
            if audit and audit.onko_post_hoc_rationalisointia:
                logical_failure = True
                penalties_applied.append("Logical Fallacies (Score capped at 2)")

        # Apply to ALL found judge outputs
        for judge_output in target_steps:
            p = judge_output.pisteet

            for comp in [p.analyysi, p.arviointi, p.synteesi]:
                if comp:
                    if security_threat:
                        comp.arvosana = 1
                        comp.perustelu += " [AUTOMATIC PENALTY: Security Threat Detected]"
                    elif logical_failure and comp.arvosana > 2:
                        comp.arvosana = 2
                        comp.perustelu += " [AUTOMATIC PENALTY: Logical Fallacies Detected]"

                    if comp.arvosana is not None:
                        total_global += comp.arvosana
                        count_global += 1

        # Calculate average
        average = (total_global / count_global) if count_global > 0 else 0.0

        summary = f"Total Score: {total_global}/{count_global * 4} (Avg: {average:.2f})"
        if penalties_applied:
            summary += f" | Penalties: {', '.join(penalties_applied)}"

        logger.info(f"[ScoringHook] {summary}")

        # Store metadata
        state.aux_data["score_summary"] = summary
        state.aux_data["calculated_average"] = average
        state.aux_data["penalties_applied"] = penalties_applied

    except Exception as e:
        logger.error(f"[ScoringHook] Calculation failed: {e}")

    return state
