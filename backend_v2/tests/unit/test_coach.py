import pytest
from pydantic import ValidationError

from backend_v2.models.domain.coach import (
    BibliographyItem,
    BibliographyResult,
    CoachingPlan,
    CoachingPlanDTO,
    CoachInput,
)


def test_coach_input_success() -> None:
    """Test valid CoachInput."""
    data = CoachInput(chat_log="User said something")
    assert data.chat_log == "User said something"
    assert data.step_judge is None


def test_coach_input_empty_chat_log() -> None:
    """Test empty chat_log fails min_length validation."""
    with pytest.raises(ValidationError):
        CoachInput(chat_log="")


def test_bibliography_item_success() -> None:
    """Test valid BibliographyItem."""
    item = BibliographyItem(source_id="1", title="Book", url="http://book", snippet="snippet")
    assert item.source_id == "1"
    assert item.title == "Book"


def test_bibliography_item_validation() -> None:
    """Test min_length validation on BibliographyItem."""
    with pytest.raises(ValidationError):
        BibliographyItem(source_id="", title="Book")
    with pytest.raises(ValidationError):
        BibliographyItem(source_id="1", title="")


def test_bibliography_result_success() -> None:
    """Test valid BibliographyResult."""
    item = BibliographyItem(source_id="1", title="Book")
    res = BibliographyResult(references=[item])
    assert len(res.references) == 1


def test_bibliography_result_validation() -> None:
    """Test empty references list fails validation."""
    with pytest.raises(ValidationError):
        BibliographyResult(references=[])


def test_coaching_plan_dto_and_output() -> None:
    """Test CoachingPlanDTO and CoachingPlan wrappers."""
    item = BibliographyItem(source_id="1", title="Book")
    dto = CoachingPlanDTO(
        actionable_steps=["Step 1"],
        bibliography=[item],
        focus_areas=["Focus 1"],
        thought_process="Thinking",
        conclusion="Done",
        confidence_score=0.9,
    )
    assert dto.actionable_steps == ["Step 1"]

    plan = CoachingPlan(
        actionable_steps=["Step 1"],
        bibliography=[item],
        focus_areas=["Focus 1"],
        thought_process="Thinking",
        conclusion="Done",
        confidence_score=0.9,
        reasoning_token="trace",
    )
    assert plan.reasoning_token == "trace"


def test_coaching_plan_validation() -> None:
    """Test list validations in CoachingPlan."""
    item = BibliographyItem(source_id="1", title="Book")

    with pytest.raises(ValidationError):
        CoachingPlanDTO(
            actionable_steps=[],
            bibliography=[item],
            focus_areas=["Focus 1"],
            thought_process="Thinking",
            conclusion="Done",
            confidence_score=0.9,
        )

    with pytest.raises(ValidationError):
        CoachingPlanDTO(
            actionable_steps=["Step 1"],
            bibliography=[item],
            focus_areas=[],
            thought_process="Thinking",
            conclusion="Done",
            confidence_score=0.9,
        )

    with pytest.raises(ValidationError):
        CoachingPlanDTO(
            actionable_steps=["Step 1"],
            bibliography=[],
            focus_areas=["Focus 1"],
            thought_process="Thinking",
            conclusion="Done",
            confidence_score=0.9,
        )
