"""Unit tests for the Mechanical-Cognitive Variance Engine."""

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.enums import AlignmentVerdict
from backend_v2.utils.scoring.variance_engine import calculate_mechanical_cognitive_variance


def test_calculate_mechanical_cognitive_variance_validation() -> None:
    """Verify that type and value validation raises appropriate AppException."""
    # Test invalid performative_phrases_count negative value
    with pytest.raises(AppException, match="performative_phrases_count must be a non-negative integer."):
        calculate_mechanical_cognitive_variance(llm_authenticity_score=2.0, performative_phrases_count=-1)

    # Test invalid performative_phrases_count string type
    with pytest.raises(AppException, match="performative_phrases_count must be a non-negative integer."):
        calculate_mechanical_cognitive_variance(llm_authenticity_score=2.0, performative_phrases_count="5")  # type: ignore[arg-type]

    # Test invalid performative_phrases_count boolean type
    with pytest.raises(AppException, match="performative_phrases_count must be a non-negative integer."):
        calculate_mechanical_cognitive_variance(llm_authenticity_score=2.0, performative_phrases_count=True)  # type: ignore[arg-type]

    # Test invalid llm_authenticity_score string type
    with pytest.raises(AppException, match="llm_authenticity_score must be a float or int."):
        calculate_mechanical_cognitive_variance(llm_authenticity_score="2.0", performative_phrases_count=5)  # type: ignore[arg-type]

    # Test invalid llm_authenticity_score boolean type
    with pytest.raises(AppException, match="llm_authenticity_score must be a float or int."):
        calculate_mechanical_cognitive_variance(llm_authenticity_score=True, performative_phrases_count=5)  # type: ignore[arg-type]


def test_calculate_mechanical_cognitive_variance_nan_infinity_validation() -> None:
    """ISTQB negative partition tests: Verify NaN, +Infinity, and -Infinity trigger AppException."""
    with pytest.raises(AppException, match="llm_authenticity_score cannot be NaN or Infinity."):
        calculate_mechanical_cognitive_variance(llm_authenticity_score=float("nan"), performative_phrases_count=0)

    with pytest.raises(AppException, match="llm_authenticity_score cannot be NaN or Infinity."):
        calculate_mechanical_cognitive_variance(llm_authenticity_score=float("inf"), performative_phrases_count=0)

    with pytest.raises(AppException, match="llm_authenticity_score cannot be NaN or Infinity."):
        calculate_mechanical_cognitive_variance(llm_authenticity_score=float("-inf"), performative_phrases_count=0)


def test_calculate_mechanical_cognitive_variance_aligned() -> None:
    """Verify alignment verdict is ALIGNED when variance is within limits."""
    # 0 performative count -> target_cognitive_dampener = 3.0
    # LLM score 3.0 -> variance = 0.0 -> ALIGNED
    result = calculate_mechanical_cognitive_variance(llm_authenticity_score=3.0, performative_phrases_count=0)
    assert result.alignment_verdict == AlignmentVerdict.ALIGNED
    assert result.variance_score == 0.0
    assert result.mechanical_metric_ref == "performative_phrases_count"
    assert result.cognitive_metric_ref == "llm_authenticity_score"

    # Variance < 0.5 (e.g. variance = 0.4) -> ALIGNED
    # 5 performative count -> normalized_performative_count = 1.0 -> target_cognitive_dampener = 2.0
    # LLM score 2.4 -> variance = 0.4 -> ALIGNED
    result = calculate_mechanical_cognitive_variance(llm_authenticity_score=2.4, performative_phrases_count=5)
    assert result.alignment_verdict == AlignmentVerdict.ALIGNED
    assert result.variance_score == 0.4

    # 5 performative count -> target_cognitive_dampener = 2.0
    # LLM score 1.6 -> variance = 0.4 -> ALIGNED
    result = calculate_mechanical_cognitive_variance(llm_authenticity_score=1.6, performative_phrases_count=5)
    assert result.alignment_verdict == AlignmentVerdict.ALIGNED
    assert result.variance_score == 0.4


def test_calculate_mechanical_cognitive_variance_sycophancy() -> None:
    """Verify alignment verdict is MISALIGNED_SYCOPHANCY when variance is high and LLM score > target."""
    # 5 performative count -> target_cognitive_dampener = 2.0
    # LLM score 2.5 -> variance = 0.5 -> MISALIGNED_SYCOPHANCY
    result = calculate_mechanical_cognitive_variance(llm_authenticity_score=2.5, performative_phrases_count=5)
    assert result.alignment_verdict == AlignmentVerdict.MISALIGNED_SYCOPHANCY
    assert result.variance_score == 0.5

    # 10 performative count -> normalized_performative_count = 2.0 -> target_cognitive_dampener = 1.0
    # LLM score 3.0 -> variance = 2.0 -> MISALIGNED_SYCOPHANCY
    result = calculate_mechanical_cognitive_variance(llm_authenticity_score=3.0, performative_phrases_count=10)
    assert result.alignment_verdict == AlignmentVerdict.MISALIGNED_SYCOPHANCY
    assert result.variance_score == 2.0


