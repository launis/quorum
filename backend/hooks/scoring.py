import logging
from backend.models.state import WorkflowState

logger = logging.getLogger(__name__)

def apply_scoring_logic(state: WorkflowState) -> WorkflowState:
    """
    HOOK: apply_scoring_logic
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
    if not state.step_judge or not state.step_judge.pisteet:
        logger.warning("   [ScoringHook] No scores to calculate.")
        return state
        
    try:
        p = state.step_judge.pisteet
        
        # --- DETERMINISTIC RULE ENFORCEMENT ---
        penalties_applied = []
        
        # Rule 1: Security Threat (Guard) -> Auto Fail (1/4)
        if state.step_guard and state.step_guard.security_check and state.step_guard.security_check.uhka_havaittu:
            logger.warning("[ScoringHook] Security Threat detected by Guard! Capping scores to 1.")
            for comp in [p.analyysi, p.arviointi, p.synteesi]:
                if comp: 
                    comp.arvosana = 1
                    comp.perustelu += " [AUTOMATIC PENALTY: Security Threat Detected]"
            penalties_applied.append("Security Threat (Score capped at 1)")

        # Rule 2: Logical Failures (Falsifier) -> Max Score 2/4
        # Check if there are critical logical errors (needs inspection of Falsifier schema/output)
        elif state.step_falsifier:
                audit = getattr(state.step_falsifier, 'paattelyketjun_uskollisuus_auditointi', None)
                if audit and audit.onko_post_hoc_rationalisointia:
                    logger.warning("[ScoringHook] Post-Hoc Rationalization detected! Capping scores to 2.")
                    for comp in [p.analyysi, p.arviointi, p.synteesi]:
                        if comp and comp.arvosana > 2:
                            comp.arvosana = 2
                            comp.perustelu += " [AUTOMATIC PENALTY: Logical Fallacies Detected]"
                    penalties_applied.append("Logical Fallacies (Score capped at 2)")
        
        # --- End Rules ---

        total = 0
        count = 0
        
        # Check each component dynamically
        for comp in [p.analyysi, p.arviointi, p.synteesi]:
            if comp and comp.arvosana is not None:
                total += comp.arvosana
                count += 1
        
        # Calculate average
        average = (total / count) if count > 0 else 0.0
        
        summary = f"Total Score: {total}/{count*4} (Avg: {average:.2f})"
        if penalties_applied:
            summary += f" | Penalties: {', '.join(penalties_applied)}"
            
        logger.info(f"[ScoringHook] {summary}")
        
        # Store metadata
        state.aux_data['score_summary'] = summary
        state.aux_data['calculated_average'] = average
        state.aux_data['penalties_applied'] = penalties_applied
        
    except Exception as e:
        logger.error(f"[ScoringHook] Calculation failed: {e}")
        
    return state
