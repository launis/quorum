import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.inputs import GuidedReflectionInputDTO, QuestionAnswerPair


def test_question_answer_pair_strictness() -> None:
    """Test QuestionAnswerPair strictness and immutability."""
    pair = QuestionAnswerPair(question="What?", answer="Yes.")
    assert pair.question == "What?"
    assert pair.answer == "Yes."

    with pytest.raises(ValidationError, match="Instance is frozen"):
        pair.question = "Why?"  # type: ignore[misc]

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        QuestionAnswerPair(question="What?", answer="Yes.", extra="not allowed")


def test_guided_reflection_input_dto_strictness() -> None:
    """Test GuidedReflectionInputDTO strictness and min_length constraints."""
    pair = QuestionAnswerPair(question="Q1", answer="A1")
    
    # Valid instantiation
    dto = GuidedReflectionInputDTO(pairs=[pair], metadata={"topic": "Test"})
    assert len(dto.pairs) == 1
    assert dto.metadata["topic"] == "Test"

    # Must have at least 1 pair
    with pytest.raises(ValidationError, match="List should have at least 1 item after validation, not 0"):
        GuidedReflectionInputDTO(pairs=[])
        
    # Extra fields forbidden
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        GuidedReflectionInputDTO(pairs=[pair], metadata={}, invalid_field="boom")


def test_guided_reflection_to_markdown() -> None:
    """Test deterministic Markdown serialization."""
    dto = GuidedReflectionInputDTO(
        pairs=[
            QuestionAnswerPair(question="First Q", answer="First A"),
            QuestionAnswerPair(question="Second Q", answer="Second A"),
        ],
        metadata={"b_key": "b_value", "a_key": "a_value"}  # Unsorted keys
    )
    
    md_output = dto.to_markdown(title="My Form")
    
    expected = (
        "# My Form\n\n"
        "**a_key:** a_value\n\n"
        "**b_key:** b_value\n\n"
        "### Q: First Q\n"
        "> **A:** First A\n\n"
        "### Q: Second Q\n"
        "> **A:** Second A"
    )
    
    assert md_output == expected
