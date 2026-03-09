"""Scoring Hook for evaluating agent performance and applying penalties."""

import logging
from typing import Any

from backend_v2.core.hook_registry import hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.utils.math_utils import normalize_score_to_100

logger = logging.getLogger(__name__)


def _extract_guard_flag(data: dict[str, Any]) -> Any | None:
    """Extracts the security threat flag from the guard output in the state.

    Args:
        data (dict): The current workflow data.

    Returns:
        Any | None: True if a security threat is detected, False otherwise, or None if guard data is missing/invalid.
    """
    if "step_guard" in data:
        guard_model = data.get("step_guard")
        if isinstance(guard_model, dict):
            security_check = guard_model.get("security_check", {})
            if isinstance(security_check, dict) and security_check.get("threat_detected"):
                return True
        elif guard_model and getattr(guard_model, "security_check", None):
            if guard_model.security_check.threat_detected:
                return True
        elif not guard_model:
            logger.warning("[ScoringHook] step_guard present but failed validation via inflate.")
    logger.debug("[ScoringHook] step_guard missing from context or no threat detected.")
    return False


def _extract_falsifier_data(data: dict[str, Any]) -> Any | None:
    """Extracts falsifier data from either step_falsifier or step_panel.

    Args:
        data (dict): The current workflow data.

    Returns:
        Any | None: The falsifier data if found, otherwise None.
    """
    falsifier_model = data.get("step_falsifier")
    panel_model = data.get("step_panel")

    if isinstance(falsifier_model, dict) and falsifier_model.get("falsifier_data"):
        return falsifier_model["falsifier_data"]
    if falsifier_model and hasattr(falsifier_model, "falsifier_data") and getattr(falsifier_model, "falsifier_data", None):
        return getattr(falsifier_model, "falsifier_data", None)

    if isinstance(panel_model, dict) and panel_model.get("falsifier_data"):
        return panel_model["falsifier_data"]
    if panel_model and hasattr(panel_model, "falsifier_data") and getattr(panel_model, "falsifier_data", None):
        return getattr(panel_model, "falsifier_data", None)

    return None


def _calculate_falsifier_penalty(falsifier_data: Any | None) -> bool:
    """Determines if a post-hoc rationalization penalty should be applied.

    Args:
        falsifier_data (Any | None): The falsifier data extracted from the state.

    Returns:
        bool: True if post-hoc rationalization is detected, False otherwise.
    """
    if isinstance(falsifier_data, dict):
        fidelity = falsifier_data.get("fidelity_audit", {})
        if isinstance(fidelity, dict) and fidelity.get("post_hoc_rationalization"):
            return True
    elif falsifier_data and hasattr(falsifier_data, "fidelity_audit"):
        if hasattr(falsifier_data.fidelity_audit, "post_hoc_rationalization"):
            if falsifier_data.fidelity_audit.post_hoc_rationalization:
                return True
    return False


