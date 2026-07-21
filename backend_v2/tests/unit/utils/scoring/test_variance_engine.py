from unittest.mock import AsyncMock
"""Unit tests for the Mechanical-Cognitive Variance Engine."""

import pytest

from backend_v2.exceptions import AppException
from backend_v2.utils.scoring.variance_engine import calculate_mechanical_cognitive_variance


def test_calculate_mechanical_cognitive_variance_validation() -> None:
    """Verify that type and value validation raises appropriate AppException."""
    # Test invalid performative_phrases_count type
    with pytest.raises(AppException, match="performative_phrases_count must be a non-negative integer."):
        calculate_mechanical_cognitive_variance(llm_authenticity_score=2.0, performative_phrases_count=-1)

    with pytest.raises(AppException, match="performative_phrases_count must be a non-negative integer."):
        calculate_mechanical_cognitive_variance(llm_authenticity_score=2.0, performative_phrases_count="5")  # type: ignore

    # Test invalid llm_authenticity_score type
    with pytest.raises(AppException, match="llm_authenticity_score must be a float or int."):
        calculate_mechanical_cognitive_variance(llm_authenticity_score="2.0", performative_phrases_count=5)  # type: ignore


def test_calculate_mechanical_cognitive_variance_aligned() -> None:
    """Verify alignment verdict is ALIGNED when variance is within limits."""
    # 0 performative count -> target_cognitive_dampener = 3.0
    # LLM score 3.0 -> variance = 0.0 -> ALIGNED
    result = calculate_mechanical_cognitive_variance(llm_authenticity_score=3.0, performative_phrases_count=0)
    assert result["alignment_verdict"] == "ALIGNED"
    assert result["variance_score"] == 0.0
    assert result["mechanical_metric_ref"] == "performative_phrases_count"
    assert result["cognitive_metric_ref"] == "llm_authenticity_score"

    # Variance < 0.5 (e.g. variance = 0.4) -> ALIGNED
    # 5 performative count -> normalized_performative_count = 1.0 -> target_cognitive_dampener = 2.0
    # LLM score 2.4 -> variance = 0.4 -> ALIGNED
    result = calculate_mechanical_cognitive_variance(llm_authenticity_score=2.4, performative_phrases_count=5)
    assert result["alignment_verdict"] == "ALIGNED"
    assert result["variance_score"] == 0.4

    # 5 performative count -> target_cognitive_dampener = 2.0
    # LLM score 1.6 -> variance = 0.4 -> ALIGNED
    result = calculate_mechanical_cognitive_variance(llm_authenticity_score=1.6, performative_phrases_count=5)
    assert result["alignment_verdict"] == "ALIGNED"
    assert result["variance_score"] == 0.4


def test_calculate_mechanical_cognitive_variance_sycophancy() -> None:
    """Verify alignment verdict is MISALIGNED_SYCOPHANCY when variance is high and LLM score > target."""
    # 5 performative count -> target_cognitive_dampener = 2.0
    # LLM score 2.5 -> variance = 0.5 -> MISALIGNED_SYCOPHANCY
    result = calculate_mechanical_cognitive_variance(llm_authenticity_score=2.5, performative_phrases_count=5)
    assert result["alignment_verdict"] == "MISALIGNED_SYCOPHANCY"
    assert result["variance_score"] == 0.5

    # 10 performative count -> normalized_performative_count = 2.0 -> target_cognitive_dampener = 1.0
    # LLM score 3.0 -> variance = 2.0 -> MISALIGNED_SYCOPHANCY
    result = calculate_mechanical_cognitive_variance(llm_authenticity_score=3.0, performative_phrases_count=10)
    assert result["alignment_verdict"] == "MISALIGNED_SYCOPHANCY"
    assert result["variance_score"] == 2.0


def test_calculate_mechanical_cognitive_variance_misaligned() -> None:
    """Verify alignment verdict is MISALIGNED when variance is high and LLM score < target."""
    # 5 performative count -> target_cognitive_dampener = 2.0
    # LLM score 1.5 -> variance = 0.5 -> MISALIGNED
    result = calculate_mechanical_cognitive_variance(llm_authenticity_score=1.5, performative_phrases_count=5)
    assert result["alignment_verdict"] == "MISALIGNED"
    assert result["variance_score"] == 0.5


def test_calculate_mechanical_cognitive_variance_cap() -> None:
    """Verify that normalized count is capped at 2.0 even for count > 10."""
    # 20 performative count -> normalized_performative_count = min(4.0, 2.0) = 2.0
    # target_cognitive_dampener = 3.0 - 2.0 = 1.0
    # LLM score 1.0 -> variance = 0.0 -> ALIGNED
    result = calculate_mechanical_cognitive_variance(llm_authenticity_score=1.0, performative_phrases_count=20)
    assert result["alignment_verdict"] == "ALIGNED"
    assert result["variance_score"] == 0.0
