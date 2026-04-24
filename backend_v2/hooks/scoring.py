"""Scoring Hook for evaluating agent performance and applying penalties."""

import logging
from typing import Any

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)


from pydantic import ValidationError

from backend_v2.models.domain.scoring import StepFalsifierDTO, StepGuardDTO, StepPanelDTO


def _extract_guard_flag(data: dict[str, Any]) -> Any | None:
    """Extracts the security threat flag from the guard output in the state.

    Args:
        data (dict): The current workflow data.

    Returns:
        Any | None: True if a security threat is detected, False otherwise, or None if guard data is missing/invalid.
    """
    guard_model = data.get("step_guard")
    if guard_model is not None:
        try:
            dto = StepGuardDTO.model_validate(guard_model)
            return dto.security_check.threat_detected
        except ValidationError as e:
            from backend_v2.exceptions import AppException, ErrorCodes

            msg = f"Strict Fail-Fast Enforced: step_guard validation failed in scoring hook: {e}"
            logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
            ) from e

    logger.debug("[ScoringHook] step_guard missing from context or no threat detected.")
    return False


def _extract_falsifier_data(data: dict[str, Any]) -> Any | None:
    """Extracts falsifier data from either step_falsifier or step_panel.

    Args:
        data (dict): The current workflow data.

    Returns:
        Any | None: The strictly typed falsifier data if found, otherwise None.
    """
    falsifier_model = data.get("step_falsifier")
    panel_model = data.get("step_panel")

    try:
        if falsifier_model is not None:
            falsifier_dto = StepFalsifierDTO.model_validate(falsifier_model)
            if falsifier_dto.falsifier_data:
                return falsifier_dto.falsifier_data

        if panel_model is not None:
            panel_dto = StepPanelDTO.model_validate(panel_model)
            if panel_dto.falsifier_data:
                return panel_dto.falsifier_data
    except ValidationError as e:
        from backend_v2.exceptions import AppException, ErrorCodes

        msg = f"Strict Fail-Fast Enforced: Falsifier data extraction failed: {e}"
        logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(
            message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
        ) from e

    return None


