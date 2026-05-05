import pytest
from pydantic import ValidationError

from backend_v2.models.domain.coach import (
    BibliographyItem,
    BibliographyResult,
    CoachInput,
    CoachingPlan,
)


def test_coach_input_strict_validation() -> None:
    """Test that CoachInput follows V2CoreBase strict constraints."""
    item = CoachInput(chat_log="User wants to improve")
    assert item.chat_log == "User wants to improve"
    
    with pytest.raises(ValidationError):
        CoachInput(chat_log="Hello", extra_field="not allowed")


def test_bibliography_item_validation() -> None:
    """Test BibliographyItem constraints."""
    item = BibliographyItem(source_id="src_1", title="Title 1")
    assert item.title == "Title 1"
    
    with pytest.raises(ValidationError):
        BibliographyItem(source_id="src_1", title="Title 1", extra_field="bad")


def test_bibliography_result_validation() -> None:
    """Test BibliographyResult constraints."""
    item = BibliographyItem(source_id="src_1", title="Title 1")
    res = BibliographyResult(references=[item])
    assert len(res.references) == 1
    
    # Test min length / bounds
    with pytest.raises(ValidationError):
        BibliographyResult(references=[])


def test_coaching_plan_validation() -> None:
    """Test CoachingPlan constraints."""
    item = BibliographyItem(source_id="src_1", title="Title 1")
    plan = CoachingPlan(
        actionable_steps=["Step 1"],
        bibliography=[item],
        focus_areas=["Focus 1"],
        thought_process="Thinking...",
        conclusion="Conclusion",
        confidence_score=0.9
    )
    assert plan.confidence_score == 0.9
    
    with pytest.raises(ValidationError):
        CoachingPlan(
            actionable_steps=[], # Min length is 1
            bibliography=[item],
            focus_areas=["Focus 1"],
            thought_process="Thinking...",
            conclusion="Conclusion",
            confidence_score=0.9
        )
