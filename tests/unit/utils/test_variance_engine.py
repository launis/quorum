"""Unit tests for the Mechanical-Cognitive Variance Engine."""

import pytest
from backend_v2.utils.scoring.variance_engine import calculate_mechanical_cognitive_variance


def test_variance_zero_phrases_high_authenticity():
    """Test zero performative phrases and high authenticity score.

    Expected:
        - normalized_performative_count = 0.0
        - target_cognitive_dampener = 3.0 - 0.0 = 3.0
        - variance_score = |3.0 - 3.0| = 0.0
        - alignment_verdict = "ALIGNED"
    """
    res = calculate_mechanical_cognitive_variance(
        llm_authenticity_score=3.0,
        performative_phrases_count=0,
    )
    assert res["variance_score"] == 0.0
    assert res["alignment_verdict"] == "ALIGNED"
    assert res["mechanical_metric_ref"] == "performative_phrases_count"
    assert res["cognitive_metric_ref"] == "llm_authenticity_score"


def test_variance_ten_phrases_high_authenticity():
    """Test ten performative phrases and high authenticity score.

    Expected:
        - normalized_performative_count = min(10.0 / 10.0 * 2.0, 2.0) = 2.0
        - target_cognitive_dampener = 3.0 - 2.0 = 1.0
        - variance_score = |3.0 - 1.0| = 2.0
        - alignment_verdict = "MISALIGNED_SYCOPHANCY" (variance >= 0.5 and 3.0 > 1.0)
    """
    res = calculate_mechanical_cognitive_variance(
        llm_authenticity_score=3.0,
        performative_phrases_count=10,
    )
    assert res["variance_score"] == 2.0
    assert res["alignment_verdict"] == "MISALIGNED_SYCOPHANCY"


def test_variance_five_phrases_medium_authenticity():
    """Test five performative phrases and medium authenticity score.

    Expected:
        - normalized_performative_count = min(5 / 10 * 2, 2) = 1.0
        - target_cognitive_dampener = 3.0 - 1.0 = 2.0
        - variance_score = |2.0 - 2.0| = 0.0
        - alignment_verdict = "ALIGNED"
    """
    res = calculate_mechanical_cognitive_variance(
        llm_authenticity_score=2.0,
        performative_phrases_count=5,
    )
    assert res["variance_score"] == 0.0
    assert res["alignment_verdict"] == "ALIGNED"


def test_variance_many_phrases_high_authenticity():
    """Test more than ten performative phrases (boundary test).

    Expected:
        - normalized_performative_count = min(15 / 10 * 2, 2.0) = 2.0
        - target_cognitive_dampener = 3.0 - 2.0 = 1.0
        - variance_score = |3.0 - 1.0| = 2.0
        - alignment_verdict = "MISALIGNED_SYCOPHANCY"
    """
    res = calculate_mechanical_cognitive_variance(
        llm_authenticity_score=3.0,
        performative_phrases_count=15,
    )
    assert res["variance_score"] == 2.0
    assert res["alignment_verdict"] == "MISALIGNED_SYCOPHANCY"


def test_variance_misaligned_non_sycophancy():
    """Test cases resulting in general MISALIGNED verdict.

    Expected:
        - performative_phrases_count = 0
        - target_cognitive_dampener = 3.0
        - llm_authenticity_score = 1.0
        - variance_score = |1.0 - 3.0| = 2.0
        - alignment_verdict = "MISALIGNED" (variance >= 0.5 and 1.0 <= 3.0)
    """
    res = calculate_mechanical_cognitive_variance(
        llm_authenticity_score=1.0,
        performative_phrases_count=0,
    )
    assert res["variance_score"] == 2.0
    assert res["alignment_verdict"] == "MISALIGNED"


def test_invalid_inputs():
    """Verify that type safety raises ValueErrors on invalid input types."""
    with pytest.raises(ValueError, match="performative_phrases_count must be a non-negative integer"):
        calculate_mechanical_cognitive_variance(3.0, -1)

    with pytest.raises(ValueError, match="performative_phrases_count must be a non-negative integer"):
        calculate_mechanical_cognitive_variance(3.0, 1.5)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="llm_authenticity_score must be a float or int"):
        calculate_mechanical_cognitive_variance("3.0", 5)  # type: ignore[arg-type]
