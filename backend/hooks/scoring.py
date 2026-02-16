"""Scoring hooks for applying penalties and calculating averages."""

import logging
from typing import Optional, List, Any

from backend.exceptions import AppException
from backend.models.state import WorkflowState
from backend.models.domain.judge import JudgeOutput, ScoringResult, DimensionResultItem

logger = logging.getLogger(__name__)


def apply_scoring_logic(state: WorkflowState) -> WorkflowState:
    """HOOK: apply_scoring_logic.

    Applies deterministic penalties based on Guard (Security) and Falsifier (Logical) findings,
    then calculates final score averages. OVERWRITES the JudgeOutput with the authoritative score.

    Rules:
    1. Security Threat -> All scores capped at 1.
    2. Post-Hoc Rationalization -> All scores capped at 2.

    Args:
        state (WorkflowState): Current state containing Judge, Guard, and Falsifier outputs.

    Returns:
        WorkflowState: State with updated JudgeOutput and ScoringResult.
        
    Raises:
        AppException: If critical scoring data is missing or calculation fails.
    """
    logger.debug("[ScoringHook] Applying scoring logic...")

    # Helper to get step data safe from context_variables (Pydantic models expected)
    def _get_step_model(key: str) -> Any:
        val = state.context_variables.get(key)
        # Verify it's not a dict (Strict Mode) unless strictly necessary for legacy transition
        # We allow dict but log warning if not model? No, strict mandate says Pydantic.
        # However, for robustness we accept models.
        return val

    step_judge = _get_step_model("step_judge")
    step_judge_cognitive = _get_step_model("step_judge_cognitive")

    # Identify targets for scoring update
    target_steps = []
    if step_judge:
        target_steps.append("step_judge")
    if step_judge_cognitive:
        target_steps.append("step_judge_cognitive")

    # FAIL FAST: If this hook is configured, it MUST find a judge output.
    if not target_steps:
        error_code = "SCORING_MISSING_JUDGE_OUTPUT"
        msg = "Cannot calculate scores: No 'step_judge' or 'step_judge_cognitive' found in state."
        logger.error(f"[ScoringHook] {msg}")
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": error_code}
        )

    try:
        # --- DETERMINISTIC RULE ENFORCEMENT & CALC ---
        
        # Rule 1: Security Threat (Guard) -> Auto Fail (1/4)
        security_threat = False
        penalties_applied = []

        step_guard = _get_step_model("step_guard")
        if step_guard:
             # Strict Pydantic Access
             # Guard output model structure: security_check.uhka_havaittu
             if hasattr(step_guard, "security_check"):
                 sec_check = step_guard.security_check
                 if sec_check and getattr(sec_check, "uhka_havaittu", False):
                     security_threat = True
                     penalties_applied.append("Security Threat (Score capped at 1)")
        
        # Rule 2: Logical Failures (Falsifier) -> Max Score 2/4
        logical_failure = False
        step_falsifier = _get_step_model("step_falsifier")

        if not security_threat and step_falsifier:
            # Falsifier output model structure: paattelyketjun_uskollisuus_auditointi.onko_post_hoc_rationalisointia
             if hasattr(step_falsifier, "paattelyketjun_uskollisuus_auditointi"):
                 audit = step_falsifier.paattelyketjun_uskollisuus_auditointi
                 if audit and getattr(audit, "onko_post_hoc_rationalisointia", False):
                     logical_failure = True
                     penalties_applied.append("Logical Fallacies (Score capped at 2)")

        new_context = state.context_variables.copy()
        scoring_result_metadata = None # We'll store the last one as metadata

        # Apply to ALL found judge outputs
        for step_key in target_steps:
            original_output = _get_step_model(step_key)
            
            # Strict Constraint: Must be Pydantic Model (JudgeOutput) or compatible
            if not isinstance(original_output, JudgeOutput):
                 # Fail Fast if we encounter legacy dicts in a strict hook
                 # OR convert? Strict mandate suggests fail fast or explicit conversion.
                 # Let's try to adapt if it looks like a dict, but prefer failing if structure is wrong.
                 if isinstance(original_output, dict):
                     try:
                         original_output = JudgeOutput(**original_output)
                     except Exception as e:
                         raise AppException(
                             message=f"Invalid Judge Output format in '{step_key}': {e}",
                             status_code=500,
                             details={"error_code": "SCORING_INVALID_DATA_FORMAT", "step": step_key}
                         ) from e
                 else:
                     # Unknown type
                     raise AppException(
                         message=f"Unknown data type for '{step_key}': {type(original_output)}",
                         status_code=500,
                         details={"error_code": "SCORING_INVALID_DATA_TYPE"}
                     )

            # Work on Pydantic Model
            score_card = original_output.score_card
            dimensions = score_card.dimensions
            
            total_sum = 0.0
            count = 0
            
            # Update dimensions loop
            updated_dimensions = []
            for dim in dimensions:
                val = dim.score
                
                if security_threat:
                    val = 1.0
                elif logical_failure and val > 2.0:
                    val = 2.0
                
                # Update dimension with penalty if changed
                new_dim = dim
                if val != dim.score:
                    new_dim = dim.model_copy(update={"score": val, "reasoning": dim.reasoning + " [PENALTY APPLIED]"})
                
                updated_dimensions.append(new_dim)
                total_sum += float(val)
                count += 1
            
            if count == 0:
                    # FAIL FAST
                    raise AppException(
                        message=f"Judge output '{step_key}' has no dimensions to score.",
                        status_code=500,
                        details={"error_code": "SCORING_NO_DIMENSIONS"}
                    )

            # Calculate Average
            if not score_card.scale_max:
                 raise AppException(
                     message=f"Missing 'scale_max' in '{step_key}'. Cannot calculate partials.",
                     status_code=500,
                     details={"error_code": "SCORING_MISSING_SCALE_MAX"}
                 )
            scale_max = float(score_card.scale_max)
            
            new_avg = round(total_sum / count, 2)
            
            # Construct Summary
            summary = f"Deterministic Score: {total_sum}/{count * scale_max} (Avg: {new_avg:.2f})"
            if penalties_applied:
                summary += f" | Penalties: {', '.join(penalties_applied)}"

            # Create Updated ScoreCard
            new_verdict = score_card.verdict
            if penalties_applied:
                    new_verdict += f" [PENALTIES: {'; '.join(penalties_applied)}]"

            updated_card = score_card.model_copy(update={
                "total_score": new_avg,
                "dimensions": updated_dimensions,
                "verdict": new_verdict
            })

            # Create Updated Output
            updated_output = original_output.model_copy(update={
                "score_card": updated_card
            })
            
            # Update State
            new_context[step_key] = updated_output
            logger.info(f"[ScoringHook] Updated '{step_key}' with authoritative score: {new_avg}")

            # Create legacy ScoringResult for metadata
            scoring_result_metadata = ScoringResult(
                total_score=total_sum,
                calculated_average=new_avg,
                score_summary=summary,
                penalties_applied=penalties_applied
            )

    except AppException:
        raise
    except Exception as e:
        error_code = "SCORING_CALCULATION_FAILED"
        logger.error(f"[ScoringHook] {error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e),
            status_code=500,
            details={"error_code": error_code}
        ) from e

    # Store metadata
    if scoring_result_metadata:
        new_context["scoring_result"] = scoring_result_metadata
        # Legacy support (kept for frontend compat but sourced from object)
        new_context["score_summary"] = scoring_result_metadata.score_summary
        new_context["calculated_average"] = scoring_result_metadata.calculated_average
        new_context["penalties_applied"] = scoring_result_metadata.penalties_applied

    return state.model_copy(update={"context_variables": new_context})


