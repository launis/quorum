"""Mechanical-Cognitive Variance Engine.

Determines mathematical alignment between mechanical anchors and cognitive evaluations
to detect sycophancy or automated automation bias, enforcing strict mathematical bounds.
"""

import logging

logger = logging.getLogger(__name__)


def calculate_mechanical_cognitive_variance(
    llm_authenticity_score: float,
    performative_phrases_count: int,
) -> dict[str, str | float]:
    """Calculate the absolute variance between the mechanical linguistics score and cognitive assessment.

    Args:
        llm_authenticity_score: Authenticity score given by the cognitive agent (1.0 to 3.0).
        performative_phrases_count: Number of performative filler phrases detected mechanically.

    Returns:
        A dictionary containing:
            - mechanical_metric_ref: Reference to the mechanical key.
            - cognitive_metric_ref: Reference to the cognitive key.
            - variance_score: The absolute difference.
            - alignment_verdict: "ALIGNED", "MISALIGNED_SYCOPHANCY", or "MISALIGNED".
    """
    if not isinstance(performative_phrases_count, int) or performative_phrases_count < 0:
        raise ValueError("performative_phrases_count must be a non-negative integer.")

    if not isinstance(llm_authenticity_score, (int, float)):
        raise ValueError("llm_authenticity_score must be a float or int.")

    # Normalization mapping count from 0-10+ to 0.0-2.0 scale
    normalized_performative_count = min((performative_phrases_count / 10.0) * 2.0, 2.0)

    # Dampener target value
    target_cognitive_dampener = 3.0 - normalized_performative_count

    # Absolute variance
    variance = abs(llm_authenticity_score - target_cognitive_dampener)

    # Alignment verdict logic
    if variance < 0.5:
        verdict = "ALIGNED"
    elif variance >= 0.5 and llm_authenticity_score > target_cognitive_dampener:
        verdict = "MISALIGNED_SYCOPHANCY"
    else:
        verdict = "MISALIGNED"

    logger.info(
        "Calculated mechanical-cognitive variance: score=%s, count=%s, variance=%s, verdict=%s",
        llm_authenticity_score,
        performative_phrases_count,
        round(variance, 4),
        verdict,
    )

    return {
        "mechanical_metric_ref": "performative_phrases_count",
        "cognitive_metric_ref": "llm_authenticity_score",
        "variance_score": round(variance, 4),
        "alignment_verdict": verdict,
    }
