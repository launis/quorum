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
    if falsifier_model and hasattr(falsifier_model, "falsifier_data") and getattr(
        falsifier_model, "falsifier_data", None
    ):
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

    # V2 Architecture Isolation: Attempt to find context in isolated data,
    # or explicitly fetch from the global context variables wrapper if provided by DAGExecutor.
    context = data.get("_sys_context_vars", data)

    # 1. Security Penalty Check (Guard)
    security_threat = _extract_guard_flag(context)

    # 2. Falsifier Penalty Check
    falsifier_data = _extract_falsifier_data(context)
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
        if judge_key in context:
            judge_model = context.get(judge_key)
            if not judge_model:
                continue
            candidates.append(judge_model)

    for item in candidates:
        if not item:
            continue

        # Handle both dicts and inflated models robustly
        # Handle both dicts and inflated models robustly
        if isinstance(item, dict):
            # Check for legacy nested score_card
            score_card = item.get("score_card", {})
            if isinstance(score_card, dict) and "total_score" in score_card:
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
            else:
                # Direct Matrix Evaluation (V2 Flat Schema) - e.g. "matrix_judge": 5.0
                for k, v in item.items():
                    # We look for normalized _raw outputs or just base keys
                    if k.startswith("matrix_") and not k.endswith("_justification") and not k.endswith("_id") and not k.endswith("_quote") and not k.endswith("_raw"):
                        if isinstance(v, (int, float)):
                            # If it's a matrix key, we assume 1-5 scale by default unless specified
                            normalized = normalize_score_to_100(score=float(v), scale_min=1.0, scale_max=5.0)
                            total_score_accum += normalized
                            count += 1
                            scores_found.append(normalized)
        elif hasattr(item, "score_card") and item.score_card:
            normalized = normalize_score_to_100(
                score=item.score_card.total_score,
                scale_min=item.score_card.scale_min,
                scale_max=item.score_card.scale_max,
            )
            total_score_accum += normalized
            count += 1
            scores_found.append(normalized)
        elif hasattr(item, "model_dump"):
            # Direct Matrix Evaluation (V2 Flat Schema) for Inflated Pydantic Models
            dumped_item = item.model_dump()
            for k, v in dumped_item.items():
                if k.startswith("matrix_") and not k.endswith("_justification") and not k.endswith("_id") and not k.endswith("_quote") and not k.endswith("_raw"):
                    if isinstance(v, (int, float)):
                        normalized = normalize_score_to_100(score=float(v), scale_min=1.0, scale_max=5.0)
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
    result = {
        "total_score": final_score,
        "final_score": final_score,
        "penalties_applied": penalties
    }

    logger.info(f"[ScoringHook] Scoring complete. Score: {final_score}")
    return {"scoring_result": result}


from backend_v2.models.enums import ScoringPenalty
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
            post_hoc = (
                audit.get("post_hoc_rationalization", False)
                if isinstance(audit, dict)
                else getattr(audit, "post_hoc_rationalization", False)
            )
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

    # V2 Architecture Isolation: Fetch keys from global context wrapper if available
    context = data.get("_sys_context_vars", data)

    updates_needed = False
    new_data: dict[str, Any] = {}

    for judge_key in ["step_judge", "step_judge_cognitive"]:
        if judge_key not in context:
            continue

        judge_model = context.get(judge_key)

        if not judge_model:
            continue

        is_dict = isinstance(judge_model, dict)
        score_card = judge_model.get("score_card", {}) if is_dict else getattr(judge_model, "score_card", None)
        
        # Strategy 1: Legacy Dimensions
        if score_card:
            scale_min = score_card.get("scale_min", 0.0) if is_dict else score_card.scale_min
            dimensions = score_card.get("dimensions", []) if is_dict else score_card.dimensions
    
            penalty_triggered = False
    
            for dim in dimensions:
                dim_score = dim.get("score", 0.0) if is_dict else getattr(dim, "score", 0.0)
                dim_id = dim.get("dimension_id", "") if is_dict else getattr(dim, "dimension_id", "")
    
                if dim_score <= scale_min:
                    penalty_triggered = True
                    logger.warning(
                        f"[ScoringHook] Passive/Low Quality detected in {judge_key} dimension '{dim_id}'"
                    )
                    break
    
            if penalty_triggered:
                logger.info(f"[ScoringHook] Applying Passivity Penalty to {judge_key} (Factor {multiplier}).")
    
                current_score = score_card.get("total_score", 0.0) if is_dict else score_card.total_score
                new_score = current_score * multiplier
    
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

        # Strategy 2: V2 Matrix (Flat Schema)
        elif is_dict:
            penalty_triggered = False
            scale_min = 1.0 # Default BARS scale minimum
            
            for k, v in judge_model.items():
                if k.startswith("matrix_") and not k.endswith("_justification") and not k.endswith("_id") and not k.endswith("_quote") and not k.endswith("_raw"):
                    if isinstance(v, (int, float)):
                        if v <= scale_min:
                             penalty_triggered = True
                             logger.warning(f"[ScoringHook] Passive/Low Quality detected in V2 Matrix '{k}'")
                             break
                             
            if penalty_triggered:
                 logger.info(f"[ScoringHook] Applying V2 Passivity Penalty to {judge_key} (Factor {multiplier}).")
                 new_judge = judge_model.copy()
                 for k, v in new_judge.items():
                      if k.startswith("matrix_") and not k.endswith("_justification") and not k.endswith("_id") and not k.endswith("_quote") and not k.endswith("_raw"):
                           if isinstance(v, (int, float)):
                                new_score = v * multiplier
                                if new_score < scale_min:
                                     new_score = scale_min
                                new_judge[k] = new_score
                                # Add a penalty trace to validation string if available
                                just_key = f"{k}_justification"
                                if just_key in new_judge:
                                     new_judge[just_key] = f"[PASSIVITY PENALTY x{multiplier:.2f}] " + str(new_judge[just_key])
                 new_data[judge_key] = new_judge
                 updates_needed = True

    if updates_needed:
        return new_data

    return {}


