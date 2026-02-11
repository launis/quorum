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
        WorkflowState: State with newly created ScoringResult in context_variables.

    """
    target_steps = []
    if state.step_judge and state.step_judge.pisteet:
        target_steps.append(state.step_judge)

    # Check for cognitive judge (optional field)
    if hasattr(state, "step_judge_cognitive") and state.step_judge_cognitive:
        if hasattr(state.step_judge_cognitive, "pisteet") and state.step_judge_cognitive.pisteet:
            target_steps.append(state.step_judge_cognitive)

    if not target_steps:
        logger.warning("   [ScoringHook] No scores to calculate (checked step_judge and step_judge_cognitive).")
        return state

    scoring_result = None

    try:
        from backend.models.domain import ScoringResult

        total_global: float = 0.0
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
                    # Note: We are calculating here based on rules, but we are NOT modifying the immutable JudgeOutput in place.
                    # We are effectively simulating the penalty for the final average calculation.
                    # If we wanted to modify the JudgeOutput itself, we would need to replace it in state via functional update.
                    # For now, we just output the *Final Penalized Score* into ScoringResult.
                    
                    val = comp.arvosana
                    
                    if security_threat:
                        val = 1
                    elif logical_failure and val > 2:
                        val = 2

                    if val is not None:
                        total_global += val
                        count_global += 1

        # Calculate average
        average = (total_global / count_global) if count_global > 0 else 0.0

        summary = f"Total Score: {total_global}/{count_global * 4} (Avg: {average:.2f})"
        if penalties_applied:
            summary += f" | Penalties: {', '.join(penalties_applied)}"

        logger.debug(f"[ScoringHook] {summary}")

        # specific strict model
        scoring_result = ScoringResult(
            total_score=total_global,
            calculated_average=average,
            score_summary=summary,
            penalties_applied=penalties_applied
        )

    except Exception as e:
        logger.error(f"[ScoringHook] Calculation failed: {e}")
        return state
        
    # Store metadata
    new_context = state.context_variables.copy()
    new_context["scoring_result"] = scoring_result
    
    # Legacy support
    new_context["score_summary"] = scoring_result.score_summary
    new_context["calculated_average"] = scoring_result.calculated_average
    new_context["penalties_applied"] = scoring_result.penalties_applied

    return state.model_copy(update={"context_variables": new_context})


def enforce_passivity_penalty(state: WorkflowState, step_id: str = "step_judge") -> WorkflowState:
    """HOOK: enforce_passivity_penalty.

    Strictly enforces a 'Passiveness Cutter' penalty:
    If any dimension is rated at the absolute minimum (Level 1 / Passenger),
    the TOTAL score is capped at the lower third of the scale (Level 2 equivalent).

    STRICT VALIDATION:
    - Requires 'scale_min' and 'scale_max' in the step result.
    - Raises ValueError if missing (No defaults permitted).
    
    Compatible with both Pydantic models and Dicts (via generic attribute access).

    Args:
        state (WorkflowState): Current workflow state.
        step_id (str): The step ID to audit (default: 'step_judge').

    Returns:
        WorkflowState: Updated state with capped score if penalty applies.
    """
    # 1. Retrieve Result
    result = state.context_variables.get(step_id)
    if not result:
        logger.warning(f"[ScoringHook] Step '{step_id}' not found in context. Skipping penalty check.")
        return state

    # Helper to get value from dict or object
    def get_val(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    # 2. Strict Scale Validation (No Defaults)
    s_min_val = get_val(result, "scale_min")
    s_max_val = get_val(result, "scale_max")

    if s_min_val is None or s_max_val is None:
        msg = f"CRITICAL: Scaling parameters (scale_min, scale_max) missing from '{step_id}' output."
        logger.error(f"[ScoringHook] {msg}")
        raise ValueError(msg)

    try:
        s_min = float(s_min_val)
        s_max = float(s_max_val)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid scale values in '{step_id}': {e}") from e

    # 3. Analyze Dimensions
    dimensions = get_val(result, "dimensions", [])
    # Accessing list from model or dict
    if not isinstance(dimensions, list):
         # If dimensions is None or empty
         dimensions = []

    passenger_found = False
    for dim in dimensions:
        # Check if score matches absolute minimum (Sensitivity: Float comparison)
        score = get_val(dim, "score")
        if score is not None and abs(float(score) - s_min) < 0.01:
            passenger_found = True
            break

    # 4. Apply Penalty
    if passenger_found:
        scale_range = s_max - s_min
        # Cap = Min + 1/3 of range
        penalty_cap = s_min + (scale_range / 3.0)
        
        current_total = float(get_val(result, "total_score", 0))
        
        if current_total > penalty_cap:
            logger.warning(
                f"[ScoringHook] 📉 Enforcing Passiveness Penalty on {step_id}. "
                f"Passenger rating detected. Score capped: {current_total} -> {penalty_cap:.2f}"
            )
            
            # Apply Cap
            
            # Check if Pydantic Model (Frozen)
            if hasattr(result, "model_copy"):
                # Functional Update
                findings = list(get_val(result, "critical_findings", []))
                findings.append(f"PASSIVENESS_CUTTER_ACTIVATED: Score capped at {penalty_cap:.2f} due to Level 1 rating.")
                
                # We need to construct the update dict carefully
                # Pydantic models from domain.py (e.g. JudgeOutput) might not have 'critical_findings' field if it wasn't defined.
                # Let's check the schema logic. If generic 'total_score' field exists.
                
                update_dict = {"total_score": penalty_cap}
                
                # Only update findings if the field exists on the model
                if hasattr(result, "critical_findings"):
                     update_dict["critical_findings"] = findings
                
                new_result = result.model_copy(update=update_dict)
                
            else:
                # Dict Mutation (Legacy)
                result["total_score"] = penalty_cap
                findings = result.get("critical_findings", [])
                findings.append(f"PASSIVENESS_CUTTER_ACTIVATED: Score capped at {penalty_cap:.2f} due to Level 1 rating.")
                result["critical_findings"] = findings
                new_result = result
            
            # Update Snapshot in Context
            new_context = state.context_variables.copy()
            new_context[step_id] = new_result
            return state.model_copy(update={"context_variables": new_context})

    return state