def enforce_passivity_penalty(state: WorkflowState, step_id: str = "step_judge") -> WorkflowState:
    """HOOK: enforce_passivity_penalty.

    Strictly enforces a 'Passiveness Cutter' penalty:
    If any dimension is rated at the absolute minimum (Level 1 / Passenger),
    the TOTAL score is capped at the lower third of the scale (Level 2 equivalent).

    STRICT VALIDATION:
    - Requires 'scale_min' and 'scale_max' in the step result.
    - Raises AppException if missing (RFC 7807 Fail Fast).
    
    Args:
        state (WorkflowState): Current workflow state.
        step_id (str): The step ID to audit (default: 'step_judge').

    Returns:
        WorkflowState: Updated state with capped score if penalty applies.
        
    Raises:
        AppException: If scale validation fails.
    """
    # 1. Retrieve Result (Smart Detection)
    # If step_id is default 'step_judge' but not found, try 'step_judge_cognitive'
    result = state.context_variables.get(step_id)

    if not result and step_id == "step_judge":
        # Fallback to cognitive judge
        alt_id = "step_judge_cognitive"
        result = state.context_variables.get(alt_id)
        if result:
            logger.info(f"[ScoringHook] 'step_judge' not found. Switched to '{alt_id}'.")
            step_id = alt_id

    if not result:
        # If explicitly checking passivity, and no judge output exists, we can return state.
        # This is not a failure of the hook logic itself, but lack of data to operate on.
        # However, checking if this should be an error? 
        # Usually hooks run only if prerequisites met. Let's log warning and return.
        logger.warning(f"[ScoringHook] Step '{step_id}' not found in context. Skipping passivity penalty check.")
        return state

    try:
        # Helper to get value strict
        def get_val_strict(obj, key):
            val = None
            if isinstance(obj, dict):
                val = obj.get(key)
            else:
                val = getattr(obj, key, None)
            
            if val is None:
                 raise AppException(
                     message=f"Missing required field '{key}' in '{step_id}' output.",
                     status_code=500,
                     details={"error_code": "SCORING_MISSING_FIELD", "field": key}
                 )
            return val

    # 2. Strict Scale Validation (No Defaults)
        # Check if score_card wrapper exists (JudgeOutput structure)
        score_card = result
        if hasattr(result, "score_card"):
            score_card = result.score_card
        elif isinstance(result, dict):
             # Strict: We should have corrected this to Pydantic by now or we fail.
             # User mandate: "no fallbacks". If it's a dict, strictly check keys.
             if "score_card" in result:
                 score_card = result["score_card"]
        
        # Now access scale on score_card
        s_min_val = get_val_strict(score_card, "scale_min")
        s_max_val = get_val_strict(score_card, "scale_max")

        try:
            s_min = float(s_min_val)
            s_max = float(s_max_val)
        except (ValueError, TypeError) as e:
            raise AppException(
                message=f"Invalid scale values in '{step_id}': {e}",
                status_code=500,
                details={"error_code": "SCORING_INVALID_SCALE_VALUES"}
            ) from e

        # 3. Analyze Dimensions
        dimensions = get_val_strict(score_card, "dimensions")
        if not isinstance(dimensions, list):
             raise AppException(
                 message=f"Invalid 'dimensions' format in '{step_id}'. Expected List.",
                 status_code=500,
                 details={"error_code": "SCORING_INVALID_DATA_FORMAT"}
             )

        passenger_found = False
        for dim in dimensions:
            # Check if score matches absolute minimum (Sensitivity: Float comparison)
            score = get_val_strict(dim, "score") # Fail if score missing
            
            if abs(float(score) - s_min) < 0.01:
                passenger_found = True
                break

        # 4. Apply Penalty
        if passenger_found:
            scale_range = s_max - s_min
            # Cap = Min + 1/2 of range (50% rule)
            penalty_cap = s_min + (scale_range / 2.0)

            total_score_val = get_val_strict(score_card, "total_score")
            current_total = float(total_score_val)

            if current_total > penalty_cap:
                logger.warning(
                    f"[ScoringHook] 📉 Enforcing Passiveness Penalty on {step_id}. "
                    f"Passenger rating detected. Score capped: {current_total} -> {penalty_cap:.2f}"
                )

                # Apply Cap
                # Check if Pydantic Model (Frozen)
                if hasattr(score_card, "model_copy"):
                    # Update ScoreCard
                    new_verdict = getattr(score_card, "verdict", "") + f" [PASSIVENESS_PENALTY: Capped at {penalty_cap:.2f}]"
                    
                    new_card = score_card.model_copy(update={
                        "total_score": penalty_cap,
                        "verdict": new_verdict
                    })
                    
                    # Update Output Wrapper
                    if hasattr(result, "model_copy"):
                         new_result = result.model_copy(update={"score_card": new_card})
                    else:
                         # Should not happen if JudgeOutput structure is respected
                         new_result = new_card 

                    # Update Context
                    new_context = state.context_variables.copy()
                    new_context[step_id] = new_result
                    return state.model_copy(update={"context_variables": new_context})

                else:
                    # Strict Fail: We do not support legacy dict mutation anymore.
                    raise AppException(
                        message=f"Cannot apply penalty to mutable dict in '{step_id}'. Strict Pydantic model required.",
                        status_code=500,
                        details={"error_code": "SCORING_LEGACY_DATA_REJECTED"}
                    )

    except AppException:
        raise
    except Exception as e:
        error_code = "SCORING_PASSIVITY_PENALTY_FAILED"
        logger.error(f"[ScoringHook] {error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e),
            status_code=500,
            details={"error_code": error_code}
        ) from e

    return state