@hook_registry.register(name="normalize_matrix_scores")
async def normalize_matrix_scores_hook(state: Any, repository: Any = None) -> Any:
    """Post-Hook to normalize any raw matrix scores into a user-defined target scale.

    It scans the current step's output in the state context.
    For any numeric field corresponding to a PromptBlock with `scales` and min/max boundaries,
    it calculates the scaled score.

    Args:
        state: WorkflowState
        repository: The active AbstractWorkflowRepository for fetching schemas.
    """
    logger.info("[ScoringHook] Running normalize_matrix_scores_hook...")

    if not repository:
        logger.warning("[ScoringHook] No repository provided. Skipping normalization.")
        return state

    # V2 Fast-Fail Architecture: State is now a strictly isolated dictionary (DAGExecutor final_dict)
    # We depend on _sys_step_id being injected during the execution context.
    if isinstance(state, dict):
        step_id = state.get("_sys_step_id")
        content_payload = state
    else:
        # Legacy fallback if anyone still executes V1 orchestration loops
        last_event = state.execution_trace[-1] if hasattr(state, "execution_trace") and state.execution_trace else None
        if not last_event or last_event.event_type != "output":
            logger.debug("[ScoringHook] No valid output event found in trace.")
            return state

        step_id = last_event.step_name
        content_payload = state.context_variables.get(step_id)
        if not content_payload:
            content_payload = last_event.content

        if not isinstance(content_payload, dict):
            # Try to convert Pydantic to dict
            if hasattr(content_payload, "model_dump"):
                content_payload = content_payload.model_dump()
            else:
                logger.debug(f"[ScoringHook] Step '{step_id}' output is not a dict/model. Skipping.")
                return state

    if not step_id:
         logger.debug("[ScoringHook] No step_id found in execution context. Skipping.")
         return state

    try:
        step_obj = await repository.get_step_by_id(step_id)
        if not step_obj:
            logger.warning(f"[ScoringHook] Step '{step_id}' not found in registry.")
            return state

        prompt_blocks_slugs = (
            step_obj.get("prompt_blocks", [])
            if isinstance(step_obj, dict)
            else getattr(step_obj, "prompt_blocks", [])
        )

        updates_made = False
        new_payload = content_payload.copy()

        for slug in prompt_blocks_slugs:
            if slug not in new_payload:
                continue

            raw_val = new_payload[slug]
            if not isinstance(raw_val, (int, float)):
                continue

            pb = await repository.get_prompt_block_by_id(slug)
            if not pb:
                logger.warning(f"[ScoringHook] Missing PromptBlock '{slug}'.")
                continue

            pb_dict = pb if isinstance(pb, dict) else pb.model_dump()

            scales = pb_dict.get("scales")
            target_min = pb_dict.get("scale_min")
            target_max = pb_dict.get("scale_max")

            if scales and target_min is not None and target_max is not None:
                # Find raw min and max from the scales definition
                scores: list[float] = []
                for s in scales:
                    val = s.get("score") if isinstance(s, dict) else getattr(s, "score", None)
                    if val is not None:
                        try:
                            scores.append(float(val))
                        except (TypeError, ValueError):
                            pass
                            
                if not scores:
                    continue

                raw_min = min(scores)
                raw_max = max(scores)

                from backend_v2.utils.math_utils import scale_to_custom_range

                scaled_val = scale_to_custom_range(
                    score=float(raw_val),
                    raw_min=raw_min,
                    raw_max=raw_max,
                    target_min=float(target_min),
                    target_max=float(target_max),
                )

                # Append raw score to payload
                new_payload[f"{slug}_raw"] = raw_val
                new_payload[slug] = scaled_val
                updates_made = True
                logger.info(
                    f"[ScoringHook] Normalized '{slug}': {raw_val} -> {scaled_val} "
                    f"(Target: {target_min}-{target_max})"
                )

        if updates_made:
            if isinstance(state, dict):
                 # V2 Dict direct mutation
                 state.update(new_payload)
            else:
                 # Legacy V1 context mutation
                 state.context_variables[step_id] = new_payload
                 step_slug = step_obj.get("slug") if isinstance(step_obj, dict) else getattr(step_obj, "slug", None)
                 if step_slug and step_slug in state.context_variables:
                     state.context_variables[step_slug] = new_payload

    except Exception as e:
        logger.error(f"[ScoringHook] Failed to normalize matrix scores: {e}", exc_info=True)
        # Fail Fast Requirement
        from backend_v2.exceptions import AppException, ErrorCodes

        raise AppException(
            message=f"Normalization failed for step '{step_id}': {e}",
            status_code=500,
            details={"error_code": ErrorCodes.HOOK_EXECUTION_FAILED.value},
        ) from e

    return state
