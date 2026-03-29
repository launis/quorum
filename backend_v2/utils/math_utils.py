"""Core Mathematical Utilities for the Cognitive Quorum System.

Contains deterministic calculation logic (Part 18.7 Python Authority),
prioritizing strict validation and Fail Fast principles.
"""

import logging

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)


def normalize_score_to_100(score: float, number_of_options: int) -> float:
    """Normalize any score to a proportional 0.0 - 100.0 percentage scale
    according to V2 proportional step logic.

    Args:
        score: The score to normalize (fractional value out of possible values).
        number_of_options: The total number of valid score choices (e.g. 4 for 1-4).

    Returns:
        float: The normalized proportional score between 0.0 and 100.0.
    """
    # 1. Calculate relative proportion of the full range: (Arvon mahdollisuuksia / X)
    # Suhteellinen osuus täydestä = score / maksimimäärä valintoja
    if number_of_options <= 0:
        msg = f"Invalid number_of_options ({number_of_options}). Must be > 0."
        logger.error("[MathUtils] %s: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, msg)
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        )

    proportional_fraction = score / number_of_options

    # 2. Normalize to 0-100: suhteellinen osuus täydestä * 100
    normalized = proportional_fraction * 100.0

    # Ensure it's between 0 and 100
    return max(0.0, min(100.0, normalized))


def calculate_scaled_score(score: float, number_of_options: int, scale_min: float, scale_max: float) -> float:
    """Calculate the absolute scaled position mathematically.

    Formula based on user V2 spec:
    scaled = scale_min + ((score / options) * (scale_max - scale_min))
    """
    if scale_min >= scale_max:
        msg = f"Invalid scale definition: scale_min ({scale_min}) >= scale_max ({scale_max})."
        logger.error("[MathUtils] %s: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, msg)
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        )

    if number_of_options <= 0:
        msg = f"Invalid number_of_options ({number_of_options}). Must be > 0."
        logger.error("[MathUtils] %s: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, msg)
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        )

    scale_gap = scale_max - scale_min
    proportional_fraction = score / number_of_options

    proportional_gap = proportional_fraction * scale_gap

    scaled_val = scale_min + proportional_gap
    return max(scale_min, min(scale_max, scaled_val))


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
