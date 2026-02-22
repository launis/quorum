"""Scoring Hook for evaluating agent performance and applying penalties."""

import logging
from typing import Any

from backend.exceptions import AppException, ErrorCodes
from backend.models.domain import (
    FalsifierOutput,
    GuardOutput,
    JudgeOutput,
    ScoringResult,
)
from backend.models.state import WorkflowState
from backend.utils.pydantic_utils import inflate

logger = logging.getLogger(__name__)


def apply_scoring_logic(state: WorkflowState) -> WorkflowState:
    """HOOK: apply_scoring_logic.

    Aggregates scores from Judge/Evaluation steps, applies penalties based on
    Security (Guard) and Falsifier findings, and updates the state.

    Fail Fast: Raises AppException if scoring data is invalid or missing.
    """
    logger.debug("[ScoringHook] Calculating final scores...")

    # Strict Enforce: State must be WorkflowState object
    if isinstance(state, dict):
        logger.error("[ScoringHook] Received dict state instead of WorkflowState. Rejecting.")
        raise AppException(
            message="Scoring Hook received dict state. Strict Pydantic Enforcement Violation.",
            status_code=500,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA},
        )

    context = state.context_variables

    # 1. Security Penalty Check (Guard)
    security_threat = False
    guard_model = state.get_context("step_guard", GuardOutput)
    if guard_model:
        # Use English keys from model
        if guard_model.security_check.threat_detected:
            security_threat = True
    else:
        logger.warning("[ScoringHook] step_guard present but failed validation via inflate.")

    # 2. Falsifier Penalty Check
    is_post_hoc = False
    falsifier_model = state.get_context("step_falsifier", FalsifierOutput)
    if falsifier_model:
        # FalsifierData -> ReasoningFidelity -> post_hoc_rationalization
        if falsifier_model.falsifier_data.fidelity_audit.post_hoc_rationalization:
            is_post_hoc = True
    else:
        logger.warning("[ScoringHook] step_falsifier present but failed validation via inflate.")

    # 3. Aggregate Scores from Audit Results
    total_score_accum = 0.0
    count = 0
    scores_found = []

    # Candidate list for potential multiple judges (Standard + Cognitive)
    candidates = []

    for judge_key in ["step_judge", "step_judge_cognitive"]:
        if judge_key in context:
            # Strict: Use Typed Accessor with Fail Fast
            judge_model = state.get_context(judge_key, JudgeOutput)
            if not judge_model:
                logger.error(f"[ScoringHook] Inflation failed for {judge_key}. Invalid data structure.")
                raise AppException(
                    message=f"Scoring Error: Data in {judge_key} is invalid (Inflation Failed).",
                    details={"error_code": ErrorCodes.SCORING_LEGACY_DATA_REJECTED},
                )
            candidates.append(judge_model)

    for item in candidates:
        if not item:
            continue

        # Try JudgeOutput (New Standard)
        # Using strict inflate here because item is from list iteration, not direct context key
        judge_model = inflate(item, JudgeOutput)
        if judge_model:
            total_score_accum += judge_model.score_card.total_score
            count += 1
            scores_found.append(judge_model.score_card.total_score)
            continue

    if count == 0:
        logger.warning("[ScoringHook] No valid scores found from Judge/Evaluation steps.")
        average_score = 0.0
    else:
        average_score = total_score_accum / count

    # 4. Apply Penalties (Relative to Values via Settings)
    from backend.settings import get_settings

    settings = get_settings()

    final_score = average_score
    penalties = []

    if security_threat:
        p_val = settings.scoring_security_penalty
        if p_val > 0:
            # Relative Penalty (Multiplicative)
            # e.g. score 4.0 * (1.0 - 0.1) = 3.6
            final_score *= 1.0 - p_val
            penalties.append(f"Security Threat Detected (-{p_val * 100:.0f}%)")
        else:
            logger.warning("[ScoringHook] Security Threat Detected (Logged Only - Penalty Disabled in Settings)")

    if is_post_hoc:
        p_val = settings.scoring_post_hoc_penalty
        if p_val > 0:
            final_score *= 1.0 - p_val
            penalties.append(f"Post-Hoc Rationalization Detected (-{p_val * 100:.0f}%)")
        else:
            logger.warning(
                "[ScoringHook] Post-Hoc Rationalization Detected (Logged Only - Penalty Disabled in Settings)"
            )

    # Safety Clamp (Relative scores should technically not go below min if min is 0, but if min is 1, they can)
    # We don't have easy access to scale_min here across all judges, so we assume 1.0 or 0.0 depending on context?
    # Actually, apply_scoring_logic is for EvaluationResult which is a Summary.
    # Let's rely on the individual judge updates for strict bounds, but for this summary, max(0.0) is safe.
    final_score = max(0.0, final_score)

    # 5. Create Result
    summary = f"Final Score: {final_score:.2f} (Base: {average_score:.2f}). "
    if penalties:
        summary += f"Penalties: {', '.join(penalties)}."
    else:
        summary += "No penalties applied."

    result = ScoringResult(
        total_score=final_score, calculated_average=average_score, score_summary=summary, penalties_applied=penalties
    )

    # 6. Update State
    new_context = context.copy()
    new_context["scoring_result"] = result

    logger.info(f"[ScoringHook] Scoring complete. Score: {final_score}")
    return state.model_copy(update={"context_variables": new_context})


