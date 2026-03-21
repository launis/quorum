"""Scoring Hook for evaluating agent performance and applying penalties."""

import logging
from typing import Any

from backend_v2.core.hook_registry import HookExecutionContext, hook_registry

logger = logging.getLogger(__name__)


def _extract_guard_flag(data: dict[str, Any]) -> Any | None:
    """Extracts the security threat flag from the guard output in the state.

    Args:
        data (dict): The current workflow data.

    Returns:
        Any | None: True if a security threat is detected, False otherwise, or None if guard data is missing/invalid.
    """
    guard_model = data.get("step_guard")
    if guard_model and isinstance(guard_model, dict):
        security_check = guard_model.get("security_check", {})
        if isinstance(security_check, dict) and security_check.get("threat_detected"):
            return True
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

    if isinstance(panel_model, dict) and panel_model.get("falsifier_data"):
        return panel_model["falsifier_data"]

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
    return False


@hook_registry.register(name="apply_scoring_logic")
def apply_scoring_logic_hook(data: dict[str, Any], context: HookExecutionContext) -> dict[str, Any]:
    """Workflow Data wrapper for apply_scoring_logic.

    Aggregates scores from Judge/Evaluation steps, applies penalties based on
    Security (Guard) and Falsifier findings, and returns the strictly updated dict.

    Fail Fast: Raises AppException if scoring data is invalid or missing.
    """
    logger.debug("[ScoringHook] Calculating final scores...")

    if not data:
        return {}

    # V2 Architecture Isolation: Use the explicit execution context wrapper provided by DAGExecutor.
    global_vars = context.global_context_vars
    # Use global vars for lookup if available, otherwise fallback to the isolated node data
    lookup_ctx = global_vars if global_vars else data

    # 1. Security Penalty Check (Guard)
    security_threat = _extract_guard_flag(lookup_ctx)

    # 2. Falsifier Penalty Check
    falsifier_data = _extract_falsifier_data(lookup_ctx)
    is_post_hoc = _calculate_falsifier_penalty(falsifier_data)

    if not falsifier_data:
        logger.debug("[ScoringHook] Falsifier data missing from context, skipping Falsifier Penalty.")

    # 3. Aggregate Commensurate Evaluative Scores
    # We explicitly define matrices that measure unified system quality and CAN mathematically be averaged.
    # We EXCLUDE orthogonal matrices (e.g. security, bias, certainty).
    EVALUATIVE_MATRICES = {
        # Opaque (V8)
        "blk_371c7724eeba40218409b5a3697ac1d3", # Toulmin
        "blk_a0405e121dbf44bfa8ee80566f8d0c2a", # Bloom
        "blk_bf8a99a1b3514f6c93aff42a4cc52213", # Causal Analyst
        "blk_a8e356b276f04ddeb7cc3a0eec58daf6", # Causal & Abductive
        "blk_d0e240184e0a40759d37138a250bd0aa", # Archivist
        "blk_d2013b25926f46d7b70903e69e53a61c", # Task Judge
        "blk_0522f2416e304a54a67b99ed08398ac8", # Analyst
        "blk_66d7a701ee29444b87cfc9e4471fdd20", # Logical Rigor
        "blk_affd89e862e84797bd58e7323a793517", # Factuality
        "blk_9bfcaa19335140faa3b610a1391ed950", # Evidentiary Rigor
        "blk_49360a958cc7494ebf053294fb7e2faf", # Process Integrity
        "blk_b17f535c936349e3bce6e7b19f505f2c", # Evidentiary Rigor v2
    }

    total_score_accum = 0.0
    count = 0
    scores_found = []

    # Candidate list for potential multiple judges (Standard + Cognitive)
    # Note: V2 matrices are extracted directly from the context history tree
    # But for final scoring, the Judge node has its own output. Actually, the Judge node
    # has ALL the outputs from previous nodes if using a `PromptBlock` approach.
    # Let's inspect the entire context for any `_scaled` keys that match the whitelist.
    # The Judge is the final aggregator so by checking context we capture everything.

    candidates = [lookup_ctx]  # Default to full history
    step_id = context.step_id
    if step_id in ["step_judge", "step_judge_cognitive"]:
        candidates.append(data)

    unique_matrices = {}

    def _extract_scores(source: dict[str, Any]) -> None:
        for k, v in source.items():
            if isinstance(k, str) and k.endswith("_normalized"):
                base_key = k.replace("_normalized", "")
                if base_key in EVALUATIVE_MATRICES:
                    try:
                        unique_matrices[base_key] = float(v)
                    except (ValueError, TypeError) as e:
                        from backend_v2.exceptions import AppException, ErrorCodes
                        msg = f"Corrupt scoring data: {k} could not be parsed as float (Value: {v})"
                        logger.error(f"[ScoringHook] {ErrorCodes.INVALID_OUTPUT_SCHEMA.name}: {msg}", exc_info=True)
                        raise AppException(
                            message=msg,
                            status_code=500,
                            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA}
                        ) from e
            elif isinstance(v, dict):
                _extract_scores(v)

    for item in candidates:
        if isinstance(item, dict):
            _extract_scores(item)

    for v_float in unique_matrices.values():
        total_score_accum += v_float
        count += 1
        scores_found.append(v_float)

    if count == 0:
        logger.warning("[ScoringHook] No valid commensurate scores found for aggregation.")
        average_score = 0.0
    else:
        # A true unified average (all 0-100 scales) of commensurate dimensions
        average_score = total_score_accum / count

    # 4. Apply Penalties (Log traces and apply to average without corrupting base)
    from backend_v2.settings import get_settings
    settings = get_settings()

    final_score = average_score
    penalties = []

    if security_threat:
        p_val = settings.scoring_security_penalty
        if p_val > 0:
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

    # 4.5 Algorithmic Tyranny Kill Switch (V2 Phase 9)
    # Extracts profiling metrics and strictness from the isolated Pydantic inputs block
    inputs = lookup_ctx.get("inputs", {})
    strictness_level = int(inputs.get("strictness_level", 3))

    if strictness_level == 5:
        profiler = lookup_ctx.get("profiler_metrics", {})
        control_ratio = float(profiler.get("control_ratio", 1.0))
        lexical_diversity = float(profiler.get("lexical_diversity", 1.0))

        if control_ratio > 0.90 or lexical_diversity < 0.40:
            final_score = 0.0
            penalties.append("Algorithmic Tyranny Kill Switch Activated (Objective Criteria Failed)")
            logger.warning(
                f"[ScoringHook] Algorithmic Tyranny Kill Switch Activated! "
                f"Control Ratio: {control_ratio}, Lexical Diversity: {lexical_diversity}. Override to 0.0."
            )

    # Safety Clamp (0.0 - 100.0)
    final_score = max(0.0, final_score)

    # 5. Create Result with True Averaging
    result = {
        "total_score": final_score,
        "final_score": final_score,
        "penalties_applied": penalties,
        "aggregation_status": f"V2 Commensurate Average of {count} matrices"
    }

    logger.info(
        f"[ScoringHook] Scoring validation complete. "
        f"Commensurate Base Average: {average_score:.1f}, "
        f"Final: {final_score:.1f}. Penalties: {len(penalties)}"
    )
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

    # Expects pure dictionaries
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
    if isinstance(falsifier_data, dict):
        audit = falsifier_data.get("fidelity_audit", {})
        if isinstance(audit, dict):
            post_hoc = audit.get("post_hoc_rationalization", False)

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

    # 3. Apply Penalties
    current_score: float | None = None
    field_name: str | None = None

    # Extraction (Dict only)
    # Case A: JudgeOutput
    if is_judge_output:
        current_score = result.get("score_card", {}).get("total_score")
        field_name = "score_card.total_score"

    # Case B: EvaluationResult
    elif is_eval_result:
        current_score = result.get("total_score")
        field_name = "total_score"

    # FAIL FAST: If we still don't have a score
    if current_score is None:
        from backend_v2.exceptions import AppException, ErrorCodes
        msg = f"Strict Scoring: Could not extract 'total_score' from {type(result).__name__}."
        logger.error(f"[ScoringHook] {ErrorCodes.INVALID_OUTPUT_SCHEMA.name}: {msg}")
        raise AppException(
            message=msg,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA},
        )

    # Calculate New Score
    new_score = current_score * penalty_factor

    logger.info(
        f"[ScoringHook] Penalties applied: {penalties}. "
        f"Factor: {penalty_factor:.2f}. Score {current_score} -> {new_score}"
    )

    # 4. Return Updated Model (Immutable Update - Dict Only)
    new_result = result.copy() if isinstance(result, dict) else {}
    if not isinstance(result, dict):
        return result

    new_result["penalties"] = penalties

    if field_name == "score_card.total_score":
        score_card = new_result.get("score_card", {}).copy()
        score_card["total_score"] = new_score
        new_result["score_card"] = score_card
    elif field_name is not None:
        new_result[field_name] = new_score

    return new_result


