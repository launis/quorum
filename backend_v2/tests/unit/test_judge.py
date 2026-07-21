from unittest.mock import AsyncMock
import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.domain.judge import (
    DimensionResultItem,
    JudgeDTO,
    JudgeInput,
    JudgeScoreCard,
    ScoringResult,
)


def test_judge_input_strictness() -> None:
    """Test that JudgeInput enforces dynamic inputs and forbids extras."""
    # Valid
    inputs = JudgeInput(chat_log="User: Hi", dynamic_inputs={"extra": "allowed_here"})
    assert inputs.chat_log == "User: Hi"

    # Fails min_length
    with pytest.raises(ValidationError):
        JudgeInput(chat_log="")

    # Fails extra
    with pytest.raises(ValidationError):
        JudgeInput(chat_log="Hi", extra_field="fail")  # type: ignore


def test_dimension_result_strictness() -> None:
    """Test DimensionResultItem constraints."""
    valid_dim = DimensionResultItem(dimension_id="dim_1", dimension_label="Analysis", score=3, reasoning="Good")
    assert valid_dim.score == 3

    # Fails negative score
    with pytest.raises(AppException):
        DimensionResultItem(dimension_id="dim_1", dimension_label="L", score=-1, reasoning="R")

    # Fails empty strings
    with pytest.raises(ValidationError):
        DimensionResultItem(dimension_id="", dimension_label="L", score=1, reasoning="R")

    with pytest.raises(ValidationError):
        DimensionResultItem(dimension_id="D", dimension_label="L", score=1, reasoning="")

    # Fails extra
    with pytest.raises(ValidationError):
        DimensionResultItem(dimension_id="D", dimension_label="L", score=1, reasoning="R", extra="fail")  # type: ignore


def test_judge_score_card_strictness() -> None:
    """Test JudgeScoreCard constraints."""
    dim = DimensionResultItem(dimension_id="d", dimension_label="l", score=5, reasoning="r")

    # Valid
    card = JudgeScoreCard(
        agent_name="Judge",
        total_score=5.0,
        max_score=5,
        verdict="Pass",
        dimensions=[dim],
        scale_min=0.0,
        scale_max=5.0,
    )
    assert card.total_score == 5.0

    # Fails empty agent_name
    with pytest.raises(ValidationError):
        JudgeScoreCard(
            agent_name="",
            total_score=5.0,
            max_score=5,
            verdict="Pass",
            dimensions=[dim],
            scale_min=0.0,
            scale_max=5.0,
        )

    # Fails empty dimensions
    with pytest.raises(ValidationError):
        JudgeScoreCard(
            agent_name="A",
            total_score=5.0,
            max_score=5,
            verdict="V",
            dimensions=[],
            scale_min=0.0,
            scale_max=5.0,
        )

    # Fails invalid scores
    with pytest.raises(AppException) as exc:
        JudgeScoreCard(
            agent_name="A",
            total_score=6.0,  # Out of range
            max_score=5,
            verdict="V",
            dimensions=[dim],
            scale_min=0.0,
            scale_max=5.0,
        )
    assert "is out of range" in str(exc.value)

    with pytest.raises(AppException) as exc:
        JudgeScoreCard(
            agent_name="A",
            total_score=5.0,
            max_score=5,
            verdict="V",
            dimensions=[dim],
            scale_min=5.0,  # Invalid range
            scale_max=2.0,
        )
    assert "must be less than" in str(exc.value)


def test_judge_dto_strictness() -> None:
    """Test JudgeDTO structure."""
    dim = DimensionResultItem(dimension_id="d", dimension_label="l", score=5, reasoning="r")
    card = JudgeScoreCard(
        agent_name="A",
        total_score=5.0,
        max_score=5,
        verdict="V",
        dimensions=[dim],
        scale_min=0.0,
        scale_max=5.0,
    )

    # Valid
    dto = JudgeDTO(
        thought_process="Thinking",
        conclusion="Conclusion",
        confidence_score=0.9,
        matrix_id="m1",
        score_card=card,
        scale_min=0.0,
        scale_max=5.0,
    )
    assert dto.matrix_id == "m1"


def test_scoring_result_strictness() -> None:
    """Test ScoringResult constraints."""
    # Valid
    res = ScoringResult(total_score=5.0, calculated_average=4.5, score_summary="Good")
    assert res.total_score == 5.0

    # Fails empty summary
    with pytest.raises(ValidationError):
        ScoringResult(total_score=5.0, calculated_average=4.5, score_summary="")

    # Fails extra
    with pytest.raises(ValidationError):
        ScoringResult(total_score=5.0, calculated_average=4.5, score_summary="S", extra="no")  # type: ignore