from backend.models.enums import ScoringPenalty
from backend.settings import get_settings


def enforce_scoring_penalties(result: Any, context: Any) -> Any:
    """Refined Truth Protocol: Applies penalties to the EvaluationResult.

    Args:
        result (EvaluationResult | dict): The initial judgment result to penalize.
        context (dict | BaseModel): The input context (JudgeInput or dict) containing other agent outputs.

    Returns:
        EvaluationResult | dict: The penalized result.
    """
    settings = get_settings()
    logger.info("[ScoringHook] Enforcing penalties on EvaluationResult...")

    # 1. Detect Penalties
    penalties = []
    penalty_factor = 1.0

    # Helper for polymorphic access (Dict or Pydantic)
    def _get_ctx(key: str) -> Any:
        if isinstance(context, dict):
            return context.get(key)
        return getattr(context, key, None)

    # 1.1 Security Warnings (Guard)
    step_guard = _get_ctx("step_guard")
    if step_guard:
        guard_model = inflate(step_guard, GuardOutput)
        if guard_model and guard_model.security_check.threat_detected:
            # Load penalty from settings
            p_val = settings.scoring_security_penalty
            if p_val > 0:
                # Standard: Append Enum Key + Percentage
                penalties.append(f"{ScoringPenalty.SECURITY_THREAT.value} (-{p_val * 100:.0f}%)")
                penalty_factor *= 1.0 - p_val
            else:
                logger.warning(f"[ScoringHook] {ScoringPenalty.SECURITY_THREAT.value} (Logged Only - Penalty Disabled)")

    # 1.2 Falsifier Findings
    step_falsifier = _get_ctx("step_falsifier")
    if step_falsifier:
        falsifier_model = inflate(step_falsifier, FalsifierOutput)
        if falsifier_model and falsifier_model.falsifier_data.fidelity_audit.post_hoc_rationalization:
            # Load penalty from settings
            p_val = settings.scoring_post_hoc_penalty
            if p_val > 0:
                # Standard: Append Enum Key + Percentage
                penalties.append(f"{ScoringPenalty.POST_HOC.value} (-{p_val * 100:.0f}%)")
                penalty_factor *= 1.0 - p_val
            else:
                logger.warning(f"[ScoringHook] {ScoringPenalty.POST_HOC.value} (Logged Only - Penalty Disabled)")

    if not penalties:
        return result

    # 2. Strict Pydantic Enforcement
    if isinstance(result, dict):
        logger.error("[ScoringHook] Output result is a dict, expected Pydantic Model.")
        raise AppException(
            message="Strict Scoring Error: Dictionary usage forbidden. Agents must return Pydantic Models.",
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA},
        )

    # 3. Apply Penalties
    current_score: float | None = None
    field_name: str | None = None

    # Extraction (Pydantic Only)
    # Case A: JudgeOutput
    if hasattr(result, "score_card"):
        current_score = result.score_card.total_score
        field_name = "score_card.total_score"

    # Case B: EvaluationResult
    elif hasattr(result, "total_score"):
        current_score = result.total_score
        field_name = "total_score"

    # FAIL FAST: If we still don't have a score
    if current_score is None:
        logger.error(f"[ScoringHook] Could not extract total_score from {type(result).__name__}.")
        raise AppException(
            message=f"Strict Scoring: Could not extract 'total_score' from {type(result).__name__}.",
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA},
        )

    # Calculate New Score
    new_score = current_score * penalty_factor

    logger.info(
        f"[ScoringHook] Penalties applied: {penalties}. Factor: {penalty_factor:.2f}. Score {current_score} -> {new_score}"
    )

    # 4. Return Updated Model (Immutable Update)
    updates: dict[str, Any] = {"penalties": penalties}

    if field_name == "score_card.total_score":
        # Nested update logic for JudgeOutput
        original_card = result.score_card
        new_card = original_card.model_copy(update={"total_score": new_score})
        updates["score_card"] = new_card
    elif field_name is not None:
        updates[field_name] = new_score

    return result.model_copy(update=updates)


