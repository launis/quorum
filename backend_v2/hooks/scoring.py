"""Scoring Hook for evaluating agent performance and applying penalties."""

import logging
from typing import Any

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)


def _extract_guard_flag(data: dict[str, Any]) -> Any | None:
    """Extracts the security threat flag from the guard output in the state.

    Args:
        data (dict): The current workflow data.

    Returns:
        Any | None: True if a security threat is detected, False otherwise, or None if guard data is missing/invalid.
    """
    guard_model = data.get("step_guard")
    if guard_model:
        return guard_model.get("security_check", {}).get("threat_detected", False)
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

    if falsifier_model and falsifier_model.get("falsifier_data"):
        return falsifier_model["falsifier_data"]

    if panel_model and panel_model.get("falsifier_data"):
        return panel_model["falsifier_data"]

    return None


def _calculate_falsifier_penalty(falsifier_data: Any | None) -> bool:
    """Determines if a post-hoc rationalization penalty should be applied.

    Args:
        falsifier_data (Any | None): The falsifier data extracted from the state.

    Returns:
        bool: True if post-hoc rationalization is detected, False otherwise.
    """
    if falsifier_data:
        fidelity = falsifier_data.get("fidelity_audit", {})
        if fidelity.get("post_hoc_rationalization"):
            return True
    return False


