"""Mechanical-Cognitive Variance Engine.

Determines mathematical alignment between mechanical anchors and cognitive evaluations
to detect sycophancy or automated automation bias, enforcing strict mathematical bounds.
"""

import logging
import math

from fastapi import status

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.variance import VarianceEngineResultDTO
from backend_v2.models.enums import AlignmentVerdict
from backend_v2.settings import get_settings

__all__ = ["calculate_mechanical_cognitive_variance"]

logger = logging.getLogger(__name__)


def calculate_mechanical_cognitive_variance(
    llm_authenticity_score: float,
    performative_phrases_count: int,
    total_word_count: int | None = None,
) -> VarianceEngineResultDTO:
    """Calculate the absolute variance between mechanical linguistics and cognitive assessment.

    Args:
        llm_authenticity_score: Authenticity score given by the cognitive agent (1.0 to 3.0).
        performative_phrases_count: Number of performative filler phrases detected mechanically.
        total_word_count: Total word count of scanned text for length-invariant density calculation.

    Returns:
        A VarianceEngineResultDTO containing:
            - mechanical_metric_ref: Reference to the mechanical key.
            - cognitive_metric_ref: Reference to the cognitive key.
            - variance_score: The absolute difference.
            - alignment_verdict: AlignmentVerdict enum value (ALIGNED, MISALIGNED_SYCOPHANCY, or MISALIGNED).

    Raises:
        AppException: If parameters fail structural or validation constraints.
    """
    if (
        isinstance(performative_phrases_count, bool)
        or not isinstance(performative_phrases_count, int)
        or performative_phrases_count < 0
    ):
        logger.error(
            "Validation failed for performative_phrases_count: must be a non-negative integer",
            exc_info=True,
        )
        raise AppException(
            message="performative_phrases_count must be a non-negative integer.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    if total_word_count is not None and (
        isinstance(total_word_count, bool) or not isinstance(total_word_count, int) or total_word_count < 0
    ):
        logger.error(
            "Validation failed for total_word_count: must be a non-negative integer or None",
            exc_info=True,
        )
        raise AppException(
            message="total_word_count must be a non-negative integer or None.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    if isinstance(llm_authenticity_score, bool) or not isinstance(llm_authenticity_score, (int, float)):
        logger.error(
            "Validation failed for llm_authenticity_score: must be a float or int",
            exc_info=True,
        )
        raise AppException(
            message="llm_authenticity_score must be a float or int.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    if math.isnan(llm_authenticity_score) or math.isinf(llm_authenticity_score):
        logger.error(
            "Validation failed for llm_authenticity_score: invalid mathematical value (%s)",
            llm_authenticity_score,
            exc_info=True,
        )
        raise AppException(
            message="llm_authenticity_score cannot be NaN or Infinity.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    settings = get_settings()

    if total_word_count is not None and total_word_count > 0:
        jargon_density = (performative_phrases_count / max(1, total_word_count)) * 100.0
        normalized_performative_count = min(
            (jargon_density / settings.variance_jargon_density_normalizer) * settings.variance_max_performative_cap,
            settings.variance_max_performative_cap,
        )
    else:
        # MIGRATION BRIDGE: Raw count fallback for backward compatibility when total_word_count is omitted
        normalized_performative_count = min(
            (performative_phrases_count / settings.variance_performative_normalizer)
            * settings.variance_max_performative_cap,
            settings.variance_max_performative_cap,
        )

    # Dampener target value
    target_cognitive_dampener = settings.variance_max_cognitive_score - normalized_performative_count

    # Absolute variance
    variance = abs(llm_authenticity_score - target_cognitive_dampener)

    # Alignment verdict logic matching UI localization parity
    if variance < settings.variance_threshold_misaligned:
        verdict = AlignmentVerdict.ALIGNED
    elif variance >= settings.variance_threshold_misaligned and llm_authenticity_score > target_cognitive_dampener:
        verdict = AlignmentVerdict.MISALIGNED_SYCOPHANCY
    else:
        verdict = AlignmentVerdict.MISALIGNED

    logger.info(
        "Calculated mechanical-cognitive variance: score=%s, count=%s, words=%s, variance=%s, verdict=%s",
        llm_authenticity_score,
        performative_phrases_count,
        total_word_count,
        round(variance, 4),
        verdict.value,
    )

    return VarianceEngineResultDTO(
        mechanical_metric_ref="performative_phrases_count",
        cognitive_metric_ref="llm_authenticity_score",
        variance_score=round(variance, 4),
        alignment_verdict=verdict,
    )