def _calculate_falsifier_penalty(falsifier_data: Any | None) -> bool:
    """Determines if a post-hoc rationalization penalty should be applied.

    Args:
        falsifier_data (Any | None): The strictly typed falsifier data.

    Returns:
        bool: True if post-hoc rationalization is detected, False otherwise.
    """
    if falsifier_data:
        # Access strictly typed Pydantic attributes
        if falsifier_data.fidelity_audit and falsifier_data.fidelity_audit.post_hoc_rationalization:
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
        # Epic 34: O(1) Map Pre-computation instead of dynamically looping over dictionary keys!
        eval_map = source.get("_evaluative_matrices", {})
        for block_id, norm_val in eval_map.items():
            unique_matrices[block_id] = float(norm_val)

        # Legacy fallback if O(1) map is missing (backward compatibility during migration)
        if not eval_map:
            for k, v in source.items():
                if isinstance(k, str) and k.endswith("_is_evaluative") and v is True:
                    block_id = k.replace("_is_evaluative", "")
                    norm_key = f"{block_id}_normalized"
                    if norm_key in source:
                        unique_matrices[block_id] = float(source[norm_key])
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

    from backend_v2.models.enums import ScoringCalibrationThresholds

    total_penalty_factor = 0.0

    if security_threat:
        p_val = settings.scoring_security_penalty
        if p_val > 0:
            total_penalty_factor += p_val
            pct_val = p_val * 100
            penalties.append(f"Security Threat Detected (-{pct_val:.0f}%)")
        else:
            logger.warning("[ScoringHook] Security Threat Detected (Logged Only - Penalty Disabled in Settings)")

    if is_post_hoc:
        p_val = settings.scoring_post_hoc_penalty
        if p_val > 0:
            total_penalty_factor += p_val
            pct_val = p_val * 100
            penalties.append(f"Post-Hoc Rationalization Detected (-{pct_val:.0f}%)")
        else:
            logger.warning(
                "[ScoringHook] Post-Hoc Rationalization Detected (Logged Only - Penalty Disabled in Settings)"
            )

    effective_penalty = min(total_penalty_factor, ScoringCalibrationThresholds.PENALTY_CAP.value)

    if effective_penalty > 0:
        final_score *= 1.0 - effective_penalty
        logger.warning(
            "[ScoringHook] Combined penalties applied: -%.0f%% (capped at %.0f%%).",
            effective_penalty * 100,
            ScoringCalibrationThresholds.PENALTY_CAP.value * 100,
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

        score_card = judge_model.get("score_card")

        # Strategy 1: Legacy Dimensions
        if score_card and isinstance(score_card, dict):
            if "scale_min" not in score_card:
                from backend_v2.exceptions import AppException, ErrorCodes

                msg = f"Strict Fail-Fast Enforced: Legacy score_card missing 'scale_min' in '{judge_key}'."
                logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                )

            scale_min = float(score_card["scale_min"])
            dimensions = score_card.get("dimensions")
            if not isinstance(dimensions, list):
                dimensions = []

            penalty_triggered = False

            for dim in dimensions:
                if not isinstance(dim, dict):
                    continue

                if "score" not in dim or "dimension_id" not in dim:
                    from backend_v2.exceptions import AppException, ErrorCodes

                    msg = f"Strict Fail-Fast Enforced: Dimension missing 'score' or 'dimension_id' in '{judge_key}'."
                    raise AppException(
                        message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                    )

                dim_score = float(dim["score"])
                dim_id = str(dim["dimension_id"])

                if dim_score <= scale_min:
                    penalty_triggered = True
                    logger.warning("[ScoringHook] Passive/Low Quality detected in %s dimension '%s'", judge_key, dim_id)
                    break

            if penalty_triggered:
                logger.info("[ScoringHook] Applying Passivity Penalty to %s (Factor %s).", judge_key, multiplier)

                if "total_score" not in score_card:
                    from backend_v2.exceptions import AppException, ErrorCodes

                    msg = f"Strict Fail-Fast Enforced: 'total_score' missing from score_card in '{judge_key}'."
                    raise AppException(
                        message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                    )

                current_score = float(score_card["total_score"])
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

        # Strategy 2: V2 Matrix (Strict Schema via LightweightMatrixOutput)
        else:
            penalty_triggered = False
            scale_min = 1.0  # Default BARS scale minimum

            from pydantic import ValidationError

            from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput

            matrix_keys = []
            for k, v in judge_model.items():
                if isinstance(v, dict) and "raw_score" in v and "normalized_score" in v:
                    try:
                        matrix_dto = LightweightMatrixOutput.model_validate(v)
                        matrix_keys.append((k, matrix_dto))
                    except ValidationError:
                        pass

            for k, matrix_dto in matrix_keys:
                if matrix_dto.raw_score <= scale_min:
                    penalty_triggered = True
                    logger.warning("[ScoringHook] Passive/Low Quality detected in V2 Matrix '%s'", k)
                    break

            if penalty_triggered:
                logger.info("[ScoringHook] Applying V2 Passivity Penalty to %s (Factor %s).", judge_key, multiplier)
                new_judge = judge_model.copy()

                for k, matrix_dto in matrix_keys:
                    new_score = matrix_dto.raw_score * multiplier
                    if new_score < scale_min:
                        new_score = scale_min

                    new_norm = matrix_dto.normalized_score * multiplier
                    if new_norm < 0.0:
                        new_norm = 0.0

                    justification = f"[PASSIVITY PENALTY x{multiplier:.2f}] " + matrix_dto.justification

                    new_dto = LightweightMatrixOutput(
                        raw_score=new_score,
                        normalized_score=new_norm,
                        level_breakdown=matrix_dto.level_breakdown,
                        justification=justification,
                        evaluated_atoms=matrix_dto.evaluated_atoms,
                        extensions=matrix_dto.extensions,
                    )
                    new_judge[k] = new_dto.model_dump(mode="json")

                # O(1) Map Update if using pre-computed map
                eval_map = new_judge.get("_evaluative_matrices", {})
                if eval_map:
                    for k, _ in matrix_keys:
                        if k in eval_map:
                            eval_map[k] = new_judge[k]["normalized_score"]

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