@hook_registry.register(name="enforce_passivity_penalty")
def enforce_passivity_penalty_hook(data: dict[str, Any], context: HookExecutionContext) -> dict[str, Any]:
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

    # V2 Architecture Isolation: Use the explicit execution context wrapper
    global_vars = context.global_context_vars
    lookup_ctx = global_vars if global_vars else data

    updates_needed = False
    new_data: dict[str, Any] = {}

    judges_to_check = []

    # 1. From context (legacy/global)
    for judge_key in ["step_judge", "step_judge_cognitive"]:
        if judge_key in lookup_ctx:
            judges_to_check.append((judge_key, lookup_ctx.get(judge_key), False))

    # 2. From V2 Isolation Fix (post-hook)
    step_id = context.step_id
    if step_id in ["step_judge", "step_judge_cognitive"]:
        judges_to_check.append((step_id, data, True))

    for judge_key, judge_model, is_post_hook in judges_to_check:
        if not judge_model or not isinstance(judge_model, dict):
            continue

        score_card = judge_model.get("score_card", {})

        # Strategy 1: Legacy Dimensions
        if score_card:
            scale_min = score_card.get("scale_min", 0.0)
            dimensions = score_card.get("dimensions", [])

            penalty_triggered = False

            for dim in dimensions:
                if not isinstance(dim, dict):
                    continue
                dim_score = dim.get("score", 0.0)
                dim_id = dim.get("dimension_id", "")

                if dim_score <= scale_min:
                    penalty_triggered = True
                    logger.warning(
                        f"[ScoringHook] Passive/Low Quality detected in {judge_key} dimension '{dim_id}'"
                    )
                    break

            if penalty_triggered:
                logger.info(f"[ScoringHook] Applying Passivity Penalty to {judge_key} (Factor {multiplier}).")

                current_score = score_card.get("total_score", 0.0)
                new_score = current_score * multiplier

                if new_score < scale_min:
                    logger.warning(
                        f"[ScoringHook] Passivity penalty reduced score ({new_score}) "
                        f"below min ({scale_min}). Clamping."
                    )
                    new_score = scale_min

                new_card = score_card.copy()
                new_card["total_score"] = new_score
                new_card["verdict"] = str(new_card.get("verdict", "")) + f" [PASSIVITY PENALTY x{multiplier:.2f}]"

                if is_post_hook:
                    new_data["score_card"] = new_card
                else:
                    new_judge = judge_model.copy()
                    new_judge["score_card"] = new_card
                    new_data[judge_key] = new_judge

                updates_needed = True

        # Strategy 2: V2 Matrix (Flat Schema)
        else:
            penalty_triggered = False
            scale_min = 1.0 # Default BARS scale minimum

            for k, v in judge_model.items():
                if (
                    k.startswith("matrix_")
                    and not k.endswith("_justification")
                    and not k.endswith("_id")
                    and not k.endswith("_quote")
                    and not k.endswith("_raw")
                ):
                    if isinstance(v, (int, float)):
                        if v <= scale_min:
                             penalty_triggered = True
                             logger.warning(f"[ScoringHook] Passive/Low Quality detected in V2 Matrix '{k}'")
                             break

            if penalty_triggered:
                 logger.info(f"[ScoringHook] Applying V2 Passivity Penalty to {judge_key} (Factor {multiplier}).")
                 new_judge = judge_model.copy()
                 for k, v in new_judge.items():
                      if (
                          k.startswith("matrix_")
                          and not k.endswith("_justification")
                          and not k.endswith("_id")
                          and not k.endswith("_quote")
                          and not k.endswith("_raw")
                      ):
                           if isinstance(v, (int, float)):
                                new_score = v * multiplier
                                if new_score < scale_min:
                                     new_score = scale_min
                                new_judge[k] = new_score
                                # Add a penalty trace to validation string if available
                                just_key = f"{k}_justification"
                                if just_key in new_judge:
                                     new_judge[just_key] = (
                                         f"[PASSIVITY PENALTY x{multiplier:.2f}] "
                                         + str(new_judge[just_key])
                                     )

                 if is_post_hook:
                     for k, v in new_judge.items():
                         if k in judge_model and judge_model[k] != v:
                             new_data[k] = v
                 else:
                     new_data[judge_key] = new_judge
                 updates_needed = True

    if updates_needed:
        return new_data

    return {}