@hook_registry.register(name="apply_scoring_logic")
def apply_scoring_logic_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Workflow Data wrapper for apply_scoring_logic.

    Aggregates scores from Judge/Evaluation steps, applies penalties based on
    Security (Guard) and Falsifier findings, and returns the strictly updated dict.

    Fail Fast: Raises AppException if scoring data is invalid or missing.
    """
    logger.debug("[ScoringHook] Calculating final scores...")

    if not state:
        return HookResult(success=True, state_delta={})

    # V2 Architecture Isolation: Use the explicit execution context wrapper provided by DAGExecutor.
    global_vars = state.global_context_vars
    # Use global vars for lookup if available, otherwise fallback to the isolated node data
    lookup_ctx = global_vars if global_vars else state.inputs

    # 1. Security Penalty Check (Guard)
    security_threat = _extract_guard_flag(lookup_ctx)

    # 2. Falsifier Penalty Check
    falsifier_data = _extract_falsifier_data(lookup_ctx)
    is_post_hoc = _calculate_falsifier_penalty(falsifier_data)

    if not falsifier_data:
        logger.debug("[ScoringHook] Falsifier data missing from context, skipping Falsifier Penalty.")

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
    step_id = state.step_id
    if step_id in ["step_judge", "step_judge_cognitive"]:
        candidates.append(state.inputs)

    unique_matrices = {}

    def _extract_scores(source: dict[str, Any]) -> None:
        for k, v in source.items():
            # Epic 10: Dynamic Evaluative Matrix resolution. Only average matrices explicitly flagged.
            if isinstance(k, str) and k.endswith("_is_evaluative") and v is True:
                base_slug = k.replace("_is_evaluative", "")
                norm_key = f"{base_slug}_normalized"
                if norm_key in source:
                    unique_matrices[base_slug] = float(source[norm_key])
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
                "[ScoringHook] Algorithmic Tyranny Kill Switch Activated! "
                "Control Ratio: %s, Lexical Diversity: %s. Override to 0.0.",
                control_ratio,
                lexical_diversity,
            )

    # Safety Clamp (0.0 - 100.0)
    final_score = max(0.0, final_score)

    # 5. Create Result with True Averaging
    result = {
        "total_score": final_score,
        "final_score": final_score,
        "penalties_applied": penalties,
        "aggregation_status": f"V2 Commensurate Average of {count} matrices",
    }

    logger.info(
        "[ScoringHook] Scoring validation complete. Commensurate Base Average: %.1f, Final: %.1f. Penalties: %d",
        average_score,
        final_score,
        len(penalties),
    )
    return HookResult(success=True, state_delta={"scoring_result": result})


from backend_v2.models.enums import ScoringPenalty


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
            logger.warning("[ScoringHook] %s (Logged Only - Penalty Disabled)", ScoringPenalty.SECURITY_THREAT.value)

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
            logger.warning("[ScoringHook] %s (Logged Only - Penalty Disabled)", ScoringPenalty.POST_HOC.value)

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
        logger.error("[ScoringHook] %s: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, msg)
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
def enforce_passivity_penalty_hook(state: HookState, deps: HookDependencies) -> HookResult:
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

    logger.info("[ScoringHook] Enforcing passivity penalties (Multiplier: %s)...", multiplier)

    if not state:
        return HookResult(success=True, state_delta={})

    # V2 Architecture Isolation: Use the explicit execution context wrapper
    global_vars = state.global_context_vars
    lookup_ctx = global_vars if global_vars else state.inputs

    updates_needed = False
    new_data: dict[str, Any] = {}

    judges_to_check = []

    # 1. From context (legacy/global)
    for judge_key in ["step_judge", "step_judge_cognitive"]:
        if judge_key in lookup_ctx:
            judges_to_check.append((judge_key, lookup_ctx.get(judge_key), False))

    # 2. From V2 Isolation Fix (post-hook)
    step_id = state.step_id
    if step_id in ["step_judge", "step_judge_cognitive"]:
        judges_to_check.append((step_id, state.inputs, True))

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
                    logger.warning("[ScoringHook] Passive/Low Quality detected in %s dimension '%s'", judge_key, dim_id)
                    break

            if penalty_triggered:
                logger.info("[ScoringHook] Applying Passivity Penalty to %s (Factor %s).", judge_key, multiplier)

                current_score = score_card.get("total_score", 0.0)
                new_score = current_score * multiplier

                if new_score < scale_min:
                    logger.warning(
                        "[ScoringHook] Passivity penalty reduced score (%s) below min (%s). Clamping.",
                        new_score,
                        scale_min,
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
            scale_min = 1.0  # Default BARS scale minimum

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
                            logger.warning("[ScoringHook] Passive/Low Quality detected in V2 Matrix '%s'", k)
                            break

            if penalty_triggered:
                logger.info("[ScoringHook] Applying V2 Passivity Penalty to %s (Factor %s).", judge_key, multiplier)
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
                                new_judge[just_key] = f"[PASSIVITY PENALTY x{multiplier:.2f}] " + str(
                                    new_judge[just_key]
                                )

                if is_post_hook:
                    for k, v in new_judge.items():
                        if k in judge_model and judge_model[k] != v:
                            new_data[k] = v
                else:
                    new_data[judge_key] = new_judge
                updates_needed = True

    if updates_needed:
        return HookResult(success=True, state_delta=new_data)

    return HookResult(success=True, state_delta={})


@hook_registry.register(name="normalize_matrix_scores")
async def normalize_matrix_scores_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Post-Hook to normalize any raw matrix scores into a user-defined target scale.

    It scans the current step's output in the state context.
    For any numeric field corresponding to a PromptBlock with `scales` and min/max boundaries,
    it calculates the scaled score.

    Args:
        state: WorkflowState
        context: The strictly typed HookExecutionContext containing dependencies.
    """
    logger.info("[ScoringHook] Running normalize_matrix_scores_hook...")

    repository = deps.repository
    if not repository:
        logger.warning("[ScoringHook] No repository provided in HookDependencies. Skipping normalization.")
        return HookResult(success=True, state_delta={})

    # V2 Fast-Fail Architecture: State is now a strictly isolated dictionary (DAGExecutor final_dict)
    # We depend on _sys_step_id being injected during the execution context.
    if not isinstance(state.inputs, dict):
        logger.debug("[ScoringHook] State inputs is not a dictionary. Skipping.")
        return HookResult(success=True, state_delta={})

    # Look up the PromptBlocks from the task_blueprint (the actual Step model schema)
    # rather than the workflow's StepRule instance ID, which lacks the prompt_blocks array.
    blueprint_id = state.task_blueprint or state.step_id

    content_payload = state.inputs

    if not blueprint_id:
        logger.debug("[ScoringHook] No blueprint_id or step_id found in execution context. Skipping.")
        return HookResult(success=True, state_delta={})

    try:
        step_obj = await repository.get_step_by_id(blueprint_id)
        if not step_obj:
            logger.warning("[ScoringHook] Step blueprint '%s' not found in registry.", blueprint_id)
            return HookResult(success=True, state_delta={})

        prompt_block_ids = (
            step_obj.get("prompt_blocks", []) if isinstance(step_obj, dict) else getattr(step_obj, "prompt_blocks", [])
        )

        updates_made = False
        new_payload = content_payload.copy()

        for pb_id in prompt_block_ids:
            if pb_id not in new_payload:
                continue

            # Epic 12: Micro-CoT Nested Dictionary Support && XAI Mapping
            raw_input_val = new_payload[pb_id]

            if isinstance(raw_input_val, dict):
                # Natively map XAI attributes for Flutter UI's dedicated alert containers!
                if "step_1_evidence_quote" in raw_input_val:
                    new_payload[f"{pb_id}_cited_text_quote"] = raw_input_val["step_1_evidence_quote"]
                    updates_made = True
                if "step_1b_cited_source_id" in raw_input_val:
                    new_payload[f"{pb_id}_cited_source_id"] = raw_input_val["step_1b_cited_source_id"]
                    updates_made = True
                if "step_2_falsification" in raw_input_val:
                    new_payload[f"{pb_id}_falsification"] = raw_input_val["step_2_falsification"]
                    updates_made = True
                if "extension_coaching" in raw_input_val:
                    new_payload[f"{pb_id}_coaching"] = raw_input_val["extension_coaching"]
                    updates_made = True
                if "extension_theory_link" in raw_input_val:
                    new_payload[f"{pb_id}_theory_link"] = raw_input_val["extension_theory_link"]
                    updates_made = True

                # The core reasoning and notes replace the global fallback, avoiding hardcoded markdown
                just_parts = []
                if "evaluation_notes" in raw_input_val and raw_input_val["evaluation_notes"]:
                    just_parts.append(str(raw_input_val["evaluation_notes"]))
                if "step_3_logical_friction" in raw_input_val and raw_input_val["step_3_logical_friction"]:
                    just_parts.append(str(raw_input_val["step_3_logical_friction"]))

                if just_parts:
                    new_payload[f"{pb_id}_justification"] = "\n\n".join(just_parts)
                    updates_made = True

                # Keep text as text, numbers as numbers (Tapa 1 vs Tapa 2)
                if "step_4_final_score" in raw_input_val:
                    # Tapa 1: Extract numeric score and continue to scale logic
                    raw_input_val = raw_input_val["step_4_final_score"]
                else:
                    # Tapa 2: String-only block. We already extracted mapped fields, so skip math scaling.
                    continue

            # --- Raw Float Cast Enforcement (V8 Pipeline) ---
            # Ensure the raw value itself is cast to a strict float so it hits the database
            # as a number, not a string representation of a number.
            try:
                raw_val = float(raw_input_val)  # Always ensure we deal with flat numeric value mathematically
            except (ValueError, TypeError):
                # Graceful Degradation: Log info before skipping.
                # Non-numeric outputs (like JSON blobs or reasoning traces) are expected for text PromptBlocks.
                # Downgraded from ERROR to DEBUG to avoid terrifying the user with stack traces.
                logger.debug(
                    "[ScoringHook] Non-numeric data for '%s', skipping score normalization. Value snippet: %s...",
                    pb_id,
                    str(new_payload[pb_id])[:100],
                )
                continue

            if not isinstance(raw_val, (int, float)):
                continue

            pb = await repository.get_prompt_block_by_id(pb_id)
            if not pb:
                logger.warning("[ScoringHook] Missing PromptBlock '%s'.", pb_id)
                continue

            pb_dict = pb if isinstance(pb, dict) else pb.model_dump()
            logger.debug(
                "[ScoringHook] Found PromptBlock '%s' with allowed decimals: %s",
                pb_id,
                pb_dict.get("allow_decimals"),
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
                        except (TypeError, ValueError) as e:
                            from backend_v2.exceptions import AppException, ErrorCodes

                            msg = f"Corrupted scale value '{val}' in PromptBlock '{pb_id}'. Expected float."
                            logger.error(
                                "[ScoringHook] %s: %s",
                                ErrorCodes.CONFIGURATION_ERROR.name,
                                msg,
                                exc_info=True,
                            )
                            raise AppException(
                                message=msg,
                                status_code=500,
                                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                            ) from e
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

                # Epic 12: Flatten the Micro-CoT dict so the Flutter UI can plot the float on the XY graphs!
                new_payload[pb_id] = raw_val

                new_payload[f"{pb_id}_scaled"] = scaled_val
                new_payload[f"{pb_id}_normalized"] = normalized_val

                # Epic 10: Check the DB truth for Evaluative Matrix status and inject it
                if pb_dict.get("is_evaluative", True):
                    new_payload[f"{pb_id}_is_evaluative"] = True

                just_key = f"{pb_id}_justification"

                # Strip out the ||DECIMAL: X.Y|| Chain-of-Thought tag from justification
                # before saving (Legacy V1 Support)
                if just_key in new_payload and isinstance(new_payload[just_key], str):
                    import re

                    cleaned = re.sub(r"\|\|DECIMAL:\s*[0-9.]+\|\|", "", new_payload[just_key])
                    new_payload[just_key] = cleaned.strip()

                updates_made = True
                logger.info(
                    "[ScoringHook] 3-Tier Score '%s': Raw=%s, Scaled=%s, Normalized=%s",
                    pb_id,
                    raw_val,
                    scaled_val,
                    normalized_val,
                )

        if updates_made:
            # V2 Dict direct mutation avoided, send back state_delta
            return HookResult(success=True, state_delta=new_payload)

    except Exception as e:
        from backend_v2.exceptions import AppException, ErrorCodes

        if isinstance(e, AppException):
            raise

        # Fail Fast Requirement
        msg = f"Normalization failed for step '{blueprint_id}': {e}"
        logger.error("[ScoringHook] %s: %s", ErrorCodes.HOOK_EXECUTION_FAILED.name, msg, exc_info=True)

        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.HOOK_EXECUTION_FAILED.value},
        ) from e

    return HookResult(success=True, state_delta={})