def test_calculate_mechanical_cognitive_variance_misaligned() -> None:
    """Verify alignment verdict is MISALIGNED when variance is high and LLM score < target."""
    # 5 performative count -> target_cognitive_dampener = 2.0
    # LLM score 1.5 -> variance = 0.5 -> MISALIGNED
    result = calculate_mechanical_cognitive_variance(llm_authenticity_score=1.5, performative_phrases_count=5)
    assert result.alignment_verdict == AlignmentVerdict.MISALIGNED
    assert result.variance_score == 0.5


def test_calculate_mechanical_cognitive_variance_cap() -> None:
    """Verify that normalized count is capped at 2.0 even for count > 10."""
    # 20 performative count -> normalized_performative_count = min(4.0, 2.0) = 2.0
    # target_cognitive_dampener = 3.0 - 2.0 = 1.0
    # LLM score 1.0 -> variance = 0.0 -> ALIGNED
    result = calculate_mechanical_cognitive_variance(llm_authenticity_score=1.0, performative_phrases_count=20)
    assert result.alignment_verdict == AlignmentVerdict.ALIGNED
    assert result.variance_score == 0.0


def test_calculate_mechanical_cognitive_variance_boundary_values() -> None:
    """ISTQB boundary value analysis: score=0.0 and score=100.0."""
    # Boundary: lower score = 0.0, performative_phrases_count = 0 -> dampener = 3.0, variance = 3.0 -> MISALIGNED
    result_low = calculate_mechanical_cognitive_variance(llm_authenticity_score=0.0, performative_phrases_count=0)
    assert result_low.alignment_verdict == AlignmentVerdict.MISALIGNED
    assert result_low.variance_score == 3.0

    # Boundary: extreme high score = 100.0, count = 10 -> dampener = 1.0, variance = 99.0 -> MISALIGNED_SYCOPHANCY
    result_high = calculate_mechanical_cognitive_variance(llm_authenticity_score=100.0, performative_phrases_count=10)
    assert result_high.alignment_verdict == AlignmentVerdict.MISALIGNED_SYCOPHANCY
    assert result_high.variance_score == 99.0


def test_calculate_mechanical_cognitive_variance_with_density_invariance() -> None:
    """Verify 2D Cartesian variance density optimization handles document length proportionally.

    2 phrases in 1500 words (0.13% density) should not trigger sycophancy,
    while 2 phrases in 40 words (5.0% density) is heavy jargon load.
    """
    # 1. 1500-word document with 2 phrases:
    # density = (2 / 1500) * 100 = 0.1333% -> dampener = 3.0 - (0.1333 / 5.0)*2 = 2.9467
    # For a high authenticity score of 2.85, variance is ~0.0967 -> ALIGNED
    result_long = calculate_mechanical_cognitive_variance(
        llm_authenticity_score=2.85,
        performative_phrases_count=2,
        total_word_count=1500,
    )
    assert result_long.alignment_verdict == AlignmentVerdict.ALIGNED
    assert result_long.variance_score < 0.15

    # 2. 40-word document with 2 phrases:
    # density = (2 / 40) * 100 = 5.0% -> dampener = 3.0 - 2.0 = 1.0
    # For the same high authenticity score of 2.85, variance is 1.85 -> MISALIGNED_SYCOPHANCY
    result_short = calculate_mechanical_cognitive_variance(
        llm_authenticity_score=2.85,
        performative_phrases_count=2,
        total_word_count=40,
    )
    assert result_short.alignment_verdict == AlignmentVerdict.MISALIGNED_SYCOPHANCY
    assert result_short.variance_score == 1.85


def test_calculate_mechanical_cognitive_variance_density_cap() -> None:
    """Verify that extreme jargon density (e.g., 20%) caps dampener reduction cleanly at 2.0."""
    # 10 phrases in 50 words = 20.0% density >> 5.0% normalizer
    # normalized count = cap = 2.0, target dampener = 3.0 - 2.0 = 1.0
    result = calculate_mechanical_cognitive_variance(
        llm_authenticity_score=1.0,
        performative_phrases_count=10,
        total_word_count=50,
    )
    assert result.alignment_verdict == AlignmentVerdict.ALIGNED
    assert result.variance_score == 0.0
