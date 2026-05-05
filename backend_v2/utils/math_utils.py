"""Core Mathematical Utilities for the Cognitive Quorum System.

Contains deterministic calculation logic (Part 18.7 Python Authority),
prioritizing strict validation and Fail Fast principles.
"""

import logging

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.enums import WaterfallThreshold

logger = logging.getLogger(__name__)


def normalize_score_to_100(score: float, math_min: float, math_max: float) -> float:
    """Normalize any score to a proportional 0.0 - 100.0 percentage scale
    according to absolute mathematical bounds.

    Args:
        score: The score to normalize (computed value).
        math_min: The minimum possible score in the calculation matrix.
        math_max: The maximum possible score in the calculation matrix.

    Returns:
        float: The normalized proportional score between 0.0 and 100.0.
    """
    if math_min >= math_max:
        msg = f"Invalid bounds for normalization: min ({math_min}) >= max ({math_max})."
        logger.error("[MathUtils] %s: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, msg)
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        )

    proportional_fraction = (score - math_min) / (math_max - math_min)
    normalized = proportional_fraction * 100.0

    return max(0.0, min(100.0, normalized))


def calculate_scaled_score(score: float, number_of_options: int, scale_min: float, scale_max: float) -> float:
    """Calculate the absolute scaled position mathematically from raw output to configured scale."""
    if scale_min >= scale_max:
        msg = f"Invalid scale definition: scale_min ({scale_min}) >= scale_max ({scale_max})."
        logger.error("[MathUtils] %s: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, msg)
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        )

    # In V2, the score is mathematically ALREADY expected to be on the `scale_min` to `scale_max` scale!
    # Especially if it comes from waterfall_scoring_hook.
    # Therefore, we simply clamp it into bounds.
    return float(max(scale_min, min(scale_max, score)))


def scale_to_custom_range(score: float, raw_min: float, raw_max: float, target_min: float, target_max: float) -> float:
    """Scale a score from a raw range to a custom target range linearly.

    Args:
        score: The score to scale.
        raw_min: The minimum possible score of the original scale.
        raw_max: The maximum possible score of the original scale.
        target_min: The minimum value of the desired target scale (e.g. 4.0).
        target_max: The maximum value of the desired target scale (e.g. 10.0).

    Returns:
        float: The proportionally scaled score.
    """
    if raw_min >= raw_max:
        msg = f"Invalid raw scale definition: raw_min ({raw_min}) >= raw_max ({raw_max})."
        logger.error("[MathUtils] %s: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, msg)
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        )

    scaled = target_min + (score - raw_min) / (raw_max - raw_min) * (target_max - target_min)

    # Clamp to target bounds
    actual_min = min(target_min, target_max)
    actual_max = max(target_min, target_max)

    return max(actual_min, min(actual_max, scaled))


def convert_strictness_to_forgiveness(strictness_level: int) -> float:
    """Convert UI strictness level (0-100) to a forgiveness multiplier (0.0 - 1.0).

    0 (Täysi joustavuus): 1.0
    15 (Salliva): 0.60
    50 (Tasapainoinen): 0.30
    85 (Tiukka): 0.10
    100 (Ehdottomuus): 0.00
    """
    if strictness_level <= 0:
        return 1.0
    elif strictness_level <= 15:
        return 1.0 - ((strictness_level - 0) / 15.0) * (1.0 - 0.60)
    elif strictness_level <= 50:
        return 0.60 - ((strictness_level - 15) / 35.0) * (0.60 - 0.30)
    elif strictness_level <= 85:
        return 0.30 - ((strictness_level - 50) / 35.0) * (0.30 - 0.10)
    elif strictness_level < 100:
        return 0.10 - ((strictness_level - 85) / 15.0) * (0.10 - 0.00)
    else:
        return 0.00