@hook_registry.register(name="waterfall_scoring_hook")
async def waterfall_scoring_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Post-Hook to calculate Hybrid Waterfall scores from blind atom evaluations."""
    logger.info("[ScoringHook] Running waterfall_scoring_hook...")

    repository = deps.repository
    if not repository:
        logger.warning("[ScoringHook] No repository provided in HookDependencies. Skipping hybrid scoring.")
        return HookResult(success=True, state_delta={})

    if not isinstance(state.inputs, dict):
        logger.debug("[ScoringHook] State inputs is not a dictionary. Skipping.")
        return HookResult(success=True, state_delta={})

    blueprint_id = state.task_blueprint or state.step_id
    if not blueprint_id:
        from backend_v2.exceptions import AppException, ErrorCodes

        msg = "Strict Fail-Fast Enforced: No blueprint_id or step_id provided to waterfall_scoring_hook."
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    try:
        step_obj = await repository.get_step_by_id(blueprint_id)
        if not step_obj:
            from backend_v2.exceptions import AppException, ErrorCodes

            msg = f"Strict Fail-Fast Enforced: Step blueprint '{blueprint_id}' not found in database."
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value}
            )

        prompt_block_ids = (
            step_obj.get("prompt_blocks", []) if isinstance(step_obj, dict) else getattr(step_obj, "prompt_blocks", [])
        )

        # Determine if this step actually contains matrix blocks
        matrix_blocks = []
        for pb_id in prompt_block_ids:
            pb_dict = await repository.get_prompt_block_by_id(pb_id)
            if pb_dict and pb_dict.get("category_id", "") == "matrix":
                matrix_blocks.append((pb_id, pb_dict))

        # If no matrix blocks exist, then waterfall scoring natively skips without demanding evaluations
        if not matrix_blocks:
            logger.debug("[ScoringHook] Step '%s' contains no matrix blocks. Skipping waterfall scoring.", blueprint_id)
            return HookResult(success=True, state_delta={})

        content_payload = state.inputs
        if "evaluations" not in content_payload:
            from backend_v2.exceptions import AppException, ErrorCodes

            msg = (
                f"Strict Fail-Fast Enforced: 'evaluations' array is completely missing from state.inputs "
                f"for step '{blueprint_id}'. Upstream atomization payload failed."
            )
            logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        evaluations = content_payload["evaluations"]

        if not isinstance(evaluations, list) or len(evaluations) == 0:
            from backend_v2.exceptions import AppException, ErrorCodes

            msg = f"Strict Fail-Fast Enforced: 'evaluations' array is empty or not a list for step '{blueprint_id}'."
            logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        import hashlib

        from backend_v2.models.enums import (
            CognitiveFlowStatus,
            CognitiveFlowThreshold,
            EvaluationMandate,
            WaterfallThreshold,
        )
        from backend_v2.utils.math_utils import (
            calculate_progressive_dampening_score,
            calculate_waterfall_floor,
            calculate_weighted_score,
        )

        atom_mapping = {}
        blocks_meta: dict[str, dict[str, Any]] = {}

        # 1. Reverse extraction of Atom Hashes
        for pb_id, pb_dict in matrix_blocks:
            scales = pb_dict.get("scales", [])
            if not scales:
                from backend_v2.exceptions import AppException, ErrorCodes

                msg = f"Strict Fail-Fast Enforced: PromptBlock '{pb_id}' has no scales."
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
                )

            blocks_meta[pb_id] = {"scales": []}

            for scale in scales:
                s_val = float(scale.get("score"))
                blocks_meta[pb_id]["scales"].append(s_val)
                claims = scale.get("claims", [])
                for claim in claims:
                    micro_atoms = claim.get("micro_atoms", [])
                    if micro_atoms:
                        mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
                        for text in micro_atoms:
                            full_text = f"{text.strip()}{mandate}"
                            atom_hash = hashlib.md5(full_text.encode("utf-8")).hexdigest()
                            atom_mapping[atom_hash] = {"block_id": pb_id, "score": s_val, "text": text}
                    else:
                        label = claim.get("label", {})
                        translations = label.get("translations", {})
                        text = translations.get("en") or translations.get(label.get("default_locale", "fi"))
                        if not text and translations:
                            text = list(translations.values())[0]
                        if not text:
                            text = claim.get("ai_description", "")

                        if text:
                            mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
                            full_text = f"{text.strip()}{mandate}"
                            atom_hash = hashlib.md5(full_text.encode("utf-8")).hexdigest()
                            atom_mapping[atom_hash] = {"block_id": pb_id, "score": s_val, "text": text}

            # Fail-fast: Ei fallbackeja. Korjattu normaalin virhehallinnan tyyliin.
            if not blocks_meta[pb_id]["scales"]:
                from backend_v2.exceptions import AppException, ErrorCodes

                msg = f"PromptBlock '{pb_id}' scales array failed to provide numeric values for waterfall bounds."
                logger.error("[ScoringHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )

            blocks_meta[pb_id]["math_min"] = min(blocks_meta[pb_id]["scales"])
            blocks_meta[pb_id]["math_max"] = max(blocks_meta[pb_id]["scales"])

        block_scale_stats: dict[str, dict[float, dict[str, int]]] = {}
        missing_atoms_by_block: dict[str, list[str]] = {}

        # 2. Iterate evaluations
        for ev in evaluations:
            # Handle both dict and Pydantic object inputs
            if isinstance(ev, dict):
                atom_id = ev.get("atom_id")
                boolean_val = ev.get("boolean", False)
                reasoning = ev.get("reasoning", "")
            else:
                atom_id = getattr(ev, "atom_id", None)
                boolean_val = getattr(ev, "boolean", False)
                reasoning = getattr(ev, "reasoning", "")

            if not atom_id:
                continue

            mapping = atom_mapping.get(atom_id)
            if not mapping:
                continue

            pb_id = mapping["block_id"]
            s_val = mapping["score"]
            text = mapping["text"]

            if pb_id not in block_scale_stats:
                block_scale_stats[pb_id] = {}
                missing_atoms_by_block[pb_id] = []

            if s_val not in block_scale_stats[pb_id]:
                block_scale_stats[pb_id][s_val] = {"hits": 0, "total": 0}

            block_scale_stats[pb_id][s_val]["total"] += 1
            if boolean_val:
                block_scale_stats[pb_id][s_val]["hits"] += 1
            else:
                if reasoning:
                    missing_atoms_by_block[pb_id].append(f"- {text} (Tuomio: {reasoning})")
                else:
                    missing_atoms_by_block[pb_id].append(f"- {text}")

        # 3. Hybrid Calculation
        new_payload = content_payload.copy()
        updates_made = False

        for pb_id, stats in block_scale_stats.items():
            meta = blocks_meta[pb_id]
            math_min = float(meta["math_min"])
            math_max = float(meta["math_max"])

            # Shadow calculations for XAI logging
            floor_score = calculate_waterfall_floor(stats, math_min, threshold=WaterfallThreshold.STANDARD.value)
            weighted_score = calculate_weighted_score(stats, math_min, math_max)

            # --- DINA Progressive Dampening Calculation ---
            # V2 Optimal Math Model: Square Root Dampening natively creates natural Gaussian variance
            # without requiring an artificial safety net floor. DINA_FLOOR is completely removed.
            dampening_score = calculate_progressive_dampening_score(stats, math_min, math_max)

            # Formatting the calculation log (Cognitive Diagnostic Model)
            log_lines = ["### Cognitive Diagnostic Model (CDM) Breakdown:"]
            sorted_levels = sorted(stats.keys())

            modifier = 1.0
            global_hits = 0
            global_total = 0

            for s_level in sorted_levels:
                level_data = stats[s_level]
                t_hits = level_data["hits"]
                t_total = level_data["total"]

                global_hits += t_hits
                global_total += t_total

                hit_rate = (t_hits / t_total) if t_total > 0 else 0.0
                pct = int(hit_rate * 100)

                if s_level == math_min:
                    modifier = hit_rate
                    log_lines.append(
                        f"- **Level {s_level}:** {t_hits}/{t_total} ({pct}% - Cognitive Flow: {modifier:.2f})"
                    )
                else:
                    if hit_rate >= CognitiveFlowThreshold.OPTIMAL.value:
                        status = CognitiveFlowStatus.OPTIMAL.value
                    elif hit_rate >= CognitiveFlowThreshold.ACCEPTABLE.value:
                        status = f"{CognitiveFlowStatus.ACCEPTABLE.value} ({hit_rate:.2f})"
                    else:
                        status = f"{CognitiveFlowStatus.WEAK.value} ({hit_rate:.2f})"

                    log_lines.append(f"- **Level {s_level}:** {t_hits}/{t_total} ({pct}% - {status})")
                    modifier = modifier * hit_rate

            log_lines.append("")
            log_lines.append("**Shadow Calculation Data:**")
            log_lines.append(f"1. *Raw Weighted Average:* {weighted_score:.2f} (Linear hits)")
            log_lines.append(f"2. *Legacy Waterfall Floor:* {floor_score:.1f} (Cutoff point)")

            diff = weighted_score - dampening_score
            if diff > CognitiveFlowThreshold.SIGNIFICANT_DROP_DIFF.value:
                log_lines.append(
                    f"-> Deficiencies in foundation credibility dampen the final score significantly (-{diff:.2f})."
                )

            log_lines.append(f"**Final CDM Score:** {dampening_score:.2f}")

            calculation_log = "\n".join(log_lines)

            # Epic 24: Tasokohtainen erittely scorecardia varten (JSON-yhteensopivat string-avaimet)
            level_breakdown = {str(k): {"hits": v["hits"], "total": v["total"]} for k, v in stats.items()}

            # Inject to new payload so normalize_matrix_scores_hook can scale it further
            existing_val = new_payload.get(pb_id)
            if isinstance(existing_val, dict):
                # Enforce hybrid scoring update inside the existing Micro-CoT dictionary
                new_payload[pb_id] = existing_val.copy()
                new_payload[pb_id]["step_4_final_score"] = float(dampening_score)
                new_payload[pb_id]["waterfall_calculation_log"] = calculation_log
                new_payload[pb_id]["true_atoms"] = global_hits
                new_payload[pb_id]["false_atoms"] = global_total - global_hits
                new_payload[pb_id]["total_atoms"] = global_total
                new_payload[pb_id]["level_breakdown"] = level_breakdown
            else:
                new_payload[pb_id] = float(dampening_score)
                new_payload[f"{pb_id}_justification"] = calculation_log
                new_payload[f"{pb_id}_true_atoms"] = global_hits
                new_payload[f"{pb_id}_false_atoms"] = global_total - global_hits
                new_payload[f"{pb_id}_total_atoms"] = global_total
                new_payload[f"{pb_id}_level_breakdown"] = level_breakdown

            # Use extending logic to append without overwriting previous UI texts
            if missing_atoms_by_block[pb_id]:
                new_payload[f"{pb_id}_missing_context"] = "\n".join(missing_atoms_by_block[pb_id])

            updates_made = True

        if updates_made:
            return HookResult(success=True, state_delta=new_payload)

    except Exception as e:
        from backend_v2.exceptions import AppException, ErrorCodes

        if isinstance(e, AppException):
            raise
        msg = f"Hybrid waterfall scoring failed for step '{blueprint_id}': {e}"
        logger.error("[ScoringHook] %s: %s", ErrorCodes.HOOK_EXECUTION_FAILED.name, msg, exc_info=True)
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.HOOK_EXECUTION_FAILED.value},
        ) from e

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
        from backend_v2.exceptions import AppException, ErrorCodes

        msg = "Strict Fail-Fast Enforced: No blueprint_id or step_id found in execution context for normalization."
        logger.error("[ScoringHook] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    try:
        step_obj = await repository.get_step_by_id(blueprint_id)
        if not step_obj:
            from backend_v2.exceptions import AppException, ErrorCodes

            msg = f"Strict Fail-Fast Enforced: Step blueprint '{blueprint_id}' not found in registry."
            logger.error("[ScoringHook] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value}
            )

        prompt_block_ids = (
            step_obj.get("prompt_blocks", []) if isinstance(step_obj, dict) else getattr(step_obj, "prompt_blocks", [])
        )

        updates_made = False
        new_payload = content_payload.copy()

        eval_map = new_payload.get("_evaluative_matrices", {})

        for pb_id in prompt_block_ids:
            if pb_id not in new_payload:
                continue

            # Epic 12: Micro-CoT Nested Dictionary Support && XAI Mapping
            raw_input_val = new_payload[pb_id]

            import json

            from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
            from backend_v2.models.enums import XaiExtensionType

            extensions: dict[XaiExtensionType, str] = {}
            justification = ""
            level_breakdown: dict[str, Any] = {}
            evaluated_atoms: dict[str, bool] = {}

            if isinstance(raw_input_val, dict):
                # Strict Schema Mapping for XAI attributes!
                if "step_1_evidence_quote" in raw_input_val:
                    extensions[XaiExtensionType.CITATION] = str(raw_input_val["step_1_evidence_quote"])
                    # Legacy UI mapping requirement
                    new_payload[f"{pb_id}_cited_text_quote"] = raw_input_val["step_1_evidence_quote"]
                if "step_1b_cited_source_id" in raw_input_val:
                    extensions[XaiExtensionType.SOURCE_ID] = str(raw_input_val["step_1b_cited_source_id"])
                    # Legacy UI mapping requirement
                    new_payload[f"{pb_id}_cited_source_id"] = raw_input_val["step_1b_cited_source_id"]
                if "step_2_falsification" in raw_input_val:
                    extensions[XaiExtensionType.FALSIFICATION] = str(raw_input_val["step_2_falsification"])
                    new_payload[f"{pb_id}_falsification"] = raw_input_val["step_2_falsification"]
                if "extension_coaching" in raw_input_val:
                    extensions[XaiExtensionType.COACHING] = str(raw_input_val["extension_coaching"])
                    new_payload[f"{pb_id}_coaching"] = raw_input_val["extension_coaching"]
                if "extension_theory_link" in raw_input_val:
                    extensions[XaiExtensionType.THEORY_LINK] = str(raw_input_val["extension_theory_link"])
                    new_payload[f"{pb_id}_theory_link"] = raw_input_val["extension_theory_link"]
                if "extension_emotional_sentiment" in raw_input_val:
                    extensions[XaiExtensionType.EMOTIONAL_SENTIMENT] = str(
                        raw_input_val["extension_emotional_sentiment"]
                    )
                    new_payload[f"{pb_id}_emotional_sentiment"] = raw_input_val["extension_emotional_sentiment"]
                if "extension_remediation_steps" in raw_input_val:
                    extensions[XaiExtensionType.REMEDIATION_STEPS] = str(raw_input_val["extension_remediation_steps"])
                    new_payload[f"{pb_id}_remediation_steps"] = raw_input_val["extension_remediation_steps"]

                for metric in ["true_atoms", "false_atoms", "total_atoms"]:
                    if metric in raw_input_val:
                        new_payload[f"{pb_id}_{metric}"] = raw_input_val[metric]

                if "level_breakdown" in raw_input_val:
                    level_breakdown = raw_input_val["level_breakdown"]
                    new_payload[f"{pb_id}_level_breakdown"] = level_breakdown

                # The core reasoning and notes replace the global fallback, avoiding hardcoded markdown
                just_parts = []
                if "evaluation_notes" in raw_input_val and raw_input_val["evaluation_notes"]:
                    just_parts.append(str(raw_input_val["evaluation_notes"]))
                if "step_3_logical_friction" in raw_input_val and raw_input_val["step_3_logical_friction"]:
                    just_parts.append(str(raw_input_val["step_3_logical_friction"]))

                if just_parts:
                    existing_just = new_payload.get(f"{pb_id}_justification", "")
                    if existing_just:
                        justification = existing_just + "\n\n---\n\n" + "\n\n".join(just_parts)
                    else:
                        justification = "\n\n".join(just_parts)
                    updates_made = True

                # Keep text as text, numbers as numbers (Tapa 1 vs Tapa 2)
                if "step_4_final_score" in raw_input_val:
                    # Tapa 1: Extract numeric score and continue to scale logic
                    raw_input_val = raw_input_val["step_4_final_score"]
                else:
                    # Tapa 2: String-only block. Ensure justification is mapped back for UI.
                    if justification:
                        new_payload[f"{pb_id}_justification"] = justification
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
                from backend_v2.exceptions import AppException, ErrorCodes

                msg = f"Strict Fail-Fast Enforced: Missing PromptBlock '{pb_id}' during score normalization."
                logger.error("[ScoringHook] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value}
                )

            pb_dict = pb if isinstance(pb, dict) else pb.model_dump()
            logger.debug(
                "[ScoringHook] Found PromptBlock '%s' with allowed decimals: %s",
                pb_id,
                pb_dict.get("allow_decimals"),
            )

            scales = pb_dict.get("scales")

            # FAIL-FAST: The scales array MUST dictate the internal math boundaries.
            if not scales:
                from backend_v2.exceptions import AppException, ErrorCodes

                msg = f"Strict Fail-Fast Enforced: PromptBlock '{pb_id}' missing 'scales' array."
                logger.error("[ScoringHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
                )

            # DISPLAY BOUNDARIES: UI projection targets
            display_min = pb_dict.get("scale_min")
            display_max = pb_dict.get("scale_max")

            if display_min is None or display_max is None:
                from backend_v2.exceptions import AppException, ErrorCodes

                msg = (
                    f"Strict Fail-Fast Enforced: PromptBlock '{pb_id}' missing explicit display "
                    "'scale_min' or 'scale_max' in database. Fallback estimates are forbidden."
                )
                logger.error("[ScoringHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
                )

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

            if not scores_in_scales:
                continue

            from backend_v2.utils.math_utils import normalize_score_to_100, scale_to_custom_range

            # 1. The original AI output, calculated on the internal Math bounds
            raw_float = float(raw_val)

            math_min = min(scores_in_scales)
            math_max = max(scores_in_scales)

            # 2. Scale mathematically to custom Output Target Range (DB scale_min/scale_max explicitly for DISPLAY)
            scaled_val = scale_to_custom_range(
                score=raw_float,
                raw_min=math_min,
                raw_max=math_max,
                target_min=float(display_min),
                target_max=float(display_max),
            )

            # 3. The 1-100 normalized value for commensurable aggregation (V2 Logic)
            normalized_val = normalize_score_to_100(
                score=raw_float,
                math_min=math_min,
                math_max=math_max,
            )

            # Strip out the ||DECIMAL: X.Y|| Chain-of-Thought tag from justification
            # before saving (Legacy V1 Support)
            import re

            cleaned_just = re.sub(r"\|\|DECIMAL:\s*[0-9.]+\|\|", "", justification)
            justification = cleaned_just.strip()

            # Replace legacy flattening with strict schema mapping!
            matrix_dto = LightweightMatrixOutput(
                raw_score=raw_float,
                normalized_score=normalized_val,
                level_breakdown=json.dumps(level_breakdown) if level_breakdown else "",
                justification=justification,
                evaluated_atoms=evaluated_atoms,
                extensions=extensions,
            )

            new_payload[pb_id] = matrix_dto.model_dump(mode="json")

            # Epic 10 & 34: Check the DB truth for Evaluative Matrix status and inject to O(1) Map
            if pb_dict.get("is_evaluative", True):
                eval_map[pb_id] = normalized_val

            new_payload["_evaluative_matrices"] = eval_map

            # UI Traceability Fallback (Keep explicitly required fields)
            new_payload[f"{pb_id}_justification"] = justification

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