@hook_registry.register(name="normalize_matrix_scores")
async def normalize_matrix_scores_hook(state: dict[str, Any], context: HookExecutionContext) -> dict[str, Any]:
    """Post-Hook to normalize any raw matrix scores into a user-defined target scale.

    It scans the current step's output in the state context.
    For any numeric field corresponding to a PromptBlock with `scales` and min/max boundaries,
    it calculates the scaled score.

    Args:
        state: WorkflowState
        context: The strictly typed HookExecutionContext containing dependencies.
    """
    logger.info("[ScoringHook] Running normalize_matrix_scores_hook...")

    repository = context.repository
    if not repository:
        logger.warning("[ScoringHook] No repository provided in HookExecutionContext. Skipping normalization.")
        return state

    # V2 Fast-Fail Architecture: State is now a strictly isolated dictionary (DAGExecutor final_dict)
    # We depend on _sys_step_id being injected during the execution context.
    if not isinstance(state, dict):
        logger.debug("[ScoringHook] State is not a dictionary. Skipping.")
        return state

    # Look up the PromptBlocks from the task_blueprint (the actual Step model schema)
    # rather than the workflow's StepRule instance ID, which lacks the prompt_blocks array.
    blueprint_id = context.task_blueprint or context.step_id

    content_payload = state

    if not blueprint_id:
         logger.debug("[ScoringHook] No blueprint_id or step_id found in execution context. Skipping.")
         return state

    try:
        step_obj = await repository.get_step_by_id(blueprint_id)
        if not step_obj:
            logger.warning(f"[ScoringHook] Step blueprint '{blueprint_id}' not found in registry.")
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

            if slug not in new_payload:
                continue

            # --- Raw Float Cast Enforcement (V8 Pipeline) ---
            # Ensure the raw value itself is cast to a strict float so it hits the database
            # as a number, not a string representation of a number.
            try:
                raw_float_val = float(new_payload[slug])
                new_payload[slug] = raw_float_val
                raw_val = raw_float_val
            except (ValueError, TypeError):
                # Graceful Degradation: Log info before skipping.
                # Non-numeric outputs (like JSON blobs or reasoning traces) are expected for text PromptBlocks.
                # Downgraded from ERROR to DEBUG to avoid terrifying the user with stack traces.
                logger.debug(
                    f"[ScoringHook] Non-numeric data for '{slug}', "
                    f"skipping score normalization. Value snippet: {str(new_payload[slug])[:100]}..."
                )
                continue

            if not isinstance(raw_val, (int, float)):
                continue

            pb = await repository.get_prompt_block_by_id(slug)
            if not pb:
                logger.warning(f"[ScoringHook] Missing PromptBlock '{slug}'.")
                continue

            pb_dict = pb if isinstance(pb, dict) else pb.model_dump()
            logger.debug(
                f"[ScoringHook] Found PromptBlock '{slug}' "
                f"with allowed decimals: {pb_dict.get('allow_decimals')}"
            )

            scales = pb_dict.get("scales")
            target_min = pb_dict.get("scale_min")
            target_max = pb_dict.get("scale_max")

            # Fallback: Infer min/max from the actual scales array if missing
            if scales and (target_min is None or target_max is None):
                scores_in_scales = []
                for s in scales:
                    val = s.get("score") if isinstance(s, dict) else getattr(s, "score", None)
                    if val is not None:
                        try:
                            scores_in_scales.append(float(val))
                        except (TypeError, ValueError):
                            pass
                if scores_in_scales:
                    target_min = min(scores_in_scales)
                    target_max = max(scores_in_scales)

            if scales and target_min is not None and target_max is not None:
                from backend_v2.utils.math_utils import calculate_scaled_score, normalize_score_to_100

                # 1. The original AI output
                raw_float = float(raw_val)
                number_of_options = len(scales)

                # 2. The Python-scaled calculated value based on relative proportion of options (V2 Logic)
                scaled_val = calculate_scaled_score(
                     score=raw_float,
                     number_of_options=number_of_options,
                     scale_min=float(target_min),
                     scale_max=float(target_max),
                )

                # 3. The 1-100 normalized value for commensurable aggregation (V2 Logic)
                normalized_val = normalize_score_to_100(
                    score=raw_float,
                    number_of_options=number_of_options,
                )

                # Store exactly three properties
                new_payload[slug] = raw_val
                new_payload[f"{slug}_scaled"] = scaled_val
                new_payload[f"{slug}_normalized"] = normalized_val

                # Strip out the ||DECIMAL: X.Y|| Chain-of-Thought tag from justification before saving
                just_key = f"{slug}_justification"
                if just_key in new_payload and isinstance(new_payload[just_key], str):
                    import re
                    # Non-greedy strip of anything resembling ||DECIMAL: X.Y||
                    cleaned = re.sub(r'\|\|DECIMAL:\s*[0-9.]+\|\|', '', new_payload[just_key])
                    new_payload[just_key] = cleaned.strip()

                updates_made = True
                logger.info(
                    f"[ScoringHook] 3-Tier Score '{slug}': Raw={raw_val}, "
                    f"Scaled={scaled_val}, Normalized={normalized_val} "
                    f"(Scale: {target_min}-{target_max})"
                )

        if updates_made:
             # V2 Dict direct mutation
             state.update(new_payload)

    except Exception as e:
        # Fail Fast Requirement
        from backend_v2.exceptions import AppException, ErrorCodes
        msg = f"Normalization failed for step '{blueprint_id}': {e}"
        logger.error(f"[ScoringHook] {ErrorCodes.HOOK_EXECUTION_FAILED.name}: {msg}", exc_info=True)

        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.HOOK_EXECUTION_FAILED},
        ) from e

    return state