def calculate_soft_waterfall_score(
    level_stats: dict[float, dict[str, int]],
    scale_min: float,
    scale_max: float,
    threshold: float = WaterfallThreshold.STANDARD.value,
    base_forgiveness: float = 0.0,
) -> float:
    """Calculate a soft waterfall score (Benefit of the Doubt).

    Instead of completely halting at the first failure, a failure reduces the value
    of all subsequent higher levels based on a penalty multiplier directly derived
    from base_forgiveness.

    Args:
        level_stats: Dictionary mapping scale_level -> {"hits": X, "total": Y}
        scale_min: The minimum floor.
        scale_max: The maximum ceiling.
        threshold: The passage fraction (default 0.75).
        base_forgiveness: The joustokerroin (0.0 - 1.0) defining how much of the remaining points pass through.

    Returns:
        float: The calculated soft waterfall score.
    """
    if scale_min >= scale_max:
        msg = f"Invalid scale definition: scale_min ({scale_min}) >= scale_max ({scale_max})."
        logger.error("[MathUtils] %s: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, msg)
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        )

    achieved_score = float(scale_min)
    current_multiplier = 1.0
    prev_level = float(scale_min)

    sorted_levels = sorted(level_stats.keys())
    for level in sorted_levels:
        stats = level_stats[level]
        total = stats.get("total", 0)
        hits = stats.get("hits", 0)

        hit_rate = (hits / total) if total > 0 else 0.0
        step_value = level - prev_level

        if hit_rate >= threshold:
            achieved_score += step_value * current_multiplier
        else:
            achieved_score += step_value * hit_rate * current_multiplier
            current_multiplier *= base_forgiveness

        prev_level = level

    return float(max(scale_min, min(scale_max, achieved_score)))


def calculate_weighted_score(
    level_stats: dict[float, dict[str, int]], scale_min: float, scale_max: float, exponent: float = 1.0
) -> float:
    """Calculate the global weighted average of all matrix atoms.

    Score is mapped proportionally to the scale based on the absolute ratio of achieved
    weighted points versus the maximum possible weighted points. An exponent can be applied
    for non-linear curve scaling based on strictness.

    Args:
        level_stats: Dictionary mapping scale_level -> {"hits": X, "total": Y}
        scale_min: The minimum value of the scale (e.g. 1.0).
        scale_max: The maximum value of the scale (e.g. 5.0).
        exponent: Non-linear exponent to apply to the proportional fraction.

    Returns:
        float: The exact weighted score.
    """
    if scale_min >= scale_max:
        msg = f"Invalid scale definition: scale_min ({scale_min}) >= scale_max ({scale_max})."
        logger.error("[MathUtils] %s: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, msg)
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        )

    achieved_weights = 0.0
    max_weights = 0.0

    for level, stats in level_stats.items():
        total = stats.get("total", 0)
        hits = stats.get("hits", 0)

        # Painotettu matematiikka
        achieved_weights += hits * level
        max_weights += total * level

    if max_weights <= 0:
        return float(scale_min)

    proportional_fraction = achieved_weights / max_weights
    proportional_fraction = proportional_fraction ** exponent
    scaled_val = scale_min + (proportional_fraction * (scale_max - scale_min))

    return float(max(scale_min, min(scale_max, scaled_val)))


def calculate_progressive_dampening_score(
    level_stats: dict[float, dict[str, int]], scale_min: float, scale_max: float, base_forgiveness: float = 0.0
) -> float:
    """Calculate the CDM (Cognitive Diagnostic Model) / DINA score using Progressive Dampening.

    Instead of a hard threshold floor, each level acts as a modifier (amplifier/dampener)
    for the subsequent levels. A low hit rate on foundational levels structurally
    limits the achievable score from higher levels.

    Args:
        level_stats: Dictionary mapping scale_level -> {"hits": X, "total": Y}
        scale_min: The minimum value of the scale.
        scale_max: The maximum value of the scale.
        base_forgiveness: Base forgiveness derived from strictness level.

    Returns:
        float: The progressive dampening score clamped to scale bounds.
    """
    if scale_min >= scale_max:
        msg = f"Invalid scale definition: scale_min ({scale_min}) >= scale_max ({scale_max})."
        logger.error("[MathUtils] %s: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, msg)
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        )

    import math

    achieved_score = float(scale_min)
    modifier = 1.0
    prev_level = float(scale_min)

    sorted_levels = sorted(level_stats.keys())

    for level in sorted_levels:
        stats = level_stats[level]
        total = stats.get("total", 0)
        hits = stats.get("hits", 0)

        hit_rate = (hits / total) if total > 0 else 0.0
        effective_hit_rate = max(hit_rate, base_forgiveness)

        if level == scale_min:
            # Foundation level sets the initial current flow (modifier) with Square Root softness
            modifier = math.sqrt(effective_hit_rate)
        else:
            # How much points this level represents
            step_value = level - prev_level

            # The achieved points are dampened by the upstream modifier
            achieved_score += step_value * hit_rate * modifier

            # The modifier is progressively dampened using Square Root to prevent absolute cliff-drop
            modifier = modifier * math.sqrt(effective_hit_rate)

        prev_level = level

    return float(max(scale_min, min(scale_max, achieved_score)))