@hook_registry.register(name="apply_scoring_logic")
def apply_scoring_logic_hook(data: dict[str, Any]) -> dict[str, Any]:
    """Workflow Data wrapper for apply_scoring_logic.

    Aggregates scores from Judge/Evaluation steps, applies penalties based on
    Security (Guard) and Falsifier findings, and returns the strictly updated dict.

    Fail Fast: Raises AppException if scoring data is invalid or missing.
    """
    logger.debug("[ScoringHook] Calculating final scores...")

    if not data:
        return {}

    # 1. Security Penalty Check (Guard)
    security_threat = _extract_guard_flag(data)

    # 2. Falsifier Penalty Check
    falsifier_data = _extract_falsifier_data(data)
    is_post_hoc = _calculate_falsifier_penalty(falsifier_data)

    if not falsifier_data:
        logger.debug("[ScoringHook] Falsifier data missing from context, skipping Falsifier Penalty.")

    # 3. Aggregate Scores from Audit Results
    total_score_accum = 0.0
    count = 0
    scores_found = []

    # Candidate list for potential multiple judges (Standard + Cognitive)
    candidates = []

    for judge_key in ["step_judge", "step_judge_cognitive"]:
        if judge_key in data:
            judge_model = data.get(judge_key)
            if not judge_model:
                continue
            candidates.append(judge_model)

    for item in candidates:
        if not item:
            continue

        # Handle both dicts and inflated models robustly
        if isinstance(item, dict):
            score_card = item.get("score_card", {})
            if isinstance(score_card, dict):
                # Normalize and aggregate
                total_score = score_card.get("total_score", 0.0)
                scale_min = score_card.get("scale_min", 0.0)
                scale_max = score_card.get("scale_max", 5.0)

                normalized = normalize_score_to_100(
                    score=total_score,
                    scale_min=scale_min,
                    scale_max=scale_max,
                )
                total_score_accum += normalized
                count += 1
                scores_found.append(normalized)
        elif hasattr(item, "score_card"):
            normalized = normalize_score_to_100(
                score=item.score_card.total_score,
                scale_min=item.score_card.scale_min,
                scale_max=item.score_card.scale_max,
            )
            total_score_accum += normalized
            count += 1
            scores_found.append(normalized)

    if count == 0:
        logger.warning("[ScoringHook] No valid scores found from Judge/Evaluation steps.")
        average_score = 0.0
    else:
        average_score = total_score_accum / count

    # 4. Apply Penalties (Relative to Values via Settings)
    from backend_v2.settings import get_settings

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
    # We now operate on a 0.0 - 100.0 scale for the aggregated score.
    final_score = max(0.0, final_score)

    # 5. Create Result
    # Strict Dict -> Dict Return
    result = {"penalties_applied": penalties}

    logger.info(f"[ScoringHook] Scoring complete. Score: {final_score}")
    return {"scoring_result": result}


from backend_v2.models.enums import ScoringPenalty  # type: ignore
from backend_v2.settings import get_settings


def enforce_scoring_penalties(result: Any, context_data: dict[str, Any]) -> Any:
    """Refined Truth Protocol: Applies penalties to the output of an evaluation.

    Args:
        result (Any | dict): The initial judgment result to penalize.
        context_data (dict): The input context (JudgeInput or dict) containing other agent outputs.

    Returns:
        Any | dict: The penalized result.
    """
    settings = get_settings()
    logger.info("[ScoringHook] Enforcing penalties on EvaluationResult...")

    # 1. Detect Penalties
    penalties = []
    penalty_factor = 1.0

    # Helper for polymorphic access (Dict or Pydantic)
    def _get_ctx(key: str) -> Any:
        return context_data.get(key)

    step_guard = _get_ctx("step_guard")

    # Can accept both domain models or dictionaries
    if _extract_guard_flag({"step_guard": step_guard}):
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
    step_panel = _get_ctx("step_panel")

    falsifier_data = None
    if step_falsifier and isinstance(step_falsifier, dict):
        falsifier_data = step_falsifier.get("falsifier_data")
    elif step_panel and isinstance(step_panel, dict):
        falsifier_data = step_panel.get("falsifier_data")

    post_hoc = False
    if falsifier_data:
        if isinstance(falsifier_data, dict):
            audit = falsifier_data.get("fidelity_audit", {})
            post_hoc = audit.get("post_hoc_rationalization", False) if isinstance(audit, dict) else getattr(audit, "post_hoc_rationalization", False)
        else:
            audit = getattr(falsifier_data, "fidelity_audit", None)
            post_hoc = getattr(audit, "post_hoc_rationalization", False)

    if post_hoc:
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

    # 2. Extract Data

    # Determine type of scoring we have to work with
    is_judge_output = isinstance(result, dict) and "score_card" in result
    is_eval_result = isinstance(result, dict) and "total_score" in result

    if not isinstance(result, dict):
        is_judge_output = hasattr(result, "score_card")
        is_eval_result = hasattr(result, "total_score")

    # 3. Apply Penalties
    current_score: float | None = None
    field_name: str | None = None

    # Extraction (Dict or Pydantic)
    # Case A: JudgeOutput
    if is_judge_output:
        if isinstance(result, dict):
            current_score = result.get("score_card", {}).get("total_score")
        else:
            current_score = result.score_card.total_score

        field_name = "score_card.total_score"

    # Case B: EvaluationResult
    elif is_eval_result:
        if isinstance(result, dict):
            current_score = result.get("total_score")
        else:
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
        f"[ScoringHook] Penalties applied: {penalties}. "
        f"Factor: {penalty_factor:.2f}. Score {current_score} -> {new_score}"
    )

    # 4. Return Updated Model (Immutable Update)
    if isinstance(result, dict):
        new_result = result.copy()
        new_result["penalties"] = penalties

        if field_name == "score_card.total_score":
            score_card = new_result.get("score_card", {}).copy()
            score_card["total_score"] = new_score
            new_result["score_card"] = score_card
        elif field_name is not None:
            new_result[field_name] = new_score

        return new_result
    else:
        updates: dict[str, Any] = {"penalties": penalties}

        if field_name == "score_card.total_score":
            # Nested update logic for JudgeOutput
            original_card = result.score_card
            new_card = original_card.model_copy(update={"total_score": new_score})
            updates["score_card"] = new_card
        elif field_name is not None:
            updates[field_name] = new_score

        return result.model_copy(update=updates)