def enforce_passivity_penalty(state: WorkflowState) -> WorkflowState:
    """Refined Truth Protocol: Enforces passivity penalty if detected in Judge Output.

    Checks if any dimension in the Judge Output has the minimum possible score.
    If found, applies a strict penalty. Supports Dual Judges (Standard & Cognitive).

    Fail Fast:
    - Raises SCORING_MISSING_FIELD if required fields are missing in dict mode (before rejection).
    - Raises SCORING_LEGACY_DATA_REJECTED if data is a dict (must be Model).
    """
    settings = get_settings()
    # User requested "Set it to max" -> 1.0 (No reduction) for testing.
    # Logic: new_score = current_score * multiplier
    multiplier = settings.scoring_passivity_multiplier

    logger.info(f"[ScoringHook] Enforcing passivity penalties (Multiplier: {multiplier})...")

    # helper for shallow copy only if needed
    context = state.context_variables
    updates_needed = False
    new_context = context.copy()

    for judge_key in ["step_judge", "step_judge_cognitive"]:
        if judge_key not in state.context_variables:
            continue

        # Best Practice: Use Typed Accessor
        # This handles dict-to-model inflation.
        judge_model = state.get_context(judge_key, JudgeOutput)

        if not judge_model:
            # Key present but inflation failed -> Invalid Data -> FAIL FAST (RFC 7807)
            # This means the dictionary structure did not match JudgeOutput schema.
            logger.error(f"[ScoringHook] Passivity check failed: {judge_key} has invalid data structure.")
            raise AppException(
                message=f"Scoring Error: Data in {judge_key} is invalid (Inflation Failed).",
                details={"error_code": ErrorCodes.SCORING_LEGACY_DATA_REJECTED},
            )

        score_card = judge_model.score_card

        # Check for Passivity (Min Score in Dimensions)
        penalty_triggered = False

        for dim in score_card.dimensions:
            # Floating point safety? Use epsilon or exact match if integer-like.
            if dim.score <= score_card.scale_min:
                penalty_triggered = True
                logger.warning(
                    f"[ScoringHook] Passive/Low Quality detected in {judge_key} dimension '{dim.dimension_id}'"
                )
                break

        if penalty_triggered:
            # Apply Penalty
            # Apply Penalty
            logger.info(f"[ScoringHook] Applying Passivity Penalty to {judge_key} (Factor {multiplier}).")
            current_score = score_card.total_score
            new_score = current_score * multiplier

            # Constraint Check: Respect scale_min
            if new_score < score_card.scale_min:
                logger.warning(
                    f"[ScoringHook] Passivity penalty reduced score ({new_score}) below min ({score_card.scale_min}). Clamping."
                )
                new_score = score_card.scale_min

            # Functional Update
            new_card = score_card.model_copy(
                update={
                    "total_score": new_score,
                    "verdict": score_card.verdict + f" [PASSIVITY PENALTY x{multiplier:.2f}]",
                }
            )
            new_judge = judge_model.model_copy(update={"score_card": new_card})

            new_context[judge_key] = new_judge
            updates_needed = True

    if updates_needed:
        return state.model_copy(update={"context_variables": new_context})

    return state
