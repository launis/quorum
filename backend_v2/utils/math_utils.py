"""Core Mathematical Utilities for the Cognitive Quorum System.

Contains deterministic calculation logic (Part 18.7 Python Authority),
prioritizing strict validation and Fail Fast principles.
"""

import logging

from pydantic import BaseModel, ConfigDict, Field

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.enums import StrictnessAnchor, WaterfallThreshold

logger = logging.getLogger(__name__)

class StrictnessConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    base_forgiveness: float = Field(ge=0.0, le=1.0)
    sigmoid_midpoint: float = Field(ge=0.0, le=1.0)
    dynamic_exponent: float = Field(ge=0.2, le=3.0)

STRICTNESS_ANCHOR_CONFIGS = {
    StrictnessAnchor.FLEXIBLE: StrictnessConfig(base_forgiveness=1.0, sigmoid_midpoint=0.1, dynamic_exponent=0.2),
    StrictnessAnchor.LENIENT: StrictnessConfig(base_forgiveness=0.60, sigmoid_midpoint=0.3, dynamic_exponent=0.3),
    StrictnessAnchor.BALANCED: StrictnessConfig(base_forgiveness=0.30, sigmoid_midpoint=0.5, dynamic_exponent=0.5),
    StrictnessAnchor.STRICT: StrictnessConfig(base_forgiveness=0.10, sigmoid_midpoint=0.7, dynamic_exponent=1.5),
    StrictnessAnchor.ABSOLUTE: StrictnessConfig(base_forgiveness=0.00, sigmoid_midpoint=0.9, dynamic_exponent=3.0),
}

def get_strictness_config(strictness_level: int) -> StrictnessConfig:
    """Hakee joko suoran ankkurin tai laskee tarkan Linear Interpolationin ankkurien väliltä."""
    level = max(0, min(100, strictness_level))
    
    if level in STRICTNESS_ANCHOR_CONFIGS:
        return STRICTNESS_ANCHOR_CONFIGS[level]
        
    anchors = sorted(STRICTNESS_ANCHOR_CONFIGS.keys())
    lower_anchor = max([a for a in anchors if a < level])
    upper_anchor = min([a for a in anchors if a > level])
    
    lower_cfg = STRICTNESS_ANCHOR_CONFIGS[lower_anchor]
    upper_cfg = STRICTNESS_ANCHOR_CONFIGS[upper_anchor]
    
    t = (level - lower_anchor) / (upper_anchor - lower_anchor)
    
    def lerp(start: float, end: float, t: float) -> float:
        return start + (end - start) * t
        
    return StrictnessConfig(
        base_forgiveness=lerp(lower_cfg.base_forgiveness, upper_cfg.base_forgiveness, t),
        sigmoid_midpoint=lerp(lower_cfg.sigmoid_midpoint, upper_cfg.sigmoid_midpoint, t),
        dynamic_exponent=lerp(lower_cfg.dynamic_exponent, upper_cfg.dynamic_exponent, t)
    )

def clamp_score(score: float, math_min: float, math_max: float) -> float:
    """Ensure the score is strictly within the mathematical bounds."""
    if math_min >= math_max:
        msg = f"Invalid bounds for clamping: min ({math_min}) >= max ({math_max})."
        logger.error("[MathUtils] %s: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, msg)
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        )
    return float(max(math_min, min(math_max, score)))


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
    """(DEPRECATED) Käytä get_strictness_config() suoraan. Jätetty vanhojen moottorien tueksi.
    Convert UI strictness level (0-100) to a forgiveness multiplier (0.0 - 1.0).
    """
    return get_strictness_config(strictness_level).base_forgiveness


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
    level_stats: dict[float, dict[str, int]], scale_min: float, scale_max: float, strictness_config: StrictnessConfig
) -> float:
    """Calculate the CDM (Cognitive Diagnostic Model) / DINA score using Progressive Dampening.

    Instead of a hard threshold floor, each level acts as a modifier (amplifier/dampener)
    for the subsequent levels. A low hit rate on foundational levels structurally
    limits the achievable score from higher levels.

    Args:
        level_stats: Dictionary mapping scale_level -> {"hits": X, "total": Y}
        scale_min: The minimum value of the scale.
        scale_max: The maximum value of the scale.
        strictness_config: StrictnessConfig derived from UI strictness level.

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

    achieved_score = float(scale_min)
    modifier = 1.0
    prev_level = float(scale_min)

    sorted_levels = sorted(level_stats.keys())
    
    safe_exponent = max(0.2, min(3.0, strictness_config.dynamic_exponent))

    for level in sorted_levels:
        stats = level_stats[level]
        total = stats.get("total", 0)
        hits = stats.get("hits", 0)

        hit_rate = (hits / total) if total > 0 else 0.0
        
        # 1. Lerp instead of max
        effective_hit_rate = strictness_config.base_forgiveness + (hit_rate * (1.0 - strictness_config.base_forgiveness))
        if effective_hit_rate <= 0.0:
            effective_hit_rate = 0.0

        try:
            modifier_factor = effective_hit_rate ** safe_exponent
        except (ValueError, OverflowError, ZeroDivisionError) as e:
            logger.error("Math error in progressive dampening score: %s", e)
            modifier_factor = 0.0

        if level == scale_min:
            # Foundation level sets the initial current flow (modifier) with dynamic exponent
            modifier = modifier_factor
        else:
            # How much points this level represents
            step_value = level - prev_level

            # The achieved points are dampened by the upstream modifier
            achieved_score += step_value * hit_rate * modifier

            # The modifier is progressively dampened
            modifier = modifier * modifier_factor

        prev_level = level

    return clamp_score(achieved_score, scale_min, scale_max)

