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

    normalized = (score - scale_min) / (scale_max - scale_min) * 100.0

    # We clamp the normalisation to 0-100 just in case floating point inaccuracies
    # or passivity penalties cause minor out-of-bounds results,
    # but the primary validation happens upstream.
    return max(0.0, min(100.0, normalized))