@hook_registry.register(name="enforce_passivity_penalty")
def enforce_passivity_penalty_hook(data: dict[str, Any]) -> dict[str, Any]:
    """Refined Truth Protocol: Enforces passivity penalty if detected in Judge Output.

    Checks if any dimension in the Judge Output has the minimum possible score.
    If found, applies a strict penalty. Supports Dual Judges (Standard & Cognitive).

    Fail Fast:
    - Raises SCORING_MISSING_FIELD if required fields are missing in dict mode.
    """
    settings = get_settings()
    # User requested "Set it to max" -> 1.0 (No reduction) for testing.
    # Logic: new_score = current_score * multiplier
    multiplier = settings.scoring_passivity_multiplier

    logger.info(f"[ScoringHook] Enforcing passivity penalties (Multiplier: {multiplier})...")

    if not data:
        return {}

    updates_needed = False
    new_data: dict[str, Any] = {}

    for judge_key in ["step_judge", "step_judge_cognitive"]:
        if judge_key not in data:
            continue

        judge_model = data.get(judge_key)

        if not judge_model:
            continue

        is_dict = isinstance(judge_model, dict)
        score_card = judge_model.get("score_card", {}) if is_dict else getattr(judge_model, "score_card", None)

        if not score_card:
            continue

        scale_min = score_card.get("scale_min", 0.0) if is_dict else score_card.scale_min
        dimensions = score_card.get("dimensions", []) if is_dict else score_card.dimensions

        # Check for Passivity (Min Score in Dimensions)
        penalty_triggered = False

        for dim in dimensions:
            dim_score = dim.get("score", 0.0) if is_dict else getattr(dim, "score", 0.0)
            dim_id = dim.get("dimension_id", "") if is_dict else getattr(dim, "dimension_id", "")

            # Floating point safety? Use epsilon or exact match if integer-like.
            if dim_score <= scale_min:
                penalty_triggered = True
                logger.warning(
                    f"[ScoringHook] Passive/Low Quality detected in {judge_key} dimension '{dim_id}'"
                )
                break

        if penalty_triggered:
            # Apply Penalty
            logger.info(f"[ScoringHook] Applying Passivity Penalty to {judge_key} (Factor {multiplier}).")

            current_score = score_card.get("total_score", 0.0) if is_dict else score_card.total_score
            new_score = current_score * multiplier

            # Constraint Check: Respect scale_min
            if new_score < scale_min:
                logger.warning(
                    f"[ScoringHook] Passivity penalty reduced score ({new_score}) "
                    f"below min ({scale_min}). Clamping."
                )
                new_score = scale_min

            if is_dict:
                new_card = score_card.copy()
                new_card["total_score"] = new_score
                new_card["verdict"] = str(new_card.get("verdict", "")) + f" [PASSIVITY PENALTY x{multiplier:.2f}]"
                new_judge = judge_model.copy()
                new_judge["score_card"] = new_card
            else:
                new_card = score_card.model_copy(
                    update={
                        "total_score": new_score,
                        "verdict": score_card.verdict + f" [PASSIVITY PENALTY x{multiplier:.2f}]",
                    }
                )
                new_judge = judge_model.model_copy(update={"score_card": new_card})

            new_data[judge_key] = new_judge
            updates_needed = True

    if updates_needed:
        return new_data

    return {}
