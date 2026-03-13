"""Core Mathematical Utilities for the Cognitive Quorum System.

Contains deterministic calculation logic (Part 18.7 Python Authority),
prioritizing strict validation and Fail Fast principles.
"""

from backend_v2.exceptions import AppException, ErrorCodes


def normalize_score_to_100(score: float, scale_min: float, scale_max: float) -> float:
    """Normalize any score to a 0.0 - 100.0 percentage scale.

    Args:
        score: The score to normalize.
        scale_min: The minimum possible score of the original scale.
        scale_max: The maximum possible score of the original scale.

    Returns:
        float: The normalized score between 0.0 and 100.0.

    Raises:
        AppException: If scale_min >= scale_max (Invalid Scale).
    """
    if scale_min >= scale_max:
        raise AppException(
            message=f"Invalid scale definition: scale_min ({scale_min}) >= scale_max ({scale_max}).",
            status_code=500,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        )

    # Note: We do NOT clamp the original score here.
    # Validation of the original score (score < scale_min or score > scale_max)
    # is the responsibility of the JudgeScoreCard Pydantic validation (Fail Fast).
    # If a score gets here, we calculate its percentage linearly.

    # Calculate mathematical percentage based on scale_max, adhering to user's logic where 
    # a score of 2.5 out of 5 equals 50, and 5 out of 10 equals 50.
    normalized = (score / scale_max) * 100.0

    # Ensure it's between 0 and 100 (clamp just in case, though logically it should be if within bounds)
    return max(0.0, min(100.0, normalized))

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
        return target_min

    scaled = target_min + (score - raw_min) / (raw_max - raw_min) * (target_max - target_min)

    # Clamp to target bounds
    actual_min = min(target_min, target_max)
    actual_max = max(target_min, target_max)

    return max(actual_min, min(actual_max, scaled))
