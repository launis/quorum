"""Unit tests for Coach Agent Domain Models."""

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.coach import (
    BibliographyItem,
    BibliographyResult,
    CoachingPlan,
    CoachingPlanDTO,
    CoachInput,
)


def test_coach_input_strict_validation() -> None:
    """Test that CoachInput follows V2CoreBase strict and frozen constraints."""
    item = CoachInput(chat_log="User wants to improve", last_reasoning_trace="Prior trace")
    assert item.chat_log == "User wants to improve"
    assert item.last_reasoning_trace == "Prior trace"
    assert item.step_judge is None
    assert item.step_analyst is None

    # Negative case 1: extra field forbidden
    with pytest.raises(ValidationError):
        CoachInput.model_validate({"chat_log": "Hello", "extra_field": "not allowed"})

    # Negative case 2: empty chat_log violates min_length=1
    with pytest.raises(ValidationError):
        CoachInput(chat_log="")

    # Negative case 3: invalid type for typed critic input step_analyst
    with pytest.raises(ValidationError):
        CoachInput.model_validate({"chat_log": "Hello", "step_analyst": "invalid_untyped_string"})


def test_bibliography_item_validation() -> None:
    """Test BibliographyItem constraints and negative boundary cases."""
    item = BibliographyItem(
        source_id="src_1",
        title="Title 1",
        url="https://example.com",
        snippet="Relevant excerpt",
    )
    assert item.source_id == "src_1"
    assert item.title == "Title 1"
    assert item.url == "https://example.com"
    assert item.snippet == "Relevant excerpt"

    # Negative case 1: extra field forbidden
    with pytest.raises(ValidationError):
        BibliographyItem.model_validate({"source_id": "src_1", "title": "Title 1", "extra_field": "bad"})

    # Negative case 2: empty source_id or title violates min_length=1
    with pytest.raises(ValidationError):
        BibliographyItem(source_id="", title="Title 1")

    with pytest.raises(ValidationError):
        BibliographyItem(source_id="src_1", title="")


def test_bibliography_result_validation() -> None:
    """Test BibliographyResult constraints and negative boundary cases."""
    item = BibliographyItem(source_id="src_1", title="Title 1")
    res = BibliographyResult(references=[item])
    assert len(res.references) == 1

    # Negative case 1: empty references list violates min_length=1
    with pytest.raises(ValidationError):
        BibliographyResult(references=[])

    # Negative case 2: extra field forbidden
    with pytest.raises(ValidationError):
        BibliographyResult.model_validate({"references": [item.model_dump()], "extra": "forbidden"})


def test_coaching_plan_dto_and_output_validation() -> None:
    """Test CoachingPlanDTO and CoachingPlan constraints and ISTQB negative boundaries."""
    item = BibliographyItem(source_id="src_1", title="Title 1")
    dto = CoachingPlanDTO(
        actionable_steps=["Step 1"],
        bibliography=[item],
        focus_areas=["Focus 1"],
        thought_process="Detailed coaching reasoning.",
        conclusion="Synthesized coaching conclusion.",
        confidence_score=0.0,
    )
    assert dto.confidence_score == 0.0

    plan = CoachingPlan(
        actionable_steps=["Step 1"],
        bibliography=[item],
        focus_areas=["Focus 1"],
        thought_process="Detailed coaching reasoning.",
        conclusion="Synthesized coaching conclusion.",
        confidence_score=1.0,
    )
    assert plan.confidence_score == 1.0

    # Negative case 1: empty actionable_steps violates min_length=1
    with pytest.raises(ValidationError):
        CoachingPlan(
            actionable_steps=[],
            bibliography=[item],
            focus_areas=["Focus 1"],
            thought_process="Thinking...",
            conclusion="Conclusion",
            confidence_score=0.9,
        )

    # Negative case 2: confidence_score below 0.0 raises AppException (VALIDATION_FAILED)
    with pytest.raises(AppException) as exc_low:
        CoachingPlan(
            actionable_steps=["Step 1"],
            bibliography=[item],
            focus_areas=["Focus 1"],
            thought_process="Thinking...",
            conclusion="Conclusion",
            confidence_score=-0.1,
        )
    assert exc_low.value.details == {"error_code": ErrorCodes.VALIDATION_FAILED}

    # Negative case 3: confidence_score above 1.0 raises AppException (VALIDATION_FAILED)
    with pytest.raises(AppException) as exc_high:
        CoachingPlanDTO(
            actionable_steps=["Step 1"],
            bibliography=[item],
            focus_areas=["Focus 1"],
            thought_process="Thinking...",
            conclusion="Conclusion",
            confidence_score=1.1,
        )
    assert exc_high.value.details == {"error_code": ErrorCodes.VALIDATION_FAILED}

    # Negative case 4: hallucinated thought_process raises AppException (VALIDATION_FAILED)
    with pytest.raises(AppException) as exc_hallucination:
        CoachingPlan(
            actionable_steps=["Step 1"],
            bibliography=[item],
            focus_areas=["Focus 1"],
            thought_process="N/A",
            conclusion="Conclusion",
            confidence_score=0.8,
        )
    assert exc_hallucination.value.details == {"error_code": ErrorCodes.VALIDATION_FAILED}
